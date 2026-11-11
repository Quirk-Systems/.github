import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLLOUT_PATH = ROOT / "docs" / "governance" / "REQUIRED_CHECKS_ROLLOUT.md"


class RequiredChecksRolloutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ROLLOUT_PATH.read_text(encoding="utf-8")

    def test_rollout_records_post_admission_boundary(self):
        self.assertIn("Authorize an organization owner to perform the owner-only rollout", self.text)
        self.assertIn("only after draft PR", self.text)
        self.assertIn("`Quirk-Systems/.github#9`", self.text)
        self.assertIn("does not activate a ruleset", self.text)
        self.assertIn("workflow as proof that enforcement exists", self.text)

    def test_required_receipt_template_fields_are_present(self):
        for field in (
            "repository:",
            "ruleset_id:",
            "mode_before: Evaluate",
            "mode_after: Active | Evaluate",
            "policy_commit:",
            "representative_pr:",
            "positive_run:",
            "negative_run:",
            "observed_check_context:",
            "actor:",
            "decided_at:",
            "rollback:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.text)

    def test_owner_only_sequence_includes_positive_and_negative_proofs(self):
        self.assertIn("Prove the positive path with a fully receipted exact range", self.text)
        self.assertIn("the governance check must fail closed", self.text)
        self.assertIn("Restore the test branch to a valid receipted state", self.text)
        self.assertIn("Change the ruleset from **Evaluate** to **Active** only through an explicit", self.text)


if __name__ == "__main__":
    unittest.main()
