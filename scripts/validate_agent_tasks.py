#!/usr/bin/env python3
"""Validate Quirk agent task contracts.

Standard library only. Modes:

  (default)              validate every .quirk/agent-tasks/*.json in --root
  --file <task.json>     validate one task record
  --issue-body <file>    check an `agent-task` issue-form body: every required
                         section present and answered; writes a Markdown
                         report with --report

Beyond the schema, a task record must satisfy: the idempotency key equals
sha256(repository + base_commit + task_id + "agent-task"); no tool or path
appears in more than one of allowed / approval-gated / forbidden; forbidden
tools must include the consequential actions no agent performs alone; and
allowed paths never include forbidden paths. Passing proves shape and
internal consistency; it does not authorize, schedule, or run anything.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "agent-task.schema.json"
TASKS = ROOT / ".quirk" / "agent-tasks"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_manifest import ManifestError, _check  # noqa: E402

CONSEQUENTIAL = ("merge", "approve", "deploy", "publish", "ruleset", "secrets")
ISSUE_SECTIONS = [
    "Owning repository",
    "Base commit",
    "Bounded objective",
    "Allowed paths",
    "Forbidden paths",
    "Allowed knowledge sources",
    "Forbidden knowledge sources",
    "Allowed tools",
    "Approval-gated tools",
    "Forbidden tools",
    "Execution environment and limits",
    "Human owner",
    "Shutdown authority",
    "Agent profile and model identity",
    "Verification commands",
    "Rollback plan",
    "Residue",
]
EMPTY = {"", "_no response_", "none", "n/a", "tbd", "todo"}


class TaskError(ValueError):
    pass


def idempotency_key(task):
    material = task["repository"] + task["subject"]["base_commit"] + task["task_id"] + "agent-task"
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def validate_task(task, schema):
    try:
        _check(task, schema, "task")
    except ManifestError as error:
        raise TaskError(str(error)) from error
    expected = idempotency_key(task)
    if task["idempotency_key"] != expected:
        raise TaskError(f"idempotency_key must be {expected}")
    tools = task["tools"]
    for a, b in (("allowed", "approval_gated"), ("allowed", "forbidden"), ("approval_gated", "forbidden")):
        overlap = sorted(set(tools[a]) & set(tools[b]))
        if overlap:
            raise TaskError(f"tools listed in both {a} and {b}: {overlap}")
    forbidden_text = " ".join(tools["forbidden"]).casefold()
    missing = [word for word in CONSEQUENTIAL if word not in forbidden_text]
    if missing:
        raise TaskError(f"tools.forbidden must name the consequential actions no agent performs alone; missing: {missing}")
    if any("*" == tool.strip() or tool.strip().casefold() in {"all", "any", "everything"} for tool in tools["allowed"]):
        raise TaskError("tools.allowed cannot be a wildcard")
    paths = task["objective"]
    overlap = sorted(set(paths["allowed_paths"]) & set(paths["forbidden_paths"]))
    if overlap:
        raise TaskError(f"paths listed as both allowed and forbidden: {overlap}")
    sources = task["knowledge_sources"]
    overlap = sorted(set(sources["allowed"]) & set(sources["forbidden"]))
    if overlap:
        raise TaskError(f"knowledge sources listed as both allowed and forbidden: {overlap}")
    if task["status"] in {"authorized", "running", "completed"} and "authorize" in task["authority"]["required_next"]:
        raise TaskError(f"status {task['status']} is inconsistent with authorize still required")
    if task["status"] == "proposed" and "authorize" not in task["authority"]["required_next"]:
        raise TaskError("a proposed task must list authorize under authority.required_next")
    return task


def parse_issue_body(text):
    sections = {}
    current = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(.*?)\s*$", line)
        if heading:
            current = heading.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def check_issue_body(text):
    sections = parse_issue_body(text)
    findings = []
    for name in ISSUE_SECTIONS:
        value = sections.get(name)
        if value is None:
            findings.append(f"missing section: {name}")
        elif value.casefold() in EMPTY:
            findings.append(f"unanswered section: {name}")
    base = sections.get("Base commit", "")
    if base and base.casefold() not in EMPTY and not re.fullmatch(r"[0-9a-f]{40}", base.strip()):
        findings.append("Base commit must be a full 40-character lowercase SHA")
    for name in ("Human owner", "Shutdown authority"):
        value = sections.get(name, "").strip()
        if value and value.casefold() not in EMPTY and not re.fullmatch(r"@[A-Za-z0-9-]+", value):
            findings.append(f"{name} must be a single GitHub handle")
    forbidden = sections.get("Forbidden tools", "").casefold()
    missing = [word for word in CONSEQUENTIAL if word not in forbidden]
    if missing:
        findings.append(f"Forbidden tools must name: {', '.join(missing)}")
    return findings


def issue_report(findings):
    lines = ["## Agent task contract check", ""]
    if findings:
        lines.append("Result: **not ready**. This check validates the form only; it does not authorize the task.")
        lines.append("")
        lines += [f"- {finding}" for finding in findings]
        lines += ["", "Fix the sections above and edit the issue; the check re-runs on edit."]
    else:
        lines.append("Result: **form complete**. Every required section is answered and well-formed.")
        lines.append("")
        lines.append("Next gate: a human owner records `authorize` (a form is not authorization), then the agent "
                     "works within the stated tools, paths, and limits and returns an evidence receipt for independent review.")
    lines += ["", "---", "_Structural check by `scripts/validate_agent_tasks.py`; authority effect none._"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--file", type=Path, help="Validate one task record")
    parser.add_argument("--issue-body", type=Path, help="Check an agent-task issue form body")
    parser.add_argument("--report", type=Path, help="Write the issue-body Markdown report here")
    args = parser.parse_args(argv)
    if args.issue_body:
        findings = check_issue_body(args.issue_body.read_text(encoding="utf-8"))
        report = issue_report(findings)
        if args.report:
            args.report.write_text(report, encoding="utf-8")
        sys.stdout.write(report)
        return 1 if findings else 0
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    files = [args.file] if args.file else sorted((args.root / ".quirk" / "agent-tasks").glob("*.json"))
    for path in files:
        try:
            task = validate_task(json.loads(path.read_text(encoding="utf-8")), schema)
        except (OSError, ValueError) as error:
            print(f"FAIL: {path}: {error}", file=sys.stderr)
            return 1
        print(f"Agent task OK: {task['task_id']} ({task['status']}, profile {task['agent']['profile']})")
    if not args.file:
        print(f"Agent task contracts OK: {len(files)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
