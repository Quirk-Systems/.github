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


class SchemaSupportError(ManifestError):
    """The schema itself cannot be applied, as opposed to the value not matching.

    It subclasses ManifestError so existing callers still catch it, but the
    boolean keywords re-raise it instead of reading it as a non-match: a branch
    the validator cannot apply must never be reported as simply unsatisfied.
    """


def _fail(message):
    raise ManifestError(message)


_ANNOTATION_KEYWORDS = frozenset({
    "$schema", "$id", "$anchor", "$comment", "$defs", "definitions",
    "title", "description", "examples", "default", "deprecated",
    "readOnly", "writeOnly",
})

# Keywords this subset validator actually applies. Anything outside the union
# of these two sets makes _check fail closed: a schema keyword that is silently
# ignored is worse than an absent one, because the schema reads as enforced.
_APPLIED_KEYWORDS = frozenset({
    "$ref", "type", "enum", "const",
    "properties", "patternProperties", "additionalProperties", "required",
    "items", "minItems", "maxItems", "uniqueItems",
    "contains", "minContains", "maxContains",
    "pattern", "minLength", "maxLength",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
})

_KNOWN_KEYWORDS = _ANNOTATION_KEYWORDS | _APPLIED_KEYWORDS

_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float), "null": type(None),
}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# Where a schema nests other schemas, by shape. Everything not listed holds
# data (enum members, const values, required names, bounds) and is not walked.
_SCHEMA_VALUED = ("items", "contains", "not", "if", "then", "else", "additionalProperties")
_SCHEMA_LIST_VALUED = ("allOf", "anyOf", "oneOf")
_SCHEMA_MAP_VALUED = ("properties", "patternProperties", "$defs", "definitions")


def _assert_supported(schema, label):
    """Reject any unsupported keyword anywhere in the document, before matching.

    Checking only the branches a value happens to reach would let an unapplied
    keyword hide behind a sibling branch that matches, which is the silent-skip
    failure this validator exists to prevent.
    """
    if isinstance(schema, bool) or schema is None:
        return
    if not isinstance(schema, dict):
        _fail(f"{label}: invalid schema {schema!r}")
    unknown = sorted(set(schema) - _KNOWN_KEYWORDS)
    if unknown:
        raise SchemaSupportError(
            f"{label}: unsupported schema keywords {unknown}; this validator "
            "fails closed rather than accepting data it cannot check"
        )
    for keyword in _SCHEMA_VALUED:
        if keyword in schema:
            _assert_supported(schema[keyword], f"{label}/{keyword}")
    for keyword in _SCHEMA_LIST_VALUED:
        if keyword not in schema:
            continue
        branches = schema[keyword]
        if not isinstance(branches, list):
            raise SchemaSupportError(
                f"{label}/{keyword}: must be a list of schemas, got {type(branches).__name__}"
            )
        for index, branch in enumerate(branches):
            _assert_supported(branch, f"{label}/{keyword}[{index}]")
    for keyword in _SCHEMA_MAP_VALUED:
        if keyword not in schema:
            continue
        entries = schema[keyword]
        if not isinstance(entries, dict):
            raise SchemaSupportError(
                f"{label}/{keyword}: must be an object of schemas, got {type(entries).__name__}"
            )
        for name, branch in entries.items():
            _assert_supported(branch, f"{label}/{keyword}.{name}")


def _resolve_ref(ref, root, label):
    """Resolve a local JSON Pointer ($ref) against the root schema."""
    if not isinstance(ref, str) or not ref.startswith("#"):
        raise SchemaSupportError(f"{label}: only local $ref is supported, got {ref!r}")
    pointer = ref[1:]
    if pointer.startswith("/"):
        pointer = pointer[1:]
    target = root
    if pointer:
        for raw in pointer.split("/"):
            token = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(target, list):
                try:
                    target = target[int(token)]
                except (ValueError, IndexError) as error:
                    raise SchemaSupportError(
                        f"{label}: $ref {ref} does not resolve"
                    ) from error
            elif isinstance(target, dict) and token in target:
                target = target[token]
            else:
                raise SchemaSupportError(f"{label}: $ref {ref} does not resolve")
    if not isinstance(target, dict):
        raise SchemaSupportError(f"{label}: $ref {ref} does not point at a schema object")
    return target


def _matches(value, schema, root, refs=frozenset()):
    """True when value validates against schema. Used by the boolean keywords.

    `refs` carries the caller's active $ref chain so a cycle reached through a
    boolean keyword is reported as a circular reference rather than recursing
    until the interpreter runs out of stack.
    """
    try:
        _check(value, schema, "?", root, refs)
    except SchemaSupportError:
        raise
    except ManifestError:
        return False
    return True


def _check(value, schema, label, root=None, _refs=frozenset()):
    if root is None:
        root = schema
        _assert_supported(schema, label)
    if schema is True:
        return
    if schema is False:
        _fail(f"{label}: schema forbids any value")
    if not isinstance(schema, dict):
        _fail(f"{label}: invalid schema {schema!r}")

    unknown = sorted(set(schema) - _KNOWN_KEYWORDS)
    if unknown:
        _fail(f"{label}: unsupported schema keywords {unknown}; this validator "
              "fails closed rather than accepting data it cannot check")

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in _refs:
            raise SchemaSupportError(f"{label}: circular $ref {ref}")
        _check(value, _resolve_ref(ref, root, label), label, root, _refs | {ref})

    if "const" in schema and value != schema["const"]:
        _fail(f"{label}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        _fail(f"{label}: {value!r} not in {schema['enum']}")

    types = schema.get("type")
    if isinstance(types, str):
        types = [types]
    if types:
        ok = False
        for name in types:
            if name not in _TYPES:
                raise SchemaSupportError(f"{label}: unsupported type {name!r}")
            if name in ("integer", "number") and isinstance(value, bool):
                continue
            if name == "integer" and isinstance(value, float):
                continue
            if isinstance(value, _TYPES[name]):
                ok = True
        if not ok:
            _fail(f"{label}: expected type {types}, got {type(value).__name__}")

    for keyword in ("allOf", "anyOf", "oneOf"):
        if keyword not in schema:
            continue
        branches = schema[keyword]
        if not isinstance(branches, list):
            _fail(f"{label}: {keyword} must be a list")
        if keyword == "allOf":
            for index, branch in enumerate(branches):
                _check(value, branch, f"{label}/allOf[{index}]", root, _refs)
        else:
            hits = sum(1 for branch in branches if _matches(value, branch, root, _refs))
            if keyword == "anyOf" and hits == 0:
                _fail(f"{label}: does not match any anyOf branch")
            if keyword == "oneOf" and hits != 1:
                _fail(f"{label}: matches {hits} oneOf branches, expected exactly 1")

    if "not" in schema and _matches(value, schema["not"], root, _refs):
        _fail(f"{label}: must not match the 'not' schema")

    if "if" in schema:
        branch = "then" if _matches(value, schema["if"], root, _refs) else "else"
        if branch in schema:
            _check(value, schema[branch], f"{label}/{branch}", root, _refs)

    if value is None:
        return

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            _fail(f"{label}: {value!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            _fail(f"{label}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            _fail(f"{label}: longer than {schema['maxLength']}")

    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            _fail(f"{label}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            _fail(f"{label}: above maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            _fail(f"{label}: not above exclusiveMinimum {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            _fail(f"{label}: not below exclusiveMaximum {schema['exclusiveMaximum']}")

    if isinstance(value, list):
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            _fail(f"{label}: items must be unique")
        if "minItems" in schema and len(value) < schema["minItems"]:
            _fail(f"{label}: needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            _fail(f"{label}: allows at most {schema['maxItems']} items")
        if "items" in schema:
            for index, item in enumerate(value):
                _check(item, schema["items"], f"{label}[{index}]", root, _refs)
        if "contains" in schema:
            hits = sum(1 for item in value if _matches(item, schema["contains"], root, _refs))
            minimum = schema.get("minContains", 1)
            if hits < minimum:
                _fail(f"{label}: needs at least {minimum} item(s) matching 'contains', found {hits}")
            if "maxContains" in schema and hits > schema["maxContains"]:
                _fail(f"{label}: allows at most {schema['maxContains']} matching item(s), found {hits}")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        pattern_properties = schema.get("patternProperties", {})
        additional = schema.get("additionalProperties", True)

        missing = [key for key in schema.get("required", []) if key not in value]
        if missing:
            _fail(f"{label}: missing required keys {missing}")

        def _is_declared(key):
            if key in properties:
                return True
            return any(re.search(expression, key) for expression in pattern_properties)

        if additional is False:
            unknown = sorted(key for key in value if not _is_declared(key))
            if unknown:
                _fail(f"{label}: unknown keys {unknown}")

        for key, item in value.items():
            matched = False
            if key in properties:
                _check(item, properties[key], f"{label}.{key}", root, _refs)
                matched = True
            for expression, subschema in pattern_properties.items():
                if re.search(expression, key):
                    _check(item, subschema, f"{label}.{key}", root, _refs)
                    matched = True
            if not matched and isinstance(additional, dict):
                _check(item, additional, f"{label}.{key}", root, _refs)

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
