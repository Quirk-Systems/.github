import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "agent-task.schema.json"
EXAMPLE = ROOT / "templates" / "agent-task.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_agent_tasks", ROOT / "scripts" / "validate_agent_tasks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AgentTaskContractTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def valid(self):
        return copy.deepcopy(self.example)

    def assert_rejected(self, task, fragment):
        with self.assertRaises(self.module.TaskError) as caught:
            self.module.validate_task(task, self.schema)
        self.assertIn(fragment, str(caught.exception))

    def test_example_validates_and_repository_has_no_orphan_records(self):
        self.assertEqual(self.module.main(["--file", str(EXAMPLE)]), 0)
        self.assertEqual(self.module.main([]), 0)

    def test_idempotency_key_is_bound_to_repository_base_and_task(self):
        task = self.valid()
        self.assertEqual(task["idempotency_key"], self.module.idempotency_key(task))
        task["task_id"] = "qtask.other"
        self.assert_rejected(task, "idempotency_key must be")

    def test_authority_effect_cannot_be_granted(self):
        task = self.valid()
        task["authority"]["effect"] = "authorized"
        self.assert_rejected(task, "must equal")

    def test_wildcard_tools_fail(self):
        task = self.valid()
        task["tools"]["allowed"].append("*")
        self.assert_rejected(task, "wildcard")

    def test_tool_in_two_lists_fails(self):
        task = self.valid()
        task["tools"]["approval_gated"].append(task["tools"]["allowed"][0])
        self.assert_rejected(task, "both allowed and approval_gated")

    def test_forbidden_tools_must_name_consequential_actions(self):
        task = self.valid()
        task["tools"]["forbidden"] = ["rm -rf"]
        self.assert_rejected(task, "consequential actions")

    def test_path_in_both_lists_fails(self):
        task = self.valid()
        task["objective"]["forbidden_paths"].append(task["objective"]["allowed_paths"][0])
        self.assert_rejected(task, "both allowed and forbidden")

    def test_proposed_task_must_await_authorization(self):
        task = self.valid()
        task["authority"]["required_next"] = ["review"]
        self.assert_rejected(task, "must list authorize")

    def test_running_task_cannot_still_require_authorization(self):
        task = self.valid()
        task["status"] = "running"
        self.assert_rejected(task, "inconsistent with authorize")

    def test_unknown_key_fails_closed(self):
        task = self.valid()
        task["priority"] = "high"
        self.assert_rejected(task, "unknown keys")

    def test_short_sha_fails(self):
        task = self.valid()
        task["subject"]["base_commit"] = "abc"
        self.assert_rejected(task, "base_commit")


class IssueBodyTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def complete_body(self):
        answers = {name: "answered" for name in self.module.ISSUE_SECTIONS}
        answers["Base commit"] = "0" * 40
        answers["Human owner"] = "@bryansayler"
        answers["Shutdown authority"] = "@bryansayler"
        answers["Forbidden tools"] = "merge, approve reviews, deploy, publish, edit rulesets, read secrets"
        return "\n".join(f"### {name}\n\n{value}\n" for name, value in answers.items())

    def test_complete_body_passes(self):
        self.assertEqual(self.module.check_issue_body(self.complete_body()), [])

    def test_missing_and_unanswered_sections_are_reported(self):
        body = self.complete_body().replace("### Rollback plan\n\nanswered\n", "### Rollback plan\n\n_No response_\n")
        body = body.replace("### Residue\n\nanswered\n", "")
        findings = self.module.check_issue_body(body)
        self.assertIn("unanswered section: Rollback plan", findings)
        self.assertIn("missing section: Residue", findings)

    def test_short_sha_and_bad_handle_are_reported(self):
        body = self.complete_body().replace("0" * 40, "abc123").replace("### Human owner\n\n@bryansayler", "### Human owner\n\nbryan")
        findings = self.module.check_issue_body(body)
        self.assertTrue(any("40-character" in f for f in findings))
        self.assertTrue(any("single GitHub handle" in f for f in findings))

    def test_forbidden_tools_must_cover_consequential_actions(self):
        body = self.complete_body().replace("merge, approve reviews, deploy, publish, edit rulesets, read secrets", "rm -rf")
        findings = self.module.check_issue_body(body)
        self.assertTrue(any("Forbidden tools must name" in f for f in findings))

    def test_report_never_claims_authorization(self):
        report = self.module.issue_report([])
        self.assertIn("a form is not authorization", report)
        self.assertIn("authority effect none", report)

    def test_cli_writes_report_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "body.md"
            report = Path(tmp) / "report.md"
            body.write_text(self.complete_body(), encoding="utf-8")
            self.assertEqual(self.module.main(["--issue-body", str(body), "--report", str(report)]), 0)
            self.assertIn("form complete", report.read_text(encoding="utf-8"))
            body.write_text("### Owning repository\n\nx\n", encoding="utf-8")
            self.assertEqual(self.module.main(["--issue-body", str(body), "--report", str(report)]), 1)
            self.assertIn("not ready", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
