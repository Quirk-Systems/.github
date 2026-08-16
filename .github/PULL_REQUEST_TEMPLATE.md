## Summary

<!-- 1-3 bullets explaining what changed and why. -->

-

## Semantic impact

Classify this change:

- [ ] Reuses existing Quirk canon
- [ ] Domain extension
- [ ] Canonical change
- [ ] Projection-only change
- [ ] Migration / deprecation

### Concepts touched

List canonical IDs or proposed new IDs. For each new named Quirk concept, specify its **kind**, **parent**, **boundary**, and **provenance**.

### Collision check

What existing concept could this accidentally duplicate, redefine, or outrank?

### Projection impact

Which docs, maps, schemas, prompts, agents, APIs, UIs, registries, or generated repos must change with it?

## Test plan

<!-- How did you verify this works? Commands, screenshots, links. -->

- [ ]

## Linked issues

<!-- Closes #123, Refs #456, etc. Delete if none. -->

## Checklist

- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Local validation passes (`bun run validate` or repo equivalent)
- [ ] Tests added/updated where it makes sense
- [ ] Docs updated where it makes sense
- [ ] Repository `.quirk/manifest.json` remains valid
- [ ] Semantic governance check passes
- [ ] No canonical concept was silently redefined
- [ ] Deprecated terminology has an explicit migration path
