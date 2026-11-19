"""Regressions for false-green recovery and misattributed local evidence."""

import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest import mock

from scripts import ci_continuity
from scripts.ci_continuity import REQUIRED, assess, capture, classify_job, collect


def successful_snapshot():
    runs = []
    for index, (path, expected) in enumerate(REQUIRED.items(), 1):
        jobs = [{"id": index, "name": name, "runner_id": 23, "status": "completed", "conclusion": "success",
                 "steps": [{"name": step, "status": "completed", "conclusion": "success"} for step in steps]}
                for name, steps in expected.items()]
        runs.append({"id": index, "path": path, "head_sha": "a" * 40, "event": "pull_request",
                     "conclusion": "success", "run_attempt": 1, "jobs": jobs})
    return {"head_sha": "a" * 40, "final_head_sha": "a" * 40,
            "base_sha": "b" * 40, "final_base_sha": "b" * 40, "runs": runs}


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

    def test_executed_steps_take_precedence_over_billing_annotations(self):
        annotation = {"message": "The job was not started because your account is locked due to a billing issue."}
        for conclusion, expected in (("success", "EXECUTED_SUCCESS"), ("failure", "EXECUTED_FAILURE")):
            with self.subTest(conclusion=conclusion):
                snapshot = successful_snapshot()
                run = snapshot["runs"][0]
                job = run["jobs"][0]
                job.update(conclusion=conclusion, annotations=[annotation])
                job["steps"][0]["conclusion"] = conclusion
                check = assess(snapshot)["checks"][run["path"]]
                self.assertEqual(check["jobs"][0]["state"], expected)
                self.assertEqual(check["state"], expected if conclusion == "success" else "HOLD")

    def test_unobserved_steps_and_nonexecuting_jobs_do_not_confirm_billing(self):
        annotation = {"message": "account is locked due to a billing issue"}
        for status, conclusion, steps, expected in (
            ("completed", "failure", None, "STEPS_UNAVAILABLE"),
            ("queued", None, [], "PENDING"),
            ("completed", "skipped", [], "NOT_RUN"),
        ):
            with self.subTest(status=status, conclusion=conclusion):
                snapshot = successful_snapshot()
                run = snapshot["runs"][0]
                run["jobs"][0].update(steps=steps, status=status, conclusion=conclusion, annotations=[annotation])
                check = assess(snapshot)["checks"][run["path"]]
                self.assertEqual(check["state"], "HOLD")
                self.assertEqual(check["jobs"][0]["state"], expected)
        job = {"status": "completed", "conclusion": "failure", "steps": []}
        self.assertEqual(classify_job(job, [{"message": "Lint warning in billing/payment.py"}]),
                         "STARTUP_BLOCK_CAUSE_UNKNOWN")

    def test_duplicate_job_name_keeps_failed_sibling_and_denies_pass(self):
        snapshot = successful_snapshot()
        run = snapshot["runs"][0]
        failed = copy.deepcopy(run["jobs"][0])
        failed.update(id=888, conclusion="failure")
        run["jobs"].insert(0, failed)
        check = assess(snapshot)["checks"][run["path"]]
        self.assertEqual(check["state"], "HOLD")
        self.assertEqual([j["id"] for j in check["jobs"]], [888, run["jobs"][1]["id"]])

    def test_unobserved_base_is_not_a_stable_subject(self):
        snapshot = successful_snapshot()
        del snapshot["base_sha"], snapshot["final_base_sha"]
        self.assertFalse(assess(snapshot)["subject_stable_during_collection"])
        self.assertEqual(assess(snapshot)["state"], "HOLD")

    def test_collection_cannot_replace_a_receipt_created_while_fetching(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "hosted.json"

            def competing_writer(*args):
                output.write_bytes(b"other collection\n")
                return {"assessment": {"state": "HOLD"}}

            with mock.patch.object(sys, "argv", ["ci_continuity", "collect", "--output", str(output)]), \
                    mock.patch.object(ci_continuity, "collect", side_effect=competing_writer), \
                    mock.patch("sys.stderr", new_callable=io.StringIO), \
                    mock.patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(ci_continuity.main(), 2)
            self.assertEqual(output.read_bytes(), b"other collection\n")
            self.assertEqual(list(output.parent.iterdir()), [output])

    def test_publication_failure_leaves_no_partial_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "hosted.json"
            with self.assertRaises(TypeError):
                ci_continuity.write_json(output, {"a_valid_prefix": 1, "z_invalid": object()})
            self.assertEqual(list(output.parent.iterdir()), [])
            ci_continuity.write_json(output, {"valid": 1})
            self.assertEqual(json.loads(output.read_bytes()), {"valid": 1})

    def test_concurrent_publication_preserves_one_complete_winner(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "hosted.json"
            ready = Barrier(2)

            def publish(writer):
                ready.wait(timeout=5)
                try:
                    ci_continuity.write_json(output, {"writer": writer})
                except FileExistsError:
                    return None
                return writer

            with ThreadPoolExecutor(max_workers=2) as pool:
                winners = [writer for writer in pool.map(publish, ("one", "two")) if writer]
            self.assertEqual(len(winners), 1)
            self.assertEqual(json.loads(output.read_bytes()), {"writer": winners[0]})
            self.assertEqual(list(output.parent.iterdir()), [output])

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

    def test_large_output_is_retained_including_the_final_buffer(self):
        result = self.run_command("verbose", "import sys; sys.stdout.buffer.write(b'x' * 1048576 + b'end')")
        expected = b"x" * 1048576 + b"end"
        self.assertEqual(result["outcome"], "COMMAND_PASSED")
        self.assertEqual((self.parent / "verbose" / "command.log").read_bytes(), expected)
        self.assertEqual(result["log_sha256"], hashlib.sha256(expected).hexdigest())

    @unittest.skipUnless(os.name == "posix", "requires creation of a new session")
    def test_detached_writer_cannot_change_a_finalized_log(self):
        release, done = self.parent / "release", self.parent / "done"
        writer = (
            "from pathlib import Path\n"
            "import os, time\n"
            "deadline = time.monotonic() + 5\n"
            f"while not Path({str(release)!r}).exists() and time.monotonic() < deadline: time.sleep(.01)\n"
            "try: os.write(1, b'late write')\n"
            "except BrokenPipeError: pass\n"
            f"Path({str(done)!r}).touch()\n"
        )
        command = (
            "import subprocess, sys\n"
            f"subprocess.Popen([sys.executable, '-c', {writer!r}], start_new_session=True)\n"
        )
        try:
            result = self.run_command("detached", command)
        finally:
            release.touch()
        deadline = time.monotonic() + 3
        while not done.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertTrue(done.exists(), "the descendant must actually attempt its delayed write")
        self.assertEqual(result["outcome"], "BACKGROUND_PROCESSES")
        log = (self.parent / "detached" / "command.log").read_bytes()
        self.assertNotIn(b"late write", log)
        self.assertEqual(result["log_sha256"], hashlib.sha256(log).hexdigest())

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_background_writer_is_stopped_before_return_and_log_is_stable(self):
        self.check_group_cleanup("", "BACKGROUND_PROCESSES")

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_timeout_also_stops_the_background_writer(self):
        self.check_group_cleanup("time.sleep(30)", "TIMED_OUT")

    def check_group_cleanup(self, leader_tail, outcome):
        import fcntl

        lock, release = self.parent / "child.lock", self.parent / "release"
        child = (
            "import fcntl, time\n"
            "from pathlib import Path\n"
            f"with open({str(lock)!r}, 'w') as handle:\n"
            " fcntl.flock(handle, fcntl.LOCK_EX)\n"
            " print('child ready', flush=True)\n"
            " handle.write('ready'); handle.flush()\n"
            " deadline = time.monotonic() + 8\n"
            f" while not Path({str(release)!r}).exists() and time.monotonic() < deadline: time.sleep(.01)\n"
        )
        command = (
            "import subprocess, sys, time\n"
            "from pathlib import Path\n"
            f"subprocess.Popen([sys.executable, '-c', {child!r}])\n"
            f"lock = Path({str(lock)!r})\n"
            "while not (lock.exists() and lock.stat().st_size): time.sleep(.005)\n"
            f"{leader_tail}\n"
        )
        try:
            result = self.run_command("background", command, timeout=2)
            self.assertEqual(result["outcome"], outcome)
            with lock.open() as handle:
                # Allow the kernel to deliver SIGKILL and release the lock.
                deadline = time.monotonic() + 2
                while True:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            self.fail("capture left the background writer running")
                        time.sleep(.01)
            log = (self.parent / "background" / "command.log").read_bytes()
            self.assertIn(b"child ready", log)
            self.assertEqual(hashlib.sha256(log).hexdigest(), result["log_sha256"])
        finally:
            release.touch()

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
