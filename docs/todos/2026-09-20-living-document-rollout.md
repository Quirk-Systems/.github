# Todo: Living-document rollout

Kind: todo  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`  
Reviewed: 2026-09-20  
Review by: 2026-10-04  
Derived from: `docs/goals/2026-09-20-living-documents-validated.md`  
Authority effect: **none**

Tasks that reach the goal, each small enough for one receipt, plus the items
only the owner can move. Proof is the command or observation that closes the
task, recorded in the receipt that ships it.

## Open

- [ ] Add the living-document header to the poster claim-binding brief in its next substantive edit (owner: @bryansayler; proof: `python scripts/validate_living_docs.py --strict` counts one brief)
- [ ] Add the living-document header to the three plans under `docs/superpowers/plans/` in their next substantive edits (owner: @bryansayler; proof: the validator counts three plans)
- [ ] Extend the twice-weekly portfolio review checklist with "read every stale living document and bump or retire it" (owner: @bryansayler; proof: `docs/governance/AUTONOMOUS_OPERATIONS.md` names the validator)
- [ ] Restore the `pull_request` trigger on the `.github-private` PR title lint caller and bump its pin (owner: @bryansayler; proof: a hosted `PR Title Lint / lint` run succeeds on a private pull request)

## Blocked

- [ ] Offer the validator to consumer repositories as `reusable-living-docs.yml` (blocked on: a second repository carrying living documents; who can unblock: @bryansayler)
- [ ] Harden `reusable-validate.yml` and remove its zizmor and pin-test exemptions (blocked on: the PR #20 decision, which owns that file; who can unblock: @bryansayler)

## Done

- [x] Living-document schema, validator, tests, four templates, one instance of each kind, and the `quirk-living-doc` skill (evidence: the receipt covering this document's subject commit)
- [x] Reusable PR title lint pinned to `v5.5.3` and removed from the legacy exemptions (evidence: receipt `qreceipt.pr-title-lint-repair.8d04d9cc4bcb`)
