# Goal: Living documents validated

Kind: goal  
Status: done  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c1061ba8867fdce4d903adc7c9589016e3ab002`  
Reviewed: 2026-10-03  
Review by: 2026-10-31  
Derived from: `docs/intentions/2026-09-20-evidence-first-planning.md`  
Authority effect: **none**

## Outcome

Every intention, goal, roadmap, and to-do document under `docs/` carries a
header that names its kind, status, owner, observed head, review dates, and
lineage; the validator rejects a malformed one, reports a lapsed one, and
runs as part of the repository's single validation entrypoint on every pull
request.

## Measure

```sh
python scripts/validate_living_docs.py --strict
```

Done means: exit code 0 on the current head with at least one document of each
of the four kinds, zero stale documents, and `scripts/validate.sh` invoking the
same script so the pull-request gate inherits it.

## Tasks

- `docs/todos/2026-09-20-living-document-rollout.md`: the tasks that reach this outcome and the owner-only items around it.

## Evidence

- VERIFIED at the observed head: `scripts/validate_templates.py` already checks section structure for briefs, plans, ADRs, and move receipts, and `validate_manifest._check` already applies the closed-schema subset used by every other Quirk contract; the living-document validator reuses both rather than adding a parser.
- INFERRED: the same header can be added to existing briefs and plans without changing their required sections, because the header block sits between the title and the first section.
- UNKNOWN: whether documents in other Quirk repositories will adopt the header before a reusable workflow exists to check them.
- VERIFIED on `main` at the observed head, which is the measure this goal set: `python scripts/validate_living_docs.py --strict` exits 0 reporting four documents, one of each of the four kinds, and zero stale, and `scripts/validate.sh` invokes that script with `--strict`. Both halves of the Review condition below are met.
- The Outcome's phrase "runs as part of the repository's single validation entrypoint on every pull request" conflated two mechanisms, and they are separate. **No workflow invokes `scripts/validate.sh`**; it is the contributor entrypoint. Freshness reaches the pull-request gate by a different route: `governance-contracts.yml` runs the unit suite directly, and `test_repository_documents_are_fresh_today` in `tests/test_living_docs.py` checks every document against the real date. Either one alone would have satisfied a careless reading of the measure; both are named here so a later reader does not look for freshness in a file CI never runs.
- VERIFIED by reading the earlier INFERRED claim: the header can be added to a brief or plan without changing its required sections. The opt-in path exists and is covered by `test_opted_in_brief_and_plan_validate_their_own_sections`, which reuses `validate_templates.REQUIRED_SECTIONS` so the two cannot diverge. No brief or plan has opted in yet; that is a task in the rollout todo, not part of this goal's measure, which asks only for one document of each of the four kinds.

## Review

Marked **done** on 2026-10-03: the measure passes on `main` at
`7c1061ba8867fdce4d903adc7c9589016e3ab002` and the validator runs inside
`scripts/validate.sh`. A `done` document does not go stale, so the review date
above is inert and kept only because the header requires it.

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
