"""Exercise strict preflight without depending on the host's lint tool set."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate.sh"
BASH = shutil.which("bash")


class ValidationEntrypointTests(unittest.TestCase):
    def run_script(self, *args, python="python3", tools=()):
        with tempfile.TemporaryDirectory() as directory:
            for tool in tools:
                path = Path(directory) / tool
                # If preflight leaks into execution, expose it immediately.
                path.write_text("#!/bin/sh\necho UNEXPECTED_EXECUTION >&2\nexit 99\n")
                path.chmod(0o755)
            env = {**os.environ, "PATH": directory, "PYTHON": python}
            return subprocess.run(
                [BASH, str(SCRIPT), *args], env=env,
                capture_output=True, text=True, check=False,
            )

    def test_missing_tools_fail_before_execution(self):
        result = self.run_script("--require-tools")
        self.assertEqual(result.returncode, 2)
        self.assertIn("REQUIRED TOOLS MISSING: python3 ruff actionlint zizmor", result.stderr)
        self.assertNotIn("==>", result.stdout)

    def test_uv_does_not_satisfy_strict_zizmor_requirement(self):
        result = self.run_script(
            "--require-tools", tools=("python3", "ruff", "actionlint", "uv"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("REQUIRED TOOLS MISSING: zizmor", result.stderr)
        self.assertNotIn("UNEXPECTED_EXECUTION", result.stderr)

    def test_configured_python_is_checked(self):
        result = self.run_script(
            "--require-tools", python="custom-python",
            tools=("python3", "ruff", "actionlint", "zizmor"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("REQUIRED TOOLS MISSING: custom-python", result.stderr)

    def test_help_needs_no_tools(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)

    def test_unknown_or_extra_arguments_fail(self):
        for args in (("--typo",), ("--require-tools", "extra")):
            with self.subTest(args=args):
                result = self.run_script(*args)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("==>", result.stdout)
