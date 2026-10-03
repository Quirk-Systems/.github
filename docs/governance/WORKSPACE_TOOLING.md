# Workspace tooling and production automation

Status: **candidate**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

How to work across many Quirk repositories at once without guessing what
each one is, and which automation exists, which is proposed, and which stays a
human act. The tool reads checkouts; it changes no registry, opens no pull
request, and runs no command a repository did not declare itself.

## The workspace

A workspace is one directory whose children are Git checkouts of Quirk
repositories, `Quirk-Systems/.github` among them:

```text
<workspace>/
  .github/            this repository (canon, validators, this tool)
  .github-private/
  project-scaffold/
  quirk-os/
  quirk-feed/
  ...
```

A Claude Code cloud session with several repositories attached produces this
layout under its working directory. Locally, clone the repositories you need
beside `.github`. Nothing else is required: `scripts/quirk_workspace.py`
defaults `--workspace` to the parent of this checkout and uses only the Python
standard library and `git`.

## Commands

```sh
# Observed facts for every checkout: commits, source files, toolchain, manifest, agent files, workflows
python scripts/quirk_workspace.py scan            # Markdown table; add --json for machine output
# Checkouts missing from .quirk/repositories.json, entries with no checkout, and lifecycle contradictions
python scripts/quirk_workspace.py drift [--fail-on-drift]
# Every caller of a .github reusable workflow, with FLOATING / OFF_TARGET refs flagged
python scripts/quirk_workspace.py pins --expect <40-hex .github main commit> [--fail-on-floating]
# Each repository's own declared validation command; --run executes them one by one and
# exits 1 if any declared command fails, cannot start (126/127), or times out (124)
python scripts/quirk_workspace.py commands [--run --timeout 900]
```

### What the states mean

| Field | Values | Rule |
| --- | --- | --- |
| `state` | `EMPTY` | the checkout has no commits |
| | `DOCS_ONLY` | commits, but no Git-tracked source file (`.py .ts .tsx .js .mjs .cjs .sh .sql .go .rs`) outside dependency and build directories; untracked virtual environments and build output never count |
| | `CODE` | at least one such tracked source file |
| | `UNREADABLE` | Git cannot read the checkout (corrupt, wrong owner, broken `.git` file); reported instead of guessing `EMPTY`, and never a basis for drift findings |
| `validation_command` | `scripts/validate.sh`; `<runner> run validate\|check\|test`; none | the first of these entry points the repository's own files define (a `scripts/validate.sh` file, or that script name in `package.json`); none otherwise. `<runner>` is the `packageManager` that `package.json` declares (`npm`, `pnpm`, `yarn` or `bun`; any other means no command), else the one a lockfile implies, else `npm`. A test directory alone is not a declaration |
| drift `kind` | `OBSERVED_UNCLASSIFIED` | a checkout the inventory does not list |
| | `NOT_IN_WORKSPACE` | an inventory entry with no checkout here (not proof it is absent on GitHub) |
| | `STATE_MISMATCH` | `active` with no commits, or `reserved` carrying a toolchain file |
| pin `status` | `FLOATING` | the ref is not a full 40-character SHA, contrary to `AGENTS.md` |
| | `OFF_TARGET` | a full SHA other than the `--expect` commit |
| | `PINNED` | a full SHA, and the expected one when `--expect` is given |

None of these states classifies a repository. `OBSERVED_UNCLASSIFIED` is the
label `AGENTS.md` requires instead of inferring purpose from a name; a class,
lifecycle, and owner arrive only through a reviewed inventory change.

## Automation map

| Loop | Where | Trigger | Writes | Human gate | Status |
| --- | --- | --- | --- | --- | --- |
| Governance contracts and receipt gate | `governance-contracts.yml`, `reusable-evidence-binding.yml` | pull request, push to `main` | none | owner merge through rulesets | running |
| Semantic governance | `quirk-semantic-governance.yml` callers | pull request, push | none | owner merge | running; caller pins vary, see `pins` |
| Agent-task intake check | `agent-task-dispatch.yml` | `agent-task` label | one issue comment | owner records `authorize` | running |
| Supply chain | CodeQL, Scorecard, dependency review, zizmor, pin test | pull request, schedule | security events only | owner triage | running |
| Stale incubation labels | `reusable-stale-incubations.yml` | schedule in callers | labels only | owner decides retire or renew | available; no caller observed in this workspace |
| Workspace scan, drift, pins | `scripts/quirk_workspace.py` | a person or a session runs it | none | the reader decides | **this change** |
| Scheduled drift report | proposed `portfolio-drift.yml` | weekly schedule | one issue | owner reads and files inventory changes | **proposed, not built**: needs read access to private repositories, which means a token or GitHub App the owner provisions; see Decisions |
| Caller pin bumps | proposed, after the drift report | a reviewed `.github` `main` commit | one pull request per caller repository | owner merge in each repository | **proposed, not built**: needs `contents: write` and `pull-requests: write` in other repositories |

### What `pins` can and cannot see

`pins` reads workflow files line by line with the standard library; it is not
a YAML parser. It finds a `uses` key (plain, `"uses"` or `'uses'`) whose value
is a plain, quoted, anchored (`&name`) or tagged (`!!str`) scalar, a block
scalar (`uses: >-`), or an entry in a single-line flow mapping
(`{uses: ...}`), and it ignores text inside script blocks such as `run: |`.
It does not resolve aliases (`*name`), merge keys, or flow mappings that span
several lines. Treat a clean `pins` result as "no floating caller in the forms
above", not as proof that none exists.

A checkout's identity is `owner/name` only when its `origin` is a GitHub URL
(`https://github.com/…`, `git@github.com:…`, `ssh://git@github.com/…`); any
other remote, or none, leaves only the directory name. Such a checkout, like
an `UNREADABLE` one, is never a basis for a drift finding and counts as
present only for an inventory entry whose repository name equals its
directory. An `UNREADABLE` checkout reports its commit and source counts as
unknown (`null`, shown `-`), and still reports any validation command its
working tree declares.

`drift --json` returns `{"findings": [...], "unreadable": [...]}`; a non-empty
`unreadable` list means those checkouts were not compared.

## Deliberately not automated

- **Classification.** The tool reports `OBSERVED_UNCLASSIFIED`; it never writes
  `.quirk/repositories.json`. The inventory schema pins the snapshot and the
  repository set, so admitting any new entry is a schema change the owner
  approves first (`AGENTS.md`, Ask first).
- **Repository creation or bootstrap.** An empty repository stays empty until it
  passes the creation gate in `docs/REPOSITORY_STRATEGY.md` §5. Scaffolding an
  empty repository because it has a name is the failure that gate exists to stop.
- **Running other repositories' code in CI here.** `commands --run` is for a
  person or a session on a host they control. It executes only the command a
  repository declares and reports exit codes; it is not a substitute for that
  repository's own required checks.
- **Merge, canon, release, deploy.** Unchanged: owner-only.

## Adding the scheduled loops

Each proposed row above ships only with a brief that names its trigger, write
permissions, kill switch, evidence, and human gate, per
`docs/governance/AUTONOMOUS_OPERATIONS.md` ("Adding a new automated loop").
