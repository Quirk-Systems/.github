#!/usr/bin/env python3
"""Validate this package's deliberately small authored format; no remote actions."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TOOLS = ["github/issue_read", "github/pull_request_read", "github/get_file_contents"]
PROFILES = {
    "quirk-repo-repair": ["read", "search", "edit", "execute"],
    "quirk-dependency-steward": ["read", "search", "edit", "execute"],
    "quirk-artifact-provenance": ["read", "search", "edit"],
}
SKILL = ".github/skills/quirk-repo-maintenance/SKILL.md"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    pieces = text.split("---\n", 2)
    require(len(pieces) == 3 and not pieces[0], f"{path}: missing frontmatter")
    data = {}
    for line in pieces[1].splitlines():
        key, sep, value = line.partition(":")
        require(sep and key not in data, f"{path}: malformed or duplicate key")
        data[key] = json.loads(value.strip())
    require(isinstance(data.get("description"), str) and data["description"].strip(), f"{path}: empty description")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data.get("name", "")), f"{path}: invalid name")
    require(pieces[2].strip(), f"{path}: empty instructions")
    return data, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT, help="Existing source checkout for unchanged relative-link targets when validating an overlay")
    args = parser.parse_args()
    markdown = []
    for name, tools in PROFILES.items():
        path = ROOT / "agents" / f"{name}.agent.md"
        data, text = frontmatter(path)
        require(set(data) == {"name", "description", "target", "tools"}, f"{path}: unexpected properties")
        require(data["name"] == name and data["target"] == "github-copilot", f"{path}: identity or target mismatch")
        require(data["tools"] == tools + SOURCE_TOOLS, f"{path}: changed tool scope requires review")
        markdown.append((path, text))
    data, text = frontmatter(ROOT / SKILL)
    require(set(data) == {"name", "description"}, "Skill: unexpected properties")
    require(data["name"] == "quirk-repo-maintenance", "Skill: directory/name mismatch")
    markdown.extend([(ROOT / SKILL, text), (ROOT / "docs/copilot-maintenance/README.md", (ROOT / "docs/copilot-maintenance/README.md").read_text())])
    links = 0
    for path, text in markdown:
        for target in re.findall(r"\]\(([^)]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / unquote(url.path)).resolve()
            require(resolved.is_relative_to(ROOT), f"{path}: link escapes repository")
            relative = resolved.relative_to(ROOT)
            require(resolved.is_file() or (args.source_root.resolve() / relative).is_file(), f"{path}: missing link {target}")
            links += 1
    cases = json.loads((ROOT / "docs/copilot-maintenance/scenarios.json").read_text())
    rubric = json.loads((ROOT / "docs/copilot-maintenance/rubric.json").read_text())
    ids = []
    for case in cases:
        require(set(case) == {"id", "kind", "profile", "request", "artifacts"}, "Scenario fields differ")
        require(case["kind"] in {"positive", "adversarial"}, "Invalid scenario kind")
        require(case["profile"] in PROFILES, "Unknown scenario profile")
        require(isinstance(case["request"], str) and case["request"].strip(), "Empty request")
        require(isinstance(case["artifacts"], dict) and case["artifacts"], "Missing artifacts")
        ids.append(case["id"])
    require(len(ids) == len(set(ids)) and set(ids) == set(rubric), "Scenario/rubric IDs differ or repeat")
    for name in PROFILES:
        require({c["kind"] for c in cases if c["profile"] == name} == {"positive", "adversarial"}, f"Missing positive/adversarial case for {name}")
    for case_id, criteria in rubric.items():
        require(set(criteria) == {"must", "must_not"}, f"{case_id}: malformed rubric")
        require(all(isinstance(criteria[k], list) and criteria[k] and all(isinstance(v, str) and v.strip() for v in criteria[k]) for k in criteria), f"{case_id}: empty criteria")
    print(f"PASS: 3 profiles, 1 skill, {links} relative links, {len(cases)} scenario/rubric pairs. Structural validation only.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
