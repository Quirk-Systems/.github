# Todo: Living-document rollout

Kind: todo  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `1263f5008838f743b16ee218046e26dac5c9edd8`  
Reviewed: 2026-10-03  
Review by: 2026-10-31  
Derived from: `docs/goals/2026-09-20-living-documents-validated.md`  
Authority effect: **none**

Tasks that reach the goal, each small enough for one receipt, plus the items
only the owner can move. Proof is the command or observation that closes the
task, recorded in the receipt that ships it.

## Open

- [ ] Add the living-document header to the poster claim-binding brief in its next substantive edit (owner: @bryansayler; proof: `python scripts/validate_living_docs.py --strict` counts one brief)
- [ ] Add the living-document header to the three plans under `docs/superpowers/plans/` in their next substantive edits (owner: @bryansayler; proof: the validator counts three plans)
- [ ] Extend the twice-weekly portfolio review checklist with "read every stale living document and bump or retire it" (owner: @bryansayler; proof: `docs/governance/AUTONOMOUS_OPERATIONS.md` names the validator). This is the mitigation for the lapse recorded below, so it is the first of these to do
- [ ] Harden `reusable-validate.yml` and remove its zizmor and pin-test exemptions, now that the PR #20 decision that owned that file is made (owner: @bryansayler; proof: the file leaves `.github/zizmor.yml` and the `LEGACY` set in `tests/test_workflow_pins.py`)

## Blocked

- [ ] Offer the validator to consumer repositories as `reusable-living-docs.yml` (blocked on: a second repository carrying living documents; who can unblock: @bryansayler)

## Done

- [x] Living-document schema, validator, tests, four templates, one instance of each kind, and the `quirk-living-doc` skill (evidence: the receipt covering this document's subject commit)
- [x] Reusable PR title lint pinned to `v5.5.3` and removed from the legacy exemptions (evidence: receipt `qreceipt.pr-title-lint-repair.8d04d9cc4bcb`)
- [x] `pull_request` trigger restored on the `.github-private` PR title lint caller and its pin bumped, proof as specified: hosted `PR Title Lint / lint` run `35599424735` succeeded, and run `35601…` succeeded again after the caller narrowed its grant to `pull-requests: read` at the repaired pin (evidence: `.github-private` PR #4, merged 2026-09-21)

## Lapse record

This document went unreviewed past 2026-10-04 and was re-read on 2026-10-03,
one day before it would have lapsed. Nothing in it had been re-read since
2026-09-20, while four of its items had in fact moved.

The cost is not cosmetic. `tests/test_living_docs.py` checks freshness against
the real date, and the `validate` check runs the whole suite, so a lapsed
document here turns **every open pull request** against `main` red, not only a
pull request that touches the document. That is a wide blast radius for a
planning document nobody is reading, and it is why the checklist item above is
first: the cadence has to carry the re-read, or the calendar will carry it
into CI instead.
