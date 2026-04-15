# experiment: autoMemoryEnabled

## Hypothesis

Claude Code's default system prompt contains a ~2.9k-token block describing the **auto-memory** feature — instructions that tell Claude when to record user preferences or facts as memories. The hypothesis is that these instructions **hurt performance on most coding tasks** by causing Claude to deliberate on whether the current conversation warrants a memory instead of focusing on the task at hand.

Ablating this block (via `"autoMemoryEnabled": false` in settings.json) removes it from the system prompt entirely. If the hypothesis holds, we expect: **lower cost / fewer turns / less output** under the ablated condition, **without a loss in pass rate**.

## Conditions

- **`on`** — default Claude Code. `settings_on.json` has `autoMemoryEnabled: true`.
- **`off`** — ablation. `settings_off.json` has `autoMemoryEnabled: false`.

Ablation confirmed by `probe.py`: the cached system-prompt size grows by ~2.9k tokens under `on`.

## How to run

```bash
# from the repo root:
./experiments/automemory/run.sh
```

Or manually:

```bash
python3 run.py \
    --tasks experiments/automemory/tasks \
    --condition on=experiments/automemory/settings_on.json \
    --condition off=experiments/automemory/settings_off.json \
    --results-dir experiments/automemory/results \
    --seeds 1 --jobs 2 --max-total-usd 5
```

## Generating the report

```bash
python3 report.py experiments/automemory/results \
    --title "autoMemoryEnabled A/B" \
    --cond "on=autoMemoryEnabled: true (default)" \
    --cond "off=autoMemoryEnabled: false (ablated)"
```
