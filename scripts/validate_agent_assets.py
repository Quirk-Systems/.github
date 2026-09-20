#!/usr/bin/env python3
"""Validate agent-facing assets: AGENTS.md, CLAUDE.md, agent profiles, skills, shims.

Structural validation only. Passing proves the files have the expected shape
and that their relative links resolve; it does not prove any agent runtime
loaded or obeyed them.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
AGENTS_MAX_LINES = 150
GENERATED_RE = re.compile(r"<!-- Generated: \d{4}-\d{2}-\d{2} by AgentFile Forge -->")
PROFILE_KEYS = {"name", "description", "target", "tools"}


class AssetError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AssetError(message)


def split_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    pieces = text.split("---\n", 2)
    require(len(pieces) == 3 and not pieces[0], f"{path}: missing frontmatter")
    return pieces[1], pieces[2], text


def parse_frontmatter(path, block, json_values):
    data = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        require(sep and key and key not in data, f"{path}: malformed or duplicate frontmatter key")
        value = value.strip()
        if json_values:
            try:
                data[key] = json.loads(value)
            except ValueError as error:
                raise AssetError(f"{path}: frontmatter value for {key} is not JSON") from error
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            data[key] = value
    return data


def check_links(path, text, root):
    count = 0
    for target in re.findall(r"\]\(([^)]+)\)", text):
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        resolved = (path.parent / unquote(url.path)).resolve()
        require(resolved.is_relative_to(root), f"{path}: link escapes repository: {target}")
        require(resolved.exists(), f"{path}: missing link target {target}")
        count += 1
    return count


def validate_profile(path, root):
    block, body, text = split_frontmatter(path)
    data = parse_frontmatter(path, block, json_values=True)
    require(set(data) == PROFILE_KEYS, f"{path}: frontmatter keys must be exactly {sorted(PROFILE_KEYS)}")
    require(NAME_RE.fullmatch(str(data["name"])), f"{path}: invalid name")
    require(data["name"] == path.name[: -len(".agent.md")], f"{path}: name must match filename")
    require(isinstance(data["description"], str) and data["description"].strip(), f"{path}: empty description")
    require(data["target"] == "github-copilot", f"{path}: target must be github-copilot")
    require(isinstance(data["tools"], list) and data["tools"] and all(isinstance(t, str) for t in data["tools"]),
            f"{path}: tools must be a non-empty list of strings")
    require(body.strip(), f"{path}: empty instructions")
    return check_links(path, text, root)


def validate_skill(path, root, json_values):
    block, body, text = split_frontmatter(path)
    data = parse_frontmatter(path, block, json_values=json_values)
    require({"name", "description"} <= set(data), f"{path}: skill frontmatter needs name and description")
    require(NAME_RE.fullmatch(str(data["name"])), f"{path}: invalid skill name")
    require(data["name"] == path.parent.name, f"{path}: skill name must match its directory")
    require(isinstance(data["description"], str) and data["description"].strip(), f"{path}: empty description")
    require(body.strip(), f"{path}: empty skill body")
    return data, body, check_links(path, text, root)


def validate_shim(path, body, root):
    match = re.search(r"`(\.github/skills/[a-z0-9-]+/SKILL\.md)`", body)
    require(match, f"{path}: shim must name its canonical .github/skills/<name>/SKILL.md")
    canonical = root / match.group(1)
    require(canonical.is_file(), f"{path}: canonical skill {match.group(1)} does not exist")
    require(canonical.parent.name == path.parent.name, f"{path}: shim and canonical skill names differ")
    require(len(body.splitlines()) <= 12, f"{path}: shim must stay a pointer, not a copy")


def validate_agents_md(root):
    path = root / "AGENTS.md"
    require(path.is_file(), "AGENTS.md is missing")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    require(len(lines) <= AGENTS_MAX_LINES, f"AGENTS.md exceeds {AGENTS_MAX_LINES} lines ({len(lines)})")
    require(GENERATED_RE.search(lines[0] if lines else ""), "AGENTS.md must start with the Generated stamp")
    for heading in ("## What This Is", "## Commands", "### Do", "### Don't → Do Instead", "## Permissions"):
        require(heading in text, f"AGENTS.md missing section {heading!r}")
    require("- **Never**" in text, "AGENTS.md Permissions must include a Never list")
    require(text.count("→") >= 4, "AGENTS.md needs Don't → Do Instead pairs, not naked prohibitions")
    return check_links(path, text, root)


def validate_claude_md(root):
    path = root / "CLAUDE.md"
    require(path.is_file(), "CLAUDE.md is missing")
    text = path.read_text(encoding="utf-8")
    require(re.search(r"^@AGENTS\.md\s*$", text, re.M), "CLAUDE.md must import AGENTS.md with a line '@AGENTS.md'")
    return check_links(path, text, root)


def validate_settings(root):
    path = root / ".claude" / "settings.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    permissions = data.get("permissions", {})
    allow = permissions.get("allow", [])
    require(not any(rule.strip() in {"Bash", "Bash(*)", "Bash(:*)"} for rule in allow),
            ".claude/settings.json must not allow unrestricted Bash")
    deny = " ".join(permissions.get("deny", []))
    require("--force" in deny and "--no-verify" in deny,
            ".claude/settings.json must deny force-push and --no-verify")
    for event, entries in data.get("hooks", {}).items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                command = hook.get("command", "")
                script = command.split()[-1] if command else ""
                require(script.startswith("scripts/hooks/") and (root / script).is_file(),
                        f".claude/settings.json {event} hook must call a committed scripts/hooks/ file")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    links = 0
    profiles = sorted((root / "agents").glob("*.agent.md"))
    require(profiles, "no agent profiles found under agents/")
    for path in profiles:
        links += validate_profile(path, root)
    canonical = sorted((root / ".github" / "skills").glob("*/SKILL.md"))
    require(canonical, "no canonical skills under .github/skills/")
    for path in canonical:
        _, _, n = validate_skill(path, root, json_values=True)
        links += n
    shims = sorted((root / ".claude" / "skills").glob("*/SKILL.md"))
    for path in shims:
        _, body, n = validate_skill(path, root, json_values=False)
        validate_shim(path, body, root)
        links += n
    links += validate_agents_md(root)
    links += validate_claude_md(root)
    validate_settings(root)
    print(f"PASS: {len(profiles)} profiles, {len(canonical)} canonical skills, {len(shims)} shims, "
          f"AGENTS.md/CLAUDE.md present, {links} relative links. Structural validation only.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssetError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
