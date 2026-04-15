#!/usr/bin/env python3
"""Render benchmark results as a markdown report.

Usage:
  python3 report.py [results_dir] [--out report.md] [--title TITLE] \
      --a on="autoMemoryEnabled: true (default)" \
      --b off="autoMemoryEnabled: false (ablated)"

  # or pipe to eyeball-md:
  python3 report.py --a ... --b ... | eyeball-md my-report
"""
import argparse, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).parent

def load(results_dir):
    rows = []
    for f in sorted(glob.glob(str(results_dir / "*__*.json"))):
        r = json.loads(Path(f).read_text())
        cc = r.get("cc_result", {})
        u = cc.get("usage", {}) if isinstance(cc, dict) else {}
        rows.append({
            "task": r["task_id"],
            "cond": r["condition"],
            "seed": r.get("seed", 0),
            "model": r.get("model", "?"),
            "pass": r["passed"],
            "turns": cc.get("num_turns") if isinstance(cc, dict) else None,
            "out_tok": u.get("output_tokens", 0),
            "cache_r": u.get("cache_read_input_tokens", 0),
            "cache_w": u.get("cache_creation_input_tokens", 0),
            "cost": cc.get("total_cost_usd", 0.0) if isinstance(cc, dict) else 0.0,
            "time": r["elapsed_s"],
        })
    return rows

def fmt_int(n): return f"{n:,}" if n else "0"
def fmt_money(x): return f"${x:.4f}"

LETTERS = [chr(ord("A") + i) for i in range(26)]

def render(rows, title, ab_map):
    """ab_map: ordered dict {"A": (cond, desc), "B": (cond, desc), ...}"""
    if not rows:
        return "# (no results)\n"
    ab_order = [k for k in ab_map if ab_map[k][0]]

    tasks = sorted({r["task"] for r in rows})
    n_seeds = len({r["seed"] for r in rows})
    model = sorted({r.get("model", "?") for r in rows})
    model_str = ", ".join(m for m in model if m)
    model_note = (f"{len(rows)} runs · {len(tasks)} tasks × {len(ab_order)} conditions × "
                  f"{n_seeds} seed(s) · model={model_str}")

    out = [f"# {title}", "", f"**{model_note}**", "", "## Conditions", ""]
    for letter in ab_order:
        cond, desc = ab_map[letter]
        suffix = f" — {desc}" if desc else ""
        out.append(f"- **{letter}** = `{cond}`{suffix}")
    out.append("")

    # aggregate
    out += ["## Aggregate", "",
            "| | pass rate | avg turns | avg out tok | avg cache read | avg cost | avg time |",
            "|---|---|---|---|---|---|---|"]
    agg = {}
    for letter in ab_order:
        cond = ab_map[letter][0]
        rs = [r for r in rows if r["cond"] == cond]
        if not rs:
            continue
        n = len(rs)
        passed = sum(1 for r in rs if r["pass"])
        avg = lambda k: sum(r[k] or 0 for r in rs) / n
        agg[letter] = {"pass": passed, "n": n, "turns": avg("turns"),
                       "out": avg("out_tok"), "cache": avg("cache_r"),
                       "cost": avg("cost"), "time": avg("time")}
        out.append(f"| **{letter}** | {passed}/{n} ({100*passed/n:.0f}%) | "
                   f"{agg[letter]['turns']:.1f} | {agg[letter]['out']:.0f} | "
                   f"{fmt_int(int(agg[letter]['cache']))} | {fmt_money(agg[letter]['cost'])} | "
                   f"{agg[letter]['time']:.1f}s |")

    # deltas vs A (baseline) for every other condition
    if "A" in agg and len(ab_order) >= 2:
        out += ["", "## Deltas vs A", ""]
        def pct(letter, k):
            base = agg["A"][k]
            d = agg[letter][k] - base
            return f"{100*d/base:+.1f}%" if base else "n/a"
        header = "| | pass | cost Δ | turns Δ | out tok Δ | time Δ |"
        sep = "|---|---|---|---|---|---|"
        out += [header, sep]
        for letter in ab_order:
            if letter == "A":
                out.append(f"| **A** | {agg['A']['pass']}/{agg['A']['n']} | — | — | — | — |")
            else:
                out.append(f"| **{letter}** | {agg[letter]['pass']}/{agg[letter]['n']} | "
                           f"{pct(letter, 'cost')} | {pct(letter, 'turns')} | "
                           f"{pct(letter, 'out')} | {pct(letter, 'time')} |")

    # per-task paired
    out += ["", "## Per task", "",
            "| task | | pass | turns | out tok | cache read | cost | time |",
            "|---|---|---|---|---|---|---|---|"]
    for t in tasks:
        for letter in ab_order:
            cond = ab_map[letter][0]
            rs = [r for r in rows if r["task"] == t and r["cond"] == cond]
            if not rs: continue
            n = len(rs)
            p = sum(r["pass"] for r in rs)
            avg = lambda k: sum(r[k] or 0 for r in rs) / n
            out.append(f"| {t} | **{letter}** | {p}/{n} | {avg('turns'):.1f} | "
                       f"{avg('out_tok'):.0f} | {fmt_int(int(avg('cache_r')))} | "
                       f"{fmt_money(avg('cost'))} | {avg('time'):.1f}s |")

    return "\n".join(out) + "\n"

def parse_ab(spec):
    """Parse 'cond=description' or just 'cond' into (cond, description)."""
    if spec is None:
        return (None, None)
    if "=" in spec:
        k, v = spec.split("=", 1)
        return (k.strip(), v.strip())
    return (spec.strip(), "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", nargs="?", default=str(ROOT / "results"))
    ap.add_argument("--out", help="write to file instead of stdout")
    ap.add_argument("--title", default="Benchmark")
    ap.add_argument("--cond", action="append", default=[], metavar="COND[=DESC]",
                    help="register a condition; repeatable. Letters A, B, C, ... are "
                         "assigned in the order given. Example: --cond on=default --cond off=ablated")
    args = ap.parse_args()

    rows = load(Path(args.results_dir))
    ab_map = {}
    if args.cond:
        for i, spec in enumerate(args.cond):
            ab_map[LETTERS[i]] = parse_ab(spec)
    else:
        # fall back: auto-assign every condition seen in results, in sorted order
        for i, c in enumerate(sorted({r["cond"] for r in rows})):
            ab_map[LETTERS[i]] = (c, "")

    md = render(rows, args.title, ab_map)
    if args.out:
        Path(args.out).write_text(md)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(md)

if __name__ == "__main__":
    main()
