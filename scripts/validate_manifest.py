#!/usr/bin/env python3
"""Validate a Quirk repository manifest (.quirk/manifest.json) against the contract.

Standard library only. Enumerations and required keys are read from
.quirk/schemas/repository-manifest.schema.json so this validator and the
schema cannot drift; the validator applies the subset of JSON Schema the
contract uses (closed objects, required keys, enums, const, patterns, typed
arrays with unique items). Passing proves shape, not that the declared
domain, owner, or lifecycle claims are true.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "repository-manifest.schema.json"


class ManifestError(ValueError):
    pass


def _fail(message):
    raise ManifestError(message)


def _check(value, schema, label):
    if "const" in schema:
        if value != schema["const"]:
            _fail(f"{label}: must equal {schema['const']!r}")
        return
    if "enum" in schema:
        if value not in schema["enum"]:
            _fail(f"{label}: {value!r} not in {schema['enum']}")
        return
    types = schema.get("type")
    if isinstance(types, str):
        types = [types]
    if types:
        allowed = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "null": type(None)}
        ok = False
        for name in types:
            expected = allowed[name]
            if name == "integer" and isinstance(value, bool):
                continue
            if isinstance(value, expected):
                ok = True
        if not ok:
            _fail(f"{label}: expected type {types}, got {type(value).__name__}")
    if value is None:
        return
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            _fail(f"{label}: {value!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            _fail(f"{label}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            _fail(f"{label}: longer than {schema['maxLength']}")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _fail(f"{label}: below minimum {schema['minimum']}")
    if isinstance(value, list):
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            _fail(f"{label}: items must be unique")
        if "minItems" in schema and len(value) < schema["minItems"]:
            _fail(f"{label}: needs at least {schema['minItems']} items")
        for index, item in enumerate(value):
            _check(item, schema.get("items", {}), f"{label}[{index}]")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                _fail(f"{label}: unknown keys {unknown}")
        missing = [key for key in schema.get("required", []) if key not in value]
        if missing:
            _fail(f"{label}: missing required keys {missing}")
        for key, item in value.items():
            if key in properties:
                _check(item, properties[key], f"{label}.{key}")


def validate_manifest(data, schema, root=None):
    _check(data, schema, "manifest")
    if root is not None:
        for extension in data["semantic_impact"]["local_extensions"]:
            if not (Path(root) / extension).is_file():
                _fail(f"manifest.semantic_impact.local_extensions: {extension} does not exist in the repository")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to .quirk/manifest.json")
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--root", type=Path, default=None,
                        help="Repository root used to resolve local_extensions (default: manifest's grandparent)")
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else args.manifest.resolve().parents[1]
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate_manifest(data, schema, root)
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Manifest OK: {data['repository']} ({data['primary_class']}, {data['lifecycle']}, policy {data['policy']['mode']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
