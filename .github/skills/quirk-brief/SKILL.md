---
name: "quirk-brief"
description: "Turn an ask, idea, spark, or issue into a bounded BRIEF.md with a real outcome, constraints, semantic impact, evidence plan, and named residue before anyone builds."
---

# Quirk brief

A brief is the smallest document that lets someone else decide whether the
work should exist. It is not a plan and not a pitch. Use `templates/BRIEF.md`.

## When to use

- A request arrives as a sentence, a spark, or a two-word coinage with no scope.
- An issue is being opened with the `brief` form.
- A plan is being written and no brief exists; write the brief first.

## Procedure

1. **Orient before writing.** Read the repository's `AGENTS.md` and the files
   the ask touches. Record the current head SHA. If the ask names a Quirk
   concept, run `python scripts/quirk_concept.py inspect <name>` and note
   whether it exists, is an alias, or is new.
2. **Write the Outcome first.** One or two sentences naming the observable
   condition. If you cannot say how it would be observed, keep interrogating
   the ask until you can, or record the gap under Residue.
3. **Fill Context, Constraints, Semantic impact, Evidence, Action,
   Verification, Risk, Residue** in that order. Mark each evidence line
   VERIFIED, INFERRED, or UNKNOWN.
4. **Apply the creation gate.** If the action would create a repository,
   capability, framework, or named system, answer the questions in
   `docs/REPOSITORY_STRATEGY.md` §5 inside the brief. The default answer is
   "not yet".
5. **Name the authority.** Under Residue, state which human decision the
   brief needs and what the brief does not grant.
6. Save as `docs/briefs/YYYY-MM-DD-<slug>.md` in the owning repository (or
   paste into the `brief` issue form) and ship with a receipt where the
   repository requires one.

## Do

- Keep it under two pages. A brief that needs a table of contents is a plan.
- Quote the ask verbatim at the top of Context so drift is visible later.
- Prefer one sharp outcome over three soft ones; split otherwise.

## Don't → Do instead

- Don't write "improve", "modernize", or "leverage" as an outcome → write
  the state that becomes true and how it is observed.
- Don't invent facts to fill a section → write UNKNOWN and what would resolve it.
- Don't let the brief name a new Quirk concept casually → answer the
  admission grammar in `docs/QUIRK_SEMANTIC_GOVERNANCE.md` or mark it experimental.
- Don't treat an accepted brief as authorization to build → the plan and its
  receipts still go through review.

## Reference

`templates/BRIEF.md`, `templates/README.md`, the `quirk-orient` and
`quirk-poke-holes` prompts in `prompt-packs/quirk/prompts/`.
