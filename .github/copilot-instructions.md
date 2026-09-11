# Quirk Systems Copilot defaults

## Operating contract

- Read the repository instructions, `CONTRIBUTING.md`, and `SECURITY.md` before making consequential changes.
- Keep changes bounded. Prefer the smallest coherent patch that fully addresses the task.
- Treat `.github/` as shared workflow and governance surface, not as a catch-all runtime or product repository.
- Use repository-relative paths such as `.github/workflows/reusable-validate.yml` and `.quirk/registry.json` in plans, docs, and reviews.
- Report what you verified, what you did not verify, and any remaining uncertainty.
- Do not treat a green check, label, path, or tool capability as authority to merge, deploy, publish, or redefine canon.

## Verification defaults

- Run the repository's documented validation commands for the paths you change.
- When changing governance contracts, include the exact commands and observed outcomes in the pull request.
- Update directly affected documentation, schemas, tests, or reusable workflow inputs when behavior changes.

## Safety defaults

- Do not commit secrets, credentials, private transcripts, or sensitive payloads.
- Escalate security-sensitive findings through `SECURITY.md` instead of public issues.
- Preserve human review and ownership boundaries for canonical, release, deployment, and production-affecting work.
