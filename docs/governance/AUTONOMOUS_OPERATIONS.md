# Autonomous operations

Status: **candidate operating loop**  
Owner: `Quirk-Systems/.github`  
Authority effect: **none**

Quirk's operating loop is `async preparation → real-time session → async
execution → real-time review → persistent world update`. This document maps
each stage to the concrete surfaces this repository provides, states what is
automated, and states what is deliberately not.

## The loop, mapped

| Stage | Surface | Who acts | Artifact |
| --- | --- | --- | --- |
| Async preparation | `brief` issue form or `templates/BRIEF.md`; `quirk-brief` skill | Human or agent | Brief with outcome, semantic impact, evidence plan |
| Real-time session | `decision` issue form; owner review | Human owner | Disposition, `authorize` recorded in a reviewed change |
| Async execution | `agent-task` issue form → `.quirk/agent-tasks/*.json` → agent profile or skill | Agent within stated tools, paths, limits | Branch, commits, evidence receipt |
| Real-time review | Pull request with the template's exact-subject fields; `governance-contracts.yml`; reusable checks | Human reviewer; validators | Governed decision (optional), review state |
| Persistent world update | Merge; registry, manifest, portfolio, and docs updated in the same change | Owner through rulesets | Canonical files at a new `main` SHA; `docs/PORTFOLIO.md` regenerated |

## What is automated here

- **Intake check.** `agent-task-dispatch.yml` runs when an issue carries the
  `agent-task` label. It checks that every containment section of the form is
  answered and well-formed, then posts one comment with the result. It has
  `issues: write` for that comment and nothing else. It does not assign an
  agent, start a session, or authorize anything.
- **Contract validation.** `reusable-agent-task-contract.yml` validates a
  caller's `.quirk/agent-tasks/*.json` against the schema at an immutable
  policy SHA: idempotency key bound to repository, base commit, and task id;
  no tool in two lists; consequential actions always forbidden; a `proposed`
  task always awaiting `authorize`.
- **Evidence gate.** `governance-contracts.yml` (here) and
  `reusable-evidence-binding.yml` (callers) reject any pull request whose
  changed paths lack a fresh verified receipt.
- **Hygiene.** CodeQL, Scorecard, dependency review, zizmor, and the pin
  policy test run without human action. Stale incubations are labeled, never
  closed.

## What is deliberately not automated

- **Authorization.** A form, a label, a green check, or a comment never
  authorizes a task. The owner records `authorize` by editing the task record
  in a reviewed change (or by an explicit comment the agent must quote).
- **Dispatch.** Starting an agent is a human act on a host the human controls:
  assigning a Copilot custom agent, opening a Claude Code session, or creating
  a Claude Code Remote routine. This repository contains no scheduler, no
  merge bot, and no self-triggering loop. Routines and cloud agents are
  optional external schedulers, configured by the owner, that must still open
  pull requests that pass the same gates.
- **Merge, canon, release, deploy, publish.** Owner-only, through rulesets
  and environment protections that repository files cannot change.

## Kill switch

Remove the `agent-task` label or close the issue. Any host running the task
must treat the label's absence as shutdown. The `shutdown_authority` named in
the task can do this at any time; so can any repository admin.

## Twice-weekly portfolio review (from `REPOSITORY_STRATEGY.md` §8.10)

Copy into a plan or run as a session agenda:

1. Active pull requests and failing CI on `main` and open heads.
2. Security and dependency findings (code scanning, Scorecard, dependency review).
3. Decisions awaiting authority (`docs/PORTFOLIO.md` "Decisions awaiting an owner"; open `decision` issues).
4. Blocked agent tasks (`agent-task` issues with `not ready` comments; records in `blocked`).
5. Repository health regressions (pin test, workflow lint, receipt coverage).
6. The single highest-leverage next move, written as a brief.

## Adding a new automated loop

Write the brief. State the trigger, the write permissions, the kill switch,
the evidence it produces, and the human gate it feeds. Add it as a workflow
that passes `tests/test_workflow_pins.py` and zizmor, document it in
`REUSABLE_WORKFLOWS.md`, and ship it with a receipt. A loop that cannot name
its kill switch and its human gate does not ship.
