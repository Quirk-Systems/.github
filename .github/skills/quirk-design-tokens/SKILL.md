---
name: "quirk-design-tokens"
description: "Add, change, or consume Quirk design tokens from the canonical .quirk/design/tokens.json: validate the source, regenerate projections (CSS variables, flat JSON), and record the change class without editing any projection by hand."
---

# Quirk design tokens

The token file is the source. CSS, Tailwind, Figma, and component themes are
projections regenerated from a pinned commit. Contract and semantics:
`docs/design/DESIGN_SYSTEM.md`.

## Procedure

1. **Consume**: pin the commit of `.quirk/design/tokens.json` you build from,
   run `python scripts/design_tokens.py emit-css .quirk/design/tokens.json
   --prefix quirk` (or `emit-json`), and commit the generated file **in your
   repository** with a header naming the source commit. Never edit it.
2. **Add a token**: choose the group by meaning, name it lowercase kebab-case
   so it identifies, brands, and deploys without explanation, give it a
   `$description`, and prefer an alias to an existing token over a new raw
   value. Run `python scripts/design_tokens.py validate .quirk/design/tokens.json`.
3. **Change a value**: bump `$extensions.quirk.version` (patch for value
   changes, minor for new tokens, major for renames or removals) and note the
   change class in the PR: value = projection change; new token = domain
   extension; format = canonical change.
4. **Remove or rename**: mark `$deprecated` with the replacement alias for one
   minor version before removal, so consumers can migrate.
5. Run `python -m unittest tests.test_design_tokens -v` and ship with a receipt.

## Do

- Keep exactly one accent (`color.signal`). If a second accent seems needed,
  write the brief first.
- Keep the three evidence-state colors (`verify`, `infer`, `unknown`)
  distinguishable from each other and from the accent.
- Use `dimension` objects with units; never bare numbers for sizes.

## Don't → Do instead

- Don't hand-edit a generated CSS or JSON projection → change the source and regenerate.
- Don't introduce neon or decorative color → the palette is two surfaces, one
  ink pair, one accent, three evidence states.
- Don't change the schema to admit a convenience → propose the format change
  as a canonical change with tests.
- Don't treat `status: candidate` values as final → `quirk-design` owns the
  visual decisions; this repository owns the contract.

## Reference

`.quirk/schemas/design-tokens.schema.json`, `scripts/design_tokens.py`,
`tests/test_design_tokens.py`, `docs/design/DESIGN_SYSTEM.md`.
