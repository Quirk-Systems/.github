# Intention: Evidence-first planning

Kind: intention  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c1061ba8867fdce4d903adc7c9589016e3ab002`  
Reviewed: 2026-10-03  
Review by: 2026-10-31  
Derived from: `.quirk/evidence/dependency-review-trigger-9925b20c1393.json`, `docs/governance/EVIDENCE_BINDING.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

## Strength

The organization already binds claims to exact bytes and refuses to merge
without it. VERIFIED at the observed head: `governance-contracts.yml` runs
the exact-range receipt gate on every pull request; 48 verified receipts cover
the history since the truthful topology cut; ten pull requests merged through
that gate between 2026-09-20 and 2026-10-03 (#6, #23, #28, #30, #34, #35, #36,
#37, #38, #41, then #39) with every changed path receipted; the topology
validator turned narrative portfolio memory into `.quirk/repositories.json`
and `.quirk/manual-prs.json`. What this proves is narrow and real: when this
organization writes a claim down next to the commit it is about, the claim
stays checkable.

Re-read on 2026-10-03, the discipline held under pressure twice in ways worth
recording, because both were caught by binding rather than by memory. A
reusable workflow's caller failed with `startup_failure` and no log at all;
what identified the cause was two hosted runs of the same caller across two
pins, differing in one declared scope (#38). And a portfolio retention rule
was about to be applied to `quirk-core` on the strength of a plan that
described a vendored pin nobody had created; reading the three repositories
found the pin absent and the rule itself to be the defect (#39). In both cases
the thing that was written down next to a commit was checkable, and the thing
written down in a plan was not.

The same discipline does not yet reach planning. Plans, briefs, intentions,
and to-do lists say "current" without naming the head they observed, "soon"
without a date, and "done" without evidence. The plan ledger for the control
plane recorded an owner-only setting as enabled before it was (corrected in
`9e1b4f7dfc296a94ccf2ab2b408f45bc44a55769`); that defect class is what this
intention exists to remove.

## Intention

Every document that says what the organization intends, wants, or will do is
a living document: it names the exact head it observed, the owner, the date it
was last read against that head, and the date by which it must be read again;
it derives from evidence or from a document upstream of it; and a validator
reports it stale the day it lapses. Strengths become intentions, intentions
become goals with measures, goals become tasks with owners and proofs, and
each step is a file under `docs/` that `scripts/validate_living_docs.py`
checks. Planning inherits the receipt discipline instead of escaping it.

## Goals

- **Done** 2026-10-03: `docs/goals/2026-09-20-living-documents-validated.md`. Every document under the four contract directories carries a validated header and the validator runs in `scripts/validate.sh`. The brief-and-plan opt-in path exists and is tested, but no brief or plan has used it yet; that is a task in the rollout todo, not part of the goal's measure.
- Goal to write, now the urgent one: the twice-weekly portfolio review in `docs/governance/AUTONOMOUS_OPERATIONS.md` reads the roadmap and to-do documents and bumps their review dates, so freshness is produced by the existing cadence rather than by a separate ritual. On 2026-10-03 nothing produced it: two documents were one and three days from lapsing after thirteen days unread, and only an unrelated drift check caught them.
- Goal to write: decide where freshness is enforced. This intention says a validator "reports it stale the day it lapses"; what shipped fails the gate instead, and because the `validate` check runs the whole test suite, one lapsed planning document fails every open pull request. The intention's own wording is the weaker claim and the implementation is the stronger one — the gap was never written down until now, and closing it is a decision about blast radius, not about whether staleness matters.
- Goal to write: consumer repositories can run the living-document validator against their own `docs/` through a reusable workflow, once two repositories carry such documents.

## Not this

- Not a new named Quirk concept. The practice the owner calls Quirk
  Intelligence has no entry in `.quirk/registry.json`; this document does not
  coin one. Proposing a concept is a canonical change through the brief form.
- Not a runtime, scheduler, dashboard, or task tracker product. Files, a
  schema, a validator, and the existing pull-request gate are the whole
  mechanism.
- Not a claim that a document's contents are true. The validator proves
  shape, lineage, and freshness; humans still decide what is worth doing.
- Not a replacement for briefs and plans. Those templates stay; this header
  can be added to them so they stop drifting silently.

## Review

Retire this intention when its goals are done or when the owner decides
planning should live outside the repository. Re-observe it whenever the
evidence gate, the templates, or the validator entrypoint changes, and at
every review date.

Still active on 2026-10-03: one goal of three is done and two are still
unwritten, so the intention stands. The owner decision it now waits on is the
one added above — where freshness is enforced — which did not exist when this
document was first written because the gap between "reports" and "fails the
gate" had not yet cost anything.
