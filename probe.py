#!/usr/bin/env python3
"""Pre-flight probe: runs a trivial prompt under each declared condition and
reports the cached system-prompt size under each. Use this to verify that
your conditions actually differ in the way you expect (e.g. that an ablation
is real).

Usage:
  python3 probe.py \\
      --condition on=experiments/automemory/settings_on.json \\
      --condition off=experiments/automemory/settings_off.json
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

def run(name, settings_path, model):
    cmd = [
        "claude", "-p", "Reply with exactly the word 'ok' and nothing else.",
        "--model", model,
        "--setting-sources", "",
        "--settings", str(settings_path),
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--max-budget-usd", "0.10",
        "--no-session-persistence",
    ]
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run(cmd, cwd=td, capture_output=True, text=True, timeout=120)
    out = json.loads(proc.stdout)
    u = out["usage"]
    return {
        "name": name,
        "cache_read": u["cache_read_input_tokens"],
        "cache_write": u["cache_creation_input_tokens"],
        "input": u["input_tokens"],
        "output": u["output_tokens"],
        "cost": out["total_cost_usd"],
        "reply": out["result"][:80],
    }

def parse_condition(spec):
    if "=" not in spec:
        raise SystemExit(f"--condition must be NAME=PATH, got: {spec!r}")
    name, path = spec.split("=", 1)
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"--condition {name}: settings file not found: {p}")
    return name.strip(), p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", action="append", default=[], required=True,
                    metavar="NAME=PATH")
    ap.add_argument("--model", default="sonnet")
    args = ap.parse_args()

    conds = [parse_condition(c) for c in args.condition]
    results = {}
    for name, path in conds:
        print(f"probing {name}...", flush=True)
        results[name] = run(name, path, args.model)

    print()
    print(f"{'condition':<16} {'cache_read':>12} {'cache_write':>12} {'cost':>10}  reply")
    for name, _ in conds:
        r = results[name]
        print(f"{name:<16} {r['cache_read']:>12,} {r['cache_write']:>12,} "
              f"${r['cost']:>8.4f}  {r['reply']!r}")

    if len(conds) >= 2:
        print()
        base_name, _ = conds[0]
        base = results[base_name]
        base_total = base["cache_read"] + base["cache_write"]
        for name, _ in conds[1:]:
            r = results[name]
            total = r["cache_read"] + r["cache_write"]
            delta = total - base_total
            print(f"  system-prompt Δ ({name} − {base_name}): {delta:+,} tokens")

if __name__ == "__main__":
    main()
