# Quirk Systems

**A stateful human–agent operating system for turning evolving intent into governed action, durable knowledge, and an inspectable shared world.**

Quirk connects humans, agents, repositories, tools, evidence, and decisions through one persistent operating loop:

```text
async preparation
→ real-time session
→ async execution
→ real-time review
→ persistent world update
```

The conversation is not the system. The agent is not the system. The repository is not the system.

**The governed, versioned state connecting them is the system.**

## Public ecosystem

- [`project-scaffold`](https://github.com/Quirk-Systems/project-scaffold) — implemented Quirk kernel and operator codebase (public, active; its relationship to `quirk-os` awaits an owner topology decision)
- [`quirk-os`](https://github.com/Quirk-Systems/quirk-os) — candidate Quirk OS runtime and Skill runtime/projection architecture (public, active, not yet canonical)
- [`quirk-core`](https://github.com/Quirk-Systems/quirk-core) — shared contracts, schemas, validators, and canonical-candidate definitions (public, classification pending review)
- [`quirk-feed`](https://github.com/Quirk-Systems/quirk-feed) — knowledge-feed and discovery surface
- [`quirk-generator`](https://github.com/Quirk-Systems/quirk-generator) — multi-model visual-generation instrument
- [`.github`](https://github.com/Quirk-Systems/.github) — public governance, semantic authority, agent instructions, and reusable organization workflows

The full truthful topology inventory for the 2026-08-21 cut is projected in [`docs/PORTFOLIO.md`](https://github.com/Quirk-Systems/.github/blob/main/docs/PORTFOLIO.md).

## Operating principles

- **Git-canonical, runtime-projected.** Canonical definitions are versioned and reviewed; databases and interfaces are projections.
- **Human authority over consequential change.** Agents prepare, propose, execute bounded work, and return evidence.
- **Containment before capability.** Every agent and automation receives explicit objectives, permissions, limits, and shutdown authority.
- **Second consumer before extraction.** Shared modules become packages or repositories only when real reuse, security, scaling, or release boundaries justify the split.
- **Every decision updates the world.** Accepted work changes canonical state, not merely a conversation or task status.

## Repository strategy

The organization’s repository classes, lifecycle rules, creation gate, extraction criteria, and management system are defined in [`docs/REPOSITORY_STRATEGY.md`](https://github.com/Quirk-Systems/.github/blob/main/docs/REPOSITORY_STRATEGY.md). Agents working in any Quirk repository start from [`AGENTS.md`](https://github.com/Quirk-Systems/.github/blob/main/AGENTS.md).

## Contributing

See [CONTRIBUTING](https://github.com/Quirk-Systems/.github/blob/main/CONTRIBUTING.md), our [Code of Conduct](https://github.com/Quirk-Systems/.github/blob/main/CODE_OF_CONDUCT.md), and the [security policy](https://github.com/Quirk-Systems/.github/blob/main/SECURITY.md).
