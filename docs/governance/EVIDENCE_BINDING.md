# Evidence binding

Status: **candidate organization control**  
Authority effect: **none**

Evidence binding answers one narrow question:

> Do the receipt's claims point at the exact Git subject and bytes named by the receipt?

It does not decide whether a change is good, sufficient, canonical, admitted,
mergeable, releasable, deployed, or proven in production.

## Exact subject

For pull-request work, the evidence subject is the complete immutable range:

```yaml
repository: owner/name
base_commit: 40-character Git SHA
head_commit: 40-character Git SHA
changed_paths: sorted exact path set
```

A head SHA identifies one tree. It does not by itself identify the patch under
review. Branch names, tags, PR numbers, screenshots, and workflow-run labels may
help locate work, but they cannot replace the exact repository/base/head/path
identity in a consequential claim.

## Two-commit receipt protocol

1. Commit the subject implementation and run its verification commands.
2. Generate the receipt against that earlier subject SHA.
3. Review the generated receipt and commit it separately.

This avoids impossible self-reference: a commit cannot contain a final digest
of itself.

For a verified receipt, the validator derives:

```text
git diff --name-status -z --no-renames <base>..<subject>
```

The sorted path list must match exactly. Present paths are bound to both the Git
blob object and SHA-256 of the bytes returned by `git show <subject>:<path>`.
Deleted paths must be absent at the subject and carry null digests. Every claim
is limited to paths in that subject range. The canonical receipt digest covers
the complete receipt except its own digest field.

The generator records commands that have already run. It never executes receipt
content or treats claimant-recorded command metadata as independent proof.

## Evidence, decision, and authority remain separate

```text
Evidence receipt
    binds observations and recorded checks to exact bytes

Governed decision
    records a human or designated reviewer disposition for that exact head

Authority action
    separately permits or performs merge, canon, release, deployment,
    publication, runtime mutation, or another consequential effect
```

An evidence receipt has structural authority effect `none`. A governed decision
also has structural authority effect `none`; it may identify the next authority
gate, but cannot satisfy that gate by describing it. GitHub reviews, protected
branch rules, environment approvals, release controls, and other authorized
systems remain separate effects.

## Receipt citation versus receipt resolution

A governed decision must cite each receipt with:

```yaml
receipt_id:
source_repository:
source_commit:
source_path:
receipt_sha256:
covered_head_commit:
```

The decision validator proves that this citation is closed, immutable in shape,
path-safe, digest-shaped, and tied to the decision's declared head. It does not
perform network access or claim that an external receipt artifact actually
exists.

Before relying on a cross-repository decision, the receiving boundary must:

1. fetch `source_repository` at the exact `source_commit`;
2. read the exact `source_path` bytes;
3. validate the receipt's canonical digest and schema;
4. verify the receipt's `repository`, base, subject, changed paths, blobs, and
   SHA-256 values against the actual subject repository;
5. confirm `covered_head_commit` equals the decision subject head;
6. reject the decision if any locator, byte, digest, subject, or status differs.

A locator makes evidence resolvable. It is not itself evidence that resolution
succeeded. The read-only pilot tracked in issue #11 owns proving this resolver
boundary before a governed decision can support a consequential action.

## Head changes and staleness

A receipt remains valid historical evidence for the subject it names. A decision
becomes stale for current action as soon as the candidate head changes.

```text
new head
→ old receipt remains historical
→ old decision cannot cover the current candidate
→ evaluate the delta or rerun proof
→ issue a new exact-head receipt and decision
```

No consequential claim may cover a mutable branch name alone.

## Pull-request coverage

For pull-request enforcement, provide `--range-base`, `--range-head`, and
`--require-covered-diff` together. The checked-out `HEAD` must equal the range
head. The union of qualifying verified subject paths must cover every range path
except discovered receipt JSON files.

A later unreceipted change fails closed, including a later modification to a
path named by an older receipt. For every path, at least one qualifying receipt
subject must be at or after its latest change in the range.

README, policy, workflow, schema, test, and documentation files are substantive
paths. They are not silently exempted.

## Merge, build, and deployment identity

A reviewed head is not automatically the final merge result, build, or deployed
runtime. Consequential delivery should preserve a chain such as:

```text
reviewed base/head range
→ merge commit or merge-queue result
→ source archive or package/container digest
→ deployment identifier
→ runtime observation receipt
```

External dependencies, remote assets, mutable image tags, model aliases, and
provider APIs are not frozen merely because Git source is exact. Release-bearing
systems must record the dependency and build identities required for their own
reproducibility claim.

## Correction receipts

Use `unverified` when an external proof claim cannot be reproduced and
`retracted` when a prior claim is withdrawn. A correction requires a reason,
observations, and one or more stable external claim references. A zero-diff
subject may document that a cited comparison contains no implementation delta.
Corrections never satisfy substantive pull-request coverage.

## Security boundary

Git is invoked with argument arrays from fixed validators; receipt content is
never executed through a shell. Reusable workflows accept no caller-provided
commands or secrets, derive repository/base/head from the pull-request event,
use read-only contents permission, and do not persist checkout credentials.

Evidence receipts should not contain credentials, private transcripts, customer
PII, or sensitive payload bytes. Store sensitive evidence behind an explicit
data-classification and retention boundary and commit only the immutable
reference and digest appropriate for review.

## Commands

Generate a receipt after the subject tests have passed:

```sh
python scripts/create_evidence_receipt.py \
  --repository Quirk-Systems/.github \
  --base 0123456789abcdef0123456789abcdef01234567 \
  --commit 89abcdef0123456789abcdef0123456789abcdef \
  --receipt-id qreceipt.example \
  --claim-id qclaim.example \
  --claim "The cited files implement the bounded subject." \
  --evidence-path path/to/subject \
  --verification-command "python -m unittest discover -s tests -v" \
  --verified-at 2026-08-28T14:00:00Z \
  --output .quirk/evidence/qreceipt.example.json
```

The example SHAs illustrate shape only. Never copy them into a real receipt.

Validate stored receipts:

```sh
python scripts/validate_evidence_receipts.py \
  --repository Quirk-Systems/.github \
  --root . \
  --receipts .quirk/evidence
```

Validate a governed decision and optionally reject it as stale for a supplied
current head:

```sh
python scripts/validate_governed_decisions.py \
  --repository Quirk-Systems/.github \
  --root . \
  --decisions .quirk/decisions \
  --current-head 89abcdef0123456789abcdef0123456789abcdef
```

See [`INTEROPERABILITY.md`](./INTEROPERABILITY.md) for cross-system identity,
projection, retry, compatibility, and authority rules.
