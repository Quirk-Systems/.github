#!/usr/bin/env bash
# Single local validation entrypoint for Quirk-Systems/.github.
# Runs the same checks CI runs plus local-only lint. Exit non-zero on any failure.
# Optional tools (ruff, actionlint, zizmor) are skipped with a notice when absent;
# a skipped check is reported, never counted as passed.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
REPO="Quirk-Systems/.github"
skipped=()

run() { echo "==> $*"; "$@"; }
optional() {
  local tool="$1"; shift
  if command -v "$tool" >/dev/null 2>&1; then run "$tool" "$@"; else skipped+=("$tool"); fi
}

run "$PY" -m unittest discover -s tests
run "$PY" scripts/validate_governed_decisions.py --repository "$REPO" --root . --decisions .quirk/decisions
run "$PY" scripts/validate_evidence_receipts.py --repository "$REPO" --root . --receipts .quirk/evidence
run "$PY" scripts/quirk_concept.py lint
run "$PY" scripts/validate-copilot-maintenance.py
run "$PY" scripts/validate_agent_assets.py
for script in scripts/validate_manifest.py scripts/validate_portfolio.py scripts/validate_templates.py \
              scripts/validate_agent_tasks.py scripts/design_tokens.py scripts/validate_living_docs.py; do
  if [[ -f "$script" ]]; then
    case "$script" in
      scripts/validate_manifest.py) run "$PY" "$script" .quirk/manifest.json ;;
      scripts/design_tokens.py) run "$PY" "$script" validate .quirk/design/tokens.json ;;
      # --strict: a living document past its review date fails the gate, so
      # freshness is enforced rather than merely printed.
      scripts/validate_living_docs.py) run "$PY" "$script" --strict ;;
      *) run "$PY" "$script" ;;
    esac
  fi
done
if [[ -f scripts/portfolio_report.py ]]; then run "$PY" scripts/portfolio_report.py --check; fi

echo "==> JSON parse of .quirk/**/*.json and .claude/settings.json"
find .quirk .claude -name '*.json' -print0 | xargs -0 -n1 "$PY" -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))'

optional ruff check .
# actionlint 1.7.x does not yet model the GitHub.com job.workflow_repository /
# job.workflow_sha contexts used by the reusable policy checkouts.
optional actionlint -ignore 'property "workflow_(repository|sha)" is not defined'
# Offline: online audits need GitHub API access; the pin policy is checked by tests.
if command -v uv >/dev/null 2>&1; then run uv tool run --quiet zizmor --offline --persona pedantic .github/workflows; else skipped+=("zizmor"); fi

if ((${#skipped[@]})); then
  echo "SKIPPED (tool not installed, not a pass): ${skipped[*]}"
fi
echo "validate.sh: all executed checks passed"
