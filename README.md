# agent-ab-bench

A small, reusable harness for running A/B (or A/B/C/D…) benchmarks on [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) across a set of agentic coding tasks. Each **condition** is a Claude Code settings JSON file; every task runs under every condition (and every seed) with everything else held constant, so you can isolate the effect of a single setting, system-prompt change, tool allowlist, etc.

## What's in here

```
run.py                      # the runner — launches one claude -p per task × condition × seed
report.py                   # turns the per-run JSON results into a markdown report
probe.py                    # pre-flight sanity check — verifies conditions actually differ
experiments/                # one subdirectory per experiment
  automemory/               # the first experiment (see experiments/automemory/README.md)
    settings_on.json
    settings_off.json
    tasks/                  # the task set for this experiment
      <task-id>/
        meta.json
        prompt.md
        starter/            # optional files copied into the workdir before Claude runs
        grade.sh            # runs in the workdir after; exit 0 = pass
    run.sh                  # convenience wrapper that calls ../../run.py with the right args
    README.md
```

## Task format

Each task is a directory:

- **`meta.json`** — `{"id": "...", "bucket": "small|medium|long", "description": "..."}`
- **`prompt.md`** — the prompt sent verbatim to `claude -p`
- **`starter/`** (optional) — files copied into the working directory before Claude runs
- **`grade.sh`** — bash script; runs in the working directory after Claude exits; exit 0 means pass. Grade on file contents and program output, not on Claude's wording.

## Running an experiment

```bash
# pre-flight: verify conditions differ as expected
python3 probe.py \
    --condition on=experiments/automemory/settings_on.json \
    --condition off=experiments/automemory/settings_off.json

# full sweep
python3 run.py \
    --tasks experiments/automemory/tasks \
    --condition on=experiments/automemory/settings_on.json \
    --condition off=experiments/automemory/settings_off.json \
    --results-dir experiments/automemory/results \
    --seeds 1 --jobs 2 --max-total-usd 5

# report
python3 report.py experiments/automemory/results \
    --title "autoMemoryEnabled A/B" \
    --cond "on=autoMemoryEnabled: true (default)" \
    --cond "off=autoMemoryEnabled: false (ablated)"
```

## Design notes

- **Settings isolation.** Every `claude` invocation is run with `--setting-sources ""` so that only the condition's settings file is loaded — user/project/local settings can't bleed in and confound the comparison.
- **Resume.** Per-run results go to files named `<task>__<condition>__s<seed>.json`. Existing files are skipped on re-run, so you can interrupt a sweep and pick up where you left off.
- **Spend ceiling.** `--max-total-usd` aborts remaining jobs once the running total exceeds the cap. `--budget-per-run` bounds any single run.
- **Reuse.** `run.py`, `report.py`, `probe.py` are experiment-agnostic. To add a new experiment, create a new directory under `experiments/`, drop settings files and a `tasks/` dir in it, and write a `run.sh` wrapper.
