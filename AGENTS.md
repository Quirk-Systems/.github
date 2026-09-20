<!-- Generated: 2026-09-20 by AgentFile Forge -->
# Quirk-Systems/.github

## What This Is

The organization's constitutional canon and shared workflow spine. It holds the
Quirk concept registry, the portfolio registry, evidence and decision contracts,
reusable GitHub Actions workflows, agent profiles, skills, prompt packs, and
templates. It is not a runtime and not a product. Everything here has authority
effect `none`: files describe and validate; humans and GitHub rulesets decide.

## Stack

Python 3.12 standard library only (no third-party imports in `scripts/` or
`tests/`), `unittest`, JSON Schema draft 2020-12, Git, GitHub Actions, Markdown.

## Commands

```sh
# One test module
python -m unittest tests.test_evidence_receipts -v
# Everything a contributor runs before a receipt (tests, validators, lint)
scripts/validate.sh
# Generate the receipt for an already-committed, already-tested subject
python scripts/create_evidence_receipt.py --help
# Simulate the pull-request gate exactly as CI runs it
python scripts/validate_evidence_receipts.py --repository Quirk-Systems/.github \
  --root . --receipts .quirk/evidence --range-base <base40> --range-head HEAD --require-covered-diff
```

## Architecture

- **Canon** lives in `.quirk/`: the concept registry is the source; docs,
  prompts, manifests, and UIs are projections that must not redefine it.
- **Evidence → decision → authority** are three separate layers. A receipt binds
  claims to exact bytes; a governed decision records a disposition for an exact
  head; authority (merge, canon, release, deploy) is a separate human act.
- **Reusable workflows** in `.github/workflows/reusable-*.yml` take no
  caller-supplied commands or secrets and pin their own policy source by SHA.
- **Agent assets**: org-level Copilot profiles in `agents/`, canonical skills in
  `.github/skills/`, Claude Code shims in `.claude/skills/`, portable prompts in
  `prompt-packs/`, creation templates in `templates/`.

## Conventions

### Do
- Follow the two-commit receipt protocol for every substantive change: commit
  the subject, run `scripts/validate.sh`, generate the receipt against that exact
  SHA, commit the receipt alone. See the `quirk-evidence-receipt` skill.
- Pin every remote action or reusable workflow to a full 40-character SHA with a
  `# vX.Y.Z` comment.
- Put values from `${{ }}` expressions into `env:` and read them from the shell;
  never interpolate expressions inside `run:` bodies.
- Label claims VERIFIED, INFERRED, or UNKNOWN. Report checks not run.
- Use Conventional Commits (`type(scope): summary`) and the PR template's exact
  base/head SHAs.

### Don't → Do Instead
- Don't touch a path after its receipt was committed → generate a newer receipt
  covering the later change.
- Don't infer a repository's purpose from its name → record it as
  `OBSERVED_UNCLASSIFIED` with observed facts only.
- Don't rename, alias, or reparent a canonical concept ID in a doc → propose a
  registry change and mark the PR `canonical-change`.
- Don't call a green check proof of behavior → cite the command, revision, and
  observed output.
- Don't write "rulesets/branch protection updated" → write what the files
  define and name the owner-only step still required.
- Don't add a `pip install` or third-party import to validators → use the
  standard library; CI has no dependency step.
- Don't create a new repository or a new capability because a concept has a
  name → open the repository-proposal issue form and answer the creation gate.

## Permissions

- **Allowed without asking**: read anything; run tests, validators, lint;
  edit files in the assigned scope; commit on the assigned branch; open a draft PR.
- **Ask first**: changing a schema version, editing `.quirk/registry.json`
  concepts, adding a workflow with any `write` permission, deleting receipts.
- **Never**: approve or merge your own PR; dismiss reviews; force-push or
  `--no-verify`; edit rulesets, secrets, or org settings; claim canon,
  admission, deployment, or publication happened.

## Context Pointers

- Changing anything about receipts, decisions, or the PR gate: read
  `docs/governance/EVIDENCE_BINDING.md` first, because the validator's
  freshness and coverage rules are stricter than they look.
- Proposing, classifying, or retiring a repository: read
  `docs/REPOSITORY_STRATEGY.md` §5–§7 for the gate and lifecycle states.
- Introducing a named Quirk concept: read `docs/QUIRK_SEMANTIC_GOVERNANCE.md`
  and run `python scripts/quirk_concept.py inspect <name>` to avoid collisions.
- Adding or consuming a workflow: read `docs/governance/REUSABLE_WORKFLOWS.md`.
- Driving an agent task end to end: read `docs/governance/AUTONOMOUS_OPERATIONS.md`.
- Writing or editing an intention, goal, roadmap, or todo: use the
  `quirk-living-doc` skill and run `python scripts/validate_living_docs.py --strict`;
  a planning document names the head it observed and the date it goes stale.
