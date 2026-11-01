---
name: quirk-ci-continuity
description: Continue bounded delivery during a confirmed hosted CI outage
agent: agent
---

Build the requested change with available tools. Read repository instructions and
the shared `docs/governance/CI_CONTINUITY.md` procedure. Preserve current required
checks, evidence gates and owner authority.

1. Record repository, current base/head, working-tree status and scope. Inspect
   the exact failed run, attempt, jobs, steps and annotations. Classify billing,
   policy, permissions, dependency/network and assertion failures separately.
   Zero steps alone does not identify the cause. Do not edit unrelated workflows.
2. During a confirmed account hold, stop manual retry loops. Use trusted local
   commands and installed tools; no paid service/model/runner fallback. Missing
   tools and online/human evaluations are NOT_RUN. Do not weaken assertions.
3. Make focused changes and test adversarial cases. Capture actual local execution
   with `scripts/ci_continuity.py capture` when available. Bind commands, exit
   codes, tool versions, SHA and safe log digests. A command exit of zero is not
   proof that every test executed; inspect skips and coverage.
4. Commit subject, test exact subject, create the existing evidence receipt,
   commit receipt separately. Open/update a draft PR; show LOCAL results and
   HOSTED HOLD separately. No fabricated status, skip-to-green, bypass or merge.
5. Provide a recovery handoff: owner eligibility, real standard-runner smoke
   step, refetched current PR head, four individually verified PR #62 gates,
   all other actual required checks and remaining engineering gaps. A date is
   not recovery evidence. Reuse issue #62 and its existing watch.

Deliver the code/prose and receipts, exact validation scope, NOT_RUN checks,
recovery commands and owner-only blockers. Preserve originals and human-review
requirements for creative work. Capability and preference never imply authority.
