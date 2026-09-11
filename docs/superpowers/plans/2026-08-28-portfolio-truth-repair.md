# Portfolio Truth Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Repair organization portfolio metadata to reflect observed repository reality without inventing purposes or granting authority.

**Architecture:** `.github` remains the portfolio/semantic governance owner. The change records observed drift, repairs only supported repository facts, and leaves uncertain classifications as owner decisions rather than inferred canon.

**Tech Stack:** JSON, Markdown.

**Spec:** Approved three-PR design, 2026-08-28.

## Global Constraints
- canonical portfolio metadata repair only
- no Skill admission/runtime/canon promotion
- no repository rename/archive/delete
- unresolved repositories remain `OBSERVED_UNCLASSIFIED` or `REQUIRES_OWNER_DECISION`
- historical migration plans are not rewritten as completed facts

### Task 1: Record drift evidence
- [ ] Create `docs/PORTFOLIO-DRIFT-2026-08-28.md` with observed current repositories and stale registry facts.

### Task 2: Repair registry facts
- [ ] Update `.quirk/repositories.json` for `quirk-os`, `project-scaffold`, `quirk-core`, and `quirk-skills` using only observed facts and bounded proposed classifications.
- [ ] Preserve unresolved strategic decisions explicitly.

### Task 3: Repair repository strategy projection
- [ ] Mark stale cutover instructions as historical/stale where current state contradicts them.
- [ ] Add current candidate-source ownership note for `quirk-skills`.

### Task 4: Verify and open draft PR
- [ ] Validate JSON syntax and inspect diff.
- [ ] Open draft PR with independent merge gate and no runtime effect.
