# Organization Control Plane Implementation Plan

> **For agentic workers:** execute wave by wave. Each wave ends with
> `scripts/validate.sh` passing and a receipt commit. Do not start the next
> wave on a red gate. Use `quirk-plan` and `quirk-evidence-receipt`.

**Goal:** Make `Quirk-Systems/.github` and `.github-private` the agent-ready
control plane of the organization: every agent host reads the same doctrine,
commands, and authority boundaries; every consumer repository can pull
SHA-pinned security, provenance, manifest, and agent-task checks; and Quirk
creation work (briefs, plans, assets, datasets, design tokens) has a
machine-checked contract.

**Base:** `b33b60b479dff7c69db79d16e9fb4a2c3b95d518` (`main`, 2026-09-19)  
**Owner:** @bryansayler  
**Authority effect:** none. Nothing here changes rulesets, org settings, or
repository classification.

## Architecture

The registry stays the source; everything added is a validator, a contract,
a projection, or an instruction. Evidence → decision → authority remain three
layers. Reusable workflows take no caller commands or secrets and pin their
own policy at `job.workflow_sha`.

## Global constraints

- Standard-library Python 3.12 validators; `unittest`; no dependency step.
- Full-SHA action pins with version comments; read-only default permissions.
- No files owned by the open workflow-hygiene pull request (#20): CODEOWNERS,
  dependabot, labeler, release-drafter, copilot-instructions,
  workflow-hygiene, and the four pre-existing workflows.
- No new repositories; observed repositories are recorded as
  `OBSERVED_UNCLASSIFIED` with facts only.

## Waves

### Wave 1 — Agent operating layer

- [x] `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `scripts/hooks/guard.py`
- [x] `quirk-evidence-receipt` skill + Claude shims; `scripts/validate_agent_assets.py`; tests
- [x] `docs/governance/AGENT_OPERATING_MODEL.md`, `scripts/validate.sh`, `pyproject.toml`, `.github/zizmor.yml`
- [x] Receipt `qreceipt.agent-operating-layer.ec2183d1845f`

### Wave 2 — Security and supply-chain spine

- [x] `codeql.yml`, `scorecard.yml`, `dependency-review.yml`, `workflow-lint.yml`
- [x] `reusable-codeql.yml`, `reusable-dependency-review.yml`, `reusable-workflow-lint.yml`, `reusable-sbom-provenance.yml`, `reusable-stale-incubations.yml`
- [x] `tests/test_workflow_pins.py`, `docs/governance/REUSABLE_WORKFLOWS.md`
- [x] Receipt `qreceipt.security-workflow-spine.6883b4a8baf2`

### Wave 3 — Repository contract and portfolio truth

- [x] `repository-manifest.schema.json` + `validate_manifest.py`; `portfolio-registry.schema.json` + `validate_portfolio.py`; tests
- [x] 35 observed-unclassified repositories recorded; `portfolio_report.py` → `docs/PORTFOLIO.md`
- [x] `profile/README.md` truth repair
- [x] Receipt `qreceipt.repository-contract-portfolio.45003f50ff79`

### Wave 4 — Creation contracts

- [x] `templates/` (BRIEF, PLAN, ADR, MOVE_RECEIPT, JSON examples)
- [x] Schemas: artifact manifest, dataset card, design tokens; `.quirk/design/tokens.json` + `design_tokens.py`; `docs/design/DESIGN_SYSTEM.md`
- [x] `datasets/quirk-governance-corpus`; skills `quirk-brief`, `quirk-plan`, `quirk-artifact-forge`, `quirk-dataset-card`, `quirk-design-tokens`; `brief` and `decision` issue forms; `validate_templates.py`
- [x] Receipt `qreceipt.creation-contracts.57d299e68162`

### Wave 5 — Autonomous operations loop

- [x] `agent-task.schema.json` + `validate_agent_tasks.py` + tests + `templates/agent-task.json`
- [x] `agent-task` issue form; `reusable-agent-task-contract.yml`; `agent-task-dispatch.yml`
- [x] `docs/governance/AUTONOMOUS_OPERATIONS.md`
- [x] Receipt `qreceipt.autonomous-operations.b0fdb9ef36c3`

### Wave 6 — Docs and hygiene

- [x] `README.md`, `CONTRIBUTING.md` (evidence protocol, forms, casing), `SUPPORT.md`, `GOVERNANCE.md`, `NOTICE`
- [x] `.editorconfig`, `.gitattributes`, `.gitignore`, issue `config.yml`, this plan
- [ ] Receipt (issued after this wave's subject commit)

### `.github-private`

- [ ] Pinned callers, CODEOWNERS, dependabot, hygiene files, manifest repair, `extensions.json`
- [ ] README, members-only profile, `AGENTS.md`, `CLAUDE.md`, templates, internal runbooks
- [ ] Receipt

## Verification (end to end)

```sh
scripts/validate.sh
python scripts/validate_evidence_receipts.py --repository Quirk-Systems/.github --root . \
  --receipts .quirk/evidence --range-base b33b60b479dff7c69db79d16e9fb4a2c3b95d518 --range-head <head> --require-covered-diff
uv run --python 3.12 -m unittest discover -s tests
```

## Out of scope

- Files owned by PR #20; if that PR closes, they become one follow-up wave.
- Owner-only: rulesets, required checks, code-scanning and Scorecard
  enablement, Copilot custom-agent enablement, any new repository.
- The `project-scaffold` / `quirk-os` / `quirk-core` topology decision.
- The cross-repository receipt resolver (issue #11) and any real governed decision.
- Real design values, real datasets, app and automation runtimes (belong in
  `quirk-design`, `quirk-data`, `quirk-os`).
- Adding the `Preference Graph` alias to `registry.preference` (a registry
  edit; proposed as a follow-up canonical change).

## Risks

- zizmor and actionlint findings on new workflows: fixed before each push; legacy files scoped by filename in `.github/zizmor.yml`.
- `tests/test_maintenance_index.py` hardcodes 2026-09-11; `MAINTENANCE_INDEX.md` is untouched.
- Receipt freshness: every later commit to a receipted path gets a new receipt.
- Scorecard publishes only after the workflow is on `main`.
