# Quirk interoperability best practices

Status: **candidate best-practice contract**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

Interoperability means independently implemented Quirk components can exchange
objects without silently changing identity, meaning, state, or authority.

## 1. Owner before path

Every exchanged object must declare what it is, who owns its definition, and
its authority ceiling before a repository path, database table, bucket key, API
route, or UI surface is selected.

```text
identity ≠ ownership ≠ custody ≠ capability ≠ authority
```

No catch-all workspace, repository, bucket, database, or service becomes the
owner merely because it stores many object types. `Quirkroot` is retired for
active work and has no wholesale successor; historical references may remain as
lineage only.

## 2. Preserve five identities

Consequential flows should preserve separate immutable identifiers for:

| Layer | Required identity |
| --- | --- |
| Source | repository, base SHA, head SHA, path, Git blob |
| Evidence | receipt ID, receipt source repository/commit/path, receipt SHA-256, evaluator version |
| Decision | decision ID, decision SHA-256, exact covered head |
| Authority | authorized actor/control reference and explicit effect |
| Runtime | release/package/container/deployment/event identifier |

A downstream system may add a local projection key. It may not replace these
source identities with an untraceable local ID.

## 3. Resolvable evidence references

A cross-system receipt citation must be sufficient to retrieve one immutable
artifact rather than merely naming a logical receipt:

```yaml
receipt_id:
source_repository:
source_commit:
source_path:
receipt_sha256:
covered_head_commit:
```

The consumer must resolve the exact source bytes and then validate the receipt,
its digest, subject repository, base/head range, changed paths, Git blobs, and
artifact SHA-256 values. A locator with correct syntax but unavailable or
mismatched bytes is unresolved evidence and cannot support `CONTINUE` or any
authority-dependent action.

A database row, URL, branch, `latest` alias, object-store key, or receipt ID
without an immutable source commit and digest is a locator convenience only.

## 4. Canon, runtime, and projection

| Layer | Responsibility | Write rule |
| --- | --- | --- |
| Git canon | Versioned definitions, schemas, policies, decisions admitted through review | Reviewed Git change only |
| Runtime | Validation, bounded execution, retries, permissions, side effects | Explicit authority and idempotent effect |
| Projection | Query-optimized state in databases, indexes, dashboards, and caches | Reproducible from source plus receipts |

A projection may report what it last observed. It may not silently redefine the
canonical object or write a learned preference, approval, owner, or authority
back into Git.

## 5. Exchange format

Control objects should use:

- UTF-8 JSON;
- JSON Schema draft 2020-12;
- closed objects (`additionalProperties: false`) at authority boundaries;
- explicit schema versions;
- full lowercase 40-character Git SHAs;
- lowercase `sha256:<64 hex>` content digests;
- RFC 3339 UTC timestamps ending in `Z`;
- safe repository-relative POSIX paths;
- sorted, unique path and enum arrays when canonical hashing depends on order;
- deterministic JSON serialization with sorted keys and compact separators for
  canonical digests.

Unknown fields fail closed in evidence, decision, authority, and execution
objects. Product-facing metadata may be more permissive only outside those
control boundaries.

## 6. Compatibility

- Version schemas independently from implementations.
- Additive changes may remain within a version only when old consumers can
  ignore them safely and the object is not closed at an authority boundary.
- Closed control objects require a new schema version for any new field unless
  the version is still explicitly candidate-only and all known consumers are
  migrated in the same exact-range change.
- Breaking changes require migration instructions, affected-consumer inventory,
  compatibility window, rollback path, and reproducibility evidence.
- Deprecated aliases remain discovery aids; they do not create a second ID.
- Provider adapters translate formats. They do not redefine canonical meaning.

## 7. Idempotency, retries, and partial failure

Every effectful request must carry an idempotency key derived from a stable
subject and authorized decision, for example:

```text
sha256(repository + head_sha + decision_id + effect_class)
```

Retries must return the prior result or continue the same operation; they must
not duplicate publication, deployment, payment, preference writes, or external
messages. Partial failure records the completed steps, remaining steps, and safe
resume or rollback action. A timeout is not evidence that an effect did not
occur.

## 8. Event and state rules

- Events are append-only observations, not mutable truth records.
- Every event carries event ID, schema version, occurred-at time, observed-at
  time, source identity, producer identity, and correlation/idempotency key.
- Reprocessing produces the same projection or an explicit superseding event.
- State transitions are validated against the current version and authority
  gate; out-of-order or duplicate events fail closed or reconcile explicitly.
- Deletion and retraction preserve tombstone lineage rather than erasing the
  prior claim.

## 9. Platform boundaries

| Platform | Proper role | Forbidden inference |
| --- | --- | --- |
| GitHub | Canonical source review, schemas, exact-range evidence, PR state | Green check equals canon, release, or deployment authority |
| Supabase | Structured operational projection, query, reconciliation | Database row silently becomes semantic authority |
| Cloudflare R2 | Content-addressed large/raw evidence and immutable artifacts | Bucket location becomes approval or current truth |
| FastAPI | Versioned validation/query API after a real second consumer exists | API availability grants execution authority |
| Vercel | Disposable review or product projection | Hosted page becomes canonical source |
| Agent/skill systems | Bounded capability invocation | Capability, installation, or tool access implies permission |

Suggested projection fields for Supabase or another operational store:

```text
source_repository
source_base_commit
source_head_commit
source_path
source_blob_sha
source_sha256
schema_version
receipt_id
receipt_source_repository
receipt_source_commit
receipt_source_path
receipt_sha256
decision_id
decision_sha256
projected_at
projection_version
```

Suggested R2 key form:

```text
sha256/<digest>/<artifact-name>
```

Mutable aliases such as `latest/` may improve navigation but cannot be used as
proof without resolving to an immutable digest.

## 10. API and adapter behavior

- Validate inbound objects before side effects.
- Return machine-readable error codes plus safe human explanations.
- Separate read, propose, approve, execute, publish, and revoke operations.
- Do not combine observation with promotion in one endpoint.
- Include authority scope and effect class in every effectful request.
- Pin or report consequential provider/model/API versions.
- Preserve upstream provenance through each adapter and output receipt.
- Resolve immutable evidence locators before using a decision as an input to an
  effectful operation.
- Use least-privilege credentials owned by the runtime boundary, never embedded
  in prompts, fixtures, receipts, or browser artifacts.

## 11. Human gates

Interoperability cannot manufacture authority. The receiving system verifies:

1. the exact subject;
2. the immutable receipt locator and fetched receipt bytes;
3. the evidence receipt and evaluator identity;
4. the decision's current-head match;
5. the required authority control;
6. the bounded effect and rollback/revocation path.

A changed head, unresolved receipt, expired approval, scope mismatch, missing
authority reference, or unresolved partial failure blocks the effect.

## 12. Minimum conformance tests

Every interoperable control should test:

1. unknown-field rejection;
2. malformed and non-UTF-8 input;
3. full-SHA, path, and digest validation;
4. missing, mutable, unavailable, or mismatched receipt locators;
5. exact-head mismatch and stale-decision rejection;
6. duplicate/reordered event handling;
7. idempotent retry after timeout;
8. partial-write recovery;
9. projection drift and rebuild;
10. provider/adapter version mismatch;
11. capability-without-authority rejection;
12. candidate-location-without-canon rejection.

## 13. Promotion rule

A passing conformance suite proves only the tested contract at the named
versions. Promotion, merge, canon, release, deployment, publication, and runtime
mutation remain separate human- or policy-authorized events with their own
receipts.
