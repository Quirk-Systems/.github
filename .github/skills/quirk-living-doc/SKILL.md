---
name: "quirk-living-doc"
description: "Turn an observed strength into an intention, the intention into goals with measures, and the goals into roadmap and todo items, each as a validated living document that names its observed head, owner, review dates, and lineage, so planning inherits the receipt discipline instead of escaping it."
---

# Quirk living document

A living document is a planning artifact that can go stale on purpose. It
names the exact head it observed, who owns it, when it was last read against
that head, when it must be read again, and what it derives from. The
validator, `scripts/validate_living_docs.py`, checks the header against
`.quirk/schemas/living-document.schema.json`, the sections each kind
requires, checkbox discipline, and lineage, and reports the day a document
lapses. Templates: `templates/INTENTION.md`, `GOAL.md`, `ROADMAP.md`,
`TODO.md`; briefs and plans can carry the same header.

## The chain

strength → intention → goal → tasks (todo, plan) → roadmap. Each arrow is a
`Derived from` path. Walk it forward when creating, backward when reviewing.

## When to use

- A review, receipt, or merged pull request shows something working well and
  someone says "we should do more of that."
- An ask arrives as a direction ("make planning trustworthy") rather than a
  bounded piece of work; a brief needs an intention above it.
- A to-do list, roadmap, or plan is about to be written or edited.
- A living document is past its review date.

## Procedure

1. **Start from evidence, not ambition.** Name the strength as something
   VERIFIED at a specific head: a passing gate, a merged PR, a receipt ID, an
   observed outcome. If no evidence exists, write the ask as a brief instead.
2. **Write the intention** with `templates/INTENTION.md`. Fill Not this before
   Goals; it is the section that keeps the next reader from widening it.
3. **Cut goals** with `templates/GOAL.md`. Each has an Outcome someone can
   observe and a Measure that is a command or query whose output can sit in a
   receipt. A goal with no measure goes back into the intention as prose.
4. **Cut tasks** with `templates/TODO.md` (owner and proof per item; blocked
   items name who can unblock them) or, for sequenced multi-wave work, the
   `quirk-plan` skill.
5. **Place them on the roadmap** with `templates/ROADMAP.md`: Now, Next,
   Later, Done. Move items; never delete them. Every Done item names its
   evidence. Decisions awaiting an owner is a real list, not a formality.
6. **Set the dates honestly.** Reviewed is today. Review by is the date the
   document will be wrong if nobody re-reads it (two weeks for roadmaps and
   todos, four for intentions and goals is a reasonable default). Observed
   head is the full SHA you actually read.
7. **Validate and ship.** `python scripts/validate_living_docs.py --strict`,
   then `scripts/validate.sh`, then the two-commit receipt protocol
   (`quirk-evidence-receipt`). The receipt claim states what the document
   observed, not that its contents are true.
8. **Review on the date.** Re-read against the current head. Bump Reviewed and
   Review by, move items, mark Done with evidence, or set Status to `retired`
   with the reason in Review. A retired document stays in the repository.

## Do

- Keep every document under `docs/` so the validator finds it; group by kind
  (`docs/intentions/`, `docs/goals/`, `docs/roadmaps/`, `docs/todos/`).
- Use `Status: candidate` until the owner has read it; only the owner moves it
  to `active`.
- Cite receipts and commits, not branch names or "recent work".
- Let stale be visible. The validator reports lapsed documents on every run;
  `--strict` turns that into a failure for the pull request that ships them.

## Don't → Do instead

- Don't coin a Quirk concept in a living document → run
  `python scripts/quirk_concept.py inspect <name>`; if it is new, propose it
  through the brief form as a canonical change and keep the document generic.
- Don't mark an item Done because a PR exists → mark it Done when the evidence
  is observable, and name it.
- Don't write "current head" or "soon" → write the SHA and the date.
- Don't let a todo grow past what one owner can review in one sitting → split
  it by goal.
- Don't put owner-only items under Open → put them under Blocked with who can
  unblock them, or under the roadmap's Decisions awaiting an owner.
- Don't delete a stale document to make the validator quiet → retire it with
  the reason, or bump it after re-reading.

## Reference

`.quirk/schemas/living-document.schema.json`, `scripts/validate_living_docs.py`,
`tests/test_living_docs.py`, `templates/README.md`, `docs/governance/EVIDENCE_BINDING.md`,
the `quirk-brief` and `quirk-plan` skills.
