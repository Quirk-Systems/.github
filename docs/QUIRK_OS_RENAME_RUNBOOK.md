# Quirk OS Repository Rename Runbook

Goal: preserve the implemented kernel and its full history while moving the canonical repository name from `project-scaffold` to `quirk-os`.

## Current state

- `Quirk-Systems/project-scaffold` — active public repository containing the implemented Quirk OS kernel, history, issues, pull requests, workflows, and architecture.
- `Quirk-Systems/quirk-os` — empty private placeholder blocking the desired name.

## Required authority

This operation requires organization-level repository administration permissions. It cannot be completed through ordinary content commits.

## Preflight

Before changing either repository:

- [ ] Confirm `quirk-os` has no unique branches, commits, releases, packages, deployments, environments, secrets, variables, webhooks, rulesets, or team permissions.
- [ ] Confirm no external system is using the empty placeholder’s repository ID.
- [ ] Record current branch protections/rulesets on `project-scaffold`.
- [ ] Record repository secrets, variables, environments, webhooks, GitHub Apps, deploy keys, and Actions permissions.
- [ ] Record Vercel, Cloudflare, Supabase, PostHog, Resend, Stripe, and other deployment/integration references.
- [ ] Search the organization for literal references to `Quirk-Systems/project-scaffold` and `project-scaffold`.
- [ ] Pause merges during the cutover window.

## Cutover sequence

### 1. Clear the desired name

Rename:

```text
Quirk-Systems/quirk-os
→ Quirk-Systems/quirk-os-reserved
```

Then:

- [ ] Add a README explaining that the repository was an empty naming placeholder.
- [ ] Mark it non-canonical.
- [ ] Archive it after verification.

Do not delete it during the cutover. Archiving preserves evidence and allows rollback without destructive recovery.

### 2. Rename the implemented kernel

Rename:

```text
Quirk-Systems/project-scaffold
→ Quirk-Systems/quirk-os
```

GitHub should redirect ordinary repository URLs and Git operations, but redirects are not a substitute for updating canonical references.

### 3. Update canonical repository identity

Update at minimum:

- [ ] `.quirk/manifest.json`
- [ ] package metadata and workspace names
- [ ] README badges and clone instructions
- [ ] architecture documents
- [ ] reusable workflow caller references
- [ ] semantic-governance manifests
- [ ] CODEOWNERS references
- [ ] issue and PR templates
- [ ] deployment documentation
- [ ] repository registry in `.github`

Canonical identity after cutover:

```json
{
  "repository": "Quirk-Systems/quirk-os",
  "primary_class": "kernel",
  "domain": "quirk-operating-system",
  "authority": "Quirk-Systems/.github",
  "lifecycle": "active"
}
```

### 4. Update external systems

Verify or relink:

- [ ] local Git remotes
- [ ] GitHub App installations
- [ ] repository webhooks
- [ ] Vercel project linkage
- [ ] Cloudflare build/deploy configuration
- [ ] Supabase integration metadata
- [ ] status dashboards
- [ ] automation prompts and scheduled jobs
- [ ] documentation links outside GitHub
- [ ] package provenance and release tooling
- [ ] dependency badges and security reporting

Suggested local command:

```bash
git remote set-url origin git@github.com:Quirk-Systems/quirk-os.git
```

## Verification

- [ ] Default branch is still `main`.
- [ ] Issues and pull requests are present.
- [ ] Open PR branches and review threads remain intact.
- [ ] Required status checks still resolve.
- [ ] `bun install --frozen-lockfile` succeeds.
- [ ] `bun run validate` succeeds.
- [ ] production dependency audit succeeds.
- [ ] Playwright workflow succeeds.
- [ ] Dependabot can open and update PRs.
- [ ] semantic governance resolves `.github` authority.
- [ ] deployment previews and production deployment succeed.
- [ ] old repository URLs redirect correctly.
- [ ] organization profile points to the new canonical URL.
- [ ] code search shows no unintended live `project-scaffold` references.

## Post-cutover cleanup

- [ ] Merge the repository-strategy foundation PR.
- [ ] Update the canonical portfolio registry.
- [ ] Close the rename tracking issue with evidence links.
- [ ] Re-enable normal merges.
- [ ] Announce the canonical name and boundary: `quirk-os` is the implemented kernel.
- [ ] Review the archived placeholder after 30 days and retain unless there is a clear reason to delete it.

## Rollback

If a critical integration cannot be repaired quickly:

1. Pause merges and deployments.
2. Rename the implemented repository back to `project-scaffold`.
3. Rename `quirk-os-reserved` back to `quirk-os` only if required.
4. Restore recorded external integration settings.
5. Document the failure as an incident and do not retry until the missing dependency is understood.

## Definition of done

- `Quirk-Systems/quirk-os` contains the full implementation and history previously held by `project-scaffold`.
- the empty placeholder is archived under `quirk-os-reserved`.
- canonical manifests and the organization registry identify the new name.
- CI, security, dependency automation, and deployments are green.
- no active system depends on `project-scaffold` except GitHub redirects maintained for compatibility.
