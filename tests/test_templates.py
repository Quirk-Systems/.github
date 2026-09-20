import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("validate_templates", ROOT / "scripts" / "validate_templates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TemplateContractTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_repository_templates_pass(self):
        self.assertEqual(self.module.main([]), 0)

    def test_single_document_modes(self):
        self.assertEqual(self.module.main(["--artifact", str(ROOT / "templates" / "artifact-manifest.json")]), 0)
        self.assertEqual(self.module.main(["--dataset-card", str(ROOT / "templates" / "dataset-card.json")]), 0)

    def test_every_schema_is_closed_2020_12(self):
        self.assertGreaterEqual(self.module.validate_schemas(), 7)

    def test_every_skill_referenced_by_templates_index_exists(self):
        index = (ROOT / "templates" / "README.md").read_text(encoding="utf-8")
        for skill in ("quirk-brief", "quirk-plan", "quirk-evidence-receipt", "quirk-artifact-forge", "quirk-dataset-card"):
            self.assertIn(f"`{skill}`", index)
            self.assertTrue((ROOT / ".github" / "skills" / skill / "SKILL.md").is_file(), skill)
            self.assertTrue((ROOT / ".claude" / "skills" / skill / "SKILL.md").is_file(), skill)

    def mutate_and_validate(self, name, schema, mutate):
        data = json.loads((ROOT / "templates" / name).read_text(encoding="utf-8"))
        data = copy.deepcopy(data)
        mutate(data)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.module.validate_document(path, schema)

    def test_artifact_manifest_rejects_authority_grant(self):
        def mutate(data):
            data["authority"]["effect"] = "publish"
        self.mutate_and_validate("artifact-manifest.json", "artifact-manifest.schema.json", mutate)

    def test_artifact_manifest_rejects_unknown_key_and_short_sha(self):
        def unknown(data):
            data["viral"] = True
        self.mutate_and_validate("artifact-manifest.json", "artifact-manifest.schema.json", unknown)

        def short(data):
            data["source"]["commit"] = "abc123"
        self.mutate_and_validate("artifact-manifest.json", "artifact-manifest.schema.json", short)

    def test_artifact_manifest_requires_outputs_with_digests(self):
        def mutate(data):
            data["outputs"][0]["sha256"] = "md5:abc"
        self.mutate_and_validate("artifact-manifest.json", "artifact-manifest.schema.json", mutate)

    def test_dataset_card_requires_limitations_and_out_of_scope(self):
        def limitations(data):
            data["known_limitations"] = []
        self.mutate_and_validate("dataset-card.json", "dataset-card.schema.json", limitations)

        def scope(data):
            data["out_of_scope_use"] = []
        self.mutate_and_validate("dataset-card.json", "dataset-card.schema.json", scope)

    def test_dataset_card_rejects_unknown_classification(self):
        def mutate(data):
            data["data_classification"] = "secret"
        self.mutate_and_validate("dataset-card.json", "dataset-card.schema.json", mutate)

    def test_governance_corpus_card_pins_a_real_commit(self):
        card = json.loads((ROOT / "datasets" / "quirk-governance-corpus" / "dataset-card.json").read_text(encoding="utf-8"))
        self.assertNotEqual(card["source"]["commit"], "0" * 40)
        self.assertEqual(card["authority"]["effect"], "none")
        self.assertFalse(card["collection"]["contains_personal_data"])


if __name__ == "__main__":
    unittest.main()
