"""Validate evidence receipts against immutable objects in a local Git repository."""

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RECEIPT_ID_PATTERN = re.compile(r"^qreceipt\.[a-z0-9][a-z0-9._-]*$")
CLAIM_ID_PATTERN = re.compile(r"^qclaim\.[a-z0-9][a-z0-9._-]*$")
UTC_TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]+)?Z$"
)
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
EXTERNAL_REF_PATTERN = re.compile(r"^(?:https://[^\s]+|[A-Za-z][A-Za-z0-9._:/#-]+)$")
CLAIM_TYPES = {"implementation", "test", "documentation", "governance", "evidence", "correction"}

TOP_LEVEL_FIELDS = {
    "schema_version", "receipt_id", "repository", "status", "subject", "claims",
    "artifacts", "verification", "authority", "correction", "receipt_sha256",
}


class ReceiptError(Exception):
    """A validation failure safe to show to a repository contributor."""


def _git(root, *args, text=True, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=text,
        shell=False,
    )
    if check and result.returncode:
        stderr = result.stderr.strip() if text else result.stderr.decode("utf-8", "replace").strip()
        raise ReceiptError("git " + " ".join(args) + " failed: " + stderr)
    return result


def _require_object(value, fields, label):
    if not isinstance(value, dict):
        raise ReceiptError(label + " must be an object")
    missing = fields - set(value)
    extra = set(value) - fields
    if missing:
        raise ReceiptError(label + " missing fields: " + ", ".join(sorted(missing)))
    if extra:
        raise ReceiptError(label + " has unexpected fields: " + ", ".join(sorted(extra)))


def _require_non_empty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ReceiptError(label + " must be a non-empty string")


def validate_repository_path(path):
    if not isinstance(path, str) or not path:
        raise ReceiptError("repository path must be a non-empty string")
    if path.startswith("/") or "\\" in path or any(ord(character) < 32 or ord(character) == 127 for character in path):
        raise ReceiptError("unsafe repository path: " + repr(path))
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ReceiptError("unsafe repository path: " + repr(path))
    return path


def canonical_receipt_digest(receipt):
    value = copy.deepcopy(receipt)
    value.pop("receipt_sha256", None)
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def require_commit(root, commit, label):
    if not isinstance(commit, str) or not FULL_SHA_PATTERN.fullmatch(commit):
        raise ReceiptError(label + " must be a full 40-character lowercase commit SHA")
    result = _git(root, "cat-file", "-t", commit, check=False)
    if result.returncode or result.stdout.strip() != "commit":
        raise ReceiptError(label + " does not resolve to a commit: " + commit)


def is_ancestor(root, ancestor, descendant):
    result = _git(root, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    if result.returncode not in {0, 1}:
        raise ReceiptError("could not evaluate Git ancestry")
    return result.returncode == 0


def derive_diff(root, base, commit):
    require_commit(root, base, "base commit")
    require_commit(root, commit, "subject commit")
    if not is_ancestor(root, base, commit):
        raise ReceiptError("base commit must be an ancestor of subject commit")
    output = _git(
        root,
        "diff",
        "--name-status",
        "-z",
        "--no-renames",
        base + ".." + commit,
        text=False,
    ).stdout
    return parse_name_status(output)


def parse_name_status(output):
    if not isinstance(output, bytes):
        raise ReceiptError("Git diff output must be bytes")
    if output and not output.endswith(b"\0"):
        raise ReceiptError("Git diff emitted a malformed NUL-delimited record")
    fields = output.split(b"\0")[:-1] if output else []
    if len(fields) % 2:
        raise ReceiptError("Git diff emitted an incomplete status/path pair")
    entries = []
    for index in range(0, len(fields), 2):
        try:
            status = fields[index].decode("ascii", "strict")
            path = fields[index + 1].decode("utf-8", "strict")
        except UnicodeDecodeError as error:
            raise ReceiptError("Git diff emitted a path that is not strict UTF-8") from error
        validate_repository_path(path)
        if status.startswith("D"):
            state = "deleted"
        elif status[:1] in {"A", "M", "T", "U"}:
            state = "present"
        else:
            raise ReceiptError("unsupported Git diff status " + status + " for " + path)
        entries.append((path, state))
    entries.sort(key=lambda item: item[0])
    if len({path for path, _ in entries}) != len(entries):
        raise ReceiptError("Git diff contains duplicate paths")
    return entries


def artifact_for_path(root, commit, path, state):
    if state == "deleted":
        probe = _git(root, "cat-file", "-e", commit + ":" + path, check=False)
        if probe.returncode == 0:
            raise ReceiptError("deleted artifact still exists at subject commit: " + path)
        return {"path": path, "state": "deleted", "git_blob": None, "sha256": None}
    blob = _git(root, "rev-parse", commit + ":" + path).stdout.strip()
    if not FULL_SHA_PATTERN.fullmatch(blob):
        raise ReceiptError("artifact does not resolve to a Git blob: " + path)
    object_type = _git(root, "cat-file", "-t", blob).stdout.strip()
    if object_type != "blob":
        raise ReceiptError("artifact is not a Git blob: " + path)
    content = _git(root, "show", commit + ":" + path, text=False).stdout
    return {
        "path": path,
        "state": "present",
        "git_blob": blob,
        "sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
    }


def _validate_subject(receipt, root, head):
    subject = receipt["subject"]
    _require_object(subject, {"base_commit", "commit", "changed_paths"}, "subject")
    base = subject["base_commit"]
    commit = subject["commit"]
    entries = derive_diff(root, base, commit)
    if not is_ancestor(root, commit, head):
        raise ReceiptError("subject commit must be an ancestor of checked-out HEAD")
    changed_paths = subject["changed_paths"]
    if not isinstance(changed_paths, list) or not all(isinstance(path, str) for path in changed_paths):
        raise ReceiptError("subject.changed_paths must be an array of paths")
    for path in changed_paths:
        validate_repository_path(path)
    if changed_paths != sorted(set(changed_paths)):
        raise ReceiptError("subject.changed_paths must be sorted and unique")
    derived_paths = [path for path, _ in entries]
    if changed_paths != derived_paths:
        raise ReceiptError("subject.changed_paths must exactly equal the subject diff: expected " + repr(derived_paths))
    return entries


def _validate_claims(receipt, changed_paths):
    claims = receipt["claims"]
    if not isinstance(claims, list) or not claims:
        raise ReceiptError("claims must be a non-empty array")
    ids = []
    for index, claim in enumerate(claims):
        label = "claims[" + str(index) + "]"
        _require_object(
            claim,
            {"claim_id", "claim_type", "authority_effect", "statement", "evidence_paths"},
            label,
        )
        if not isinstance(claim["claim_id"], str) or not CLAIM_ID_PATTERN.fullmatch(claim["claim_id"]):
            raise ReceiptError(label + ".claim_id is invalid")
        ids.append(claim["claim_id"])
        if claim["claim_type"] not in CLAIM_TYPES:
            raise ReceiptError(label + ".claim_type must be a bounded non-authority type")
        if claim["authority_effect"] != "none":
            raise ReceiptError(label + ".authority_effect must be none")
        _require_non_empty(claim["statement"], label + ".statement")
        evidence_paths = claim["evidence_paths"]
        if not isinstance(evidence_paths, list) or not all(isinstance(path, str) for path in evidence_paths):
            raise ReceiptError(label + ".evidence_paths must be an array of paths")
        for path in evidence_paths:
            validate_repository_path(path)
        if evidence_paths != sorted(set(evidence_paths)):
            raise ReceiptError(label + ".evidence_paths must be sorted and unique")
        if not set(evidence_paths).issubset(changed_paths):
            raise ReceiptError(label + ".evidence_paths must be within the subject diff")
        if receipt["status"] == "verified" and not evidence_paths:
            raise ReceiptError("verified claims require at least one evidence path")
    if len(ids) != len(set(ids)):
        raise ReceiptError("claim IDs must be unique")
    return ids


def _validate_artifacts(receipt, entries, root):
    artifacts = receipt["artifacts"]
    if not isinstance(artifacts, list):
        raise ReceiptError("artifacts must be an array")
    changed_paths = [path for path, _ in entries]
    if len(artifacts) != len(changed_paths):
        raise ReceiptError("artifact count must equal subject path count")
    artifact_paths = []
    for index, (artifact, (path, state)) in enumerate(zip(artifacts, entries)):
        label = "artifacts[" + str(index) + "]"
        _require_object(artifact, {"path", "state", "git_blob", "sha256"}, label)
        validate_repository_path(artifact["path"])
        artifact_paths.append(artifact["path"])
        if artifact["path"] != path or artifact["state"] != state:
            raise ReceiptError("artifacts must have the same path order and state as the subject diff")
        expected = artifact_for_path(root, receipt["subject"]["commit"], path, state)
        if artifact != expected:
            raise ReceiptError("artifact Git blob or SHA-256 does not match subject bytes: " + path)
    if artifact_paths != changed_paths:
        raise ReceiptError("artifact path order must equal subject path order")


def _validate_verification(receipt):
    verification = receipt["verification"]
    _require_object(verification, {"commands", "verified_at"}, "verification")
    if not isinstance(verification["verified_at"], str) or not UTC_TIMESTAMP_PATTERN.fullmatch(verification["verified_at"]):
        raise ReceiptError("verification.verified_at must be an RFC 3339 UTC timestamp")
    try:
        parsed_time = datetime.fromisoformat(verification["verified_at"][:-1] + "+00:00")
    except ValueError as error:
        raise ReceiptError("verification.verified_at must be a valid calendar timestamp") from error
    if parsed_time.tzinfo != timezone.utc:
        raise ReceiptError("verification.verified_at must be UTC")
    commands = verification["commands"]
    if not isinstance(commands, list):
        raise ReceiptError("verification.commands must be an array")
    if receipt["status"] == "verified" and not commands:
        raise ReceiptError("verified receipts require at least one verification command")
    for index, command in enumerate(commands):
        label = "verification.commands[" + str(index) + "]"
        _require_object(command, {"command", "result", "exit_code"}, label)
        _require_non_empty(command["command"], label + ".command")
        if command["result"] not in {"pass", "fail"}:
            raise ReceiptError(label + ".result must be pass or fail")
        if isinstance(command["exit_code"], bool) or not isinstance(command["exit_code"], int):
            raise ReceiptError(label + ".exit_code must be an integer")
        if (command["result"] == "pass") != (command["exit_code"] == 0):
            raise ReceiptError(label + " must record pass iff exit code is 0")
        if receipt["status"] == "verified" and (command["result"] != "pass" or command["exit_code"] != 0):
            raise ReceiptError("verified receipt commands must record pass with exit code 0")


def _validate_authority_and_correction(receipt):
    authority = receipt["authority"]
    _require_object(authority, {"admission_effect", "authority_ref"}, "authority")
    if authority["admission_effect"] != "none":
        raise ReceiptError("authority.admission_effect must be none")
    if authority["authority_ref"] is not None:
        _require_non_empty(authority["authority_ref"], "authority.authority_ref")
    correction = receipt["correction"]
    if receipt["status"] == "verified":
        if correction is not None:
            raise ReceiptError("verified receipts require correction to be null")
        return
    _require_object(correction, {"reason", "external_claim_refs", "observations"}, "correction")
    _require_non_empty(correction["reason"], "correction.reason")
    refs = correction["external_claim_refs"]
    if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and EXTERNAL_REF_PATTERN.fullmatch(ref) for ref in refs):
        raise ReceiptError("correction.external_claim_refs requires HTTPS URLs or stable claim IDs")
    if len(refs) != len(set(refs)):
        raise ReceiptError("correction.external_claim_refs must be unique")
    observations = correction["observations"]
    if not isinstance(observations, list) or not observations:
        raise ReceiptError("correction.observations must be a non-empty array")
    for observation in observations:
        _require_non_empty(observation, "correction observation")


def validate_receipt(receipt, repository, root, head=None):
    _require_object(receipt, TOP_LEVEL_FIELDS, "receipt")
    if receipt["schema_version"] != "evidence-receipt.v1":
        raise ReceiptError("schema_version must be evidence-receipt.v1")
    if not isinstance(receipt["receipt_id"], str) or not RECEIPT_ID_PATTERN.fullmatch(receipt["receipt_id"]):
        raise ReceiptError("receipt_id is invalid")
    if receipt["repository"] != repository or not REPOSITORY_PATTERN.fullmatch(str(receipt["repository"])):
        raise ReceiptError("receipt repository must match --repository")
    if receipt["status"] not in {"verified", "unverified", "retracted"}:
        raise ReceiptError("status must be verified, unverified, or retracted")
    if not isinstance(receipt["receipt_sha256"], str) or not SHA256_PATTERN.fullmatch(receipt["receipt_sha256"]):
        raise ReceiptError("receipt_sha256 must be a lowercase SHA-256 digest")
    expected_digest = canonical_receipt_digest(receipt)
    if receipt["receipt_sha256"] != expected_digest:
        raise ReceiptError("receipt_sha256 does not match canonical receipt JSON")
    if head is None:
        head = _git(root, "rev-parse", "HEAD").stdout.strip()
    require_commit(root, head, "checked-out HEAD")
    entries = _validate_subject(receipt, root, head)
    changed_paths = {path for path, _ in entries}
    claim_ids = _validate_claims(receipt, changed_paths)
    _validate_artifacts(receipt, entries, root)
    _validate_verification(receipt)
    _validate_authority_and_correction(receipt)
    if receipt["status"] == "verified" and (not entries or not receipt["artifacts"]):
        raise ReceiptError("verified receipts require non-empty subject paths and artifacts")
    return claim_ids


def discover_receipts(root, receipts):
    root = Path(root).resolve()
    receipts = Path(receipts)
    if not receipts.is_absolute():
        receipts = root / receipts
    receipts = receipts.resolve()
    try:
        receipts.relative_to(root)
    except ValueError as error:
        raise ReceiptError("receipt directory must be inside repository root") from error
    if not receipts.exists():
        return []
    if not receipts.is_dir():
        raise ReceiptError("receipt path must be a directory")
    return sorted(path for path in receipts.rglob("*.json") if path.is_file())


def _validate_coverage(root, receipt_records, receipt_paths, range_base, range_head):
    require_commit(root, range_base, "range base")
    require_commit(root, range_head, "range head")
    if not is_ancestor(root, range_base, range_head):
        raise ReceiptError("range base must be an ancestor of range head")
    checked_out_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    if checked_out_head != range_head:
        raise ReceiptError("checked-out HEAD must equal --range-head")
    range_entries = derive_diff(root, range_base, range_head)
    receipt_path_set = set(receipt_paths)
    required_paths = {path for path, _ in range_entries if path not in receipt_path_set}
    candidate_subjects = {path: [] for path in required_paths}
    all_qualified_paths = set()
    for receipt in receipt_records:
        if receipt["status"] != "verified":
            continue
        subject = receipt["subject"]["commit"]
        if is_ancestor(root, range_base, subject) and is_ancestor(root, subject, range_head):
            subject_paths = set(receipt["subject"]["changed_paths"])
            all_qualified_paths.update(subject_paths)
            for path in required_paths.intersection(subject_paths):
                candidate_subjects[path].append(subject)
    missing = {path for path, subjects in candidate_subjects.items() if not subjects}
    stale = set()
    for path, subjects in candidate_subjects.items():
        if not subjects:
            continue
        literal_pathspec = ":(literal)" + path
        if all(_git(root, "log", "--format=%H", subject + ".." + range_head, "--", literal_pathspec).stdout.strip() for subject in subjects):
            stale.add(path)
    extra = all_qualified_paths - required_paths - receipt_path_set
    if missing or stale or extra:
        messages = []
        if missing:
            messages.append("uncovered paths: " + ", ".join(sorted(missing)))
        if stale:
            messages.append("stale receipt paths changed after their latest qualifying subject: " + ", ".join(sorted(stale)))
        if extra:
            messages.append("qualified receipt paths outside pull-request range: " + ", ".join(sorted(extra)))
        raise ReceiptError("; ".join(messages))


def validate_directory(repository, root, receipts, range_base=None, range_head=None, require_covered_diff=False):
    root = Path(root).resolve()
    if not (root / ".git").exists():
        # Worktrees use a .git file, while temporary fixtures use a directory.
        probe = _git(root, "rev-parse", "--is-inside-work-tree", check=False)
        if probe.returncode or probe.stdout.strip() != "true":
            raise ReceiptError("--root must be a Git worktree")
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    paths = discover_receipts(root, receipts)
    records = []
    receipt_ids = set()
    claim_ids = set()
    relative_receipt_paths = []
    for path in paths:
        relative_path = path.relative_to(root).as_posix()
        validate_repository_path(relative_path)
        relative_receipt_paths.append(relative_path)
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ReceiptError(relative_path + ": invalid JSON: " + str(error)) from error
        try:
            current_claim_ids = validate_receipt(receipt, repository, root, head=head)
        except ReceiptError as error:
            raise ReceiptError(relative_path + ": " + str(error)) from error
        if receipt["receipt_id"] in receipt_ids:
            raise ReceiptError("duplicate receipt ID: " + receipt["receipt_id"])
        receipt_ids.add(receipt["receipt_id"])
        duplicates = claim_ids.intersection(current_claim_ids)
        if duplicates:
            raise ReceiptError("duplicate claim IDs: " + ", ".join(sorted(duplicates)))
        claim_ids.update(current_claim_ids)
        records.append(receipt)
    if require_covered_diff:
        _validate_coverage(root, records, relative_receipt_paths, range_base, range_head)
    return len(records)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--receipts", default=".quirk/evidence")
    parser.add_argument("--range-base")
    parser.add_argument("--range-head")
    parser.add_argument("--require-covered-diff", action="store_true")
    args = parser.parse_args(argv)
    coverage_values = (args.range_base is not None, args.range_head is not None, args.require_covered_diff)
    if any(coverage_values) and not all(coverage_values):
        parser.error("--range-base, --range-head, and --require-covered-diff must be supplied together")
    try:
        count = validate_directory(
            args.repository,
            args.root,
            args.receipts,
            range_base=args.range_base,
            range_head=args.range_head,
            require_covered_diff=args.require_covered_diff,
        )
    except ReceiptError as error:
        parser.error(str(error))
    noun = "receipt" if count == 1 else "receipts"
    print("Evidence binding passed: " + str(count) + " " + noun)
    return 0


if __name__ == "__main__":
    sys.exit(main())
