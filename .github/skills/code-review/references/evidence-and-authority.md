# Evidence and authority

## Revision binding

Record the repository, full 40-hex base/head revisions, exact changed-path set, and immutable blob/file links where available. Head identity alone does not identify a reviewed patch. Capture evidence at collection time, not by retroactively adding the current SHA to an older result. For local tests, record checkout revision and dirty/untracked changes affecting execution. For synthetic merge checks, preserve their execution SHA and the documented relation to head/base.

Recheck current head before reporting and before each authorized write. If it changes, archive the earlier review as stale; rereview the delta, integration effects, and relevant validation. A head unchanged since review does not prove base, rules, approvals, or required checks are unchanged. Freshness is an observed timestamp and revision relationship, not an invented universal expiration interval.

## Repository receipts

Read and follow the repository's receipt schema and coverage/freshness rules. Do not copy a template identifier into a governed receipt. Handle deleted files with the contract's prescribed base hash/tombstone and renamed files with both relevant paths. Bind receipt subjects and test execution honestly; if the repository uses a subject commit followed by a receipt-only commit, record both and validate ancestry and subsequent changes.

Keep generated output ledger provenance consistent with the actual destination. Do not label preview, local validation, hosted validation, and post-merge observation as interchangeable proof. File hashes attest content identity; they do not attest human decisions.

For receipt-bearing changes, inspect the repository's permitted merge methods. When subject ancestry is enforced, require an ancestry-preserving merge commit; squash/rebase can invalidate receipts even when content matches. Do not claim that skill instructions disable those buttons.

## Authority record

Record the actor/source, action, repository and object scope, head SHA, conditions, timestamp, and expiry/revocation evidence when applicable. If a supplied decision omits detail, preserve its actual wording and mark unestablished fields UNKNOWN; clarify only when the ambiguity blocks an action. The user can authorize several actions together. Separate records do not demand separate permission prompts.

Review permission is not merge permission. Human approval does not automatically authorize deployment or canon promotion. A repository role shows capability, not task-specific consent. An agent recommendation is not a human disposition. A user instruction to merge does not waive applicable repository self-review or protection rules.

Use available expected-head arguments when merging. Recheck results after an authorized action and record actual outcome IDs; if an API errors, record failure rather than asserting a side effect occurred. Do not store access tokens, private keys, or credentials in packets.
