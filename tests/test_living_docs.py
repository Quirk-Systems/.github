import datetime as dt
import importlib.util
import os
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
        self.assert_rejects_at(text, "todo.md", fragment)

    def assert_rejects_at(self, text, name, fragment):
        with self.assertRaises(ValueError) as ctx:
            self.module.validate_document(self.write(text, name), self.tmp, TODAY)
        self.assertIn(fragment, str(ctx.exception))

    def header(self, kind):
        return (f"# {kind.title()}: fixture\n\nKind: {kind}\nStatus: active\nOwner: @bryansayler\n"
                "Repository: `Quirk-Systems/.github`\n"
                "Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`\n"
                "Reviewed: 2026-09-20\nReview by: 2026-10-04\n"
                "Derived from: `docs/upstream.md`\nAuthority effect: **none**\n")

    def opt_in(self, kind):
        """A brief or plan outside the contract directories, opting in with its header."""
        body = "".join(f"\n{section}\n\nBody.\n" for section in self.module.KIND_SECTIONS[kind])
        return self.header(kind) + body

    def roadmap(self):
        return self.header("roadmap") + (
            "\n## Now\n\n- [ ] ship the contract\n"
            "\n## Next\n\n- [ ] repin the callers\n"
            "\n## Later\n\n- [ ] offer a reusable workflow\n"
            "\n## Done\n\n- [x] enable the dependency graph (evidence: PR #30)\n"
            "\n## Decisions awaiting an owner\n\n- [ ] decide PR #20 (owner: @bryansayler)\n")

    def test_repository_documents_pass_strict_on_their_review_dates(self):
        self.assertEqual(self.module.main(["--strict", "--today", TODAY.isoformat()]), 0)

    def test_repository_documents_are_fresh_today(self):
        """The contract only bites if freshness is checked against the real date.

        scripts/validate.sh runs this validator with --strict, so a lapsed
        document turns the gate red. This test fails the same way, naming the
        documents to re-read and bump or retire.
        """
        stale = [
            f"{path.relative_to(ROOT)}: {message}"
            for path in self.module.discover(ROOT)
            for message in [self.module.validate_document(path, ROOT)[1]]
            if message
        ]
        self.assertEqual(stale, [], "living documents are past their review date; re-read and bump or retire them")

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

    def test_rejects_omitted_or_empty_lineage(self):
        self.assert_rejects(GOOD_TODO.replace("Derived from: `docs/upstream.md`\n", ""), "derived_from")
        self.assert_rejects(GOOD_TODO.replace("Derived from: `docs/upstream.md`", "Derived from:"), "derived_from")

    def test_rejects_lineage_outside_the_checkout_even_when_it_exists(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        external = outside / "external-evidence.md"
        external.write_text("# outside\n", encoding="utf-8")
        traversal = os.path.relpath(external, self.tmp)
        self.assertTrue(traversal.startswith(".."))
        self.assert_rejects(GOOD_TODO.replace("docs/upstream.md", traversal), "escapes the repository")
        self.assert_rejects(GOOD_TODO.replace("docs/upstream.md", str(external)), "must be repository-relative")

    def test_every_list_marker_needs_a_checkbox(self):
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "* first task"), "## Open")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "+ first task"), "## Open")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "1. first task"), "## Open")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "2) first task"), "## Open")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "- [ ] first task\n  1. nested task"), "## Open")
        self.assert_rejects(GOOD_TODO.replace("- [ ] first task", "- [ ] first task\n  - nested task"), "## Open")
        data, _ = self.module.validate_document(
            self.write(GOOD_TODO.replace("- [ ] first task", "- [ ] first task\n  - [ ] nested task")), self.tmp, TODAY)
        self.assertEqual(data["kind"], "todo")

    def test_contract_directories_are_validated_unconditionally(self):
        (self.tmp / "docs" / "todos").mkdir()
        self.write("# Todo: no header\n\nProse only, no Kind line.\n", name="todos/late.md")
        self.assertEqual([p.name for p in self.module.discover(self.tmp)], ["late.md"])
        with self.assertRaises(ValueError) as ctx:
            self.module.main(["--root", str(self.tmp), "--today", TODAY.isoformat()])
        self.assertIn("Kind", str(ctx.exception))

    def test_a_comma_inside_one_lineage_entry_fails_loudly(self):
        """Commas separate entries, so an entry containing one is split and must not pass."""
        self.assert_rejects(GOOD_TODO.replace("`docs/upstream.md`", "`https://example.invalid/a,b`"),
                            "derived-from path does not exist: b")

    def test_urls_in_lineage_are_not_resolved_locally(self):
        text = GOOD_TODO.replace("`docs/upstream.md`", "`https://github.com/Quirk-Systems/.github/pull/30`")
        data, _ = self.module.validate_document(self.write(text), self.tmp, TODAY)
        self.assertEqual(data["derived_from"], ["https://github.com/Quirk-Systems/.github/pull/30"])

    def test_documents_without_kind_line_are_not_living_documents(self):
        self.write("# Ordinary doc\n\nProse only.\n", name="plain.md")
        self.assertEqual([p.name for p in self.module.discover(self.tmp)], [])

    def test_decisions_awaiting_an_owner_needs_unchecked_boxes(self):
        roadmap = self.roadmap()
        self.assertIsNone(self.module.validate_document(self.write(roadmap, "roadmap.md"), self.tmp, TODAY)[1])
        self.assert_rejects_at(roadmap.replace("- [ ] decide PR #20", "- decide PR #20"),
                               "roadmap.md", "Decisions awaiting an owner")
        self.assert_rejects_at(roadmap.replace("- [ ] decide PR #20", "- [x] decide PR #20"),
                               "roadmap.md", "Decisions awaiting an owner")

    def test_opted_in_brief_and_plan_validate_their_own_sections(self):
        for kind, name in (("brief", "brief.md"), ("plan", "plan.md")):
            text = self.opt_in(kind)
            data, stale = self.module.validate_document(self.write(text, name), self.tmp, TODAY)
            self.assertEqual(data["kind"], kind)
            self.assertIsNone(stale)
            self.assertIn(self.tmp / "docs" / name, self.module.discover(self.tmp))
            missing = self.module.KIND_SECTIONS[kind][0]
            self.assert_rejects_at(text.replace(f"{missing}\n\nBody.\n", ""), name, "missing section")

    def test_opted_in_kinds_reuse_the_markdown_template_sections(self):
        from validate_templates import REQUIRED_SECTIONS
        self.assertEqual(self.module.KIND_SECTIONS["brief"], REQUIRED_SECTIONS["BRIEF.md"])
        self.assertEqual(self.module.KIND_SECTIONS["plan"], REQUIRED_SECTIONS["PLAN.md"])


if __name__ == "__main__":
    unittest.main()
