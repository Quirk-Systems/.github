#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / ".quirk" / "registry.json"


def load_registry(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def index_concepts(data):
    return {c["id"]: c for c in data.get("concepts", [])}


def lint(data):
    errors, warnings = [], []
    concepts = data.get("concepts", [])
    ids = [c.get("id") for c in concepts]
    if len(ids) != len(set(ids)):
        errors.append("duplicate concept ids detected")

    by_id = index_concepts(data)
    alias_owner = {}
    for c in concepts:
        cid = c.get("id")
        if not cid or not c.get("name") or not c.get("kind") or not c.get("definition"):
            errors.append(f"{cid or '<missing-id>'}: id, name, kind and definition are required")
        parent = c.get("parent")
        if parent and parent not in by_id:
            errors.append(f"{cid}: missing parent {parent}")
        if c.get("status") == "deprecated" and not c.get("replacement"):
            errors.append(f"{cid}: deprecated concept requires replacement")
        for alias in c.get("aliases", []):
            key = alias.casefold()
            if key in alias_owner and alias_owner[key] != cid:
                errors.append(f"alias collision: {alias!r} -> {alias_owner[key]} and {cid}")
            alias_owner[key] = cid

    visiting, visited = set(), set()
    def visit(cid):
        if cid in visiting:
            errors.append(f"hierarchy cycle detected at {cid}")
            return
        if cid in visited or cid not in by_id:
            return
        visiting.add(cid)
        parent = by_id[cid].get("parent")
        if parent:
            visit(parent)
        visiting.remove(cid)
        visited.add(cid)
    for cid in by_id:
        visit(cid)

    mutate = by_id.get("move.transform.mutate")
    if mutate and mutate.get("parent") != "move.transform":
        errors.append("invariant: Mutate must remain nested under Transform")

    for c in concepts:
        if not c.get("aliases"):
            warnings.append(f"{c['id']}: no aliases recorded")

    return errors, warnings


def inspect(data, query):
    by_id = index_concepts(data)
    if query in by_id:
        return by_id[query]
    q = query.casefold()
    for c in data.get("concepts", []):
        names = [c.get("name", ""), *c.get("aliases", [])]
        if any(n.casefold() == q for n in names):
            return c
    return None


def emit_map(data):
    print("graph TD")
    for c in data.get("concepts", []):
        node = c["id"].replace(".", "_").replace("-", "_")
        label = c["name"].replace('"', "'")
        print(f'  {node}["{label}"]')
        if c.get("parent"):
            parent = c["parent"].replace(".", "_").replace("-", "_")
            print(f"  {parent} --> {node}")


def main():
    parser = argparse.ArgumentParser(prog="quirk concept")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    sub = parser.add_subparsers(dest="command", required=True)
    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("query")
    sub.add_parser("lint")
    sub.add_parser("map")
    args = parser.parse_args()

    data = load_registry(Path(args.registry))
    if args.command == "lint":
        errors, warnings = lint(data)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        print(f"Concepts: {len(data.get('concepts', []))}; errors: {len(errors)}; warnings: {len(warnings)}")
        raise SystemExit(1 if errors else 0)
    if args.command == "inspect":
        concept = inspect(data, args.query)
        if not concept:
            print(f"Unknown concept: {args.query}", file=sys.stderr)
            raise SystemExit(2)
        print(json.dumps(concept, indent=2, ensure_ascii=False))
    if args.command == "map":
        emit_map(data)

if __name__ == "__main__":
    main()
