"""Regression checks for safe runner selection and exact-head preflight evidence."""

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/reusable-validate.yml"


def environment_check():
    text = WORKFLOW.read_text(encoding="utf-8")
    section = text.split("      - name: Validate runner choice and record exact environment\n", 1)[1]
    section = section.split("\n      - name:", 1)[0]
    return "\n".join(line[10:] for line in section.split("        run: |\n", 1)[1].splitlines())


class UbuntuPreflightTests(unittest.TestCase):
    def check_environment(self, image, head):
        env = dict(os.environ, UBUNTU_IMAGE=image, EXPECTED_HEAD=head,
                   ImageOS="local-test", ImageVersion="local-test")
        return subprocess.run(["bash", "-e", "-c", environment_check()], cwd=ROOT,
                              env=env, capture_output=True, text=True)

    def test_unsupported_images_cannot_reach_setup_or_caller_commands(self):
        for image in ("self-hosted", "ubuntu-22.04", "", "ubuntu-26.04; touch /tmp/bad"):
            result = self.check_environment(image, "unused")
            self.assertNotEqual(result.returncode, 0, image)
            self.assertIn("Unsupported Ubuntu runner choice", result.stderr)
            self.assertNotIn("commit=", result.stdout)

    def test_exact_head_mismatch_fails_before_setup(self):
        result = self.check_environment("ubuntu-26.04", "0" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("commit=", result.stdout)

    def test_supported_images_record_the_actual_subject(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        for image in ("ubuntu-latest", "ubuntu-24.04", "ubuntu-26.04"):
            result = self.check_environment(image, head)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("commit=" + head, result.stdout)

    def test_runner_selection_is_a_closed_mapping_with_the_original_default(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        runner = re.search(r"^    runs-on: (.+)$", text, re.M).group(1)
        self.assertEqual(runner, "${{ inputs.ubuntu-image == 'ubuntu-26.04' && 'ubuntu-26.04' || "
                         "inputs.ubuntu-image == 'ubuntu-24.04' && 'ubuntu-24.04' || 'ubuntu-latest' }}")
        self.assertIn("        default: ubuntu-latest", text.split("      ubuntu-image:", 1)[1])
        caller = (ROOT / ".github/workflows/governance-contracts.yml").read_text(encoding="utf-8")
        self.assertIn("image: [ubuntu-24.04, ubuntu-26.04]", caller)
        self.assertIn("uses: ./.github/workflows/reusable-validate.yml", caller)
        self.assertIn("      run-e2e: true", caller)


if __name__ == "__main__":
    unittest.main()
