#!/usr/bin/env python3
"""Local execution records and read-only GitHub recovery evidence. No status writes."""

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REQUIRED = {
    ".github/workflows/golden-gates.yml": {
        "structural-integrity": ["Verify exact source head", "Validate Golden Project Pack", "Inspect current admission work and enforce evidence boundaries"],
    },
    ".github/workflows/evidence-binding.yml": {
        "validate / validate": ["Validate caller evidence bindings"],
    },
    ".github/workflows/validate-agents.yml": {
        "agent-candidate-conformance": ["Verify exact source head", "Run agent manifest unit and adversarial tests", "Run agent candidate conformance"],
    },
    ".github/workflows/one-to-infinity-candidate.yml": {
        "one-to-infinity-candidate-conformance": ["Test exact-head receipt guards", "Validate candidate pack", "Bind source head and evidence digests"],
    },
}


def now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(root, expected, output, command, timeout):
    """Execute an explicitly supplied, reviewed command; this is not a sandbox."""
    root, output = Path(root).resolve(), Path(output).resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", expected) or git(root, "rev-parse", "HEAD") != expected:
        raise ValueError("expected full SHA must equal checked-out HEAD")
    if output.is_relative_to(root):
        raise ValueError("output must be outside the source checkout")
    if git(root, "status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("commit or remove working-tree changes before capturing evidence")
    if not command or timeout <= 0:
        raise ValueError("a reviewed argv command and positive timeout are required")
    output.mkdir(parents=True, exist_ok=False)
    log = output / "command.log"
    record = {
        "format": "quirk-local-execution-v1", "authority_effect": "none",
        "evidence_kind": "assistant_or_operator_local_execution",
        "hosted_validation": "NOT_RUN", "merge_authorized": False,
        "source_head": expected, "source_tree": git(root, "rev-parse", "HEAD^{tree}"),
        "command": command, "executable_resolved": shutil.which(command[0]),
        "started_at": now(), "timeout_seconds": timeout,
        "platform": platform.platform(), "capture_python": platform.python_version(),
        "git_version": git(root, "--version"),
    }
    with log.open("wb") as stream:
        try:
            process = subprocess.Popen(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == "posix"))
            try:
                code = process.wait(timeout=timeout)
                outcome = "COMMAND_PASSED" if code == 0 else "COMMAND_FAILED"
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                code, outcome = 124, "TIMED_OUT"
        except OSError as error:
            stream.write(f"{type(error).__name__}: {error}\n".encode())
            code, outcome = 127, "NOT_RUN"
    dirty = bool(git(root, "status", "--porcelain", "--untracked-files=normal"))
    final_head = git(root, "rev-parse", "HEAD")
    if dirty or final_head != expected:
        outcome = "SOURCE_CHANGED"
    record.update(finished_at=now(), exit_code=code, outcome=outcome,
                  final_head=final_head, working_tree_changed=dirty,
                  log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    write_json(output / "execution.json", record)
    return record


def classify_job(job, annotations):
    messages = " ".join(a.get("message", "") for a in annotations).lower()
    executed = [s for s in job.get("steps", []) if s.get("status") == "completed"
                and s.get("conclusion") not in (None, "skipped")]
    if "billing" in messages and ("locked" in messages or "payment" in messages):
        return "BILLING_BLOCK_CONFIRMED"
    if job.get("status") != "completed":
        return "PENDING"
    if job.get("conclusion") == "skipped":
        return "NOT_RUN"
    if not executed:
        return "STARTUP_BLOCK_CAUSE_UNKNOWN"
    return "EXECUTED_SUCCESS" if job.get("conclusion") == "success" else "EXECUTED_FAILURE"


def assess(snapshot):
    """Check each requested workflow independently; never infer merge authority."""
    results = {}
    for path, jobs_needed in REQUIRED.items():
        candidates = [r for r in snapshot["runs"] if r.get("path") == path
                      and r.get("event") == "pull_request"
                      and r.get("head_sha") == snapshot["head_sha"]]
        if not candidates:
            results[path] = {"state": "NOT_RUN"}
            continue
        run = max(candidates, key=lambda r: (r["id"], r.get("run_attempt", 1)))
        jobs = {j["name"]: j for j in run.get("jobs", [])}
        passed = run.get("conclusion") == "success" and not run.get("jobs_error")
        for name, steps in jobs_needed.items():
            job = jobs.get(name, {})
            observed = {s["name"] for s in job.get("steps", [])
                        if s.get("status") == "completed" and s.get("conclusion") == "success"}
            passed = passed and (job.get("conclusion") == "success" and bool(job.get("runner_id"))
                                 and set(steps).issubset(observed))
        # A green required job alongside a failed/skipped matrix sibling is not a full pass.
        passed = passed and bool(jobs) and all(classify_job(j, []) == "EXECUTED_SUCCESS" for j in jobs.values())
        results[path] = {"state": "EXECUTED_SUCCESS" if passed else "HOLD",
                         "run_id": run["id"], "attempt": run.get("run_attempt", 1),
                         "jobs": [{"id": j["id"], "name": j["name"],
                                   "state": classify_job(j, j.get("annotations", []))} for j in jobs.values()]}
    stable = (snapshot.get("final_head_sha") == snapshot["head_sha"]
              and snapshot.get("final_base_sha") == snapshot.get("base_sha"))
    return {"authority_effect": "none", "merge_authorized": False,
            "subject_stable_during_collection": stable, "checks": results,
            "state": "HOSTED_STEPS_VERIFIED" if stable and all(
                c["state"] == "EXECUTED_SUCCESS" for c in results.values()) else "HOLD",
            "limits": "Does not verify checkout logs, current protection rules, independent review, smoke, or merge eligibility."}


class GitHub:
    """GET only, bounded pagination, no credential discovery or automatic retries."""

    def get(self, path):
        if not path.startswith("/repos/"):
            raise ValueError("repository endpoints only")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "quirk-ci-continuity"}
        token = os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request("https://api.github.com" + path, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    def pages(self, path, field=None):
        items = []
        for page in range(1, 101):
            data = self.get(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            batch = data[field] if field else data
            items.extend(batch)
            if len(batch) < 100:
                return items
        raise ValueError("pagination limit reached: incomplete evidence")


def collect(api, repository, pr):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or pr <= 0:
        raise ValueError("invalid repository or PR")
    prefix = f"/repos/{repository}"
    pull = api.get(f"{prefix}/pulls/{pr}")
    head = pull["head"]["sha"]
    snapshot = {"repository": repository, "pr": pr, "head_sha": head,
                "base_sha": pull["base"]["sha"], "observed_at": now(), "runs": []}
    for run in api.pages(f"{prefix}/actions/runs?head_sha={head}", "workflow_runs"):
        item = {k: run[k] for k in ("id", "path", "head_sha", "event", "conclusion", "run_attempt", "html_url")}
        item["jobs"] = api.pages(f"{prefix}/actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs", "jobs")
        for job in item["jobs"]:
            try:
                job["annotations"] = api.pages(f"{prefix}/check-runs/{job['id']}/annotations")
            except urllib.error.HTTPError as error:
                job["annotations"] = []
                job["annotations_unavailable"] = error.code
            job["classification"] = classify_job(job, job["annotations"])
        snapshot["runs"].append(item)
    final = api.get(f"{prefix}/pulls/{pr}")
    snapshot["final_head_sha"] = final["head"]["sha"]
    snapshot["final_base_sha"] = final["base"]["sha"]
    snapshot["assessment"] = assess(snapshot)
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    local = commands.add_parser("capture", help="run one reviewed local command; never publish a GitHub status")
    local.add_argument("--root", required=True)
    local.add_argument("--expect-head", required=True)
    local.add_argument("--output", required=True)
    local.add_argument("--timeout", type=int, default=900)
    local.add_argument("command", nargs=argparse.REMAINDER)
    remote = commands.add_parser("collect", help="read current PR head, runs, jobs and annotations")
    remote.add_argument("--repository", default="Quirk-Systems/quirk-os", choices=["Quirk-Systems/quirk-os"])
    remote.add_argument("--pr", type=int, default=62)
    remote.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.operation == "capture":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            result = capture(args.root, args.expect_head, args.output, command, args.timeout)
            print(json.dumps(result, indent=2))
            return 0 if result["outcome"] == "COMMAND_PASSED" else 1
        output = Path(args.output)
        if output.exists():
            raise ValueError("use a new output path; evidence is append-only")
        result = collect(GitHub(), args.repository, args.pr)
        write_json(output, result)
        print(json.dumps(result["assessment"], indent=2))
        return 0 if result["assessment"]["state"] == "HOSTED_STEPS_VERIFIED" else 1
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
