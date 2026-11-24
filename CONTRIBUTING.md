# Contributing to Quirk Systems

Thanks for your interest in contributing! These guidelines apply to every repository under [@Quirk-Systems](https://github.com/Quirk-Systems). Individual repos may add a `CONTRIBUTING.md` of their own that supplements (but does not override) this one. Agents start from [`AGENTS.md`](AGENTS.md).

## Code of Conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to uphold it.

## Reporting issues

- **Bugs:** open a [bug report](https://github.com/Quirk-Systems/.github/issues/new?template=bug_report.yml). Include reproduction steps, expected vs. actual behavior, and environment details.
- **Features:** open a [feature request](https://github.com/Quirk-Systems/.github/issues/new?template=feature_request.yml).
- **Bounded work, decisions, agent tasks:** use the [brief](https://github.com/Quirk-Systems/.github/issues/new?template=brief.yml), [decision](https://github.com/Quirk-Systems/.github/issues/new?template=decision.yml), and [agent task](https://github.com/Quirk-Systems/.github/issues/new?template=agent-task.yml) forms; the matching Markdown templates are in [`templates/`](templates/README.md).
- **Security vulnerabilities:** see [SECURITY.md](SECURITY.md). Do **not** file a public issue.

## Development workflow

### Branch naming

Use one of these prefixes:

- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `chore/<short-description>` — refactors, deps, tooling, docs

### Commits

Repos use [Conventional Commits](https://www.conventionalcommits.org/) enforced by [commitlint](https://commitlint.js.org/). Format:

```
<type>(<scope>): <short summary>
```

Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `perf`, `build`. Squash-merge PR titles must also follow this format — the org's reusable PR-title workflow enforces it.

### Local hooks

Repos that use [Lefthook](https://lefthook.dev/) install pre-commit and commit-msg hooks automatically when you install dependencies. They run lint, format checks, type-check, and commit-message validation. Don't bypass with `--no-verify` — fix the underlying issue.

### Validation

Each repo exposes a single command that runs the full local validation pipeline:

| Repo                                                                  | Command                                                                     |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| [.github](https://github.com/Quirk-Systems/.github)                   | `scripts/validate.sh` (unit tests + validators + ruff + actionlint + zizmor) |
| [project-scaffold](https://github.com/Quirk-Systems/project-scaffold) | `bun run validate` (lint + type-check + test + build)                       |

Run it before requesting review. A draft may open earlier and list what still needs testing.

### Working through a hosted runner outage

During [incident #62](https://github.com/Quirk-Systems/.github/issues/62), an assigned
change can move through these steps. Follow any narrower repository, role, or
PR-specific direction, including an explicit instruction to keep a draft or hold a merge.

| Action | When to proceed |
| --- | --- |
| Commit and push | The assignment covers the repository and the change. Create or use a dedicated work branch, commit in coherent pieces, and push normally. One assignment covers subsequent in-scope pushes. |
| Open or update a draft | Share work as soon as a reviewer could help. List unfinished work and checks still to run. |
| Mark ready for review | The diff is ready for a reviewer. Give the base and head, local commands and results, and any gaps. A hosted job that never started can be recorded as such and review can begin. |
| Merge | An owner can authorize one reviewed PR or a batch by listing each repository, PR, base, head, and who may execute the merge. The named operator may then use GitHub's ordinary merge path without another round of approval. |

For a merge during the incident, inspect the local evidence, blocking findings,
required reviews and checks, and any effects triggered by merging. An optional
hosted job that never acquired a runner can be recorded as unexecuted. An
unsatisfied required check, a failing relevant test, an unresolved blocker, or an
effect outside the grant keeps that PR on hold. If a check's requirement or
execution is unknown, establish it before relying on the outage allowance.

Immediately before merging, re-read the base, head and owner decision. If either
SHA moved, review the delta and renew the entry for that PR. Supply the expected
head to the ordinary merge operation with bypass disabled and use a merge commit for receipt-bearing
work. Record the resulting merge SHA. The author cannot supply their own
independent review. Required CI contexts keep their own provenance.

Return to the normal hosted validation procedure when runner recovery is
verified under #62. The owner can withdraw a grant earlier.

### Shipping a change to `.github` (evidence binding)

This repository's pull-request check fails unless every changed path is covered by a fresh, verified evidence receipt. Use the two-commit protocol:

1. Commit the subject (Conventional Commit message). Note the base SHA and the subject SHA.
2. Run `scripts/validate.sh` on that exact tree.
3. Generate the receipt against the subject SHA:

   ```sh
   python scripts/create_evidence_receipt.py --repository Quirk-Systems/.github --root . \
     --base <base40> --commit <subject40> \
     --receipt-id qreceipt.<slug>.<subject12> --claim-id qclaim.<slug>.<subject12> \
     --claim "<what the bytes establish and what remains unproven>" \
     --evidence-path <every changed path> ... \
     --verification-command "scripts/validate.sh" ... \
     --verified-at <RFC3339 UTC Z> --output .quirk/evidence/<slug>-<subject12>.json
   ```

4. Commit the receipt alone (`docs(evidence): bind <slug> to <subject12>`).
5. Simulate the gate before pushing:

   ```sh
   python scripts/validate_evidence_receipts.py --repository Quirk-Systems/.github --root . \
     --receipts .quirk/evidence --range-base <base40> --range-head <head40> --require-covered-diff
   ```

Touching a receipted path again needs a newer receipt. Details: [`docs/governance/EVIDENCE_BINDING.md`](docs/governance/EVIDENCE_BINDING.md) and the `quirk-evidence-receipt` skill.

## Pull requests

Use the PR template. It asks for the exact subject (full base and head SHAs), the scope and authority classification, semantic impact, the evidence receipt locator, commands with observed results, and the checks not run. Fill it literally; a green check is not evidence for untested behavior, and no receipt or decision grants authority.

Keep PRs focused. If a change grows, split it into waves that each leave `main` green.

## License

By contributing you agree your contribution is licensed under the project's license (Apache 2.0 unless the repo specifies otherwise).
