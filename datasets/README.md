# Datasets

Owner: `Quirk-Systems/.github`  
Authority effect: **none**

This directory holds **dataset cards**, not datasets. A card is a
`dataset-card.json` validated against `.quirk/schemas/dataset-card.schema.json`
plus a short `README.md`. The data itself stays where it is owned; large or
sensitive data belongs behind the boundary that `Quirk-Systems/quirk-data`
reserves, never in this public repository.

A card exists so that any agent or human can answer, before consuming data:
where it came from, what one record is, what schema it follows, who holds the
rights, how it is classified, what it is for, what it must not be used for,
and what is known to be wrong with it.

| Card | Describes | Status |
| --- | --- | --- |
| [`quirk-governance-corpus`](./quirk-governance-corpus/) | This repository's own registries, receipts, schemas, and evaluation fixtures as a machine-readable corpus | candidate |

## Adding a card

1. Copy `templates/dataset-card.json` to `datasets/<name>/dataset-card.json`
   and fill every field with real identities (a 40-character source commit,
   real paths, real counts).
2. Write `datasets/<name>/README.md`: two paragraphs, what it is and what it
   is not.
3. Run `python scripts/validate_templates.py` (it validates every card).
4. Ship with an evidence receipt. The `quirk-dataset-card` skill walks
   through this.

A validated card proves shape and internal consistency. It does not admit the
dataset to any registry, clear its license, or prove its quality.
