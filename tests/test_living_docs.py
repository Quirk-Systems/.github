import datetime as dt
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = dt.date(2026, 9, 20)

GOOD_TODO = """# Todo: fixture

Kind: todo
Status: active
Owner: @bryansayler
Repository: `Quirk-Systems/.github`
Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`
Reviewed: 2026-09-20
Review by: 2026-10-04
Derived from: `docs/upstream.md`
Authority effect: **none**

## Open

- [ ] first task

## Blocked

None.

## Done

- [x] done task
"""


def load_module():
    spec = importlib.util.spec_from_file_location("validate_living_docs", ROOT / "scripts" / "validate_living_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LivingDocumentTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / ".quirk" / "schemas").mkdir(parents=True)
        shutil.copy(ROOT / ".quirk" / "schemas" / "living-document.schema.json", self.tmp / ".quirk" / "schemas")
        (self.tmp / "docs").mkdir()
        (self.tmp / "docs" / "upstream.md").write_text("# upstream\n", encoding="utf-8")

    def write(self, text, name="todo.md"):
        path = self.tmp / "docs" / name
        path.write_text(text, encoding="utf-8")
        return path

    def assert_rejects(self, text, fragment):
        with self.assertRaises(ValueError) as ctx:
            self.module.validate_document(self.write(text), self.tmp, TODAY)
        self.assertIn(fragment, str(ctx.exception))

    def test_repository_documents_pass_strict_on_their_review_dates(self):
        self.assertEqual(self.module.main(["--strict", "--today", TODAY.isoformat()]), 0)

    def test_every_kind_has_a_template_and_an_instance(self):
        kinds = {self.module.validate_document(p, ROOT, TODAY)[0]["kind"] for p in self.module.discover(ROOT)}
        for kind in ("intention", "goal", "roadmap", "todo"):
            self.assertIn(kind, kinds)
            self.assertTrue((ROOT / "templates" / f"{kind.upper()}.md").is_file(), kind)

    def test_fixture_passes_and_is_fresh(self):
        data, stale = self.module.validate_document(self.write(GOOD_TODO), self.tmp, TODAY)
        self.assertEqual(data["kind"], "todo")
        self.assertEqual(data["derived_from"], ["docs/upstream.md"])
        self.assertIsNone(stale)

    def test_stale_is_reported_and_fails_only_with_strict(self):
        self.write(GOOD_TODO)
        late = dt.date(2026, 11, 1).isoformat()
        self.assertEqual(self.module.main(["--root", str(self.tmp), "--today", late]), 0)
        self.assertEqual(self.module.main(["--root", str(self.tmp), "--today", late, "--strict"]), 1)

    def test_done_documents_never_go_stale(self):
        text = GOOD_TODO.replace("Status: active", "Status: done")
        _, stale = self.module.validate_document(self.write(text), self.tmp, dt.date(2027, 1, 1))
        self.assertIsNone(stale)

    def test_rejects_unknown_kind_status_and_short_head(self):
        self.assert_rejects(GOOD_TODO.replace("Kind: todo", "Kind: vibe"), "kind")
        self.assert_rejects(GOOD_TODO.replace("Status: active", "Status: shipped"), "status")
        self.assert_rejects(GOOD_TODO.replace("62218674c00d6a9d4c81db13000d25c5f37afc6d", "6221867"), "observed_head")

    def test_rejects_authority_grant_and_unknown_header_key(self):
        self.assert_rejects(GOOD_TODO.replace("Authority effect: **none**", "Authority effect: **merge**"), "authority")
        self.assert_rejects(GOOD_TODO.replace("Owner: @bryansayler", "Owner: @bryansayler\nMood: great"), "unexpected")

    def test_rejects_missing_section_and_bad_checkbox(self):
        self.assert_rejects(GOOD_TODO.replace("## Blocked\n\nNone.\n", ""), "missing section")
        self.assert_rejects(GOOD_TODO.replace("- [x] done task", "- [ ] done task"), "## Done")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "- first task"), "## Open")

    def test_rejects_missing_lineage_and_reversed_dates(self):
        self.assert_rejects(GOOD_TODO.replace("docs/upstream.md", "docs/missing.md"), "derived-from")
        self.assert_rejects(GOOD_TODO.replace("Reviewed: 2026-09-20", "Reviewed: 2026-12-01"), "after Review by")

    def test_urls_in_lineage_are_not_resolved_locally(self):
        text = GOOD_TODO.replace("`docs/upstream.md`", "`https://github.com/Quirk-Systems/.github/pull/30`")
        data, _ = self.module.validate_document(self.write(text), self.tmp, TODAY)
        self.assertEqual(data["derived_from"], ["https://github.com/Quirk-Systems/.github/pull/30"])

    def test_documents_without_kind_line_are_not_living_documents(self):
        self.write("# Ordinary doc\n\nProse only.\n", name="plain.md")
        self.assertEqual([p.name for p in self.module.discover(self.tmp)], [])


if __name__ == "__main__":
    unittest.main()
