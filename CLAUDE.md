# CLAUDE.md
# Shared instructions live in AGENTS.md
@AGENTS.md

## Claude-Specific

- Skills under `.claude/skills/` are thin shims; the canonical bodies live in
  `.github/skills/<name>/SKILL.md` so Copilot and Claude read the same text.
  Load `quirk-evidence-receipt` before your first commit here.
- `.claude/settings.json` pre-approves the validation commands and blocks
  force-push and `--no-verify` through a `PreToolUse` guard. Do not edit it to
  widen permissions; open a PR that explains why.
- Local Python may be 3.11 while CI runs 3.12. Avoid 3.12-only syntax and run
  `uv run --python 3.12 -m unittest discover -s tests` before the final push.
- When a PR is opened, use the template's fields literally: full SHAs, receipt
  locators, commands with observed results, and checks not run.
