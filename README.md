# Quirk-Systems/.github

The organization's constitutional canon and shared workflow spine. This
repository holds what every Quirk Systems repository inherits or consumes:
governance doctrine, the semantic and portfolio registries, evidence and
decision contracts, reusable GitHub Actions workflows, agent instructions,
skills, prompt packs, and creation templates.

It is not a runtime and not a product. Everything here has authority effect
**none**: files describe, validate, and project; humans and GitHub rulesets
decide. A green check proves what the named tool checked at the named
revision, nothing more.

## Map

| Path | What lives there |
| --- | --- |
| `AGENTS.md`, `CLAUDE.md`, `.claude/` | Instructions every agent reads first; Claude Code settings, guard hook, skill shims |
| `agents/`, `.github/skills/`, `prompt-packs/` | Org-level Copilot profiles, canonical skills, the eleven-move prompt pack |
| `.quirk/registry.json` | The Quirk concept registry: the semantic source of truth |
| `.quirk/repositories.json` → `docs/PORTFOLIO.md` | Portfolio registry and its generated projection, including observed-but-unclassified repositories |
| `.quirk/schemas/` | Closed JSON Schemas: evidence receipts, governed decisions, repository manifests, portfolio, artifact manifests, dataset cards, design tokens, agent tasks |
| `.quirk/evidence/`, `.quirk/decisions/`, `.quirk/agent-tasks/` | Exact-range receipts, decision records, agent task contracts |
| `.quirk/design/tokens.json` | Candidate design-token source (contract owned here; visuals owned by `quirk-design`) |
| `.github/workflows/` | Self-applied checks and `reusable-*` workflows for consumer repositories |
| `scripts/`, `tests/` | Standard-library validators and their unit tests |
| `templates/`, `datasets/` | Brief, plan, ADR, move-receipt, artifact, dataset-card, and agent-task templates; dataset cards |
| `docs/` | Strategy, semantic governance, evidence binding, interoperability, reusable workflows, agent operating model, autonomous operations, design system |
| `profile/` | The public organization profile |

## Consume a reusable workflow

Pin to a full commit SHA of a reviewed `main`; never a branch or tag.

```yaml
jobs:
  evidence:
    uses: Quirk-Systems/.github/.github/workflows/reusable-evidence-binding.yml@<sha> # main YYYY-MM-DD
    permissions:
      contents: read
```

The catalog, inputs, permissions, and proof boundary of each workflow are in
[`docs/governance/REUSABLE_WORKFLOWS.md`](docs/governance/REUSABLE_WORKFLOWS.md).
Every consumer also declares a `.quirk/manifest.json` validated by
`scripts/validate_manifest.py` against
[`.quirk/schemas/repository-manifest.schema.json`](.quirk/schemas/repository-manifest.schema.json).

## Validate locally

```sh
scripts/validate.sh
```

Runs the unit suite, every validator, ruff, and (when installed) actionlint
and zizmor. Python 3.12 standard library only; CI has no dependency step.

## Ship a change here

Every substantive change needs an exact-range evidence receipt or the pull
request gate fails. The two-commit protocol (subject commit, then receipt
commit) is in [`CONTRIBUTING.md`](CONTRIBUTING.md) and the
`quirk-evidence-receipt` skill; the contract is
[`docs/governance/EVIDENCE_BINDING.md`](docs/governance/EVIDENCE_BINDING.md).

## Doctrine

- [`docs/REPOSITORY_STRATEGY.md`](docs/REPOSITORY_STRATEGY.md): classes, lifecycle, creation gate, security baseline, agent governance.
- [`docs/QUIRK_SEMANTIC_GOVERNANCE.md`](docs/QUIRK_SEMANTIC_GOVERNANCE.md): the registry is the source; everything else projects it.
- [`docs/governance/INTEROPERABILITY.md`](docs/governance/INTEROPERABILITY.md): identities, exchange format, idempotency, platform boundaries.
- [`docs/governance/AGENT_OPERATING_MODEL.md`](docs/governance/AGENT_OPERATING_MODEL.md) and [`docs/governance/AUTONOMOUS_OPERATIONS.md`](docs/governance/AUTONOMOUS_OPERATIONS.md): how agents work here and what is deliberately not automated.
- [`GOVERNANCE.md`](GOVERNANCE.md), [`SUPPORT.md`](SUPPORT.md), [`SECURITY.md`](SECURITY.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

> A repository is not created to honor a noun. It is created to enforce a real boundary.
