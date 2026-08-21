"""Contract tests for the 2026-08-21 truthful topology snapshot."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / ".quirk" / "repositories.json"
LEDGER = ROOT / ".quirk" / "manual-prs.json"
VALIDATOR = ROOT / "scripts" / "validate_topology.py"
INVENTORY_SCHEMA = ROOT / ".quirk" / "schemas" / "repository-inventory.schema.json"
LEDGER_SCHEMA = ROOT / ".quirk" / "schemas" / "manual-pr-ledger.schema.json"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_topology  # noqa: E402


class TopologyContractsTest(unittest.TestCase):
    def load(self, path):
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def validate(self, inventory=INVENTORY, ledger=LEDGER):
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--inventory",
                str(inventory),
                "--pull-requests",
                str(ledger),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_snapshot_counts_and_unique_ids(self):
        inventory = self.load(INVENTORY)
        ledger = self.load(LEDGER)
        repositories = inventory["repositories"]
        pull_requests = ledger["pull_requests"]

        self.assertEqual(inventory["scope"]["expected_organization_repository_count"], 17)
        self.assertEqual(inventory["scope"]["expected_adjacent_repository_count"], 2)
        self.assertEqual(len(repositories), 19)
        self.assertEqual(len({item["repository"] for item in repositories}), 19)
        self.assertEqual(ledger["scope"]["expected_open_non_dependabot_pull_request_count"], 27)
        self.assertEqual(len(pull_requests), 27)
        self.assertEqual(len({item["id"] for item in pull_requests}), 27)

    def test_snapshot_uses_exact_expected_repository_and_pr_sets(self):
        inventory = self.load(INVENTORY)
        ledger = self.load(LEDGER)
        organization_repositories = {
            item["repository"]
            for item in inventory["repositories"]
            if item["scope"] == "organization"
        }
        adjacent_repositories = {
            item["repository"]
            for item in inventory["repositories"]
            if item["scope"] == "adjacent"
        }
        self.assertSetEqual(organization_repositories, validate_topology.EXPECTED_ORGANIZATION_REPOSITORIES)
        self.assertSetEqual(adjacent_repositories, validate_topology.EXPECTED_ADJACENT_REPOSITORIES)
        self.assertSetEqual(
            {item["id"] for item in ledger["pull_requests"]},
            validate_topology.EXPECTED_MANUAL_PULL_REQUEST_IDS,
        )

    def test_every_repository_has_full_boundary_facts(self):
        inventory = self.load(INVENTORY)
        required = {
            "repository",
            "visibility",
            "scope",
            "primary_class",
            "lifecycle",
            "owner",
            "canonical_responsibility",
            "consumers_and_dependencies",
            "extraction_or_retirement_rule",
            "deployment_security_boundary",
            "evidence_anchors",
        }
        for repository in inventory["repositories"]:
            self.assertTrue(required.issubset(repository), repository["repository"])
            self.assertIn(repository["owner"]["state"], {"open", "identified"})
            self.assertTrue(repository["evidence_anchors"], repository["repository"])

    def test_manual_pr_dispositions_and_successors_are_sound(self):
        ledger = self.load(LEDGER)
        allowed = {"merge", "revise", "hold", "supersede", "close"}
        for pull_request in ledger["pull_requests"]:
            self.assertIn(pull_request["decision"], allowed)
            self.assertRegex(pull_request["id"], r"^[^/]+/[^#]+#[1-9][0-9]*$")
            if pull_request["decision"] == "supersede":
                self.assertTrue(pull_request["successor"], pull_request["id"])

    def test_schema_and_validator_contracts_stay_in_parity(self):
        inventory_schema = self.load(INVENTORY_SCHEMA)
        ledger_schema = self.load(LEDGER_SCHEMA)
        repository_definition = inventory_schema["$defs"]["repository"]
        pull_request_definition = ledger_schema["$defs"]["pullRequest"]

        self.assertFalse(inventory_schema["additionalProperties"])
        self.assertFalse(ledger_schema["additionalProperties"])
        self.assertFalse(inventory_schema["properties"]["scope"]["additionalProperties"])
        self.assertFalse(ledger_schema["properties"]["scope"]["additionalProperties"])
        self.assertFalse(repository_definition["additionalProperties"])
        self.assertFalse(pull_request_definition["additionalProperties"])
        self.assertFalse(inventory_schema["$defs"]["owner"]["additionalProperties"])
        self.assertFalse(inventory_schema["$defs"]["evidenceAnchor"]["additionalProperties"])
        self.assertSetEqual(set(repository_definition["required"]), validate_topology.REQUIRED_REPOSITORY_FIELDS)
        self.assertSetEqual(set(pull_request_definition["required"]), validate_topology.REQUIRED_PULL_REQUEST_FIELDS)
        self.assertSetEqual(
            set(repository_definition["properties"]["lifecycle"]["enum"]),
            validate_topology.ALLOWED_LIFECYCLES,
        )
        self.assertSetEqual(
            set(repository_definition["properties"]["primary_class"]["enum"]),
            validate_topology.ALLOWED_CLASSES,
        )
        self.assertSetEqual(
            set(repository_definition["properties"]["visibility"]["enum"]),
            validate_topology.ALLOWED_VISIBILITIES,
        )
        self.assertSetEqual(
            set(inventory_schema["$defs"]["owner"]["properties"]["state"]["enum"]),
            validate_topology.ALLOWED_OWNER_STATES,
        )
        self.assertEqual(
            repository_definition["properties"]["repository"]["pattern"],
            validate_topology.REPOSITORY_PATTERN.pattern,
        )
        self.assertEqual(
            pull_request_definition["properties"]["id"]["pattern"],
            validate_topology.PULL_REQUEST_PATTERN.pattern,
        )
        self.assertSetEqual(
            set(pull_request_definition["properties"]["decision"]["enum"]),
            validate_topology.ALLOWED_DECISIONS,
        )
        self.assertSetEqual(
            set(repository_definition["properties"]["repository"]["enum"]),
            validate_topology.EXPECTED_ORGANIZATION_REPOSITORIES | validate_topology.EXPECTED_ADJACENT_REPOSITORIES,
        )
        self.assertSetEqual(
            set(pull_request_definition["properties"]["id"]["enum"]),
            validate_topology.EXPECTED_MANUAL_PULL_REQUEST_IDS,
        )
        self.assertSetEqual(
            {clause["contains"]["properties"]["repository"]["const"] for clause in inventory_schema["properties"]["repositories"]["allOf"]},
            validate_topology.EXPECTED_ORGANIZATION_REPOSITORIES | validate_topology.EXPECTED_ADJACENT_REPOSITORIES,
        )
        self.assertSetEqual(
            {clause["contains"]["properties"]["id"]["const"] for clause in ledger_schema["properties"]["pull_requests"]["allOf"]},
            validate_topology.EXPECTED_MANUAL_PULL_REQUEST_IDS,
        )

    def test_validator_accepts_complete_snapshot(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Topology validation passed", result.stdout)

    def test_validator_rejects_stale_identity_invalid_lifecycle_class_and_successor(self):
        inventory = self.load(INVENTORY)
        ledger = self.load(LEDGER)
        inventory["repositories"][0]["repository"] = "Quirk-Systems/demo-repository"
        inventory["repositories"][10]["primary_class"] = "kernel"
        ledger["pull_requests"][0]["decision"] = "supersede"
        ledger["pull_requests"][0]["successor"] = None

        with tempfile.TemporaryDirectory() as fixture_dir:
            bad_inventory = Path(fixture_dir) / "bad-inventory.json"
            bad_ledger = Path(fixture_dir) / "bad-ledger.json"
            bad_inventory.write_text(json.dumps(inventory), encoding="utf-8")
            bad_ledger.write_text(json.dumps(ledger), encoding="utf-8")
            result = self.validate(bad_inventory, bad_ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demo-repository", result.stderr)
        self.assertIn("reserved repository", result.stderr)
        self.assertIn("successor", result.stderr)

    def test_validator_rejects_invented_members_without_changing_counts(self):
        inventory = self.load(INVENTORY)
        ledger = self.load(LEDGER)
        inventory["repositories"][-1]["repository"] = "bryansayler/quirk-invented-store"
        ledger["pull_requests"][-1]["id"] = "Quirk-Systems/project-scaffold#499"
        ledger["pull_requests"][-1]["number"] = 499

        with tempfile.TemporaryDirectory() as fixture_dir:
            bad_inventory = Path(fixture_dir) / "bad-inventory.json"
            bad_ledger = Path(fixture_dir) / "bad-ledger.json"
            bad_inventory.write_text(json.dumps(inventory), encoding="utf-8")
            bad_ledger.write_text(json.dumps(ledger), encoding="utf-8")
            result = self.validate(bad_inventory, bad_ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected adjacent repository ids", result.stderr)
        self.assertIn("missing adjacent repository ids", result.stderr)
        self.assertIn("unexpected manual pull-request ids", result.stderr)
        self.assertIn("missing manual pull-request ids", result.stderr)

    def test_validator_rejects_empty_and_invalid_boundary_scalars(self):
        inventory = self.load(INVENTORY)
        ledger = self.load(LEDGER)
        candidate = inventory["repositories"][0]
        candidate["canonical_responsibility"] = ""
        candidate["extraction_or_retirement_rule"] = ""
        candidate["deployment_security_boundary"] = ""
        candidate["consumers_and_dependencies"] = ["", 42]
        candidate["visibility"] = "internal"
        ledger["pull_requests"][0]["number"] = True
        ledger["pull_requests"][0]["id"] = "Quirk-Systems/quirk-os#True"

        with tempfile.TemporaryDirectory() as fixture_dir:
            bad_inventory = Path(fixture_dir) / "bad-inventory.json"
            bad_ledger = Path(fixture_dir) / "bad-ledger.json"
            bad_inventory.write_text(json.dumps(inventory), encoding="utf-8")
            bad_ledger.write_text(json.dumps(ledger), encoding="utf-8")
            result = self.validate(bad_inventory, bad_ledger)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing repository description", result.stderr)
        self.assertIn("invalid consumer/dependency item", result.stderr)
        self.assertIn("invalid visibility", result.stderr)
        self.assertIn("invalid pull-request number", result.stderr)


if __name__ == "__main__":
    unittest.main()
