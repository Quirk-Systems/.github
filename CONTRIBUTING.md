# Contributing to Quirk Systems

Thanks for your interest in contributing! These guidelines apply to every repository under [@quirk-systems](https://github.com/quirk-systems). Individual repos may add a `CONTRIBUTING.md` of their own that supplements (but does not override) this one.

## Code of Conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to uphold it.

## Reporting issues

- **Bugs:** open a [bug report](https://github.com/quirk-systems/.github/issues/new?template=bug_report.yml). Include reproduction steps, expected vs. actual behavior, and environment details.
- **Features:** open a [feature request](https://github.com/quirk-systems/.github/issues/new?template=feature_request.yml).
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

| Repo                                                                  | Command                                               |
| --------------------------------------------------------------------- | ----------------------------------------------------- |
| [project-scaffold](https://github.com/quirk-systems/project-scaffold) | `bun run validate` (lint + type-check + test + build) |

Run it before opening a PR. CI runs the same checks; passing locally first saves a round trip.

## Pull requests

Use the PR template — at minimum:

- **Summary** of the change and the motivation.
- **Test plan** — how you verified it (commands, screenshots, links).
- **Linked issue** if one exists.

Keep PRs focused. If a change grows, split it.

## License

By contributing you agree your contribution is licensed under the project's license (Apache 2.0 unless the repo specifies otherwise).
