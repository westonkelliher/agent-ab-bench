#!/usr/bin/env python3
"""Generic A/B/C/... benchmark runner for Claude Code.

An experiment = a set of conditions (each a Claude Code settings file)
tested against a set of tasks. Every task runs under every condition under
every seed. Results are stored per-run and aggregated by report.py.

Task format (one directory per task):
  <tasks_dir>/<task-id>/
    meta.json     {"id": ..., "bucket": ..., "description": ...}
    prompt.md     prompt sent verbatim to `claude -p`
    starter/      (optional) files copied into the workdir before the run
    grade.sh      runs in the workdir AFTER claude; exit 0 = pass

Usage:
  python3 run.py \\
      --tasks experiments/automemory/tasks \\
      --condition on=experiments/automemory/settings_on.json \\
      --condition off=experiments/automemory/settings_off.json \\
      --results-dir experiments/automemory/results \\
      --seeds 1 --jobs 2 --max-total-usd 5

Results go to --results-dir (defaults to ./results). Runs whose result file
already exists are skipped, so interrupted sweeps can resume.
"""
import argparse, json, os, shutil, subprocess, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).parent

_spend_lock = Lock()
_total_spend = 0.0

def load_tasks(tasks_dir: Path, only=None):
    tasks = []
    for meta_path in sorted(tasks_dir.glob("*/meta.json")):
        task_dir = meta_path.parent
        meta = json.loads(meta_path.read_text())
        if only and meta["id"] not in only:
            continue
        tasks.append({
            "id": meta["id"],
            "bucket": meta.get("bucket", "unknown"),
            "dir": task_dir,
            "prompt": (task_dir / "prompt.md").read_text(),
            "starter": task_dir / "starter" if (task_dir / "starter").exists() else None,
            "grade": task_dir / "grade.sh",
        })
    return tasks

def result_path(results_dir, task_id, condition, seed):
    return results_dir / f"{task_id}__{condition}__s{seed}.json"

def run_one(task, condition, settings_path, model, seed,
            budget_usd, max_total_usd, results_dir, workdirs_root):
    global _total_spend
    out_path = result_path(results_dir, task["id"], condition, seed)
    if out_path.exists():
        return {"skipped": True, "run_id": out_path.stem}

    with _spend_lock:
        if max_total_usd is not None and _total_spend >= max_total_usd:
            return {"aborted": True, "reason": "max_total_usd reached",
                    "run_id": out_path.stem}

    run_id = f"{task['id']}__{condition}__s{seed}__{uuid.uuid4().hex[:6]}"
    workdir = workdirs_root / run_id
    workdir.mkdir(parents=True, exist_ok=True)
    if task["starter"]:
        for item in task["starter"].iterdir():
            dst = workdir / item.name
            if item.is_dir():
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)

    cmd = [
        "claude", "-p", task["prompt"],
        "--model", model,
        "--setting-sources", "",
        "--settings", str(settings_path),
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--max-budget-usd", str(budget_usd),
        "--no-session-persistence",
        "--add-dir", str(workdir),
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True,
                              text=True, timeout=1800)
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout) or ""
        stderr = ((e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr) or "") + "\n[TIMEOUT]"
        rc = -1
    elapsed = time.time() - t0

    try:
        cc_out = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        cc_out = {"raw_stdout": stdout[-2000:], "parse_error": True}

    cost = cc_out.get("total_cost_usd", 0.0) if isinstance(cc_out, dict) else 0.0
    with _spend_lock:
        _total_spend += cost

    passed, detail = grade(task, workdir)
    record = {
        "run_id": run_id,
        "task_id": task["id"],
        "bucket": task["bucket"],
        "condition": condition,
        "settings_file": str(settings_path),
        "seed": seed,
        "model": model,
        "elapsed_s": round(elapsed, 2),
        "passed": passed,
        "grade_detail": detail,
        "exit_code": rc,
        "stderr": (stderr or "")[-2000:],
        "cc_result": cc_out,
        "workdir": str(workdir),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2))
    return record

def grade(task, workdir):
    grade_sh = task["grade"]
    if not grade_sh.exists():
        return False, "no grade.sh"
    try:
        r = subprocess.run(["bash", str(grade_sh.resolve())],
                           cwd=workdir, capture_output=True,
                           text=True, timeout=120)
        return r.returncode == 0, (r.stdout + r.stderr)[-500:]
    except Exception as e:
        return False, f"grade_error: {e}"

def parse_condition(spec):
    """Parse 'name=path/to/settings.json' into (name, Path)."""
    if "=" not in spec:
        raise SystemExit(f"--condition must be NAME=PATH, got: {spec!r}")
    name, path = spec.split("=", 1)
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"--condition {name}: settings file not found: {p}")
    return name.strip(), p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True,
                    help="directory containing task subdirs")
    ap.add_argument("--condition", action="append", default=[], required=True,
                    metavar="NAME=PATH",
                    help="condition: a label and a Claude Code settings JSON file. "
                         "Repeat for each condition, e.g. --condition on=on.json "
                         "--condition off=off.json")
    ap.add_argument("--results-dir", default=str(ROOT / "results"),
                    help="where per-run result JSONs are written")
    ap.add_argument("--workdirs-dir", default=str(ROOT / "workdirs"),
                    help="where per-run working directories live")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--budget-per-run", type=float, default=1.00)
    ap.add_argument("--max-total-usd", type=float, default=None)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--only", default=None,
                    help="comma-separated task ids (skip others)")
    args = ap.parse_args()

    if len(args.condition) < 1:
        raise SystemExit("provide at least one --condition")
    conditions = [parse_condition(c) for c in args.condition]
    names = [c[0] for c in conditions]
    if len(set(names)) != len(names):
        raise SystemExit(f"duplicate condition names: {names}")

    only = set(args.only.split(",")) if args.only else None
    tasks = load_tasks(Path(args.tasks).resolve(), only=only)
    if not tasks:
        raise SystemExit(f"no tasks found under {args.tasks}")

    results_dir = Path(args.results_dir).resolve()
    workdirs_root = Path(args.workdirs_dir).resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    workdirs_root.mkdir(parents=True, exist_ok=True)

    jobs = []
    for seed in range(args.seeds):
        for task in tasks:
            for (cname, cpath) in conditions:
                jobs.append((task, cname, cpath, seed))

    print(f"Running {len(jobs)} jobs: {len(tasks)} tasks × "
          f"{len(conditions)} conditions × {args.seeds} seeds · jobs={args.jobs}")
    print(f"Conditions: {', '.join(f'{n} → {p.name}' for n, p in conditions)}")
    print(f"Results → {results_dir}")

    records = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, t, cn, cp, args.model, s,
                          args.budget_per_run, args.max_total_usd,
                          results_dir, workdirs_root): (t["id"], cn, s)
                for (t, cn, cp, s) in jobs}
        for fut in as_completed(futs):
            rec = fut.result()
            if rec.get("skipped"):
                print(f"[skip] {rec['run_id']} (already done)")
            elif rec.get("aborted"):
                print(f"[abort] {rec['run_id']}: {rec['reason']}")
            else:
                cost = rec['cc_result'].get('total_cost_usd', 0) \
                    if isinstance(rec['cc_result'], dict) else 0
                print(f"[done] {rec['run_id']} pass={rec['passed']} "
                      f"t={rec['elapsed_s']}s cost=${cost:.4f}")
            records.append(rec)

    print(f"\nTotal spend this run: ${_total_spend:.4f}")

if __name__ == "__main__":
    main()
