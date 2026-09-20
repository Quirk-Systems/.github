"""Contract tests for the JSON Schema subset checker shared by the validators.

`_check` in scripts/validate_manifest.py is imported by validate_portfolio.py,
validate_agent_tasks.py and validate_templates.py, and four of the repository's
schemas route their real constraints through `$ref`. A `$ref` the checker
ignored meant those constraints were never applied while the schema still read
as enforced, so these tests pin resolution and the fail-closed behaviour that
keeps an unimplemented keyword from silently admitting data.
"""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_manifest.py"
SCHEMAS = ROOT / ".quirk" / "schemas"
INVENTORY = ROOT / ".quirk" / "repositories.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SchemaSubsetTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.check = self.module._check
        self.error = self.module.ManifestError

    def assertRejects(self, value, schema, fragment):
        with self.assertRaises(self.error) as caught:
            self.check(value, schema, "x")
        self.assertIn(fragment, str(caught.exception))

    # --- $ref resolution -------------------------------------------------

    def test_ref_is_resolved_and_enforced(self):
        schema = {
            "type": "object",
            "properties": {"name": {"$ref": "#/$defs/nonEmptyString"}},
            "$defs": {"nonEmptyString": {"type": "string", "minLength": 1}},
        }
        self.check({"name": "ok"}, schema, "x")
        self.assertRejects({"name": 42}, schema, "expected type ['string']")
        self.assertRejects({"name": ""}, schema, "shorter than 1")

    def test_ref_beneath_array_items_is_enforced(self):
        schema = {
            "type": "array",
            "items": {"$ref": "#/$defs/entry"},
            "$defs": {
                "entry": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["visibility"],
                    "properties": {"visibility": {"enum": ["public", "private"]}},
                }
            },
        }
        self.check([{"visibility": "public"}], schema, "x")
        self.assertRejects([{"visibility": ["public"]}], schema, "not in ['public', 'private']")
        self.assertRejects([{"visibility": "public", "extra": 1}], schema, "unknown keys ['extra']")

    def test_unresolvable_and_remote_refs_fail(self):
        self.assertRejects({}, {"$ref": "#/$defs/missing"}, "does not resolve")
        self.assertRejects({}, {"$ref": "https://example.test/s.json"}, "only local $ref")

    def test_circular_ref_is_detected_not_hung(self):
        schema = {"$ref": "#/$defs/loop", "$defs": {"loop": {"$ref": "#/$defs/loop"}}}
        self.assertRejects({}, schema, "circular $ref")

    # --- fail closed -----------------------------------------------------

    def test_unsupported_keyword_fails_closed(self):
        self.assertRejects("anything", {"multipleOf": 3}, "unsupported schema keywords")
        self.assertRejects({}, {"propertyNames": {"pattern": "^a"}}, "unsupported schema keywords")

    def test_every_repository_schema_uses_only_supported_keywords(self):
        for path in sorted(SCHEMAS.glob("*.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(schema=path.name):
                self.check_schema_keywords(schema, path.name)

    def check_schema_keywords(self, node, name):
        known = self.module._KNOWN_KEYWORDS
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("properties", "patternProperties", "$defs", "definitions"):
                    for child in (value or {}).values():
                        self.check_schema_keywords(child, name)
                    continue
                self.assertIn(key, known, f"{name}: schema keyword {key!r} is not applied by _check")
                self.check_schema_keywords(value, name)
        elif isinstance(node, list):
            for child in node:
                self.check_schema_keywords(child, name)

    # --- the composition keywords the repository's schemas rely on -------

    def test_boolean_and_conditional_keywords(self):
        self.check("s", {"anyOf": [{"type": "string"}, {"type": "null"}]}, "x")
        self.assertRejects(1, {"anyOf": [{"type": "string"}, {"type": "null"}]}, "any anyOf branch")

        one_of = {"oneOf": [{"type": "string"}, {"type": "null"}]}
        self.check(None, one_of, "x")
        self.assertRejects(1, one_of, "matches 0 oneOf branches")

        self.assertRejects("no", {"not": {"type": "string"}}, "must not match")

        conditional = {
            "if": {"properties": {"kind": {"const": "supersede"}}, "required": ["kind"]},
            "then": {"required": ["successor"]},
        }
        self.check({"kind": "other"}, conditional, "x")
        self.check({"kind": "supersede", "successor": "y"}, conditional, "x")
        self.assertRejects({"kind": "supersede"}, conditional, "missing required keys ['successor']")

    def test_contains_and_item_bounds(self):
        schema = {"type": "array", "maxItems": 2,
                  "contains": {"const": "needle"}, "minContains": 1}
        self.check(["needle"], schema, "x")
        self.assertRejects(["hay"], schema, "matching 'contains'")
        self.assertRejects(["needle", "a", "b"], schema, "at most 2 items")

    def test_pattern_properties_are_applied(self):
        schema = {"type": "object", "additionalProperties": False,
                  "patternProperties": {"^x-": {"type": "string"}}}
        self.check({"x-a": "ok"}, schema, "x")
        self.assertRejects({"x-a": 1}, schema, "expected type ['string']")
        self.assertRejects({"y": "no"}, schema, "unknown keys ['y']")

    # --- the reported bug, end to end ------------------------------------

    def test_real_inventory_rejects_malformed_fields_behind_ref(self):
        schema = json.loads((SCHEMAS / "repository-inventory.schema.json").read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.check(inventory, schema, "inventory")

        for field, bad in (("visibility", ["public"]), ("consumers_and_dependencies", "a string")):
            with self.subTest(field=field):
                broken = copy.deepcopy(inventory)
                broken["repositories"][0][field] = bad
                with self.assertRaises(self.error):
                    self.check(broken, schema, "inventory")


if __name__ == "__main__":
    unittest.main()
