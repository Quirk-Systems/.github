"""Create a verified evidence receipt from an already-tested Git subject commit."""

import argparse
import json
import sys
from pathlib import Path

from validate_evidence_receipts import (
    ReceiptError,
    artifact_for_path,
    canonical_receipt_digest,
    derive_diff,
    validate_receipt,
)


def build_receipt(args):
    root = Path(args.root).resolve()
    entries = derive_diff(root, args.base, args.commit)
    changed_paths = [path for path, _ in entries]
    evidence_paths = sorted(set(args.evidence_path))
    if len(evidence_paths) != len(args.evidence_path):
        raise ReceiptError("--evidence-path values must be unique")
    outside = set(evidence_paths) - set(changed_paths)
    if outside:
        raise ReceiptError("claim evidence paths are outside the subject diff: " + ", ".join(sorted(outside)))
    receipt = {
        "schema_version": "evidence-receipt.v1",
        "receipt_id": args.receipt_id,
        "repository": args.repository,
        "status": "verified",
        "subject": {
            "base_commit": args.base,
            "commit": args.commit,
            "changed_paths": changed_paths,
        },
        "claims": [{
            "claim_id": args.claim_id,
            "claim_type": "evidence",
            "authority_effect": "none",
            "statement": args.claim,
            "evidence_paths": evidence_paths,
        }],
        "artifacts": [
            artifact_for_path(root, args.commit, path, state) for path, state in entries
        ],
        "verification": {
            "commands": [
                {"command": command, "result": "pass", "exit_code": 0}
                for command in args.verification_command
            ],
            "verified_at": args.verified_at,
        },
        "authority": {"admission_effect": "none", "authority_ref": None},
        "correction": None,
    }
    receipt["receipt_sha256"] = canonical_receipt_digest(receipt)
    validate_receipt(receipt, args.repository, root)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--claim", required=True)
    parser.add_argument("--evidence-path", action="append", required=True)
    parser.add_argument("--verification-command", action="append", required=True)
    parser.add_argument("--verified-at", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        receipt = build_receipt(args)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ReceiptError) as error:
        parser.error(str(error))
    print("Created verified evidence receipt: " + str(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
