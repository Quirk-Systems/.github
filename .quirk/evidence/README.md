# Evidence receipts

This directory contains JSON receipts governed by
`.quirk/schemas/evidence-receipt.schema.json`. The validator discovers every
`*.json` file below this directory. A README or other policy file is not a
receipt and is not excluded from pull-request coverage.

A verified receipt follows a two-commit protocol. First commit the subject and
run the recorded tests. Then generate and commit the receipt. The receipt binds
the subject base and commit, its exact no-renames diff, Git blob IDs, SHA-256
bytes, bounded claim paths, and the results reported by the author.

Each claim carries a bounded non-authority `claim_type` and a structural
`authority_effect` whose only valid value is `none`. Free-text statements are
informational and cannot override that structural boundary.

The validator never executes a receipt's recorded commands. Those commands are
evidence metadata, not instructions. Passing validation proves identity and
recorded outcomes; it does not independently prove semantic sufficiency and it
does not grant canon, admission, activation, deployment, or production status.

`unverified` and `retracted` correction receipts preserve a reason,
observations, and external claim references. They never satisfy pull-request
coverage.

Pull-request coverage is freshness-sensitive. A receipt stops covering a path
as soon as a later commit touches that path. A new verified receipt whose subject
includes the latest path change restores coverage.

The stable preference concept ID remains `registry.preference`. Its canonical
display name is now **Preference Graph**. **Quirk Preference Core** is retained
only as a deprecated alias so older documents can be found. This naming
projection is anchored in the `quirk-core` preference-language source at commit
[`1b70bce23e88ecb97d652bd8a50896c8f4bc64c4`](https://github.com/Quirk-Systems/quirk-core/blob/1b70bce23e88ecb97d652bd8a50896c8f4bc64c4/docs/canon/preference-language.md);
it is not a new admission.
