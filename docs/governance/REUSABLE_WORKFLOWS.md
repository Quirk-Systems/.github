# Reusable workflows

Status: **candidate shared workflow spine**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

Every workflow below is called with a **full 40-character commit SHA** of this
repository, never a branch or tag. Pick the SHA of a reviewed `main` commit,
record it in the caller's change, and let Dependabot (github-actions ecosystem)
propose bumps. A green check from any of these proves only what the named
tool checked at the named revision; it is not approval, canon, release, or
deployment.

```yaml
# Caller pattern. Replace <sha> with the reviewed .github main commit.
jobs:
  codeql:
    uses: Quirk-Systems/.github/.github/workflows/reusable-codeql.yml@<sha> # main YYYY-MM-DD
    with:
      languages: javascript-typescript
    permissions:
      contents: read
      actions: read
      security-events: write
```

Callers never pass secrets or commands. Inputs are typed and reach actions
through `with:`; no reusable workflow interpolates caller input inside a
`run:` body. Policy sources (validators, parsers) are checked out at
`job.workflow_sha`, so a caller cannot substitute them.

## Catalog

| Workflow | Trigger it serves | Inputs | Caller permissions | What it proves | What it does not prove |
| --- | --- | --- | --- | --- | --- |
| `reusable-evidence-binding.yml` | `pull_request` only | none | `contents: read` | Every changed path in the PR range is covered by a fresh verified receipt | Semantic sufficiency, review, merge, canon |
| `quirk-semantic-governance.yml` | any | none | `contents: read` | Caller `.quirk/manifest.json` has the required keys; the canonical registry, read at this workflow's own pinned commit, lints clean | That the manifest's domain claims are true |
| `reusable-validate.yml` | any | `package-manager`, `node-version`, `bun-version`, `working-directory`, `test-script`, `run-build`, `run-e2e`, `e2e-script` | `contents: read` | JS lint, type-check, tests, build, optional Playwright e2e | Deployment or runtime behavior. Being hardened in a separate PR (pins, permissions) |
| `reusable-pr-title-lint.yml` | `pull_request` | none | `pull-requests: read` | PR title is a Conventional Commit | Commit contents |
| `reusable-codeql.yml` | `push`, `pull_request`, `schedule` | `languages` (required), `build-mode`, `queries` | `contents: read`, `actions: read`, `security-events: write` | CodeQL analysis uploaded to code scanning | Absence of vulnerabilities outside the query suite |
| `reusable-dependency-review.yml` | `pull_request` only | `fail-on-severity`, `deny-licenses` | `contents: read` | No newly introduced dependency crosses the severity or license policy | Runtime reachability of any advisory |
| `reusable-workflow-lint.yml` | `push`, `pull_request` | `persona` | `contents: read` | zizmor finds nothing at the chosen persona (honors the caller's `.github/zizmor.yml`) | Correctness of the workflow logic |
| `reusable-sbom-provenance.yml` | `release`, `push` tag, `workflow_dispatch` | `subject-path` (required), `sbom-path`, `sbom-format` | `contents: read`, `id-token: write`, `attestations: write` | An SBOM artifact and a signed SLSA build-provenance attestation for the subject | That the subject was reviewed or is safe to publish |
| `reusable-stale-incubations.yml` | `schedule` | `days-before-stale`, `only-labels` | `issues: write`, `pull-requests: write` | Idle incubations and proposals get the `stale-incubation` label and a comment | Anything; it never closes. A label is a signal, not a lifecycle decision |
| `reusable-agent-task-contract.yml` | `pull_request`, `push` | none | `contents: read` | Every `.quirk/agent-tasks/*.json` in the caller validates against the agent-task schema | That the task ran, or that its authority was granted |

## Self-applied checks in this repository

`governance-contracts.yml` (tests, validators, exact-range receipts),
`codeql.yml`, `scorecard.yml` (publishes to the OpenSSF Scorecard API after
merge to `main`), `workflow-lint.yml`, `agent-task-dispatch.yml`, and
`dependency-review.yml` on pull requests. Dependency review depends on the
repository's **Dependency graph** (Settings → Code security), an owner-only
setting; the action fails at startup without it, so a red `Dependency Review`
check that names the graph is a settings problem, not a dependency finding.
The owner enabled it on 2026-09-20 (read back: the repository SBOM endpoint
answered 200 and the check passed on PR #30); if it is ever disabled, the
check fails at startup again on every pull request.
Self-applied jobs run
`step-security/harden-runner` in egress **audit** mode; switch to `block`
only after the observed egress allowlist is recorded in a governed change.

## Pin and update policy

- Pin actions to full SHAs with a `# vX.Y.Z` comment; `tests/test_workflow_pins.py`
  enforces this for every workflow not listed as legacy.
- Pin runners to `ubuntu-24.04`, set `timeout-minutes` on every job, set
  `persist-credentials: false` on every checkout, declare top-level
  `permissions: contents: read` and grant write scopes only at job level with a
  comment explaining each one.
- Never use `pull_request_target` or `workflow_run` here; if a future need
  arises it is an owner-reviewed decision with its own receipt.
- Local lint: `scripts/validate.sh` runs actionlint and zizmor (offline,
  pedantic). `.github/zizmor.yml` lists, by exact filename, the four legacy
  workflows whose known findings are being repaired elsewhere; remove each
  entry when that file is fixed.

## Required-check rollout

Repository files cannot activate rulesets. Follow
[`REQUIRED_CHECKS_ROLLOUT.md`](./REQUIRED_CHECKS_ROLLOUT.md): observe the
emitted check context on a representative pull request, record it, then move
the ruleset from Evaluate to Active.
