# Quirk organization defaults and repository map

Status: candidate operating baseline  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

This repository should remain Quirk Systems' constitutional and shared-workflow spine. Keep policy, templates, reusable workflows, semantic contracts, and lightweight Copilot assets here. Move heavier runtime, template, action, and evaluation systems into dedicated repositories once they are real reusable products.

## Path convention

Use repository-relative paths in Quirk docs and reviews:

- `.github/CODEOWNERS`
- `.github/workflows/reusable-validate.yml`
- `.quirk/registry.json`
- `docs/REPOSITORY_STRATEGY.md`

Do not rely on clone-specific filesystem paths when describing the operating model.

## Defaults implemented in this repository

1. **`.github/CODEOWNERS`** — routes review for canonical state, workflows, scripts, tests, prompts, and agents.
2. **`.github/dependabot.yml`** — establishes a weekly GitHub Actions dependency update policy.
3. **`.github/release-drafter.yml`** — provides a shared release-note taxonomy for governance, workflow, Copilot, and documentation changes.
4. **`.github/labeler.yml`** — defines path-based labeling categories for governance, semantic, workflow, Copilot, test, and documentation changes.
5. **`.github/workflows/workflow-hygiene.yml`** — validates workflow defaults from an immutable policy source.
6. **`.github/copilot-instructions.md`** — gives repositories a concise Copilot operating contract focused on bounded change, verification, and authority boundaries.

## Candidate extracted repositories and advanced defaults

7. **`Quirk-Systems/quirk-repo-template`** — a starter repository containing `.devcontainer/devcontainer.json`, `mise.toml`, a `.quirk/manifest.json`, baseline workflows, validation entrypoints, security defaults, and starter docs.
8. **`Quirk-Systems/quirk-actions`** — shared composite or JavaScript actions that should not live indefinitely in `.github` once they carry substantial implementation detail.
9. **`Quirk-Systems/quirk-evals`** — prompt, workflow, semantic, and regression evaluation assets with explicit scoring and reproducibility boundaries.
10. **`Quirk-Systems/quirk-connect`** — candidate interoperability and provider-adapter boundary when connectors become shared products instead of local repository details.
11. **`Quirk-Systems/quirk-cli`** — candidate operator command surface when local tooling, automation entrypoints, and runtime helpers need an independently versioned boundary.

## Placement rules

Keep a capability in `Quirk-Systems/.github` when it is primarily:

- organization policy;
- issue, pull-request, or Copilot guidance;
- reusable workflow orchestration;
- semantic, evidence, or governance validation.

Extract a capability into another repository when it requires:

- its own runtime or package lifecycle;
- a developer-environment baseline shared by multiple repositories;
- substantial action implementation logic;
- independent evaluation datasets or scoring harnesses;
- connector-specific credentials, adapters, or release cadence.

## Relationship to existing strategy

`docs/REPOSITORY_STRATEGY.md` defines the governing extraction rule: do not create a repository merely because a concept has a name. The repositories above are target boundaries, not automatic admissions. Create them only when their second-consumer, ownership, release, or security boundary is proven.
