# Evidence binding

Evidence binding answers a narrow question: do the receipt's claims point at the
exact Git changes and bytes named by the receipt? It does not decide whether the
change is good, sufficient, canonical, admitted, active, deployed, or proven in
production.

## Receipt protocol

Use two commits:

1. Commit the subject implementation and run its verification commands.
2. Generate the receipt against that earlier subject SHA, review it, and commit
   the receipt separately.

For a verified receipt, the validator derives
`git diff --name-status -z --no-renames <base>..<subject>`. The sorted path list
must match exactly. Present paths are bound to both the Git blob object and SHA-256 of
the bytes returned by `git show <subject>:<path>`. Deleted paths must be absent
at the subject and carry null digests. Each claim is bounded to subject paths.
The canonical receipt digest covers the complete receipt except its own digest
field.

Git path records are read as strict UTF-8 from that NUL-delimited output. This
preserves non-ASCII names without relying on Git's display quoting and rejects
malformed or unsafe path records.

The generator records commands that have already run. It never runs them:

```sh
python scripts/create_evidence_receipt.py \
  --repository Quirk-Systems/.github \
  --base 0123456789abcdef0123456789abcdef01234567 \
  --commit 89abcdef0123456789abcdef0123456789abcdef \
  --receipt-id qreceipt.topology-cut \
  --claim-id qclaim.topology-cut \
  --claim "The topology cut is bound to the cited files." \
  --evidence-path .quirk/repositories.json \
  --verification-command "python -m unittest discover -s tests -v" \
  --verified-at 2026-08-21T12:00:00Z \
  --output .quirk/evidence/qreceipt.topology-cut.json
```

Pass every changed subject path needed by the claim as a repeatable
`--evidence-path`. Pass every already-run command as a repeatable
`--verification-command`. Use full lowercase 40-character Git SHAs and an
explicit UTC timestamp. The example SHAs illustrate shape only; never copy them
into a real receipt.

Validate the current repository without pull-request coverage:

```sh
python scripts/validate_evidence_receipts.py \
  --repository Quirk-Systems/.github \
  --root . \
  --receipts .quirk/evidence
```

For a pull request, add `--range-base`, `--range-head`, and
`--require-covered-diff` together. The checked-out `HEAD` must equal the range
head. The union of qualifying verified subject paths must cover every range path
except discovered receipt JSON files. A later unreceipted change therefore
fails closed, including a later modification to a path named by an older
receipt. For each path, at least one qualifying receipt subject must be at or
after its latest change in the range. A newer receipt may replace stale coverage
for that path. README and policy files are substantive paths and remain covered.

## Correction receipts

Use `unverified` when an external proof claim cannot be reproduced and
`retracted` when a prior claim is withdrawn. A correction requires a reason,
observations, and one or more HTTPS URLs or stable claim IDs. A zero-diff subject
may document that a cited comparison contains no implementation delta.
Corrections never satisfy substantive pull-request coverage.

## Security and authority boundary

Git is invoked with argument arrays from a fixed validator; no receipt content
is executed through a shell. The reusable workflow accepts no caller inputs. It
fails outside a `pull_request` event and derives repository, base SHA, and head
SHA from the caller's GitHub event context. It accepts no commands or secrets,
runs read-only without persisted checkout credentials, and checks out its own
validator at the immutable workflow SHA.

The receipt's command results are claimant-recorded metadata and must be
internally consistent: `pass` means exit code `0`, while `fail` requires a
nonzero exit code. Artifact identity does not establish semantic sufficiency.
Both receipt authority and every claim have a structural effect of `none`.
Claim types are limited to non-authority categories. Free-text statements,
including truthful discussion of authority, are informational and cannot
override those structural fields. Human review and separately authorized
governance still decide meaning and status.

## Preference Graph naming migration

The stable concept ID `registry.preference` is unchanged. Its canonical display
name is **Preference Graph**; **Quirk Preference Core** is a deprecated alias.
The source anchor is
[`quirk-core/docs/canon/preference-language.md` at `1b70bce23e88ecb97d652bd8a50896c8f4bc64c4`](https://github.com/Quirk-Systems/quirk-core/blob/1b70bce23e88ecb97d652bd8a50896c8f4bc64c4/docs/canon/preference-language.md).
This is a projection correction, not a new admission or ownership transfer.
