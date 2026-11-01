"""Regressions for false-green recovery and misattributed local evidence."""

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ci_continuity import REQUIRED, assess, capture, classify_job, collect


def successful_snapshot():
    runs = []
    for index, (path, expected) in enumerate(REQUIRED.items(), 1):
        jobs = [{"id": index, "name": name, "runner_id": 23, "status": "completed", "conclusion": "success",
                 "steps": [{"name": step, "status": "completed", "conclusion": "success"} for step in steps]}
                for name, steps in expected.items()]
        runs.append({"id": index, "path": path, "head_sha": "a" * 40, "event": "pull_request",
                     "conclusion": "success", "run_attempt": 1, "jobs": jobs})
    return {"head_sha": "a" * 40, "final_head_sha": "a" * 40, "runs": runs}


class RecoveryTests(unittest.TestCase):
    def test_each_gate_requires_actual_successful_named_steps(self):
        snapshot = successful_snapshot()
        self.assertEqual(assess(snapshot)["state"], "HOSTED_STEPS_VERIFIED")
        self.assertFalse(assess(snapshot)["merge_authorized"])
        for index in range(4):
            for mutation in ("empty", "skipped", "failed", "runnerless", "wrong_step"):
                with self.subTest(gate=index, mutation=mutation):
                    changed = copy.deepcopy(snapshot)
                    job = changed["runs"][index]["jobs"][0]
                    if mutation == "empty":
                        job["steps"] = []
                    elif mutation == "runnerless":
                        job["runner_id"] = 0
                    elif mutation == "wrong_step":
                        job["steps"][0]["name"] = "Set up job"
                    else:
                        job["steps"][0]["conclusion"] = mutation
                    self.assertEqual(assess(changed)["state"], "HOLD")

    def test_old_head_and_push_only_and_missing_workflow_hold(self):
        for key, value in (("head_sha", "b" * 40), ("event", "push"), ("path", "unknown.yml")):
            snapshot = successful_snapshot()
            snapshot["runs"][0][key] = value
            self.assertEqual(assess(snapshot)["state"], "HOLD")

    def test_head_changes_and_latest_failed_run_and_skipped_sibling_hold(self):
        snapshot = successful_snapshot()
        snapshot["final_head_sha"] = "b" * 40
        self.assertEqual(assess(snapshot)["state"], "HOLD")
        snapshot = successful_snapshot()
        snapshot.update(base_sha="b" * 40, final_base_sha="c" * 40)
        self.assertEqual(assess(snapshot)["state"], "HOLD")
        snapshot = successful_snapshot()
        latest = copy.deepcopy(snapshot["runs"][0])
        latest.update(id=100, conclusion="failure")
        snapshot["runs"].append(latest)
        self.assertEqual(assess(snapshot)["state"], "HOLD")
        snapshot = successful_snapshot()
        sibling = copy.deepcopy(snapshot["runs"][0]["jobs"][0])
        sibling.update(name="matrix sibling", conclusion="skipped")
        snapshot["runs"][0]["jobs"].append(sibling)
        self.assertEqual(assess(snapshot)["state"], "HOLD")

    def test_billing_requires_annotation_not_zero_steps_alone(self):
        job = {"status": "completed", "conclusion": "failure", "runner_id": 0, "steps": []}
        self.assertEqual(classify_job(job, []), "STARTUP_BLOCK_CAUSE_UNKNOWN")
        self.assertEqual(classify_job(job, [{"message": "account is locked due to a billing issue"}]),
                         "BILLING_BLOCK_CONFIRMED")
        job["conclusion"] = "skipped"
        self.assertEqual(classify_job(job, []), "NOT_RUN")

    def test_collector_binds_attempt_and_reads_head_again(self):
        class Fake:
            calls = []

            def get(self, path):
                self.calls.append(path)
                return {"head": {"sha": "a" * 40}, "base": {"sha": "b" * 40}}

            def pages(self, path, field=None):
                self.calls.append(path)
                if field == "workflow_runs":
                    return [{"id": 77, "path": "x.yml", "head_sha": "a" * 40,
                             "event": "pull_request", "conclusion": "failure", "run_attempt": 2, "html_url": "url"}]
                return []

        api = Fake()
        result = collect(api, "Quirk-Systems/quirk-os", 62)
        self.assertTrue(any("/runs/77/attempts/2/jobs" in p for p in api.calls))
        self.assertEqual(sum(p.endswith("/pulls/62") for p in api.calls), 2)
        self.assertEqual(result["assessment"]["state"], "HOLD")


class LocalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "source"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / "tracked").write_text("original")
        self.git("add", "tracked")
        self.git("commit", "-qm", "fixture")
        self.head = self.git("rev-parse", "HEAD")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True).strip()

    def run_command(self, name, code, timeout=10):
        return capture(self.root, self.head, self.parent / name, [sys.executable, "-c", code], timeout)

    def test_pass_is_local_only_and_logs_bound(self):
        result = self.run_command("pass", "print('real execution')")
        self.assertEqual(result["outcome"], "COMMAND_PASSED")
        self.assertEqual(result["hosted_validation"], "NOT_RUN")
        self.assertFalse(result["merge_authorized"])
        self.assertEqual(len(result["log_sha256"]), 64)
        self.assertTrue((self.parent / "pass" / "execution.json").exists())

    def test_failure_timeout_missing_executable_never_pass(self):
        self.assertEqual(self.run_command("fail", "raise SystemExit(3)")["exit_code"], 3)
        self.assertEqual(self.run_command("timeout", "import time; time.sleep(20)", 1)["outcome"], "TIMED_OUT")
        result = capture(self.root, self.head, self.parent / "missing", ["/nonexistent/quirk-executable"], 1)
        self.assertEqual(result["outcome"], "NOT_RUN")

    def test_wrong_head_dirty_source_and_internal_output_rejected(self):
        with self.assertRaises(ValueError):
            capture(self.root, "b" * 40, self.parent / "wrong", ["true"], 1)
        with self.assertRaises(ValueError):
            capture(self.root, self.head, self.root / "output", ["true"], 1)
        (self.root / "untracked").write_text("new source")
        with self.assertRaises(ValueError):
            self.run_command("dirty", "pass")

    def test_command_mutating_source_invalidates_result(self):
        result = self.run_command("mutate", "from pathlib import Path; Path('tracked').write_text('changed')")
        self.assertEqual(result["outcome"], "SOURCE_CHANGED")

    def test_no_overwrite_of_existing_receipt(self):
        self.run_command("once", "pass")
        with self.assertRaises(FileExistsError):
            self.run_command("once", "pass")


if __name__ == "__main__":
    unittest.main()
