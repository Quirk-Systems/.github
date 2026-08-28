# PR Closure Harness v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, read-only PR Closure Harness that binds repository ownership, blockers, proof, review state, authority ceilings, and one non-authoritative disposition to an exact pull-request head.

**Architecture:** `Quirk-Systems/.github` owns a Python 3.12 standard-library package, closed JSON contracts, hermetic fixtures, a Code Ontology projection, an EvalDossier generator, a Plugin Eval metric pack, and a reusable GitHub Actions shadow workflow. The workflow checks out the immutable PR head, reads the repository-local boundary and closure input, queries review/check metadata with read-only permissions, emits validated artifacts, and stops at `ELIGIBLE_FOR_HUMAN_REVIEW`.

**Tech Stack:** Python 3.12 standard library, `unittest`, JSON Schema 2020-12 contract documents with repository-native validators, canonical JSON/SHA-256, Git, GitHub Actions on `ubuntu-24.04`, Plugin Eval metric-pack interface.

**Spec:** `docs/superpowers/specs/2026-08-28-pr-closure-harness-design.md`

## Global Constraints

- Canonical owner is `Quirk-Systems/.github`.
- `Quirkroot` remains retired as an active architecture boundary.
- Version 0.1 is read-only/shadow mode and ends at `ELIGIBLE_FOR_HUMAN_REVIEW`.
- No merge, close, approval, Canon/admission, ruleset activation, runtime activation, release, deployment, publication, provider provisioning, provider write, Supabase migration, Sentry provisioning, ownership transfer, financial, physical, personal-identity, or irreversible action.
- Every consequential subject uses full lowercase 40-character Git SHAs.
- Any head change makes the prior Passport, Dossier, review, metric result, and Warrant stale for current action.
- Every proof status is exactly `PASS`, `FAIL`, `NOT_EXECUTED`, or `NOT_OBSERVED`.
- Python implementation uses the standard library only.
- JSON objects are closed; unknown fields fail validation.
- All fixtures are hermetic and perform zero external writes.
- GitHub Actions are pinned to immutable commits; do not use floating tags or branches.
- Code Ontology output is structural only and never claims TypeScript execution, runtime reachability, admission, or authority.
- EvalDossier requires exact external audience, evaluator identity, rubric version, nonce, limitations, and withheld claims.
- Plugin Eval metrics supplement but never overwrite the core evaluation result.
- Cloudflare evidence is limited to type, bundle, dry-run, and hermetic behavioral fixtures; no deployment or binding creation.
- Sentry events are generated as local candidate envelopes only; no DSN or network transmission.

---

## File Map

```text
.github/workflows/pr-closure-harness.yml
.github/workflows/reusable-pr-closure-shadow.yml

schemas/repository-boundary.v1.schema.json
schemas/pr-closure-input.v1.schema.json
schemas/pr-closure-passport.v1.schema.json
schemas/pr-closure-ontology.v1.schema.json
schemas/eval-dossier.v1.schema.json
schemas/closure-observability-event.v1.schema.json

scripts/compile_pr_closure.py
scripts/fetch_pr_review_snapshot.py
scripts/pr_closure/__init__.py
scripts/pr_closure/canonical.py
scripts/pr_closure/contracts.py
scripts/pr_closure/git_subject.py
scripts/pr_closure/github_snapshot.py
scripts/pr_closure/compiler.py
scripts/pr_closure/ontology.py
scripts/pr_closure/dossier.py
scripts/pr_closure/observability.py

metric-packs/pr-closure/evaluate.py
metric-packs/pr-closure/README.md

fixtures/pr-closure/positive/ordinary-merge-review/
fixtures/pr-closure/positive/boundary-admission-review/
fixtures/pr-closure/positive/held-runtime-candidate/
fixtures/pr-closure/adversarial/stale-head/
fixtures/pr-closure/adversarial/mergeable-open-p1/
fixtures/pr-closure/adversarial/candidate-as-canon/
fixtures/pr-closure/adversarial/synthetic-as-real/
fixtures/pr-closure/adversarial/receipt-byte-mismatch/
fixtures/pr-closure/adversarial/wrong-owner/
fixtures/pr-closure/adversarial/skipped-as-pass/
fixtures/pr-closure/adversarial/hidden-review-thread/
fixtures/pr-closure/adversarial/authority-unknown-key/
fixtures/pr-closure/adversarial/path-traversal/
fixtures/pr-closure/adversarial/telemetry-as-value/
fixtures/pr-closure/adversarial/green-boundary-plus-runtime/

tests/pr_closure/__init__.py
tests/pr_closure/test_canonical.py
tests/pr_closure/test_contracts.py
tests/pr_closure/test_git_subject.py
tests/pr_closure/test_github_snapshot.py
tests/pr_closure/test_compiler.py
tests/pr_closure/test_ontology.py
tests/pr_closure/test_dossier.py
tests/pr_closure/test_observability.py
tests/pr_closure/test_metric_pack.py
tests/pr_closure/test_cli.py

docs/governance/PR_CLOSURE_HARNESS.md
```

---

### Task 1: Canonical JSON and digest primitives

**Files:**
- Create: `scripts/pr_closure/__init__.py`
- Create: `scripts/pr_closure/canonical.py`
- Create: `tests/pr_closure/__init__.py`
- Create: `tests/pr_closure/test_canonical.py`

**Interfaces:**
- Produces: `canonical_json_bytes(value: object) -> bytes`
- Produces: `canonical_sha256(value: object) -> str`
- Produces: `load_json_no_duplicates(raw: bytes) -> object`

- [ ] **Step 1: Write duplicate-key, non-finite-number, Unicode, and digest tests**

```python
# tests/pr_closure/test_canonical.py
import unittest

from scripts.pr_closure.canonical import (
    canonical_json_bytes,
    canonical_sha256,
    load_json_no_duplicates,
)


class CanonicalJsonTests(unittest.TestCase):
    def test_orders_keys_and_preserves_utf8(self) -> None:
        self.assertEqual(
            canonical_json_bytes({"z": "Minnesota", "a": "Quirk™"}),
            '{"a":"Quirk™","z":"Minnesota"}'.encode("utf-8"),
        )

    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: head_sha"):
            load_json_no_duplicates(b'{"head_sha":"a","head_sha":"b"}')

    def test_rejects_non_finite_numbers(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_bytes({"score": float("nan")})

    def test_digest_has_sha256_prefix(self) -> None:
        self.assertRegex(
            canonical_sha256({"authority_effect": "none"}),
            r"^sha256:[0-9a-f]{64}$",
        )
```

- [ ] **Step 2: Run the test and verify the import fails**

Run:

```bash
python -m unittest tests.pr_closure.test_canonical -v
```

Expected: `ModuleNotFoundError` for `scripts.pr_closure.canonical`.

- [ ] **Step 3: Implement canonical JSON and duplicate-key rejection**

```python
# scripts/pr_closure/canonical.py
from __future__ import annotations

import hashlib
import json
from typing import Any


def _object_pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_no_duplicates(raw: bytes) -> object:
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_object_pairs_no_duplicates,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON number: {value}")
        ),
    )


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()
```

- [ ] **Step 4: Run the focused tests**

Run:

```bash
python -m unittest tests.pr_closure.test_canonical -v
```

Expected: four tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/pr_closure tests/pr_closure
git commit -m "feat(governance): add canonical closure primitives"
```

---

### Task 2: Closed repository-boundary and closure-input contracts

**Files:**
- Create: `schemas/repository-boundary.v1.schema.json`
- Create: `schemas/pr-closure-input.v1.schema.json`
- Create: `scripts/pr_closure/contracts.py`
- Create: `tests/pr_closure/test_contracts.py`
- Create: `fixtures/pr-closure/positive/ordinary-merge-review/repository-boundary.json`
- Create: `fixtures/pr-closure/positive/ordinary-merge-review/closure-input.json`

**Interfaces:**
- Consumes: `load_json_no_duplicates`
- Produces: `RepositoryBoundary`
- Produces: `ClosureInput`
- Produces: `load_repository_boundary(path: Path, expected_repository: str) -> RepositoryBoundary`
- Produces: `load_closure_input(path: Path, expected_head_sha: str) -> ClosureInput`

Treat `responsibilities[]` and `prohibited_responsibilities[]` as repository-relative POSIX glob patterns. The validator rejects absolute paths, backslashes, NUL bytes, empty patterns, and `..` path segments.

- [ ] **Step 1: Write contract tests**

```python
# tests/pr_closure/test_contracts.py
import json
import tempfile
import unittest
from pathlib import Path

from scripts.pr_closure.contracts import (
    load_closure_input,
    load_repository_boundary,
)


VALID_HEAD = "a" * 40


class ContractTests(unittest.TestCase):
    def write_json(self, value: object) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "input.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_boundary_rejects_another_repository(self) -> None:
        path = self.write_json({
            "schema_version": "repository-boundary.v1",
            "repository": "Quirk-Systems/quirk-run",
            "owner": "Quirk Systems governance",
            "purpose": "Organization governance",
            "responsibilities": [".github/**"],
            "prohibited_responsibilities": ["runtime/**"],
            "authority_ceiling": "governance_candidate",
            "supported_runtimes": ["python-3.12"],
            "required_checks": ["PR Closure Harness / validate"],
            "related_repositories": ["Quirk-Systems/Quirk"],
        })
        with self.assertRaisesRegex(ValueError, "boundary repository mismatch"):
            load_repository_boundary(path, "Quirk-Systems/.github")

    def test_boundary_rejects_path_traversal_pattern(self) -> None:
        path = self.write_json({
            "schema_version": "repository-boundary.v1",
            "repository": "Quirk-Systems/.github",
            "owner": "Quirk Systems governance",
            "purpose": "Organization governance",
            "responsibilities": ["../quirk-run/**"],
            "prohibited_responsibilities": [],
            "authority_ceiling": "governance_candidate",
            "supported_runtimes": ["python-3.12"],
            "required_checks": [],
            "related_repositories": [],
        })
        with self.assertRaisesRegex(ValueError, "unsafe path pattern"):
            load_repository_boundary(path, "Quirk-Systems/.github")

    def test_closure_input_rejects_stale_head(self) -> None:
        path = self.write_json({
            "schema_version": "pr-closure-input.v1",
            "head_sha": "b" * 40,
            "scope_classification": "IMPLEMENTATION_DETAIL",
            "blockers": [],
            "proofs": [],
            "external_writes": 0,
            "successors": [],
            "authority_ceiling": "candidate",
            "external_audience": "Quirk Systems human reviewer",
            "evaluator_identity": "pr-closure-harness",
            "rubric_id": "quirk.pr-closure.v1",
            "rubric_version": "1.0.0",
            "nonce": "closure-fixture-001",
            "limitations": ["Synthetic fixture only"],
            "withheld_claims": ["No merge authority"],
        })
        with self.assertRaisesRegex(ValueError, "closure input head is stale"):
            load_closure_input(path, VALID_HEAD)
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run:

```bash
python -m unittest tests.pr_closure.test_contracts -v
```

Expected: import failure for `scripts.pr_closure.contracts`.

- [ ] **Step 3: Write both closed JSON Schema documents**

Use JSON Schema 2020-12 with `additionalProperties: false`, exact enum values from the design, full-SHA regex `^[0-9a-f]{40}$`, digest regex `^sha256:[0-9a-f]{64}$`, and `minItems: 1` only where the design requires at least one value. Encode authority grants as constant `false` in later Passport schemas; closure input carries only the authority ceiling.

- [ ] **Step 4: Implement dataclasses and repository-native validation**

```python
# scripts/pr_closure/contracts.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .canonical import load_json_no_duplicates

SHA40 = set("0123456789abcdef")


def _require_sha(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40 or any(c not in SHA40 for c in value):
        raise ValueError(f"{field} must be a lowercase 40-character Git SHA")
    return value


def _require_closed_object(value: object, allowed: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("document must be a JSON object")
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise ValueError(f"unknown fields: {', '.join(unknown)}")
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    return value


def _safe_pattern(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("unsafe path pattern")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe path pattern")
    return value
```

Complete the dataclasses with immutable tuples and exact enum validation. Do not silently coerce numbers, booleans, strings, lists, or missing values.

- [ ] **Step 5: Add the valid fixture pair and run tests**

Run:

```bash
python -m unittest tests.pr_closure.test_contracts -v
```

Expected: all contract tests pass.

- [ ] **Step 6: Commit**

```bash
git add schemas scripts/pr_closure/contracts.py tests/pr_closure/test_contracts.py fixtures/pr-closure/positive/ordinary-merge-review
git commit -m "feat(governance): define closure boundary and input contracts"
```

---

### Task 3: Proof Passport contract and validator

**Files:**
- Create: `schemas/pr-closure-passport.v1.schema.json`
- Create: `scripts/pr_closure/model.py`
- Create: `scripts/validate_pr_closure_passport.py`
- Create: `tests/pr_closure/test_passport.py`

**Interfaces:**
- Produces: immutable dataclasses `PRSubject`, `ScopeDelta`, `BlockerRecord`, `ProofResult`, `ReviewSnapshot`, `CheckSnapshot`, `AuthorityBoundary`, `Disposition`, `ProofPassport`
- Produces: `ProofPassport.to_dict() -> dict[str, object]`
- Produces: `validate_passport(value: object) -> ProofPassport`

- [ ] **Step 1: Write tests for closed authority fields and status semantics**

```python
# tests/pr_closure/test_passport.py
import unittest

from scripts.pr_closure.model import validate_passport


class PassportTests(unittest.TestCase):
    def test_rejects_true_authority_grant(self) -> None:
        value = self.valid_passport()
        value["authority"]["deployment_granted"] = True
        with self.assertRaisesRegex(ValueError, "deployment_granted must be false"):
            validate_passport(value)

    def test_not_executed_requires_reason_and_no_command(self) -> None:
        value = self.valid_passport()
        value["proofs"] = [{
            "id": "behavioral-fixture",
            "status": "NOT_EXECUTED",
            "command": "npm test",
            "reason": "runner unavailable",
            "runner": None,
            "observed_at": None,
            "subject_head_sha": "a" * 40,
            "artifact_locator": None,
            "limitations": ["No runtime proof"],
        }]
        with self.assertRaisesRegex(ValueError, "NOT_EXECUTED proof cannot carry a command"):
            validate_passport(value)

    @staticmethod
    def valid_passport() -> dict[str, object]:
        return {
            "schema_version": "pr-closure-passport.v1",
            "subject": {
                "repository": "Quirk-Systems/.github",
                "pull_request": 14,
                "base_sha": "b" * 40,
                "head_sha": "a" * 40,
                "merge_base_sha": "b" * 40,
                "head_tree_sha": "c" * 40,
                "changed_paths": ["schemas/pr-closure-passport.v1.schema.json"],
            },
            "scope": {"classification": "IMPLEMENTATION_DETAIL", "owner_valid": True, "fingerprint": "sha256:" + "d" * 64},
            "blockers": [],
            "proofs": [],
            "review": {"complete": True, "independent_review_count": 1, "independent_approval_count": 1, "open_review_thread_count": 0},
            "checks": [],
            "authority": {
                "ceiling": "merge_candidate",
                "merge_granted": False,
                "canon_granted": False,
                "runtime_granted": False,
                "release_granted": False,
                "deployment_granted": False,
                "publication_granted": False,
                "provider_write_granted": False,
            },
            "disposition": {"value": "READY_FOR_MERGE", "required_next": ["Human merge decision"], "stale_when_head_changes": True},
            "external_writes": 0,
        }
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
python -m unittest tests.pr_closure.test_passport -v
```

- [ ] **Step 3: Implement the closed model and CLI validator**

The validator must enforce cross-field rules after structural validation:

```text
PASS           → command, runner, observed_at, and exact subject_head_sha required
FAIL           → command, runner, observed_at, and exact subject_head_sha required
NOT_EXECUTED   → reason required; command, runner, observed_at, artifact_locator forbidden
NOT_OBSERVED   → reason required; command, runner, observed_at, artifact_locator forbidden
```

The CLI accepts exactly one path and exits `0` only for a valid Passport:

```bash
python scripts/validate_pr_closure_passport.py /tmp/pr-closure/passport.json
```

- [ ] **Step 4: Run focused tests**

```bash
python -m unittest tests.pr_closure.test_passport -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add schemas/pr-closure-passport.v1.schema.json scripts/pr_closure/model.py scripts/validate_pr_closure_passport.py tests/pr_closure/test_passport.py
git commit -m "feat(governance): add closed proof passport contract"
```

---

### Task 4: Exact Git subject collection and staleness detection

**Files:**
- Create: `scripts/pr_closure/git_subject.py`
- Create: `tests/pr_closure/test_git_subject.py`

**Interfaces:**
- Consumes: event JSON and repository root
- Produces: `collect_subject(event: dict[str, object], repo_root: Path) -> PRSubject`
- Produces: `assert_current_head(expected_head_sha: str, repo_root: Path) -> None`

- [ ] **Step 1: Write temporary-repository tests**

Create a Git repository in `tempfile.TemporaryDirectory`, make two commits, and assert:

```text
checked-out HEAD must equal event pull_request.head.sha
base, head, merge-base, tree, and changed paths are full immutable values
changed paths are sorted and unique
absolute/backslash/traversal paths are rejected
stale event head raises "checked-out HEAD does not match event head"
```

- [ ] **Step 2: Run the focused tests and verify import failure**

```bash
python -m unittest tests.pr_closure.test_git_subject -v
```

- [ ] **Step 3: Implement Git execution without a shell**

```python
# scripts/pr_closure/git_subject.py
from __future__ import annotations

import subprocess
from pathlib import Path


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()
```

Use `git diff --name-only -z base..head` for changed paths and parse NUL-delimited bytes. Do not parse newline-delimited filenames. Use `git merge-base`, `git rev-parse HEAD^{tree}`, and exact SHA comparison.

- [ ] **Step 4: Run the focused tests**

```bash
python -m unittest tests.pr_closure.test_git_subject -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/pr_closure/git_subject.py tests/pr_closure/test_git_subject.py
git commit -m "feat(governance): bind closure subject to exact Git state"
```

---

### Task 5: Read-only GitHub review and check snapshots

**Files:**
- Create: `scripts/pr_closure/github_snapshot.py`
- Create: `scripts/fetch_pr_review_snapshot.py`
- Create: `tests/pr_closure/test_github_snapshot.py`

**Interfaces:**
- Produces: `fetch_review_snapshot(repository: str, pr_number: int, author_login: str, token: str) -> ReviewSnapshot`
- Produces: `fetch_check_snapshot(repository: str, head_sha: str, required_checks: tuple[str, ...], token: str) -> CheckSnapshot`
- Produces normalized JSON at `/tmp/pr-closure/github-snapshot.json`

- [ ] **Step 1: Write mocked HTTP tests**

Test these cases with `unittest.mock.patch`:

```text
one COMMENTED human review by a non-author → independent_review_count=1
one APPROVED human review by a non-author → independent_approval_count=1
review by PR author → not independent
Bot/App review → not independent
one unresolved review thread → open_review_thread_count=1
GraphQL pageInfo.hasNextPage=true → complete=false
missing required check → NOT_OBSERVED
skipped or cancelled required check → NOT_EXECUTED
successful exact-head check → PASS
failure exact-head check → FAIL
check with another head SHA → ignored
```

- [ ] **Step 2: Run tests and verify they fail**

```bash
python -m unittest tests.pr_closure.test_github_snapshot -v
```

- [ ] **Step 3: Implement the read-only GraphQL review query**

Use this exact query and fail `complete=false` when either collection has another page:

```graphql
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      author { login }
      reviews(first: 100) {
        nodes { state submittedAt author { login __typename } }
        pageInfo { hasNextPage }
      }
      reviewThreads(first: 100) {
        nodes { isResolved }
        pageInfo { hasNextPage }
      }
    }
  }
}
```

Use `urllib.request` with `Authorization: Bearer <token>` and `X-GitHub-Api-Version: 2022-11-28`. Never log the token or raw response headers.

- [ ] **Step 4: Implement exact-head check-run normalization**

Call:

```text
GET https://api.github.com/repos/{owner}/{repo}/commits/{head_sha}/check-runs?per_page=100
```

Map conclusions exactly:

```text
success                         → PASS
failure, timed_out, action_required → FAIL
skipped, cancelled, neutral     → NOT_EXECUTED
missing required context        → NOT_OBSERVED
queued, in_progress             → NOT_OBSERVED
```

If more than 100 check runs exist, set snapshot `complete=false` and prevent a ready disposition.

- [ ] **Step 5: Run focused tests**

```bash
python -m unittest tests.pr_closure.test_github_snapshot -v
```

- [ ] **Step 6: Commit**

```bash
git add scripts/pr_closure/github_snapshot.py scripts/fetch_pr_review_snapshot.py tests/pr_closure/test_github_snapshot.py
git commit -m "feat(governance): collect read-only review and check snapshots"
```

---

### Task 6: Deterministic owner, blocker, proof, and disposition compiler

**Files:**
- Create: `scripts/pr_closure/compiler.py`
- Create: `tests/pr_closure/test_compiler.py`
- Create: all three positive fixture directories
- Create: adversarial fixture directories `stale-head`, `mergeable-open-p1`, `wrong-owner`, `skipped-as-pass`, `hidden-review-thread`, and `green-boundary-plus-runtime`

**Interfaces:**
- Produces: `path_is_owned(boundary: RepositoryBoundary, path: str) -> bool`
- Produces: `compile_passport(boundary, closure_input, subject, review, checks) -> ProofPassport`

- [ ] **Step 1: Write the disposition matrix tests**

Create one test per disposition and one test for monotonic restriction:

```python
class CompilerTests(unittest.TestCase):
    def test_open_p1_forces_revise_even_when_checks_are_green(self) -> None:
        passport = compile_fixture("adversarial/mergeable-open-p1")
        self.assertEqual(passport.disposition.value, "REVISE")

    def test_wrong_owner_with_successor_forces_supersede(self) -> None:
        passport = compile_fixture("adversarial/wrong-owner")
        self.assertEqual(passport.disposition.value, "SUPERSEDE")

    def test_unobserved_required_check_forces_hold(self) -> None:
        passport = compile_fixture("adversarial/skipped-as-pass")
        self.assertEqual(passport.disposition.value, "HOLD_CANDIDATE")

    def test_green_boundary_plus_runtime_is_not_ready(self) -> None:
        passport = compile_fixture("adversarial/green-boundary-plus-runtime")
        self.assertEqual(passport.disposition.value, "HOLD_CANDIDATE")
        self.assertIn("SPLIT_BOUNDARY_FROM_RUNTIME", passport.disposition.required_next)
```

- [ ] **Step 2: Run tests and verify they fail**

```bash
python -m unittest tests.pr_closure.test_compiler -v
```

- [ ] **Step 3: Implement owner checks**

Rules:

```text
any changed path matching prohibited_responsibilities → owner_valid=false
all changed paths must match at least one responsibilities pattern
missing/invalid boundary → owner status unresolved; maximum HOLD_CANDIDATE
wrong owner + named successor → SUPERSEDE
wrong owner without successor → HOLD_CANDIDATE + NAME_SUCCESSOR_OWNER
```

Use `pathlib.PurePosixPath.match`; reject patterns and paths before matching.

- [ ] **Step 4: Implement restrictive disposition precedence**

Use this exact order:

```python
if wrong_owner and successors:
    disposition = "SUPERSEDE"
elif exact_successor_covers_subject:
    disposition = "CLOSE_AS_REDUNDANT"
elif open_blocker or failed_required_check:
    disposition = "REVISE"
elif unresolved_owner or stale_evidence or incomplete_snapshot or unobserved_required_check or missing_independent_review or boundary_forbids_promotion or mixed_boundary_and_runtime:
    disposition = "HOLD_CANDIDATE"
elif admission_required:
    disposition = "READY_FOR_HUMAN_ADMISSION"
else:
    disposition = "READY_FOR_MERGE"
```

`READY_FOR_MERGE` requires at least one independent approval and zero open review threads. `READY_FOR_HUMAN_ADMISSION` requires at least one independent review, but the human admission decision remains external.

- [ ] **Step 5: Enforce external-write and authority ceilings**

Any nonzero `external_writes` forces `REVISE`. Every Passport authority grant remains `false`. `AUTHORITY_CHANGE` adds `PAUSE_REAUTHORIZE` and prevents a ready disposition.

- [ ] **Step 6: Run focused tests**

```bash
python -m unittest tests.pr_closure.test_compiler -v
```

Expected: all disposition tests pass.

- [ ] **Step 7: Commit**

```bash
git add scripts/pr_closure/compiler.py tests/pr_closure/test_compiler.py fixtures/pr-closure
git commit -m "feat(governance): compile monotonic PR closure dispositions"
```

---

### Task 7: Code Ontology projection

**Files:**
- Create: `schemas/pr-closure-ontology.v1.schema.json`
- Create: `scripts/pr_closure/ontology.py`
- Create: `tests/pr_closure/test_ontology.py`

**Interfaces:**
- Produces: `build_ontology(passport: ProofPassport, boundary: RepositoryBoundary) -> dict[str, object]`

- [ ] **Step 1: Write deterministic entity/relation tests**

Assert:

```text
entity IDs are stable and sorted
relations reference existing entity IDs
Repository OWNS RepositoryBoundary
PullRequest CHANGES Path
ProofResult VERIFIES PullRequest
Disposition STALE_AFTER Commit
candidate/runtime relations never emit ADMITS or AUTHORIZES
```

Add a negative test where one relation targets `entity:missing`; validation must fail with `dangling ontology reference`.

- [ ] **Step 2: Run tests and verify failure**

```bash
python -m unittest tests.pr_closure.test_ontology -v
```

- [ ] **Step 3: Implement the closed ontology projection**

Allowed entity kinds:

```text
Repository RepositoryBoundary PullRequest Commit Path Contract EvidenceReceipt ProofResult Reviewer Decision Authority Runtime Projection Provider
```

Allowed relation kinds:

```text
OWNS PROHIBITS CHANGES DEPENDS_ON CITES VERIFIES REVIEWS SUPERSEDES PROJECTS_TO REQUIRES_AUTHORITY STALE_AFTER
```

Do not emit execution, runtime-coverage, admission, or authority claims.

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests.pr_closure.test_ontology -v
```

- [ ] **Step 5: Commit**

```bash
git add schemas/pr-closure-ontology.v1.schema.json scripts/pr_closure/ontology.py tests/pr_closure/test_ontology.py
git commit -m "feat(governance): emit bounded closure ontology projection"
```

---

### Task 8: EvalDossier generation

**Files:**
- Create: `schemas/eval-dossier.v1.schema.json`
- Create: `scripts/pr_closure/dossier.py`
- Create: `tests/pr_closure/test_dossier.py`
- Create: adversarial fixtures `candidate-as-canon`, `synthetic-as-real`, and `receipt-byte-mismatch`

**Interfaces:**
- Produces: `build_dossier(passport, closure_input, ontology_digest) -> dict[str, object]`

- [ ] **Step 1: Write required-pin and withheld-claim tests**

Test that the Dossier rejects:

```text
empty external_audience
empty evaluator_identity
nonce shorter than 12 characters
missing rubric version
artifact without immutable repository/commit/path/digest locator
synthetic evidence paired with a real-world outcome claim
Canon, economic value, or authority claim absent from proof
passport digest mismatch
```

- [ ] **Step 2: Run tests and verify failure**

```bash
python -m unittest tests.pr_closure.test_dossier -v
```

- [ ] **Step 3: Implement canonical Dossier generation**

Required withheld claims for every version 0.1 Dossier:

```text
No merge authority
No Canon or admission authority
No runtime or deployment authority
No provider-write authority
No real-world outcome inferred from synthetic evidence
No economic value inferred from test or telemetry output
```

Dossier ID:

```text
qdossier.pr-closure.<first-12-head-sha>.<first-12-nonce-sha256>
```

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests.pr_closure.test_dossier -v
```

- [ ] **Step 5: Commit**

```bash
git add schemas/eval-dossier.v1.schema.json scripts/pr_closure/dossier.py tests/pr_closure/test_dossier.py fixtures/pr-closure/adversarial/candidate-as-canon fixtures/pr-closure/adversarial/synthetic-as-real fixtures/pr-closure/adversarial/receipt-byte-mismatch
git commit -m "feat(governance): generate exact-head EvalDossiers"
```

---

### Task 9: Plugin Eval closure metric pack

**Files:**
- Create: `metric-packs/pr-closure/evaluate.py`
- Create: `metric-packs/pr-closure/README.md`
- Create: `tests/pr_closure/test_metric_pack.py`

**Interfaces:**
- Script consumes one Passport path as its final CLI argument.
- Script prints one JSON object containing only `checks`, `metrics`, and optional `artifacts`.

- [ ] **Step 1: Write stdout-contract tests**

The test invokes the script with `subprocess.run` and asserts stable IDs:

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

Metrics:

```text
closure.open_blocker_count
closure.unobserved_check_count
closure.stale_evidence_count
closure.negative_fixture_count
closure.open_review_thread_count
closure.external_write_count
closure.required_next_count
```

- [ ] **Step 2: Run the test and verify failure**

```bash
python -m unittest tests.pr_closure.test_metric_pack -v
```

- [ ] **Step 3: Implement deterministic metric output**

The script must:

```text
read and validate the Passport
emit no prose before or after JSON
sort checks and metrics by ID
never emit a core score or summary override
return exit 0 for a valid restrictive Passport
return exit 2 for invalid input
```

- [ ] **Step 4: Run the Plugin Eval metric-pack designer workflow**

From repository root, run:

```bash
plugin-eval start . --request "Design the smallest deterministic metric-pack manifest for metric-packs/pr-closure/evaluate.py. The script accepts one validated PR Closure Passport path and emits only checks, metrics, and optional artifacts. Keep every listed closure.* ID stable and do not override the core score or summary." --format markdown
```

Use the generated manifest exactly as produced by the installed Plugin Eval version. Commit the generated manifest under `metric-packs/pr-closure/` only after this command validates its local schema. Do not invent manifest fields when the installed version differs.

- [ ] **Step 5: Run metric-pack analysis against a positive and adversarial fixture**

```bash
plugin-eval analyze . --metric-pack metric-packs/pr-closure/manifest.json --format json
python -m unittest tests.pr_closure.test_metric_pack -v
```

Expected: the metric pack loads; positive fixture checks pass; `green-boundary-plus-runtime` reports restrictive failed checks without changing the core summary.

- [ ] **Step 6: Commit**

```bash
git add metric-packs/pr-closure tests/pr_closure/test_metric_pack.py
git commit -m "feat(governance): add PR closure Plugin Eval metrics"
```

---

### Task 10: Candidate Sentry observability envelope

**Files:**
- Create: `schemas/closure-observability-event.v1.schema.json`
- Create: `scripts/pr_closure/observability.py`
- Create: `tests/pr_closure/test_observability.py`
- Create: adversarial fixture `telemetry-as-value`

**Interfaces:**
- Produces: `build_observability_event(event_name, passport, harness_commit, environment) -> dict[str, object]`

- [ ] **Step 1: Write redaction and authority tests**

Reject any event containing keys or values derived from:

```text
token secret password authorization cookie request_body source_content personal_data dsn provider_credential exception_string
```

Allow event names only:

```text
closure_harness.completed
closure_harness.blocked
closure_harness.stale
closure_harness.scope_paused
closure_harness.authority_paused
```

Assert `release == harness_commit`, `head_sha == passport.subject.head_sha`, and environment is one of `fixture`, `ci-shadow`, or `local`.

- [ ] **Step 2: Run tests and verify failure**

```bash
python -m unittest tests.pr_closure.test_observability -v
```

- [ ] **Step 3: Implement local event generation only**

Do not import a Sentry SDK. Do not read a DSN. Do not transmit. Serialize the candidate envelope to `/tmp/pr-closure/observability-event.json` for artifact inspection.

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests.pr_closure.test_observability -v
```

- [ ] **Step 5: Commit**

```bash
git add schemas/closure-observability-event.v1.schema.json scripts/pr_closure/observability.py tests/pr_closure/test_observability.py fixtures/pr-closure/adversarial/telemetry-as-value
git commit -m "feat(governance): define redacted closure observability events"
```

---

### Task 11: End-to-end compiler CLI

**Files:**
- Create: `scripts/compile_pr_closure.py`
- Create: `tests/pr_closure/test_cli.py`

**Interfaces:**
- CLI inputs: `--event`, `--repository-root`, `--boundary`, `--closure-input`, `--github-snapshot`, `--output-directory`
- CLI outputs: `passport.json`, `ontology.json`, `eval-dossier.json`, `observability-event.json`, `metric-input.json`

- [ ] **Step 1: Write end-to-end fixture tests**

Invoke the CLI for all three positive fixtures and all twelve adversarial fixtures. Assert:

```text
output filenames are exact
all output JSON is canonical
repeated runs are byte-identical
passport head equals fixture event head
invalid identity exits 2 and emits no Passport
a controlled blocker exits 0 with a restrictive valid Passport
zero external writes are recorded
```

- [ ] **Step 2: Run tests and verify failure**

```bash
python -m unittest tests.pr_closure.test_cli -v
```

- [ ] **Step 3: Implement CLI orchestration**

```python
# scripts/compile_pr_closure.py
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--boundary", type=Path, required=True)
    parser.add_argument("--closure-input", type=Path, required=True)
    parser.add_argument("--github-snapshot", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser.parse_args()
```

Create the output directory only after subject identity validates. Write each file atomically with a temporary sibling followed by `Path.replace`.

- [ ] **Step 4: Run the full local suite**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all closure tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/compile_pr_closure.py tests/pr_closure/test_cli.py
git commit -m "feat(governance): compile closure artifacts end to end"
```

---

### Task 12: Read-only reusable GitHub Actions shadow workflow

**Files:**
- Create: `.github/workflows/reusable-pr-closure-shadow.yml`
- Create: `.github/workflows/pr-closure-harness.yml`
- Modify: `tests/pr_closure/test_workflow_contract.py`

**Interfaces:**
- Reusable workflow inputs: `closure_input_path`, `external_audience`, `evaluator_identity`, `nonce`
- Workflow artifact: `pr-closure-<head_sha>` containing the five generated JSON files

- [ ] **Step 1: Write workflow contract tests**

Parse YAML as text without a third-party YAML package and assert exact invariant fragments:

```text
permissions contain contents: read and pull-requests: read only
checkout ref uses github.event.pull_request.head.sha
fetch-depth is 0
persist-credentials is false
Python is 3.12
no deployment, environments, id-token, packages, actions: write, contents: write, issues: write, or pull-requests: write permission
workflow does not call curl with a token on the command line
workflow invokes full unittest discovery before compiling artifacts
workflow validates checked-out HEAD equals event head
workflow uploads only /tmp/pr-closure/*.json
```

- [ ] **Step 2: Run workflow tests and verify failure**

```bash
python -m unittest tests.pr_closure.test_workflow_contract -v
```

- [ ] **Step 3: Create the reusable workflow with immutable action pins**

Use:

```text
actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09
actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1
actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
```

The workflow sequence is:

```text
checkout exact PR head with history
assert git rev-parse HEAD equals event head
setup Python 3.12
run all unit tests
fetch read-only review/check snapshot
compile five closure artifacts
validate every artifact
run Plugin Eval metric pack
append a bounded summary
upload only generated JSON artifacts
```

The job must not fail merely because the disposition is restrictive. It fails only for invalid identity, invalid contract, crashed validation, or artifact inconsistency.

- [ ] **Step 4: Create the local caller for the harness PR**

`pr-closure-harness.yml` triggers only on pull requests that change:

```text
.github/workflows/pr-closure-*.yml
schemas/*closure*.json
schemas/repository-boundary.v1.schema.json
schemas/eval-dossier.v1.schema.json
scripts/compile_pr_closure.py
scripts/fetch_pr_review_snapshot.py
scripts/pr_closure/**
metric-packs/pr-closure/**
fixtures/pr-closure/**
tests/pr_closure/**
docs/governance/PR_CLOSURE_HARNESS.md
```

- [ ] **Step 5: Run workflow contract and full tests**

```bash
python -m unittest tests.pr_closure.test_workflow_contract -v
python -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

- [ ] **Step 6: Commit**

```bash
git add .github/workflows tests/pr_closure/test_workflow_contract.py
git commit -m "ci(governance): add read-only closure shadow workflow"
```

---

### Task 13: Documentation, Agent Ready evidence, and pilot boundary

**Files:**
- Create: `docs/governance/PR_CLOSURE_HARNESS.md`
- Create: `.quirk/repository-boundary.v1.json`
- Create: `.quirk/closure/pr-closure-harness.json`
- Modify: `README.md`

**Interfaces:**
- Documents local use, caller use, outputs, dispositions, stop rules, and authority ceiling.

- [ ] **Step 1: Write the `.github` repository boundary**

Use responsibilities limited to organization governance paths and prohibited patterns covering runtime, migrations, provider adapters, product surfaces, and application data. The boundary must name `Quirk-Systems/.github` exactly and set authority ceiling to `governance_candidate`.

- [ ] **Step 2: Write the harness closure input**

Bind it to the implementation PR exact head after all substantive commits are present. Include:

```text
scope_classification: MATERIAL_SCOPE_CHANGE
external_writes: 0
authority_ceiling: candidate
external_audience: Quirk Systems human reviewer
evaluator_identity: pr-closure-harness-v0.1
rubric_id: quirk.pr-closure.v1
rubric_version: 1.0.0
nonce: pr-closure-harness-review-2026-08-28
limitations: fixture and shadow-CI evidence only
withheld_claims: every authority and real-world claim required by the design
```

- [ ] **Step 3: Document Agent Ready baseline without assigning an unproven owner**

Record scan `4L8pJOcmAE` for `https://quirk.systems`:

```text
status: failed
pages_scanned: 0
vercel_score: 0
llms_txt_score: 0
observed: no llms.txt, no sitemap, no AGENTS.md, HTTPS handshake timeout
```

State explicitly that this scan does not identify the serving repository, DNS owner, TLS owner, or deployment provider. Do not add public-site files or infrastructure changes to this PR.

- [ ] **Step 4: Document the Cloudflare and Sentry ceilings**

Cloudflare: fixture/type/bundle/dry-run evidence only; no deploy or binding creation.  
Sentry: local candidate event envelope only; no SDK, project, DSN, release, alert, or transmission.

- [ ] **Step 5: Run complete verification**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/compile_pr_closure.py \
  --event fixtures/pr-closure/positive/ordinary-merge-review/event.json \
  --repository-root fixtures/pr-closure/positive/ordinary-merge-review/repository \
  --boundary fixtures/pr-closure/positive/ordinary-merge-review/repository-boundary.json \
  --closure-input fixtures/pr-closure/positive/ordinary-merge-review/closure-input.json \
  --github-snapshot fixtures/pr-closure/positive/ordinary-merge-review/github-snapshot.json \
  --output-directory /tmp/pr-closure-positive
python scripts/validate_pr_closure_passport.py /tmp/pr-closure-positive/passport.json
python metric-packs/pr-closure/evaluate.py /tmp/pr-closure-positive/passport.json

git diff --check
```

- [ ] **Step 6: Commit**

```bash
git add docs/governance .quirk README.md
git commit -m "docs(governance): document PR Closure Harness shadow mode"
```

---

### Task 14: Exact-head evidence cycle and draft PR handoff

**Files:**
- Create: `.quirk/evidence/<date>-pr-closure-harness-<subject-prefix>.json`
- Modify only the generated closure input head binding when required by the exact receipt cycle.

**Interfaces:**
- Produces one exact-range evidence receipt through the admitted `.github#9` mechanism.
- Produces one draft PR disposition packet ending at `ELIGIBLE_FOR_HUMAN_REVIEW`.

- [ ] **Step 1: Rebase only after `.github#9` lands**

```bash
git fetch origin main
git rebase origin/main
```

If `.github#9` is not admitted and merged, stop. Do not duplicate or float its receipt machinery in this implementation.

- [ ] **Step 2: Run the entire suite on the final substantive subject**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
git diff --check origin/main...HEAD
git status --short
```

Expected: all tests pass; diff check clean; only intended files present.

- [ ] **Step 3: Generate the exact-range receipt candidate**

Use the exact generator and validator merged from `.github#9`. Commit the emitted receipt unchanged as the sole follow-up file. Do not edit substantive files in the receipt commit.

- [ ] **Step 4: Verify the receipt-only final head**

Run the repository-native Governance Contracts workflow and the new PR Closure Harness workflow. Both must check out and report the same final exact head.

- [ ] **Step 5: Run Plugin Eval analysis**

```bash
plugin-eval analyze . --metric-pack metric-packs/pr-closure/manifest.json --format json
```

Record whether token/budget figures are static estimates or measured harness results. Do not present static estimates as measured execution.

- [ ] **Step 6: Request independent review**

The review packet must contain:

```text
base SHA
substantive subject SHA
receipt-only final head SHA
exact changed paths
workflow run IDs
Passport digest
EvalDossier ID and digest
Plugin Eval metric-pack result
Agent Ready baseline as non-gating external evidence
limitations and withheld claims
authority ceiling: none
```

- [ ] **Step 7: Stop at draft review eligibility**

Required final state:

```text
PR: open, draft, mergeable if Git permits
Disposition: ELIGIBLE_FOR_HUMAN_REVIEW
Merge: not authorized
Ruleset activation: not authorized
Cloudflare deployment: not authorized
Sentry provisioning: not authorized
Supabase mutation: not authorized
Canon/admission: not authorized
```

Do not mark ready, approve, merge, deploy, activate, publish, provision, or close.

---

## Plan Self-Review

### Spec coverage

- Exact-head identity: Tasks 3–6 and 11–14.
- Repository-local ownership: Tasks 2, 6, and 13.
- Monotonic disposition: Task 6.
- Code Ontology Companion seam: Task 7.
- EvalDossier seam: Task 8.
- Plugin Eval metric pack: Task 9.
- Sentry candidate observability: Task 10.
- Cloudflare boundary: Tasks 6 and 13 documentation; no deployment task exists.
- Agent Ready baseline: Task 13; no unproven serving-owner mutation exists.
- Read-only GitHub shadow workflow: Task 12.
- Adversarial suite: Tasks 6, 8, 10, and 11.
- Exact receipt and human review handoff: Task 14.

### Placeholder scan

The plan contains no `TBD`, `TODO`, generic “add validation,” or unspecified test steps. Plugin Eval manifest generation is intentionally delegated to the installed `metric-pack-designer` workflow and fails closed rather than inventing an unverified manifest schema.

### Type consistency

The plan consistently uses `RepositoryBoundary`, `ClosureInput`, `PRSubject`, `ReviewSnapshot`, `CheckSnapshot`, `ProofPassport`, and the same six disposition enum values. All proof statuses use the same four-value enum.