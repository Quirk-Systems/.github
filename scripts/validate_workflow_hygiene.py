#!/usr/bin/env python3
"""Validate Quirk workflow hygiene defaults from YAML structure."""

import argparse
import copy
import re
import sys
from pathlib import Path

PINNED_ACTION_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-f]{40}$")
PINNED_IMAGE_PATTERN = re.compile(r"^docker://[^\s@]+@sha256:[0-9a-f]{64}$")
PINNED_CONTAINER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*@sha256:[0-9a-f]{64}$")
UNSAFE_TRIGGERS = {"pull_request_target", "workflow_run"}


class WorkflowHygieneError(Exception):
    """Validation failure safe to show to contributors."""


class InlineParser:
    def __init__(self, text, anchors):
        self.text = text
        self.anchors = anchors
        self.index = 0

    def parse(self):
        value = self.parse_value()
        self.skip_space()
        if self.index != len(self.text):
            raise WorkflowHygieneError(f"unexpected trailing content: {self.text[self.index:]}")
        return value

    def skip_space(self):
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def parse_value(self):
        self.skip_space()
        if self.index >= len(self.text):
            return None
        char = self.text[self.index]
        if char == '&':
            return self.parse_anchor()
        if char == '*':
            return self.parse_alias()
        if char == '[':
            return self.parse_sequence()
        if char == '{':
            return self.parse_mapping()
        if char in {'"', "'"}:
            return self.parse_quoted()
        return self.parse_plain()

    def parse_anchor(self):
        self.index += 1
        start = self.index
        while self.index < len(self.text) and re.match(r"[A-Za-z0-9_.-]", self.text[self.index]):
            self.index += 1
        name = self.text[start:self.index]
        if not name:
            raise WorkflowHygieneError("anchor name cannot be empty")
        value = self.parse_value()
        self.anchors[name] = copy.deepcopy(value)
        return value

    def parse_alias(self):
        self.index += 1
        start = self.index
        while self.index < len(self.text) and re.match(r"[A-Za-z0-9_.-]", self.text[self.index]):
            self.index += 1
        name = self.text[start:self.index]
        if name not in self.anchors:
            raise WorkflowHygieneError(f"unknown YAML alias: {name}")
        return copy.deepcopy(self.anchors[name])

    def parse_sequence(self):
        items = []
        self.index += 1
        self.skip_space()
        if self.index < len(self.text) and self.text[self.index] == ']':
            self.index += 1
            return items
        while True:
            items.append(self.parse_value())
            self.skip_space()
            if self.index >= len(self.text):
                raise WorkflowHygieneError("unterminated flow sequence")
            char = self.text[self.index]
            if char == ',':
                self.index += 1
                continue
            if char == ']':
                self.index += 1
                return items
            raise WorkflowHygieneError(f"unexpected flow sequence token: {char}")

    def parse_mapping(self):
        mapping = {}
        self.index += 1
        self.skip_space()
        if self.index < len(self.text) and self.text[self.index] == '}':
            self.index += 1
            return mapping
        while True:
            key = self.parse_key()
            if key == '<<':
                raise WorkflowHygieneError("YAML merge keys are not supported; use explicit mappings")
            self.skip_space()
            if self.index >= len(self.text) or self.text[self.index] != ':':
                raise WorkflowHygieneError("expected ':' in flow mapping")
            self.index += 1
            value = self.parse_value()
            if key in mapping:
                raise WorkflowHygieneError(f"duplicate YAML key: {key}")
            mapping[key] = value
            self.skip_space()
            if self.index >= len(self.text):
                raise WorkflowHygieneError("unterminated flow mapping")
            char = self.text[self.index]
            if char == ',':
                self.index += 1
                continue
            if char == '}':
                self.index += 1
                return mapping
            raise WorkflowHygieneError(f"unexpected flow mapping token: {char}")

    def parse_key(self):
        self.skip_space()
        if self.index >= len(self.text):
            raise WorkflowHygieneError("mapping keys must be strings")
        if self.text[self.index] in {'"', "'"}:
            return self.parse_quoted()
        start = self.index
        while self.index < len(self.text) and self.text[self.index] not in ':,}':
            self.index += 1
        key = self.text[start:self.index].strip()
        if not key:
            raise WorkflowHygieneError("mapping keys must be strings")
        return key

    def parse_quoted(self):
        quote = self.text[self.index]
        self.index += 1
        value = []
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == quote:
                if quote == "'" and self.index < len(self.text) and self.text[self.index] == quote:
                    value.append(quote)
                    self.index += 1
                    continue
                return ''.join(value)
            if quote == '"' and char == '\\' and self.index < len(self.text):
                escaped = self.text[self.index]
                self.index += 1
                value.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(escaped, escaped))
                continue
            value.append(char)
        raise WorkflowHygieneError("unterminated quoted scalar")

    def parse_plain(self):
        start = self.index
        while self.index < len(self.text) and self.text[self.index] not in ',]}':
            self.index += 1
        token = self.text[start:self.index].strip()
        return plain_scalar(token)


class WorkflowParser:
    def __init__(self, text):
        self.lines = text.splitlines()
        self.index = 0
        self.anchors = {}

    def parse(self):
        value = self.parse_node(0)
        self.skip_ignored()
        if self.index != len(self.lines):
            raise WorkflowHygieneError(f"unexpected trailing content on line {self.index + 1}")
        return value

    def skip_ignored(self):
        while self.index < len(self.lines):
            stripped = self.lines[self.index].strip()
            if not stripped or stripped.startswith('#'):
                self.index += 1
                continue
            break

    def line_info(self):
        line = self.lines[self.index]
        if '\t' in line[:len(line) - len(line.lstrip(' \t'))]:
            raise WorkflowHygieneError("tabs are not supported for indentation")
        indent = len(line) - len(line.lstrip(' '))
        return indent, line[indent:]

    def parse_node(self, indent):
        self.skip_ignored()
        if self.index >= len(self.lines):
            return None
        current_indent, content = self.line_info()
        if current_indent < indent:
            return None
        if current_indent > indent:
            raise WorkflowHygieneError(f"unexpected indentation on line {self.index + 1}")
        if content.startswith('-') and (content == '-' or content[1:2].isspace()):
            return self.parse_sequence(indent)
        return self.parse_mapping(indent)

    def parse_sequence(self, indent):
        items = []
        while True:
            self.skip_ignored()
            if self.index >= len(self.lines):
                return items
            current_indent, content = self.line_info()
            if current_indent < indent:
                return items
            if current_indent != indent:
                raise WorkflowHygieneError(f"unexpected indentation on line {self.index + 1}")
            if not (content.startswith('-') and (content == '-' or content[1:2].isspace())):
                raise WorkflowHygieneError("cannot mix sequence and mapping entries at the same indentation")
            item_text = content[1:].lstrip()
            self.index += 1
            if not item_text:
                value = self.parse_child(indent)
            elif item_text[0] in '|>':
                value = self.parse_block_scalar(indent)
            else:
                key, rest = self.split_mapping_entry(item_text)
                if key is None:
                    value = self.parse_inline_value(item_text)
                else:
                    value = {}
                    self.add_mapping_entry(value, key, rest, indent)
                    value = self.extend_mapping(value, indent)
            items.append(value)

    def parse_mapping(self, indent):
        mapping = {}
        while True:
            self.skip_ignored()
            if self.index >= len(self.lines):
                return mapping
            current_indent, content = self.line_info()
            if current_indent < indent:
                return mapping
            if current_indent != indent:
                raise WorkflowHygieneError(f"unexpected indentation on line {self.index + 1}")
            if content.startswith('-') and (content == '-' or content[1:2].isspace()):
                raise WorkflowHygieneError("cannot mix mapping and sequence entries at the same indentation")
            key, rest = self.split_mapping_entry(content)
            if key is None:
                raise WorkflowHygieneError(f"expected mapping entry on line {self.index + 1}")
            self.index += 1
            self.add_mapping_entry(mapping, key, rest, indent)

    def extend_mapping(self, mapping, parent_indent):
        while True:
            saved = self.index
            self.skip_ignored()
            if self.index >= len(self.lines):
                return mapping
            current_indent, content = self.line_info()
            if current_indent <= parent_indent:
                return mapping
            if content.startswith('-') and (content == '-' or content[1:2].isspace()):
                self.index = saved
                return mapping
            if self.split_mapping_entry(content)[0] is None:
                raise WorkflowHygieneError(f"expected mapping entry on line {self.index + 1}")
            child_indent = current_indent
            while True:
                self.skip_ignored()
                if self.index >= len(self.lines):
                    return mapping
                current_indent, content = self.line_info()
                if current_indent < child_indent:
                    return mapping
                if current_indent != child_indent:
                    raise WorkflowHygieneError(f"unexpected indentation on line {self.index + 1}")
                key, rest = self.split_mapping_entry(content)
                if key is None:
                    raise WorkflowHygieneError(f"expected mapping entry on line {self.index + 1}")
                self.index += 1
                self.add_mapping_entry(mapping, key, rest, child_indent)

    def add_mapping_entry(self, mapping, key_text, rest, indent):
        key = self.parse_inline_value(key_text)
        if not isinstance(key, str):
            raise WorkflowHygieneError("mapping keys must be strings")
        if key == '<<':
            raise WorkflowHygieneError("YAML merge keys are not supported; use explicit mappings")
        if key in mapping:
            raise WorkflowHygieneError(f"duplicate YAML key: {key}")
        if rest:
            rest = rest.lstrip()
            if rest and rest[0] in '|>':
                value = self.parse_block_scalar(indent)
            else:
                value = self.parse_inline_value(rest)
        else:
            value = self.parse_child(indent)
        mapping[key] = value

    def parse_child(self, indent):
        saved = self.index
        self.skip_ignored()
        if self.index >= len(self.lines):
            return None
        current_indent, _ = self.line_info()
        if current_indent <= indent:
            self.index = saved
            return None
        return self.parse_node(current_indent)

    def parse_block_scalar(self, indent):
        raw_lines = []
        while self.index < len(self.lines):
            raw = self.lines[self.index]
            if not raw.strip():
                raw_lines.append(None)
                self.index += 1
                continue
            current_indent = len(raw) - len(raw.lstrip(' '))
            if current_indent <= indent:
                break
            raw_lines.append(raw)
            self.index += 1
        content_indent = min(
            len(line) - len(line.lstrip(' '))
            for line in raw_lines
            if line is not None
        )
        lines = []
        for line in raw_lines:
            if line is None:
                lines.append('')
                continue
            lines.append(line[content_indent:])
        return '\n'.join(lines)

    def parse_inline_value(self, text):
        value = strip_inline_comment(text).strip()
        if not value:
            return None
        if value[0] not in {'[', '{', '&', '*', '"', "'"}:
            return plain_scalar(value)
        return InlineParser(value, self.anchors).parse()

    @staticmethod
    def split_mapping_entry(text):
        colon = top_level_colon(text)
        if colon is None:
            return None, None
        return text[:colon].rstrip(), text[colon + 1:]


def strip_inline_comment(text):
    depth = 0
    quote = None
    for index, char in enumerate(text):
        if quote:
            if char == quote and (quote == "'" or index == 0 or text[index - 1] != '\\'):
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
            continue
        if char in '[{':
            depth += 1
            continue
        if char in ']}':
            depth = max(depth - 1, 0)
            continue
        if char == '#' and depth == 0 and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip()
    return text.rstrip()


def plain_scalar(token):
    if token in {'', '~', 'null', 'Null', 'NULL'}:
        return None
    if token == 'true':
        return True
    if token == 'false':
        return False
    if re.fullmatch(r'-?\d+', token):
        return int(token)
    return token


def top_level_colon(text):
    depth = 0
    quote = None
    for index, char in enumerate(text):
        if quote:
            if char == quote and (quote == "'" or index == 0 or text[index - 1] != '\\'):
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
            continue
        if char in '[{':
            depth += 1
            continue
        if char in ']}':
            depth = max(depth - 1, 0)
            continue
        if char != ':' or depth != 0:
            continue
        next_char = text[index + 1:index + 2]
        if not next_char or next_char.isspace() or next_char in {'[', '{', '&', '*', '"', "'"}:
            return index
    return None


def parse_yaml_text(text):
    return WorkflowParser(text).parse()


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


def iter_containers(workflow):
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        raise WorkflowHygieneError("jobs must be a mapping")
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            raise WorkflowHygieneError("job must be a mapping")
        if "container" in job:
            value = job["container"]
            yield f"jobs.{job_id}.container", value.get("image") if isinstance(value, dict) else value
        services = job.get("services", {})
        if not isinstance(services, dict):
            raise WorkflowHygieneError(f"jobs.{job_id}.services must be a mapping")
        for service_id, service in services.items():
            if not isinstance(service, dict):
                raise WorkflowHygieneError(f"jobs.{job_id}.services.{service_id} must be a mapping")
            yield f"jobs.{job_id}.services.{service_id}.image", service.get("image")


def permission_errors(value, location):
    if value == "write-all":
        return [f"{location}: permissions: write-all is not allowed"]
    if value == "read-all":
        return []
    if not isinstance(value, dict):
        return [f"{location}: missing top-level permissions or invalid permissions value"]
    if any(not isinstance(access, str) or access not in {"read", "write", "none"} for access in value.values()):
        return [f"{location}: invalid permissions access value"]
    return []


def requires_concurrency(triggers):
    return any(trigger != "workflow_call" for trigger in triggers)


def validate_file(path: Path, root: Path):
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    errors = []
    try:
        workflow = parse_yaml_text(path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict):
            raise WorkflowHygieneError("workflow must be a mapping")
        triggers = parse_triggers(workflow)
        actions = list(iter_actions(workflow))
        containers = list(iter_containers(workflow))
    except (OSError, WorkflowHygieneError) as error:
        return [f"{relative}: invalid workflow structure: {error}"]
    for value in actions:
        if isinstance(value, str) and value.startswith("./"):
            continue
        if isinstance(value, str) and PINNED_IMAGE_PATTERN.fullmatch(value):
            continue
        if not isinstance(value, str) or PINNED_ACTION_PATTERN.fullmatch(value) is None:
            errors.append(f"{relative}: remote action must pin a full commit SHA (Docker requires a SHA-256 digest): {value}")
    for location, image in containers:
        if not isinstance(image, str) or PINNED_CONTAINER_PATTERN.fullmatch(image) is None:
            errors.append(f"{relative}: {location} must pin an immutable SHA-256 image digest: {image}")
    errors.extend(permission_errors(workflow.get("permissions"), relative))
    for job_id, job in workflow["jobs"].items():
        if "permissions" in job:
            errors.extend(permission_errors(job["permissions"], f"{relative}: jobs.{job_id}"))
    unsafe = sorted(triggers & UNSAFE_TRIGGERS)
    if unsafe:
        errors.append(f"{relative}: unsafe trigger requires separate review: {', '.join(unsafe)}")
    concurrency = workflow.get("concurrency")
    group = concurrency.get("group") if isinstance(concurrency, dict) else concurrency
    if requires_concurrency(triggers) and (not isinstance(group, str) or not group.strip()):
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
