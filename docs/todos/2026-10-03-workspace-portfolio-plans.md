# Todo: Workspace portfolio plans

Kind: todo  
Status: candidate  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `d320f775a1be9ca8f6becfc19c84165bed176d1d`
Reviewed: 2026-10-30
Review by: 2026-11-03
Derived from: `docs/roadmaps/2026-09-20-org-control-plane.md`, `docs/REPOSITORY_STRATEGY.md`, `docs/governance/WORKSPACE_TOOLING.md`  
Authority effect: **none**

## Review — 2026-10-30

**VERIFIED — substantive reassessment; authority effect remains none.** This
review supersedes the action queue below, not its historical observations.
Owner and candidate status remain unchanged. Repository classifications,
lifecycles, ownership, schemas, registry entries, workflow pins, and authority
are not changed. November 3 is the next portfolio review checkpoint, not a
newly configured automation.

### Recovery, sources, and coverage

No newer completed portfolio review was recovered from accessible document
history, repository planning paths, portfolio PR search, or saved-file search.
The latest document revision was October 3 commit
`c3af72ce28add3d5fffe9f382436fc5c03460a83`, included in merged [PR #44](https://github.com/Quirk-Systems/.github/pull/44).
This search does not establish absence from inaccessible conversations or files.

The [public evidence inventory](../reviews/2026-10-30-workspace-portfolio-evidence.json)
records exact public repository heads, scanner output, and selected public PR
states. Detailed private-repository observations were assessed separately and
retained in a private review report; their source payloads, heads, per-repository
metadata, and review details are not added to this public correction. The
historical text below was already present publicly and is preserved.

**VERIFIED — public subset.** This public evidence inventory covers seven public
repositories. Six are source-bearing (`CODE`) and one (`greenfield`) is
`DOCS_ONLY` under the scanner's rules. The public governed inventory still has
17 organization and two adjacent entries. `greenfield` is outside that inventory.
No new organization-wide count, private repository state, or private-derived
aggregate is disclosed here. The historical survey remains historical.

Seven actual public checkouts were available: `.github`, `greenfield`,
`project-scaffold`, `quirk-core`, `quirk-feed`, `quirk-generator`, and `quirk-os`.
The existing scanner ran without modifications:

```sh
python3 scripts/quirk_workspace.py scan --json
python3 scripts/quirk_workspace.py drift --json
python3 scripts/quirk_workspace.py pins --expect 92e5b2d928f25d0fedae87aaad2ef764a806065d --json
python3 scripts/quirk_workspace.py commands --json
```

Six public clones are shallow, so their commit counts were not compared with
October 3. Scanner `NOT_IN_WORKSPACE` means checkout coverage only; the public
evidence file omits rows about repositories outside this public subset. This is
not an exhaustive organization inventory, and it does not establish absence or
status for any repository outside the listed checkouts.

`commands --run` was not used across the portfolio: dependency installations
and native/browser environments were not reconstructed. This correction reruns
only the governance repository's local checks. Application passes from October 3
are not renewed. Detailed nonpublic review material is retained separately and
is not part of the evidence offered by this public patch.

### Verified changes and remaining work

| Area | Current public evidence | Disposition |
| --- | --- | --- |
| Original caller repairs | [Feed #28](https://github.com/Quirk-Systems/quirk-feed/pull/28) and [Generator #5](https://github.com/Quirk-Systems/quirk-generator/pull/5) merged; both current main callers retain `92e5b2d928f25d0fedae87aaad2ef764a806065d`. | Public caller merge tasks complete; remaining original caller review details stay in the private report. |
| Policy pins | The public subset has five calls with full SHA refs across four policy commits, with no floating ref in parser-supported forms. Caller detail is below. | Selecting a common target remains a review decision. A different full SHA is not automatically invalid or vulnerable. |
| `quirk-os` | Main `03f70e1a790bac09294fe0f31a3c5f0d0fb4418e` has 13 workflows, no `scripts/validate.sh`, and no scanner-recognized local validation command. | Single declared entrypoint remains open; individual workflow commands exist, but equivalence was not assessed. |
| `quirk-core` | Main remains `b3162b0cd6dcc6c07570f240ca33c711ed860f0b`; complete tree has no `.quirk/manifest.json`. | Manifest task remains open; preserve the existing doctrine-retention decision. |
| `quirk-feed` runtime | Main `a338ea3e0158437167cd875bb4655b67c3b9dc68` declares Node `>=24.21.0 <25`, Bun `>=1.4.2 <2`; CI reads `.node-version` = `24.21.0` and `.bun-version` = `1.4.2`. | Runtime declaration gap addressed. Full-install validation is not renewed by reading configuration. |
| `greenfield` | Main `6e6d4b425fe9082d469493d64a5b8e12b15dc9da` is `DOCS_ONLY` under scanner rules and is not in the governed inventory. | `OBSERVED_UNCLASSIFIED`; no inferred purpose or owner. |
| Governance improvements | #44 and #47 merged; #47 is main `d320f775a1be9ca8f6becfc19c84165bed176d1d`. #55 and Ubuntu preflight #51 remain drafts. #58 closed without merge; the current Actions dependency group is #59. | Keep review candidates separate from landed changes. |

### Public workflow pins

Caller heads and exact file locations are in the evidence inventory. The old
October 3 pin is a comparison value only, not a newly selected policy target.
Private caller details remain outside the new public evidence file.

| Public caller | Reusable workflow | Full policy SHA |
| --- | --- | --- |
| Feed, Generator | `quirk-semantic-governance.yml` | `92e5b2d928f25d0fedae87aaad2ef764a806065d` |
| `project-scaffold` | semantic governance | `1263f5008838f743b16ee218046e26dac5c9edd8` |
| `project-scaffold` | evidence binding | `ed2f2ff7caacdb7a148ac9811dce1e7cce48a7c8` |
| `quirk-os` | evidence binding | `6136fa5fa77116abfbc103c822d9d244a0e870b3` |

### Dependencies, existing decisions, and unknowns

**VERIFIED — reuse existing candidates.** Scaffold #137 (CI modernization), #149
(testing/runtime alignment), and #152 (TruffleHog update) remain open; none is
main. Reconcile their CI overlap at their recorded heads. Feed #48 remains open.
The shared Actions dependency group #59 is open at
`3b5747734aee9eccf30c14f715150044e8fb840e`. #55's current head is
`35c3a05341de125f6466b663775105cb7307527b`. These states establish pending
review, not readiness to merge. Private candidate dependencies are retained in
the private review rather than republished here.

**VERIFIED — decisions retained.** The inventory and control-plane roadmap keep
Core separate for owning a distinct, versioned, enforceable contract; lack of a
consumer alone is not grounds to fold it. Scaffold remains a reference repository
and OS a candidate kernel. The 19 inventory owner fields remain open; this
planning document's owner does not become each repository's owner. No governed
decision JSON is committed on this main; the accessible open `label:decision`
issue query returned none. Neither observation rules out decisions elsewhere.
Public provisioning #24 and working defaults #55 remain drafts with no submitted
reviews. They do not replace merged decisions.

**UNKNOWN / not established here.** Current owner-only ruleset/merge-method
settings, complete Core consumer graph, application install/test health,
private Actions credentials, deployment, and human usefulness. The main workflow
tree contains neither `portfolio-drift.yml` nor caller-bump automation. Session
read access does not establish Actions access. The receipt protocol already
requires merge commits; settings enforcement is a separate owner check.

**Local versus hosted.** Baseline `scripts/validate.sh` ran 233 tests: 232 passed;
the sole failure was `test_repository_documents_are_fresh_today` because this
document was due October 17. The script stopped there; later stages were not
counted as passed. Exact-subject correction results are recorded in its evidence
receipt and PR. No validator, test, workflow, or unrelated document is changed.
Four other living documents still have October 31 deadlines and need substantive
review before November 1.

At the baseline main SHA, [Governance Contracts run 41004601321](https://github.com/Quirk-Systems/.github/actions/runs/41004601321)
failed with one job and zero steps. CodeQL and Scorecard also failed; Dependabot
service runs succeeded. #47's earlier public validation record identifies a
billing lock; current check annotations were unavailable through this connection.
The current startup cause and successful hosted execution cannot be inferred
from a document-freshness repair.

## Open

- [ ] Add a declared `quirk-os` validation entrypoint derived from its existing workflows (owner: @bryansayler; proof: scanner `commands` lists it and that repository's applicable checks run successfully).
- [ ] Add the existing doctrine declaration's manifest in `quirk-core` through its own review (owner: @bryansayler; proof: complete tree contains the manifest and its applicable validator passes).
- [ ] Reconcile existing Scaffold #137/#149/#152, and review Feed #48 and shared Actions #59 independently (owner: @bryansayler; proof: current exact-head checks, compatibility assessment, and recorded disposition).
- [ ] Reassess this portfolio by November 3; first review the four other living documents due October 31 (owner: @bryansayler; proof: substantive reviews, observed heads, remaining unknowns, and strict freshness validation).

## Blocked

- [ ] Select a reviewed common policy target after comparing the four public policy commits and obtaining the remaining caller evidence within its access boundary; do not automatically downgrade newer evidence callers to the historical comparison SHA (blocked on: owner policy selection and per-repository review; who can unblock: @bryansayler; proof: complete `pins --expect <selected-sha>` has no unintended drift).
- [ ] Reconcile newly observed public inventory drift (`greenfield`) and assess the remaining portfolio within its access boundaries (blocked on: owner topology and schema decisions; who can unblock: @bryansayler). The inventory schema still fixes snapshot `2026-08-21`, 19 entries, and organization count 17. No additional private findings are disclosed here.
- [ ] Decide empty-repository retention/archive and adjacent commerce selection through the existing creation/retirement gates (blocked on: owner judgement; who can unblock: @bryansayler).
- [ ] Authorize scheduled drift reports or caller-bump automation only with a brief, scoped credentials, permissions, and kill switch (blocked on: owner-controlled Actions access and write grants; who can unblock: @bryansayler).
- [ ] Verify receipt-preserving merge-method enforcement and restore hosted validation access (blocked on: owner settings/account access; who can unblock: @bryansayler). Preserve the existing merge-commit protocol and receipts; local success cannot close this item.

## Done

- [x] Recovered the original survey and checked accessible history for a successor; reviewed the seven public checkouts on October 30 (evidence: public inventory, exact heads, and scanner output; nonpublic review retained separately).
- [x] Feed #28 and Generator #5 merged and their main callers retain the reviewed October 3 pin (evidence: merge SHAs and caller heads in the public evidence inventory).
- [x] Original scanner/receipt repair #44 and Dependabot label correction #47 merged (evidence: recorded merge SHAs; no hosted success claim).
- [x] Feed runtime declarations and CI version-file wiring are present (evidence: `a338ea3e0158437167cd875bb4655b67c3b9dc68`, `.node-version`, `.bun-version`, `package.json`, and `.github/workflows/ci.yml`; application tests not rerun here).

## Historical survey — 2026-10-03 (preserved)

Original observed head: `92e5b2d928f25d0fedae87aaad2ef764a806065d`.
Original review: October 3; original deadline: October 17. The following survey,
plans, checkboxes, and unknowns are historical evidence already present publicly.
Only section headings are demoted; original observations and wording remain.
Use the October 30 queue above for current action.

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

### What the workspace showed

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

### Per-repository plans

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

### Open

- [ ] Merge the four caller-pin pull requests in `quirk-beauty`, `quirk-feed`, `quirk-generator`, and `quirk-town` (owner: @bryansayler; proof: `python scripts/quirk_workspace.py pins --fail-on-floating` exits 0)
- [ ] Choose one reviewed `.github` commit and move every caller to it, `.github-private` and `project-scaffold` included (owner: @bryansayler; proof: `pins --expect <sha>` reports no `OFF_TARGET`)
- [ ] Give `quirk-os` a single local validation entrypoint (owner: @bryansayler; proof: `commands` lists a command for `Quirk-Systems/quirk-os`)
- [ ] Add `.quirk/manifest.json` to `quirk-core` (owner: @bryansayler; proof: `scan` shows `Manifest yes` for `quirk-core`)
- [ ] Re-run this survey at the twice-weekly portfolio review and bump this document (owner: @bryansayler; proof: Reviewed date and Observed head updated)

### Blocked

- [ ] Admit the 32 `OBSERVED_UNCLASSIFIED` repositories to `.quirk/repositories.json` (blocked on: the inventory schema pins the snapshot `2026-08-21`, exactly 19 entries, and 17 organization repositories, so any admission is a schema version change, which `AGENTS.md` puts under Ask first; who can unblock: @bryansayler)
- [ ] Build the scheduled `portfolio-drift.yml` report proposed in `docs/governance/WORKSPACE_TOOLING.md` (blocked on: read access to private repositories from Actions, which means a token or GitHub App the owner provisions, plus a brief naming its kill switch; who can unblock: @bryansayler)
- [ ] Automate caller pin bumps across repositories (blocked on: a workflow with `contents: write` and `pull-requests: write` in other repositories, which is Ask first; who can unblock: @bryansayler)
- [ ] Stop receipts being stranded by squash merges: the PR #14 squash is what broke the receipt check on `main`, and squashing this pull request would strand its own four subject commits the same way. Merge with a merge commit, as PRs #39 and #41 were, and either restrict the repository to merge commits or teach the receipt protocol to re-bind after a squash (blocked on: a repository merge-method setting or a protocol decision; who can unblock: @bryansayler)
- [ ] Decide each empty repository: keep reserved, or archive (blocked on: owner judgement at the quarterly topology review; who can unblock: @bryansayler)

### Done

- [x] Repaired the receipt that the PR #14 squash merge stranded: `qreceipt.pr-closure-harness-plan-followup.1010b25a9fe4` replaced by `qreceipt.pr-closure-harness-plan-followup.92e5b2d928f2`, bound to the squash commit whose two document blobs are byte-identical; the coverage check now excludes a subject equal to the range base and treats a deleted receipt JSON like a present one (evidence: the receipt that covers the validator subject commit; full-history validation passes)
- [x] Workspace scanner with `scan`, `drift`, `pins`, and `commands`, with tests (evidence: `scripts/quirk_workspace.py`, `tests/test_quirk_workspace.py`, and the receipt that covers this document's subject commit)
- [x] Four floating `@main` callers pinned to `92e5b2d928f25d0fedae87aaad2ef764a806065d` with `contents: read`, as draft pull requests in each repository (evidence: commits `3037791` quirk-beauty, `ceb00e1` quirk-feed, `45cebae` quirk-generator, `600de1e` quirk-town on `claude/quirk-repo-tooling-automation-walwbu`; not merged)
