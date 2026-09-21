# Intention: Evidence-first planning

Kind: intention  
Status: active  
Owner: @bryansayler  
Repository: `Quirk-Systems/.github`  
Observed head: `62218674c00d6a9d4c81db13000d25c5f37afc6d`  
Reviewed: 2026-09-20  
Review by: 2026-10-18  
Derived from: `.quirk/evidence/dependency-review-trigger-9925b20c1393.json`, `docs/governance/EVIDENCE_BINDING.md`, `docs/governance/TRUTHFUL_TOPOLOGY_CUT_SPEC.md`  
Authority effect: **none**

## Strength

The organization already binds claims to exact bytes and refuses to merge
without it. VERIFIED at the observed head: `governance-contracts.yml` runs
the exact-range receipt gate on every pull request; 29 verified receipts
cover the history since the truthful topology cut; three pull requests in
one day (#23, #30, #35) merged through that gate with every changed path
receipted; the topology validator turned narrative portfolio memory into
`.quirk/repositories.json` and `.quirk/manual-prs.json`. What this proves is
narrow and real: when this organization writes a claim down next to the
commit it is about, the claim stays checkable.

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

- `docs/goals/2026-09-20-living-documents-validated.md`: every document under the four contract directories, plus each brief and plan that opts in, carries a validated living-document header, and the validator runs in `scripts/validate.sh`.
- Goal to write: the twice-weekly portfolio review in `docs/governance/AUTONOMOUS_OPERATIONS.md` reads the roadmap and to-do documents and bumps their review dates, so freshness is produced by the existing cadence rather than by a separate ritual.
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
every review date. The owner decision it waits on: none; it is projection
and validation only.
