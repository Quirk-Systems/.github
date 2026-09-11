import tempfile
import unittest
from pathlib import Path

from scripts.validate_workflow_hygiene import validate_workflows


class WorkflowHygieneTests(unittest.TestCase):
    def write(self, directory, name, content):
        path = Path(directory) / ".github" / "workflows" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_reusable_workflow_passes_without_concurrency(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(
                directory,
                "valid.yml",
                """name: Valid\non:\n  workflow_call:\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955\n""",
            )
            self.assertEqual(validate_workflows(Path(directory), ".github/workflows"), [])

    def test_push_workflow_requires_concurrency(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(
                directory,
                "missing-concurrency.yml",
                """name: Missing concurrency\non:\n  push:\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955\n""",
            )
            errors = validate_workflows(Path(directory), ".github/workflows")
            self.assertEqual(len(errors), 1)
            self.assertIn("missing top-level concurrency", errors[0])

    def test_unpinned_action_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(
                directory,
                "unpinned.yml",
                """name: Unpinned\non:\n  workflow_call:\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n""",
            )
            errors = validate_workflows(Path(directory), ".github/workflows")
            self.assertEqual(len(errors), 1)
            self.assertIn("pin a full commit SHA", errors[0])

    def test_missing_permissions_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(
                directory,
                "missing-permissions.yml",
                """name: Missing permissions\non:\n  workflow_call:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955\n""",
            )
            errors = validate_workflows(Path(directory), ".github/workflows")
            self.assertEqual(len(errors), 1)
            self.assertIn("missing top-level permissions", errors[0])

    def test_unsafe_triggers_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write(
                directory,
                "unsafe.yml",
                """name: Unsafe\non:\n  pull_request_target:\npermissions:\n  contents: read\nconcurrency:\n  group: test\n  cancel-in-progress: true\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955\n""",
            )
            errors = validate_workflows(Path(directory), ".github/workflows")
            self.assertEqual(len(errors), 1)
            self.assertIn("unsafe trigger", errors[0])


if __name__ == "__main__":
    unittest.main()
