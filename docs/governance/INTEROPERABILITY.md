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
| Evidence | receipt ID, receipt SHA-256, evaluator version |
| Decision | decision ID, decision SHA-256, exact covered head |
| Authority | authorized actor/control reference and explicit effect |
| Runtime | release/package/container/deployment/event identifier |

A downstream system may add a local projection key. It may not replace these
source identities with an untraceable local ID.

## 3. Canon, runtime, and projection

| Layer | Responsibility | Write rule |
| --- | --- | --- |
| Git canon | Versioned definitions, schemas, policies, decisions admitted through review | Reviewed Git change only |
| Runtime | Validation, bounded execution, retries, permissions, side effects | Explicit authority and idempotent effect |
| Projection | Query-optimized state in databases, indexes, dashboards, and caches | Reproducible from source plus receipts |

A projection may report what it last observed. It may not silently redefine the
canonical object or write a learned preference, approval, owner, or authority
back into Git.

## 4. Exchange format

Control objects should use:

- UTF-8 JSON;
- JSON Schema draft 2020-12;
- closed objects (`additionalProperties: false`) at authority boundaries;
- explicit schema versions;
- full lowercase 40-character Git SHAs;
- lowercase `sha256:<64 hex>` content digests;
- RFC 3339 UTC timestamps ending in `Z`;
- sorted, unique path and enum arrays when canonical hashing depends on order;
- deterministic JSON serialization with sorted keys and compact separators for
  canonical digests.

Unknown fields fail closed in evidence, decision, authority, and execution
objects. Product-facing metadata may be more permissive only outside those
control boundaries.

## 5. Compatibility

- Version schemas independently from implementations.
- Additive changes may remain within a version only when old consumers can
  ignore them safely and the object is not closed at an authority boundary.
- Closed control objects require a new schema version for any new field.
- Breaking changes require migration instructions, affected-consumer inventory,
  compatibility window, rollback path, and reproducibility evidence.
- Deprecated aliases remain discovery aids; they do not create a second ID.
- Provider adapters translate formats. They do not redefine canonical meaning.

## 6. Idempotency, retries, and partial failure

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

## 7. Event and state rules

- Events are append-only observations, not mutable truth records.
- Every event carries event ID, schema version, occurred-at time, observed-at
  time, source identity, producer identity, and correlation/idempotency key.
- Reprocessing produces the same projection or an explicit superseding event.
- State transitions are validated against the current version and authority
  gate; out-of-order or duplicate events fail closed or reconcile explicitly.
- Deletion and retraction preserve tombstone lineage rather than erasing the
  prior claim.

## 8. Platform boundaries

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

## 9. API and adapter behavior

- Validate inbound objects before side effects.
- Return machine-readable error codes plus safe human explanations.
- Separate read, propose, approve, execute, publish, and revoke operations.
- Do not combine observation with promotion in one endpoint.
- Include authority scope and effect class in every effectful request.
- Pin or report consequential provider/model/API versions.
- Preserve upstream provenance through each adapter and output receipt.
- Use least-privilege credentials owned by the runtime boundary, never embedded
  in prompts, fixtures, receipts, or browser artifacts.

## 10. Human gates

Interoperability cannot manufacture authority. The receiving system verifies:

1. the exact subject;
2. the evidence receipt and evaluator identity;
3. the decision's current-head match;
4. the required authority control;
5. the bounded effect and rollback/revocation path.

A changed head, expired approval, scope mismatch, missing authority reference,
or unresolved partial failure blocks the effect.

## 11. Minimum conformance tests

Every interoperable control should test:

1. unknown-field rejection;
2. malformed and non-UTF-8 input;
3. full-SHA and digest validation;
4. exact-head mismatch and stale-decision rejection;
5. duplicate/reordered event handling;
6. idempotent retry after timeout;
7. partial-write recovery;
8. projection drift and rebuild;
9. provider/adaptor version mismatch;
10. capability-without-authority rejection;
11. candidate-location-without-canon rejection.

## 12. Promotion rule

A passing conformance suite proves only the tested contract at the named
versions. Promotion, merge, canon, release, deployment, publication, and runtime
mutation remain separate human- or policy-authorized events with their own
receipts.
