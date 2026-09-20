# Quirk creation templates

Owner: `Quirk-Systems/.github`  
Authority effect: **none**

Copy a template, fill every section, delete nothing. A section that does not
apply says why. Each template is the human-readable half of a contract; the
machine-checked half lives in `.quirk/schemas/`. `scripts/validate_templates.py`
verifies that every template still carries its required sections and that
every JSON example validates against its schema.

| Template | Use it when | Machine contract | Skill |
| --- | --- | --- | --- |
| [`BRIEF.md`](./BRIEF.md) | Turning an ask, idea, or spark into a bounded piece of work before anyone builds | — (sections checked) | `quirk-brief` |
| [`PLAN.md`](./PLAN.md) | Sequencing a brief into commits, waves, and proofs an agent can execute | — (sections checked) | `quirk-plan` |
| [`ADR.md`](./ADR.md) | Recording an organization or repository architecture decision | — (sections checked) | `quirk-architecture` prompt |
| [`MOVE_RECEIPT.md`](./MOVE_RECEIPT.md) | Recording one bounded consequential action, its authority, and the resulting state change | pairs with an evidence receipt | `quirk-evidence-receipt` |
| [`artifact-manifest.json`](./artifact-manifest.json) | Publishing any generated asset (image, audio, document, dataset slice, model output) with provenance | `.quirk/schemas/artifact-manifest.schema.json` | `quirk-artifact-forge` |
| [`dataset-card.json`](./dataset-card.json) | Describing a dataset's origin, schema, license, and intended use before it is consumed | `.quirk/schemas/dataset-card.schema.json` | `quirk-dataset-card` |
| [`agent-task.json`](./agent-task.json) | Proposing a bounded agent task with tools, paths, limits, owner, shutdown authority, evidence, and rollback | `.quirk/schemas/agent-task.schema.json` | `agent-task` issue form |
| [`INTENTION.md`](./INTENTION.md) | Turning an evidenced strength into a direction the organization keeps true | `.quirk/schemas/living-document.schema.json` (header) | `quirk-living-doc` |
| [`GOAL.md`](./GOAL.md) | Stating an observable outcome with a measure that can sit in a receipt | `.quirk/schemas/living-document.schema.json` (header) | `quirk-living-doc` |
| [`ROADMAP.md`](./ROADMAP.md) | Ordering work as Now / Next / Later / Done with the decisions only an owner can make | `.quirk/schemas/living-document.schema.json` (header) | `quirk-living-doc` |
| [`TODO.md`](./TODO.md) | Tracking bounded tasks with an owner, a proof, and who can unblock each blocked one | `.quirk/schemas/living-document.schema.json` (header) | `quirk-living-doc` |

The four living-document templates share one header (kind, status, owner,
observed head, reviewed, review by, derived from, authority effect) that
`scripts/validate_living_docs.py` parses and checks for every document under
`docs/` that carries a `Kind:` line, including briefs and plans that adopt it.
A document past its review date is reported stale; `--strict` fails on it.

Design tokens have no template; the seed source is `.quirk/design/tokens.json`
and the contract is `.quirk/schemas/design-tokens.schema.json` (see
`docs/design/DESIGN_SYSTEM.md`).

## Rules that apply to every template

- Name the exact subject: repository, base SHA, head SHA, paths. Branch names
  and issue numbers locate; they do not prove.
- State the semantic impact class (reuse / extend / change / project canon) and
  the concept IDs touched, per `docs/QUIRK_SEMANTIC_GOVERNANCE.md`.
- Separate VERIFIED, INFERRED, and UNKNOWN.
- Name the human authority still required. A filled template grants nothing.
