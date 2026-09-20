# Quirk design system contract

Status: **candidate contract; candidate values**  
Source of truth: `.quirk/design/tokens.json`  
Contract: `.quirk/schemas/design-tokens.schema.json`  
Implementation owner: `Quirk-Systems/quirk-design`  
Authority effect: **none**

This repository owns the **contract** for Quirk's design tokens: the file
format, naming rules, alias grammar, validation, and projection commands. It
does not own the look. `quirk-design` owns the visual decisions and can replace
every seed value through a reviewed change to the token file. Products consume
projections; nothing edits a projection by hand.

## Format

A constrained subset of the W3C Design Tokens Community Group format:

- Groups are objects whose names are lowercase kebab-case (`color`, `font`,
  `space`, `ink-muted`). A group may declare `$type`, `$description`,
  `$extensions`; children inherit `$type`.
- Tokens are objects with `$value` and optionally `$type`, `$description`,
  `$deprecated`, `$extensions`.
- Types: `color` (`#rrggbb` or `#rrggbbaa`, lowercase), `dimension`
  (`{value, unit: px|rem}`), `duration` (`{value, unit: ms|s}`),
  `fontFamily` (string or ordered list), `fontWeight` (1–1000 or a named
  weight), `cubicBezier` (four numbers), `number`, `typography`, `shadow`.
- Aliases are strings of the form `{color.ink}`; they must resolve, must not
  cycle, and inherit the target's type.
- The root carries `$extensions.quirk` with `status`, `version`,
  `implementation_owner`, and `authority_effect: none`.

## Commands

```sh
python scripts/design_tokens.py validate .quirk/design/tokens.json
python scripts/design_tokens.py emit-css .quirk/design/tokens.json --prefix quirk > build/tokens.css
python scripts/design_tokens.py emit-json .quirk/design/tokens.json > build/tokens.flat.json
```

Consumers commit generated projections only inside their own repository and
regenerate them from a pinned commit of this file; a projection is stale the
moment the source commit moves.

## Seed semantics (candidate)

| Group | Intent |
| --- | --- |
| `color.ink*`, `color.paper*`, `color.slate*` | Two surface families (paper, slate) with one ink pair. |
| `color.signal`, `color.signal-soft` | The single accent. Quirk does not use decorative color; the accent means "act here". |
| `color.verify`, `color.infer`, `color.unknown` | The three evidence states every Quirk surface must be able to show: VERIFIED, INFERRED, UNKNOWN. |
| `space.*` | 4px base scale. |
| `radius.*` | `sharp` for data, `soft` for controls, `round` for pills. |
| `font.*` | Text and mono families, three weights, six sizes, two line heights. |
| `motion.*` | Two durations, two curves. Motion communicates state change; nothing animates for its own sake. |

The evidence-state colors are the only semantic requirement this contract
imposes on a Quirk interface: if a surface shows a claim, it must be able to
show which of the three states the claim is in.

## Change classes

- Adding or renaming a group or token: **domain extension** until
  `quirk-design` adopts it, then a versioned bump of `$extensions.quirk.version`.
- Changing a value: **projection change** for consumers, recorded by a version
  bump and a receipt.
- Changing the format or schema: **canonical change**; update the schema, the
  validator, its tests, and this document in one reviewed change.

## Not in scope here

Component libraries, iconography, layout systems, brand voice, and any
rendered asset. Those belong in `quirk-design` (implementation) and, for
voice and naming, the `quirk-brand-system` skill. Naming here follows that
skill's rule: a token name must identify, brand, and deploy without
explanation.
