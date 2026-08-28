import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_governed_decisions.py"
SCHEMA_PATH = ROOT / ".quirk" / "schemas" / "governed-decision.schema.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_governed_decisions", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load governed decision validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GovernedDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module()

    def valid_decision(self):
        decision = {
            "schema_version": "governed-decision.v1",
            "decision_id": "qdecision.control-booth-boundary",
            "repository": "Quirk-Systems/Quirk",
            "subject": {
                "pull_request": 5,
                "base_commit": "1" * 40,
                "head_commit": "2" * 40,
                "changed_paths": ["README.md", "venues/control-booth/index.html"],
            },
            "evidence": {
                "receipts": [
                    {
                        "receipt_id": "qreceipt.control-booth-proof",
                        "receipt_sha256": "sha256:" + "a" * 64,
                        "covered_head_commit": "2" * 40,
                    }
                ]
            },
            "classification": "BOUNDARY_ONLY",
            "disposition": "REVIEW",
            "reason": "The exact candidate head preserves the no-authority boundary but still needs human review.",
            "limitations": ["No merge, canon, release, deployment, or publication authority is granted."],
            "actor": {
                "identity": "bryansayler",
                "authority_ref": None,
                "decided_at": "2026-08-28T14:00:00Z",
            },
            "authority": {
                "effect": "none",
                "required_next": ["merge"],
            },
            "staleness": {"stale_if_head_changes": True},
            "decision_sha256": "sha256:" + "0" * 64,
        }
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        return decision

    def test_valid_decision_passes(self):
        decision = self.valid_decision()
        self.validator.validate_decision(decision)

    def test_schema_is_closed_and_binds_exact_range(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        subject = schema["properties"]["subject"]
        self.assertFalse(subject["additionalProperties"])
        self.assertEqual(
            subject["required"],
            ["pull_request", "base_commit", "head_commit", "changed_paths"],
        )
        self.assertEqual(schema["properties"]["authority"]["properties"]["effect"]["const"], "none")

    def test_receipt_must_cover_subject_head(self):
        decision = self.valid_decision()
        decision["evidence"]["receipts"][0]["covered_head_commit"] = "3" * 40
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "covered_head_commit must equal subject.head_commit"):
            self.validator.validate_decision(decision)

    def test_material_scope_change_cannot_continue(self):
        decision = self.valid_decision()
        decision["classification"] = "MATERIAL_SCOPE_CHANGE"
        decision["disposition"] = "CONTINUE"
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "MATERIAL_SCOPE_CHANGE cannot use disposition CONTINUE"):
            self.validator.validate_decision(decision)

    def test_authority_change_cannot_continue(self):
        decision = self.valid_decision()
        decision["classification"] = "AUTHORITY_CHANGE"
        decision["disposition"] = "CONTINUE"
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "AUTHORITY_CHANGE cannot use disposition CONTINUE"):
            self.validator.validate_decision(decision)

    def test_decision_cannot_grant_authority(self):
        decision = self.valid_decision()
        decision["authority"]["effect"] = "merge"
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "authority.effect must be none"):
            self.validator.validate_decision(decision)

    def test_non_insufficient_decision_requires_evidence(self):
        decision = self.valid_decision()
        decision["evidence"]["receipts"] = []
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "requires at least one exact-head evidence receipt"):
            self.validator.validate_decision(decision)

    def test_insufficient_evidence_may_record_no_receipt(self):
        decision = self.valid_decision()
        decision["classification"] = "INSUFFICIENT_EVIDENCE"
        decision["disposition"] = "HOLD"
        decision["evidence"]["receipts"] = []
        decision["authority"]["required_next"] = []
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        self.validator.validate_decision(decision)

    def test_head_change_makes_decision_stale_for_current_action(self):
        decision = self.valid_decision()
        with self.assertRaisesRegex(self.validator.DecisionError, "decision is stale for current head"):
            self.validator.validate_decision(decision, current_head="4" * 40)

    def test_digest_tampering_fails(self):
        decision = self.valid_decision()
        decision["reason"] = "Changed after signing."
        with self.assertRaisesRegex(self.validator.DecisionError, "decision_sha256 does not match"):
            self.validator.validate_decision(decision)

    def test_changed_paths_are_sorted_and_unique(self):
        decision = self.valid_decision()
        decision["subject"]["changed_paths"] = ["z.txt", "a.txt", "a.txt"]
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "changed_paths must be sorted and unique"):
            self.validator.validate_decision(decision)

    def test_reauthorize_disposition_names_required_next_gate(self):
        decision = self.valid_decision()
        decision["classification"] = "MATERIAL_SCOPE_CHANGE"
        decision["disposition"] = "REAUTHORIZE"
        decision["authority"]["required_next"] = []
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "REAUTHORIZE requires authority.required_next to include reauthorize"):
            self.validator.validate_decision(decision)

    def test_unknown_fields_fail_closed(self):
        decision = self.valid_decision()
        decision["silent_promotion"] = True
        decision["decision_sha256"] = self.validator.canonical_decision_digest(decision)
        with self.assertRaisesRegex(self.validator.DecisionError, "unexpected fields"):
            self.validator.validate_decision(decision)


if __name__ == "__main__":
    unittest.main()
