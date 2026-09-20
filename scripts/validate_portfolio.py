#!/usr/bin/env python3
"""Validate the portfolio registry (.quirk/repositories.json).

Standard library only. Applies .quirk/schemas/portfolio-registry.schema.json
through the same subset validator used for manifests, then checks the
cross-entry rules: unique repositories, the two canon repositories present,
no observed-unclassified entry that is also a classified entry, and no
observed entry claiming anything beyond observation. Passing proves the file
is well-formed and internally consistent; it does not prove any
classification is correct or that the observation is current.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / ".quirk" / "schemas" / "portfolio-registry.schema.json"
REGISTRY = ROOT / ".quirk" / "repositories.json"
REQUIRED_REPOSITORIES = ("Quirk-Systems/.github", "Quirk-Systems/.github-private")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_manifest import ManifestError, _check  # noqa: E402


class PortfolioError(ValueError):
    pass


def validate_portfolio(data, schema):
    try:
        _check(data, schema, "portfolio")
    except ManifestError as error:
        raise PortfolioError(str(error)) from error
    names = [entry["repository"] for entry in data["repositories"]]
    if len(names) != len(set(names)):
        raise PortfolioError("repositories must be unique")
    for required in REQUIRED_REPOSITORIES:
        if required not in names:
            raise PortfolioError(f"{required} must be registered")
    observed = data.get("observed_unclassified", [])
    observed_names = [entry["repository"] for entry in observed]
    if len(observed_names) != len(set(observed_names)):
        raise PortfolioError("observed_unclassified repositories must be unique")
    overlap = sorted(set(observed_names) & set(names))
    if overlap:
        raise PortfolioError(f"observed_unclassified entries duplicate classified entries: {overlap}")
    if observed_names != sorted(observed_names, key=str.casefold):
        raise PortfolioError("observed_unclassified must be sorted by repository name")
    observation = data.get("observation")
    if observed and not observation:
        raise PortfolioError("observed_unclassified requires an observation record")
    if observation:
        for name in observation["registered_not_observed"]:
            if name not in names:
                raise PortfolioError(f"registered_not_observed names an unregistered repository: {name}")
        expected_total = len(names) - len(observation["registered_not_observed"]) + len(observed_names)
        if observation["total_observed"] != expected_total:
            raise PortfolioError(
                f"observation.total_observed is {observation['total_observed']} but registered-observed plus "
                f"observed-unclassified is {expected_total}"
            )
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
        f"Portfolio OK: {len(data['repositories'])} classified, "
        f"{len(data.get('observed_unclassified', []))} observed-unclassified"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
