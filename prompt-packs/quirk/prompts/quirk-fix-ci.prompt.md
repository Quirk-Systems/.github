---
name: quirk-fix-ci
description: Diagnose and repair failing repository checks
agent: agent
---

Diagnose the failing check from evidence.

Process:

1. Read the complete failure output.
2. Identify the earliest meaningful error, not merely the final cascade.
   Inspect run head, attempt, runner assignment, executed steps and annotations.
   For zero-step jobs, distinguish confirmed billing/policy restrictions from
   unknown startup failures before changing application code. During an account
   hold, use `quirk-ci-continuity.prompt.md`; stop blind retries and preserve the
   hosted gate as blocked while continuing local work with exact-subject receipts.
3. Reproduce it locally when possible.
4. Determine whether the cause is code, tests, configuration, environment, dependency drift, or workflow logic.
5. Implement the narrowest durable repair.
6. Re-run the failed check and relevant neighboring checks.

Do not:

- weaken assertions to manufacture a pass
- disable checks without explicit justification
- conceal type or lint failures
- perform unrelated cleanup

Report root cause, repair, verification evidence, and anything still dependent on CI-only infrastructure.
