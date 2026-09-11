# Maintenance decision, evidence, and artifact index

Status: **observed maintenance index**  
Owner: `Quirk-Systems/.github`  
Observed at: **2026-09-11 UTC**  
Authority effect: **none**

This file is a source-linked maintenance index for the exact-head closure program
in [`.github` issue #13](https://github.com/Quirk-Systems/.github/issues/13).
It applies the source-reading posture in
[`quirk-orient`](../../prompt-packs/quirk/prompts/quirk-orient.prompt.md),
the defect triage posture in
[`quirk-review`](../../prompt-packs/quirk/prompts/quirk-review.prompt.md),
the extraction discipline in
[`quirk-compound`](../../prompt-packs/quirk/prompts/quirk-compound.prompt.md),
and the exact-range boundary in [`EVIDENCE_BINDING.md`](./EVIDENCE_BINDING.md).

The table below records what was directly re-read on 2026-09-11. It separates
source material, review state, authorization, and actual repository effects.
Only merged commits and successful post-merge runs are treated as repository
effects. A plan, green check, mergeable state, or draft PR is not by itself an
implementation, enforcement proof, admission, or runtime effect.

| Record | Owner repository | Owning artifact(s) | Source URL | Exact source commit | Relationship | Observed status | Smallest next proof |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `.github#9` exact-range controls | `Quirk-Systems/.github` | `docs/governance/EVIDENCE_BINDING.md`; `.quirk/evidence/2026-08-28-exact-range-decision-spine-f0ece9e7bf65.json`; `.github/workflows/governance-contracts.yml` | [PR #9](https://github.com/Quirk-Systems/.github/pull/9) | `a043f905a5fc57e31b74b4f5c5e4316a42d12485` | `implements` | 2026-09-11: merged to `main`; the older queue head `c848db6cbb83c5919ca19775295d1c534bbbceaf` is historical/stale for current action. | Cite the merge commit plus post-merge evidence instead of relying on the older pre-merge head alone. |
| `.github` run `34619330907` | `Quirk-Systems/.github` | `.github/workflows/governance-contracts.yml` | [run 34619330907](https://github.com/Quirk-Systems/.github/actions/runs/34619330907) | `a043f905a5fc57e31b74b4f5c5e4316a42d12485` | `evidence-for` | 2026-09-11: `Governance Contracts` completed `success` on `main` after merge of `.github#9`. | Re-read logs or emitted artifacts only if a downstream reviewer needs the exact run output. |
| `quirk-core#6` working-intent record | `Quirk-Systems/quirk-core` | `README.md`; `docs/working-intent-2026-09-10.md` | [PR #6](https://github.com/Quirk-Systems/quirk-core/pull/6) | `e7312dcabd21db2b3621cbae2bdde9e05b930eb4` | `references` | 2026-09-11: merged to `main`; it records working intent and observed state, not full repository-policy enforcement. | Use it as source-bound context only; do not treat a merged documentation PR as enforcement closure. |
| `quirk-core` run `34619185134` | `Quirk-Systems/quirk-core` | `.github/workflows/quirk-contracts-conformance.yml` | [run 34619185134](https://github.com/Quirk-Systems/quirk-core/actions/runs/34619185134) | `e7312dcabd21db2b3621cbae2bdde9e05b930eb4` | `evidence-for` | 2026-09-11: `Quirk Contracts Conformance` completed `success` on `main` after merge of `quirk-core#6`. | Re-read the run output only if a later consumer needs the exact conformance evidence. |
| `quirk-core#4` enforcement issue | `Quirk-Systems/quirk-core` | GitHub `main` policy; `contracts/v0.2/`; `.github/workflows/quirk-contracts-conformance.yml` | [issue #4](https://github.com/Quirk-Systems/quirk-core/issues/4) | `c2e2e3fc62e75b7e23eeed4d22b53b967ed7def9` | `blocked-by` | 2026-09-11: open; the issue body still says effective `main` policy readback is missing, so a green workflow run is not closure evidence. | Read back the active branch-protection or ruleset state and preserve the red/green proof PRs as unmerged evidence. |
| `quirk-core#9` clarification PR | `Quirk-Systems/quirk-core` | repository-policy clarification only; no implementation artifact named in the PR body | [PR #9](https://github.com/Quirk-Systems/quirk-core/pull/9) | `b0c45fbe47cfb4fce9149b0496fdf12a0653a427` | `references` | 2026-09-11: open draft clarification PR; issue #17 reports its false automatic-closure keyword was removed. | Keep `quirk-core#4` open until policy readback exists; this clarification PR is not the enforcement proof. |
| `quirk-core#7` negative proof PR | `Quirk-Systems/quirk-core` | `contracts/v0.2` negative-check proof | [PR #7](https://github.com/Quirk-Systems/quirk-core/pull/7) | `d1003b3ef602cf0d957dfeb22106f5078e1514a3` | `evidence-for` | 2026-09-11: open draft; explicitly marked proof-only and unmerged. | Keep it unmerged and use it only after active repository policy is read back. |
| `quirk-core#8` clean control PR | `Quirk-Systems/quirk-core` | unrelated clean-path proof for `frozen-contracts-v0.2` | [PR #8](https://github.com/Quirk-Systems/quirk-core/pull/8) | `b72d869c6bb983a83200aa2e525c24e699ee9689` | `evidence-for` | 2026-09-11: open draft; explicitly marked proof-only and unmerged. | Keep it unmerged and pair it with the negative proof only after the required-check policy is active. |
| `Quirk` lineage record named in issue #17 | `Quirk-Systems/Quirk` | source lineage for oversized PR `#3` as described by issue #17 | [issue #7](https://github.com/Quirk-Systems/Quirk/issues/7) | — | `references` | 2026-09-11: inaccessible/unverified from this repository context; the URL and purpose were preserved from `.github#17`, not re-read here. | Re-read the issue and oversized PR in an authorized repo context before treating the ownership or lineage claim as verified. |
| `.github#14` closure-harness plan | `Quirk-Systems/.github` | `docs/superpowers/specs/2026-08-28-pr-closure-harness-design.md`; `docs/superpowers/plans/2026-08-28-pr-closure-harness.md` | [PR #14](https://github.com/Quirk-Systems/.github/pull/14) | `b3d7eb3e2223b31be63c8812cbba5fcb7b8278aa` | `references` | 2026-09-11: open draft plan with one review comment; its own body says it is not an implemented gate. | Land a separate bounded implementation subject with code, tests, and fresh exact-head evidence; do not infer implementation from a plan or a green check. |
| `.github#15` portfolio correction | `Quirk-Systems/.github` | candidate portfolio-truth registry changes on its own branch | [PR #15](https://github.com/Quirk-Systems/.github/pull/15) | `00f3838d034b7bd93fd22a955c18cea77afe1321` | `references` | 2026-09-11: open draft and being repaired separately. | Let that branch finish its own repair and review; do not duplicate or partially import its registry edits here. |
| `project-scaffold#91` dependency audit | `Quirk-Systems/project-scaffold` | `package.json`; `bun.lock`; `.github/workflows/*` as enumerated by the audit issue | [issue #91](https://github.com/Quirk-Systems/project-scaffold/issues/91) | `af8923fa339033e331a0821aa2afbb8bb2cfbc0d` | `references` | 2026-09-11: open audit; it remains broader than the fast-uri repair and still includes non-fast-uri maintenance. | Keep the parent audit open until the remaining non-fast-uri maintenance items have their own verified closure path. |
| `project-scaffold#108` fast-uri repair | `Quirk-Systems/project-scaffold` | targeted lockfile and dependency-path repair for vulnerable `fast-uri` paths | [issue #108](https://github.com/Quirk-Systems/project-scaffold/issues/108) | `af8923fa339033e331a0821aa2afbb8bb2cfbc0d` | `implements` | 2026-09-11: open bounded repair issue; its body points to a successor draft PR `#109` and keeps `#91` open. | Reproduce the affected paths on the exact head, refresh only the narrow resolver paths, and show validation plus absence of vulnerable `fast-uri` versions. |
| `project-scaffold#84` YAML repair | `Quirk-Systems/project-scaffold` | `package.json`; `bun.lock` | [PR #84](https://github.com/Quirk-Systems/project-scaffold/pull/84) | `ed365f5d03fec0e08cc2cf47f96c0bab372328d8` | `references` | 2026-09-11: closed and not merged; issue #17 classifies its closure as redundant, while the direct re-read here verifies only closed/not-merged status. | Treat it as historical only unless an authorized reviewer re-reads the redundant-closure rationale in its original review context. |

## Negative control: what this index must not infer

- `.github#14` is a plan artifact. Even if it later becomes mergeable or shows
  green checks, that would still not prove a Closure Harness implementation
  exists on `main`.
- `.github` run `34619330907` is evidence for the merged exact-range controls in
  `.github#9`. It is not evidence that `quirk-core#4` enforcement is installed.
- `quirk-core#9` is a clarification PR. Its existence does not close
  `quirk-core#4`, and a successful workflow run there would still not read back
  GitHub policy settings.

## Privacy and inaccessible-source check

- This public repository copies no private document titles, article text, or
  unauthorized asset content into the index.
- Sources that were not re-readable from this repository context are marked
  **inaccessible/unverified** instead of being paraphrased as verified facts.
- The only verified repository effects recorded here are merged commits and
  successful post-merge workflow runs that were directly re-read on 2026-09-11.

Independent review remains required. This index does not close `.github#13`,
admit canon, activate rulesets, or authorize runtime or publication effects.
