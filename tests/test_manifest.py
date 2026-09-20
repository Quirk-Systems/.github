import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_manifest.py"
SCHEMA = ROOT / ".quirk" / "schemas" / "repository-manifest.schema.json"
MANIFEST = ROOT / ".quirk" / "manifest.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def valid(self):
        return copy.deepcopy(self.manifest)

    def assert_rejected(self, data, fragment):
        with self.assertRaises(self.module.ManifestError) as caught:
            self.module.validate_manifest(data, self.schema, ROOT)
        self.assertIn(fragment, str(caught.exception))

    def test_repository_manifest_is_valid(self):
        self.assertEqual(self.module.main([str(MANIFEST)]), 0)

    def test_schema_is_closed_and_2020_12(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(self.schema["additionalProperties"])
        for key in ("registry", "policy", "semantic_impact"):
            self.assertFalse(self.schema["properties"][key]["additionalProperties"], key)

    def test_reusable_workflow_keys_remain_required(self):
        for key in ("repository", "registry", "policy", "semantic_impact"):
            self.assertIn(key, self.schema["required"])

    def test_unknown_key_fails_closed(self):
        data = self.valid()
        data["surprise"] = True
        self.assert_rejected(data, "unknown keys")

    def test_missing_required_key_fails(self):
        data = self.valid()
        del data["owner"]
        self.assert_rejected(data, "missing required keys")

    def test_wrong_authority_fails(self):
        data = self.valid()
        data["registry"]["authority"] = "Quirk-Systems/quirk-core"
        self.assert_rejected(data, "must equal")

    def test_undocumented_change_class_fails(self):
        data = self.valid()
        data["semantic_impact"]["default_change_class"] = "projection-or-domain-extension"
        self.assert_rejected(data, "not in")

    def test_invalid_primary_class_and_lifecycle_fail(self):
        data = self.valid()
        data["primary_class"] = "product"
        self.assert_rejected(data, "primary_class")
        data = self.valid()
        data["lifecycle"] = "experimental"
        self.assert_rejected(data, "lifecycle")

    def test_policy_mode_must_be_warn_or_required(self):
        data = self.valid()
        data["policy"]["mode"] = "off"
        self.assert_rejected(data, "policy.mode")

    def test_missing_local_extension_file_fails(self):
        data = self.valid()
        data["semantic_impact"]["local_extensions"] = [".quirk/does-not-exist.json"]
        self.assert_rejected(data, "does not exist")

    def test_owner_must_be_a_handle(self):
        data = self.valid()
        data["owner"] = "bryan"
        self.assert_rejected(data, "owner")

    def test_duplicate_projections_fail(self):
        data = self.valid()
        data["semantic_impact"]["projections"] = ["ci", "ci"]
        self.assert_rejected(data, "unique")


if __name__ == "__main__":
    unittest.main()
