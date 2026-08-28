# Quirk Systems Portfolio Drift — 2026-08-28

Status: **candidate evidence / non-operative**.

This document records repository-state drift observed during the Capability Harvest ownership repair. It is evidence for review, not authority to rename, archive, classify, activate, or delete repositories.

## Confirmed drift

1. `.quirk/repositories.json` previously described `Quirk-Systems/quirk-os` as a private empty placeholder proposed for archive. Current observed repository metadata shows `quirk-os` is public and non-empty, with Skill/runtime architecture and candidate code.
2. The same registry treated `project-scaffold → quirk-os` as an uncompleted future rename while both repositories currently exist as distinct non-empty repositories. The historical cutover plan therefore cannot be treated as completed fact.
3. `Quirk-Systems/quirk-core` exists and contains shared contracts, schemas, governance documentation, and validators but was absent from the registry.
4. `Quirk-Systems/quirk-skills` exists as a private candidate source repository and explicitly declares itself non-operative, but was absent from the registry.

## Candidate registry dispositions

| Repository | Disposition in this draft | Authority effect |
| --- | --- | --- |
| `project-scaffold` | preserve as observed active kernel; mark topology reconciliation required | none beyond candidate metadata |
| `quirk-os` | repair visibility/state; mark active observed kernel candidate | no runtime/admission effect |
| `quirk-core` | add candidate portfolio record | no new canonical admission |
| `quirk-skills` | add candidate source record | no Skill admission/runtime effect |

## Observed but unclassified repositories

The organization currently contains additional repositories not represented in the prior portfolio registry, including domain/product names such as `Quirk`, `quirk-dog`, `quirk-music`, `quirk-preference`, `quirk-art`, `quirk-city`, `quirk-style`, `quirk-fitness`, `quirk-feedback`, `quirk-press`, `quirk-work`, `quirk-intelligence`, `quirk-code`, `quirk-bio`, `quirk-health`, `quirk-home`, `quirk-prompt`, `quirk-ops`, `quirk-agents`, `quirk-lab`, `quirk-memory`, `quirk-merchant`, `quirk-arcade`, `quirk-house`, `quirk-club`, `quirk-flirt`, `quirk-money`, `quirk-format`, `quirk-hygiene`, `quirk-design`, `quirk-local`, `quirk-directory`, `quirk-arena`, `quirk-word`, and `quirk-market`.

This draft intentionally does **not** infer their purpose, owner, lifecycle, class, authority, or canonical status from repository names. They remain `OBSERVED_UNCLASSIFIED` or `REQUIRES_OWNER_DECISION` until independently reviewed.

## Stale strategy projection

`docs/REPOSITORY_STRATEGY.md` contains a historical immediate-naming plan that says `quirk-os` is an empty private placeholder and `project-scaffold` should be renamed into it. Current repository state contradicts those premises.

Until a successor topology decision is approved, interpret that section as `HISTORICAL_OR_STALE_PLAN`, not current execution authority. This drift record is additive evidence; it does not perform the rename, archive, migration, or reconciliation itself.

## Next bounded decision

Resolve the current relationship among `project-scaffold`, `quirk-os`, and `quirk-core` as a dedicated topology decision. Keep that decision separate from Capability Harvest and from Skill admission.
