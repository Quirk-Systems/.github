#!/usr/bin/env python3
"""Validate the truthful topology inventory used for the portfolio projection.

Standard library only. Applies the loaded inventory schema, then checks the
cross-entry invariants needed by docs/PORTFOLIO.md.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "repository-inventory.schema.json"
REGISTRY = ROOT / ".quirk" / "repositories.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_manifest import ManifestError, _check  # noqa: E402
import validate_topology  # noqa: E402


class PortfolioError(ValueError):
    pass


def validate_portfolio(data, schema):
    try:
        _check(data, schema, "portfolio")
    except ManifestError as error:
        raise PortfolioError(str(error)) from error

    if not isinstance(data, dict):
        raise PortfolioError("portfolio must be an object")

    errors = []
    root_fields = {"registry_version", "authority", "snapshot", "scope", "repositories"}
    validate_topology.validate_object(data, root_fields, root_fields, "portfolio", errors)

    repositories = data.get("repositories", [])
    scope = data.get("scope", {})
    if not isinstance(scope, dict):
        scope = {}
    scope_fields = {
        "organization",
        "expected_organization_repository_count",
        "expected_adjacent_repository_count",
        "adjacent_repository_selection_rule",
    }
    validate_topology.validate_object(scope, scope_fields, scope_fields, "portfolio scope", errors)

    if not isinstance(repositories, list):
        errors.append("repositories must be an array")
        repositories = []

    repository_ids = []
    organization = set()
    adjacent = set()
    organization_entries = 0
    adjacent_entries = 0
    for item in repositories:
        if not validate_topology.validate_object(
            item,
            validate_topology.REQUIRED_REPOSITORY_FIELDS,
            validate_topology.REQUIRED_REPOSITORY_FIELDS,
            "repository",
            errors,
        ):
            continue
        repository = item["repository"]
        repository_ids.append(repository)
        if item["scope"] == "organization":
            organization.add(repository)
            organization_entries += 1
        elif item["scope"] == "adjacent":
            adjacent.add(repository)
            adjacent_entries += 1
        else:
            errors.append("invalid repository scope: " + str(item["scope"]))

    if len(repository_ids) != len(set(repository_ids)):
        errors.append("repositories must be unique")
    validate_topology.validate_expected_set(
        organization,
        validate_topology.EXPECTED_ORGANIZATION_REPOSITORIES,
        "organization repositories",
        errors,
    )
    validate_topology.validate_expected_set(
        adjacent,
        validate_topology.EXPECTED_ADJACENT_REPOSITORIES,
        "adjacent repositories",
        errors,
    )
    expected_organization_count = scope.get("expected_organization_repository_count")
    expected_adjacent_count = scope.get("expected_adjacent_repository_count")
    if len(organization) != expected_organization_count:
        errors.append(
            f"organization repository count does not match scope: expected {expected_organization_count}, got {len(organization)}"
        )
    if len(adjacent) != expected_adjacent_count:
        errors.append(
            f"adjacent repository count does not match scope: expected {expected_adjacent_count}, got {len(adjacent)}"
        )
    if organization_entries != expected_organization_count:
        errors.append(
            f"organization repository entry count does not match scope: expected {expected_organization_count}, got {organization_entries}"
        )
    if adjacent_entries != expected_adjacent_count:
        errors.append(
            f"adjacent repository entry count does not match scope: expected {expected_adjacent_count}, got {adjacent_entries}"
        )

    if errors:
        raise PortfolioError("; ".join(errors))
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    args = parser.parse_args(argv)
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        data = json.loads(args.registry.read_text(encoding="utf-8"))
        validate_portfolio(data, schema)
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"Portfolio OK: {len(data['repositories'])} inventory repositories "
        f"({data['scope']['expected_organization_repository_count']} organization, "
        f"{data['scope']['expected_adjacent_repository_count']} adjacent)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
