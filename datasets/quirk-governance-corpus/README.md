# Quirk governance corpus

The machine-readable governance state of `Quirk-Systems/.github` treated as a
dataset: the concept registry, the portfolio registry, every evidence receipt,
every JSON schema, the design-token source, and the Copilot evaluation
fixtures. One record is one JSON document. The corpus is what validators,
tests, and evaluations in this repository consume, and it is the smallest
honest example of a Quirk dataset card applied to real data.

It is not a benchmark, not training data, and not an export of any product
or user data. Its record count changes with every receipt; the card pins the
count to the source commit it names. See `dataset-card.json` for the contract
fields and `scripts/validate_templates.py` for the check that keeps the card
valid.
