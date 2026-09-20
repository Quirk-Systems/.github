#!/usr/bin/env python3
"""Claude Code PreToolUse guard: block history rewrites and hook bypasses.

Reads the hook payload from stdin. Exit code 2 blocks the tool call and
returns the reason to the agent; exit code 0 allows it. The guard inspects
only the shell command text; it does not execute anything and it does not
grant any permission that the settings allowlist does not already grant.
"""

import json
import re
import sys

BLOCKED = [
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+[A-Za-z0-9_./-]*)",
     "force-push and refspec overwrites are not allowed on Quirk branches"),
    (r"\bgit\s+(commit|push|merge|rebase)\b.*\s(--no-verify|-n)\b",
     "hook bypass (--no-verify) is not allowed"),
    (r"\bgit\s+rebase\b", "history rewrite (rebase) is not allowed on shared branches"),
    (r"\bgit\s+commit\b.*\s--amend\b", "history rewrite (--amend) is not allowed; add a new commit"),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-zA-Z]*f)", "destructive working-tree reset is not allowed"),
    (r"\bgit\s+branch\s+-D\b", "forced branch deletion is not allowed"),
]


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    for pattern, reason in BLOCKED:
        if re.search(pattern, command):
            sys.stderr.write(f"quirk-guard: blocked: {reason}\n")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
