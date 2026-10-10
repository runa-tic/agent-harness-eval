"""Turn graded runs into a report: success rates with intervals, the paired difference between
arms, grader agreement, run-to-run consistency, cost of a run, and the list of failures.

Intervals
  Per-arm success uses a Wilson 95% interval over runs. Runs of the same task are not independent,
  so that interval is too narrow; it is reported for readability only.
  The arm difference uses a bootstrap over TASKS (resample tasks with replacement, keep all of a
  task's repeats together), which is the unit that was actually sampled.

Agreement
  Cohen's kappa between the LLM judge and the programmatic check, and between the judge and the
  human labels in hand_labels.csv once that column is filled.

Usage: python stats.py --label pilot-shim
"""
import argparse, csv, hashlib, json, math, random, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def task_bootstrap(by_task, arm_a, arm_b, field, iters=10000, seed=11):
    """Difference in mean per-task success (arm_a - arm_b), resampling tasks."""
    tasks = sorted(by_task)
    def diff(sample):
        da = [statistics.mean(by_task[t][arm_a]) for t in sample if by_task[t][arm_a]]
        db = [statistics.mean(by_task[t][arm_b]) for t in sample if by_task[t][arm_b]]
        return statistics.mean(da) - statistics.mean(db)
    rng = random.Random(seed)
    point = diff(tasks)
    draws = sorted(diff([rng.choice(tasks) for _ in tasks]) for _ in range(iters))
    return point, draws[int(0.025 * iters)], draws[int(0.975 * iters)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    d = ROOT / "results" / a.label
    graded = json.loads((d / "graded.json").read_text(encoding="utf-8"))
    runs = {f"{r['arm']}:{r['task']}:{r['rep']}": r for r in
            (json.loads(l) for l in (d / "runs.jsonl").read_text(encoding="utf-8").splitlines())}
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    arms = sorted({g["arm"] for g in graded})
    usable = [g for g in graded if g["judge"] is not None]
    L = [f"# Results: {a.label}", "",
         f"Model under test: `{meta['model']}` on both arms. Hermes backend: `{meta['hermes_backend']}`. "
         f"{len({g['task'] for g in graded})} tasks, {meta['reps']} repeats, {len(graded)} runs "
         f"({len(graded) - len(usable)} without a judge verdict).", ""]

    L += ["## Success rate", "", "| Arm | Runs | Judge correct | Wilson 95% (runs) | Programmatic correct |", "|---|---|---|---|---|"]
    for arm in arms:
        g = [x for x in usable if x["arm"] == arm]
        k = sum(x["judge"] for x in g)
        lo, hi = wilson(k, len(g))
        L.append(f"| {arm} | {len(g)} | {k}/{len(g)} = {k / len(g):.0%} | {lo:.0%} to {hi:.0%} | {sum(x['prog'] for x in g)}/{len(g)} |")

    # Runs a human has traced to the backend rather than to the harness (annotations.json, by run
    # id). They stay in every headline number above; this table shows what is left without them.
    ann_path = d / "annotations.json"
    ann = json.loads(ann_path.read_text(encoding="utf-8")) if ann_path.exists() else {}
    if ann:
        L += ["", f"### Excluding {len(ann)} runs annotated as backend artifacts", "",
              "| Arm | Runs | Judge correct | Wilson 95% (runs) |", "|---|---|---|---|"]
        for arm in arms:
            g = [x for x in usable if x["arm"] == arm and x["run"] not in ann]
            k = sum(x["judge"] for x in g)
            lo, hi = wilson(k, len(g))
            L.append(f"| {arm} | {len(g)} | {k}/{len(g)} = {k / len(g):.0%} | {lo:.0%} to {hi:.0%} |")
        L += ["", "Annotated runs:"] + [f"- `{k}`: {v}" for k, v in ann.items()]

    by_task = defaultdict(lambda: defaultdict(list))
    for x in usable:
        by_task[x["task"]][x["arm"]].append(x["judge"])
    if len(arms) == 2:
        p, lo, hi = task_bootstrap(by_task, arms[0], arms[1], "judge")
        L += ["", f"Difference in per-task success, {arms[0]} minus {arms[1]}: **{p:+.1%}** "
                  f"(95% bootstrap over tasks: {lo:+.1%} to {hi:+.1%}; n = {len(by_task)} tasks)."]

    L += ["", "## By task", "", "| Task | Kind | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    kinds = {x["task"]: x["kind"] for x in graded}
    for t in sorted(by_task, key=lambda t: [g["task"] for g in graded].index(t)):
        L.append(f"| {t} | {kinds[t]} | " + " | ".join(f"{sum(by_task[t][arm])}/{len(by_task[t][arm])}" for arm in arms) + " |")

    L += ["", "## Run-to-run consistency", ""]
    for arm in arms:
        same = sum(1 for t in by_task if len(set(by_task[t][arm])) == 1)
        L.append(f"- **{arm}:** {same} of {len(by_task)} tasks gave the same verdict on every repeat.")

    L += ["", "## Grader agreement", ""]
    k = kappa([x["judge"] for x in usable], [x["prog"] for x in usable])
    dis = [x for x in usable if x["judge"] != x["prog"]]
    L.append(f"- **Judge vs programmatic check:** Cohen's kappa = {'n/a (no variance)' if k is None else f'{k:.2f}'} "
             f"over {len(usable)} runs; {len(dis)} disagreements.")
    for x in dis:
        L.append(f"  - `{x['run']}`: judge {x['judge']}, programmatic {x['prog']}. Judge: {x['reason']}")
    sheet = d / "hand_labels.csv"
    hand = {}
    if sheet.exists():
        with sheet.open(encoding="utf-8-sig", newline="") as f:
            hand = {row["id"]: row["hand"].strip() for row in csv.DictReader(f) if row.get("hand", "").strip() in ("0", "1")}
    pairs = [(x["judge"], int(hand[h])) for x in usable
             if (h := hashlib.sha256(("blind\0" + x["run"]).encode()).hexdigest()[:10]) in hand]
    if pairs:
        k = kappa([p[0] for p in pairs], [p[1] for p in pairs])
        L.append(f"- **Judge vs human labels:** Cohen's kappa = {'n/a (no variance)' if k is None else f'{k:.2f}'} over {len(pairs)} labelled runs.")
    else:
        L.append("- **Judge vs human labels:** not available; `hand_labels.csv` has no labels filled in yet.")

    L += ["", "## What a run costs", "", "| Arm | Median wall time | Median tool calls | Errors or timeouts |", "|---|---|---|---|"]
    for arm in arms:
        rs = [r for r in runs.values() if r["arm"] == arm]
        L.append(f"| {arm} | {statistics.median(r['wall_s'] for r in rs):.0f} s | "
                 f"{statistics.median(len(r['tool_calls']) for r in rs):.0f} | {sum(1 for r in rs if r['error'])} |")
    if "127.0.0.1" in meta["hermes_backend"]:
        L += ["", "Hermes ran through a local translation shim, not the provider API: its wall times include a new "
                  "CLI process per model call with no prompt caching, and its token counts are not Hermes' own. "
                  "Treat the time column as an upper bound for Hermes and do not compare tokens."]

    L += ["", "## Failures (judge verdict incorrect)", ""]
    fails = [x for x in usable if x["judge"] == 0]
    if not fails:
        L.append("None.")
    for x in fails:
        r = runs[x["run"]]
        tail = " ".join(r["answer"].split())[-220:]
        L.append(f"- `{x['run']}` ({x['kind']}): {x['reason']}  \n  Tools: {', '.join(r['tool_calls']) or 'none'}. "
                 f"Error: {r['error'] or 'none'}.  \n  Answer tail: {tail or '(empty)'}")
    (d / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
