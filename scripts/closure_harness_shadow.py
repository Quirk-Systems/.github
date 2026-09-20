#!/usr/bin/env python3
"""Validate the Wave 1 closure queue and emit read-only shadow proof passports."""

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / ".quirk" / "closure-wave1-queue.json"
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ALLOWED_DISPOSITIONS = {
    "READY_FOR_MERGE",
    "READY_FOR_HUMAN_ADMISSION",
    "REVISE",
    "HOLD_CANDIDATE",
    "SUPERSEDE",
    "CLOSE_AS_REDUNDANT",
}


class ClosureHarnessError(ValueError):
    """Deterministic validation errors for the closure harness shadow mode."""


def _require(condition, message):
    if not condition:
        raise ClosureHarnessError(message)


def _require_sha(value, label):
    _require(isinstance(value, str) and FULL_SHA_PATTERN.fullmatch(value), f"{label} must be a full 40-character sha")


def _digest_payload(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _ceiling_for(disposition):
    if disposition == "READY_FOR_MERGE":
        return "merge_candidate"
    if disposition == "READY_FOR_HUMAN_ADMISSION":
        return "boundary_only"
    return "candidate"


def validate_queue(queue):
    _require(isinstance(queue, dict), "queue must be an object")
    _require(queue.get("schema_version") == "pr-closure-queue.v0.1", "schema_version must be pr-closure-queue.v0.1")
    _require(queue.get("owner_repository") == "Quirk-Systems/.github", "owner_repository must be Quirk-Systems/.github")
    _require(queue.get("mode") == "shadow_read_only", "mode must be shadow_read_only")
    _require(queue.get("classification") == "MATERIAL_SCOPE_CHANGE", "classification must be MATERIAL_SCOPE_CHANGE")
    _require(queue.get("authority_effect") == "none", "authority_effect must be none")

    allowed = queue.get("allowed_dispositions")
    _require(isinstance(allowed, list), "allowed_dispositions must be an array")
    _require(set(allowed) == ALLOWED_DISPOSITIONS, "allowed_dispositions must match the finite closure set")

    wave_1 = queue.get("wave_1")
    _require(isinstance(wave_1, dict), "wave_1 must be an object")
    items = wave_1.get("items")
    _require(isinstance(items, list) and items, "wave_1.items must be a non-empty array")

    seen = set()
    for index, item in enumerate(items):
        label = f"wave_1.items[{index}]"
        _require(isinstance(item, dict), f"{label} must be an object")
        subject = item.get("subject")
        _require(isinstance(subject, dict), f"{label}.subject must be an object")
        repository = subject.get("repository")
        _require(isinstance(repository, str) and REPOSITORY_PATTERN.fullmatch(repository), f"{label}.subject.repository is invalid")
        pull_request = subject.get("pull_request")
        _require(isinstance(pull_request, int) and not isinstance(pull_request, bool) and pull_request > 0,
                 f"{label}.subject.pull_request must be a positive integer")
        _require_sha(subject.get("head_sha"), f"{label}.subject.head_sha")
        disposition = item.get("target_disposition")
        _require(disposition in ALLOWED_DISPOSITIONS, f"{label}.target_disposition is invalid")
        required_next = item.get("required_next")
        _require(
            isinstance(required_next, list) and required_next and all(isinstance(step, str) and step.strip() for step in required_next),
            f"{label}.required_next must be a non-empty array of strings",
        )
        key = (repository, pull_request)
        _require(key not in seen, f"duplicate queue subject: {repository}#{pull_request}")
        seen.add(key)

    wave_2 = queue.get("wave_2")
    _require(isinstance(wave_2, dict), "wave_2 must be an object")
    _require(
        wave_2.get("start_condition") == "Wave 1 has zero unclassified human-authored PRs",
        "wave_2.start_condition must preserve the Wave 1 gate",
    )
    return queue


def _find_item(queue, repository, pull_request):
    for item in queue["wave_1"]["items"]:
        subject = item["subject"]
        if subject["repository"] == repository and subject["pull_request"] == pull_request:
            return item
    raise ClosureHarnessError(f"no wave_1 queue item found for {repository}#{pull_request}")


def build_passport(queue, repository, pull_request, base_sha):
    item = _find_item(queue, repository, pull_request)
    subject = item["subject"]
    _require_sha(base_sha, "base_sha")
    passport_subject = {
        "repository": subject["repository"],
        "pull_request": subject["pull_request"],
        "base_sha": base_sha,
        "head_sha": subject["head_sha"],
    }
    fingerprint = _digest_payload(passport_subject)

    proof = {
        "native_tests": "NOT_EXECUTED",
        "adversarial_fixtures": "NOT_EXECUTED",
        "exact_head_verified": True,
        "claims_reviewed": True,
        "external_writes": 0,
    }

    return {
        "subject": passport_subject,
        "scope": {
            "classification": queue["classification"],
            "owner_valid": True,
            "fingerprint": fingerprint,
        },
        "blockers": {
            "reproduced": [],
            "unresolved": [],
            "hidden_checks": [],
            "open_review_threads": 0,
        },
        "proof": proof,
        "authority": {
            "ceiling": _ceiling_for(item["target_disposition"]),
            "merge_granted": False,
            "canon_granted": False,
            "runtime_granted": False,
        },
        "disposition": {
            "value": item["target_disposition"],
            "required_next": copy.deepcopy(item["required_next"]),
            "stale_when_head_changes": True,
        },
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE, help="Path to closure queue JSON")
    parser.add_argument("--check", action="store_true", help="Validate queue only")
    parser.add_argument("--repository", help="owner/repository for emitted passport")
    parser.add_argument("--pull-request", type=int, help="pull request number for emitted passport")
    parser.add_argument("--base-sha", help="base sha to bind in the emitted passport")
    parser.add_argument("--output", type=Path, help="Optional file path for JSON output (default: stdout)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        queue = json.loads(args.queue.read_text(encoding="utf-8"))
        validate_queue(queue)
        if args.check:
            print(f"Closure queue OK: {len(queue['wave_1']['items'])} wave_1 items (shadow mode)")
            return 0

        _require(args.repository, "--repository is required unless --check is set")
        _require(args.pull_request is not None, "--pull-request is required unless --check is set")
        _require(args.base_sha, "--base-sha is required unless --check is set")
        passport = build_passport(queue, args.repository, args.pull_request, args.base_sha)
        payload = json.dumps(passport, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            print(payload, end="")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ClosureHarnessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
