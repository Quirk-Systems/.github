# Quirk Systems Repository Strategy

Status: **Proposed foundation**
Authority: `Quirk-Systems/.github`
Applies to: every repository in the Quirk Systems organization

## 1. Strategic position

Quirk Systems is not managed as a loose collection of applications. It is managed as a stateful human–agent operating system with one governed portfolio of repositories.

The repository ecosystem must preserve continuity between:

- human intent
- canonical concepts and rules
- proposed and authorized work
- agent execution
- evidence and review
- accepted world-state changes

The operating loop is:

```text
async preparation
→ real-time session
→ async execution
→ real-time review
→ persistent world update
```

Every repository must clearly declare which part of this loop it serves and which canonical authority it consumes.

## 2. Immediate naming decision

The implemented kernel is currently `Quirk-Systems/project-scaffold`. The private `Quirk-Systems/quirk-os` repository is an empty placeholder.

The intended cutover is:

1. Rename the empty `quirk-os` placeholder to `quirk-os-reserved`.
2. Archive the renamed placeholder after confirming it contains no unique settings, secrets, environments, releases, packages, or branch rules.
3. Rename `project-scaffold` to `quirk-os`.
4. Update manifests, deployments, badges, local remotes, integrations, and policy references.
5. Verify GitHub redirects, CI, Dependabot, webhooks, environments, and deployment providers.

The operational checklist is maintained in `docs/QUIRK_OS_RENAME_RUNBOOK.md`.

## 3. Canonical repository classes

Every repository receives exactly one primary class. Secondary facets are allowed, but they do not replace the primary responsibility.

| Class | Responsibility |
| --- | --- |
| `canon` | Organization-wide truth, semantic authority, policy, and shared governance |
| `kernel` | Shared runtime, orchestration, state transitions, and system-level execution |
| `registry` | Governed inventories, projections, provenance, evidence, and query surfaces |
| `interface` | Human-facing operational surface over canonical or runtime state |
| `connector` | Integration with an external platform, protocol, provider, or data source |
| `instrument` | A bounded executable capability with explicit inputs and outputs |
| `realm` | A domain-specific world, product, or experience consuming core contracts |
| `reference` | A gold-standard implementation intended for reuse or comparison |
| `lab` | Time-bounded experimental work that is not yet canonical |
| `sandbox` | Disposable, non-canonical testing or demonstration environment |

## 4. Current portfolio classification

| Repository | Visibility | Primary class | Current state | Strategic action |
| --- | --- | --- | --- | --- |
| `.github` | public | canon | active | Keep as public constitutional authority and shared workflow source |
| `.github-private` | private | canon | active | Define internal policy, sensitive templates, and private organization controls |
| `project-scaffold` | public | kernel | active | Rename to `quirk-os`; preserve history, PRs, issues, and implementation |
| `quirk-os` | private | sandbox | empty placeholder | Rename to `quirk-os-reserved`, verify, then archive |
| `quirk-data` | private | registry | reserved | Keep as a boundary until a second consumer or security/release boundary justifies extraction |
| `quirk-me` | private | interface | reserved | Keep as identity, preference, consent, and memory boundary until independently deployable |
| `quirk-run` | private | kernel | reserved | Keep as execution and containment boundary until workers/CLI/scheduled agents become real consumers |
| `quirk-feed` | public | interface | active | Grow into the preparation, ingestion, discovery, and derived-knowledge surface |
| `quirk-generator` | public | instrument | active | Treat as a bounded visual-generation instrument, not a second kernel |
| `quirk-beauty` | private | realm | active proof | Keep only while it validates reusable realm and deterministic-transformation patterns |
| `quirk-pet` | private | realm | active proof | Use as a reference for time-based state, actions, consequences, and derived status |
| `quirk-town` | private | realm | active proof | Use as a reference for identity, directory, residency, and claimable-space patterns |
| `demo-repository` | private | sandbox | active demo | Mark non-canonical and archive when no longer needed for GitHub feature testing |

## 5. Repository creation gate

No new repository should be created merely because a concept has a name.

A repository proposal must answer:

1. What unique responsibility will this repository own?
2. Why can the work not remain a module, package, folder, feature flag, branch, or experiment in an existing repository?
3. What is the primary repository class?
4. What is the source of truth, and what is only a projection?
5. Who owns the repository and its decisions?
6. What data, permissions, secrets, or deployment boundary requires separation?
7. Is there a real second consumer?
8. Does it require an independent release cadence?
9. What is the success condition?
10. What is the retirement or merge-back condition?
11. How does it participate in the Quirk operating loop?

The default answer is **do not create the repository yet** unless one of these extraction triggers is true:

- a second independent consumer imports the capability
- a security, privacy, credential, or permission boundary requires isolation
- a separate deployment/runtime target is operationally necessary
- release cadence or versioning must be independent
- ownership and review authority are materially different
- scale or reliability requirements cannot be met inside the current boundary
- public/open-source distribution requires a clean legal or dependency boundary

## 6. Required repository contract

Every active repository must include a `.quirk/manifest.json` declaring at minimum:

```json
{
  "repository": "Quirk-Systems/example",
  "primary_class": "realm",
  "domain": "example-domain",
  "authority": "Quirk-Systems/.github",
  "lifecycle": "active",
  "owner": "@owner",
  "canonical_inputs": [],
  "projections": [],
  "data_classification": "internal",
  "semantic_policy": "required",
  "extraction_trigger": null,
  "retirement_condition": null
}
```

Required repository-level files or inherited organization defaults:

- `README.md`
- `LICENSE` or explicit private/internal designation
- `SECURITY.md`
- `CONTRIBUTING.md`
- `CODEOWNERS`
- `.quirk/manifest.json`
- issue and pull-request templates
- dependency and secret scanning
- validation workflow
- release or deployment declaration
- architecture decision location

## 7. Lifecycle management

Repositories move through explicit lifecycle states:

```text
proposed
→ incubating
→ active
→ maintained
→ frozen
→ deprecated
→ archived
```

Rules:

- `proposed`: no repository exists yet; work remains an issue, RFC, branch, or lab.
- `incubating`: bounded proof with a named owner, deadline, and evaluation criteria.
- `active`: receives product or platform development.
- `maintained`: stable and supported, but not under heavy feature development.
- `frozen`: preserved for reference; only security or critical fixes accepted.
- `deprecated`: replacement and migration path are declared.
- `archived`: read-only; no longer part of current runtime or canonical authority.

No repository may remain indefinitely in an unnamed experimental state.

## 8. Management foundations

### 8.1 Canonical portfolio registry

Maintain a machine-readable repository registry in `.github` containing:

- repository identity
- primary class
- visibility
- lifecycle state
- owner
- canonical authority
- runtime/deployment target
- data classification
- dependencies and consumers
- extraction trigger
- retirement condition
- health status

### 8.2 Shared workflow spine

The `.github` repository should provide reusable workflows for:

- semantic governance
- manifest validation
- lint, type-check, test, build, and E2E
- dependency audit and license policy
- secret scanning and CodeQL
- SBOM and provenance generation
- release validation
- repository health reporting
- stale or abandoned incubations

Repositories should call shared workflows rather than copy and drift.

### 8.3 Decision system

Use three levels of architectural decision:

- **Organization ADR**: changes canonical topology, governance, repository classes, security posture, or shared contracts.
- **Repository ADR**: changes an individual repository’s architecture or operational behavior.
- **Move receipt**: records a bounded consequential action, its authority, evidence, and resulting state update.

Accepted decisions must update canonical files or manifests. A closed issue alone is not the final state.

### 8.4 Work item grammar

Standard issue types:

- `proposal`
- `decision`
- `implementation`
- `investigation`
- `incident`
- `migration`
- `maintenance`
- `deprecation`
- `world-state-update`

Every implementation issue should identify:

- preparatory evidence
- required real-time decision, if any
- authorization owner
- execution boundary
- review evidence
- persistent files or registries that must change when accepted

### 8.5 Ownership and approvals

Define CODEOWNERS by responsibility, not only by file path:

- canon owner
- runtime owner
- security owner
- data owner
- realm/product owner
- release owner
- incident shutdown authority

High-impact changes require the relevant authority even when an agent authored the patch.

### 8.6 Version and release policy

Use semantic versioning for shared contracts and packages. Use dated or product releases for realm applications where appropriate.

Breaking changes to canonical schemas, manifests, ontology, agent contracts, or shared APIs must include:

- migration instructions
- affected consumer list
- compatibility window
- rollback path
- evidence that projections remain reproducible

### 8.7 Security and supply-chain baseline

Organization minimums:

- branch protection or rulesets on default branches
- required status checks
- signed or verified release provenance where practical
- secret scanning and push protection
- Dependabot security updates
- CodeQL for supported languages
- production dependency audit
- least-privilege GitHub Actions permissions
- pinned or trusted Actions
- environment protection for production deploys
- documented credential ownership and rotation
- generated SBOM for release-bearing repositories

### 8.8 Agent governance

Agent-authored work must expose:

- bounded objective
- allowed and forbidden knowledge sources
- allowed, approval-gated, and forbidden tools
- execution environment and limits
- human owner and shutdown authority
- evidence receipt
- model/provider identity when consequential
- reversible postcondition or rollback plan

Agent setup belongs in versioned repository configuration, not only personal chat context.

### 8.9 Repository health score

Track a lightweight scorecard for each active repository:

- purpose clarity
- owner assigned
- manifest valid
- CI health
- security posture
- dependency freshness
- documentation freshness
- test coverage confidence
- release/deployment health
- consumer evidence
- unresolved architectural debt

The score is a decision aid, not vanity telemetry.

### 8.10 Portfolio review cadence

Run a portfolio review twice weekly for active work and quarterly for topology.

Twice-weekly review:

- active PRs and failing CI
- security and dependency findings
- decisions awaiting authority
- blocked agent or human work
- repository health regressions
- the single highest-leverage next move

Quarterly topology review:

- repositories to merge, archive, split, or reclassify
- extraction triggers that became real
- stale labs and incubations
- duplicate capabilities
- public/private boundary changes
- owner and permission drift
- canonical registry accuracy

### 8.11 Public/private doctrine

Public repositories should expose reusable infrastructure, reference implementations, governance, or products intended for external inspection.

Private repositories should contain personal data, unreleased strategy, credentials or sensitive operational policy, private realm experiments, or work whose legal and product posture is unresolved.

Visibility is a governed property, not the accidental default selected during repository creation.

## 9. Target topology

### Now

```text
.github              public canon and shared workflows
.github-private      private internal governance
quirk-os             implemented kernel and operator surface
quirk-feed           preparation and discovery interface
quirk-generator      visual-generation instrument
quirk-beauty         realm proof
quirk-pet            realm proof
quirk-town           realm proof
quirk-data           reserved registry boundary
quirk-me             reserved identity/interface boundary
quirk-run            reserved execution boundary
demo-repository      sandbox
```

### Extract only when justified

```text
quirk-core           canonical contracts, ontology, schemas, validators
quirk-evals          system, agent, semantic, and regression evaluations
quirk-connect        external connectors and interoperability contracts
quirk-cli            local/operator command surface
```

These are not automatic next repositories. They are candidate boundaries whose extraction conditions must be proven.

## 10. Phased implementation

### Phase 0 — truthful topology

- perform the `project-scaffold` → `quirk-os` cutover
- rename and archive the empty placeholder
- publish the organization profile
- classify every repository
- mark `demo-repository` non-canonical

### Phase 1 — repository contract

- expand `.quirk/manifest.json`
- add schema validation
- add organization-default issue and PR templates
- add CODEOWNERS and lifecycle state
- establish shared validation and security workflows

### Phase 2 — portfolio registry and health

- create machine-readable repository registry
- generate an organization portfolio view
- add repository health checks
- add stale incubation and missing-owner alerts
- map dependencies and real consumers

### Phase 3 — stateful operating loop

- connect proposals, approvals, runs, evidence, and commits
- define move receipts and world-state updates
- make accepted review outcomes update canonical registries
- project Git-canonical state into runtime data and operator interfaces

### Phase 4 — evidence-based extraction

- extract packages or repositories only after triggers are met
- publish compatibility contracts
- introduce independent releases only where required
- archive superseded shells and proofs

## 11. Non-negotiable doctrine

> A repository is not created to honor a noun. It is created to enforce a real boundary.

> Canon remains reviewable in Git. Runtime systems may project it, but may not silently redefine it.

> Agents may prepare and execute; humans retain authority over consequential state change.

> Every accepted change must leave the shared world more accurate than it found it.
