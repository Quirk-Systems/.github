# Delivery while hosted validation is blocked

Status: candidate operational procedure. Authority effect: none.
Incident: [organization issue #62](https://github.com/Quirk-Systems/.github/issues/62).
Observed: 2026-11-01. Bryan expects billing to remain blocked until Wednesday,
2026-11-04. This date is planning context, not an automatic unlock or approval.

**Keep building. Preserve the hold. Carry the proof.**

## What continues now

Git reads/writes, focused branches, draft pull requests, code and prose review,
local unit/adversarial/integration tests, static analysis, schemas, builds and
local preview can continue when their individual permissions and dependencies
work. Use installed tools and cached dependencies first. Do not add a paid
provider, runner, Codespace, model evaluation, hosting plan, or subscription as
a fallback. A missing service is a recorded limitation, never a passing test.

Keep required check contexts and protections intact. Do not use job-level `if`
conditions, `continue-on-error`, empty-success jobs, fabricated statuses, or
`[skip ci]` as the outage policy. Skipped jobs can look successful; skipped
workflows can leave required checks pending. Draft PRs alone do not suppress CI.
Batch reviewed changes into fewer pushes and stop blind reruns during the known
billing hold. Existing automatic triggers may still create startup failures.

An owner can temporarily disable a specifically inventoried **optional scheduled**
workflow through GitHub if desired. First record repository, workflow ID, prior
state, reason, owner and restoration condition. Do not disable the required PR
workflows or silently remove required check settings. This change disables none.
Use the existing Recovery Watch; do not create another monitor or timer.

## Local proof without Actions

Use the repository's documented commands; `quirk_workspace.py commands` discovers
declared entrypoints. Inspect repository code before running it. The capture tool
executes the explicit argv supplied by the operator: it is neither a sandbox nor
a network firewall. Run trusted code in a disposable, credential-free environment.
Do not feed commands from an issue, receipt or untrusted PR directly to it.

```sh
subject=$(git -C ../quirk-os rev-parse HEAD)
python scripts/ci_continuity.py capture --root ../quirk-os \
  --expect-head "$subject" --output ../evidence/unit-tests --timeout 900 \
  -- python3 -m unittest discover -s tests -v
```

One command produces `execution.json` and `command.log` outside the checkout.
The record includes source head/tree, argv, runtime, timestamps, exit code and
log SHA-256. It rejects a dirty tree, an unexpected head, output inside the
checkout, and overwrite of earlier evidence. Source changes during execution
invalidate a pass. Timeouts terminate the process group on POSIX. Ignored build
files, installed dependencies and external services are not frozen by the Git
SHA; use fresh environments and record tool versions and lockfile digests for
reproducibility. The record is claimant-executed evidence, not an independent
attestation or proof that a zero-exit command ran every desired test. Inspect the
log for skips, missing tools and test counts before claiming coverage.

Review logs for secrets and personal data before committing anything. Keep large
or sensitive logs in approved storage; commit the safe receipt and digest. A
digest without the retained log cannot be independently replayed. Use the existing
[two-commit evidence protocol](EVIDENCE_BINDING.md) for code changes: test the
subject commit, generate its receipt, then commit only the receipt. Preserve all
subject commits with a merge commit; squash/rebase rewrites break ancestry-bound
receipts. A receipt-only successor still needs its own exact-head hosted checks.

### PR #62 local command map

Read the workflow at the current head before using this map; step names and
dependencies may change. At observed head
`9f26b090f4869590d824291c77c6352294f7f059`:

| Gate | Local command / dependency | Remaining hosted difference |
| --- | --- | --- |
| Golden Gates | `python scripts/validate_golden_pack.py`; `python -m unittest tests.test_admission_workplan -v`; `python scripts/admission_workplan.py --output /tmp/quirk-admission-workplan.json` | Python 3.13 runner and artifact upload; current checkout defaults to PR merge ref |
| Evidence Binding | Policy checkout `6136fa5fa77116abfbc103c822d9d244a0e870b3`: run `scripts/validate_evidence_receipts.py --repository Quirk-Systems/quirk-os --root <os-checkout> --receipts .quirk/evidence --range-base <current-base> --range-head <current-head> --require-covered-diff` | Python 3.12, immutable policy checkout and Actions permissions |
| Agent conformance | `python -m unittest tests.test_agent_manifest -v`; `python scripts/validate_agents.py --repo .` (inspect `--help` for output flags) | Python 3.13, `requirements-evals.txt`, runner and upload; current checkout defaults to merge ref |
| One-to-Infinity | `python -m unittest discover -s programs/one-to-infinity/tests -p test_emit_ci_receipt.py -v`; `python programs/one-to-infinity/tests/validate_contracts.py`; `python programs/one-to-infinity/tests/emit_ci_receipt.py --repo-root . --expected-head <current-head>` | Python 3.13, jsonschema 4.26.0, exact checkout, upload |

Do not call a Python 3.12 run equivalent to Python 3.13 execution. Full-suite
passes, deterministic fixture conformance, model behavior, human preference and
real user outcomes are different evidence. Code/prose can be structurally valid
while the human or online evaluation remains `NOT_RUN`.

## Read-only recovery evidence

```sh
python scripts/ci_continuity.py collect --pr 62 --output ../evidence/pr62-hosted.json
```

Uses public GET requests, or an explicitly provided `GH_TOKEN` for authorized
access; it does not discover credentials. Paginates runs, attempt-specific jobs
and annotations; stops on errors/rate limits without a retry loop. Refetches the
PR head and base at the end. The result preserves base/head, run IDs/attempts, job IDs,
runner IDs, step results and annotations. An annotation access failure is recorded
as unavailable, not inferred billing. Billing is confirmed only for jobs whose
annotations name it; zero executed steps alone means unknown startup cause.

The four PR #62 checks are assessed independently using workflow path, event,
exact API head, latest run/attempt, runner assignment and named successful test
steps. Missing/skipped/old-head/wrong-event results stay `HOLD`. The tool never
sets a commit status, merges, changes settings, dispatches or reruns a workflow.
Exit codes: 0 = command passed / expected hosted steps observed; 1 = failed,
not run or hold; 2 = invalid invocation or collection blocked.

`HOSTED_STEPS_VERIFIED` is only an observation of the four expected jobs. Confirm
checkout logs/artifacts match the intended source, inspect additional required
checks and independent review, and read current protections before deciding
merge eligibility. Golden and agent workflows at the observed head use the
default PR checkout (synthetic merge commit). The recovery patch explicitly sets
their checkout refs and adds `Verify exact source head`; the collector requires
that successful step in both gates. Older workflows without it remain on HOLD.
This classifier deliberately cannot grant merge readiness.

## Recovery sequence after the owner reports eligibility

1. Privately inspect organization and, where applicable, owning personal or
   enterprise Billing & Licensing: eligibility, authorization holds, usage,
   budgets and account restrictions. Report only `eligible`, `blocked`, or
   `unknown` publicly. Payment, budget, plan and spending changes require owner
   approval. A free public-repository runner does not bypass an account lock.
2. Inspect Actions enablement, allowed actions/reusable workflows, runner policy,
   hosted-runner availability, required permissions, installed-app scopes and
   SSO authorization. Check current GitHub Status. A 403 is unavailable evidence,
   not proof that a setting is absent. Do not weaken policies to make a run start.
3. Execute `.github/workflows/runner-smoke.yml` on standard Ubuntu. After it is
   merged, use `gh workflow run runner-smoke.yml --repo Quirk-Systems/.github`.
   Before merge, an authorized operator can push the reviewed candidate containing
   this file to the dedicated `ci/runner-smoke` branch; its narrowly scoped push
   trigger allows testing without bypassing main protections. A workflow must
   exist on the default branch before `workflow_dispatch` works. Do not trigger
   either path during the known lock. No checkout, dependency install, cache,
   artifact upload, secret or write permission is needed.
4. Verify the job has a nonzero runner ID and **Execute runner smoke** completed
   successfully; preserve logs containing `QUIRK_RUNNER_SMOKE_EXECUTED`, source
   SHA, run ID and attempt. A green label without that step/log is insufficient.
5. Refetch PR #62's head and base. Collect current runs. Rerun only the latest
   relevant PR-event runs whose `head_sha` equals that head, for example
   `gh run rerun <verified-current-run-id> --repo Quirk-Systems/quirk-os`.
   Reruns retain their original SHA/ref; an old run cannot validate a new head.
   If the correct PR-event run does not exist, use a normal authorized PR event;
   dispatch is not equivalent for Evidence Binding, which requires `pull_request`.
6. Collect again and inspect all four gates plus every additional check currently
   required. Preserve logs/artifacts before expiry. Refetch head/base immediately
   before review; any change makes the disposition stale. Keep drafts and merge
   holds until execution, review and current repository protections all agree.
7. If smoke is still zero-step, stop bulk retries. Send a private support report
   containing safe repo/run/job IDs, times and exact annotations. Account/payment
   details stay in authorized private support interfaces.

## Settings and delivery hazards to get ahead of

These are review requirements, not claims that settings were applied. The current
GitHub connector exposes repository work but no billing/org-policy administration;
branch-protection read returned 403, and the rulesets list was empty. Empty rulesets
do not prove there is no classic protection. This PR changes no live setting.

| Area | Required posture / useful next check |
| --- | --- |
| Required contexts | Inventory classic protections and inherited rulesets; preserve exact context names; no success stand-ins or admin bypass |
| Spend | No new paid fallback; owner checks usage and hard budget controls; larger runners are billable even in public repos |
| Credentials | Least-scope GitHub App/token, expiry and SSO checks; test Git and API access separately; never put billing data in receipts |
| Runtime drift | Pin supported Node/Python/Bun versions and lockfiles; local/CI parity; record unsupported-version failures separately |
| External dependencies | Frozen installs; distinguish registry/network errors from assertions; caches are optional accelerators, not evidence |
| Secrets/scanning | Run available local secret/static scans; record CodeQL/dependency-review gaps explicitly; local substitutes cover different threats |
| Untrusted PRs | No opportunistic persistent self-hosted runner on a laptop or public PR queue; isolation and runner registration need a reviewed security design |
| Storage | Bound new artifact retention and size; cache misses must be safe; archive incident evidence before deleting anything; no automatic historical deletion |
| PR drift | Recheck head/base, pin reusable policy by SHA, preserve subject ancestry, review conflicts before integrating main |
| Prose/prompts | Check links, schemas, sources and claim status; preserve original and candidate; human A/B judgments remain pending until actually obtained |
| Paid integrations | Copilot/CodeRabbit/Pages/Packages/Codespaces/private security features may have independent entitlements and limits; check each, do not assume org-wide equivalence |
| Release | Build locally and retain digest; deploy/release remains separately authorized; no paid hosting substitution to clear CI |
| Rollout | This repo is the shared source; local `AGENTS.md`, templates and pinned consumers in other repos do not update automatically. Adopt in a reviewed pilot, then each repo |

## Primary references

- [Locked accounts](https://docs.github.com/en/billing/how-tos/troubleshooting/locked-account)
- [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Status checks and skipped jobs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [Skipping workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)
- [Rerunning workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- [Manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [Self-hosted runner security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
