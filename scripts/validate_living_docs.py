#!/usr/bin/env python3
"""Validate living documents: intentions, goals, roadmaps, todos, plans, briefs.

Standard library only. A living document is a Markdown file under docs/ whose
header block carries a `Kind:` line. The header is parsed into an object and
checked against .quirk/schemas/living-document.schema.json; the body is
checked for the sections that kind requires, for checkbox discipline in
roadmap and todo lists, and for lineage (every repository-relative `Derived
from` path exists). A document whose `Review by` date has passed while it is
still candidate, active, or paused is stale: stale is always reported and
fails the run only with --strict. Passing proves shape, lineage, and
freshness, not that an intention is wise, a goal is met, or a task is done.
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "living-document.schema.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_manifest import _check  # noqa: E402
from validate_templates import REQUIRED_SECTIONS as TEMPLATE_SECTIONS  # noqa: E402

KIND_SECTIONS = {
    "intention": ["## Strength", "## Intention", "## Goals", "## Not this", "## Review"],
    "goal": ["## Outcome", "## Measure", "## Tasks", "## Evidence", "## Review"],
    "roadmap": ["## Now", "## Next", "## Later", "## Done", "## Decisions awaiting an owner"],
    "todo": ["## Open", "## Blocked", "## Done"],
    "plan": TEMPLATE_SECTIONS["PLAN.md"],
    "brief": TEMPLATE_SECTIONS["BRIEF.md"],
}
CHECKBOX_SECTIONS = {
    "roadmap": {"## Now": "[ ]", "## Next": "[ ]", "## Later": "[ ]", "## Done": "[x]"},
    "todo": {"## Open": "[ ]", "## Blocked": "[ ]", "## Done": "[x]"},
}
HEADER_KEYS = {
    "Kind": "kind",
    "Status": "status",
    "Owner": "owner",
    "Repository": "repository",
    "Observed head": "observed_head",
    "Reviewed": "reviewed",
    "Review by": "review_by",
    "Derived from": "derived_from",
    "Authority effect": "authority_effect",
}
OPEN_STATUSES = {"candidate", "active", "paused"}
KIND_LINE = re.compile(r"^Kind:\s*\S", re.M)
HEADER_SCAN_LINES = 15


class LivingDocError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise LivingDocError(message)


def load_schema(root):
    return json.loads((root / ".quirk" / "schemas" / "living-document.schema.json").read_text(encoding="utf-8"))


def strip_markup(value):
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value.strip())
    return value.replace("`", "").strip()


def is_living_document(text):
    head = "\n".join(text.splitlines()[:HEADER_SCAN_LINES])
    return bool(KIND_LINE.search(head))


def parse_header(path, text):
    """Return (header object, body) from the H1 and the key: value block under it."""
    lines = text.splitlines()
    require(lines and lines[0].startswith("# ") and lines[0][2:].strip(), f"{path}: first line must be an H1 title")
    data = {"schema_version": "living-document.v1", "title": lines[0][2:].strip()}
    seen = set()
    i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].strip():
        key, sep, value = lines[i].partition(":")
        key = key.strip()
        require(sep and key in HEADER_KEYS, f"{path}: unexpected header line {lines[i].strip()!r}")
        require(key not in seen, f"{path}: duplicate header key {key!r}")
        seen.add(key)
        field = HEADER_KEYS[key]
        if field == "derived_from":
            data[field] = [strip_markup(item) for item in value.split(",") if item.strip()]
        else:
            data[field] = strip_markup(value)
        i += 1
    data.setdefault("derived_from", [])
    return data, "\n".join(lines[i:])


def section_lines(body, heading):
    out, inside = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            inside = line.strip() == heading
            continue
        if inside:
            out.append(line)
    return out


def check_sections(path, kind, body):
    for section in KIND_SECTIONS[kind]:
        require(re.search("^" + re.escape(section) + r"\s*$", body, re.M), f"{path}: missing section {section!r}")
    for heading, mark in CHECKBOX_SECTIONS.get(kind, {}).items():
        for line in section_lines(body, heading):
            if line.startswith("- "):
                require(line.startswith(f"- {mark} "),
                        f"{path}: every item under {heading!r} must start with '- {mark} ': {line.strip()!r}")


def check_lineage(path, root, data):
    for item in data["derived_from"]:
        if item.startswith(("http://", "https://")):
            continue
        require((root / item).exists(), f"{path}: derived-from path does not exist: {item}")


def staleness(data, today):
    reviewed = dt.date.fromisoformat(data["reviewed"])
    review_by = dt.date.fromisoformat(data["review_by"])
    require(reviewed <= review_by, f"{data['title']}: Reviewed {reviewed} is after Review by {review_by}")
    if data["status"] in OPEN_STATUSES and review_by < today:
        return f"review was due {review_by} ({(today - review_by).days} days ago) and status is {data['status']}"
    return None


def validate_document(path, root=ROOT, today=None, schema=None):
    """Validate one living document; return (header object, stale message or None)."""
    path = Path(path)
    today = today or dt.date.today()
    text = path.read_text(encoding="utf-8")
    require(is_living_document(text), f"{path}: no 'Kind:' line in the first {HEADER_SCAN_LINES} lines")
    data, body = parse_header(path, text)
    _check(data, schema or load_schema(root), str(path))
    check_sections(path, data["kind"], body)
    check_lineage(path, root, data)
    return data, staleness(data, today)


def discover(root):
    docs = root / "docs"
    if not docs.is_dir():
        return []
    return [p for p in sorted(docs.rglob("*.md")) if is_living_document(p.read_text(encoding="utf-8"))]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    parser.add_argument("--path", type=Path, action="append", help="validate only this document (repeatable)")
    parser.add_argument("--strict", action="store_true", help="fail when any open document is past its review date")
    parser.add_argument("--today", type=dt.date.fromisoformat, default=None, help="override today's date (YYYY-MM-DD)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    schema = load_schema(root)
    paths = [p.resolve() for p in args.path] if args.path else discover(root)
    counts, stale = {}, []
    for path in paths:
        data, message = validate_document(path, root, args.today, schema)
        counts[data["kind"]] = counts.get(data["kind"], 0) + 1
        if message:
            stale.append(f"{path.relative_to(root)}: {message}")
    for line in stale:
        print(f"STALE: {line}")
    summary = ", ".join(f"{count} {kind}" for kind, count in sorted(counts.items())) or "none"
    print(f"{'FAIL' if stale and args.strict else 'PASS'}: {len(paths)} living documents ({summary}); "
          f"{len(stale)} stale. Shape, lineage, and freshness only.")
    return 1 if stale and args.strict else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
