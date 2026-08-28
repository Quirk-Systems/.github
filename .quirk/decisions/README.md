# Governed decisions

This directory holds optional `governed-decision.v1` JSON records. A record
captures a disposition for an exact repository/base/head/path subject and cites
receipts that cover that exact head.

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
