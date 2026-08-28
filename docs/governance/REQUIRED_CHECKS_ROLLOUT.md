# Required-check rollout

Repository files can define checks. They cannot truthfully claim to have changed
owner-only rulesets. Activate enforcement only after the exact check contexts
have run on representative pull requests.

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
2. Open or update a representative pull request and observe the emitted context.
   Expected local names are `Governance Contracts / validate` for `.github` and
   `Reusable Evidence Binding / validate` for a caller, but the observed GitHub
   context is authoritative.
3. Record repository, pull-request URL, workflow run URL, observed check context,
   pinned policy SHA, actor, and UTC timestamp in the rollout change.
4. Require the observed evidence context together with the repository's existing
   CI context. Never replace functional CI with artifact binding.
5. Confirm a clean pull request passes and a deliberately uncovered follow-up
   commit fails.
6. Change the ruleset from **Evaluate** to **Active** only after those results are
   reviewed.

If the emitted name differs, update the documented expectation and ruleset to
the observed name before activation. A green content check is not proof that
branch protection is configured.

## Rollback

If the check is unavailable or incorrectly blocks safe work, return the ruleset
to Evaluate mode. Do not float the reusable workflow ref. Repair and review the
policy at a new commit, update callers to that full SHA with evidence, observe
the new context, and reactivate deliberately.
