# Ubuntu 26 runner migration audit — 2026-10-08

Status: observed snapshot; authority effect: none. This document records source inspection, not an admission or compatibility certificate.

GitHub schedules ubuntu-latest migration for October 19–November 19, 2026. [Official announcement](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/) and [runner-image migration issue](https://github.com/actions/runner-images/issues/14748). [Playwright release notes](https://playwright.dev/docs/release-notes#version-161) establish Ubuntu 26 support in 1.61.

This public projection includes only public repository workflow sources. Private repository findings belong in their own review surfaces. The accessible portfolio audit inspected 50 repository records, 20 nonempty trees, and 50 workflow files, including actual pinned reusable targets. Empty repository records were not bootstrapped.

## Public source inventory

| Repository | Observed main head | Direct latest workflows | Assessment |
| --- | --- | --- | --- |
| project-scaffold | `eae6dc9aabb4c63dfe97f72f0cb565266daa709b` | ci.yml, deps-audit.yml | Playwright 1.62.1 supports Ubuntu 26; native package/build proof and E2E still needed. deps-audit installs Bun; no specific OS defect established. |
| quirk-generator | `8b5d979e3c4cb42f076d2bf5836267e290bf873f` | ci.yml | Playwright 1.63.0 supports Ubuntu 26; no frozen install in current workflow. Validate resolved dependency tree before compatibility claims. |
| .github | `eb889adf3009951de873890103199600f4aad20f` | quirk-semantic-governance.yml, reusable-validate.yml | Shared browser path and implicit-system-Python semantic path warrant preflight; 14 other shared workflows already retain Ubuntu 24. |
| quirk-feed | `a338ea3e0158437167cd875bb4655b67c3b9dc68` | ci.yml | Playwright 1.63.0 supports Ubuntu 26; frozen dependencies plus native SQLite, build, browser dependency installation and isolated E2E warrant explicit probe. |
| quirk-os | `03f70e1a790bac09294fe0f31a3c5f0d0fb4418e` | agent-reliability.yml | Python 3.12 setup and pinned eval requirements reduce preinstalled-runtime exposure. Add exact-head Ubuntu 26 fixtures; no Python incompatibility established. Other direct Linux jobs retain Ubuntu 24. |
| quirk-core | `b3162b0cd6dcc6c07570f240ca33c711ed860f0b` | quirk-contracts-conformance.yml | Python 3.12 explicitly installed; jsonschema range floats. Open PR #12 owns locking dependencies; do not duplicate it. |
| greenfield | `6e6d4b425fe9082d469493d64a5b8e12b15dc9da` | None | No direct latest exposure observed. |

## Shared infrastructure and dependency boundaries

- VERIFIED: no observed default-branch caller uses reusable-validate.yml. Its optional Playwright path remains available infrastructure; the new fixture tests it without inventing a consumer.
- VERIFIED: semantic-workflow consumers pin commits 1263f5008838f743b16ee218046e26dac5c9edd8, 92e5b2d928f25d0fedae87aaad2ef764a806065d, 52eed09e4fbb9a08d9d0eba4fc101483241f3965, and 571ecd4f9e1086d3f3cd4c5e6d4a40ae8ea3748d. All inspected target versions select ubuntu-latest. Their code pin does not pin the OS. Existing caller pins remain untouched.
- VERIFIED: current runner inventory lists default Python 3.12.3 on Ubuntu 24 versus 3.14.4 on Ubuntu 26; default Node 22.23.3 versus 24.21.0; GCC and OpenSSL versions also change. Explicit setup actions reduce runtime drift, but do not isolate system libraries or native builds. Image lists are moving snapshots, not immutable guarantees.
- INFERRED: semantic governance, which invokes system Python without setup-python, merits a Python 3.14 probe. No failing deprecated API has been established; retaining all its callers on Ubuntu 24 would be premature.
- VERIFIED: Playwright installs bundled browsers and OS dependencies. Updated system Chrome/Firefox alone is not a defect for this path. Compatibility of installed dependency packages and browser launch must still be tested.
- VERIFIED: SQLite native module builds and framework native binaries are material preflight targets. No unavailable apt package, hard-coded OpenSSL/ICU version, or demonstrated Ubuntu 26 failure was identified in the inspected public workflow commands.

## Migration versus selective Ubuntu 24 retention

| Path | Choose when | Evidence and exit condition |
| --- | --- | --- |
| Keep existing latest label | Exact-head Ubuntu 26 application checks pass | Record image, resolved versions, dependency installation and full app tests; current results remain limited to that image |
| Explicit Ubuntu 26 preflight | Support exists but app proof is missing | Read-only additive job, timeout, no secrets or side effects; preserve existing required-check contexts |
| Temporary Ubuntu 24 retention | Reproducible OS-specific failure or critical unvalidated gate before rollout | Scope to affected job/caller; record failure and independent Ubuntu 24 pass; remove after repaired exact-head Ubuntu 26 pass |

No blanket pin is proposed. Existing Ubuntu 24 governance choices are preserved. No ruleset readback or changes, approvals, merges, deploys, capability grants, canonical changes, or external-service tests are claimed. Review and human merge authority remain separate from evidence.

## Candidate changes and validation limits

Shared reusable validation receives a closed image choice and an exact-head npm/Playwright fixture on Ubuntu 24 and 26. Feed and agent reliability receive additive Ubuntu 26 jobs running existing application/fixture commands. Existing check contexts remain unchanged. Revert the added probe jobs (and the shared optional input) to undo the change. Changelogs accompany each candidate.

Local tests and receipt gates are supplemental. Hosted run IDs, candidate head, image version, dependency output and actual tests must be resolved from the PR before any compatibility claim. Shared fixture success does not certify every package manager, older pinned shared workflow, private app, native dependency tree, or downstream consumer. An additive Ubuntu 26 system-Python job tests the current semantic registry and governance regressions without setup-python. Its result does not retroactively certify older pinned semantic-policy code. Remaining application preflights and pinned-policy revisions remain gaps until independently run.

