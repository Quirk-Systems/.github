---
name: "quirk-dataset-card"
description: "Write or update a dataset-card.json that documents a dataset's source, collection, structure, license, classification, intended and forbidden uses, and known limitations before anything consumes it."
---

# Quirk dataset card

No dataset is consumed by a Quirk validator, evaluation, model, or product
without a card. The contract is `.quirk/schemas/dataset-card.schema.json`;
the example is `templates/dataset-card.json`; cards live under `datasets/<name>/`.

## Procedure

1. **Locate the data by immutable identity**: repository, 40-character
   commit, paths. If the data lives outside Git (object store, database), the
   card names the content digest and the boundary that owns it; the data does
   not come into this repository.
2. **Answer the collection questions honestly**: method, period, whether any
   personal data is present, and on what consent basis. Unknown is a valid
   answer written as UNKNOWN in `known_limitations`; a guess is not.
3. **Describe structure**: format, what one record is, where the schema lives,
   splits (empty list if none), and the record count at the named commit.
4. **Record rights**: SPDX license and rights holder. If either is unclear,
   `authority.required_next` includes `license-clearance` and the status stays
   `draft`.
5. **Write intended use, out-of-scope use, and known limitations** as short
   imperative lines. Every dataset has at least one of each.
6. **Validate**: `python scripts/validate_templates.py` (validates every card
   under `datasets/`). Add the card to `datasets/README.md`.
7. Ship with a receipt.

## Do

- Set `data_classification` conservatively; downgrade only through review.
- Link evidence receipts that produced or validated the data in
  `provenance.evidence_receipts`.
- Bump `status` from `draft` to `candidate` only after the count and digests
  are real.

## Don't → Do instead

- Don't copy data into `datasets/` to make the card easier → point at the
  owning boundary and keep the card small.
- Don't write "no personal data" without checking → inspect a sample and
  say what was inspected under `known_limitations`.
- Don't treat a valid card as registry admission or publication → name the
  gate under `authority.required_next`.

## Reference

`datasets/README.md`, `datasets/quirk-governance-corpus/dataset-card.json`
(a real, validated example), `docs/governance/INTEROPERABILITY.md` §9 for
platform boundaries.
