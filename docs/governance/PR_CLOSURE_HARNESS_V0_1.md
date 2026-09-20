# PR Closure Harness v0.1 (shadow mode)

Status: **candidate / read-only shadow mode**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

This contract turns the Wave 1 pull-request portfolio into a finite exact-head
closure queue. It records candidate dispositions only; it does not merge, close,
admit canon, deploy runtime, activate rulesets, publish artifacts, or perform
any irreversible authority action.

## Allowed dispositions

- `READY_FOR_MERGE`
- `READY_FOR_HUMAN_ADMISSION`
- `REVISE`
- `HOLD_CANDIDATE`
- `SUPERSEDE`
- `CLOSE_AS_REDUNDANT`

## Ownership map used by this queue

| Repository | Owning responsibility |
| --- | --- |
| `Quirk-Systems/Quirk` | Civic Surface: venues, explainers, manifests, navigation, non-authoritative consumer proofs |
| `Quirk-Systems/.github` | Organization governance, exact-head evidence contracts, PR controls, templates, reusable workflows |
| `Quirk-Systems/quirk-os` | Candidate contracts, evaluation systems, doctrine, governed system designs |
| `Quirk-Systems/quirk-core` | Explicitly admitted canonical contracts and narrow canonical state |
| `Quirk-Systems/project-scaffold` | Runnable reference implementation and DevRel example |
| `Quirk-Systems/quirk-run` | Bounded runtime execution |
| `Quirk-Systems/quirk-data` | Append-only evidence and projection storage |
| `Quirk-Systems/quirk-skills` | Reusable skills only |

`Quirkroot` is retired as an active boundary.

## Proof Passport output contract

`scripts/closure_harness_shadow.py` validates
`.quirk/closure-wave1-queue.json` and emits a machine-readable JSON proof
passport for one exact queue subject.

```sh
python scripts/closure_harness_shadow.py --check
python scripts/closure_harness_shadow.py \
  --repository Quirk-Systems/.github \
  --pull-request 9 \
  --base-sha <full-40-sha>
```

The emitted passport keeps `external_writes: 0`, keeps every authority grant
field `false`, and marks `stale_when_head_changes: true`.

## Required loop

`OBSERVE → CLASSIFY → LOCK → REPRODUCE → CHEAPEST DISPROOF → ISOLATE → RED → REPAIR → VERIFY → ATTACK → REVIEW → PASSPORT → WARRANT → HUMAN GATE → POST-MERGE PROOF → RE-SNAPSHOT`

## Stop/split boundaries

- `MATERIAL_SCOPE_CHANGE → PAUSE → SPLIT`
- `AUTHORITY_CHANGE → PAUSE → RE_AUTHORIZE`
- Stop when a candidate mixes boundary admission with runtime implementation,
  when more than three unrelated blocker classes appear, after two failed repair
  iterations without blocker reduction, when provider writes become necessary, or
  when head changes stale prior evidence.

## Wave split

Wave 1 includes human-authored security/governance/admission/ownership/evidence/
runtime-boundary/repository-safety PRs.

Wave 2 (dependabot majors, generated migrations, duplicated bot PRs,
framework/toolchain trains) begins only after Wave 1 has zero unclassified
human-authored PRs.
