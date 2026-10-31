# Roadmap: Organization control plane

Kind: roadmap  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c52c0407ea2fa6d3fa99cf13d86492a74733259`
Reviewed: 2026-10-31
Review by: 2026-11-03
Derived from: `docs/intentions/2026-09-20-evidence-first-planning.md`, `docs/superpowers/plans/2026-09-20-org-control-plane.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

The running order for `Quirk-Systems/.github` and `.github-private` as the
organization's agent-ready control plane. Items move between sections; they
are never deleted. Each Done item names the evidence that closed it.

## Review — 2026-10-31

**VERIFIED — active, with owner decisions outstanding.** Main was
`d320f775a1be9ca8f6becfc19c84165bed176d1d`; the observed head is
[PR #60](https://github.com/Quirk-Systems/.github/pull/60)'s unmerged portfolio
review. Its November 3 checkpoint and three files are preserved, as is the done
living-documents goal. The [rollout review](../todos/2026-09-20-living-document-rollout.md)
records the recovery search, exact candidate heads, task proofs, and five-plan
inventory. No newer completed review of these three records was recovered.

The cadence gap remains: the two existing portfolio checklists do not name
living-document review. The freshness decision remains: `validate.sh` invokes
the strict validator locally, while `governance-contracts.yml` invokes the unit
suite, whose real-date freshness test can fail an unrelated PR's next run.
There is no schedule in that workflow and no merge-time freshness mechanism
added here. A completed check is not retroactively changed by the calendar.
The two items are now explicitly separated into pending owner dispositions
and their implementation work below.

**Current settings observation, not activation.** On October 31 the GitHub
`branches/main` response reported `protected: false` and required status checks
disabled; the repository `rulesets` list was empty. These are dated API reads,
not an exhaustive audit of organization settings or permission to change them.
Receipt-preserving merge-method settings were not verified. The
[owner's October 5 follow-up](https://github.com/Quirk-Systems/.github/issues/42#issuecomment-5994668559)
names the same settings and merge-time freshness as unresolved; no owner
decision closing them was found in the inspected sources.

**Dependencies.** #51 at `7f18e49a90b1b6d772ed7d80fc6bb48258a2cc77` is
still a draft: its Bun pin, runner preflight, lockfile repair, and proposed
semantic-lint job are not on main. It retains the legacy exemptions and does
not add the maintenance-validator check. #45 at
`5de16a5979aa5cbb298f3e16b52984d38caaffba` adds optional strict tool
availability/handoff guidance; it does not integrate the review cadence.
#55 at `35c3a05341de125f6466b663775105cb7307527b` is also still a draft.
None is marked Done here. `workflow-lint.yml` retains path filters, the
self-applied harden-runner jobs retain audit mode, and no workflow references
the labeler or release-drafter configuration.

**Core boundary.** `quirk-core/main` was read at
`b3162b0cd6dcc6c07570f240ca33c711ed860f0b`, unchanged from the recorded
contract head. The portfolio review leaves its manifest task open. The complete
current consumer graph was not re-established; the September absence remains a
dated observation, not renewed proof of universal absence. The existing
doctrine-retention decision stands.

**Next review: November 3.** This short checkpoint aligns with the recovered
portfolio review and asks the owner to disposition cadence, enforcement, and
overlapping candidates before another lapse. It does not promise those decisions
will be complete or configure a new automation. Earlier dependency-head changes
also trigger a re-read. The three active records are fresh through November 3
after correction and become stale November 4 if still unreviewed. The goal's
done status exempts it. Hosted success remains separate: the observed PR #60
head's Governance Contracts run `41070255937`, Dependency Review
`41070255939`, and CodeQL `41070255837` failed; this review does not turn those
failures into passes.

### Historical context retained

The prior header observed `7c1061ba8867fdce4d903adc7c9589016e3ab002`,
reviewed October 4, due October 31. On October 3 the rollout todo was one day
from its October 4 review date and this roadmap two days from October 5: two
and three days from any stale result, since `review_by < today`. The rollout's
full near-lapse/correction record remains unchanged. The inherited Done entries
below retain their original evidence; references in them to "this head" or
"the observed head" mean that historical head, not this October 31 observation.

## Now

- [ ] Prepare cadence integration for the owner disposition below, then apply the accepted wording to `docs/governance/AUTONOMOUS_OPERATIONS.md` and record one actual review using it (owner: @bryansayler; current proposal and closure proof are in the rollout todo). This replaces the previous instruction to bump dates with substantive re-reading.
- [ ] Add the living-document header to `docs/briefs/2026-09-20-poster-claim-binding.md` and the five plans named in the rollout review in their next substantive edits; the prior three-plan count is superseded
- [ ] Close the two-check gap between `scripts/validate.sh` and the pull-request gate. No workflow runs `validate.sh`; the gate runs the unit suite, and eleven of the thirteen checks in that script reach it anyway because a test applies each validator to this repository's own files. The two that do not are `scripts/quirk_concept.py lint` and `scripts/validate-copilot-maintenance.py`, neither of which has a test module. The first is the sharper one: this repository offers the registry linter to other repositories through `quirk-semantic-governance.yml`, which is `workflow_call`/`workflow_dispatch` only, and has no self-caller — so the one repository that never lints its own registry on a pull request is the one that owns it (owner: @bryansayler)

## Next

- [ ] Harden `reusable-validate.yml` (pins, permissions, no interpolation inside `run:`) and remove its exemptions after reconciling draft #51. PR #20 is decided, but four workflows still occur in `LEGACY`; the prior "last legacy workflow" description was inaccurate
- [ ] Decide whether `workflow-lint.yml` drops its `paths:` filters so `zizmor` becomes requireable, per `docs/governance/OWNER_ACTIVATION_INPUTS.md`
- [ ] Switch self-applied `harden-runner` jobs from egress `audit` to `block`, one workflow at a time, from the observed allowlist in `docs/governance/OWNER_ACTIVATION_INPUTS.md`

## Later

- [ ] Offer the living-document validator to consumer repositories as a reusable workflow once two repositories carry such documents
- [ ] Give the org-default `labeler.yml` and `release-drafter.yml` the workflows that read them, once a `pull-requests: write` and `contents: write` job is agreed
- [ ] Verify whether a first consumer of quirk-core's `contracts/v0.2` tranche now exists; if none is established, build or name one through its own review (owner: @bryansayler; proof: exact consumer head and contract-use evidence). Preserve the recorded September gap without asserting a fresh exhaustive search

## Done

- [x] Agent operating layer, security spine, repository contract, creation contracts, autonomous-operations loop, docs and hygiene (evidence: PR #23, fifteen receipts in `.quirk/evidence/`)
- [x] Private governance buildout in `.github-private` (evidence: `.github-private` PR #2, receipt `qreceipt.private-governance-buildout.b6bf5aab6639`)
- [x] Dependency review restored on pull requests and the Dependency graph enabled by the owner (evidence: PR #30, receipts `qreceipt.dependency-review-trigger.9925b20c1393` and `qreceipt.dependency-graph-pending-step.9e1b4f7dfc29`; SBOM endpoint read back 200 on 2026-09-20)
- [x] Truthful topology cut, portfolio validator repairs, manual PR ledger, poster claim-binding brief (evidence: PR #35, receipts `qreceipt.governance-contracts-topology-repair.2f9e74dad035` through `qreceipt.poster-claim-binding.d8bff043f194`)
- [x] `Preference Graph` named on `registry.preference` with `Quirk Preference Core` kept as an alias (evidence: `.quirk/registry.json` at the observed head)
- [x] Living-document contract landed: schema, strict validator, templates, skill, and four documents that pass it (evidence: PR #37, receipts `qreceipt.living-document-contract.22ac1f3dd420`, `qreceipt.living-document-freshness.dbf106bd8152`, `qreceipt.living-document-lineage-fix.2ce5fbe9b112`, `qreceipt.living-document-list-markers.0343f0c2a7af` and `qreceipt.living-document-wording.ef1a6de17459`)
- [x] Reusable PR title lint repaired and its caller unblocked: the callee no longer names a workflow-level scope its job leaves unused, and three other reusable workflows carrying the same latent shape were fixed with it (evidence: PR #38, receipt `qreceipt.reusable-caller-permissions.c2b321a15deb`; `.github-private` PR #4 observed `startup_failure` then `success` at the same callee pin)
- [x] `.github-private` callers pinned to a reviewed `main` commit, the `pull_request` trigger restored, and a `reusable-workflow-lint.yml` caller added (evidence: `.github-private` PRs #3 and #4)
- [x] PR #20 decided: closed, with its five org-default files re-landed and its duplicated workflow-hygiene validator dropped in favour of `tests/test_workflow_pins.py` (evidence: this pull request, receipt `qreceipt.org-defaults.ca693deef695`)
- [x] The owner-only activation inputs compiled from observed runs rather than predicted: check contexts and per-job egress destinations (evidence: `docs/governance/OWNER_ACTIVATION_INPUTS.md`)
- [x] `quirk-core` decided by tightening the test rather than the repository: a doctrine-class repository is kept separate for owning a distinct, versioned, enforceable contract, and a consumer is no longer part of that test, because canon precedes what is built against it and no sibling `canon` or `kernel` entry carries such a requirement. Re-applied, quirk-core passes on the frozen `contracts/v0.2` tranche; the absent consumer is recorded as an observation (evidence: `.quirk/repositories.json` and `docs/PORTFOLIO.md` at this head, anchored to quirk-core `b3162b0cd6dcc6c07570f240ca33c711ed860f0b`)
- [x] `.github-private` carries the clarified `internal` rule: content stays internal, a bare cross-reference may be named in a public artifact (evidence: `.github-private` PR #5, merged 2026-09-25, receipt `qreceipt.internal-line.ca3d9ecb887d`; private `main` at `fe3ec1c978ee748d90c5645467eff3261af7b0c3`)

## Decisions awaiting an owner

- [ ] Integrate review into the existing twice-weekly portfolio cadence: accept or revise the rollout's proposal to inspect documents due by the next checkpoint and record substantive findings, including unresolved decisions. No date-only renewal and no new scheduler are proposed (owner: @bryansayler; proof: explicit disposition and a reviewed checklist change)
- [ ] Decide where living-document freshness should be enforced: retain all-PR real-date failure, scope it to relevant changes with scheduled reporting, and/or add merge-time rechecking. Each option needs its coverage, unrelated-PR cost, and missed-review behavior stated before implementation. This item moved from Now because it requires an owner decision; current enforcement is unchanged (owner: @bryansayler)
- [ ] Required-checks ruleset activation: owner-only, and the exact contexts to require are in `docs/governance/OWNER_ACTIVATION_INPUTS.md`. `zizmor` must not be required until its `paths:` filters go, or it pends forever (owner: @bryansayler)
- [ ] Verify and enforce receipt-preserving merge methods in repository settings. The existing protocol requires Create a merge commit; whether the squash/rebase buttons are restricted is UNKNOWN here (owner: @bryansayler; proof: settings readback)

## Completed work recovered in the October 31 review

These are landed changes, distinct from the open decisions above. The historical
Done section is preserved rather than rewritten as new evidence.

| Work | Evidence on observed main | Limit |
| --- | --- | --- |
| Living-document goal closure and review corrections | #42 merge `ed2f2ff7caacdb7a148ac9811dce1e7cce48a7c8`; the goal remains done. | Cadence and freshness-placement decisions stayed open. |
| Workspace scanner, portfolio plan, receipt-range repairs | #44 merge `c029a903c018e63633e4b2c8b4a83da54801e32f`. | Does not configure scheduled portfolio review. |
| Evidence-bound code-review skill | #48 merge `eb889adf3009951de873890103199600f4aad20f`. | Does not establish execution or usefulness in consumers. |
| Dependabot label correction | #47 merge `d320f775a1be9ca8f6becfc19c84165bed176d1d`. | Does not resolve hosted execution failures. |

The October 30 portfolio review is separately completed as review work in
`bc4d582573306d076c3611f8463dce42d8be90ab` with receipt-only successor
`7c52c0407ea2fa6d3fa99cf13d86492a74733259`; its PR #60 is still an open
draft, so adoption on main is pending. Its content is not changed here.
