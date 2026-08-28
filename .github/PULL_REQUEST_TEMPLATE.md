## Outcome

<!-- What observable condition becomes true? Keep this bounded. -->

-

## Exact subject

<!-- Full immutable SHAs. Branch names and PR numbers are locators, not proof. -->

- Base SHA:
- Head SHA:
- Merge-base SHA, when different from base:
- Changed paths or generated receipt:

## Scope and authority

Classify the delta:

- [ ] `NO_DELTA`
- [ ] `IMPLEMENTATION_DETAIL`
- [ ] `MATERIAL_SCOPE_CHANGE`
- [ ] `AUTHORITY_CHANGE`
- [ ] `BOUNDARY_ONLY`
- [ ] `INSUFFICIENT_EVIDENCE`

Authority effects explicitly **not** granted by this PR:

- [ ] Merge
- [ ] Canon/admission
- [ ] Runtime mutation
- [ ] Release
- [ ] Deployment
- [ ] Publication

Name the human or policy authority still required for any consequential effect.

## Semantic impact

- [ ] Reuses existing Quirk canon
- [ ] Domain extension
- [ ] Canonical change
- [ ] Projection-only change
- [ ] Migration / deprecation

### Concepts touched

List canonical IDs or proposed new IDs. For each new named Quirk concept, specify
its **kind**, **parent**, **boundary**, and **provenance**.

### Collision check

What existing concept could this accidentally duplicate, redefine, or outrank?

## Evidence and verification

<!-- Commands must describe what actually ran against the exact subject. -->

- Evidence receipt ID/path:
- Receipt SHA-256:
- Validator/evaluator commit or version:
- Commands and observed results:
- Checks not run and why:

A green check is not evidence for untested behavior. A receipt does not grant
authority.

## Interoperability impact

- Schemas or APIs changed:
- Consumers/adapters affected:
- Compatibility and migration:
- Idempotency/retry/partial-failure behavior:
- Canonical source and projections:
- Data classification, secrets, or PII impact:

## Risk, rollback, and residue

- Credible failure modes:
- Reversal or containment:
- Unresolved human decisions:

## Linked issues and PRs

<!-- Closes #123, Refs #456, supersedes or depends on another exact head. -->

## Checklist

- [ ] Commits follow Conventional Commits
- [ ] Exact base/head identity is current
- [ ] Tests and validators passed for the stated scope
- [ ] Evidence covers every substantive changed path
- [ ] Documentation and interoperability notes are current
- [ ] Repository `.quirk/manifest.json` remains valid, when present
- [ ] No canonical concept was silently redefined
- [ ] No capability, path, database row, or green check was treated as authority
- [ ] A head change will invalidate the current disposition until re-evaluated
