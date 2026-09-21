"""Workflow hygiene policy for this repository's own workflow files.

Line-based checks against the declared policy: full-SHA pins with version
comments, top-level permissions, per-job timeouts, no persisted checkout
credentials, and no `${{ }}` expressions inside `run:` bodies. This is not a
YAML parser or a GitHub Actions schema check; zizmor and actionlint cover
those. Four pre-existing files are exempt from the strict rules until the
separate hardening pull request that owns them lands; the exemption is by
exact filename so nothing new inherits it.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

# Owned by the workflow-hygiene pull request; remove entries as they are repaired.
LEGACY = {
    "governance-contracts.yml",
    "quirk-semantic-governance.yml",
    "reusable-evidence-binding.yml",
    "reusable-validate.yml",
}

USES_RE = re.compile(r"^\s*-?\s*uses:\s*(\S+)(?:\s+#\s*(\S+))?\s*$")
PINNED_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?@[0-9a-f]{40}$")
VERSION_RE = re.compile(r"^v\d+(?:\.\d+){0,2}$")
PERMISSIONS_RE = re.compile(r"^(\s*)permissions:\s*(\S*)\s*$")
SCOPE_RE = re.compile(r"^(\s*)([a-z-]+):\s*(read|write|none)\s*(?:#.*)?$")


def workflow_files():
    return sorted(p for p in WORKFLOWS.iterdir() if p.suffix in {".yml", ".yaml"})


def strict_files():
    return [p for p in workflow_files() if p.name not in LEGACY]


def indent(line):
    return len(line) - len(line.lstrip(" "))


def permission_blocks(text):
    """Return (workflow-level scopes, [job-level scopes, ...]) as scope->level maps.

    An inline block (`permissions: {}` or `permissions: read-all`) yields no
    scopes, which is what those forms mean for the purposes of these checks.
    """
    lines = text.splitlines()
    top, jobs = {}, []
    i = 0
    while i < len(lines):
        match = PERMISSIONS_RE.match(lines[i])
        if not match:
            i += 1
            continue
        base = len(match.group(1))
        scopes = {}
        i += 1
        if not match.group(2):
            while i < len(lines):
                scope = SCOPE_RE.match(lines[i])
                if not scope or len(scope.group(1)) <= base:
                    break
                scopes[scope.group(2)] = scope.group(3)
                i += 1
        if base == 0:
            top.update(scopes)
        else:
            jobs.append(scopes)
    return top, jobs


def run_blocks(text):
    """Yield the text of every `run:` body (single line or block scalar)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^(\s*)(?:-\s+)?run:\s*(.*)$", line)
        if not match:
            i += 1
            continue
        base = indent(line)
        value = match.group(2).strip()
        if value and value[0] not in "|>":
            yield value
            i += 1
            continue
        body = []
        i += 1
        while i < len(lines) and (not lines[i].strip() or indent(lines[i]) > base):
            body.append(lines[i])
            i += 1
        yield "\n".join(body)


class WorkflowPinPolicyTests(unittest.TestCase):
    def test_new_workflows_exist(self):
        names = {p.name for p in strict_files()}
        for expected in ("codeql.yml", "scorecard.yml", "dependency-review.yml", "workflow-lint.yml",
                         "reusable-codeql.yml", "reusable-dependency-review.yml", "reusable-workflow-lint.yml",
                         "reusable-sbom-provenance.yml", "reusable-stale-incubations.yml"):
            self.assertIn(expected, names)

    def test_every_remote_action_is_pinned_to_a_full_sha_with_version_comment(self):
        for path in strict_files():
            for line in path.read_text(encoding="utf-8").splitlines():
                match = USES_RE.match(line)
                if not match:
                    continue
                ref, comment = match.group(1), match.group(2)
                if ref.startswith("./") or ref.startswith("docker://"):
                    continue
                self.assertRegex(ref, PINNED_RE, f"{path.name}: unpinned or malformed uses: {ref}")
                self.assertIsNotNone(comment, f"{path.name}: pin needs a '# vX.Y.Z' comment: {ref}")
                self.assertRegex(comment, VERSION_RE, f"{path.name}: bad version comment for {ref}")

    def test_top_level_permissions_and_concurrency_are_declared(self):
        """Every workflow declares its top-level scopes explicitly.

        A workflow this repository runs itself defaults to read-only and needs
        `contents: read` to check out. A reusable workflow's top-level block is
        a contract with its callers rather than a local default, so it may name
        a write scope its jobs use; the next test pins it to exactly that set.
        """
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            top, _ = permission_blocks(text)
            self.assertIsNotNone(re.search(r"^permissions:", text, re.M),
                                 f"{path.name}: needs an explicit top-level permissions block")
            self.assertIsNotNone(re.search(r"^concurrency:\n", text, re.M), f"{path.name}: needs a concurrency group")
            self.assertNotIn("write-all", text, path.name)
            self.assertNotIn("pull_request_target", text, path.name)
            self.assertNotIn("workflow_run", text, path.name)
            if "workflow_call" in text:
                continue
            self.assertTrue(top, f"{path.name}: the top-level block must name its scopes")
            for scope, level in sorted(top.items()):
                self.assertEqual(level, "read", f"{path.name}: top-level '{scope}: {level}' — default to read-only")
            self.assertEqual(top.get("contents"), "read", f"{path.name}: needs read-only default permissions")

    def test_a_reusable_workflow_asks_callers_for_nothing_its_jobs_leave_unused(self):
        """A called workflow's top-level block is validated against the caller's grant.

        GitHub checks it before it creates any job, so a scope named at workflow
        level is demanded of every caller whether or not a job uses it. A caller
        that grants only what the jobs use then never compiles: its run ends
        `startup_failure` with no job and no log to diagnose from. Naming
        `contents: read` at workflow level beside a job that named only
        `pull-requests: read` is how that was observed.

        So where every job names its own scopes the top-level block is pure
        caller tax and must be `permissions: {}`. Where a job names none it
        inherits the block, which is then exactly what that job uses.
        """
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            if "workflow_call" not in text:
                continue
            top, jobs = permission_blocks(text)
            if len(jobs) < len(re.findall(r"^\s+runs-on:", text, re.M)):
                continue  # at least one job inherits the top-level block and so uses all of it
            self.assertEqual(top, {}, f"{path.name}: every job here names its own scopes, so the top-level block "
                                      "must be `permissions: {}` — a scope named there is demanded of every caller "
                                      "before any job is created, and used by none of them")

    def test_every_job_has_a_timeout_and_a_pinned_runner(self):
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            runs_on = re.findall(r"^\s+runs-on:\s*(\S+)", text, re.M)
            timeouts = re.findall(r"^\s+timeout-minutes:\s*\d+", text, re.M)
            self.assertTrue(runs_on, path.name)
            self.assertEqual(len(runs_on), len(timeouts), f"{path.name}: every job needs timeout-minutes")
            for runner in runs_on:
                self.assertEqual(runner, "ubuntu-24.04", f"{path.name}: pin the runner image, not {runner}")

    def test_checkouts_do_not_persist_credentials(self):
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            checkouts = text.count("uses: actions/checkout@")
            self.assertEqual(checkouts, text.count("persist-credentials: false"),
                             f"{path.name}: every checkout must set persist-credentials: false")

    def test_no_expressions_inside_run_bodies(self):
        for path in strict_files():
            for body in run_blocks(path.read_text(encoding="utf-8")):
                self.assertNotIn("${{", body, f"{path.name}: move expressions into env:, never into run: bodies")

    def test_reusable_workflows_accept_no_secrets(self):
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            if "workflow_call" not in text:
                continue
            self.assertNotRegex(text, r"^\s+secrets:", f"{path.name}: reusable workflows take no caller secrets")

    def test_the_caller_contract_check_reads_each_permission_shape(self):
        """The shape that produced the startup failure, and the two that must pass.

        Without this the contract test could pass by parsing nothing at all.
        """
        broken = ("permissions:\n  contents: read\n\njobs:\n  lint:\n    runs-on: ubuntu-24.04\n"
                  "    permissions:\n      pull-requests: read # comment\n    steps: []\n")
        self.assertEqual(permission_blocks(broken), ({"contents": "read"}, [{"pull-requests": "read"}]))
        inherited = "permissions:\n  pull-requests: read\n\njobs:\n  lint:\n    runs-on: ubuntu-24.04\n"
        self.assertEqual(permission_blocks(inherited), ({"pull-requests": "read"}, []))
        self.assertEqual(permission_blocks("permissions: {}\n\njobs:\n  lint:\n    runs-on: ubuntu-24.04\n"), ({}, []))

    def test_legacy_exemptions_only_name_existing_files(self):
        for name in LEGACY:
            self.assertTrue((WORKFLOWS / name).is_file(), f"stale legacy exemption: {name}")


if __name__ == "__main__":
    unittest.main()
