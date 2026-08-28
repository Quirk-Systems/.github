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
bytes; governed decisions cite receipts and name the next authority gate while
retaining structural authority effect `none`. Interoperability guidance keeps
Git canon, runtime effects, and database/object-store/UI projections separate.

**Tech Stack:** Python 3.12 standard library, JSON Schema draft 2020-12, Git,
GitHub Actions, Markdown.

**Spec:** `docs/governance/EVIDENCE_BINDING.md`

## Global Constraints

- Work from the current `main` head and deliver only through a draft PR.
- Do not merge, close historical PRs, activate rulesets, deploy, publish, or
  admit any repository or concept.
- Full repository/base/head SHAs and exact changed paths anchor consequential
  claims.
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

- [ ] Import the already-tested files from `.github` PR #6 without importing its
  stale topology inventory or manual PR ledger.
- [ ] Run `python -m unittest tests.test_evidence_receipts -v`.
- [ ] Confirm mutation cases reject forged digests, stale paths, non-ancestor
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

- [ ] Write a failing test that imports the absent validator.
- [ ] Verify failure is `FileNotFoundError` for
  `scripts/validate_governed_decisions.py`.
- [ ] Implement closed-field, full-SHA, digest, exact-head receipt, sorted-path,
  classification/disposition, staleness, and authority-effect checks.
- [ ] Run `python -m unittest tests.test_governed_decisions -v` and require 13
  passing tests.
- [ ] Run
  `python scripts/validate_governed_decisions.py --repository Quirk-Systems/.github --root . --decisions .quirk/decisions`.

### Task 3: Document interoperability and review inputs

**Files:**

- Modify: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `docs/governance/INTEROPERABILITY.md`
- Replace: `docs/governance/EVIDENCE_BINDING.md`
- Create: `docs/governance/REQUIRED_CHECKS_ROLLOUT.md`

**Interfaces:**

- PRs expose exact subject, scope class, authority not granted, evidence,
  interoperability impact, rollback, and residue.
- GitHub, Supabase, Cloudflare R2, FastAPI, Vercel, and skill/agent systems retain
  distinct source, projection, and authority roles.

- [ ] Preserve existing semantic-impact prompts while adding exact-range and
  authority sections.
- [ ] Document canonical JSON, schema versioning, immutable IDs, idempotency,
  retries, partial failure, projection rebuild, data classification, and
  provider-adapter rules.
- [ ] Document Evaluate-before-Active ruleset rollout as an owner-only follow-up.

### Task 4: Wire validation and create exact evidence

**Files:**

- Create: `.github/workflows/governance-contracts.yml`
- Create after the subject commit:
  `.quirk/evidence/2026-08-28-exact-range-decision-spine.json`

**Interfaces:**

- `Governance Contracts / validate` checks out the event's exact head with full
  history and read-only credentials.
- The subject commit contains implementation and documentation.
- The later receipt commit contains only the receipt JSON.

- [ ] Run the complete Python suite on the subject head.
- [ ] Emit the generated candidate receipt in the workflow log.
- [ ] Commit the exact generated receipt without editing its subject or digests.
- [ ] Require the final workflow to pass full changed-path coverage.

### Task 5: Update PR and issue control records

**Files:** GitHub PR and issue metadata only.

- [ ] Open the new change as a draft PR from current `main`.
- [ ] Mark `.github` PR #6 as historically preserved and superseded for the
  evidence/decision spine; do not close or merge it automatically.
- [ ] Comment on `quirk-os#44`, `quirk-core#2`, `project-scaffold#95`, and
  `Quirk#5` with their observed exact heads and the new current-head rule.
- [ ] Create an owner-only issue for Evaluate → Active required-check rollout.
- [ ] Create a read-only pilot issue for applying the admitted contract to
  `Quirk#5` after the organization policy lands.
- [ ] Add an interoperability note to `.github` issue #8 without admitting or
  extracting `quirk-evals`.
