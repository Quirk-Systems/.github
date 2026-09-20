#!/usr/bin/env python3
"""Validate creation templates, JSON examples, dataset cards, and schemas.

Standard library only. Checks that every Markdown template keeps its required
sections, every JSON example under templates/ validates against its schema,
every datasets/<name>/dataset-card.json validates and is indexed, every
schema under .quirk/schemas/ is a closed draft 2020-12 schema with a matching
$id, and the design-token source validates. Optional: --artifact <path> or
--dataset-card <path> validates one document. Structural validation only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / ".quirk" / "schemas"
TEMPLATES = ROOT / "templates"
DATASETS = ROOT / "datasets"
TOKENS = ROOT / ".quirk" / "design" / "tokens.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_tokens import validate as validate_tokens  # noqa: E402
from validate_manifest import _check  # noqa: E402

REQUIRED_SECTIONS = {
    "BRIEF.md": ["## Context", "## Outcome", "## Constraints", "## Semantic impact", "## Evidence", "## Action",
                 "## Verification", "## Risk", "## Residue"],
    "PLAN.md": ["## Goal", "## Architecture", "## Global constraints", "## Waves", "## Verification (end to end)",
                "## Out of scope", "## Risks"],
    "ADR.md": ["## Decision", "## Forces and constraints", "## Options considered", "## Rationale",
               "## Semantic impact", "## Consequences", "## Evidence", "## Required next authority"],
    "MOVE_RECEIPT.md": ["## Action", "## Authority", "## Exact subject", "## Resulting state", "## Reversal", "## Residue"],
}
JSON_EXAMPLES = {
    "artifact-manifest.json": "artifact-manifest.schema.json",
    "dataset-card.json": "dataset-card.schema.json",
    "agent-task.json": "agent-task.schema.json",
}
ID_PREFIX = "https://github.com/Quirk-Systems/.github/blob/main/.quirk/schemas/"


class TemplateError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise TemplateError(message)


def load_schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_document(path, schema_name):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    _check(data, load_schema(schema_name), Path(path).name)
    return data


def validate_markdown_templates():
    count = 0
    for name, sections in REQUIRED_SECTIONS.items():
        path = TEMPLATES / name
        require(path.is_file(), f"missing template {path}")
        text = path.read_text(encoding="utf-8")
        for section in sections:
            require(re.search("^" + re.escape(section) + r"\s*$", text, re.M), f"{name}: missing section {section!r}")
        require("Authority effect: **none**" in text, f"{name}: must state authority effect none")
        count += 1
    index = (TEMPLATES / "README.md").read_text(encoding="utf-8")
    for name in list(REQUIRED_SECTIONS) + list(JSON_EXAMPLES):
        require(name in index, f"templates/README.md does not index {name}")
    return count


def validate_json_examples():
    for name, schema in JSON_EXAMPLES.items():
        validate_document(TEMPLATES / name, schema)
    return len(JSON_EXAMPLES)


def validate_dataset_cards():
    cards = sorted(DATASETS.glob("*/dataset-card.json"))
    index = (DATASETS / "README.md").read_text(encoding="utf-8")
    for card in cards:
        data = validate_document(card, "dataset-card.schema.json")
        require((card.parent / "README.md").is_file(), f"{card.parent.name}: missing README.md")
        require(f"`{card.parent.name}`" in index, f"datasets/README.md does not index {card.parent.name}")
        require(data["dataset_id"].endswith(card.parent.name.replace("-", "-")), f"{card}: dataset_id should end with the directory name")
    return len(cards)


def validate_schemas():
    schemas = sorted(SCHEMAS.glob("*.schema.json"))
    require(schemas, "no schemas found")
    for path in schemas:
        data = json.loads(path.read_text(encoding="utf-8"))
        require(data.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{path.name}: must be draft 2020-12")
        require(data.get("$id") == ID_PREFIX + path.name, f"{path.name}: $id must be {ID_PREFIX + path.name}")
        require(data.get("type") == "object" and data.get("additionalProperties") is False,
                f"{path.name}: root must be a closed object")
        require(isinstance(data.get("title"), str) and data["title"].strip(), f"{path.name}: needs a title")
    return len(schemas)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, help="Validate one artifact manifest and exit")
    parser.add_argument("--dataset-card", type=Path, help="Validate one dataset card and exit")
    args = parser.parse_args(argv)
    if args.artifact:
        data = validate_document(args.artifact, "artifact-manifest.schema.json")
        print(f"Artifact manifest OK: {data['artifact_id']} ({data['kind']}, {data['status']})")
        return 0
    if args.dataset_card:
        data = validate_document(args.dataset_card, "dataset-card.schema.json")
        print(f"Dataset card OK: {data['dataset_id']} ({data['status']})")
        return 0
    markdown = validate_markdown_templates()
    examples = validate_json_examples()
    cards = validate_dataset_cards()
    schemas = validate_schemas()
    tokens, _ = validate_tokens(json.loads(TOKENS.read_text(encoding="utf-8")))
    print(f"PASS: {markdown} markdown templates, {examples} JSON examples, {cards} dataset cards, "
          f"{schemas} schemas, {len(tokens)} design tokens. Structural validation only.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
