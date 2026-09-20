# Quirk GitHub Prompt System

## Purpose

This is the human-readable source of truth for the Quirk GitHub Prompt Pack: eleven reusable Copilot workflows that turn repository work into bounded actions with evidence.

## Architecture

| Layer | Best format | Responsibility |
| --- | --- | --- |
| Organization doctrine | Organization instructions | Standards shared across Quirk Systems |
| Repository doctrine | `.github/copilot-instructions.md` or `AGENTS.md` | Architecture, commands, constraints, and conventions |
| Repeatable task | `.github/prompts/*.prompt.md` | Manually invoked workflows |
| Persistent specialist | `.github/agents/*.agent.md` | Focused role, tools, and operating method |
| Reusable capability | `.github/skills/*/SKILL.md` | On-demand instructions, scripts, examples, and resources |

## Eleven Moves

1. **Orient** — understand the repository before acting.
2. **Build** — implement the smallest coherent feature with tests.
3. **Review** — prioritize real defects and issue an explicit verdict.
4. **Poke Holes** — attack assumptions before implementation hardens them.
5. **Fix CI** — trace the earliest meaningful failure and prove the repair.
6. **Dependencies** — inspect direct upgrades, transitive churn, and migration risk.
7. **Architecture** — compare viable options and record the decision.
8. **Core Contract** — protect canonical, runtime, and projection boundaries.
9. **Security Pass** — trace inputs, identity, authority, secrets, and side effects.
10. **Ship** — produce a clean, verified, reviewer-ready change.
11. **Compound** — extract the reusable capability proven by completed work.

## Prompt Spine

Every serious Quirk prompt should establish:

1. **Context** — what repository state and instructions govern the task?
2. **Outcome** — what observable behavior must become true?
3. **Constraints** — what must remain true while accomplishing it?
4. **Evidence** — what code, tests, logs, schemas, or documentation support each claim?
5. **Action** — what is the smallest coherent intervention?
6. **Verification** — what proves the outcome actually works?
7. **Risk** — what could still fail, and under what conditions?
8. **Residue** — what remains unknown, deliberately excluded, or dependent on human authority?

## Quality Gate

- A plausible answer is not evidence.
- A green check is not proof of complete behavior.
- A large diff is not proof of progress.
- A recommendation without tradeoffs is incomplete.
- An agent must distinguish verified facts, reasonable inference, and unresolved uncertainty.
- No workflow may claim success without reporting the verification performed and the checks not run.

## Installation

Copy the eleven files from `prompts/` into `.github/prompts/` in any target repository. Keep repo-specific facts out of the shared prompt bodies; place them in repository instructions so the prompts remain portable.
