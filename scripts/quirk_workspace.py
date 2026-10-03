#!/usr/bin/env python3
"""Inventory a multi-repository Quirk workspace and report topology drift.

A workspace is a directory whose children are Git checkouts of Quirk
repositories (the layout a Claude Code session or a local `~/src/quirk`
clone-all produces). This script reads those checkouts and records observed
facts only: whether a repository has commits, what toolchain files it carries,
whether it declares a `.quirk/manifest.json`, and which validation command its
own files name. It never infers purpose from a repository's name.

`drift` compares the observed set with `.quirk/repositories.json`. A checkout
missing from the inventory is `OBSERVED_UNCLASSIFIED`; an inventory entry with
no checkout is `NOT_IN_WORKSPACE`; an entry whose lifecycle contradicts what is
on disk (for example `active` with no commits) is `STATE_MISMATCH`. The output
is a decision aid with authority effect `none`: it changes no registry.

`pins` lists every caller of a `Quirk-Systems/.github` reusable workflow and
flags refs that are not a full commit SHA (`FLOATING`) or, given `--expect`,
not the reviewed commit the organization is moving callers to (`OFF_TARGET`).

`commands` prints each repository's own validation command. With `--run` it
executes them, one repository at a time, and reports exit codes; it runs only
commands the repository itself declares, and nothing for repositories without
one. A declared command that cannot start (127, 126) or times out (124) fails
the run; only a repository with no declared command is skipped. Standard library only; deterministic output.
"""

import argparse
import contextlib
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".quirk" / "repositories.json"

EMPTY = "EMPTY"
DOCS_ONLY = "DOCS_ONLY"
CODE = "CODE"
UNREADABLE = "UNREADABLE"

OBSERVED_UNCLASSIFIED = "OBSERVED_UNCLASSIFIED"
NOT_IN_WORKSPACE = "NOT_IN_WORKSPACE"
STATE_MISMATCH = "STATE_MISMATCH"

# Files whose presence makes a checkout buildable, in the order the validation
# command is chosen. Each maps to the command the repository's own convention
# implies; a package.json only counts when it names the script.
TOOLCHAIN_FILES = ("package.json", "pyproject.toml", "go.mod", "Cargo.toml")
AGENT_FILES = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md")
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".sh", ".sql", ".go", ".rs"}
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".venv", "__pycache__"}


FLOATING = "FLOATING"
PINNED = "PINNED"
OFF_TARGET = "OFF_TARGET"
# `uses:` may be a plain, single-quoted, or double-quoted YAML scalar, and GitHub
# resolves the owner and repository case-insensitively.
CALLER = re.compile(
    r"""^\s*(?:-\s*)?uses\s*:\s*(["']?)(?i:Quirk-Systems/\.github/\.github/workflows/)([^@\s"']+)@([^\s#"']+)\1(?:\s|$)"""
)
# A key whose value is a literal or folded block scalar (`run: |`, `script: >-`).
BLOCK_SCALAR = re.compile(r"^(\s*(?:-\s+)?)([^\s:#][^:#]*?)\s*:\s*[|>][-+0-9]*\s*(?:#.*)?$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


class WorkspaceError(Exception):
    pass


def git(path, *args):
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def repository_name(path):
    """Return `owner/name` from the origin URL, or the directory name."""
    code, url = git(path, "remote", "get-url", "origin")
    if code == 0 and url:
        trimmed = url.rstrip("/").removesuffix(".git").replace(":", "/")
        parts = [part for part in trimmed.split("/") if part]
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
    return path.name


def package_scripts(path):
    manifest = path / "package.json"
    if not manifest.is_file():
        return {}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts") if isinstance(data, dict) else None
    return scripts if isinstance(scripts, dict) else {}


def source_files(path):
    """Count tracked source files outside dependency and build directories.

    Only files Git tracks count, so a local virtual environment, build output,
    or other ignored directory never turns a docs-only repository into code.
    """
    result = subprocess.run(
        ["git", "-C", str(path), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None  # an unreadable index is not the same as no tracked files
    count = 0
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode("utf-8", "replace"))
        if relative.suffix in SOURCE_SUFFIXES and not SKIP_DIRS.intersection(relative.parts[:-1]):
            count += 1
    return count


def validation_command(path):
    """The validation command the repository's own files declare, or None."""
    if (path / "scripts" / "validate.sh").is_file():
        return "scripts/validate.sh"
    scripts = package_scripts(path)
    if scripts:
        runner = "bun" if (path / "bun.lock").is_file() or (path / "bun.lockb").is_file() else "npm"
        for name in ("validate", "check", "test"):
            if name in scripts:
                return f"{runner} run {name}"
    return None


def count_commits(path):
    """Commits reachable from HEAD: 0 for an unborn HEAD, None when Git cannot read the checkout."""
    if git(path, "rev-parse", "--git-dir")[0]:
        return None
    if git(path, "rev-parse", "--verify", "--quiet", "HEAD")[0]:
        # A readable repository whose HEAD names no commit yet is genuinely empty.
        return 0
    code, count = git(path, "rev-list", "--count", "HEAD")
    return int(count) if code == 0 and count.isdigit() else None


def observe(path):
    counted = count_commits(path)
    commits = counted or 0
    head = git(path, "rev-parse", "HEAD")[1] if commits else None
    entries = sorted(entry.name for entry in path.iterdir() if entry.name != ".git")
    toolchain = [name for name in TOOLCHAIN_FILES if (path / name).is_file()]
    workflows_dir = path / ".github" / "workflows"
    workflows = sorted(p.name for p in workflows_dir.glob("*.y*ml")) if workflows_dir.is_dir() else []
    sources = source_files(path) if commits else 0
    if counted is None or sources is None:
        state = UNREADABLE
    elif commits == 0:
        state = EMPTY
    elif sources:
        state = CODE
    else:
        state = DOCS_ONLY
    return {
        "repository": repository_name(path),
        "directory": path.name,
        "state": state,
        "commits": commits,
        "head": head,
        "top_level_entries": len(entries),
        "source_files": sources,
        "toolchain": toolchain,
        "manifest": (path / ".quirk" / "manifest.json").is_file(),
        "agent_files": [name for name in AGENT_FILES if (path / name).is_file()],
        "workflows": workflows,
        "validation_command": validation_command(path) if commits else None,
    }


def scan(workspace):
    workspace = Path(workspace)
    if not workspace.is_dir():
        raise WorkspaceError(f"{workspace}: not a directory")
    found = [child for child in workspace.iterdir() if child.is_dir() and (child / ".git").exists()]
    return sorted((observe(child) for child in found), key=lambda item: item["repository"].lower())


def load_inventory(path=REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {entry["repository"]: entry for entry in data["repositories"]}


def drift(observed, inventory):
    """Return findings sorted by kind then repository, comparing names case-insensitively."""
    # An unreadable checkout supports no finding: its identity may be only the
    # directory name, and its state is unknown. It still counts as present.
    present = {item["repository"].lower() for item in observed}
    by_name = {item["repository"].lower(): item for item in observed if item["state"] != UNREADABLE}
    listed = {name.lower(): entry for name, entry in inventory.items()}
    findings = []
    for key, item in by_name.items():
        if key not in listed:
            findings.append({
                "kind": OBSERVED_UNCLASSIFIED,
                "repository": item["repository"],
                "detail": f"observed {item['state']} with {item['commits']} commit{'' if item['commits'] == 1 else 's'}; not in .quirk/repositories.json",
            })
            continue
        entry = listed[key]
        if entry["lifecycle"] == "active" and item["state"] == EMPTY:
            findings.append({
                "kind": STATE_MISMATCH,
                "repository": entry["repository"],
                "detail": "inventory lifecycle is active but the checkout has no commits",
            })
        if entry["lifecycle"] == "reserved" and item["toolchain"]:
            findings.append({
                "kind": STATE_MISMATCH,
                "repository": entry["repository"],
                "detail": f"inventory lifecycle is reserved but the checkout carries {', '.join(item['toolchain'])}",
            })
    for key, entry in listed.items():
        if key not in present:
            findings.append({
                "kind": NOT_IN_WORKSPACE,
                "repository": entry["repository"],
                "detail": "listed in .quirk/repositories.json; no checkout in this workspace (absence here is not absence on GitHub)",
            })
    return sorted(findings, key=lambda f: (f["kind"], f["repository"].lower()))


def mapping_lines(lines):
    """Yield (number, line) for lines outside YAML block scalars.

    Text inside `run: |` and similar is a script, not workflow keys, so a
    heredoc that prints `uses: ...` must not be audited as a caller. A block
    scalar that is itself the value of `uses` is still a caller: its first
    content line is yielded as `uses: <value>`.
    """
    block_indent = None
    uses_prefix = None
    for number, line in enumerate(lines, start=1):
        indent = len(line) - len(line.lstrip())
        if block_indent is not None:
            if not line.strip() or indent > block_indent:
                if uses_prefix is not None and line.strip():
                    yield number, f"{uses_prefix}uses: {line.strip()}"
                    uses_prefix = None
                continue
            block_indent = None
            uses_prefix = None
        match = BLOCK_SCALAR.match(line)
        if match:
            block_indent = len(match.group(1))
            if match.group(2).strip().strip("\"'") == "uses":
                uses_prefix = match.group(1)
        yield number, line


def caller_pins(workspace, observed, expect=None):
    """Every call into a Quirk-Systems/.github reusable workflow, with its ref status."""
    rows = []
    for item in observed:
        workflows_dir = Path(workspace) / item["directory"] / ".github" / "workflows"
        for name in item.get("workflows", []):
            lines = (workflows_dir / name).read_text(encoding="utf-8", errors="replace").splitlines()
            for number, line in mapping_lines(lines):
                match = CALLER.match(line)
                if not match:
                    continue
                _, workflow, ref = match.groups()
                if not FULL_SHA.match(ref):
                    status = FLOATING
                elif expect and ref != expect:
                    status = OFF_TARGET
                else:
                    status = PINNED
                rows.append({
                    "repository": item["repository"],
                    "file": f".github/workflows/{name}:{number}",
                    "workflow": workflow,
                    "ref": ref,
                    "status": status,
                })
    return rows


def render_pins(rows):
    if not rows:
        return "No callers of Quirk-Systems/.github reusable workflows found.\n"
    lines = ["| Status | Repository | Caller | Reusable workflow | Ref |", "| --- | --- | --- | --- | --- |"]
    lines += [
        f"| {row['status']} | `{row['repository']}` | `{row['file']}` | `{row['workflow']}` | `{row['ref']}` |"
        for row in sorted(rows, key=lambda r: (r["status"], r["repository"].lower(), r["file"]))
    ]
    return "\n".join(lines) + "\n"


def render_scan(observed):
    lines = [
        "| Repository | State | Commits | Sources | Toolchain | Manifest | Agent files | Workflows | Validation |",
        "| --- | --- | ---: | ---: | --- | --- | --- | ---: | --- |",
    ]
    for item in observed:
        lines.append(
            f"| `{item['repository']}` | {item['state']} | {item['commits']} | {'-' if item['source_files'] is None else item['source_files']} | "
            f"{', '.join(item['toolchain']) or '-'} | {'yes' if item['manifest'] else 'no'} | "
            f"{', '.join(item['agent_files']) or '-'} | {len(item['workflows'])} | "
            f"{'`' + item['validation_command'] + '`' if item['validation_command'] else '-'} |"
        )
    counts = {state: sum(1 for item in observed if item["state"] == state) for state in (CODE, DOCS_ONLY, EMPTY, UNREADABLE)}
    lines.append("")
    lines.append(f"Observed {len(observed)} checkouts: " + ", ".join(f"{counts[k]} {k}" for k in counts) + ".")
    return "\n".join(lines) + "\n"


def render_drift(findings):
    if not findings:
        return "No drift: every checkout is inventoried and every inventory entry is checked out.\n"
    lines = ["| Finding | Repository | Detail |", "| --- | --- | --- |"]
    lines += [f"| {f['kind']} | `{f['repository']}` | {f['detail']} |" for f in findings]
    totals = {}
    for f in findings:
        totals[f["kind"]] = totals.get(f["kind"], 0) + 1
    lines.append("")
    lines.append("Totals: " + ", ".join(f"{totals[k]} {k}" for k in sorted(totals)) + ".")
    return "\n".join(lines) + "\n"


def stop_group(process):
    """Kill every process in the check's session and reap the leader."""
    # The group may already be gone if every process exited at the deadline.
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGKILL)
    process.wait()


def run_commands(workspace, observed, timeout):
    results = []
    for item in observed:
        command = item["validation_command"]
        if not command:
            results.append((item["repository"], None, "no declared validation command"))
            continue
        # A declared check that never completes is a failure, not a skip; the
        # codes follow the shell's conventions so callers can tell them apart.
        try:
            # Its own session, so a timeout can stop every process the check started.
            process = subprocess.Popen(
                command.split(),
                cwd=Path(workspace) / item["directory"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError as error:
            results.append((item["repository"], 127, f"not run: {error.filename} not installed"))
            continue
        except OSError as error:
            results.append((item["repository"], 126, f"not run: {error.strerror or error}"))
            continue
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_group(process)
            results.append((item["repository"], 124, f"timed out after {timeout}s"))
            continue
        except BaseException:
            # Ctrl-C or any other abort: the detached group would outlive the runner.
            stop_group(process)
            raise
        # The script may have exited while processes it backgrounded live on.
        stop_group(process)
        results.append((item["repository"], returncode, command))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", default=str(ROOT.parent), help="directory of sibling checkouts (default: parent of this repository)")
    parser.add_argument("--registry", default=str(REGISTRY), help="truthful topology inventory to compare against")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    # Accept --json after the subcommand too; SUPPRESS keeps a global --json from being reset.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="emit JSON instead of Markdown")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan", parents=[common], help="record observed facts for every checkout")
    drift_parser = sub.add_parser("drift", parents=[common], help="compare checkouts with the inventory")
    drift_parser.add_argument("--fail-on-drift", action="store_true", help="exit 1 when any finding is reported")
    pins_parser = sub.add_parser("pins", parents=[common], help="audit refs used to call Quirk-Systems/.github reusable workflows")
    pins_parser.add_argument("--expect", help="40-hex .github commit every caller should pin; others are OFF_TARGET")
    pins_parser.add_argument("--fail-on-floating", action="store_true", help="exit 1 when any caller uses a non-SHA ref")
    commands_parser = sub.add_parser("commands", parents=[common], help="list or run each repository's declared validation command")
    commands_parser.add_argument("--run", action="store_true", help="execute the commands and report exit codes")
    commands_parser.add_argument("--timeout", type=int, default=900, help="per-repository timeout in seconds")
    args = parser.parse_args(argv)

    try:
        observed = scan(args.workspace)
    except WorkspaceError as error:
        print(f"quirk_workspace: {error}", file=sys.stderr)
        return 2

    if args.command == "scan":
        print(json.dumps(observed, indent=2) if args.json else render_scan(observed), end="" if not args.json else "\n")
        return 0

    if args.command == "drift":
        findings = drift(observed, load_inventory(args.registry))
        print(json.dumps(findings, indent=2) if args.json else render_drift(findings), end="" if not args.json else "\n")
        return 1 if findings and args.fail_on_drift else 0

    if args.command == "pins":
        if args.expect and not FULL_SHA.match(args.expect):
            print("quirk_workspace: --expect must be a full 40-character lowercase SHA", file=sys.stderr)
            return 2
        rows = caller_pins(args.workspace, observed, args.expect)
        print(json.dumps(rows, indent=2) if args.json else render_pins(rows), end="" if not args.json else "\n")
        return 1 if args.fail_on_floating and any(row["status"] == FLOATING for row in rows) else 0

    if not args.run:
        declared = [item for item in observed if item["validation_command"]]
        if args.json:
            print(json.dumps([{"repository": i["repository"], "command": i["validation_command"]} for i in declared], indent=2))
        else:
            for item in declared:
                print(f"{item['directory']}: {item['validation_command']}")
        return 0
    results = run_commands(args.workspace, observed, args.timeout)
    failed = any(code not in (None, 0) for _, code, _ in results)
    if args.json:
        print(json.dumps([{"repository": r, "exit_code": c, "note": n} for r, c, n in results], indent=2))
    else:
        for repository, code, note in results:
            status = "skipped" if code is None else ("pass" if code == 0 else f"fail ({code})")
            print(f"{repository}: {status} — {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
