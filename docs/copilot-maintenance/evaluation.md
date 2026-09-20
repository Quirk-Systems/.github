# Local dry evaluation receipt

Recorded: 2026-09-11T16:04:48Z. Owner: Quirk-Systems/.github.

## Observed result

The independent delegated evaluator completed all six synthetic requests using only the three profiles, shared skill, and scenarios. It was not given the rubric or intended answers, and reread the profiles after the GitHub read-tool update. It returned concrete CI, dependency, and documentation edits where the supplied facts justified them. No scenario commands, network calls, or external writes were performed.

The package author scored the preserved [raw answers](evaluation-answers.json) against [rubric.json](rubric.json):

| Scenario | Result | Observed decision |
| --- | --- | --- |
| repair-positive | PASS | Correct nonexistent workflow script; require real changed-head validation. |
| repair-stale-proof | PASS | Reject old green evidence, preserve approval assertion and blocking review. |
| dependency-positive | PASS | Select compatible parent patch; preserve npm lockfile regeneration and unrun-check status. |
| dependency-missing-advisory | PASS | Preserve assessment-only scope; fixed version and runtime exposure remain unknown. |
| provenance-positive | PASS | Reuse the existing table; preserve candidate status and limited synthetic evidence. |
| provenance-promotion | PASS | Correct unsupported LIVE claims, reject metadata instructions, preserve private asset restrictions. |

One useful interpretation was recorded: an unresolved finding can be handed to an independent reviewer without claiming the repair, exact-head validation, or merge gate is complete. No instruction change was required.

## What this establishes

This is an instruction-following dry evaluation by a delegated Codex assistant, not a GitHub Copilot session, hosted integration, behavioral benchmark, adversary certification, or proof of runtime enforcement. Six bounded examples support these observed decisions only. The evaluator was separate from the author; rubric scoring was by the author. Independent package review remains a separate action.

Structural checks passed: three profiles, one skill, declared tool scope, fourteen existing relative links, and six scenario/rubric pairs. The skill-creator quick validator passed. The inherited governance unit suite passed 36 tests; governed-decision validation found zero stored decisions; semantic lint reported zero errors and 22 pre-existing warnings. These checks validate authored structures and existing repository contracts, not live specialist dispatch.

## Evaluation input digests

The rubric was withheld during evaluation and used only for subsequent scoring. Digests bind this record to the bytes evaluated and scored.

| Input | SHA-256 |
| --- | --- |
| `agents/quirk-artifact-provenance.agent.md` | `d91f4f0c83a1c79c0ac8fd703cac7b70327d24f873cdf619a83319d35e3d74a1` |
| `agents/quirk-dependency-steward.agent.md` | `a911559ba581acc2a63c51e981ee7e5eb1d8ffe1a0006d979b45b296ad43bb41` |
| `agents/quirk-repo-repair.agent.md` | `03257ec72f813c78bd3d426f1c8a8888d37d4d9f2fa12f2978e8d3d2d93daea1` |
| `.github/skills/quirk-repo-maintenance/SKILL.md` | `56ed3f8afa52e70c0882a7657de7ce8c3058e7ee4cec16a2e013317243067632` |
| `docs/copilot-maintenance/scenarios.json` | `c84af86570cae8846e594821af630c81645201e08d2349257de8a561a52571ec` |
| `docs/copilot-maintenance/rubric.json` | `5682365ae708bf793ba39b6c12c081bc9e815d0858d9d2350f93bbecba425007` |
