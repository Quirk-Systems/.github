import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "closure_harness_shadow.py"
QUEUE_PATH = ROOT / ".quirk" / "closure-wave1-queue.json"


def load_module():
    spec = importlib.util.spec_from_file_location("closure_harness_shadow", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClosureHarnessShadowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    def valid_queue(self):
        return copy.deepcopy(self.queue)

    def test_queue_is_valid(self):
        self.module.validate_queue(self.valid_queue())

    def test_queue_uses_exact_disposition_set(self):
        self.assertEqual(
            set(self.queue["allowed_dispositions"]),
            {
                "READY_FOR_MERGE",
                "READY_FOR_HUMAN_ADMISSION",
                "REVISE",
                "HOLD_CANDIDATE",
                "SUPERSEDE",
                "CLOSE_AS_REDUNDANT",
            },
        )

    def test_queue_rejects_bad_head_sha(self):
        queue = self.valid_queue()
        queue["wave_1"]["items"][0]["subject"]["head_sha"] = "deadbeef"
        with self.assertRaisesRegex(self.module.ClosureHarnessError, "head_sha"):
            self.module.validate_queue(queue)

    def test_queue_rejects_unknown_disposition(self):
        queue = self.valid_queue()
        queue["wave_1"]["items"][0]["target_disposition"] = "MERGE_NOW"
        with self.assertRaisesRegex(self.module.ClosureHarnessError, "target_disposition"):
            self.module.validate_queue(queue)

    def test_emit_passport_is_read_only_and_exact_head_bound(self):
        passport = self.module.build_passport(
            self.queue,
            repository="Quirk-Systems/.github",
            pull_request=9,
            base_sha="a" * 40,
        )
        self.assertEqual(passport["subject"]["head_sha"], "c848db6cbb83c5919ca19775295d1c534bbbceaf")
        self.assertEqual(passport["proof"]["external_writes"], 0)
        self.assertFalse(passport["authority"]["merge_granted"])
        self.assertFalse(passport["authority"]["canon_granted"])
        self.assertFalse(passport["authority"]["runtime_granted"])
        self.assertTrue(passport["disposition"]["stale_when_head_changes"])

    def test_cli_check_and_emit(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "passport.json"
            self.assertEqual(self.module.main(["--check"]), 0)
            self.assertEqual(
                self.module.main([
                    "--repository",
                    "Quirk-Systems/.github",
                    "--pull-request",
                    "9",
                    "--base-sha",
                    "b" * 40,
                    "--output",
                    str(output),
                ]),
                0,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["disposition"]["value"], "READY_FOR_HUMAN_ADMISSION")


if __name__ == "__main__":
    unittest.main()
