import importlib.util
import json
import subprocess
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(path, *args):
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
    )


def make_repo(workspace, name, files=None, owner="Quirk-Systems"):
    path = Path(workspace) / name
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "remote", "add", "origin", f"https://github.com/{owner}/{name}.git")
    for relative, content in (files or {}).items():
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    if files:
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", "init")
    return path


def inventory(entries):
    return {entry["repository"]: entry for entry in entries}


class WorkspaceScanTests(unittest.TestCase):
    def setUp(self):
        self.ws = load("quirk_workspace")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def by_name(self):
        return {item["repository"]: item for item in self.ws.scan(self.root)}

    def test_classifies_empty_docs_and_code(self):
        make_repo(self.root, "quirk-empty")
        make_repo(self.root, "quirk-docs", {"README.md": "# docs\n"})
        make_repo(self.root, "quirk-app", {
            "package.json": json.dumps({"scripts": {"validate": "x", "test": "y"}}),
            "bun.lock": "",
            "src/index.ts": "export {}\n",
        })
        seen = self.by_name()
        self.assertEqual(seen["Quirk-Systems/quirk-empty"]["state"], self.ws.EMPTY)
        self.assertIsNone(seen["Quirk-Systems/quirk-empty"]["head"])
        self.assertEqual(seen["Quirk-Systems/quirk-docs"]["state"], self.ws.DOCS_ONLY)
        app = seen["Quirk-Systems/quirk-app"]
        self.assertEqual(app["state"], self.ws.CODE)
        self.assertEqual(app["validation_command"], "bun run validate")
        self.assertEqual(len(app["head"]), 40)

    def test_dependency_directories_do_not_count_as_source(self):
        make_repo(self.root, "quirk-docs", {"README.md": "x\n", "node_modules/pkg/index.js": "x\n"})
        self.assertEqual(self.by_name()["Quirk-Systems/quirk-docs"]["state"], self.ws.DOCS_ONLY)

    def test_untracked_environments_do_not_count_as_source(self):
        path = make_repo(self.root, "quirk-docs", {"README.md": "x\n"})
        for env in ("venv", "env", ".tox/py312"):
            target = path / env / "lib" / "site.py"
            target.parent.mkdir(parents=True)
            target.write_text("x = 1\n", encoding="utf-8")
        seen = self.by_name()["Quirk-Systems/quirk-docs"]
        self.assertEqual((seen["state"], seen["source_files"]), (self.ws.DOCS_ONLY, 0))

    def test_validation_command_uses_only_declared_entrypoints(self):
        make_repo(self.root, "a", {"scripts/validate.sh": "#!/bin/sh\n", "package.json": "{}"})
        make_repo(self.root, "b", {"package.json": json.dumps({"scripts": {"test": "vitest"}})})
        make_repo(self.root, "c", {"package.json": json.dumps({"scripts": {"dev": "next dev"}})})
        make_repo(self.root, "d", {"scripts/tool.py": "print(1)\n"})
        make_repo(self.root, "e", {"pyproject.toml": "[tool.pytest.ini_options]\n", "tests/test_x.py": "\n"})
        seen = self.by_name()
        self.assertEqual(seen["Quirk-Systems/a"]["validation_command"], "scripts/validate.sh")
        self.assertEqual(seen["Quirk-Systems/b"]["validation_command"], "npm run test")
        self.assertIsNone(seen["Quirk-Systems/c"]["validation_command"])
        self.assertIsNone(seen["Quirk-Systems/d"]["validation_command"])
        self.assertIsNone(seen["Quirk-Systems/e"]["validation_command"])

    def test_repository_name_comes_from_origin_not_directory(self):
        path = make_repo(self.root, "local-dir", {"README.md": "x\n"}, owner="bryansayler")
        git(path, "remote", "set-url", "origin", "git@github.com:bryansayler/quirk-commerce.git")
        self.assertIn("bryansayler/quirk-commerce", self.by_name())

    def test_unreadable_checkout_is_not_reported_empty(self):
        path = Path(self.root) / "broken"
        path.mkdir()
        (path / ".git").write_text("gitdir: /nonexistent/quirk\n", encoding="utf-8")
        make_repo(self.root, "unborn")
        seen = {item["directory"]: item for item in self.ws.scan(self.root)}
        self.assertEqual(seen["broken"]["state"], self.ws.UNREADABLE)
        self.assertEqual(seen["unborn"]["state"], self.ws.EMPTY)
        registry = inventory([{"repository": seen["broken"]["repository"], "lifecycle": "active"}])
        self.assertEqual([f for f in self.ws.drift([seen["broken"]], registry) if f["kind"] == self.ws.STATE_MISMATCH], [])

    def test_non_git_directories_are_ignored(self):
        (Path(self.root) / "notes").mkdir()
        self.assertEqual(self.ws.scan(self.root), [])

    def test_missing_workspace_is_an_error(self):
        with self.assertRaises(self.ws.WorkspaceError):
            self.ws.scan(Path(self.root) / "absent")


class WorkspaceDriftTests(unittest.TestCase):
    def setUp(self):
        self.ws = load("quirk_workspace")

    def observed(self, name, state, toolchain=()):
        return {"repository": name, "state": state, "commits": 0 if state == self.ws.EMPTY else 1, "toolchain": list(toolchain)}

    def test_reports_each_finding_kind(self):
        observed = [
            self.observed("Quirk-Systems/quirk-new", self.ws.EMPTY),
            self.observed("Quirk-Systems/quirk-live", self.ws.EMPTY),
            self.observed("Quirk-Systems/quirk-held", self.ws.CODE, ["package.json"]),
        ]
        registry = inventory([
            {"repository": "Quirk-Systems/quirk-live", "lifecycle": "active"},
            {"repository": "Quirk-Systems/quirk-held", "lifecycle": "reserved"},
            {"repository": "bryansayler/quirk-elsewhere", "lifecycle": "candidate"},
        ])
        kinds = {(f["kind"], f["repository"]) for f in self.ws.drift(observed, registry)}
        self.assertEqual(kinds, {
            (self.ws.OBSERVED_UNCLASSIFIED, "Quirk-Systems/quirk-new"),
            (self.ws.STATE_MISMATCH, "Quirk-Systems/quirk-live"),
            (self.ws.STATE_MISMATCH, "Quirk-Systems/quirk-held"),
            (self.ws.NOT_IN_WORKSPACE, "bryansayler/quirk-elsewhere"),
        })

    def test_names_compare_case_insensitively(self):
        observed = [self.observed("quirk-systems/quirk", self.ws.DOCS_ONLY)]
        registry = inventory([{"repository": "Quirk-Systems/Quirk", "lifecycle": "reserved"}])
        self.assertEqual(self.ws.drift(observed, registry), [])

    def test_findings_are_deterministic(self):
        observed = [self.observed(f"Quirk-Systems/q{i}", self.ws.EMPTY) for i in (3, 1, 2)]
        first = self.ws.drift(observed, {})
        self.assertEqual(first, self.ws.drift(list(reversed(observed)), {}))
        self.assertEqual([f["repository"] for f in first], ["Quirk-Systems/q1", "Quirk-Systems/q2", "Quirk-Systems/q3"])

    def test_real_inventory_loads(self):
        entries = self.ws.load_inventory()
        self.assertIn("Quirk-Systems/.github", entries)


class WorkspacePinTests(unittest.TestCase):
    SHA = "a" * 40
    OTHER = "b" * 40

    def setUp(self):
        self.ws = load("quirk_workspace")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        caller = "jobs:\n  semantic:\n    uses: Quirk-Systems/.github/.github/workflows/{w}@{ref} # main\n"
        make_repo(self.root, "floating", {".github/workflows/a.yml": caller.format(w="quirk-semantic-governance.yml", ref="main")})
        make_repo(self.root, "pinned", {".github/workflows/a.yml": caller.format(w="reusable-evidence-binding.yml", ref=self.SHA)})
        make_repo(self.root, "other", {".github/workflows/a.yml": caller.format(w="reusable-evidence-binding.yml", ref=self.OTHER)})
        make_repo(self.root, "local", {".github/workflows/a.yml": "jobs:\n  x:\n    uses: ./.github/workflows/reusable-validate.yml\n"})
        make_repo(self.root, "dquoted", {".github/workflows/a.yml": caller.format(w="quirk-semantic-governance.yml", ref="main").replace("uses: ", 'uses: "').replace(" # main", '" # main')})
        make_repo(self.root, "squoted", {".github/workflows/a.yml": caller.format(w="quirk-semantic-governance.yml", ref=self.SHA).replace("uses: ", "uses: '").replace(" # main", "' # main")})
        make_repo(self.root, "spaced", {".github/workflows/a.yml": caller.format(w="reusable-evidence-binding.yml", ref="main").replace("uses: ", "uses : ")})
        make_repo(self.root, "lowercase", {".github/workflows/a.yml": caller.format(w="reusable-evidence-binding.yml", ref="main").replace("Quirk-Systems/", "quirk-systems/")})
        make_repo(self.root, "mismatched", {".github/workflows/a.yml": caller.format(w="quirk-semantic-governance.yml", ref="main").replace("uses: ", 'uses: "')})

    def tearDown(self):
        self.tmp.cleanup()

    def statuses(self, expect=None):
        rows = self.ws.caller_pins(self.root, self.ws.scan(self.root), expect)
        return {row["repository"]: (row["status"], row["file"]) for row in rows}

    def test_classifies_refs(self):
        self.assertEqual(self.statuses(), {
            "Quirk-Systems/floating": (self.ws.FLOATING, ".github/workflows/a.yml:3"),
            "Quirk-Systems/pinned": (self.ws.PINNED, ".github/workflows/a.yml:3"),
            "Quirk-Systems/other": (self.ws.PINNED, ".github/workflows/a.yml:3"),
            "Quirk-Systems/dquoted": (self.ws.FLOATING, ".github/workflows/a.yml:3"),
            "Quirk-Systems/squoted": (self.ws.PINNED, ".github/workflows/a.yml:3"),
            "Quirk-Systems/lowercase": (self.ws.FLOATING, ".github/workflows/a.yml:3"),
            "Quirk-Systems/spaced": (self.ws.FLOATING, ".github/workflows/a.yml:3"),
        })

    def test_expect_marks_other_shas_off_target(self):
        seen = self.statuses(self.SHA)
        self.assertEqual(seen["Quirk-Systems/pinned"][0], self.ws.PINNED)
        self.assertEqual(seen["Quirk-Systems/other"][0], self.ws.OFF_TARGET)

    def test_cli_exit_codes(self):
        base = ["--workspace", self.root]
        self.assertEqual(self.ws.main([*base, "pins"]), 0)
        self.assertEqual(self.ws.main([*base, "pins", "--fail-on-floating"]), 1)
        self.assertEqual(self.ws.main([*base, "pins", "--expect", "main"]), 2)


class WorkspaceCliTests(unittest.TestCase):
    def setUp(self):
        self.ws = load("quirk_workspace")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        make_repo(self.root, "quirk-new")
        self.registry = Path(self.root) / "inventory.json"
        self.registry.write_text(json.dumps({"repositories": []}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_fail_on_drift_sets_exit_code(self):
        base = ["--workspace", self.root, "--registry", str(self.registry)]
        self.assertEqual(self.ws.main([*base, "drift"]), 0)
        self.assertEqual(self.ws.main([*base, "drift", "--fail-on-drift"]), 1)

    def test_run_skips_repositories_without_a_command(self):
        results = self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=5)
        self.assertEqual(results, [("Quirk-Systems/quirk-new", None, "no declared validation command")])

    def test_json_flag_works_before_or_after_the_subcommand(self):
        import contextlib
        import io

        for argv in (["--json", "--workspace", self.root, "scan"], ["--workspace", self.root, "scan", "--json"]):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(self.ws.main(argv), 0)
            self.assertEqual(json.loads(buffer.getvalue())[0]["repository"], "Quirk-Systems/quirk-new")

    def test_run_reports_a_command_that_cannot_launch(self):
        path = make_repo(self.root, "noexec", {"scripts/validate.sh": "#!/bin/sh\nexit 0\n"})
        (path / "scripts" / "validate.sh").chmod(0o644)
        results = dict((repo, (code, note)) for repo, code, note in self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=5))
        code, note = results["Quirk-Systems/noexec"]
        self.assertEqual(code, 126)
        self.assertTrue(note.startswith("not run:"), note)
        self.assertEqual(self.ws.main(["--workspace", self.root, "commands", "--run", "--timeout", "5"]), 1)

    def test_run_treats_a_timeout_as_a_failure(self):
        make_repo(self.root, "slow", {"scripts/validate.sh": "#!/bin/sh\nsleep 5\n"})
        (Path(self.root) / "slow" / "scripts" / "validate.sh").chmod(0o755)
        results = {repo: (code, note) for repo, code, note in self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=1)}
        self.assertEqual(results["Quirk-Systems/slow"], (124, "timed out after 1s"))
        self.assertEqual(results["Quirk-Systems/quirk-new"][0], None)

    def test_timeout_stops_processes_the_check_started(self):
        path = make_repo(self.root, "spawner", {"scripts/validate.sh": "#!/bin/sh\n(sleep 2; touch late-write) &\nsleep 30\n"})
        (path / "scripts" / "validate.sh").chmod(0o755)
        results = {repo: code for repo, code, _ in self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=1)}
        self.assertEqual(results["Quirk-Systems/spawner"], 124)
        time.sleep(2.5)
        self.assertFalse((path / "late-write").exists())

    def test_success_stops_processes_the_check_left_behind(self):
        path = make_repo(self.root, "leaver", {"scripts/validate.sh": "#!/bin/sh\n(sleep 2; touch late-write) &\nexit 0\n"})
        (path / "scripts" / "validate.sh").chmod(0o755)
        results = {repo: code for repo, code, _ in self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=30)}
        self.assertEqual(results["Quirk-Systems/leaver"], 0)
        time.sleep(2.5)
        self.assertFalse((path / "late-write").exists())

    def test_interrupt_stops_processes_the_check_started(self):
        path = make_repo(self.root, "spawner", {"scripts/validate.sh": "#!/bin/sh\n(sleep 2; touch late-write) &\nsleep 30\n"})
        (path / "scripts" / "validate.sh").chmod(0o755)
        real_wait = subprocess.Popen.wait

        def interrupted(process, timeout=None):
            if timeout is not None:
                raise KeyboardInterrupt
            return real_wait(process)

        with unittest.mock.patch.object(subprocess.Popen, "wait", interrupted):
            with self.assertRaises(KeyboardInterrupt):
                self.ws.run_commands(self.root, self.ws.scan(self.root), timeout=60)
        time.sleep(2.5)
        self.assertFalse((path / "late-write").exists())

    def test_commands_honours_json_in_either_position(self):
        import contextlib
        import io

        make_repo(self.root, "app", {"package.json": json.dumps({"scripts": {"validate": "true"}})})
        for argv in (["--json", "--workspace", self.root, "commands"], ["--workspace", self.root, "commands", "--json"]):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(self.ws.main(argv), 0)
            self.assertEqual(json.loads(buffer.getvalue()), [{"repository": "Quirk-Systems/app", "command": "npm run validate"}])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.ws.main(["--workspace", self.root, "commands", "--run", "--json", "--timeout", "5"])
        rows = {row["repository"]: row for row in json.loads(buffer.getvalue())}
        self.assertIsNone(rows["Quirk-Systems/quirk-new"]["exit_code"])

    def test_bad_workspace_exits_two(self):
        self.assertEqual(self.ws.main(["--workspace", str(Path(self.root) / "nope"), "scan"]), 2)


if __name__ == "__main__":
    unittest.main()
