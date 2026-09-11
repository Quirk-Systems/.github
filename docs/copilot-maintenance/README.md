# Quirk Copilot maintenance specialists

Owner: `Quirk-Systems/.github`. These profiles package the existing Quirk prompt workflows into three focused Copilot roles and one reusable skill. They are instructions; no dispatcher, recurring job, merge bot, access-control implementation, or deployment workflow is installed by this package.

| Profile | Assigned work | Tools |
| --- | --- | --- |
| `quirk-repo-repair` | Bounded source and CI repairs | Read, search, edit, execute |
| `quirk-dependency-steward` | Dependency paths, compatibility, minimal authorized updates | Read, search, edit, execute |
| `quirk-artifact-provenance` | Documentation and source/artifact relationships | Read, search, edit |

`execute` permits shell commands and is not a path sandbox. Natural-language restrictions describe expected behavior; they do not implement permission enforcement. Existing GitHub rules and host permissions remain authoritative. All three profiles also allow the documented `github/issue_read`, `github/pull_request_read`, and `github/get_file_contents` tools to inspect source context. Their availability and repository access depend on the host; unavailable source reads remain unknown. No GitHub write tool is listed.

## Availability and invocation

The root `agents/` directory in the organization's `.github` repository is GitHub's organization-level profile location. Integration into its default branch makes these profiles available through GitHub's supported custom-agent surfaces, subject to account, organization, and enterprise settings. Repository-local profiles instead belong under `.github/agents/`.

The skill is located at `.github/skills/quirk-repo-maintenance/SKILL.md` in this repository. This location does **not** imply organization-wide skill distribution. Profiles include essential guidance so they can operate without it. To install the skill into another repository, copy that folder in a separately scoped change, record its source commit, and review the target repository's instructions. No cross-repository installation is performed here.

Select an available custom profile while assigning a bounded issue, or use the official assignment API with a verified profile identifier. Provide the owning repository, actual issue/PR, current head, desired outcome, allowed scope, relevant source links, and acceptance checks. Do not launch duplicate work for an already assigned task.

The current ChatGPT GitHub connector exposes ordinary issue assignees but no `custom_agent` selector. Assigning `copilot-swe-agent[bot]` through that connector proves only ordinary assignment when read back. An issue brief can describe the specialist task, but it is not proof the named custom profile ran. Report profile selection only from actual session or resulting PR evidence. GitHub-native recurring automations are not configured by this package.

## Verification

Run from the repository root with Python 3:

```sh
python3 scripts/validate-copilot-maintenance.py
```

The validator checks the four authored frontmatters, declared tool restrictions, file locations, relative Markdown links (within the checked-out repository), and scenario/rubric integrity. It accepts this package's simple JSON-valued YAML frontmatter; it is not a general YAML parser or a Copilot runtime simulator.

`scenarios.json` contains synthetic positive and adversarial requests, not real advisories or live repository facts. Give the profiles, skill, and scenarios to an independent evaluator **without** `rubric.json`; ask for decisions and next actions with no external writes. Score the output against `rubric.json`. Dry evaluation can expose instruction weaknesses, but does not prove Copilot dispatch, tool enforcement, hosted CI, merge safety, or actual agent behavior. A later live proof should name the profile version, task/session, resultant PR/head, observed actions, checks, and independent review.

The recorded local results and their limits are in [evaluation.md](evaluation.md).

## Provenance and references

Package design inspected `CONTRIBUTING.md`, `SECURITY.md`, the prompt-pack overview, and Orient/Review/Fix CI/Dependencies/Poke Holes/Ship at source commit `0c657bcbed85cd81d2da0dcfbaf400bf004098f9`. No root `AGENTS.md` existed at that source revision. The package branch starts from governance- and portfolio-integrated main `59c05caf9b68ef006d8627d9fc679b536c0a4e56`; its evidence cycle uses a substantive commit followed by a receipt-only commit. Existing prompts remain unchanged.

- [Quirk prompt system](../../prompt-packs/quirk/Quirk-GitHub-Prompt-System.md)
- [Contribution rules](../../CONTRIBUTING.md)
- [Security policy](../../SECURITY.md)
- [GitHub organization profile placement](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/prepare-for-custom-agents)
- [GitHub MCP read-tool definitions](https://github.com/github/github-mcp-server/blob/main/README.md)
- [Profile configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Skill installation and discovery](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Copilot assignment API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api)

GitHub documentation was checked on 2026-09-11. Recheck provider-specific fields when updating the package. The existing prompt pack describes manual IDE prompts; linking a prompt here does not make it a GitHub.com slash command.
