# Todo: Workspace portfolio plans

Kind: todo  
Status: candidate  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `92e5b2d928f25d0fedae87aaad2ef764a806065d`  
Reviewed: 2026-10-03  
Review by: 2026-10-17  
Derived from: `docs/roadmaps/2026-09-20-org-control-plane.md`, `docs/REPOSITORY_STRATEGY.md`, `docs/governance/WORKSPACE_TOOLING.md`  
Authority effect: **none**

One plan per repository, written from what a 50-repository workspace showed on
2026-10-03, not from repository names. Counts, states, drift, pins, and
validation exit codes are scanner output from these four invocations against
sibling checkouts of each repository that day:

```sh
python scripts/quirk_workspace.py scan
python scripts/quirk_workspace.py drift
python scripts/quirk_workspace.py pins --expect 92e5b2d928f25d0fedae87aaad2ef764a806065d
python scripts/quirk_workspace.py commands --run
```

The `bun install` failures, the hosted Governance Contracts run, and pull
request numbers were observed separately, not by the scanner. A plan here is a
next bounded move, not a classification: classes, lifecycles, and owners
change only through a reviewed inventory change.

## What the workspace showed

- **VERIFIED (scanner) — 50 checkouts**: 11 `CODE`, 9 `DOCS_ONLY`, 30 `EMPTY` (no commits at all).
- **VERIFIED (scanner) — inventory drift**: 32 `OBSERVED_UNCLASSIFIED` (29 empty, plus
  `quirk-arcade`, `quirk-design`, `quirk-skills`) and 1 `NOT_IN_WORKSPACE`
  (`bryansayler/quirk-beauty-store`, which this session could not reach,
  so this is not evidence it is gone). `.quirk/repositories.json` counts 17
  organization repositories; the session saw 49.
- **VERIFIED (scanner, first survey) — floating reusable-workflow refs**: 4 callers of
  `quirk-semantic-governance.yml` used `@main` (`quirk-beauty`, `quirk-feed`,
  `quirk-generator`, `quirk-town`); the 7 pinned callers use 4 different
  `.github` commits.
- **VERIFIED (scanner) — validation**: `bun run validate` exited 0 in `project-scaffold`,
  `quirk-beauty`, `quirk-generator`, `quirk-pet`, `quirk-feed`, and
  `quirk-town`. VERIFIED (observed outside the scanner): in the last two, `bun install --frozen-lockfile` failed
  building `better-sqlite3` in this container (Node 22 here; `quirk-feed`
  pins Node 24), so those passes ran with an incomplete install; whether they
  pass with a complete install is UNKNOWN here and left to their hosted CI.
  `scripts/validate.sh` here exited 2 on the first survey because of the
  stranded receipt below, and 0 on the re-run after its repair.
- **VERIFIED (hosted run, observed outside the scanner) — `main` was red**: Governance Contracts run `37113795859` on `92e5b2d`
  failed on "Validate evidence receipts on main"; repaired in this change.

- **UNKNOWN — `bryansayler/quirk-beauty-store`**: not reachable from this
  session, so nothing about it is observed here.
- **INFERRED — the per-repository plans below**: each next move is a judgement
  from the observations above, not an observation itself.

Checks not run: `actionlint` (not installed in this container); validation
in the 13 repositories with commits but no declared validation command,
`quirk-os` and `quirk-core` among them (the scanner runs only declared
commands); the commerce repositories' own CI; anything in the 30 empty
repositories.

## Per-repository plans

| Repository | Observed | Next bounded move | Gate |
| --- | --- | --- | --- |
| `.github` | CODE, 168 commits, receipt check red on `main` until this change | Extend `drift` into a scheduled report | owner |
| `.github-private` | DOCS_ONLY, 3 workflows pinned to `571ecd4` | Bump caller pins together with the other repositories (below) | owner merge there |
| `project-scaffold` | CODE, `bun run validate` passes, 2 pinned callers on 2 different commits | Move both callers to one reviewed `.github` commit | owner merge |
| `quirk-os` | CODE (Python), 121 commits, 9 workflows, no single local entrypoint | Add a `scripts/validate.sh` that runs what its workflows run, so people and agents can check it in one command | that repository's review |
| `quirk-core` | CODE, contracts, 1 conformance workflow, no manifest | Add `.quirk/manifest.json` declaring the doctrine class the inventory already records | that repository's review |
| `quirk-feed`, `quirk-town` | CODE, pass with incomplete native install | Caller pinned in this change; record the Node version the native build needs in CI and docs | that repository's review |
| `quirk-beauty`, `quirk-generator` | CODE, `bun run validate` passes | Caller pinned in this change | owner merge |
| `quirk-pet` | CODE, passes, pinned to `52eed09` | Move to the common pin | owner merge |
| `quirk-skills`, `quirk-arcade`, `quirk-design` | content present, absent from the inventory | Inventory entries as `OBSERVED_UNCLASSIFIED` facts | owner: inventory schema change |
| `Quirk`, `quirk-data`, `quirk-run`, `quirk-dog`, `quirk-music`, `quirk-preference` | DOCS_ONLY, inventoried as reserved | None; stay reserved | owner, at the quarterly topology review |
| `quirk-me` | EMPTY, inventoried as reserved | None; stays reserved | same |
| 29 empty repositories outside the inventory | EMPTY, no default branch | Record them; do not bootstrap. Each stays empty until it passes the creation gate in `REPOSITORY_STRATEGY.md` §5, or the owner archives it | owner |
| `bryansayler/quirk-commerce` | CODE, one 2025-01-04 commit (a Medusa starter), no validation or test script | None until the owner selects a commerce candidate, as the inventory says | owner |

## Open

- [ ] Merge the four caller-pin pull requests in `quirk-beauty`, `quirk-feed`, `quirk-generator`, and `quirk-town` (owner: @bryansayler; proof: `python scripts/quirk_workspace.py pins --fail-on-floating` exits 0)
- [ ] Choose one reviewed `.github` commit and move every caller to it, `.github-private` and `project-scaffold` included (owner: @bryansayler; proof: `pins --expect <sha>` reports no `OFF_TARGET`)
- [ ] Give `quirk-os` a single local validation entrypoint (owner: @bryansayler; proof: `commands` lists a command for `Quirk-Systems/quirk-os`)
- [ ] Add `.quirk/manifest.json` to `quirk-core` (owner: @bryansayler; proof: `scan` shows `Manifest yes` for `quirk-core`)
- [ ] Re-run this survey at the twice-weekly portfolio review and bump this document (owner: @bryansayler; proof: Reviewed date and Observed head updated)

## Blocked

- [ ] Admit the 32 `OBSERVED_UNCLASSIFIED` repositories to `.quirk/repositories.json` (blocked on: the inventory schema pins the snapshot `2026-08-21`, exactly 19 entries, and 17 organization repositories, so any admission is a schema version change, which `AGENTS.md` puts under Ask first; who can unblock: @bryansayler)
- [ ] Build the scheduled `portfolio-drift.yml` report proposed in `docs/governance/WORKSPACE_TOOLING.md` (blocked on: read access to private repositories from Actions, which means a token or GitHub App the owner provisions, plus a brief naming its kill switch; who can unblock: @bryansayler)
- [ ] Automate caller pin bumps across repositories (blocked on: a workflow with `contents: write` and `pull-requests: write` in other repositories, which is Ask first; who can unblock: @bryansayler)
- [ ] Stop receipts being stranded by squash merges: the PR #14 squash is what broke the receipt check on `main`, and squashing this pull request would strand its own four subject commits the same way. Merge with a merge commit, as PRs #39 and #41 were, and either restrict the repository to merge commits or teach the receipt protocol to re-bind after a squash (blocked on: a repository merge-method setting or a protocol decision; who can unblock: @bryansayler)
- [ ] Decide each empty repository: keep reserved, or archive (blocked on: owner judgement at the quarterly topology review; who can unblock: @bryansayler)

## Done

- [x] Repaired the receipt that the PR #14 squash merge stranded: `qreceipt.pr-closure-harness-plan-followup.1010b25a9fe4` replaced by `qreceipt.pr-closure-harness-plan-followup.92e5b2d928f2`, bound to the squash commit whose two document blobs are byte-identical; the coverage check now excludes a subject equal to the range base and treats a deleted receipt JSON like a present one (evidence: the receipt that covers the validator subject commit; full-history validation passes)
- [x] Workspace scanner with `scan`, `drift`, `pins`, and `commands`, with tests (evidence: `scripts/quirk_workspace.py`, `tests/test_quirk_workspace.py`, and the receipt that covers this document's subject commit)
- [x] Four floating `@main` callers pinned to `92e5b2d928f25d0fedae87aaad2ef764a806065d` with `contents: read`, as draft pull requests in each repository (evidence: commits `3037791` quirk-beauty, `ceb00e1` quirk-feed, `45cebae` quirk-generator, `600de1e` quirk-town on `claude/quirk-repo-tooling-automation-walwbu`; not merged)
