# Agent task contracts

This directory holds `agent-task.v1` JSON records validated by
`scripts/validate_agent_tasks.py` against
`.quirk/schemas/agent-task.schema.json`. A record is the machine-readable
form of the `agent-task` issue form: bounded objective, allowed and forbidden
knowledge sources, allowed / approval-gated / forbidden tools, execution
limits, human owner and shutdown authority, required evidence, model
identity, rollback plan, and residue.

A record describes work. Its `authority.effect` is always `none`. A task
moves from `proposed` to `authorized` only when the human owner records that
change in a reviewed commit; the validator rejects a record that claims to be
running or complete while still listing `authorize` as a required gate.

The idempotency key is `sha256(repository + base_commit + task_id + "agent-task")`
so a retry of the same task against the same base resolves to the same key
and cannot be double-dispatched (see `docs/governance/INTEROPERABILITY.md` §7).

The example record is `templates/agent-task.json`. This directory is empty
until a real task is recorded here; the validator reports zero records and
passes.
