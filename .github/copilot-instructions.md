# Quirk Systems Copilot defaults

The doctrine, stack, commands, conventions, permissions, and context pointers
for this repository live in [`AGENTS.md`](../AGENTS.md). Read it first; it is
the source, and this file is a projection of it for the one surface that does
not read `AGENTS.md` on its own. Nothing here overrides it, and when the two
disagree, `AGENTS.md` is correct and this file is stale — say so rather than
following it.

## What Copilot reads that other agents do not

- GitHub Copilot loads this file automatically for chat and code review in this
  repository and across the organization. Claude Code loads `CLAUDE.md`, which
  imports `AGENTS.md` the same way.
- Org-level Copilot agent profiles are in [`agents/`](../agents/); the canonical
  skill bodies they share with Claude are in
  [`.github/skills/`](./skills/). A `.claude/skills/` entry is a shim that
  points at the canonical body, never a second copy of it.

## The four rules worth repeating here

These are restated, not invented, because getting them wrong is expensive and
review is where it shows.

1. **Evidence before claims.** Label each claim VERIFIED, INFERRED, or UNKNOWN,
   and name the checks you did not run. A green check is not evidence for
   untested behavior; cite the command, the revision, and the observed output.
2. **Authority is a separate act.** No capability, path, label, locator, or
   passing check authorizes merge, canon, admission, release, deployment, or
   publication. Do not write that a ruleset or org setting changed — describe
   what the files define and name the owner-only step still required.
3. **Two-commit receipts.** A substantive change is the subject commit, then
   `scripts/validate.sh`, then a receipt generated against that exact SHA and
   committed alone. Touching a path after its receipt invalidates the coverage;
   generate a newer one.
4. **Standard library only.** `scripts/` and `tests/` import nothing outside
   Python 3.12's standard library, and no workflow adds a dependency step.

## Safety

- Never commit secrets, credentials, private transcripts, or personal data.
- Route security-sensitive findings through [`SECURITY.md`](../SECURITY.md)
  rather than a public issue.
- Keep changes bounded: the smallest coherent patch that fully addresses the
  task, and no widening of scope that was not asked for.
