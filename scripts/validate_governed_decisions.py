"""Validate non-authoritative decisions bound to exact Git subjects and receipts."""

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DECISION_ID_PATTERN = re.compile(r"^qdecision\.[a-z0-9][a-z0-9._-]*$")
RECEIPT_ID_PATTERN = re.compile(r"^qreceipt\.[a-z0-9][a-z0-9._-]*$")
UTC_TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]+)?Z$"
)

CLASSIFICATIONS = {
    "NO_DELTA",
    "IMPLEMENTATION_DETAIL",
    "MATERIAL_SCOPE_CHANGE",
    "AUTHORITY_CHANGE",
    "BOUNDARY_ONLY",
    "INSUFFICIENT_EVIDENCE",
}
DISPOSITIONS = {"CONTINUE", "REVIEW", "REAUTHORIZE", "SPLIT", "HOLD", "REJECT"}
REQUIRED_NEXT_VALUES = {"merge", "canon", "runtime", "release", "deploy", "publish", "reauthorize"}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "decision_id",
    "repository",
    "subject",
    "evidence",
    "classification",
    "disposition",
    "reason",
    "limitations",
    "actor",
    "authority",
    "staleness",
    "decision_sha256",
}


class DecisionError(Exception):
    """A deterministic decision-contract failure safe to show to contributors."""


def _require_object(value, fields, label):
    if not isinstance(value, dict):
        raise DecisionError(label + " must be an object")
    missing = fields - set(value)
    extra = set(value) - fields
    if missing:
        raise DecisionError(label + " missing fields: " + ", ".join(sorted(missing)))
    if extra:
        raise DecisionError(label + " has unexpected fields: " + ", ".join(sorted(extra)))


def _require_non_empty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise DecisionError(label + " must be a non-empty string")


def _require_full_sha(value, label):
    if not isinstance(value, str) or not FULL_SHA_PATTERN.fullmatch(value):
        raise DecisionError(label + " must be a full 40-character lowercase commit SHA")


def _require_sha256(value, label):
    if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
        raise DecisionError(label + " must be a lowercase SHA-256 digest")


def _validate_path(path):
    if not isinstance(path, str) or not path:
        raise DecisionError("subject.changed_paths entries must be non-empty strings")
    if path.startswith("/") or "\\" in path or any(ord(character) < 32 or ord(character) == 127 for character in path):
        raise DecisionError("unsafe repository path: " + repr(path))
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise DecisionError("unsafe repository path: " + repr(path))


def canonical_decision_digest(decision):
    value = copy.deepcopy(decision)
    value.pop("decision_sha256", None)
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _validate_subject(subject):
    _require_object(subject, {"pull_request", "base_commit", "head_commit", "changed_paths"}, "subject")
    pull_request = subject["pull_request"]
    if pull_request is not None and (isinstance(pull_request, bool) or not isinstance(pull_request, int) or pull_request < 1):
        raise DecisionError("subject.pull_request must be null or a positive integer")
    _require_full_sha(subject["base_commit"], "subject.base_commit")
    _require_full_sha(subject["head_commit"], "subject.head_commit")
    paths = subject["changed_paths"]
    if not isinstance(paths, list):
        raise DecisionError("subject.changed_paths must be an array")
    for path in paths:
        _validate_path(path)
    if paths != sorted(set(paths)):
        raise DecisionError("subject.changed_paths must be sorted and unique")


def _validate_evidence(evidence, subject_head, classification):
    _require_object(evidence, {"receipts"}, "evidence")
    receipts = evidence["receipts"]
    if not isinstance(receipts, list):
        raise DecisionError("evidence.receipts must be an array")
    if classification != "INSUFFICIENT_EVIDENCE" and not receipts:
        raise DecisionError(classification + " requires at least one exact-head evidence receipt")
    receipt_ids = []
    receipt_digests = []
    for index, receipt in enumerate(receipts):
        label = "evidence.receipts[" + str(index) + "]"
        _require_object(receipt, {"receipt_id", "receipt_sha256", "covered_head_commit"}, label)
        receipt_id = receipt["receipt_id"]
        if not isinstance(receipt_id, str) or not RECEIPT_ID_PATTERN.fullmatch(receipt_id):
            raise DecisionError(label + ".receipt_id is invalid")
        _require_sha256(receipt["receipt_sha256"], label + ".receipt_sha256")
        _require_full_sha(receipt["covered_head_commit"], label + ".covered_head_commit")
        if receipt["covered_head_commit"] != subject_head:
            raise DecisionError(label + ".covered_head_commit must equal subject.head_commit")
        receipt_ids.append(receipt_id)
        receipt_digests.append(receipt["receipt_sha256"])
    if len(receipt_ids) != len(set(receipt_ids)):
        raise DecisionError("evidence receipt IDs must be unique")
    if len(receipt_digests) != len(set(receipt_digests)):
        raise DecisionError("evidence receipt digests must be unique")


def _validate_actor(actor):
    _require_object(actor, {"identity", "authority_ref", "decided_at"}, "actor")
    _require_non_empty(actor["identity"], "actor.identity")
    if actor["authority_ref"] is not None:
        _require_non_empty(actor["authority_ref"], "actor.authority_ref")
    decided_at = actor["decided_at"]
    if not isinstance(decided_at, str) or not UTC_TIMESTAMP_PATTERN.fullmatch(decided_at):
        raise DecisionError("actor.decided_at must be an RFC 3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(decided_at[:-1] + "+00:00")
    except ValueError as error:
        raise DecisionError("actor.decided_at must be a valid calendar timestamp") from error
    if parsed.tzinfo != timezone.utc:
        raise DecisionError("actor.decided_at must be UTC")


def _validate_authority(authority, disposition):
    _require_object(authority, {"effect", "required_next"}, "authority")
    if authority["effect"] != "none":
        raise DecisionError("authority.effect must be none")
    required_next = authority["required_next"]
    if not isinstance(required_next, list) or not all(isinstance(item, str) for item in required_next):
        raise DecisionError("authority.required_next must be an array of strings")
    if required_next != sorted(set(required_next)):
        raise DecisionError("authority.required_next must be sorted and unique")
    unknown = set(required_next) - REQUIRED_NEXT_VALUES
    if unknown:
        raise DecisionError("authority.required_next has unknown values: " + ", ".join(sorted(unknown)))
    if disposition == "REAUTHORIZE" and "reauthorize" not in required_next:
        raise DecisionError("REAUTHORIZE requires authority.required_next to include reauthorize")


def validate_decision(decision, repository=None, current_head=None):
    _require_object(decision, TOP_LEVEL_FIELDS, "decision")
    if decision["schema_version"] != "governed-decision.v1":
        raise DecisionError("schema_version must be governed-decision.v1")
    if not isinstance(decision["decision_id"], str) or not DECISION_ID_PATTERN.fullmatch(decision["decision_id"]):
        raise DecisionError("decision_id is invalid")
    if not isinstance(decision["repository"], str) or not REPOSITORY_PATTERN.fullmatch(decision["repository"]):
        raise DecisionError("repository must use owner/name form")
    if repository is not None and decision["repository"] != repository:
        raise DecisionError("decision repository must match --repository")

    _require_sha256(decision["decision_sha256"], "decision_sha256")
    if decision["decision_sha256"] != canonical_decision_digest(decision):
        raise DecisionError("decision_sha256 does not match canonical decision JSON")

    classification = decision["classification"]
    disposition = decision["disposition"]
    if classification not in CLASSIFICATIONS:
        raise DecisionError("classification is invalid")
    if disposition not in DISPOSITIONS:
        raise DecisionError("disposition is invalid")
    if classification in {"MATERIAL_SCOPE_CHANGE", "AUTHORITY_CHANGE"} and disposition == "CONTINUE":
        raise DecisionError(classification + " cannot use disposition CONTINUE")
    if classification == "INSUFFICIENT_EVIDENCE" and disposition == "CONTINUE":
        raise DecisionError("INSUFFICIENT_EVIDENCE cannot use disposition CONTINUE")

    _validate_subject(decision["subject"])
    _validate_evidence(decision["evidence"], decision["subject"]["head_commit"], classification)
    _require_non_empty(decision["reason"], "reason")
    limitations = decision["limitations"]
    if not isinstance(limitations, list) or not all(isinstance(item, str) and item.strip() for item in limitations):
        raise DecisionError("limitations must be an array of non-empty strings")
    if limitations != sorted(set(limitations)):
        raise DecisionError("limitations must be sorted and unique")
    _validate_actor(decision["actor"])
    _validate_authority(decision["authority"], disposition)
    _require_object(decision["staleness"], {"stale_if_head_changes"}, "staleness")
    if decision["staleness"]["stale_if_head_changes"] is not True:
        raise DecisionError("staleness.stale_if_head_changes must be true")

    if current_head is not None:
        _require_full_sha(current_head, "current head")
        if current_head != decision["subject"]["head_commit"]:
            raise DecisionError("decision is stale for current head")
    return decision["decision_id"]


def discover_decisions(root, decisions):
    root = Path(root).resolve()
    path = Path(decisions)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise DecisionError("decision directory must be inside repository root") from error
    if not path.exists():
        return []
    if not path.is_dir():
        raise DecisionError("decision path must be a directory")
    return sorted(candidate for candidate in path.rglob("*.json") if candidate.is_file())


def validate_directory(repository, root, decisions, current_head=None):
    paths = discover_decisions(root, decisions)
    ids = set()
    for path in paths:
        try:
            decision = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise DecisionError(path.as_posix() + ": invalid JSON: " + str(error)) from error
        try:
            decision_id = validate_decision(decision, repository=repository, current_head=current_head)
        except DecisionError as error:
            raise DecisionError(path.as_posix() + ": " + str(error)) from error
        if decision_id in ids:
            raise DecisionError("duplicate decision ID: " + decision_id)
        ids.add(decision_id)
    return len(paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--decisions", default=".quirk/decisions")
    parser.add_argument("--current-head")
    args = parser.parse_args(argv)
    try:
        count = validate_directory(
            args.repository,
            args.root,
            args.decisions,
            current_head=args.current_head,
        )
    except DecisionError as error:
        parser.error(str(error))
    noun = "decision" if count == 1 else "decisions"
    print("Governed decision validation passed: " + str(count) + " " + noun)
    return 0


if __name__ == "__main__":
    sys.exit(main())
