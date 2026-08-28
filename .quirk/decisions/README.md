# Governed decisions

This directory holds optional `governed-decision.v1` JSON records. A record
captures a disposition for an exact repository/base/head/path subject and cites
receipts that declare coverage of that exact head.

Every cited receipt must carry an immutable locator:

```yaml
receipt_id: qreceipt.example
source_repository: owner/repository
source_commit: 40-character Git SHA
source_path: .quirk/evidence/qreceipt.example.json
receipt_sha256: sha256:<64 lowercase hex>
covered_head_commit: 40-character Git SHA
```

The validator checks that this locator is complete, immutable, safe, and
internally consistent with the decision subject. It does **not** fetch an
external repository or independently prove that the cited bytes exist. Before a
human or system relies on a decision, the receiving boundary must materialize
`source_repository@source_commit:source_path`, validate the receipt and digest,
and verify its Git subject against the actual repository bytes.

A governed decision is deliberately non-authoritative:

```yaml
authority:
  effect: none
  required_next:
    - merge
```

`required_next` names gates still needed. It does not satisfy them. The record
becomes stale for current action when the candidate head changes, while remaining
valid historical lineage for the head it names.

Validate records with:

```sh
python scripts/validate_governed_decisions.py \
  --repository Quirk-Systems/.github \
  --root . \
  --decisions .quirk/decisions
```

The canonical digest is SHA-256 over UTF-8 JSON serialized with sorted keys and
compact separators after removing `decision_sha256`.
