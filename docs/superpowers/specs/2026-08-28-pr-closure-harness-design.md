# PR Closure Harness v0.1 Design

**Status:** candidate design only  
**Owner:** `Quirk-Systems/.github`  
**Program issue:** `Quirk-Systems/.github#13`  
**Date:** 2026-08-28  
**Scope classification:** `MATERIAL_SCOPE_CHANGE`  
**Authority effect:** `none`

## 1. Objective

Build one organization-owned, read-only **PR Closure Harness** that turns a pull request into a deterministic exact-head evidence packet and one bounded disposition:

```text
READY_FOR_MERGE
READY_FOR_HUMAN_ADMISSION
REVISE
HOLD_CANDIDATE
SUPERSEDE
CLOSE_AS_REDUNDANT
```

The harness does not make the human decision. It makes the current decision surface finite, reproducible, exact-head bound, and stale when the head changes.

The first release ends at:

```text
ELIGIBLE_FOR_HUMAN_REVIEW
```

It does not merge, close, approve, admit Canon, activate runtime, release, deploy, publish, provision a provider, mutate a database, transfer ownership, or perform financial, physical, personal-identity, or irreversible action.

## 2. Architectural decisions

### 2.1 Organization governance owns the harness

`Quirk-Systems/.github` owns the schemas, validators, reusable workflow, metric pack, fixtures, and documentation because the harness governs cross-repository review behavior. It does not own the product, runtime, data, or canonical contracts inspected by the harness.

### 2.2 Every evaluation subject is immutable

The consequential subject is:

```text
repository + pull_request + base_sha + head_sha + changed_paths
```

Branch names and PR numbers are locators. They are not evidence identities. A new commit makes the prior Passport, Dossier, review, and Warrant stale for current action.

### 2.3 Repository ownership is local and explicit

Each participating repository supplies:

```text
.quirk/repository-boundary.v1.json
```

The file declares the repository purpose, responsibilities, prohibited responsibilities, authority ceiling, supported runtimes, required checks, and related repositories. The Closure Harness reads that file from the exact PR head.

The harness does not maintain a manual organization topology ledger. When the file is absent or invalid, owner status is `UNRESOLVED` and the maximum disposition is `HOLD_CANDIDATE`.

### 2.4 Shadow mode is read-only

The reusable workflow receives only:

```yaml
permissions:
  contents: read
  pull-requests: read
```

It may read the exact checkout and PR review metadata, emit logs, write a GitHub job summary, and upload a generated artifact. It may not comment, label, approve, mark ready, merge, close, dispatch another workflow, write repository contents, create a deployment, or access provider credentials.

### 2.5 Proof is typed, not implied

Every proof result uses one of:

```text
PASS
FAIL
NOT_EXECUTED
NOT_OBSERVED
```

A skipped job, zero-job workflow, absent fixture, unavailable review query, or local run from another SHA is never converted to `PASS`.

### 2.6 Capability and evidence remain non-authoritative

The harness enforces these separations:

```text
capability != authority
mergeable != safe
candidate location != Canon
receipt locator != receipt resolution
synthetic fixture != real outcome
telemetry != evidence of value
workflow green != admission
```

## 3. Core data model

### 3.1 `RepositoryBoundary`

Required fields:

```text
schema_version
repository
owner
purpose
responsibilities[]
prohibited_responsibilities[]
authority_ceiling
supported_runtimes[]
required_checks[]
related_repositories[]
```

The object is closed. Unknown fields fail validation.

### 3.2 `PRSubject`

Required fields:

```text
repository
pull_request
base_sha
head_sha
merge_base_sha
changed_paths[]
head_tree_sha
```

All SHAs are lowercase, full 40-character Git object IDs. Paths are normalized repository-relative POSIX paths. Absolute paths, `..`, NUL bytes, and backslashes fail validation.

### 3.3 `ScopeDelta`

The harness records one classification:

```text
NO_DELTA
CONTEXT_ONLY
IMPLEMENTATION_DETAIL
MATERIAL_SCOPE_CHANGE
AUTHORITY_CHANGE
BOUNDARY_ONLY
INSUFFICIENT_EVIDENCE
```

Material or authority changes stop automatic progression and add an explicit required-next action.

### 3.4 `BlockerRecord`

Each blocker contains:

```text
id
severity
invariant
symptom
reproduction
cheapest_disproof
owning_paths[]
status
source
```

`status` is one of `OPEN`, `REPAIRED_UNVERIFIED`, `VERIFIED_CLOSED`, or `NOT_REPRODUCED`. A prose claim cannot mark a blocker closed.

### 3.5 `ProofResult`

Each check records:

```text
id
status
command
runner
observed_at
subject_head_sha
artifact_locator
limitations[]
```

A command is required for executed checks. `NOT_EXECUTED` and `NOT_OBSERVED` require a reason and may not carry an artifact locator.

### 3.6 `AuthorityBoundary`

The boundary is closed and explicit:

```text
ceiling
merge_granted: false
canon_granted: false
runtime_granted: false
release_granted: false
deployment_granted: false
publication_granted: false
provider_write_granted: false
```

Version 0.1 structurally fixes every consequential grant to `false`.

### 3.7 `Disposition`

The deterministic compiler may emit only:

```text
READY_FOR_MERGE
READY_FOR_HUMAN_ADMISSION
REVISE
HOLD_CANDIDATE
SUPERSEDE
CLOSE_AS_REDUNDANT
```

`READY_FOR_MERGE` remains a recommendation for human review, not merge authority.

## 4. Disposition rules

The compiler applies the following precedence from most restrictive to least restrictive:

1. `SUPERSEDE` when repository ownership is invalid and a named successor/extraction path exists.
2. `CLOSE_AS_REDUNDANT` when an exact successor fully covers the PR and preservation requirements are recorded.
3. `REVISE` when a reproducible blocker is open or a required check is `FAIL`.
4. `HOLD_CANDIDATE` when ownership is unresolved, evidence is stale, a check is `NOT_EXECUTED` or `NOT_OBSERVED`, an independent reviewer is missing, or candidate boundaries forbid promotion.
5. `READY_FOR_HUMAN_ADMISSION` when all required proof is current and green but a separate admission decision is required.
6. `READY_FOR_MERGE` only when the repository boundary allows ordinary integration, all required proof is current and green, review threads are resolved, an independent review is present, and no admission/runtime/authority decision is bundled into the merge.

A blocker list is monotonic: a more permissive result cannot override a stricter active condition.

## 5. Code Ontology Companion seam

The harness emits a deterministic ontology projection from exact-head data:

### Entities

```text
Repository
RepositoryBoundary
PullRequest
Commit
Path
Contract
EvidenceReceipt
ProofResult
Reviewer
Decision
Authority
Runtime
Projection
Provider
```

### Relations

```text
OWNS
PROHIBITS
CHANGES
DEPENDS_ON
CITES
VERIFIES
REVIEWS
SUPERSEDES
PROJECTS_TO
REQUIRES_AUTHORITY
STALE_AFTER
```

The ontology output is a structural aid. It must not claim TypeScript execution, runtime reachability, production behavior, admission, or authority from relation consistency.

## 6. EvalDossier seam

Every run emits one `eval-dossier.v1.json` containing:

```text
repository
pull_request
base_sha
head_sha
external_audience
evaluator_identity
rubric_id
rubric_version
nonce
commands[]
artifacts[]
limitations[]
withheld_claims[]
passport_digest
disposition
```

`external_audience`, `evaluator_identity`, and `nonce` are mandatory. Synthetic evidence cannot satisfy a real-world outcome claim. The Dossier cannot infer economic value, product-market fit, Canon, admission, or authority.

## 7. Plugin Eval seam

A custom deterministic metric pack consumes the validated Passport and emits stable checks and metrics.

### Checks

```text
closure.exact_head_bound
closure.owner_valid
closure.evidence_current
closure.required_checks_observed
closure.negative_fixtures_present
closure.claim_evidence_parity
closure.no_authority_leakage
closure.no_external_writes
closure.review_threads_clear
closure.disposition_complete
```

### Metrics

```text
closure.open_blocker_count
closure.unobserved_check_count
closure.stale_evidence_count
closure.negative_fixture_count
closure.open_review_thread_count
closure.external_write_count
closure.required_next_count
```

The metric pack supplements Plugin Eval output. It cannot overwrite the core score or summary.

## 8. Cloudflare boundary

The Closure Harness does not deploy to Cloudflare. For `quirk-run` candidates it may consume hermetic evidence proving:

```text
wrangler types
TypeScript validation
bundle construction
behavioral fixture execution
authority-change pause behavior
retry idempotency
zero external bindings
```

It must distinguish bundle/type proof from runtime behavior proof. Production route creation, Worker deployment, Durable Object/Workflow activation, KV, D1, R2, Queue, service binding, browser binding, AI binding, and world-state mutation remain outside version 0.1.

## 9. Sentry observability boundary

Version 0.1 defines but does not transmit candidate observability events:

```text
closure_harness.completed
closure_harness.blocked
closure_harness.stale
closure_harness.scope_paused
closure_harness.authority_paused
```

Every event binds `repository`, `pull_request`, `head_sha`, `passport_digest`, and `disposition`. Events prohibit source content, request bodies, tokens, secrets, personal data, provider credentials, and arbitrary exception strings. `release` equals the exact harness commit; `environment` is `fixture`, `ci-shadow`, or `local`.

No Sentry organization, project, DSN, release, environment, alert, or source-map upload is created by this design.

## 10. Agent Ready boundary

Agent Ready is an external public-surface evaluation, not a repository admission gate.

The 2026-08-28 scan `4L8pJOcmAE` for `https://quirk.systems` is retained as a baseline with:

```text
status: failed
pages_scanned: 0
vercel_score: 0
llms_txt_score: 0
```

Observed gaps include absent `llms.txt`, sitemap, and `AGENTS.md`, plus an HTTPS handshake timeout. The scan does not prove which repository, provider, DNS record, certificate, or deployment owns the failure. An owner-specific successor must establish the serving boundary before changing site files or infrastructure.

## 11. Failure behavior

The harness fails closed when:

- event repository, PR number, base SHA, or head SHA is absent;
- checked-out `HEAD` differs from the event head;
- the repository boundary is absent, malformed, or names another repository;
- changed paths escape the repository root;
- evidence cites another head without an explicit historical classification;
- a required check is missing, skipped, or unobserved;
- blockers and disposition conflict;
- an authority field is true;
- an EvalDossier lacks audience, evaluator, nonce, limitations, or withheld claims;
- an ontology relation references an unknown entity;
- a metric-pack result contains unstable IDs or attempts to overwrite the core evaluation.

Controlled failure produces a valid Passport with a restrictive disposition whenever the subject can still be identified. Invalid identity fails the workflow without emitting a misleading Passport.

## 12. Test strategy

Version 0.1 uses Python 3.12 standard library, JSON Schema documents as contracts, canonical JSON, and hermetic fixtures.

Required positive fixtures:

1. ordinary repository change eligible for human merge review;
2. boundary-only candidate eligible for human admission review;
3. explicitly held runtime candidate with all fixture proof present.

Required adversarial fixtures:

1. head changes after proof;
2. `mergeable=true` with an open P1 blocker;
3. candidate path presented as Canon;
4. synthetic outcome presented as real-world outcome;
5. receipt locator with mismatched bytes;
6. repository boundary naming another owner;
7. skipped workflow presented as passed;
8. unresolved review thread omitted from prose;
9. authority field smuggled through an unknown key;
10. path traversal in changed paths or artifact locators;
11. telemetry presented as proof of value;
12. the seductive false version: every check is green, but the PR combines a boundary admission decision with runtime activation.

Every mutation must fail for the intended invariant, not merely because parsing crashed.

## 13. Rollout

### Phase 0 — plan-only

Land this design and its implementation plan as documentation. No checks or rulesets change.

### Phase 1 — local fixtures

Implement schemas, validators, compiler, ontology projection, EvalDossier generator, metric pack, and tests. No GitHub API access.

### Phase 2 — PR shadow workflow

Run on the Closure Harness PR itself with read-only permissions. Emit artifact and job summary only.

### Phase 3 — one consumer pilot

Pilot on `Quirk#5` after its secret incident has a clean successor head. Compare harness output with an independent human review.

### Phase 4 — organization Evaluate mode

After explicit admission, add the reusable caller to selected repositories. Observe positive and negative behavior before any required-check activation.

### Phase 5 — Active gate

Requires a separate owner-authorized change. It is not authorized by this design.

## 14. Non-goals

Version 0.1 does not:

- repair every PR;
- merge or close PRs;
- infer semantic correctness from test counts;
- implement a general code ontology engine;
- deploy Cloudflare resources;
- provision Sentry;
- modify Supabase;
- repair `quirk.systems` infrastructure;
- create a central Canon database;
- replace independent human review;
- automatically promote a candidate disposition;
- evaluate Dependabot major-version migrations;
- reopen Quirkroot as an active architecture boundary.

## 15. Success criteria

The design is successfully implemented when one exact-head PR run produces:

1. a schema-valid Proof Passport;
2. a schema-valid EvalDossier with audience, evaluator, nonce, limitations, and withheld claims;
3. a valid ontology projection with no dangling entity references;
4. deterministic Plugin Eval metric-pack output;
5. a restrictive disposition consistent with blockers, ownership, evidence, review state, and candidate authority ceiling;
6. zero repository/provider/runtime writes;
7. adversarial fixtures proving stale evidence, ownership drift, authority leakage, skipped checks, path traversal, and seductive green-but-unauthorized promotion all fail closed.