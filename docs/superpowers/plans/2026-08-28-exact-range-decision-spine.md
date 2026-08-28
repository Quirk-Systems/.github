# Exact-Range Decision Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> execute this plan task-by-task. Use test-driven development for validator
> behavior and verification-before-completion before making success claims.

**Goal:** Establish one narrow organization evidence and decision spine that
binds claims to an exact Git range, makes head changes stale for current action,
and preserves authority as a separate gate.

**Architecture:** `Quirk-Systems/.github` owns versioned evidence and decision
contracts plus read-only reusable validation. Evidence receipts bind exact
bytes; governed decisions cite receipts through immutable source locators and
name the next authority gate while retaining structural authority effect `none`.
Interoperability guidance keeps Git canon, runtime effects, and
database/object-store/UI projections separate.

**Tech Stack:** Python 3.12 standard library, JSON Schema draft 2020-12, Git,
GitHub Actions, Markdown.

**Spec:** `docs/governance/EVIDENCE_BINDING.md`

## Global Constraints

- Work from the current `main` head and deliver only through a draft PR.
- Do not merge, close historical PRs, activate rulesets, deploy, publish, or
  admit any repository or concept.
- Full repository/base/head SHAs and exact changed paths anchor consequential
  claims.
- Every cited receipt has an immutable source repository/commit/path plus its
  receipt digest and covered head.
- A syntactically valid locator is not resolved evidence; a receiving boundary
  must fetch and validate the exact bytes before reliance.
- Evidence and governed decisions have authority effect `none`.
- A candidate head change invalidates the decision for current action.
- Use no third-party Python package in the validator path.
- `Quirkroot` has no active-work path and no wholesale successor.

---

### Task 1: Port the exact-range evidence spine

**Files:**

- Create: `.quirk/schemas/evidence-receipt.schema.json`
- Create: `.quirk/evidence/README.md`
- Create: `scripts/create_evidence_receipt.py`
- Create: `scripts/validate_evidence_receipts.py`
- Create: `tests/test_evidence_receipts.py`
- Create: `.github/workflows/reusable-evidence-binding.yml`

**Interfaces:**

- Produces: `create_evidence_receipt.py` and
  `validate_evidence_receipts.py --range-base <sha> --range-head <sha>
  --require-covered-diff`.
- Authority effect: receipt and claim fields are structurally `none`.

- [x] Import the already-tested files from `.github` PR #6 without importing its
  stale topology inventory or manual PR ledger.
- [x] Run `python -m unittest tests.test_evidence_receipts -v`.
- [x] Confirm mutation cases reject forged digests, stale paths, non-ancestor
  subjects, failed commands, and admission effects.

### Task 2: Add the governed-decision contract with TDD

**Files:**

- Create: `.quirk/schemas/governed-decision.schema.json`
- Create: `.quirk/decisions/README.md`
- Create: `scripts/validate_governed_decisions.py`
- Create: `tests/test_governed_decisions.py`

**Interfaces:**

```python
canonical_decision_digest(decision: dict) -> str
validate_decision(
    decision: dict,
    repository: str | None = None,
    current_head: str | None = None,
) -> str
validate_directory(
    repository: str,
    root: str,
    decisions: str,
    current_head: str | None = None,
) -> int
```

- [x] Write a failing test that imports the absent validator.
- [x] Verify failure is `FileNotFoundError` for
  `scripts/validate_governed_decisions.py`.
- [x] Implement closed-field, full-SHA, digest, exact-head receipt, sorted-path,
  classification/disposition, staleness, and authority-effect checks.
- [x] Run `python -m unittest tests.test_governed_decisions -v` and require 13
  passing tests.
- [x] Run
  `python scripts/validate_governed_decisions.py --repository Quirk-Systems/.github --root . --decisions .quirk/decisions`.

### Task 2A: Repair receipt citation interoperability with TDD

**Files:**

- Modify: `.quirk/schemas/governed-decision.schema.json`
- Modify: `.quirk/decisions/README.md`
- Modify: `scripts/validate_governed_decisions.py`
- Modify: `tests/test_governed_decisions.py`

- [x] Add a failing fixture that requires `source_repository`, `source_commit`,
  and `source_path` for every receipt citation.
- [x] Observe the old validator reject those fields and the old schema fail the
  new required-field assertion.
- [x] Validate immutable repository/commit/path shape, safe paths, unique source
  locators, receipt digests, and exact covered-head equality.
- [ ] Run the full suite and require all 36 tests to pass.
- [ ] Generate a fresh receipt because the repaired files supersede the earlier
  exact bytes.

### Task 3: Document interoperability and review inputs

**Files:**

- Modify: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `docs/governance/INTEROPERABILITY.md`
- Replace: `docs/governance/EVIDENCE_BINDING.md`
- Create: `docs/governance/REQUIRED_CHECKS_ROLLOUT.md`

**Interfaces:**

- PRs expose exact subject, scope class, authority not granted, immutable receipt
  locator, evidence, interoperability impact, rollback, and residue.
- GitHub, Supabase, Cloudflare R2, FastAPI, Vercel, and skill/agent systems retain
  distinct source, projection, and authority roles.

- [x] Preserve existing semantic-impact prompts while adding exact-range and
  authority sections.
- [x] Document canonical JSON, schema versioning, immutable IDs, idempotency,
  retries, partial failure, projection rebuild, data classification, and
  provider-adapter rules.
- [x] Document that locator validation does not replace fetching and validating
  the exact external receipt bytes.
- [x] Document Evaluate-before-Active ruleset rollout as an owner-only follow-up.

### Task 4: Wire validation and create exact evidence

**Files:**

- Create: `.github/workflows/governance-contracts.yml`
- Create after each substantive subject repair:
  `.quirk/evidence/<dated-exact-subject>.json`

**Interfaces:**

- `Governance Contracts / validate` checks out the event's exact head with full
  history and read-only credentials.
- A subject commit contains implementation and documentation.
- A later receipt-only commit contains only the generated receipt JSON.
- Receipt IDs include the first 12 characters of the subject SHA so repaired
  subjects cannot collide with earlier evidence IDs.

- [x] Run the complete Python suite on the first subject head.
- [x] Emit the first generated candidate receipt in the workflow log.
- [x] Commit the exact generated first receipt without editing its subject or
  digests.
- [x] Require the first final workflow to pass full changed-path coverage.
- [ ] Run the complete Python suite on the receipt-locator repair head.
- [ ] Commit the exact second receipt as the sole next file.
- [ ] Require the new final workflow to pass full changed-path coverage.

### Task 5: Update PR and issue control records

**Files:** GitHub PR and issue metadata only.

- [x] Open the new change as a draft PR from current `main`.
- [x] Mark `.github` PR #6 as historically preserved and superseded for the
  evidence/decision spine; do not close or merge it automatically.
- [x] Comment on `quirk-os#44`, `quirk-core#2`, `project-scaffold#95`, and
  `Quirk#5` with their observed exact heads and the new current-head rule.
- [x] Create an owner-only issue for Evaluate → Active required-check rollout.
- [x] Create a read-only pilot issue for applying the admitted contract to
  `Quirk#5` after the organization policy lands.
- [x] Add an interoperability note to `.github` issue #8 without admitting or
  extracting `quirk-evals`.
- [ ] Update the pilot acceptance criteria to require materialization and
  validation of the receipt at its immutable source locator.
