# Quirk Systems Repository Strategy

Status: **Truthful topology snapshot — 2026-08-21 UTC**
Authority: `Quirk-Systems/.github`

The machine-verifiable source for this strategy is
[`.quirk/repositories.json`](../.quirk/repositories.json). It records all 17
visible organization repositories and two materially related adjacent commerce
candidates. [`scripts/validate_topology.py`](../scripts/validate_topology.py)
rejects stale identities and incomplete boundary records.

## Current topology

| Boundary | State | Responsibility |
| --- | --- | --- |
| `.github` | active canon | Public organization policy, profile, registry, and reusable workflows |
| `.github-private` | active canon | Private policy and sensitive organization controls |
| `project-scaffold` | active reference | Reusable runnable application scaffold; not a kernel |
| `quirk-os` | candidate kernel | Contract-first operating foundation pending human admission and corrected evidence |
| `quirk-core` | candidate Preference Graph doctrine | Versioned Preference Graph language and storage doctrine; no admitted runtime or declared consumer |
| `quirk-feed`, `quirk-generator` | active product boundaries | Discovery interface and bounded visual-generation instrument |
| `quirk-beauty`, `quirk-pet`, `quirk-town` | candidate realms | Bounded proofs with no inferred canonical authority |
| `Quirk`, `quirk-data`, `quirk-me`, `quirk-run`, `quirk-dog`, `quirk-music`, `quirk-preference` | reserved names | No implementation, consumer, owner, or independent boundary is evidenced |
| `bryansayler/quirk-commerce`, `bryansayler/quirk-beauty-store` | adjacent candidates | Private commerce candidates; neither is organization canon or deployable without payment/PII ownership |

## Governing rules

- A repository name is not a capability, admission, deployment, or named owner.
- `project-scaffold` remains a reference surface. Its examples do not grant
  system authority.
- `quirk-os` is implemented enough to evaluate, but remains a candidate until
  a human admits it on corrected, reviewable evidence.
- `quirk-core` currently owns candidate Preference Graph language and storage
  doctrine, not an admitted runtime. A distinct owned contract and consumer
  are required before it remains separate.
- Reserved repositories remain names until an independent consumer, privacy or
  credential boundary, runtime/release requirement, or named owner justifies
  implementation.
- The two commerce candidates are outside organization canon. Select at most
  one only after assigning product, payment, PII, and security ownership.

## Repository creation and extraction gate

Before creating or extracting a repository, record all of the following:

1. A unique responsibility and primary class.
2. The canonical source and each consumer or dependency.
3. The named owner or explicit `OPEN` owner state.
4. The deployment, security, privacy, credential, and data boundary.
5. A real second consumer, independent runtime/release, or justified isolated
   boundary.
6. An extraction trigger and a retirement or merge-back condition.
7. Evidence anchors that a reviewer can inspect.

The default is to keep work in its existing boundary until those facts exist.

## Pull-request control record

[`.quirk/manual-prs.json`](../.quirk/manual-prs.json) is the complete ledger
of the 27 open non-Dependabot PRs at this snapshot. Its decisions are
recommendations and evidence records, not automatic GitHub actions:

| Decision | Meaning |
| --- | --- |
| `merge` | Topologically sound after current validation |
| `revise` | Keep the PR but repair evidence, scope, or checks |
| `hold` | Preserve the candidate while a named human decision is unresolved |
| `supersede` | Preserve history and replace it with the recorded narrower successor |
| `close` | No independently reviewable delta or satisfiable current action remains |

Any later decision must update the ledger with the acting human, timestamp,
and successor or closing evidence. The current inventory and ledger are facts
for this cut; they do not grant admission, deployment, or owner authority.
