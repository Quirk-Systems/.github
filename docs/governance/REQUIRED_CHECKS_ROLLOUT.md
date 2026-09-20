# Required-check rollout

Repository files can define checks. They cannot truthfully claim to have changed
owner-only rulesets. Activate enforcement only after the exact check contexts
have run on representative pull requests.

## Decision requested

Authorize an organization owner to perform the owner-only rollout for the
exact-range governance check only after draft PR
[`Quirk-Systems/.github#9`](https://github.com/Quirk-Systems/.github/pull/9)
was reviewed, merged, and observed on `main`.

This repository change does not activate a ruleset and does not treat a green
workflow as proof that enforcement exists.

## Preconditions

- [ ] PR `Quirk-Systems/.github#9` is approved and merged through normal GitHub
      authority.
- [ ] Record the full merge commit SHA; do not pin callers to a branch or tag.
- [ ] `Governance Contracts / validate` succeeds on the exact `main` merge
      commit.
- [ ] The reusable workflow path and admitted policy commit are recorded.
- [ ] Existing functional CI contexts are inventoried; governance evidence must
      complement, not replace, them.

## Content rollout

1. Merge the reviewed `.github` evidence-binding workflow and validator.
2. Record that merge's full 40-character commit SHA.
3. In each caller repository, add a pull-request workflow that calls
   `Quirk-Systems/.github/.github/workflows/reusable-evidence-binding.yml` at
   that full SHA. A branch, tag, short SHA, or placeholder is not acceptable.
4. Do not add a `with:` block or pass repository, range, commands, or secrets.
   The caller supplies only the full-SHA `uses:` reference and read-only contents
   permission. The called workflow fails outside `pull_request` and derives the
   repository, base SHA, and head SHA from the immutable event context.
5. Add a verified two-commit receipt that covers the caller change.

The reusable workflow checks out the caller's explicit head with full history
and checks out its own policy source from `job.workflow_repository` at
`job.workflow_sha`. Both official actions are pinned to complete commit SHAs,
and checkout credentials are not persisted. There are no path filters, so a
later documentation-only or receipt-adjacent change cannot silently skip the
check. Coverage also checks path freshness: modifying an already-receipted path
after its subject fails until a newer qualifying receipt covers that latest
change.

## Owner-only rollout

For each target repository, an authorized owner must:

1. Create or update the branch ruleset for the default branch in **Evaluate**
   mode.
2. Open or update a representative pull request and observe the exact emitted
   check context. Expected local names are `Governance Contracts / validate` for
   `.github` and `Reusable Evidence Binding / validate` for a caller, but the
   observed GitHub context is authoritative.
3. Record repository, pull-request URL, positive and negative workflow run URLs,
   observed check context, pinned policy SHA, actor, and UTC timestamp in the
   rollout change.
4. Require the observed governance context together with the repository's existing
   CI context. Never replace functional CI with artifact binding.
5. Prove the positive path with a fully receipted exact range.
6. Prove the negative path by adding a substantive uncovered follow-up commit;
   the governance check must fail closed.
7. Restore the test branch to a valid receipted state and re-observe success.
8. Review false-positive, bypass, administrator, merge-queue, and rollback
   behavior.
9. Change the ruleset from **Evaluate** to **Active** only through an explicit
   owner decision recorded in the rollout issue.

## Required receipt

```yaml
repository:
ruleset_id:
mode_before: Evaluate
mode_after: Active | Evaluate
policy_commit:
representative_pr:
positive_run:
negative_run:
observed_check_context:
actor:
decided_at:
rollback:
```

## Authority boundary

- Content in `.github` can define a check; it cannot activate owner-only
  rulesets.
- This rollout record grants no merge, canon, release, deployment, publication,
  or runtime authority.
- If the admitted policy head changes, repeat observation against the new
  immutable policy commit.
- If the check blocks safe work incorrectly, return the ruleset to **Evaluate**;
  do not float the workflow reference.

If the emitted name differs, update the documented expectation and ruleset to
the observed name before activation. A green content check is not proof that
branch protection is configured.

## Rollback

If the check is unavailable or incorrectly blocks safe work, return the ruleset
to Evaluate mode. Do not float the reusable workflow ref. Repair and review the
policy at a new commit, update callers to that full SHA with evidence, observe
the new context, and reactivate deliberately.
