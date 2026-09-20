# Governance

Status: **candidate operating rules**  
Authority effect of this file: **none**. It records how decisions are made;
GitHub rulesets, environment protections, and the organization owner hold
the enforcement.

## Roles

Ownership is by responsibility, not only by path
(`docs/REPOSITORY_STRATEGY.md` §8.5):

| Role | Responsibility | Current holder |
| --- | --- | --- |
| Canon owner | `.quirk/registry.json`, schemas, doctrine documents | @bryansayler |
| Runtime owner | Kernel and runtime repositories | @bryansayler |
| Security owner | `SECURITY.md`, security workflows, credential policy | @bryansayler |
| Data owner | Dataset cards, data classification, `quirk-data` boundary | @bryansayler |
| Realm / product owner | Individual realm and product repositories | @bryansayler |
| Release owner | Release provenance and publication | @bryansayler |
| Incident shutdown authority | Stopping any agent task or automation | @bryansayler |

A single holder today is a fact, not a design. Path-level routing lives in
`CODEOWNERS` (added in a separate pull request).

## Decision levels

- **Organization ADR**: topology, governance, repository classes, security
  posture, shared contracts. Template: `templates/ADR.md` (level:
  organization). Requires the canon owner.
- **Repository ADR**: one repository's architecture or operational behavior.
  Template: `templates/ADR.md` (level: repository). Requires that
  repository's owner.
- **Move receipt**: one bounded consequential action, its authority, and the
  resulting state. Template: `templates/MOVE_RECEIPT.md`.

Accepted decisions update canonical files or registries in the same change.
A closed issue alone is not the final state.

## How a change lands

1. Brief (`templates/BRIEF.md` or the `brief` issue form).
2. Plan (`templates/PLAN.md`) when the work spans more than one wave.
3. Pull request using the template's exact-subject fields, with an evidence
   receipt per substantive commit.
4. Review by the responsible owner. Agents never approve or merge their own work.
5. Merge under the repository's ruleset. Merge is the authority action;
   nothing before it is.

## Semantic changes

Any change that adds, renames, reparents, or deprecates a concept in
`.quirk/registry.json` is a **canonical change**: it needs the admission
grammar in `docs/QUIRK_SEMANTIC_GOVERNANCE.md`, the canon owner's review, and
regeneration of dependent projections.

## Review cadence

Twice weekly for active work; quarterly for topology
(`docs/REPOSITORY_STRATEGY.md` §8.10). The agenda is in
`docs/governance/AUTONOMOUS_OPERATIONS.md`.

## Amending this file

Open a `decision` issue at organization level, then a pull request with a
receipt. This file changes only through that path.
