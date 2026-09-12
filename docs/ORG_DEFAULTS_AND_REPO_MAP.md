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

### Workflow hygiene proof boundary

The validator checks actual action references, job and service container image
digests, unsafe triggers, top-level concurrency, and both workflow and job
permission declarations. An explicit job permission mapping remains allowed;
`write-all` is rejected at either level. Expressions cannot substitute for a
literal immutable container digest.

The reusable hygiene workflow checks out candidate data in `.quirk-subject` and
its own immutable source in `.quirk-policy`. It executes no candidate code and
uses Python isolated mode so candidate files cannot supply imported modules.
The GitHub.com [`job.workflow_repository` and `job.workflow_sha` contexts](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#example-usage-of-job-context-workflow-identity)
identify the called workflow, including for external callers. They are supported
on GitHub.com and unavailable on GitHub Enterprise Server. Missing or unexpected
identity fails before policy execution; no caller or default-branch fallback is
used. The policy checkout SHA is read back before use.

Local adversarial tests demonstrate rejection of mutable images and job-level
permission overrides, and execute the isolated validator against a subject
containing a no-op replacement checker and a hostile Python module. These tests
do not establish a hosted cross-repository invocation or required-check policy.
Making the job mandatory, admitting a policy revision, and changing repository
permissions remain separate reviewed decisions. A workflow in a PR cannot make
its own definition an independently enforced repository rule.

## Candidate extracted repositories and advanced defaults

7. **`Quirk-Systems/quirk-repo-template`** — a starter repository containing `.devcontainer/devcontainer.json`, `mise.toml`, a `.quirk/manifest.json`, baseline workflows, validation entrypoints, security defaults, and starter docs.
8. **`Quirk-Systems/quirk-actions`** — shared composite or JavaScript actions that should not live indefinitely in `.github` once they carry substantial implementation detail.
9. **`Quirk-Systems/quirk-evals`** — prompt, workflow, semantic, and regression evaluation assets with explicit scoring and reproducibility boundaries.
10. **`Quirk-Systems/quirk-connect`** — candidate interoperability and provider-adapter boundary when connectors become shared products instead of local repository details.
11. **`Quirk-Systems/quirk-cli`** — candidate operator command surface when local tooling, automation entrypoints, and runtime helpers need an independently versioned boundary.

## Additional Quirk capability lanes

When the capability becomes a real shared product rather than lightweight `.github` configuration, prefer a dedicated repository boundary:

- **`Quirk-Systems/quirk-skills`** — versioned Skill source, packaging, examples, and admission tests beyond lightweight shared `.github/skills/` assets.
- **`Quirk-Systems/quirk-plugins`** — plugin SDKs, extension contracts, compatibility fixtures, and plugin release lifecycle.
- **`Quirk-Systems/quirk-mcp`** — MCP servers, tool manifests, transport adapters, and host-integration contracts.
- **`Quirk-Systems/quirk-api`** — versioned query/control APIs, schema publication, and service-surface compatibility guarantees.
- **`Quirk-Systems/quirk-auth`** — identity, auth, consent, token, and permission-boundary logic that should not be hidden inside generic workflow configuration.

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

## Workflow validator development

Install the pinned parser in an isolated Python environment with
`python -m pip install -r requirements-workflow-hygiene.txt`, then run
`python -m unittest tests.test_workflow_hygiene -v` and
`python scripts/validate_workflow_hygiene.py --root . --workflows .github/workflows`.
Governance CI runs these rules against the repository; the reusable workflow
checks out its own parser and dependency pin for downstream callers.

The validator reads YAML structure rather than scanning text. It handles scalar,
sequence, mapping, quoted and aliased triggers; nested remote action paths; and
read-only permission shorthand. Duplicate keys, YAML merge keys, missing event
structure, mutable remote actions/images, and empty concurrency groups fail
closed. Text inside `run` blocks is not interpreted as workflow configuration.
Only direct `.github/workflows/*.yml` and `*.yaml` files are workflow inputs.
This checks the declared hygiene policy, not the complete GitHub Actions schema
or runtime execution of every reusable workflow.
