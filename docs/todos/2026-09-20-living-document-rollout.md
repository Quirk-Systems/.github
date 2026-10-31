# Todo: Living-document rollout

Kind: todo  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c52c0407ea2fa6d3fa99cf13d86492a74733259`
Reviewed: 2026-10-31
Review by: 2026-11-03
Derived from: `docs/goals/2026-09-20-living-documents-validated.md`  
Authority effect: **none**

Tasks that reach the goal, each small enough for one receipt, plus the items
only the owner can move. Proof is the command or observation that closes the
task, recorded in the receipt that ships it.

## Review — 2026-10-31

**VERIFIED — active work remains.** Read against main
`d320f775a1be9ca8f6becfc19c84165bed176d1d` and the observed head above,
which adds only [PR #60](https://github.com/Quirk-Systems/.github/pull/60)'s
portfolio review and evidence. That review is prepared, not merged. This
correction depends on its exact head and preserves its three files byte for
byte; the completed goal also stays unchanged. November 3 aligns with the
portfolio's next checkpoint because cadence integration and enforcement still
need an owner disposition. This is a review deadline, not a configured schedule
or a claim that those decisions have been made. Re-read sooner if a dependency
head or the validation mechanism changes.

**Recovery.** Accessible all-ref document history and recent repository PRs
were checked for later work. The latest rollout/roadmap edit is
`5c1d3520294cbd3cc3264cfd027031ac9a74e24b`; the latest intention edit is
`ceb13f171620028db3c9e015ac22aad2a98be1c0`, both in merged
[PR #42](https://github.com/Quirk-Systems/.github/pull/42). Its corrections
already survive in these files. The owner's
[October 5 follow-up](https://github.com/Quirk-Systems/.github/issues/42#issuecomment-5994668559)
still names required checks, merge methods, and merge-time freshness as pending.
PR #60 is the newer portfolio review, not a review of these three records. No
later completed review of them was recovered in this bounded search; this says
nothing about inaccessible work.

| Task or dependency | October 31 observation | Disposition |
| --- | --- | --- |
| Brief and plan opt-in | The poster brief and all five Markdown plans in `docs/superpowers/plans/` lack a living-document header. The previous queue said three plans. | Still open at each next substantive edit; counts corrected, no opt-in invented. |
| Review cadence | `AUTONOMOUS_OPERATIONS.md` and `REPOSITORY_STRATEGY.md` §8.10 still have six portfolio agenda items and no living-document validator/review item. Draft #45 adds handoff guidance, not this agenda change. | Owner disposition and implementation remain pending. |
| Reusable validator hardening | `reusable-validate.yml` still has `oven-sh/setup-bun@v2`, expressions in `run:`, and exemptions in `.github/zizmor.yml` and `tests/test_workflow_pins.py`. Four workflows remain in `LEGACY`, so this is not the only legacy workflow. | Open; reconcile draft #51 before touching the same file. |
| Two-check PR gate gap | Main's unit suite has no invocation of `quirk_concept.py lint` or `validate-copilot-maintenance.py`; no self-caller invokes semantic governance. | Open. #51 proposes a semantic-lint job but is not merged and does not close the maintenance-validator gap. |
| Consumer rollout | No `reusable-living-docs.yml` exists here; a second adopting repository was not established by this bounded review. | Blocked on adoption evidence, not a claim that no adopter exists anywhere. |

The five plans are `2026-08-21-truthful-topology-cut.md`,
`2026-08-28-exact-range-decision-spine.md`,
`2026-08-28-portfolio-truth-repair.md`, `2026-08-28-pr-closure-harness.md`, and
`2026-09-20-org-control-plane.md`. Source files and tests above were read at the
observed head. Related draft heads were read as candidates: #45
`5de16a5979aa5cbb298f3e16b52984d38caaffba`, #51
`7f18e49a90b1b6d772ed7d80fc6bb48258a2cc77`, and #55
`35c3a05341de125f6466b663775105cb7307527b`. #55 adds working defaults, not
evidence that the missing cadence or gate work is complete.

**Freshness boundary.** Before this correction, strict validation at the PR #60
head with `--today 2026-11-01` exited 1: five documents, exactly these three
active records stale. `Status: done` excludes the goal from staleness; its
October 31 date does not require repair. The portfolio is due November 3.
The validator still uses `review_by < today`; no enforcement code is changed.
Correction checks and their exact tested subject belong in the separate receipt
and PR, not in an assertion of successful hosted execution. The historical
near-lapse account below is retained verbatim.

## Open

- [ ] Add the living-document header to the poster claim-binding brief in its next substantive edit (owner: @bryansayler; proof: `python scripts/validate_living_docs.py --strict` counts one brief)
- [ ] Add the living-document header to the five plans named in the October 31 review in their next substantive edits (owner: @bryansayler; proof: the validator counts each opted-in plan; prior count of three is superseded)
- [ ] Harden `reusable-validate.yml` and remove its zizmor and pin-test exemptions, reconciling draft #51's runner, Bun-pin, and lockfile repairs first (owner: @bryansayler; proof: reviewed file leaves `.github/zizmor.yml` and the `LEGACY` set in `tests/test_workflow_pins.py`; #51's existence alone does not close this task)
- [ ] Give `scripts/quirk_concept.py lint` and `scripts/validate-copilot-maintenance.py` a route into this repository's own pull-request gate: either a test that applies each to this repository's files, as every other validator in `scripts/validate.sh` already has, or a self-caller for `quirk-semantic-governance.yml`. Prefer the test — the gate runs the suite, and a second check context is one more thing an owner must require (owner: @bryansayler; proof: `python -m unittest discover -s tests` fails when `.quirk/registry.json` or a `docs/copilot-maintenance/` link is broken)

## Blocked

- [ ] Integrate living-document review into the existing twice-weekly portfolio agenda after the owner records its scope. Proposed wording: run the strict validator, inspect active/candidate/paused documents due by the next checkpoint, substantively re-read or explicitly retire them, and record evidence and unresolved decisions; never just bump dates (blocked on: @bryansayler's cadence disposition; proof: `docs/governance/AUTONOMOUS_OPERATIONS.md` names the validator and one dated review demonstrates use). This moves the previous Open item here without claiming completion.
- [ ] Offer the validator to consumer repositories as `reusable-living-docs.yml` (blocked on: a second repository carrying living documents; who can unblock: @bryansayler)

## Done

- [x] Living-document schema, validator, tests, four templates, one instance of each kind, and the `quirk-living-doc` skill (evidence: the receipt covering this document's subject commit)
- [x] Reusable PR title lint pinned to `v5.5.3` and removed from the legacy exemptions (evidence: receipt `qreceipt.pr-title-lint-repair.8d04d9cc4bcb`)
- [x] `pull_request` trigger restored on the `.github-private` PR title lint caller and its pin bumped, proof as specified: hosted `PR Title Lint / lint` run `35599424735` succeeded, and run `35602325469` succeeded again on head `b197032d06997f1045a6d9e30d100ae84f11e984` after the caller narrowed its grant to `pull-requests: read` at the repaired pin (evidence: `.github-private` PR #4, merged 2026-09-21)

## Near-lapse record

This document did **not** lapse. Its review date was 2026-10-04 and it was
re-read on 2026-10-03 — one day before that date, and **two** days before any
red, because `validate_living_docs.py` reports a document stale only when
`review_by < today`, which for 2026-10-04 first happens on 2026-10-05. The
first version of this section called it a lapse, said the document "went
unreviewed past 2026-10-04", and then conflated the review date with the first
stale day; all three are corrected here.

What is true is thirteen days unread: nothing in it had been re-read since
2026-09-20, while four of its items had in fact moved. That is the drift worth
recording, and it was caught with a day to spare by an unrelated check rather
than by any cadence.

The cost is not cosmetic, though it is narrower than the first version of this
section claimed. `tests/test_living_docs.py` checks freshness against the real
date and the `validate` check runs the whole suite, so a stale document here
fails the `validate` check on any pull request whose checks run or re-run while the document is stale, including pull requests that changed nothing related. It does not reach back: `governance-contracts.yml` has no
scheduled trigger, so no check already completed turns red on the calendar, and
the first version's "turns every open pull request red" overstated it. The
blast radius is still wide for a planning document nobody is reading, and it is
why the checklist item above is first: the cadence has to carry the re-read, or
the calendar will carry it into CI instead.
