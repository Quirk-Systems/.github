"""Validate the fixed 2026-08-21 repository and manual-PR topology snapshot."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse


REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PULL_REQUEST_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$")
EXPECTED_ORGANIZATION_REPOSITORIES = {
    "Quirk-Systems/.github", "Quirk-Systems/.github-private", "Quirk-Systems/project-scaffold",
    "Quirk-Systems/quirk-os", "Quirk-Systems/quirk-core", "Quirk-Systems/quirk-feed",
    "Quirk-Systems/quirk-generator", "Quirk-Systems/quirk-beauty", "Quirk-Systems/quirk-pet",
    "Quirk-Systems/quirk-town", "Quirk-Systems/Quirk", "Quirk-Systems/quirk-data",
    "Quirk-Systems/quirk-me", "Quirk-Systems/quirk-run", "Quirk-Systems/quirk-dog",
    "Quirk-Systems/quirk-music", "Quirk-Systems/quirk-preference",
}
EXPECTED_ADJACENT_REPOSITORIES = {"bryansayler/quirk-commerce", "bryansayler/quirk-beauty-store"}
EXPECTED_MANUAL_PULL_REQUEST_IDS = {
    "Quirk-Systems/quirk-os#24", "Quirk-Systems/quirk-os#23", "Quirk-Systems/project-scaffold#84",
    "Quirk-Systems/quirk-os#41", "Quirk-Systems/quirk-os#36", "Quirk-Systems/quirk-os#39",
    "Quirk-Systems/quirk-os#37", "Quirk-Systems/quirk-os#35", "Quirk-Systems/quirk-os#38",
    "Quirk-Systems/quirk-os#40", "Quirk-Systems/quirk-os#25", "Quirk-Systems/quirk-os#21",
    "Quirk-Systems/quirk-os#17", "Quirk-Systems/quirk-os#22", "Quirk-Systems/quirk-os#18",
    "Quirk-Systems/quirk-os#15", "Quirk-Systems/quirk-os#20", "Quirk-Systems/quirk-os#19",
    "Quirk-Systems/quirk-core#1", "Quirk-Systems/.github#6", "Quirk-Systems/project-scaffold#66",
    "Quirk-Systems/project-scaffold#67", "Quirk-Systems/project-scaffold#62", "Quirk-Systems/project-scaffold#60",
    "Quirk-Systems/project-scaffold#55", "Quirk-Systems/.github#2", "Quirk-Systems/project-scaffold#49",
    "Quirk-Systems/quirk-os#44", "Quirk-Systems/quirk-core#2", "Quirk-Systems/project-scaffold#95",
}
REQUIRED_REPOSITORY_FIELDS = {
    "repository", "scope", "visibility", "primary_class", "lifecycle", "owner",
    "canonical_responsibility", "consumers_and_dependencies", "extraction_or_retirement_rule",
    "deployment_security_boundary", "evidence_anchors",
}
REQUIRED_PULL_REQUEST_FIELDS = {
    "id", "repository", "number", "title", "draft", "age_days", "check_state",
    "base", "head", "decision", "rationale", "successor",
}
ALLOWED_LIFECYCLES = {"active", "candidate", "reserved"}
ALLOWED_CLASSES = {"canon", "reference", "kernel", "doctrine", "interface", "instrument", "realm", "reservation", "commerce"}
ALLOWED_DECISIONS = {"merge", "revise", "hold", "supersede", "close"}
ALLOWED_VISIBILITIES = {"public", "private"}
ALLOWED_OWNER_STATES = {"open", "identified"}


def load(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def validate_object(value, required, allowed, label, errors):
    if not isinstance(value, dict):
        errors.append(label + " must be an object")
        return False
    missing = required - set(value)
    extra = set(value) - allowed
    if missing:
        errors.append(label + " missing fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append(label + " has unexpected fields: " + ", ".join(sorted(extra)))
    return not missing


def validate_expected_set(actual, expected, label, errors):
    missing = expected - actual
    unexpected = actual - expected
    if missing:
        errors.append("missing " + label + ": " + ", ".join(sorted(missing)))
    if unexpected:
        errors.append("unexpected " + label + ": " + ", ".join(sorted(unexpected)))


def validate(inventory, ledger):
    errors = []
    inventory_root_fields = {"registry_version", "authority", "snapshot", "scope", "repositories"}
    ledger_root_fields = {"ledger_version", "authority", "snapshot", "scope", "pull_requests"}
    validate_object(inventory, inventory_root_fields, inventory_root_fields, "inventory", errors)
    validate_object(ledger, ledger_root_fields, ledger_root_fields, "ledger", errors)
    if not isinstance(inventory, dict):
        inventory = {}
    if not isinstance(ledger, dict):
        ledger = {}
    repositories = inventory.get("repositories", [])
    pull_requests = ledger.get("pull_requests", [])
    scope = inventory.get("scope", {})
    ledger_scope = ledger.get("scope", {})

    if inventory.get("registry_version") != "0.3.0":
        errors.append("inventory registry_version must be 0.3.0")
    if ledger.get("ledger_version") != "0.1.0":
        errors.append("ledger ledger_version must be 0.1.0")
    if inventory.get("authority") != "Quirk-Systems/.github":
        errors.append("inventory authority must be Quirk-Systems/.github")
    if ledger.get("authority") != "Quirk-Systems/.github":
        errors.append("ledger authority must be Quirk-Systems/.github")
    if inventory.get("snapshot") != "2026-08-21" or ledger.get("snapshot") != "2026-08-21":
        errors.append("inventory and ledger snapshot must be 2026-08-21")

    scope_fields = {"organization", "expected_organization_repository_count", "expected_adjacent_repository_count", "adjacent_repository_selection_rule"}
    validate_object(scope, scope_fields, scope_fields, "inventory scope", errors)
    if not isinstance(scope, dict):
        scope = {}
    if scope.get("organization") != "Quirk-Systems":
        errors.append("inventory scope organization must be Quirk-Systems")
    if scope.get("expected_organization_repository_count") != 17:
        errors.append("expected organization repository count must be 17")
    if scope.get("expected_adjacent_repository_count") != 2:
        errors.append("expected adjacent repository count must be 2")
    if not non_empty_string(scope.get("adjacent_repository_selection_rule")):
        errors.append("adjacent repository selection rule must be non-empty")
    validate_object(ledger_scope, {"expected_open_non_dependabot_pull_request_count"}, {"expected_open_non_dependabot_pull_request_count"}, "ledger scope", errors)
    if not isinstance(ledger_scope, dict):
        ledger_scope = {}
    if ledger_scope.get("expected_open_non_dependabot_pull_request_count") != 30:
        errors.append("expected open non-Dependabot pull-request count must be 30")
    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []
    if not isinstance(pull_requests, list):
        errors.append("pull_requests must be an array")
        pull_requests = []
    if len(repositories) != 19:
        errors.append("inventory must contain exactly 19 in-scope repositories")
    if len(pull_requests) != 30:
        errors.append("ledger must contain exactly 30 open non-Dependabot pull requests")

    repository_ids = []
    organization_ids = set()
    adjacent_ids = set()
    for item in repositories:
        if not validate_object(item, REQUIRED_REPOSITORY_FIELDS, REQUIRED_REPOSITORY_FIELDS, "repository", errors):
            continue
        repository = item["repository"]
        repository_ids.append(repository)
        if not non_empty_string(repository) or not REPOSITORY_PATTERN.fullmatch(repository):
            errors.append("invalid repository id: " + str(repository))
        if repository == "Quirk-Systems/demo-repository":
            errors.append("demo-repository is stale and must not appear in the canonical inventory")
        if item["scope"] == "organization":
            organization_ids.add(repository)
            if not isinstance(repository, str) or not repository.startswith("Quirk-Systems/"):
                errors.append("organization repository must belong to Quirk-Systems: " + str(repository))
        elif item["scope"] == "adjacent":
            adjacent_ids.add(repository)
        else:
            errors.append("invalid repository scope: " + str(item["scope"]))
        if item["visibility"] not in ALLOWED_VISIBILITIES:
            errors.append("invalid visibility: " + str(repository))
        if item["lifecycle"] not in ALLOWED_LIFECYCLES:
            errors.append("invalid lifecycle for " + str(repository))
        if item["primary_class"] not in ALLOWED_CLASSES:
            errors.append("invalid primary class for " + str(repository))
        if item["lifecycle"] == "reserved" and item["primary_class"] != "reservation":
            errors.append("reserved repository must use reservation class: " + str(repository))
        for field in {"canonical_responsibility", "extraction_or_retirement_rule", "deployment_security_boundary"}:
            if not non_empty_string(item[field]):
                errors.append("missing repository description " + field + ": " + str(repository))
        owner = item["owner"]
        if validate_object(owner, {"state"}, {"state", "name"}, "owner", errors):
            if owner.get("state") not in ALLOWED_OWNER_STATES:
                errors.append("owner state must be open or identified: " + str(repository))
            if "name" in owner and not non_empty_string(owner["name"]):
                errors.append("owner name must be non-empty: " + str(repository))
            if owner.get("state") == "identified" and not non_empty_string(owner.get("name")):
                errors.append("identified owner requires name: " + str(repository))
        consumers = item["consumers_and_dependencies"]
        if not isinstance(consumers, list) or not consumers:
            errors.append("consumers/dependencies must be a non-empty list: " + str(repository))
        else:
            for consumer in consumers:
                if not non_empty_string(consumer):
                    errors.append("invalid consumer/dependency item: " + str(repository))
        anchors = item["evidence_anchors"]
        if not isinstance(anchors, list) or not anchors:
            errors.append("evidence anchors are required: " + str(repository))
        else:
            for anchor in anchors:
                if not validate_object(anchor, {"label", "url"}, {"label", "url"}, "evidence anchor", errors):
                    continue
                parsed = urlparse(anchor["url"]) if non_empty_string(anchor["url"]) else None
                if not non_empty_string(anchor["label"]) or not parsed or parsed.scheme != "https" or not parsed.netloc:
                    errors.append("invalid evidence anchor: " + str(repository))
    if len(set(repository_ids)) != len(repository_ids):
        errors.append("repository ids must be unique")
    validate_expected_set(organization_ids, EXPECTED_ORGANIZATION_REPOSITORIES, "organization repository ids", errors)
    validate_expected_set(adjacent_ids, EXPECTED_ADJACENT_REPOSITORIES, "adjacent repository ids", errors)

    pull_request_ids = []
    known_repositories = EXPECTED_ORGANIZATION_REPOSITORIES | EXPECTED_ADJACENT_REPOSITORIES
    for item in pull_requests:
        if not validate_object(item, REQUIRED_PULL_REQUEST_FIELDS, REQUIRED_PULL_REQUEST_FIELDS, "pull request", errors):
            continue
        pull_request_id = item["id"]
        pull_request_ids.append(pull_request_id)
        if not non_empty_string(pull_request_id) or not PULL_REQUEST_PATTERN.fullmatch(pull_request_id):
            errors.append("invalid pull-request id: " + str(pull_request_id))
        if item["repository"] not in known_repositories:
            errors.append("pull request repository absent from inventory: " + str(item["repository"]))
        number = item["number"]
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            errors.append("invalid pull-request number: " + str(pull_request_id))
        if pull_request_id != str(item["repository"]) + "#" + str(number):
            errors.append("pull-request id does not match repository and number: " + str(pull_request_id))
        if item["decision"] not in ALLOWED_DECISIONS:
            errors.append("invalid pull-request decision: " + str(pull_request_id))
        successor = item["successor"]
        if item["decision"] == "supersede" and not non_empty_string(successor):
            errors.append("supersede decision requires successor: " + str(pull_request_id))
        if successor is not None and not non_empty_string(successor):
            errors.append("successor must be a non-empty string or null: " + str(pull_request_id))
        if not isinstance(item["draft"], bool):
            errors.append("draft must be boolean: " + str(pull_request_id))
        if isinstance(item["age_days"], bool) or not isinstance(item["age_days"], int) or item["age_days"] < 0:
            errors.append("age_days must be a non-negative integer: " + str(pull_request_id))
        for field in {"title", "check_state", "base", "head", "rationale"}:
            if not non_empty_string(item[field]):
                errors.append("missing pull-request evidence field " + field + ": " + str(pull_request_id))
    if len(set(pull_request_ids)) != len(pull_request_ids):
        errors.append("pull-request ids must be unique")
    validate_expected_set(set(pull_request_ids), EXPECTED_MANUAL_PULL_REQUEST_IDS, "manual pull-request ids", errors)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--pull-requests", required=True)
    args = parser.parse_args()
    errors = validate(load(args.inventory), load(args.pull_requests))
    if errors:
        parser.error("; ".join(errors))
    print("Topology validation passed: 19 repositories and 30 manual pull requests")


if __name__ == "__main__":
    main()
