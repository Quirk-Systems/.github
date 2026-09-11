import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "governance" / "MAINTENANCE_INDEX.md"

ALLOWED_RELATIONSHIPS = {
    "implements",
    "evidence-for",
    "supersedes",
    "blocked-by",
    "references",
}


class MaintenanceIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = INDEX_PATH.read_text(encoding="utf-8")

    def test_index_has_required_links_and_markers(self):
        self.assertIn(
            "../../prompt-packs/quirk/prompts/quirk-orient.prompt.md",
            self.text,
        )
        self.assertIn(
            "../../prompt-packs/quirk/prompts/quirk-review.prompt.md",
            self.text,
        )
        self.assertIn(
            "../../prompt-packs/quirk/prompts/quirk-compound.prompt.md",
            self.text,
        )
        self.assertIn("./EVIDENCE_BINDING.md", self.text)
        self.assertIn("Observed at: **2026-09-11 UTC**", self.text)
        self.assertIn("Authority effect: **none**", self.text)
        self.assertIn("they are not a privacy-enforcement", self.text)
        self.assertIn("mechanism or a proof-producing reasoning guard", self.text)

    def test_index_table_binds_records_to_relationships_and_exact_commits(self):
        rows = [
            line
            for line in self.text.splitlines()
            if line.startswith("| `") or line.startswith("| `.github") or line.startswith("| `project-scaffold")
        ]
        self.assertGreaterEqual(len(rows), 12)

        for row in rows:
            columns = [column.strip() for column in row.split("|")[1:-1]]
            self.assertEqual(len(columns), 8, row)
            self.assertIn(columns[5].strip("`"), ALLOWED_RELATIONSHIPS, row)
            self.assertIn("2026-09-11", columns[6], row)
            if columns[4] != "—":
                self.assertRegex(columns[4], r"[0-9a-f]{40}", row)

    def test_negative_control_section_records_non_inference_statements(self):
        self.assertIn("not prove a Closure Harness implementation", self.text)
        self.assertIn("It is not evidence that `quirk-core#4` enforcement is installed", self.text)
        self.assertIn("does not close", self.text)

    def test_privacy_section_marks_inaccessible_sources(self):
        self.assertIn("**inaccessible/unverified**", self.text)
        self.assertIn("copies no private document titles", self.text)
        self.assertIn("instead of being paraphrased as verified facts", self.text)
        self.assertIn(
            "document-level checks only confirm that this markdown keeps its explicit",
            self.text,
        )

    def test_local_links_resolve(self):
        for target in re.findall(r"\]\(([^)]+)\)", self.text):
            if target.startswith("http"):
                continue
            path = (INDEX_PATH.parent / target).resolve()
            self.assertTrue(path.exists(), target)


if __name__ == "__main__":
    unittest.main()
