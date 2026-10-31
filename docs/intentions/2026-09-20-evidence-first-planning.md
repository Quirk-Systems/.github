# Intention: Evidence-first planning

Kind: intention  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `7c52c0407ea2fa6d3fa99cf13d86492a74733259`
Reviewed: 2026-10-31
Review by: 2026-11-03
Derived from: `.quirk/evidence/dependency-review-trigger-9925b20c1393.json`, `docs/governance/EVIDENCE_BINDING.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

## Strength

**VERIFIED at the observed head:** main
`d320f775a1be9ca8f6becfc19c84165bed176d1d` retains exact-range receipt
validation and the living-document contract. The observed PR #60 head adds a
substantive portfolio re-read at `bc4d582573306d076c3611f8463dce42d8be90ab`
and a separate receipt, with exact source heads, incomplete work, and a
November 3 checkpoint. That is evidence of a completed review, not an owner
approval or a durable cadence. The [rollout review](../todos/2026-09-20-living-document-rollout.md)
and [roadmap review](../roadmaps/2026-09-20-org-control-plane.md) separate
landed work from overlapping drafts and pending human decisions.

**VERIFIED limitation:** the workflow defines checks on pull requests, but
successful execution is not assured. The PR #60 head's Governance Contracts,
Dependency Review, and CodeQL runs are recorded as failed, so their historical
successes below are not a claim about current hosted health. The October 31
branch response reported main unprotected and the repository ruleset list was
empty; activation and merge-method settings remain separate owner work.

### Historical strength — October 3 (preserved)

The following observations, counts, present-tense statements, and reference to
"the observed head" belong to the original review at
`7c1061ba8867fdce4d903adc7c9589016e3ab002`. They are preserved as history,
not promoted to October 31 evidence.

The organization already binds claims to exact bytes, and the binding is
checked on every pull request — though nothing yet makes it *block*, which is
the correction below. VERIFIED at the observed head: `governance-contracts.yml`
runs the exact-range receipt gate on every pull request; 48 verified receipts
cover the history since the truthful topology cut; ten pull requests passed
that gate between 2026-09-20 and 2026-10-03 (#23, #28, #30, #34, #35, #36,
#37, #38, #41, then #39) with every changed path receipted; the topology
validator turned narrative portfolio memory into `.quirk/repositories.json`
and `.quirk/manual-prs.json`. What this proves is narrow and real: when this
organization writes a claim down next to the commit it is about, the claim
stays checkable.

One merge is deliberately **not** in that list, and it is the sharpest fact
here. Attempt 2 of PR #6's `Governance Contracts` run
(`35531136510`) started at 2026-09-20T19:16:49Z; its `validate` job completed
with failure at 19:17:04Z and #6 merged at 19:17:08Z — four seconds later, over
a red gate. An earlier version of this section counted it among the ten as having
"merged through that gate", and opened by saying the organization "refuses to
merge without" binding. Both were false, and false in the flattering direction.
The gate reports; it does not refuse, because no ruleset requires it. That is
the entire case for the owner-only activation still pending in
`docs/governance/OWNER_ACTIVATION_INPUTS.md`: until a ruleset requires the
check, a red gate stops nothing.

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

- **Done, preserved:** `docs/goals/2026-09-20-living-documents-validated.md`. PR #42 corrected the measure and recorded the actual unit-test enforcement path. This review leaves that file, its status, and its historical evidence byte-identical. Its October 31 date is exempt from staleness because status is done.
- **Pending owner disposition and implementation:** integrate living-document review into the existing twice-weekly portfolio agenda. Proposed scope: run strict validation, inspect open documents due by the next checkpoint, re-read against exact evidence, and record continued work or retirement. `AUTONOMOUS_OPERATIONS.md` and `REPOSITORY_STRATEGY.md` §8.10 still do not name that work. Proof of completion would be an accepted checklist change plus a dated review demonstrating its use; neither is claimed here.
- **Pending owner decision:** select where freshness is enforced. The current real-date test can fail an unrelated PR's next run; changing it, adding a scheduled report, or adding merge-time enforcement requires an explicit disposition with its tradeoffs. The roadmap's owner-decision section holds this question. The October 5 owner follow-up on #42 repeated it without selecting an option.
- **Blocked on evidence:** identify a second repository carrying living documents before proposing `reusable-living-docs.yml`. Such adoption was not established by this review. The absence of a reusable workflow in this repository does not prove that no external adopter exists.

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

**Reviewed October 31; still active.** One goal remains done, and cadence,
enforcement disposition, and consumer rollout remain incomplete. The shorter
November 3 review date aligns with PR #60's existing portfolio checkpoint and
keeps these unresolved decisions visible before another lapse; it is not a
newly configured automation. At that checkpoint, record the owner disposition
or the explicit continuing dependency, and re-read the source heads before
renewing. Re-observe earlier if dependencies, the evidence gate, templates, or
validator entrypoint change. Retire only if the goals are met or the owner
chooses a different planning home.

**Recovery and scope.** The rollout review records the all-ref history search,
current source files, and candidate heads. The latest intention edit recovered
was `ceb13f171620028db3c9e015ac22aad2a98be1c0` in merged PR #42; its
header still recorded October 3. The newer October 30 portfolio review in
PR #60 is preserved at `7c52c0407ea2fa6d3fa99cf13d86492a74733259`, not
mistaken for a review of this intention or for a merge. No newer completed
review of these three documents was found in the inspected history and PRs;
inaccessible work remains outside that claim.

**Freshness and authority.** The pre-correction PR #60 tree fails strict
validation on simulated November 1 with exactly these three active records
stale. The done goal is exempt. The correction keeps all three active and
changes no validator, test, workflow, settings, owner, schema, or authority.
Post-correction local commands and exact subject are recorded by the receipt.
Hosted execution and human approval remain separate evidence. If no further
review occurs, these three records become stale on November 4, not November 3.

### Historical goals — October 3 (preserved)

- **Done** 2026-10-03: `docs/goals/2026-09-20-living-documents-validated.md`. Every document under the four contract directories carries a validated header and the validator runs in `scripts/validate.sh`. The brief-and-plan opt-in path exists and is tested, but no brief or plan has used it yet; that is a task in the rollout todo, not part of the goal's measure.
- Goal to write, now the urgent one: the twice-weekly portfolio review in `docs/governance/AUTONOMOUS_OPERATIONS.md` reads the roadmap and to-do documents and bumps their review dates, so freshness is produced by the existing cadence rather than by a separate ritual. On 2026-10-03 nothing produced it: the rollout todo was one day from its review date and the roadmap two — two and three days from any stale result, since the validator fires on `review_by < today` — after thirteen days unread, and only an unrelated drift check caught them.
- Goal to write: decide where freshness is enforced. This intention says a validator "reports it stale the day it lapses"; what shipped fails the gate instead, and because the `validate` check runs the whole test suite, one stale planning document fails the `validate` check on any pull request whose checks run or re-run while the document is stale, including pull requests that changed nothing related. The intention's own wording is the weaker claim and the implementation is the stronger one — the gap was never written down until now, and closing it is a decision about blast radius, not about whether staleness matters.
- Goal to write: consumer repositories can run the living-document validator against their own `docs/` through a reusable workflow, once two repositories carry such documents.

### Historical review — October 3 (preserved)

Retire this intention when its goals are done or when the owner decides
planning should live outside the repository. Re-observe it whenever the
evidence gate, the templates, or the validator entrypoint changes, and at
every review date.

Still active on 2026-10-03: of four goals one is done and three are still
unwritten, so the intention stands. The owner decision it now waits on is the
one added above — where freshness is enforced — which did not exist when this
document was first written because the gap between "reports" and "fails the
gate" had not yet cost anything.
