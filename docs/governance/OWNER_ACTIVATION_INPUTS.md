# Owner activation inputs

Two settings in `docs/roadmaps/2026-09-20-org-control-plane.md` wait on an
owner: the required-checks ruleset, and harden-runner's egress `block` mode.
Repository content cannot change either. This file supplies the exact values
those settings need, each traced to the run it was read from, so the owner
pastes rather than guesses.

Nothing here activates anything. Authority effect: **none**. Record what you
actually applied in [`REQUIRED_CHECKS_ROLLOUT.md`](./REQUIRED_CHECKS_ROLLOUT.md)
after reading the setting back, never from this file.

Everything below was read from hosted runs of `Quirk-Systems/.github` on
2026-09-21, against `main` at `1263f5008838f743b16ee218046e26dac5c9edd8` or the
pull-request head `2136b88a97f4bfe5f6e01220d1256a90d7c14838`. Each row names its
run. Re-read them if the workflows change.

## Required status check contexts

A GitHub ruleset matches the **check-run name**, which is the job's `name:`, not
the workflow's. `REQUIRED_CHECKS_ROLLOUT.md` predicted `Governance Contracts /
validate`; the observed context is the bare `validate`. A required context that
never matches is not a loud failure — GitHub reports it as expected and pending,
and the pull request simply never becomes mergeable.

| Context | Workflow | File | Runs on a pull request | Safe to require |
| --- | --- | --- | --- | --- |
| `validate` | Governance Contracts | `governance-contracts.yml` | every one, no filters | **yes** |
| `review` | Dependency Review | `dependency-review.yml` | every one, no filters | **yes** |
| `analyze` | CodeQL | `codeql.yml` | only when the base is `main` | **yes, on a `main` ruleset only** |
| `zizmor` | Workflow Lint | `workflow-lint.yml` | only when the diff touches `.github/workflows/**` or `.github/zizmor.yml` | **no — see below** |
| `analysis` | OpenSSF Scorecard | `scorecard.yml` | never; `push` and `schedule` only | **no** |

Observed on pull-request head `2136b88a97f4bfe5f6e01220d1256a90d7c14838`, where
`validate`, `review`, `analyze` and `zizmor` all reported. `analysis` appeared
only on the `push` to `main` at `1263f500…`.

`copilot-pull-request-reviewer` also reports on pull requests. It comes from a
GitHub App rather than a workflow in this repository, so its availability is an
org setting, not something this repository's files control.

### Why `zizmor` is not requireable as it stands

`workflow-lint.yml` filters its `pull_request` trigger to `.github/workflows/**`
and `.github/zizmor.yml`. A pull request touching neither never emits `zizmor`.
Required plus never-emitted means pending forever, so requiring it today would
block every documentation-only or script-only pull request.

Two ways out, owner's choice:

1. **Do not require it.** It still runs and still fails loudly on the pull
   requests that change workflows, which is where it matters.
2. **Remove the two `paths:` filters** so it runs on every pull request, then
   require it. The job is a container pull plus a lint — it took 23 seconds in
   run `35602225653` — so the cost is small and the check becomes honest. This
   is a one-line-per-trigger change to `workflow-lint.yml` that nobody has made;
   ask for it and it is a single pull request.

## Harden-runner egress allowlist

Five workflows run `step-security/harden-runner` in `egress-policy: audit`:
`codeql.yml`, `scorecard.yml`, `dependency-review.yml`, `workflow-lint.yml`, and
`agent-task-dispatch.yml`. Audit mode records destinations and blocks nothing.

The destinations below are the `endpoint called` lines from each job's
harden-runner post-step log — actual connections, not predictions. Do not
confuse them with the much longer `initialized global blocklist` and `fetched
GitHub meta domains` lists in the same log: the first is StepSecurity's
threat-intelligence blocklist and the second is GitHub's published range. Only
`endpoint called` means this job reached that host.

Every job also reaches harden-runner's own two endpoints, which any allowlist
must include or the agent cannot report:

```
agent.api.stepsecurity.io:443
prod.app-api.stepsecurity.io:443
```

| Job | Workflow | Run | Observed destinations |
| --- | --- | --- | --- |
| `review` | Dependency Review | `35600183459` | `github.com:443`, `api.github.com:443` |
| `zizmor` | Workflow Lint | `35602225653` | `github.com:443`, `api.github.com:443`, `ghcr.io:443`, `pkg-containers.githubusercontent.com:443`, `results-receiver.actions.githubusercontent.com:443` |
| `analyze` | CodeQL | `35602870628` | `github.com:443`, `api.github.com:443`, `uploads.github.com:443`, `release-assets.githubusercontent.com:443` |
| `analysis` | OpenSSF Scorecard | `35602870625` | `github.com:443`, `api.github.com:443`, `codeload.github.com:443`, `api.deps.dev:443`, `api.osv.dev:443`, `api.scorecard.dev:443`, `www.bestpractices.dev:443`, `fulcio.sigstore.dev:443`, `rekor.sigstore.dev:443`, `tuf-repo-cdn.sigstore.dev:443`, `oss-fuzz-build-logs.storage.googleapis.com:443`, `results-receiver.actions.githubusercontent.com:443`, `run-actions-2-azure-eastus.actions.githubusercontent.com:443`, `productionresultssa12.blob.core.windows.net:443` |

`agent-task-dispatch.yml` is absent because it triggers on a labeled issue and
no run of it exists to read.

### Three things that will bite

- **Two of Scorecard's hosts are not stable.**
  `productionresultssa12.blob.core.windows.net` is one of twenty numbered log
  storage accounts, and `run-actions-2-azure-eastus` names a region. A different
  run lands on a different index or region. Allowlist
  `productionresultssa*.blob.core.windows.net` and
  `*.actions.githubusercontent.com`, or that job breaks on a run that is
  otherwise identical.
- **One run is one sample.** These lists are what each job happened to need
  once. A CodeQL pack update, a new zizmor image layer, or a Scorecard check
  that was skipped can add a host. Move one workflow to `block` at a time, watch
  it across several runs, and keep the rest on `audit`.
- **Blocking is a behavior change, not a setting.** `egress-policy: block` is set
  in the workflow file, not in org settings, so it lands as a reviewed pull
  request here with its own receipt — unlike the ruleset, which is owner-only.

## What to record afterwards

For each setting actually applied, add a dated row to
[`REQUIRED_CHECKS_ROLLOUT.md`](./REQUIRED_CHECKS_ROLLOUT.md) naming the
repository, the ruleset mode, the exact contexts, the actor, the UTC timestamp,
and the setting read back afterwards. A row written from intent rather than from
a read-back is the thing that rule exists to prevent.
