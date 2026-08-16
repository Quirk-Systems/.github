# Quirk Semantic Governance

Status: proposed canonical policy for Quirk Systems
Version: 0.1.0

## Strategic position

Quirk Systems treats semantic integrity as infrastructure. New products, agents, repositories, assets, capabilities, skills, commands, characters, registries, maps, and strategic initiatives MUST resolve against the Quirk Concept Registry before they introduce new conceptual nouns or redefine existing ones.

The registry is the source. Maps, docs, prompts, APIs, UIs, agent instructions, database projections, diagrams, and repository manifests are projections.

## Layers that must not be collapsed

- **Ontology** — what kinds of things exist.
- **Taxonomy** — how those things are classified.
- **Topology** — how those things connect.
- **Grammar** — what combinations and transformations are legal.
- **Constraints** — what is required, prohibited, or bounded.
- **Semantics** — what a term precisely means.
- **State** — what currently exists and its lifecycle condition.
- **Provenance** — where an assertion or decision came from.
- **Projection** — how canonical knowledge is rendered into a surface.

## Canonical precedence

When Quirk sources disagree, resolve in this order:

1. Explicit canonical registry entry in `Quirk-Systems/.github/.quirk/registry.json`.
2. Approved Quirk Core governance decision that updates the registry.
3. Repository-local `.quirk/manifest.json` domain extension that does not contradict canonical definitions.
4. Current repository documentation.
5. Historical documents, conversations, generated outputs, diagrams, and informal usage.

Higher-precedence sources may deprecate or redirect lower-precedence terms.

## Concept admission grammar

Before creating a new named Quirk concept, answer:

1. **Need** — what existing concept fails to represent the intended distinction?
2. **Kind** — what type of thing is this?
3. **Parent** — what broader concept contains it?
4. **Relations** — what does it require, expose, transform, govern, or conflict with?
5. **Boundary** — what is explicitly *not* this concept?
6. **Provenance** — where did the decision originate?
7. **Projection impact** — which repos, maps, prompts, schemas, agents, docs, or APIs need regeneration or migration?

If these cannot be answered, the proposed name remains experimental rather than canonical.

## Hard invariants

- `Mutate` is a Quirk Move nested under `Transform`; it is not a top-level peer of Transform.
- `Asset` is the canonical reusable-output term; `Artifact` is retained only as an alias/migration term where legacy compatibility requires it.
- `Realm` is a contextual operating environment, not a synonym for ontology, taxonomy, organizational structure, or arbitrary collection.
- Maps and diagrams do not become sources of truth by themselves; they project registry-backed knowledge.
- A repository may extend the canon locally, but may not silently redefine a canonical ID.

## Repository contract

Every active Quirk Systems repository should contain `.quirk/manifest.json` declaring:

- repository identity and domain;
- registry authority and version;
- semantic policy mode;
- local concepts or extension paths;
- projection surfaces that depend on the registry;
- ownership of unresolved semantic debt.

## Change classes

### Canonical change
Changes the shared meaning or hierarchy of Quirk. Requires a registry change and semantic review.

### Domain extension
Introduces a repository-specific concept without changing shared meaning. Requires a local manifest declaration and parent relationship.

### Projection change
Changes docs, diagrams, UI, prompts, APIs, or database representations without changing canonical meaning.

### Migration
Replaces deprecated terms or structures while preserving lineage and redirects.

## Strategic-plan integration

All Quirk strategic planning should include a **Semantic Impact** section alongside product, technical, operational, and risk considerations. Any initiative that creates a new system, framework, method, protocol, registry, agent family, world/realm/location structure, or branded capability must explicitly identify whether it is:

- reusing canon;
- extending canon;
- changing canon; or
- merely projecting canon.

This keeps conceptual proliferation from becoming architectural debt.

## Compiler commands

```bash
python scripts/quirk_concept.py lint
python scripts/quirk_concept.py inspect move.transform.mutate
python scripts/quirk_concept.py map
```

`lint` is the constitutional check. `inspect` is the semantic resolver. `map` emits Mermaid-ready topology from the registry.

## Rollout sequence

1. Establish central registry and compiler.
2. Add manifests to all active repositories.
3. Add reusable semantic CI and repository calls.
4. Add concept-admission prompts to PR and issue templates.
5. Migrate high-value existing Quirk docs and schemas to canonical IDs.
6. Generate registries/maps/docs from the source rather than manually duplicating them.
7. Extend linting from structural validation into semantic-debt detection, deprecated-term scanning, and collision analysis.
