# Project Scaffold and Quirk OS Separation Record

Status: **SUPERSEDED — RENAME CANCELLED**  
Decision date: **2026-08-11**

This file formerly instructed maintainers to rename
`Quirk-Systems/project-scaffold` to `Quirk-Systems/quirk-os`. That operation
is cancelled and must not be executed.

## Canonical topology

| Repository | Role | State |
| --- | --- | --- |
| `Quirk-Systems/project-scaffold` | Public GitHub template, runnable scaffold, and reference implementation | Active |
| `Quirk-Systems/quirk-os` | Separate operating-system boundary | Reserved; requires independent admission |

Project Scaffold does not become Quirk OS because it contains Quirk-domain
examples, agents, pipelines, or runtime-shaped capabilities. Capability does
not imply authority, and adjacency does not erase repository boundaries.

## Prohibited legacy actions

- Do not rename, move, archive, or repurpose either repository to clear a name.
- Do not rewrite Project Scaffold's manifest, package, or README identity to
  `quirk-os`.
- Do not treat the closed issue #75 or PR #76 as current authority.
- Do not claim the minimal `quirk-os` repository inherited Project Scaffold's
  history, implementation, evidence, or release status.

## Required future path

Quirk OS must proceed as an independent candidate:

1. establish its own purpose, owner, canon, contracts, and non-goals;
2. define runtime, authority, data, security, and interoperability boundaries;
3. implement and test its claimed capabilities;
4. pass Quirk admission and applicable Ship It Without gates;
5. receive explicit owner approval before active, current, live, chooseable, or
   useable status.

Project Scaffold may remain a downstream fixture or source of deliberately
selected patterns. Any transfer occurs through explicit, versioned changes—not
repository identity laundering.

## Evidence

- Project Scaffold canonical identity:
  https://github.com/Quirk-Systems/project-scaffold/blob/main/docs/canon/PROJECT_SCAFFOLD_IDENTITY.md
- Superseded rename issue:
  https://github.com/Quirk-Systems/project-scaffold/issues/75
- Closed rename implementation:
  https://github.com/Quirk-Systems/project-scaffold/pull/76

The historical rename instructions remain available in Git history.
