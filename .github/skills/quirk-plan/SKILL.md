---
name: "quirk-plan"
description: "Sequence an accepted brief into an executable PLAN.md of waves, each with files, reused code, exact verification commands, and a receipt, so an agent can build it without inventing scope."
---

# Quirk plan

A plan converts a brief's outcome into ordered, independently shippable waves.
Use `templates/PLAN.md`. Existing precedent lives in `docs/superpowers/plans/`.

## Procedure

1. **Start from a brief.** If none exists, run `quirk-brief` first. Copy the
   brief's outcome into Goal unchanged.
2. **Pin the base.** Record the base commit SHA the plan starts from. Every
   wave's receipt will chain from it.
3. **Inventory reuse before design.** Search the repository for validators,
   schemas, tests, workflows, and templates that already do part of the job.
   List them under Reuses with paths. New code that duplicates an existing
   utility is a defect in the plan.
4. **Cut waves by shippability**, not by file type. A wave is done when the
   repository's validation entrypoint passes and the receipt is committed. If
   the work stops after any wave, the repository must still be green and
   coherent.
5. **Write verification as commands**, one per line, that will be recorded in
   the receipt exactly as run. Include the pull-request gate simulation where
   the repository enforces evidence binding.
6. **Name what is out of scope** and where it goes (follow-up issue, another
   repository, owner decision). Doctrine: no new repository or capability
   because a concept has a name.
7. **List risks with containment**, not just risks.

## Do

- Keep waves small enough that a receipt claim can describe them honestly.
- Put owner-only actions (rulesets, org settings, publication) in Out of
  scope with the exact step the owner performs.
- Use checkboxes and tick them as delivered so the plan doubles as a ledger.

## Don't → Do instead

- Don't plan a wave that cannot be verified by a command → split it until it can.
- Don't schedule "cleanup later" → either it is a wave with a receipt or it is
  out of scope.
- Don't write file paths for things that will move → describe the capability
  and name only load-bearing paths (commands, schemas, entrypoints).
- Don't reorder waves so the risky one lands last → put the change most likely
  to be rejected first, while the diff is smallest.

## Reference

`templates/PLAN.md`, `docs/governance/EVIDENCE_BINDING.md`, the
`quirk-build` and `quirk-ship` prompts in `prompt-packs/quirk/prompts/`.
