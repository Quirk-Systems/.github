---
name: "quirk-evidence-receipt"
description: "Ship a change to a Quirk repository that enforces exact-range evidence binding: run the checks, generate the receipt against the tested commit, commit it separately, and simulate the pull-request gate before pushing."
---

# Quirk evidence receipt

A receipt binds claims to exact Git bytes. It has authority effect `none`: it
never makes a change mergeable, canonical, released, or deployed. This skill
gets you through the gate honestly; it does not get you past review.

## When to use

- Any commit to `Quirk-Systems/.github` that touches a path other than
  `.quirk/evidence/*.json`.
- Any repository whose pull-request workflow calls
  `reusable-evidence-binding.yml`.
- Re-covering a path you touched again after its receipt was committed.

## Procedure (two commits, never one)

1. **Commit the subject.** Stage only the intended paths. Use a Conventional
   Commit message. Record the base SHA (`git merge-base origin/main HEAD` before
   your first commit, or the PR base) and the subject SHA (`git rev-parse HEAD`).
2. **Run the checks against that exact tree.** In `.github`:
   `scripts/validate.sh`. Elsewhere, the repository's documented validation.
   Every command you will record must have actually run and exited 0.
3. **Generate the receipt** from the `.github` checkout (the generator imports
   the validator from the same directory):

   ```sh
   python scripts/create_evidence_receipt.py \
     --repository <owner/name> --root <path-to-that-repo> \
     --base <base40> --commit <subject40> \
     --receipt-id qreceipt.<slug>.<subject12> \
     --claim-id qclaim.<slug>.<subject12> \
     --claim "<bounded statement of what the bytes do and what remains unproven>" \
     --evidence-path <every path in the subject diff> \
     --verification-command "<each command exactly as run>" \
     --verified-at <RFC3339 UTC ending in Z> \
     --output <repo>/.quirk/evidence/<slug>-<subject12>.json
   ```

   `<slug>` is kebab-case and describes the change; `<subject12>` is the first
   12 hex characters of the subject SHA. Every path in the diff must appear in
   `--evidence-path`, or the generator refuses.
4. **Commit the receipt alone**: `docs(evidence): bind <slug> to <subject12>`.
5. **Simulate the gate** before pushing:

   ```sh
   python scripts/validate_evidence_receipts.py --repository <owner/name> --root . \
     --receipts .quirk/evidence --range-base <base40> --range-head HEAD --require-covered-diff
   ```

   `missing` means a path has no receipt; `stale` means a later commit touched a
   receipted path. Fix by adding a new subject commit plus a new receipt.

## Do

- Write the claim as what the bytes establish and what they do not: "Adds X;
  hosted execution, policy enforcement, and merge approval are not established."
- Keep one receipt per subject commit. Multiple subject/receipt pairs in one PR
  are fine.
- Use `git show -s --format=%cI <subject>` converted to UTC for `--verified-at`
  when generating in CI-like conditions; otherwise the actual time you ran the checks.

## Don't → Do instead

- Don't hand-edit a receipt → regenerate it; the digest covers every field.
- Don't include the receipt in the subject commit → a commit cannot contain its
  own digest.
- Don't record a command you did not run → omit it and list it under "checks not run".
- Don't describe the receipt as approval, canon, or proof of behavior → cite it
  by locator (`source_repository`, `source_commit`, `source_path`, `receipt_sha256`).

## Reference

`docs/governance/EVIDENCE_BINDING.md` defines the subject, freshness, coverage,
correction receipts, and the security boundary. `.quirk/evidence/README.md`
explains the directory rules. The validator never executes recorded commands.
