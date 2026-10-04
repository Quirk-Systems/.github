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


def correction_for(args):
    """Build the receipt's `correction` object, or None when it corrects nothing.

    The evidence contract treats a correction as a separate instrument rather
    than an annotation on an attestation: `validate_evidence_receipts` requires
    `correction` to be null on a `verified` receipt and non-null on an
    `unverified` or `retracted` one. So a receipt cannot both attest bytes and
    correct an earlier claim; correcting one means issuing a non-verified receipt
    that names the claim it corrects.

    This generator emitted only `verified` receipts with `correction` hardcoded
    to null, so the instrument the schema has carried all along was unreachable
    and every correction so far was prose inside a claim statement, where no
    validator or query can find it. The three parts travel together because a
    correction with no reason, no claim it corrects, or no observation behind it
    is not a correction; the schema requires all three.

    Adding `--status` alone did not finish the job. `--evidence-path` and
    `--verification-command` stayed mandatory, and a correction has neither: it
    withdraws a claim rather than attesting bytes, so its subject is zero-diff
    and there is nothing for a command to have passed against. The validator
    always allowed both to be empty on a non-verified receipt and requires both
    on a verified one; only this generator insisted. Until this change the one
    correction in `.quirk/evidence` had to be written by hand, which is the
    failure mode receipts exist to prevent.
    """
    parts = (args.correction_reason, args.corrects_claim, args.correction_observation)
    if args.status == "verified":
        if any(parts):
            raise SystemExit(
                "a verified receipt cannot carry a correction: the validator requires "
                "correction to be null when status is verified. Issue the correction as a "
                "separate receipt with --status retracted or --status unverified."
            )
        return None
    if not all(parts):
        raise SystemExit(
            f"--status {args.status} requires a correction: --correction-reason, at least one "
            "--corrects-claim, and at least one --correction-observation; got "
            f"reason={bool(args.correction_reason)}, "
            f"claims={len(args.corrects_claim)}, "
            f"observations={len(args.correction_observation)}"
        )
    refs = list(dict.fromkeys(args.corrects_claim))
    if len(refs) != len(args.corrects_claim):
        raise SystemExit("--corrects-claim must not repeat a claim reference")
    return {
        "reason": args.correction_reason,
        "external_claim_refs": refs,
        "observations": list(args.correction_observation),
    }


def build_receipt(args):
    root = Path(args.root).resolve()
    correction = correction_for(args)
    if args.status == "verified":
        # The validator rejects a verified receipt with no evidence path and no
        # command; failing here says which flag is missing instead.
        if not args.evidence_path:
            raise ReceiptError("--evidence-path is required for a verified receipt")
        if not args.verification_command:
            raise ReceiptError("--verification-command is required for a verified receipt")
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
        "status": args.status,
        "subject": {
            "base_commit": args.base,
            "commit": args.commit,
            "changed_paths": changed_paths,
        },
        "claims": [{
            "claim_id": args.claim_id,
            # A withdrawal is not an attestation, and the bounded claim types
            # distinguish them, so the type follows the status rather than
            # needing a flag a caller could set inconsistently with it.
            "claim_type": "evidence" if args.status == "verified" else "correction",
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
        "correction": correction,
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
    # Required for a verified receipt and checked in build_receipt; a correction
    # has a zero-diff subject and no command, so neither can be mandatory here.
    parser.add_argument("--evidence-path", action="append", default=[])
    parser.add_argument("--verification-command", action="append", default=[])
    parser.add_argument("--verified-at", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--status", default="verified", choices=("verified", "unverified", "retracted"),
                        help="verified attests bytes and forbids a correction; unverified and "
                             "retracted are correction instruments and require one")
    parser.add_argument("--correction-reason",
                        help="why an earlier claim is being corrected; requires the two flags below")
    parser.add_argument("--corrects-claim", action="append", default=[],
                        help="claim id this receipt corrects, repeatable; must not repeat")
    parser.add_argument("--correction-observation", action="append", default=[],
                        help="an observation supporting the correction, repeatable")
    args = parser.parse_args(argv)
    try:
        receipt = build_receipt(args)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ReceiptError) as error:
        parser.error(str(error))
    print("Created " + args.status + " evidence receipt: " + str(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
