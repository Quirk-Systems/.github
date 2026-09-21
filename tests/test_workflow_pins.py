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


def workflow_files():
    return sorted(p for p in WORKFLOWS.iterdir() if p.suffix in {".yml", ".yaml"})


def strict_files():
    return [p for p in workflow_files() if p.name not in LEGACY]


def indent(line):
    return len(line) - len(line.lstrip(" "))


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
        for path in strict_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNotNone(re.search(r"^permissions:\n  contents: read\n", text, re.M),
                                 f"{path.name}: needs read-only default permissions")
            self.assertIsNotNone(re.search(r"^concurrency:\n", text, re.M), f"{path.name}: needs a concurrency group")
            self.assertNotIn("write-all", text, path.name)
            self.assertNotIn("pull_request_target", text, path.name)
            self.assertNotIn("workflow_run", text, path.name)

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

    def test_legacy_exemptions_only_name_existing_files(self):
        for name in LEGACY:
            self.assertTrue((WORKFLOWS / name).is_file(), f"stale legacy exemption: {name}")


if __name__ == "__main__":
    unittest.main()
