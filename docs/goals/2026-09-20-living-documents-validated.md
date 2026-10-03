# Goal: Living documents validated

Kind: goal  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`  
Reviewed: 2026-09-20  
Review by: 2026-10-18  
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

## Review

Mark done when the measure passes on `main` and the validator is in
`scripts/validate.sh`. Re-scope if the owner wants a different freshness
policy (for example, stale fails the gate rather than being reported).
