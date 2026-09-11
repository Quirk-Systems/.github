#!/usr/bin/env python3
"""Validate Quirk workflow hygiene defaults."""

import argparse
import re
import sys
from pathlib import Path

PINNED_ACTION_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@(?P<sha>[0-9a-f]{40})$")
INLINE_ON_PATTERN = re.compile(r"^on:\s*\[(?P<body>[^\]]+)\]\s*$", re.MULTILINE)
MAPPING_EVENT_PATTERN = re.compile(
    r"^(?: {2})?(?P<event>push|pull_request|pull_request_target|workflow_dispatch|workflow_call|workflow_run|schedule):\s*(?:#.*)?$",
    re.MULTILINE,
)
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<value>[^\s#]+)", re.MULTILINE)
TOP_LEVEL_KEY_TEMPLATE = r"^(?P<key>{key}):(?:\s*(?:#.*|\{{.*\}}))?$"
UNSAFE_TRIGGERS = {"pull_request_target", "workflow_run"}
CONCURRENCY_TRIGGERS = {"push", "pull_request", "workflow_dispatch", "schedule"}


class WorkflowHygieneError(Exception):
    """Validation failure safe to show to contributors."""


def discover_workflows(root: Path, workflows: str):
    workflows_path = Path(workflows)
    if not workflows_path.is_absolute():
        workflows_path = root / workflows_path
    workflows_path = workflows_path.resolve()
    try:
        workflows_path.relative_to(root)
    except ValueError as error:
        raise WorkflowHygieneError("workflow directory must be inside repository root") from error
    if not workflows_path.exists():
        raise WorkflowHygieneError(f"workflow directory does not exist: {workflows}")
    if not workflows_path.is_dir():
        raise WorkflowHygieneError("workflow path must be a directory")
    candidates = sorted(
        path for pattern in ("*.yml", "*.yaml") for path in workflows_path.rglob(pattern) if path.is_file()
    )
    if not candidates:
        raise WorkflowHygieneError("workflow directory contains no workflow files")
    return candidates


def _relative(path: Path, root: Path):
    return path.resolve().relative_to(root).as_posix()


def parse_triggers(text: str):
    triggers = set()
    inline = INLINE_ON_PATTERN.search(text)
    if inline:
        triggers.update(item.strip().strip("'\"") for item in inline.group("body").split(",") if item.strip())
    triggers.update(match.group("event") for match in MAPPING_EVENT_PATTERN.finditer(text))
    return triggers


def has_top_level_key(text: str, key: str):
    return re.search(TOP_LEVEL_KEY_TEMPLATE.format(key=re.escape(key)), text, re.MULTILINE) is not None


def iter_remote_actions(text: str):
    for match in USES_PATTERN.finditer(text):
        value = match.group("value")
        if value.startswith("./") or value.startswith("docker://") or value.startswith("${{"):
            continue
        if "/" not in value or "@" not in value:
            continue
        yield value


def validate_file(path: Path, root: Path):
    text = path.read_text(encoding="utf-8")
    errors = []
    relative = _relative(path, root)
    triggers = parse_triggers(text)

    for value in iter_remote_actions(text):
        if PINNED_ACTION_PATTERN.fullmatch(value) is None:
            errors.append(f"{relative}: remote action must pin a full commit SHA: {value}")

    if not has_top_level_key(text, "permissions"):
        errors.append(f"{relative}: missing top-level permissions")
    if "permissions: write-all" in text:
        errors.append(f"{relative}: permissions: write-all is not allowed")

    unsafe = sorted(trigger for trigger in triggers if trigger in UNSAFE_TRIGGERS)
    if unsafe:
        errors.append(f"{relative}: unsafe trigger requires separate review: {', '.join(unsafe)}")

    if triggers & CONCURRENCY_TRIGGERS and not has_top_level_key(text, "concurrency"):
        needed = ", ".join(sorted(triggers & CONCURRENCY_TRIGGERS))
        errors.append(f"{relative}: missing top-level concurrency for event-driven workflow ({needed})")

    return errors


def validate_workflows(root: Path, workflows: str):
    errors = []
    for path in discover_workflows(root, workflows):
        errors.extend(validate_file(path, root))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--workflows", default=".github/workflows")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        errors = validate_workflows(root, args.workflows)
    except (OSError, WorkflowHygieneError) as error:
        parser.error(str(error))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Workflow hygiene errors: {len(errors)}", file=sys.stderr)
        return 1
    print("Workflow hygiene OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
