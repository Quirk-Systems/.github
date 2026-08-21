# Truthful Topology Cut Implementation Plan

> For agentic workers: use `superpowers:subagent-driven-development` to execute each task, `superpowers:test-driven-development` for behavior changes, and `superpowers:verification-before-completion` before reporting a task or pull request complete.

**Goal:** Replace the stale Quirk repository canon, disposition every open manual PR, make proof claims mechanically traceable to commits/paths/digests, introduce stable reusable checks, and deliver one deterministic preference/evidence reference slice.

**Architecture:** `.github` owns the machine-readable topology, PR ledger, evidence schema, validators, and reusable workflow. `quirk-os` adopts the control and records a corrective unverified receipt for the zero-delta PR #42 claim. `quirk-core` owns the versioned preference/evidence candidate contract. `project-scaffold` pins that contract digest and hosts the deterministic runnable reference wedge.

**Tech Stack:** Python 3 standard library, JSON/JSON Schema, Git, GitHub Actions, TypeScript, Vitest, Bun, Next.js repository conventions.

**Spec:** `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`

**Global Constraints:** Work only on feature branches and draft PRs. Reuse `.github` PR #6. Do not merge, close, or edit historical PR state automatically. Do not claim rulesets are active until an owner enables them after an observed check run. A receipt attests to an earlier subject commit; never put a placeholder or predicted SHA into a receipt. Preserve the scaffold/reference, kernel/candidate, and preference-canon boundaries.

## Task 1: Replace organization topology and manual PR canon

**Files:**

- Replace: `.quirk/repositories.json`
- Create: `.quirk/manual-prs.json`
- Create: `.quirk/schemas/repository-inventory.schema.json`
- Create: `.quirk/schemas/manual-pr-ledger.schema.json`
- Create: `scripts/validate_topology.py`
- Create: `tests/test_topology_contracts.py`
- Modify: `docs/REPOSITORY_STRATEGY.md`
- Modify: `profile/README.md`
- Modify: `docs/QUIRK_OS_RENAME_RUNBOOK.md`

**Interfaces and invariants:**

- `python scripts/validate_topology.py --inventory .quirk/repositories.json --pull-requests .quirk/manual-prs.json`
- Inventory IDs are exact `owner/repository` names, unique, and exhaustive for the declared snapshot.
- `scope.expected_organization_repository_count` is `17`; `scope.expected_adjacent_repository_count` is `2`.
- Manual PR keys are exact `owner/repository#number`, unique, and count `27`.
- Required fields include lifecycle, primary class, owner state, canonical responsibility, consumers/dependencies, extraction/retirement rules, deployment/security boundary, and evidence anchors.
- Allowed decisions are `merge`, `revise`, `hold`, `supersede`, and `close`; successors are required for `supersede` and conditional for other states.

**TDD sequence:**

1. Add tests for counts, uniqueness, allowed states, lifecycle/class combinations, complete fields, stale `demo-repository` rejection, and invalid successor handling.
2. Run `python -m unittest tests.test_topology_contracts -v` and capture the expected failure because the validator and complete ledgers do not exist.
3. Implement the validator with `json`, `argparse`, `pathlib`, `re`, and `urllib.parse` only.
4. Replace both ledgers with the 2026-08-21 exhaustive snapshot.
5. Run the unit test and CLI validator to green.
6. Update the human-readable profile and strategy from the validated machine facts.

**Commit:** `feat(governance): replace topology and manual PR canon`

## Task 2: Implement evidence receipts and stable shared checks

**Files:**

- Create: `.quirk/schemas/evidence-receipt.schema.json`
- Create: `.quirk/evidence/README.md`
- Modify: `.gitignore`
- Modify: `.quirk/registry.json`
- Create: `scripts/create_evidence_receipt.py`
- Create: `scripts/validate_evidence_receipts.py`
- Create: `tests/test_evidence_receipts.py`
- Create: `.github/workflows/reusable-evidence-binding.yml`
- Create: `.github/workflows/governance-contracts.yml`
- Create: `docs/governance/EVIDENCE_BINDING.md`
- Create: `docs/governance/REQUIRED_CHECKS_ROLLOUT.md`

**Interfaces and invariants:**

- `python scripts/create_evidence_receipt.py --repository Quirk-Systems/.github --base <sha> --commit <sha> --receipt-id <id> --claim-id <id> --claim <statement> --evidence-path <path> --verification-command <command> --output <path>`
- `python scripts/validate_evidence_receipts.py --repository Quirk-Systems/.github --root . --receipts .quirk/evidence`
- A verified receipt exactly matches the subject diff and SHA-256 bytes at the subject commit.
- Each verified claim cites one or more subject-diff paths.
- Failed/missing commands, forged hashes, non-ancestor subjects, path substitutions, and admission effects fail closed.
- Unverified/retracted receipts require a reason, observations, and external claim references; they cannot imply admission.
- `Governance Contracts / validate` has no path filter and invokes both topology and evidence validators.
- Reusable validation checks out the caller with full history and its own policy source at `job.workflow_sha`.
- In pull-request enforcement mode, the union of verified receipt paths covers every non-receipt path in the base-to-head diff; a later unreceipted change fails the check.
- Rename `registry.preference` to canonical display name `Preference Graph`, retain `Quirk Preference Core` as a deprecated alias, and make the migration explicit in the evidence documentation.

**TDD sequence:**

1. Build a temporary Git repository fixture and write tests for generator output plus one valid two-commit receipt.
2. Add mutation tests for digest, path, ancestry, command result, and admission effect.
3. Run `python -m unittest tests.test_evidence_receipts -v` and capture the expected missing-validator failure.
4. Implement the minimal validator and schema.
5. Add workflows and run their underlying commands locally.
6. Run the complete Python test suite and both validator CLIs.

**Commit:** `feat(governance): bind proof receipts to immutable git evidence`

## Task 3: Record the topology cut's own verified receipt

**Files:**

- Create after Tasks 1–2 commit: `.quirk/evidence/2026-08-21-truthful-topology-cut.json`

**Sequence:**

1. Treat the published Task 1–2 implementation commit as `subject.commit` and the immutable `main` snapshot used for the cut as `subject.base_commit`; the base must be an ancestor but need not be the first parent when the existing PR branch is reconciled by merge commit.
2. Generate the exact name-status diff.
3. Compute SHA-256 from `git show <subject>:<path>` for every present changed path; mark deletions explicitly.
4. Record the exact passing validator/test commands.
5. Validate the receipt against the local branch.
6. Commit the receipt separately.

**Commit:** `docs(evidence): attest truthful topology implementation`

## Task 4: Adopt the control and correct PR #42 in quirk-os

**Files:**

- Create branch from: `Quirk-Systems/quirk-os@main`
- Create: `.quirk/manifest.json`
- Create: `.github/workflows/evidence-binding.yml`
- Create: `.quirk/evidence/2026-08-21-pr-42-zero-delta-correction.json`
- Create after the adoption commit: `.quirk/evidence/2026-08-21-quirk-os-evidence-adoption.json`
- Create: `docs/evidence/PR_42_CORRECTION.md`
- Modify tests only if an executable local receipt adapter is needed; do not change kernel admission status.

**Interfaces and invariants:**

- Caller workflow pins the full commit SHA produced by Task 3.
- Manifest lifecycle is `candidate`, authority is `Quirk-Systems/.github`, and admission is `not_admitted`.
- The correction receipt status is `unverified`; its subject base/head are the exact PR #42 SHAs; changed paths and artifacts are empty; the observation records the zero-file GitHub diff; the retracted external claim is the PR #42 proof statement.

**TDD/verification sequence:**

1. Add the manifest and correction record without changing runtime contracts.
2. Run `pytest -q` to preserve the 32-test baseline.
3. Run the pinned `.github` evidence validator against the repository and correction receipt.
4. Confirm the branch diff contains only manifest, workflow, correction, and documentation files.
5. Create a draft PR; do not revise or close PR #42 automatically.

**Commits:**

- `chore(evidence): correct zero-delta PR 42 proof claim`
- `docs(evidence): attest quirk-os evidence adoption`

## Task 5: Define the canonical preference/evidence candidate contract

**Files:**

- Create branch from: `Quirk-Systems/quirk-core@main`
- Create: `schemas/preference-evidence-wedge.v1.schema.json`
- Create: `examples/preference-evidence-wedge/project-only.json`
- Create: `examples/preference-evidence-wedge/edge-opt-in.json`
- Create: `scripts/validate_preference_wedge.py`
- Create: `tests/test_preference_wedge_contract.py`
- Create: `docs/canon/preference-evidence-wedge.md`
- Modify: `docs/canon/preference-language.md`
- Modify: `README.md`
- Create: `.quirk/manifest.json`
- Create: `.github/workflows/evidence-binding.yml`
- Create after the contract commit: `.quirk/evidence/2026-08-21-preference-evidence-contract.json`

**Interfaces and invariants:**

- `python scripts/validate_preference_wedge.py --schema schemas/preference-evidence-wedge.v1.schema.json examples/preference-evidence-wedge/*.json`
- The only predicate is `presentation.response_density`; the only values are `concise`, `balanced`, and `detailed`.
- Evidence is `explicit_user_statement`, sensitivity is `non_sensitive`, subject is authenticated self, and purpose/surface/task values are exact and non-wildcard.
- `project_only` is the default effect. `create_edge` is an explicit separately approved effect, `system_default` is false, and no consumer/application authority is granted.
- Candidate, proposal, decision, projection, and receipt objects have closed versioned shapes and deterministic SHA-256 content hashes.
- `PreferenceBasis`, implicit evidence, confidence inference, sensitive preferences, and runtime execution are rejected.

**TDD sequence:**

1. Write contract tests for valid project-only and explicit edge-opt-in chains.
2. Add mutations for silence, inferred evidence, wildcard scope, stale decision, effect expansion, non-human decision, and applied/runtime authority.
3. Run `python -m unittest tests.test_preference_wedge_contract -v` and capture the missing-validator/schema failure.
4. Implement the standard-library validator and schema/examples.
5. Run tests and example validation to green.
6. Adopt the pinned shared workflow and create a verified two-commit receipt.

**Commits:**

- `feat(preferences): define preference evidence wedge contract`
- `docs(evidence): attest preference evidence contract`

## Task 6: Ship the preference/evidence runnable reference

**Files:**

- Create branch from: `Quirk-Systems/project-scaffold@main`
- Create: `src/lib/quirk/preference-evidence/contracts.ts`
- Create: `src/lib/quirk/preference-evidence/wedge.ts`
- Create: `src/lib/quirk/preference-evidence/index.ts`
- Create: `src/lib/quirk/preference-evidence/__tests__/wedge.test.ts`
- Modify: `package.json`
- Modify: `src/lib/quirk/governance/authority.ts`
- Modify: `src/lib/quirk/governance/authority.test.ts`
- Create: `scripts/run-preference-evidence-wedge.ts`
- Create: `scripts/check-preference-contract.mjs`
- Create: `vendor/quirk-core/preference-evidence-wedge.v1.schema.json`
- Create: `vendor/quirk-core/PIN.json`
- Create: `docs/quirk/PREFERENCE_EVIDENCE_WEDGE.md`
- Create: `.quirk/manifest.json` if absent, otherwise modify it without granting canonical authority
- Create: `.github/workflows/evidence-binding.yml`
- Create after the wedge commit: `.quirk/evidence/2026-08-21-preference-evidence-wedge.json`

**Interfaces and invariants:**

- `evaluatePreferenceEvidence(input): PreferenceEvaluation` returns a fail-closed eligibility result with machine-readable reasons.
- `proposePreferenceMove(input): ProposedPreferenceMove` requires an eligible explicit preference and records its digest.
- `decidePreferenceMove(move, decision): AuthorizedPreferenceMove | RejectedPreferenceMove` requires an explicit human decision with scope and expiry.
- `executePreferenceMove(authorized): PreferenceEvidenceReceipt` performs a deterministic in-memory projection only within approved scope.
- `confirmLearnedPreference(receipt, confirmation)` creates a learned edge only from explicit human confirmation.
- The vendored contract digest and `quirk-core` source commit are checked on every validation run; this repository owns only the reference implementation.
- The flow handles the authenticated-human actor as an explicit input and proves the consent/state machine; it does not provision Auth.js routes, secrets, persistent credentials, or a production Preference Graph database.

**TDD sequence:**

1. Write tests for the full project-only path, explicit edge opt-in, and explicit rejection.
2. Write adversarial tests for silence, inferred preference, expired validity, purpose mismatch, context mismatch, stale approval, self-expanded scope, and unconfirmed learning.
3. Run the targeted Vitest file and capture the expected missing-module failure.
4. Implement the smallest deterministic flow needed to pass.
5. Run `bun test src/lib/quirk/preference-evidence/__tests__/wedge.test.ts` and the digest pin check.
6. Run `bun run typecheck`, `bun run lint`, and the existing full test command.
7. Run `bun scripts/run-preference-evidence-wedge.ts` and preserve its deterministic JSON output in the PR description.
8. Adopt the pinned shared evidence workflow and create a verified two-commit receipt for the wedge implementation.

**Commits:**

- `feat(preferences): add preference evidence reference wedge`
- `docs(evidence): attest preference evidence wedge`

## Task 7: Cross-repository verification and review handoff

**Files:**

- Modify only PR descriptions and the canonical ledger if final remote SHAs differ from the staged local record.

**Sequence:**

1. Re-run `.github` Python tests, topology validator, and evidence validator from clean worktrees.
2. Re-run `quirk-os` pytest and the pinned evidence validator.
3. Re-run the `quirk-core` contract mutation suite, example validator, and pinned evidence validator.
4. Re-run targeted/full scaffold tests, typecheck, lint, digest check, deterministic wedge demo, and pinned evidence validator.
5. Inspect `git diff --check`, `git status --short`, exact base/head SHAs, and changed-file lists for all four branches.
6. Request a final code/evidence review across the four PRs.
7. Update draft PR bodies with commands, outputs, subject SHAs, receipt paths, known owner-only rollout actions, and links between the topology, correction, contract, and reference PRs.
8. Report the exact remaining human decisions: merge approval, historical PR state changes, ruleset Evaluate/Active rollout, named repository owners, and commerce-candidate selection.

**Completion rule:** Do not say “complete,” “enforced,” “admitted,” or “verified” without fresh command output or an observed GitHub check supporting that exact scope.
