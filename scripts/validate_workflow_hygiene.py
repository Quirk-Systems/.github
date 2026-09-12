#!/usr/bin/env python3
"""Validate Quirk workflow hygiene defaults from YAML structure."""
import argparse
import re
import sys
from pathlib import Path

import yaml

PINNED_ACTION_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-f]{40}$")
PINNED_IMAGE_PATTERN = re.compile(r"^docker://[^\s@]+@sha256:[0-9a-f]{64}$")
UNSAFE_TRIGGERS = {"pull_request_target", "workflow_run"}
CONCURRENCY_TRIGGERS = {"push", "pull_request", "workflow_dispatch", "schedule"}


class WorkflowHygieneError(Exception):
    """Validation failure safe to show to contributors."""


class WorkflowLoader(yaml.BaseLoader):
    """Keep GitHub's `on` key as text; reject ambiguous duplicate mappings."""

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise WorkflowHygieneError("mapping keys must be strings")
            if key in result:
                raise WorkflowHygieneError(f"duplicate YAML key: {key}")
            if key == "<<":
                raise WorkflowHygieneError("YAML merge keys are not supported; use explicit mappings")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def discover_workflows(root: Path, workflows: str):
    root = root.resolve()
    folder = Path(workflows)
    folder = (folder if folder.is_absolute() else root / folder).resolve()
    try:
        folder.relative_to(root)
    except ValueError as error:
        raise WorkflowHygieneError("workflow directory must be inside repository root") from error
    if not folder.is_dir():
        raise WorkflowHygieneError("workflow path must be an existing directory")
    candidates = sorted(path for pattern in ("*.yml", "*.yaml") for path in folder.glob(pattern) if path.is_file())
    if not candidates:
        raise WorkflowHygieneError("workflow directory contains no workflow files")
    for path in candidates:
        try:
            path.resolve().relative_to(root)
        except ValueError as error:
            raise WorkflowHygieneError("workflow file resolves outside repository root") from error
    return candidates


def parse_triggers(workflow):
    value = workflow.get("on")
    if isinstance(value, str) and value:
        return {value}
    if isinstance(value, dict) and value:
        return set(value)
    if isinstance(value, list) and value and all(isinstance(item, str) and item for item in value):
        return set(value)
    raise WorkflowHygieneError("on must contain an event name, sequence, or mapping")


def iter_actions(workflow):
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        raise WorkflowHygieneError("jobs must be a mapping")
    for job in jobs.values():
        if not isinstance(job, dict):
            raise WorkflowHygieneError("job must be a mapping")
        if "uses" in job:
            yield job["uses"]
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            raise WorkflowHygieneError("steps must be a sequence")
        for step in steps:
            if not isinstance(step, dict):
                raise WorkflowHygieneError("step must be a mapping")
            if "uses" in step:
                yield step["uses"]


def validate_file(path: Path, root: Path):
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    try:
        workflow = yaml.load(path.read_text(encoding="utf-8"), Loader=WorkflowLoader)
        if not isinstance(workflow, dict):
            raise WorkflowHygieneError("workflow must be a mapping")
        triggers = parse_triggers(workflow)
        actions = list(iter_actions(workflow))
    except (yaml.YAMLError, WorkflowHygieneError) as error:
        return [f"{relative}: invalid workflow structure: {error}"]
    errors = []
    for value in actions:
        if isinstance(value, str) and value.startswith("./"):
            continue
        if isinstance(value, str) and PINNED_IMAGE_PATTERN.fullmatch(value):
            continue
        if not isinstance(value, str) or PINNED_ACTION_PATTERN.fullmatch(value) is None:
            errors.append(f"{relative}: remote action must pin a full commit SHA (Docker requires a SHA-256 digest): {value}")
    permissions = workflow.get("permissions")
    if permissions == "write-all":
        errors.append(f"{relative}: permissions: write-all is not allowed")
    elif not isinstance(permissions, dict) and permissions != "read-all":
        errors.append(f"{relative}: missing top-level permissions or invalid permissions value")
    unsafe = sorted(triggers & UNSAFE_TRIGGERS)
    if unsafe:
        errors.append(f"{relative}: unsafe trigger requires separate review: {', '.join(unsafe)}")
    concurrency = workflow.get("concurrency")
    group = concurrency.get("group") if isinstance(concurrency, dict) else concurrency
    if triggers & CONCURRENCY_TRIGGERS and (not isinstance(group, str) or not group.strip()):
        errors.append(f"{relative}: missing top-level concurrency for event-driven workflow")
    return errors


def validate_workflows(root: Path, workflows: str):
    root = root.resolve()
    return [error for path in discover_workflows(root, workflows) for error in validate_file(path, root)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--workflows", default=".github/workflows")
    args = parser.parse_args(argv)
    try:
        errors = validate_workflows(Path(args.root), args.workflows)
    except (OSError, WorkflowHygieneError) as error:
        parser.error(str(error))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Workflow hygiene errors: {len(errors)}", file=sys.stderr)
        return 1
    print("Workflow hygiene OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
