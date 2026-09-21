# Roadmap: Organization control plane

Kind: roadmap  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `1263f5008838f743b16ee218046e26dac5c9edd8`  
Reviewed: 2026-09-21  
Review by: 2026-10-05  
Derived from: `docs/intentions/2026-09-20-evidence-first-planning.md`, `docs/superpowers/plans/2026-09-20-org-control-plane.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

The running order for `Quirk-Systems/.github` and `.github-private` as the
organization's agent-ready control plane. Items move between sections; they
are never deleted. Each Done item names the evidence that closed it.

## Now

- [ ] Fold the living-document review into the twice-weekly portfolio review in `docs/governance/AUTONOMOUS_OPERATIONS.md` so review dates are bumped by an existing cadence
- [ ] Add the living-document header to `docs/briefs/2026-09-20-poster-claim-binding.md` and the three plans under `docs/superpowers/plans/` in their next substantive edit

## Next

- [ ] Harden `reusable-validate.yml` (pins, permissions, no interpolation inside `run:`), the last legacy workflow with exemptions; unblocked now that PR #20 is decided
- [ ] Decide whether `workflow-lint.yml` drops its `paths:` filters so `zizmor` becomes requireable, per `docs/governance/OWNER_ACTIVATION_INPUTS.md`
- [ ] Switch self-applied `harden-runner` jobs from egress `audit` to `block`, one workflow at a time, from the observed allowlist in `docs/governance/OWNER_ACTIVATION_INPUTS.md`

## Later

- [ ] Offer the living-document validator to consumer repositories as a reusable workflow once two repositories carry such documents
- [ ] Give the org-default `labeler.yml` and `release-drafter.yml` the workflows that read them, once a `pull-requests: write` and `contents: write` job is agreed

## Done

- [x] Agent operating layer, security spine, repository contract, creation contracts, autonomous-operations loop, docs and hygiene (evidence: PR #23, fifteen receipts in `.quirk/evidence/`)
- [x] Private governance buildout in `.github-private` (evidence: `.github-private` PR #2, receipt `qreceipt.private-governance-buildout.b6bf5aab6639`)
- [x] Dependency review restored on pull requests and the Dependency graph enabled by the owner (evidence: PR #30, receipts `qreceipt.dependency-review-trigger.9925b20c1393` and `qreceipt.dependency-graph-pending-step.9e1b4f7dfc29`; SBOM endpoint read back 200 on 2026-09-20)
- [x] Truthful topology cut, portfolio validator repairs, manual PR ledger, poster claim-binding brief (evidence: PR #35, receipts `qreceipt.governance-contracts-topology-repair.2f9e74dad035` through `qreceipt.poster-claim-binding.d8bff043f194`)
- [x] `Preference Graph` named on `registry.preference` with `Quirk Preference Core` kept as an alias (evidence: `.quirk/registry.json` at the observed head)
- [x] Living-document contract landed: schema, strict validator, templates, skill, and four documents that pass it (evidence: PR #37, receipts `qreceipt.living-documents.*`)
- [x] Reusable PR title lint repaired and its caller unblocked: the callee no longer names a workflow-level scope its job leaves unused, and three other reusable workflows carrying the same latent shape were fixed with it (evidence: PR #38, receipt `qreceipt.reusable-caller-permissions.c2b321a15deb`; `.github-private` PR #4 observed `startup_failure` then `success` at the same callee pin)
- [x] `.github-private` callers pinned to a reviewed `main` commit, the `pull_request` trigger restored, and a `reusable-workflow-lint.yml` caller added (evidence: `.github-private` PRs #3 and #4)
- [x] PR #20 decided: closed, with its five org-default files re-landed and its duplicated workflow-hygiene validator dropped in favour of `tests/test_workflow_pins.py` (evidence: this pull request, receipt `qreceipt.org-defaults.ca693deef695`)
- [x] The owner-only activation inputs compiled from observed runs rather than predicted: check contexts and per-job egress destinations (evidence: `docs/governance/OWNER_ACTIVATION_INPUTS.md`)

## Decisions awaiting an owner

- [ ] `quirk-core`: fold into the admitted kernel canon, or keep distinct and accept that it has no consumer yet. Read on 2026-09-21 at `b3162b0cd6dcc6c07570f240ca33c711ed860f0b`, it does own a distinct contract — the frozen `contracts/v0.2` tranche, nine schemas and eight invariants behind digest `sha256:c0532f52…`, with its own conformance workflow. No repository consumes it: `project-scaffold` at `18636ffe` has no vendored pin, and its `docs/ontology/ONTOLOGY.md` says extraction should wait for a second independent consumer; `quirk-os` at `f8cc12ed` names it only in prose. The registry's own test wants both, so half of it fails (owner: @bryansayler)
- [ ] Required-checks ruleset activation: owner-only, and the exact contexts to require are in `docs/governance/OWNER_ACTIVATION_INPUTS.md`. `zizmor` must not be required until its `paths:` filters go, or it pends forever (owner: @bryansayler)
