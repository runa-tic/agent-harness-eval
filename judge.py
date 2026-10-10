"""Grade every run twice, independently: a programmatic check and an LLM judge.

The programmatic check applies each task's regexes to the text after the last 'FINAL ANSWER:'.
The LLM judge sees the question, the gold answer and the full reply, never the arm, and is a
different model from the one under test. Verdicts are cached in results/<label>/grades.jsonl.

It also writes results/<label>/hand_labels.csv: every run in shuffled order, blind to arm and to
both graders, with an empty `hand` column for a human to fill with 1 (correct) or 0. stats.py
reads that column to report judge-vs-human agreement.

Usage: python judge.py --label pilot-shim [--judge-model claude-sonnet-5-5]
"""
import argparse, csv, hashlib, json, os, random, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

JUDGE_PROMPT = """You are grading one answer to a question about a set of company notes.

Question: {q}

Reference answer (correct by construction): {gold}

Answer to grade:
<answer>
{answer}
</answer>

Grade CORRECT only if the answer's final conclusion states the same fact as the reference. Extra
correct detail is fine. Grade INCORRECT if the conclusion is wrong, missing, hedged between the
right and a wrong value, or invents something the reference says is not recorded. An empty answer
is INCORRECT. Reply with exactly one line: VERDICT: CORRECT or VERDICT: INCORRECT, then a dash and
a reason of at most 20 words."""


def final_segment(answer: str) -> str:
    i = answer.rfind("FINAL ANSWER:")
    return answer[i + len("FINAL ANSWER:"):] if i >= 0 else answer


def programmatic(task, answer: str) -> int:
    seg = final_segment(answer)
    if not seg.strip():
        return 0
    if any(not re.search(m, seg, re.I | re.S) for m in task["must"]):
        return 0
    if task.get("trap") and re.search(task["trap"], seg, re.I | re.S):
        return 0
    return 1


def ask_judge(prompt: str, model: str):
    exe = shutil.which("claude") or "claude"
    env = {k: v for k, v in os.environ.items() if not (k.startswith("CLAUDE") or k.endswith("_API_KEY"))}
    env.update(ENABLE_CLAUDEAI_MCP_SERVERS="false", CLAUDE_BRAIN_NO_HOOK="1", PYTHONUTF8="1")
    cwd = os.path.realpath(tempfile.mkdtemp(prefix="ahe-judge-"))
    try:
        p = subprocess.run([exe, "-p", "--model", model, "--strict-mcp-config", "--no-session-persistence",
                            "--setting-sources", "", "--disable-slash-commands", "--tools", ""],
                           input=prompt, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300)
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    m = re.search(r"VERDICT:\s*(CORRECT|INCORRECT)\b\s*[-—–:]*\s*(.*)", p.stdout, re.S)
    if not m:
        return None, (p.stdout or p.stderr).strip()[:200]
    return int(m.group(1) == "CORRECT"), m.group(2).strip()[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--judge-model", default="claude-sonnet-5-5")
    a = ap.parse_args()
    d = ROOT / "results" / a.label
    tasks = {t["id"]: t for t in json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))}
    runs = [json.loads(l) for l in (d / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    gpath = d / "grades.jsonl"
    cache = {}
    if gpath.exists():
        for l in gpath.read_text(encoding="utf-8").splitlines():
            g = json.loads(l)
            cache[g["key"]] = g

    out = []
    for r in runs:
        t = tasks[r["task"]]
        rid = f"{r['arm']}:{r['task']}:{r['rep']}"
        key = hashlib.sha256((a.judge_model + "\0" + r["task"] + "\0" + r["answer"]).encode("utf-8")).hexdigest()[:20]
        g = cache.get(key)
        if g is None or g.get("judge") is None:
            verdict, reason = (0, "empty answer") if not r["answer"].strip() else ask_judge(
                JUDGE_PROMPT.format(q=t["q"], gold=t["gold"], answer=r["answer"]), a.judge_model)
            g = {"key": key, "judge": verdict, "reason": reason, "judge_model": a.judge_model}
            cache[key] = g
            with gpath.open("a", encoding="utf-8") as f:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
        out.append({"run": rid, "arm": r["arm"], "task": r["task"], "rep": r["rep"], "kind": r["kind"],
                    "prog": programmatic(t, r["answer"]), "judge": g["judge"], "reason": g["reason"]})
        print(f"{rid:16} prog={out[-1]['prog']} judge={g['judge']} | {g['reason'][:80]}", flush=True)
    (d / "graded.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    sheet = d / "hand_labels.csv"
    done = {}
    if sheet.exists():
        with sheet.open(encoding="utf-8-sig", newline="") as f:
            done = {row["id"]: row.get("hand", "") for row in csv.DictReader(f)}
    rows = []
    for r in runs:
        rid = f"{r['arm']}:{r['task']}:{r['rep']}"
        blind = hashlib.sha256(("blind\0" + rid).encode()).hexdigest()[:10]
        rows.append({"id": blind, "question": tasks[r["task"]]["q"], "reference": tasks[r["task"]]["gold"],
                     "answer": r["answer"].strip()[-1500:], "hand": done.get(blind, "")})
    random.Random(7).shuffle(rows)
    with sheet.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "question", "reference", "answer", "hand"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(out)} runs graded -> {d / 'graded.json'}; hand-label sheet -> {sheet}")


if __name__ == "__main__":
    sys.exit(main())
