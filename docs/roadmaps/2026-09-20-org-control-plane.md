# Roadmap: Organization control plane

Kind: roadmap  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`  
Reviewed: 2026-09-20  
Review by: 2026-10-04  
Derived from: `docs/intentions/2026-09-20-evidence-first-planning.md`, `docs/superpowers/plans/2026-09-20-org-control-plane.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

The running order for `Quirk-Systems/.github` and `.github-private` as the
organization's agent-ready control plane. Items move between sections; they
are never deleted. Each Done item names the evidence that closed it.

## Now

- [ ] Land the living-document contract (schema, validator, templates, skill) so planning documents stop drifting silently (goal: `docs/goals/2026-09-20-living-documents-validated.md`)
- [ ] Repair the reusable PR title lint (pinned action, runner, timeout, job-level scope) so consumers can call it under the organization's pinned-actions policy
- [ ] Pin `.github-private` callers to the reviewed `main` commit that carries the merged dependency-review and topology work

## Next

- [ ] Restore the `pull_request` trigger on the `.github-private` PR title lint caller once the repaired callee is on `main`, and bump its pin
- [ ] Add a `reusable-workflow-lint.yml` caller in `.github-private` so its two workflows are linted the same way as the public ones
- [ ] Fold the living-document review into the twice-weekly portfolio review in `docs/governance/AUTONOMOUS_OPERATIONS.md` so review dates are bumped by an existing cadence
- [ ] Add the living-document header to `docs/briefs/2026-09-20-poster-claim-binding.md` and the three plans under `docs/superpowers/plans/` in their next substantive edit

## Later

- [ ] Offer the living-document validator to consumer repositories as a reusable workflow once two repositories carry such documents
- [ ] Harden `reusable-validate.yml` (pins, permissions, no interpolation inside `run:`), the last legacy workflow with exemptions, after the owner decides PR #20
- [ ] Switch self-applied `harden-runner` jobs from egress `audit` to `block` after the observed egress allowlist is recorded in a governed change
- [ ] Move the required-checks ruleset from Evaluate to Active per `docs/governance/REQUIRED_CHECKS_ROLLOUT.md` after observing check contexts on representative pull requests

## Done

- [x] Agent operating layer, security spine, repository contract, creation contracts, autonomous-operations loop, docs and hygiene (evidence: PR #23, fifteen receipts in `.quirk/evidence/`)
- [x] Private governance buildout in `.github-private` (evidence: `.github-private` PR #2, receipt `qreceipt.private-governance-buildout.b6bf5aab6639`)
- [x] Dependency review restored on pull requests and the Dependency graph enabled by the owner (evidence: PR #30, receipts `qreceipt.dependency-review-trigger.9925b20c1393` and `qreceipt.dependency-graph-pending-step.9e1b4f7dfc29`; SBOM endpoint read back 200 on 2026-09-20)
- [x] Truthful topology cut, portfolio validator repairs, manual PR ledger, poster claim-binding brief (evidence: PR #35, receipts `qreceipt.governance-contracts-topology-repair.2f9e74dad035` through `qreceipt.poster-claim-binding.d8bff043f194`)
- [x] `Preference Graph` named on `registry.preference` with `Quirk Preference Core` kept as an alias (evidence: `.quirk/registry.json` at the observed head)

## Decisions awaiting an owner

- [ ] PR #20 (Copilot workflow hygiene): merge, revise, or close; it owns CODEOWNERS, dependabot, labeler, release-drafter, copilot-instructions, workflow-hygiene, and edits to the legacy workflows, and it has been dirty against `main` since 2026-09-11 (owner: @bryansayler)
- [ ] `quirk-core`: fold its doctrine into the admitted kernel canon or define a distinct owned contract and consumer, per the truthful topology cut (owner: @bryansayler)
- [ ] Egress `block` mode and required-checks activation: both are owner-only settings that repository content cannot change (owner: @bryansayler)
