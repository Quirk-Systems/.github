# Truthful Topology Cut

Status: implementation contract
Authority: `Quirk-Systems/.github`
Cut date: 2026-08-21 UTC
Scope: every visible `Quirk-Systems` repository, every open non-Dependabot pull request, and the two personal Quirk commerce candidates whose names and product surfaces create a material boundary question

## Decision

This cut replaces narrative portfolio memory with three machine-verifiable facts:

1. `.quirk/repositories.json` is the complete repository inventory for this snapshot.
2. `.quirk/manual-prs.json` is the complete disposition ledger for open human/agent-authored pull requests at this snapshot.
3. `.quirk/evidence/*.json` binds proof claims to an earlier subject commit, its exact diff paths, and SHA-256 artifact digests.

No repository becomes canonical, active, admitted, or production-proven because it appears in an inventory, passes a content check, or has a generated receipt. Those are separate human decisions.

## Canonical topology

- `Quirk-Systems/.github` is the public organization canon and shared workflow source.
- `Quirk-Systems/.github-private` is the private governance boundary.
- `Quirk-Systems/project-scaffold` is the public reference application scaffold. It is not Quirk OS.
- `Quirk-Systems/quirk-os` is the candidate kernel boundary. It is implemented enough to evaluate, but it is not admitted or production-proven.
- `Quirk-Systems/quirk-core` is a candidate doctrine boundary until it has a distinct owned contract and consumer; otherwise its doctrine folds into the admitted kernel canon.
- Empty or name-only repositories remain reserved. A name is not a capability.
- `bryansayler/quirk-commerce` and `bryansayler/quirk-beauty-store` remain adjacent candidates, not organization canon. One must be selected and assigned payment/PII ownership before either is treated as an operating commerce boundary.

The exhaustive classification, responsibility, owner state, consumers, dependencies, deployment/security boundary, extraction trigger, retirement condition, and evidence anchors live in `.quirk/repositories.json`. Human-readable tables in the repository strategy are projections of that file.

## Pull-request cut

`.quirk/manual-prs.json` records every open non-Dependabot pull request visible in `Quirk-Systems` at the cut:

- `merge`: the change is topologically sound and reviewable after current validation;
- `revise`: keep the PR, but correct evidence, isolate scope, or repair checks;
- `hold`: preserve the candidate while a named human authority decision remains open;
- `supersede`: preserve the record but replace the implementation with a narrower successor;
- `close`: no independently reviewable delta or no satisfiable current action remains.

The ledger is a recommendation and historical control record. It does not merge or close a PR by itself. A later state change must update the ledger with the acting human, timestamp, and successor or closing evidence.

## Proof contract

Evidence receipts use a two-commit protocol:

1. The subject commit contains the implementation being claimed.
2. A later receipt commit records the subject base SHA, subject SHA, exact changed paths, per-path state and SHA-256 digest, scoped claim statements, and verification commands.

This avoids an impossible self-reference: a commit cannot truthfully contain its own final SHA.

For a `verified` receipt, validation fails unless:

- base and subject are full 40-character Git commit IDs;
- the base is an ancestor of the subject and the subject is an ancestor of the checked-out head;
- receipt paths exactly equal `git diff --name-only <base>..<subject>`;
- every present path digest equals the bytes at `<subject>:<path>`;
- every deleted path is explicitly marked deleted and has no digest;
- every claim names at least one evidence path and all named paths are in the subject diff;
- at least one verification command is recorded and every result is `pass` with exit code `0`;
- `admission_effect` is `none`.

For an `unverified` or `retracted` receipt, validation requires a reason, at least one observation, and at least one external claim reference. Empty diffs are allowed because the absence of a claimed implementation is itself the observation. These statuses cannot contain language that grants admission.

The validator establishes artifact identity and recorded test outcomes; it does not independently prove a product claim is semantically complete. Reviewers still judge whether the evidence supports the claim.

## Stable checks

The shared workflow is intentionally stable:

- fixed workflow and job names;
- `pull_request` and `push` triggers with no path filters;
- read-only contents permission;
- full Git history for ancestry and diff validation;
- validator source checked out from the same `.github` commit that supplies the reusable workflow;
- no network service or mutable package dependency in the validator path.

Caller repositories pin the reusable workflow to a full `.github` commit SHA. Branch protections or repository rulesets should first run the check in Evaluate mode and only become Active after the exact emitted check name has been observed on a pull request. Content changes cannot configure owner-only repository settings, so the rollout record names that remaining action rather than claiming it happened.

## Preference/evidence reference wedge

The end-to-end wedge has two explicit owners. `quirk-core` owns the versioned candidate contract because it already owns Preference Graph vocabulary and storage doctrine. `project-scaffold` owns the deterministic runnable reference because it is an application scaffold, not canon. The slice cites reviewed `quirk-os` control-plane patterns as lineage but has no runtime dependency on its unadmitted or draft contracts.

The wedge must demonstrate one bounded flow:

1. a stated preference is captured with purpose, context, authority, validity, and provenance;
2. a candidate action cites that preference as evidence;
3. no action is authorized from silence, an expired or scope-mismatched preference, or system inference alone;
4. an explicit human decision authorizes or rejects the proposed move;
5. execution is simulated inside the authorized scope;
6. a receipt binds the decision, resulting projection, and evidence digests;
7. only explicit human confirmation may write a learned preference edge.

The first preference is deliberately narrow and non-sensitive: response density for repository-audit reports on the reference surface, with `concise`, `balanced`, or `detailed` as the only values. The default effect is `project_only`; a reference-backed Preference Edge requires a separate exact opt-in and remains recorded but unapplied.

The wedge is fail-closed and deterministic. It is not an autonomous preference learner, production executor, admission of Intent Shaper, `PreferenceBasis`, or a production migration of the canonical preference store.

## Out of scope

- direct merges to `main`;
- closing or merging the historical pull requests automatically;
- activating repository rulesets without an observed check run and owner authority;
- admitting `quirk-os`, `quirk-core`, Intent Shaper, or any reserved repository;
- choosing between the duplicate commerce candidates;
- inventing named owners where the inspected repositories expose none.

## Acceptance

The cut is complete when:

- the inventory validates and contains exactly the 19 in-scope repositories (17 organization repositories plus 2 adjacent commerce candidates);
- the manual PR ledger validates and contains exactly the 30 open non-Dependabot PRs observed on 2026-08-21 after the three cross-repository implementation PRs were opened;
- stale repository names such as `demo-repository` are rejected;
- evidence validator mutation tests fail for changed paths, forged digests, non-ancestor commits, missing proof commands, and admission language;
- `.github`, `quirk-os`, and `project-scaffold` run the stable evidence check from a pinned revision;
- the PR #42 correction receipt is explicitly `unverified` and records its zero-file base-to-head diff;
- the `quirk-core` contract/examples and the digest-pinned `project-scaffold` implementation pass happy-path and adversarial tests;
- each repository change is delivered through a reviewable draft PR, with current commands and commit SHAs in its body.
