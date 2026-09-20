#!/usr/bin/env python3
"""Validate and project Quirk design tokens (.quirk/design/tokens.json).

Standard library only. Implements the constrained W3C Design Tokens subset
documented in .quirk/schemas/design-tokens.schema.json: nested lowercase
kebab-case groups, leaf tokens with $value, inherited $type, aliases written
as {group.path}. Commands:

  validate <tokens.json>              shape, types, alias resolution, no cycles
  emit-css <tokens.json> [--prefix]   CSS custom properties on :root
  emit-json <tokens.json>             flat map of resolved token values

Passing validation proves the file is well-formed and every alias resolves;
it proves nothing about visual quality, contrast, or accessibility.
"""

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^#(?:[0-9a-f]{6}|[0-9a-f]{8})$")
ALIAS_RE = re.compile(r"^\{([a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+)\}$")
DIMENSION_UNITS = {"px", "rem"}
DURATION_UNITS = {"ms", "s"}
TYPES = {"color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier", "number", "typography", "shadow"}
FONT_WEIGHT_NAMES = {"thin", "hairline", "extra-light", "ultra-light", "light", "normal", "regular", "book", "medium",
                     "semi-bold", "demi-bold", "bold", "extra-bold", "ultra-bold", "black", "heavy", "extra-black",
                     "ultra-black"}
ROOT_META = {"$schema", "$description", "$extensions"}
TOKEN_META = {"$value", "$type", "$description", "$deprecated", "$extensions"}
GROUP_META = {"$type", "$description", "$extensions"}


class TokenError(ValueError):
    pass


def _fail(message):
    raise TokenError(message)


def collect(node, path=(), inherited=None, out=None):
    """Walk groups and tokens; return {"a.b": {"value":..., "type":..., "path":...}}."""
    out = {} if out is None else out
    if "$value" in node:
        unknown = set(node) - TOKEN_META
        if unknown:
            _fail(f"{'.'.join(path)}: unknown token keys {sorted(unknown)}")
        token_type = node.get("$type", inherited)
        if token_type is not None and token_type not in TYPES:
            _fail(f"{'.'.join(path)}: unknown $type {token_type!r}")
        out[".".join(path)] = {"value": node["$value"], "type": token_type, "path": path}
        return out
    group_type = node.get("$type", inherited)
    if group_type is not None and group_type not in TYPES:
        _fail(f"{'.'.join(path) or '<root>'}: unknown $type {group_type!r}")
    for key, child in node.items():
        if key.startswith("$"):
            allowed = ROOT_META if not path else GROUP_META
            if key not in allowed:
                _fail(f"{'.'.join(path) or '<root>'}: unknown group key {key}")
            continue
        if not NAME_RE.match(key):
            _fail(f"{'.'.join(path + (key,))}: names must be lowercase kebab-case")
        if not isinstance(child, dict):
            _fail(f"{'.'.join(path + (key,))}: groups and tokens must be objects")
        collect(child, path + (key,), group_type, out)
    return out


def resolve(tokens):
    """Resolve aliases; return {"a.b": resolved_value}. Fails on missing targets or cycles."""
    resolved = {}

    def value_of(name, chain):
        if name in resolved:
            return resolved[name]
        if name in chain:
            _fail("alias cycle: " + " -> ".join(chain + [name]))
        if name not in tokens:
            _fail(f"alias target does not exist: {name}")
        raw = tokens[name]["value"]
        match = ALIAS_RE.match(raw) if isinstance(raw, str) else None
        if match:
            target = match.group(1)
            value = value_of(target, chain + [name])
            if tokens[name]["type"] is None:
                tokens[name]["type"] = tokens[target]["type"]
            elif tokens[target]["type"] != tokens[name]["type"]:
                _fail(f"{name}: alias type {tokens[name]['type']} differs from target type {tokens[target]['type']}")
        else:
            value = raw
        resolved[name] = value
        return value

    for name in tokens:
        value_of(name, [])
    return resolved


def check_value(name, token_type, value):
    if token_type is None:
        _fail(f"{name}: no $type declared or inherited")
    if token_type == "color":
        if not (isinstance(value, str) and HEX_RE.match(value)):
            _fail(f"{name}: color must be lowercase #rrggbb or #rrggbbaa")
    elif token_type == "dimension":
        if not (isinstance(value, dict) and set(value) == {"value", "unit"} and isinstance(value["value"], (int, float))
                and not isinstance(value["value"], bool) and value["unit"] in DIMENSION_UNITS):
            _fail(f"{name}: dimension must be {{value: number, unit: px|rem}}")
    elif token_type == "duration":
        if not (isinstance(value, dict) and set(value) == {"value", "unit"} and isinstance(value["value"], (int, float))
                and not isinstance(value["value"], bool) and value["unit"] in DURATION_UNITS):
            _fail(f"{name}: duration must be {{value: number, unit: ms|s}}")
    elif token_type == "fontFamily":
        ok = isinstance(value, str) or (isinstance(value, list) and value and all(isinstance(v, str) and v for v in value))
        if not ok:
            _fail(f"{name}: fontFamily must be a string or non-empty list of strings")
    elif token_type == "fontWeight":
        ok = (isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 1000) or value in FONT_WEIGHT_NAMES
        if not ok:
            _fail(f"{name}: fontWeight must be 1-1000 or a named weight")
    elif token_type == "cubicBezier":
        ok = (isinstance(value, list) and len(value) == 4
              and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)
              and 0 <= value[0] <= 1 and 0 <= value[2] <= 1)
        if not ok:
            _fail(f"{name}: cubicBezier must be four numbers with x values in [0, 1]")
    elif token_type == "number":
        if not (isinstance(value, (int, float)) and not isinstance(value, bool)):
            _fail(f"{name}: number must be numeric")
    elif token_type in {"typography", "shadow"}:
        if not isinstance(value, dict):
            _fail(f"{name}: {token_type} must be an object")


def validate(data):
    if not isinstance(data, dict):
        _fail("token file must be an object")
    if data.get("$schema") != "https://github.com/Quirk-Systems/.github/blob/main/.quirk/schemas/design-tokens.schema.json":
        _fail("$schema must reference the Quirk design-tokens schema")
    quirk = data.get("$extensions", {}).get("quirk")
    if not isinstance(quirk, dict):
        _fail("$extensions.quirk is required")
    required = {"status", "version", "implementation_owner", "authority_effect"}
    if set(quirk) != required:
        _fail(f"$extensions.quirk keys must be exactly {sorted(required)}")
    if quirk["status"] not in {"candidate", "reviewed", "canonical"}:
        _fail("$extensions.quirk.status must be candidate, reviewed, or canonical")
    if not re.match(r"^\d+\.\d+\.\d+$", quirk["version"]):
        _fail("$extensions.quirk.version must be semver")
    if not re.match(r"^Quirk-Systems/[A-Za-z0-9_.-]+$", quirk["implementation_owner"]):
        _fail("$extensions.quirk.implementation_owner must be a Quirk-Systems repository")
    if quirk["authority_effect"] != "none":
        _fail("$extensions.quirk.authority_effect must be none")
    tokens = collect(data)
    if not tokens:
        _fail("no tokens defined")
    resolved = resolve(tokens)
    for name, token in tokens.items():
        check_value(name, token["type"], resolved[name])
    return tokens, resolved


def css_value(token_type, value):
    if token_type in {"dimension", "duration"}:
        return f"{value['value']}{value['unit']}"
    if token_type == "fontFamily":
        families = value if isinstance(value, list) else [value]
        return ", ".join(f'"{f}"' if " " in f else f for f in families)
    if token_type == "cubicBezier":
        return "cubic-bezier(" + ", ".join(str(v) for v in value) + ")"
    if isinstance(value, dict):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def emit_css(tokens, resolved, prefix):
    lines = ["/* Generated by scripts/design_tokens.py from .quirk/design/tokens.json. Do not edit. */", ":root {"]
    for name in sorted(tokens):
        variable = f"--{prefix}-" + name.replace(".", "-")
        lines.append(f"  {variable}: {css_value(tokens[name]['type'], resolved[name])};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def emit_json(tokens, resolved):
    flat = {name: {"type": tokens[name]["type"], "value": resolved[name]} for name in sorted(tokens)}
    return json.dumps(flat, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "emit-css", "emit-json"):
        p = sub.add_parser(command)
        p.add_argument("tokens", type=Path)
        if command == "emit-css":
            p.add_argument("--prefix", default="quirk")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.tokens.read_text(encoding="utf-8"))
        tokens, resolved = validate(data)
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    if args.command == "validate":
        aliases = sum(1 for t in tokens.values() if isinstance(t["value"], str) and ALIAS_RE.match(t["value"]))
        print(f"Design tokens OK: {len(tokens)} tokens, {aliases} aliases resolved, "
              f"status {data['$extensions']['quirk']['status']} v{data['$extensions']['quirk']['version']}")
    elif args.command == "emit-css":
        sys.stdout.write(emit_css(tokens, resolved, args.prefix))
    else:
        sys.stdout.write(emit_json(tokens, resolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
