# Project Scaffold and Quirk OS Boundary Record

Status: **current topology projection**
Authority: [`../.quirk/repositories.json`](../.quirk/repositories.json)

| Repository | Current boundary | Evidence standard |
| --- | --- | --- |
| `Quirk-Systems/project-scaffold` | Public runnable application scaffold and reference implementation | Its examples are reusable patterns, not kernel authority |
| `Quirk-Systems/quirk-os` | Public candidate kernel boundary | Human admission, a named owner, corrected evidence, reconciled gates, and a canonical manifest are required before active status |

These repositories have separate identities, histories, and authority. A
capability demonstrated in the reference scaffold does not establish system
authority. A repository's existence does not establish its admission,
deployment, or production proof.

Patterns may move between boundaries only through explicit, versioned,
reviewable changes that name the source, destination, authority, and evidence.
The canonical inventory is the controlling record; this document is a
human-readable projection of it.

## Consequences for review

- Shared policy and reusable workflows belong in `.github`.
- Runnable examples belong in `project-scaffold`.
- Candidate runtime contracts and their admission evidence belong in
  `quirk-os`.
- A PR that conflicts with these boundaries is revised, held, superseded, or
  closed according to `.quirk/manual-prs.json`; the ledger does not perform a
  GitHub action by itself.
