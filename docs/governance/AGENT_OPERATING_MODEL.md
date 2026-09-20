# Agent operating model

Status: **candidate operating baseline**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

Quirk treats agent instructions as versioned repository configuration, not chat
context. This document maps the five-layer model from the
[Quirk prompt system](../../prompt-packs/quirk/Quirk-GitHub-Prompt-System.md) to
the concrete files each agent host reads, and states what those files can and
cannot do.

## Layers and their files

| Layer | Purpose | Claude Code | GitHub Copilot | Any other host |
| --- | --- | --- | --- | --- |
| Organization doctrine | Standards shared across every Quirk repository | `AGENTS.md` (imported by `CLAUDE.md`) | Organization instructions (owner-configured) + `.github/copilot-instructions.md` (pending in PR #20) | `AGENTS.md` |
| Repository doctrine | Architecture, commands, constraints, conventions | `AGENTS.md`, `CLAUDE.md` | `.github/copilot-instructions.md` | `AGENTS.md` |
| Repeatable task | Manually invoked, portable workflows | Prompt bodies in `prompt-packs/quirk/prompts/` | `.github/prompts/*.prompt.md` (copied from the pack) | Paste the prompt |
| Persistent specialist | Focused role, tools, operating method | Skills under `.claude/skills/` | `agents/*.agent.md` (org level) | `AGENTS.md` Permissions section |
| Reusable capability | On-demand instructions, scripts, resources | `.claude/skills/<name>/SKILL.md` shim → `.github/skills/<name>/SKILL.md` | `.github/skills/<name>/SKILL.md` | Read the canonical file |

The canonical skill body lives once, under `.github/skills/`. Claude shims are
pointers validated by `scripts/validate_agent_assets.py`; a shim that copies the
body fails validation so the two hosts cannot drift.

## Instruction budget

Root instruction files are kept under 150 lines and use "Don't → Do instead"
pairs. Anything deterministic (formatting, pin checks, schema shape) is enforced
by validators and tests, never by prose. Deep guidance lives in skills and docs
that load on demand.

## What every agent-authored change must expose

From `docs/REPOSITORY_STRATEGY.md` §8.8, restated as fields an agent fills in
the pull request or the agent-task contract:

- bounded objective;
- allowed and forbidden knowledge sources;
- allowed, approval-gated, and forbidden tools;
- execution environment and limits;
- human owner and shutdown authority;
- evidence receipt (see `docs/governance/EVIDENCE_BINDING.md`);
- model/provider identity when consequential;
- reversible postcondition or rollback plan.

The `agent-task` issue form and `.quirk/schemas/agent-task.schema.json` carry
the same fields in machine-readable form.

## Boundaries

- Instruction files guide behavior. They are not enforcement. GitHub rulesets,
  environment protections, and host permissions remain the only enforcement.
- `.claude/settings.json` narrows what Claude Code may run without asking and
  blocks force-push, `--no-verify`, rebase, amend, and hard resets through
  `scripts/hooks/guard.py`. It cannot grant anything the host does not allow.
- Copilot `tools:` lists in `agents/*.agent.md` describe intended scope; the
  `execute` tool is a shell, not a path sandbox (see
  `docs/copilot-maintenance/README.md`).
- No agent approves or merges its own work, dismisses reviews, activates
  candidate capabilities, changes access controls, or deploys.

## Parity checklist when adding an asset

1. Write the canonical body under `.github/skills/<name>/SKILL.md` with the
   JSON-valued frontmatter the existing validator expects.
2. Add the `.claude/skills/<name>/SKILL.md` shim naming the canonical path.
3. Run `python scripts/validate_agent_assets.py` and
   `python3 scripts/validate-copilot-maintenance.py`.
4. Link the asset from the relevant doc and, if it changes how contributors
   ship, from `CONTRIBUTING.md`.
5. Ship with an evidence receipt.
