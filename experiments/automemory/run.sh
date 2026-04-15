#!/usr/bin/env bash
# Wrapper for the autoMemoryEnabled A/B experiment.
# Conditions: on / off.
# Prefixes:   clean (empty) / bloated (~12k chars of unrelated prior conversation).
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

python3 "$REPO/run.py" \
    --tasks "$HERE/tasks" \
    --condition "on=$HERE/settings_on.json" \
    --condition "off=$HERE/settings_off.json" \
    --prefix "clean=$HERE/prefixes/clean.txt" \
    --prefix "bloated=$HERE/prefixes/bloated.txt" \
    --results-dir "$HERE/results" \
    --workdirs-dir "$HERE/workdirs" \
    --seeds "${SEEDS:-1}" \
    --jobs "${JOBS:-3}" \
    --budget-per-run "${BUDGET_PER_RUN:-0.80}" \
    --max-total-usd "${MAX_TOTAL_USD:-15.00}" \
    "$@"
