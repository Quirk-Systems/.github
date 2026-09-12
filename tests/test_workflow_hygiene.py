import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_workflow_hygiene import validate_workflows
from scripts.validate_workflow_hygiene import WorkflowLoader
import yaml


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

    def check_text(self, content):
        with tempfile.TemporaryDirectory() as directory:
            self.write(directory, "case.yml", content)
            return validate_workflows(Path(directory), ".github/workflows")

    def test_scalar_quoted_flow_and_aliased_triggers_are_checked(self):
        for event in ["on: pull_request_target", '"on": [pull_request_target]', "on: {pull_request_target: {}}", "event: &event pull_request_target\non: *event"]:
            with self.subTest(event=event):
                errors = self.check_text(event + "\npermissions: {}\njobs: {}\n")
                self.assertTrue(any("unsafe trigger" in e for e in errors), errors)

    def test_valid_quoted_and_nested_actions_and_permissions(self):
        action = 'owner/repo/sub/action@' + 'a' * 40
        text = '"on": [push]\npermissions: read-all\nconcurrency: build\njobs: {test: {steps: [{uses: "' + action + '"}]}}\n'
        self.assertEqual(self.check_text(text), [])

    def test_workflow_call_path_and_digest_pinned_docker(self):
        for action in ['owner/repo/.github/workflows/test.yml@' + 'a' * 40, 'docker://alpine@sha256:' + 'a' * 64]:
            self.assertEqual(self.check_text('on: workflow_call\npermissions: {}\njobs: {test: {uses: "' + action + '"}}'), [])

    def test_mutable_docker_and_expression_actions_fail(self):
        for action in ['docker://alpine:latest', '${{ inputs.action }}', 'owner/repo', 'owner/repo@main']:
            errors = self.check_text('on: workflow_call\npermissions: {}\njobs: {test: {uses: "' + action + '"}}')
            self.assertTrue(any('pin a full commit SHA' in e for e in errors), errors)

    def test_malformed_duplicate_and_missing_trigger_fail(self):
        for text in ['on: [', 'on: push\non: workflow_call\npermissions: {}\njobs: {}', 'permissions: {}\njobs: {}']:
            self.assertTrue(any('invalid workflow structure' in e for e in self.check_text(text)))

    def test_run_body_is_not_interpreted_as_workflow_metadata(self):
        text = 'on: workflow_call\npermissions: {}\njobs:\n  test:\n    steps:\n      - run: |\n          on: pull_request_target\n          uses: unpinned/repo@main\n'
        self.assertEqual(self.check_text(text), [])

    def test_merge_keys_and_empty_concurrency_fail(self):
        self.assertTrue(self.check_text('base: &base {on: workflow_call}\n<<: *base\npermissions: {}\njobs: {}'))
        self.assertTrue(any('concurrency' in e for e in self.check_text('on: push\npermissions: {}\nconcurrency: {}\njobs: {}')))

    def test_job_permission_override_cannot_escape_top_level_policy(self):
        for declaration in ['write-all', '{contents: write-all}', 'false', '[]']:
            with self.subTest(declaration=declaration):
                text = ('on: workflow_call\npermissions: read-all\njobs:\n'
                        '  test:\n    permissions: ' + declaration + '\n    steps: []\n')
                self.assertTrue(any('permissions' in e for e in self.check_text(text)))

    def test_explicit_job_permissions_and_inheritance_remain_supported(self):
        for declaration in ['', '    permissions: {}\n', '    permissions: read-all\n',
                            '    permissions: {contents: read, pull-requests: write}\n']:
            with self.subTest(declaration=declaration):
                text = ('on: workflow_call\npermissions: {}\njobs:\n  test:\n'
                        + declaration + '    steps: []\n')
                self.assertEqual(self.check_text(text), [])

    def test_job_and_service_images_require_immutable_digests(self):
        for declaration in ['container: node:latest', 'container: {image: node:20}',
                            'services: {db: {image: postgres:latest}}',
                            'container: {image: "${{ inputs.image }}"}',
                            'container: {}', 'services: {db: {}}']:
            with self.subTest(declaration=declaration):
                text = ('on: workflow_call\npermissions: {}\njobs:\n  test:\n    '
                        + declaration + '\n    steps: []\n')
                self.assertTrue(self.check_text(text))

    def test_digest_pinned_job_and_service_images_pass(self):
        image = 'ghcr.io/quirk/image@sha256:' + 'a' * 64
        for declaration in ['container: ' + image,
                            'container: {image: "' + image + '"}',
                            'services: {db: {image: "' + image + '"}}']:
            with self.subTest(declaration=declaration):
                text = ('on: workflow_call\npermissions: {}\njobs:\n  test:\n    '
                        + declaration + '\n    steps: []\n')
                self.assertEqual(self.check_text(text), [])

    def test_trusted_checker_ignores_subject_validator_and_python_modules(self):
        """Execute the actual isolated checker against attacker-owned files."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = root / '.quirk-policy' / 'scripts'
            policy.mkdir(parents=True)
            shutil.copyfile(Path(__file__).parents[1] / 'scripts/validate_workflow_hygiene.py',
                            policy / 'validate_workflow_hygiene.py')
            subject = root / '.quirk-subject'
            (subject / 'scripts').mkdir(parents=True)
            (subject / 'scripts/validate_workflow_hygiene.py').write_text('raise SystemExit(0)\n')
            (subject / 'yaml.py').write_text('raise RuntimeError("untrusted import executed")\n')
            self.write(subject, 'unsafe.yml',
                       'on: workflow_call\npermissions: {}\njobs:\n  test:\n'
                       '    steps: [{uses: actions/checkout@v4}]\n')
            result = subprocess.run(
                [sys.executable, '-I', str(policy / 'validate_workflow_hygiene.py'),
                 '--root', str(subject), '--workflows', '.github/workflows'],
                cwd=subject, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('pin a full commit SHA', result.stderr)
            self.assertNotIn('untrusted import executed', result.stderr)

    def test_reusable_job_keeps_subject_and_policy_checkouts_separate(self):
        workflow = yaml.load((Path(__file__).parents[1] /
                              '.github/workflows/workflow-hygiene.yml').read_text(),
                             Loader=WorkflowLoader)
        steps = workflow['jobs']['validate']['steps']
        checkouts = [s for s in steps if s.get('uses', '').startswith('actions/checkout@')]
        self.assertEqual([s['with']['path'] for s in checkouts],
                         ['.quirk-subject', '.quirk-policy'])
        commands = '\n'.join(s.get('run', '') for s in steps)
        self.assertIn('python -I .quirk-policy/scripts/validate_workflow_hygiene.py', commands)
        self.assertIn('--root .quirk-subject', commands)
        self.assertNotIn('python .quirk-subject/', commands)


if __name__ == "__main__":
    unittest.main()
