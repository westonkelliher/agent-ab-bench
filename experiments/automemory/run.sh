#!/usr/bin/env bash
# Wrapper for the autoMemoryEnabled A/B experiment.
# Run from the repo root or from inside the experiment directory.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

python3 "$REPO/run.py" \
    --tasks "$HERE/tasks" \
    --condition "on=$HERE/settings_on.json" \
    --condition "off=$HERE/settings_off.json" \
    --results-dir "$HERE/results" \
    --workdirs-dir "$HERE/workdirs" \
    --seeds "${SEEDS:-1}" \
    --jobs "${JOBS:-2}" \
    --budget-per-run "${BUDGET_PER_RUN:-0.50}" \
    --max-total-usd "${MAX_TOTAL_USD:-5.00}" \
    "$@"
