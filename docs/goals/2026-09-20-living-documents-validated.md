# Goal: Living documents validated

Kind: goal  
Status: done  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c1061ba8867fdce4d903adc7c9589016e3ab002`  
Reviewed: 2026-10-04  
Review by: 2026-10-31  
Derived from: `docs/intentions/2026-09-20-evidence-first-planning.md`  
Authority effect: **none**

## Outcome

Every intention, goal, roadmap, and to-do document under `docs/` carries a
header that names its kind, status, owner, observed head, review dates, and
lineage; the validator rejects a malformed one and fails on a lapsed one under
`--strict`; `scripts/validate.sh` runs it that way for contributors; and the
unit suite the pull-request gate does run checks the same freshness against the
real date, so **the next pull-request check to run or re-run while a document is
stale fails**.

That is the whole of it, and the limit is part of the outcome rather than a
caveat on it. A check that already completed green stays green, and
`governance-contracts.yml` has no `schedule` trigger, so a pull request that
passed before a review date and merges after it carries the lapse to `main`
with nothing going red. Enforcing freshness at merge time would close that, and
it is an open owner decision on the roadmap, not something this goal claimed.

## Measure

```sh
python scripts/validate_living_docs.py --strict
```

Done means three things, each checkable at the observed head: exit code 0 with
at least one document of each of the four kinds and zero stale documents;
`scripts/validate.sh` invoking the same script with `--strict`; and
`tests/test_living_docs.py` applying the validator to the real documents
against the real date, because the pull-request gate runs the unit suite and
runs no part of `scripts/validate.sh`.

## Tasks

- `docs/todos/2026-09-20-living-document-rollout.md`: the tasks that reach this outcome and the owner-only items around it.

## Evidence

- VERIFIED at the observed head: `scripts/validate_templates.py` already checks section structure for briefs, plans, ADRs, and move receipts, and `validate_manifest._check` already applies the closed-schema subset used by every other Quirk contract; the living-document validator reuses both rather than adding a parser.
- VERIFIED: the same header can be added to existing briefs and plans without changing their required sections. The opt-in path is covered by `test_opted_in_brief_and_plan_validate_their_own_sections`, which reuses `validate_templates.REQUIRED_SECTIONS` so the two cannot diverge.
- UNKNOWN: whether documents in other Quirk repositories will adopt the header before a reusable workflow exists to check them.
- VERIFIED on `main` at the observed head: `python scripts/validate_living_docs.py --strict` exits 0 reporting four documents, one of each of the four kinds, and zero stale; `scripts/validate.sh` invokes that script with `--strict`; and `tests/test_living_docs.py` applies the validator to the real documents. All three conditions of the Measure hold.
- The Outcome and Measure first read "runs as part of the repository's single validation entrypoint on every pull request" and "so the pull-request gate inherits it". That conflated two separate mechanisms and the second clause was simply false. **No workflow invokes `scripts/validate.sh`**; it is the contributor entrypoint. Freshness reaches the pull-request gate by a different route: `governance-contracts.yml` runs the unit suite directly, and `test_repository_documents_are_fresh_today` in `tests/test_living_docs.py` checks every document against the real date. Both are now named in the Measure so a later reader does not look for freshness in a file CI never runs.
- VERIFIED by reading `scripts/validate.sh` against `.github/workflows/` and `tests/` at the observed head: of the thirteen checks `validate.sh` runs, every one but two reaches the pull-request gate, because the suite the gate runs applies each validator to this repository's own files — `test_repository_manifest_is_valid`, `test_projection_is_in_sync`, `test_example_validates_and_repository_has_no_orphan_records`, `test_repository_documents_are_fresh_today` and their siblings. The two with no route in are `scripts/quirk_concept.py lint` and `scripts/validate-copilot-maintenance.py`, neither of which has a test module. `quirk_concept.py lint` does run in `quirk-semantic-governance.yml`, but that workflow is `workflow_call`/`workflow_dispatch` only and this repository has no self-caller for it, so the registry linter this repository offers other repositories is the one check it does not apply to itself on a pull request. That gap is recorded on the roadmap; it is not part of this goal's measure, which is about living documents.
- No brief or plan has opted in yet; that is a task in the rollout todo, not part of this goal's measure, which asks only for one document of each of the four kinds.

## Review

Marked **done** on 2026-10-03: the measure passes on `main` at
`7c1061ba8867fdce4d903adc7c9589016e3ab002` and the validator runs inside
`scripts/validate.sh`. A `done` document does not go stale, so the review date
above is inert and kept only because the header requires it.

Re-read on 2026-10-04 after review challenged the `done`, on the grounds that
the Measure's trailing clause — "so the pull-request gate inherits it" — is
false, which it is. Two responses were available and they are not equivalent.

Flipping this goal back to `active` was the first, and it was rejected on the
facts: it would assert that the outcome is not reached when it is. Living-document
freshness **is** enforced on every pull request, by `tests/test_living_docs.py`
inside the suite `governance-contracts.yml` runs. Marking a reached outcome
unreached to look rigorous is as dishonest as the opposite, and it would have
buried a real finding under a false one.

What was done instead: the false clause was struck and the Measure now names
the mechanism that actually carries freshness into the gate. That is not the
same move as rewriting a measure to fit what was delivered, and the difference
is worth stating because the two look alike. Nothing testable was removed. The
original Measure asked for two checkable things (the validator passing; and
`validate.sh` invoking it) and gave a third clause as the *reason* the second
mattered. The reason was wrong; the bar is now higher, not lower, because the
replacement clause is itself checkable and someone can fail it. Had the measure
required something the work did not deliver, the honest move would have been
`active`, and this paragraph would say so.

The finding that survives is narrower and real, and it belongs to the roadmap
rather than here: the gate runs the unit suite, not `scripts/validate.sh`, so
any check in that script with no test behind it is unenforced on a pull request.
Two qualify, both named in the Evidence above.

A later round of the same review caught the replacement Outcome overstating its
own guarantee: it said a lapse "cannot reach `main` unnoticed", while the
paragraph four below it already said completed checks stay green and only the
next push or re-run fails. Both cannot be true, and the weaker one is the true
one — a pull request that passes before a review date and merges after it
carries the lapse through. The Outcome now says what the test does and names
the hole as part of the outcome. That makes three times in this document's
history that the same subtlety has been got wrong in the same direction, always
by overstating where staleness bites, which is why the limit is now written
into the Outcome rather than left to a later section.

The re-scope this section anticipated did happen, and it is worth naming
because it was not a neutral choice. The Outcome above says the validator
*reports* a lapsed document. What shipped is stricter: `scripts/validate.sh`
passes `--strict`, and `tests/test_living_docs.py` checks freshness against the
real date, so a lapse *fails* the gate. That is the "stale fails the gate
rather than being reported" option, adopted without being written down here.

Its cost showed up on 2026-10-03. The validator reports a document stale when
`review_by < today`, so a review date is not the day anything breaks — the day
after it is. The rollout todo was due 2026-10-04 and would first have reported
stale on 2026-10-05; this roadmap was due 2026-10-05 and would first have
reported stale on 2026-10-06. Read on 2026-10-03, that is one and two days
before their review dates, two and three before any red.

The consequence is narrower than "every open pull request" but still wide:
because the `validate` check runs the whole suite, a stale planning document
fails the `validate` check on any pull request whose checks run or re-run while the document is stale, including pull requests that changed nothing related. `governance-contracts.yml` has no scheduled trigger, so
nothing turns red on the calendar alone and checks already completed stay
green; the next push or re-run is what fails. Staleness should bite — the open question,
now on the roadmap, is whether it should bite the stale document's own change
or a scheduled report instead. That question belongs to a successor goal, not
to this one; this goal's outcome is reached.
