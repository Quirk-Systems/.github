# Brief: Poster claim binding

Status: draft
Owner: @bryansayler
Repository: `Quirk-Systems/.github`
Date: 2026-09-20
Authority effect: **none**

## Context

The ask arrived as `/quirk-brief` with five images attached and no accompanying
text. Four are Quirk posters: "Yet To Be Discovered Quirk Studio", "Quirk Black
Box Inspection OS v1 — Kickoff Edition", "Quirk Ω — The Weird-to-Wealth
Catalog", and "Quirkverse Materialize". The fifth is third-party (a CLAUDE.md
guide credited to AllyHub AI via the AIToolsPromptWorkflow subreddit); it is the
source of the visual format, not a subject of this brief.

The outcome below is INFERRED, not quoted. The prior turn in this session
audited five LinkedIn infographics and recommended a claim card: slop's visual
grammar carrying a receipt payload, where every tile has a status label and a
date. This brief applies that recommendation to Bryan's own posters, which
exhibit the same defect class the audit found in the LinkedIn set.

Repository state at `e1782a1775cd0688c147e92e8ae7d5335bac7e67`. `.quirk/registry.json`
holds 26 canonical concepts. `AGENTS.md` establishes that canon lives in
`.quirk/` and that docs, prompts, manifests, and UIs are projections that must
not redefine it. A poster is such a projection; nothing currently treats it as one.

## Outcome

A Quirk poster's factual assertions are checkable before it is published: each
assertion exists as a row in a claims file carrying a status label and a date,
and a validator exits non-zero when a poster asserts something the claims file
does not carry or carries a claim past its freshness window. Observed by running
the validator against a claims file for one poster and seeing it name that
poster's duplicate column and its undated tool versions.

## Constraints

- Python 3.12 standard library only; no third-party imports in `scripts/` or `tests/`.
- Authority effect stays `none`. The validator reports; it does not gate publication.
- No new repository. No new registry concepts admitted by this brief.
- Under the two-commit receipt protocol, subject and receipt commit separately.
- The posters' existing visual density is not a defect to be designed away. The
  claim binding attaches to the content, not the art direction.

## Semantic impact

- Change class: domain extension
- Concept IDs touched (from `.quirk/registry.json`): `concept.projection` and
  `concept.provenance` are consumed, not redefined. `asset` (alias `Artifact`,
  parent `system.quirk`) is the entity a poster projects.
- Proposed new concepts: none. The four posters name roughly forty unregistered
  terms (Overswerve, Override, Quirk Subrata, Quirk Studio, Quirk Ω, Sentinel,
  and the twelve Creative Moves among them). `python3 scripts/quirk_concept.py
  inspect` returns "Unknown concept" for studio, overswerve, override, subrata,
  omega, quirkverse, claim, and poster. They stay unregistered here; admission
  is a separate `canonical-change` PR under `docs/QUIRK_SEMANTIC_GOVERNANCE.md`.
- Collision check: "claim" in this brief means a poster assertion, which is
  narrower than the evidence-receipt `claim_id` in `.quirk/evidence/`. If the
  term is ever registered, that collision must be resolved first.

## Evidence

- VERIFIED — Quirk Ω Level 1 has two columns titled "Intelligence". Columns
  seven and eight carry near-identical creative-media item lists (Writing, Film,
  Video, Animation, Characters, Comics, Worldbuilding, Voice, Performance,
  Improvisation). Source: the poster image as supplied.
- VERIFIED — Quirk Black Box section numbering runs 1 through 9, then 12, then
  11, then 12. There is no section 10 and there are two sections numbered 12.
- VERIFIED — A Quirk Black Box panel header reads "SCUAL OPERMLLA" above a risk
  scoring formula. The header is garbled.
- VERIFIED — Quirk Studio lists thirteen reuse categories in its right column
  and shows twelve in its bottom gallery; "Quirk Properties" is omitted from the
  gallery. The label "POP CULTURAL A" is truncated.
- VERIFIED — None of the four posters carries a date or an as-of marker.
  Staleness cannot be assessed from the artifact at all. This is the root
  finding; the individual defects below are downstream of it.
- INFERRED — Quirkverse Materialize names "Claude OPUS 4" in its tooling
  arsenal, which is behind the current Claude 5 family. The reference is this
  session's runtime context, not a citable source.
- UNKNOWN — Currency of the other tools named on the same poster (GPT-4o,
  Gemini 1.5 Pro, Midjourney V6.1, Suno 4.5, Runway GEN-3). Resolved by a live
  version check against each vendor.
- UNKNOWN — Method behind the Quirkverse Materialize character scores (99, 97,
  93, and 88, each out of 111). No rubric appears on the poster. Resolved by
  Bryan naming the rubric or marking the scores as editorial.
- UNKNOWN — Whether the 111 Proactive Prevention Goals claimed by Quirk Black
  Box exist. One row (QPG-001) is shown. Resolved by producing the dataset.
- UNKNOWN — Third-party claims in the fifth image about Claude Code behavior
  (a 300-line skim threshold, a memory path, a 200-line load limit). Out of
  scope; this repository's own `CLAUDE.md` governs here.

## Action

Smallest coherent intervention, in wave order:

1. This brief at `docs/briefs/2026-09-20-poster-claim-binding.md`, with a receipt.
2. `schemas/poster-claim.schema.json` — the claim row shape.
3. `.quirk/posters/quirk-omega.claims.json` — one worked claims file for the
   Quirk Ω poster, as an example living in this repository.
4. `scripts/validate_poster_claims.py` — checks that every claim row validates
   against the schema, carries a status label and a date, and is within its
   freshness window; plus `tests/test_poster_claims.py`.

Waves 2 through 4 are the plan's scope, not this brief's. This brief commits
wave 1 only.

## Verification

For wave 1: `scripts/validate.sh` exits 0, and the pull-request gate simulation
in `scripts/validate_evidence_receipts.py` reports no missing or stale path for
the brief. For waves 2 through 4, the observable condition in Outcome is met
when the validator, run against the worked claims file, names the duplicate
Level 1 column and the undated tool versions and exits non-zero.

## Risk

- The load-bearing assumption is a reversal. Today the arrow runs poster to
  claims, reverse-engineered by reading the image. The outcome needs claims to
  poster, with the art rendered from the data. The four posters were made in an
  image tool, not generated from a file, so the binding does not hold until the
  authoring order changes.
- A validator nobody runs is worse than no validator, because it reads as
  coverage. Containment: it stays advisory with authority effect `none` until
  the authoring order changes.
- Scope creep toward admitting the forty unregistered names. Containment: the
  Semantic impact section above admits none of them.

## Residue

Two decisions need Bryan and are not granted here.

1. Are posters governed artifacts at all? They may be deliberately ungoverned
   creative output, in which case this brief should be rejected rather than
   narrowed.
2. Does poster authoring invert, so that the claims file is written first and
   the poster is rendered from it? Without this the outcome is unreachable.

Deliberately excluded: admission of any concept named on the four posters;
correction of the specific defects listed under Evidence, which is content work,
not contract work; and the "What The Quirk Fuck" series name, offered once in
the prior turn and undecided.

Unknown: which repository owns production poster claims files. `Quirk-Systems/.github`
is not a product and hosts validators, so the worked example belongs here but
the production location does not.

This brief grants no canon, no admission, no authorization to build waves 2
through 4, and no publication. The plan and its receipts still go through review.
