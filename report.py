#!/usr/bin/env python3
"""Render benchmark results as a markdown report.

Supports two dimensions: conditions (A, B, ...) and prefixes.

Usage:
  python3 report.py [results_dir] [--out report.md] [--title TITLE] \\
      --cond on="autoMemoryEnabled: true (default)" \\
      --cond off="autoMemoryEnabled: false (ablated)" \\
      --prefix clean="no prior context" \\
      --prefix bloated="~12k chars of unrelated prior conversation"
"""
import argparse, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).parent
LETTERS = [chr(ord("A") + i) for i in range(26)]

def load(results_dir):
    rows = []
    for f in sorted(glob.glob(str(results_dir / "*__*.json"))):
        r = json.loads(Path(f).read_text())
        cc = r.get("cc_result", {}) or {}
        u = (cc.get("usage") or {}) if isinstance(cc, dict) else {}
        rows.append({
            "task": r["task_id"],
            "cond": r["condition"],
            "prefix": r.get("prefix", "none"),
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

def fmt_money(x): return f"${x:.4f}"
def fmt_int(n): return f"{n:,}" if n else "0"
def avg_of(rs, k):
    vs = [r[k] or 0 for r in rs]
    return sum(vs) / len(vs) if vs else 0
def pct(a, b):
    return f"{100*(b-a)/a:+.1f}%" if a else "n/a"

def cell(rows, cond, prefix):
    return [r for r in rows if r["cond"] == cond and r["prefix"] == prefix]

def summarize(rs):
    if not rs:
        return None
    n = len(rs)
    p = sum(1 for r in rs if r["pass"])
    return {
        "n": n, "pass": p, "pass_rate": p / n,
        "turns": avg_of(rs, "turns"), "out": avg_of(rs, "out_tok"),
        "cache_r": avg_of(rs, "cache_r"), "cost": avg_of(rs, "cost"),
        "time": avg_of(rs, "time"),
    }

def render(rows, title, cond_map, prefix_map):
    if not rows:
        return "# (no results)\n"
    cond_order = [c for c in cond_map]
    pref_order = [p for p in prefix_map] or sorted({r["prefix"] for r in rows})
    tasks = sorted({r["task"] for r in rows})
    n_seeds = len({r["seed"] for r in rows})
    model = sorted({r.get("model", "?") for r in rows})
    model_str = ", ".join(m for m in model if m)

    out = [f"# {title}", "",
           f"**{len(rows)} runs** · {len(tasks)} tasks × {len(cond_order)} conditions × "
           f"{len(pref_order)} prefixes × {n_seeds} seed(s) · model={model_str}", ""]

    out += ["## Conditions", ""]
    for i, c in enumerate(cond_order):
        letter = LETTERS[i]
        desc = cond_map[c]
        suffix = f" — {desc}" if desc else ""
        out.append(f"- **{letter}** = `{c}`{suffix}")
    out.append("")

    if pref_order:
        out += ["## Prefixes", ""]
        for p in pref_order:
            desc = prefix_map.get(p, "")
            suffix = f" — {desc}" if desc else ""
            out.append(f"- `{p}`{suffix}")
        out.append("")

    # Cell grid: one row per (condition, prefix)
    out += ["## Cells (condition × prefix)", "",
            "| cond | prefix | pass | avg turns | avg out tok | avg cost | avg time |",
            "|---|---|---|---|---|---|---|"]
    cells = {}
    for i, c in enumerate(cond_order):
        for p in pref_order:
            rs = cell(rows, c, p)
            s = summarize(rs)
            if not s:
                continue
            cells[(c, p)] = s
            out.append(f"| **{LETTERS[i]}** `{c}` | `{p}` | {s['pass']}/{s['n']} "
                       f"({100*s['pass_rate']:.0f}%) | {s['turns']:.1f} | {s['out']:.0f} "
                       f"| {fmt_money(s['cost'])} | {s['time']:.1f}s |")

    # Interaction: within each prefix, compare B vs A
    if len(cond_order) >= 2 and len(pref_order) >= 1:
        a_cond = cond_order[0]
        out += ["", f"## Within-prefix deltas (relative to A = `{a_cond}`)", ""]
        header_cols = ["prefix"] + [f"{LETTERS[i]} cost Δ" for i in range(1, len(cond_order))] \
            + [f"{LETTERS[i]} turns Δ" for i in range(1, len(cond_order))] \
            + [f"{LETTERS[i]} out tok Δ" for i in range(1, len(cond_order))] \
            + [f"{LETTERS[i]} pass Δ" for i in range(1, len(cond_order))]
        out.append("| " + " | ".join(header_cols) + " |")
        out.append("|" + "---|" * len(header_cols))
        for p in pref_order:
            base = cells.get((a_cond, p))
            if not base: continue
            row = [f"`{p}`"]
            # Cost deltas
            for c in cond_order[1:]:
                other = cells.get((c, p))
                row.append(pct(base["cost"], other["cost"]) if other else "—")
            for c in cond_order[1:]:
                other = cells.get((c, p))
                row.append(pct(base["turns"], other["turns"]) if other else "—")
            for c in cond_order[1:]:
                other = cells.get((c, p))
                row.append(pct(base["out"], other["out"]) if other else "—")
            for c in cond_order[1:]:
                other = cells.get((c, p))
                row.append(f"{(other['pass']-base['pass']):+d}" if other else "—")
            out.append("| " + " | ".join(row) + " |")

    # Main effect of prefix (within A): is bloat alone doing anything?
    if len(pref_order) >= 2 and len(cond_order) >= 1:
        a_cond = cond_order[0]
        base_prefix = pref_order[0]
        out += ["", f"## Prefix main effect (within A = `{a_cond}`, relative to `{base_prefix}`)", ""]
        base = cells.get((a_cond, base_prefix))
        if base:
            out += ["| prefix | cost Δ | turns Δ | out tok Δ | pass Δ |",
                    "|---|---|---|---|---|"]
            for p in pref_order:
                if p == base_prefix: continue
                other = cells.get((a_cond, p))
                if not other: continue
                out.append(f"| `{p}` | {pct(base['cost'], other['cost'])} | "
                           f"{pct(base['turns'], other['turns'])} | "
                           f"{pct(base['out'], other['out'])} | "
                           f"{other['pass']-base['pass']:+d} |")

    # Per task
    out += ["", "## Per task", "",
            "| task | cond | prefix | pass | turns | out tok | cost | time |",
            "|---|---|---|---|---|---|---|---|"]
    for t in tasks:
        for i, c in enumerate(cond_order):
            for p in pref_order:
                rs = [r for r in rows if r["task"] == t and r["cond"] == c and r["prefix"] == p]
                if not rs: continue
                n = len(rs)
                pp = sum(r["pass"] for r in rs)
                out.append(f"| {t} | **{LETTERS[i]}** `{c}` | `{p}` | {pp}/{n} | "
                           f"{avg_of(rs, 'turns'):.1f} | {avg_of(rs, 'out_tok'):.0f} | "
                           f"{fmt_money(avg_of(rs, 'cost'))} | {avg_of(rs, 'time'):.1f}s |")

    return "\n".join(out) + "\n"

def parse_kv(spec):
    if "=" in spec:
        k, v = spec.split("=", 1)
        return k.strip(), v.strip()
    return spec.strip(), ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", nargs="?", default=str(ROOT / "results"))
    ap.add_argument("--out", help="write to file instead of stdout")
    ap.add_argument("--title", default="Benchmark")
    ap.add_argument("--cond", action="append", default=[], metavar="NAME[=DESC]",
                    help="declare a condition in order; letters A, B, C assigned by order given.")
    ap.add_argument("--prefix", action="append", default=[], metavar="NAME[=DESC]",
                    help="declare a prefix in order.")
    args = ap.parse_args()

    rows = load(Path(args.results_dir))

    # Ordered dicts preserving CLI order
    cond_map = {}
    for spec in args.cond:
        k, v = parse_kv(spec)
        cond_map[k] = v
    if not cond_map:
        for c in sorted({r["cond"] for r in rows}):
            cond_map[c] = ""

    prefix_map = {}
    for spec in args.prefix:
        k, v = parse_kv(spec)
        prefix_map[k] = v
    if not prefix_map:
        for p in sorted({r["prefix"] for r in rows}):
            prefix_map[p] = ""

    md = render(rows, args.title, cond_map, prefix_map)
    if args.out:
        Path(args.out).write_text(md)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(md)

if __name__ == "__main__":
    main()
