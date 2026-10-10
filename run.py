"""Run every task on both harnesses, k times each, with fresh state per run.

Arms
  hermes  Hermes Agent at a pinned commit, `file` toolset, fresh HERMES_HOME per run, the
          self-modifying features (skill creation, memory nudges, background review, curator) off.
  claude  Claude Code headless (`claude -p`), tools Read/Grep/Glob, no MCP, no saved session,
          run in a fresh copy of the corpus with no CLAUDE.md.

Both get the same model, the same prompt text and a private copy of the same corpus. Each run is
one JSON record in results/<label>/runs.jsonl; a run that already has a record is skipped, so an
interrupted sweep resumes.

Usage: python run.py --label pilot --reps 3 [--arms hermes,claude] [--tasks R1,T1] [--model claude-haiku-4-5]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HERMES_EVAL = Path(os.environ.get("HERMES_EVAL_DIR", ROOT.parent / "hermes-eval"))
HERMES_REPO = HERMES_EVAL / "hermes-agent"
HERMES_RUNTIME = HERMES_EVAL / "runtime"
TIMEOUT = 900

PROMPT = (
    "You are working in the current directory, which holds a company's internal notes as markdown "
    "files in subfolders. Answer the question using only what these files say. Work autonomously "
    "and do not ask questions. If the notes do not contain the answer, say so instead of guessing. "
    "End your reply with one line that starts with 'FINAL ANSWER:'.\n\nQuestion: {q}"
)

HERMES_CONFIG = """\
model:
  provider: anthropic
  default: {model}
auth:
  adopt_external_logins: false
agent:
  max_turns: {max_turns}
auxiliary:
  background_review:
    enabled: false
skills:
  creation_nudge_interval: 0
memory:
  nudge_interval: 0
curator:
  enabled: false
"""


def child_env(extra=None):
    """The parent's environment minus anything that ties a child to this Claude Code session or
    hands it a provider key the arm did not ask for."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE") or k.startswith("CODEX_") or k == "AI_AGENT" or k.endswith("_API_KEY"))}
    env["PYTHONUTF8"] = "1"
    env.update(extra or {})
    return env


def fresh_corpus():
    # realpath: on Windows the temp dir can come back as an 8.3 short path, and Claude Code then
    # sees the files' long paths as outside its working directory and asks for permission.
    ws = Path(os.path.realpath(tempfile.mkdtemp(prefix="ahe-ws-")))
    shutil.copytree(ROOT / "corpus", ws, dirs_exist_ok=True)
    return ws


def hermes_python():
    return next(HERMES_RUNTIME.glob("python-*/python.exe"), None) or next(HERMES_RUNTIME.glob("python-*/bin/python3"))


_hermes_env = None


def hermes_env(home: Path, ws: Path, backend: dict):
    """Hermes' own composed environment (what activate.ps1 sets), plus this run's home and cwd."""
    global _hermes_env
    if _hermes_env is None:
        base = child_env({"HERMES_RUNTIME_DIR": str(HERMES_RUNTIME), "PYTHONPATH": str(HERMES_REPO)})
        out = subprocess.run([str(hermes_python()), "-m", "pm.environments"], env=base, capture_output=True,
                             text=True, encoding="utf-8", timeout=120)
        if out.returncode:
            raise SystemExit("ABORT: could not read Hermes' environment: " + out.stderr[-400:])
        composed = json.loads(out.stdout)
        _hermes_env = {k: composed[k] for k in ("PATH", "PYTHONPATH", "PYTHONUTF8", "HERMES_RUNTIME_DIR",
                                                "AGENT_BROWSER_EXECUTABLE_PATH", "PLAYWRIGHT_BROWSERS_PATH",
                                                "__HERMES_ACTIVATED") if k in composed}
    return child_env({**_hermes_env, "HERMES_HOME": str(home), "TERMINAL_CWD": str(ws), **backend})


def run_hermes(q, model, max_turns, backend):
    ws = fresh_corpus()
    # A profile under the installing home, not a temp dir elsewhere: Hermes scopes its dependency
    # environment per data root and only <root>/profiles/<name> borrows the root's install. The
    # profile still has its own sessions, memory, skills and state.db, and is deleted after the run.
    home = HERMES_EVAL / "home" / "profiles" / f"ahe-{uuid.uuid4().hex[:12]}"
    home.mkdir(parents=True)
    (home / "config.yaml").write_text(HERMES_CONFIG.format(model=model, max_turns=max_turns), encoding="utf-8")
    qfile = home / "query.txt"
    qfile.write_text(PROMPT.format(q=q), encoding="utf-8")
    argv = [str(hermes_python()), "-m", "hermes_cli.main", "chat", "--query-file", str(qfile), "--oneshot",
            "--format", "stream-json", "--max-turns", str(max_turns), "-t", "file", "--yolo"]
    t0 = time.monotonic()
    rec = {"tool_calls": [], "model_calls": None, "tokens": {}, "error": None, "answer": ""}
    try:
        p = subprocess.run(argv, cwd=str(ws), env=hermes_env(home, ws, backend), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=TIMEOUT)
        rec["exit"] = p.returncode
        events = []
        for line in p.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        rec["events"] = events
        for e in events:
            if e.get("type") == "tool_use":
                rec["tool_calls"].append(e.get("name"))
            elif e.get("type") == "result":
                rec["answer"] = e.get("text") or ""
                rec["tokens"] = {"tokens": e.get("tokens"), "duration_ms": e.get("duration_ms")}
                if e.get("exit_code"):
                    rec["error"] = f"hermes exit_code {e.get('exit_code')}"
        if p.returncode and not rec["answer"]:
            rec["error"] = (p.stderr or p.stdout)[-600:]
    except subprocess.TimeoutExpired:
        rec["error"] = f"timeout after {TIMEOUT}s"
    finally:
        rec["wall_s"] = round(time.monotonic() - t0, 1)
        shutil.rmtree(ws, ignore_errors=True)
        shutil.rmtree(home, ignore_errors=True)
    return rec


def run_claude(q, model, max_turns, backend):
    ws = fresh_corpus()
    exe = shutil.which("claude") or "claude"
    argv = [exe, "-p", "--model", model, "--strict-mcp-config", "--no-session-persistence",
            "--setting-sources", "", "--disable-slash-commands", "--max-turns", str(max_turns),
            "--output-format", "stream-json", "--verbose", "--allowedTools", "Read,Grep,Glob",
            "--tools", "Read,Grep,Glob"]
    t0 = time.monotonic()
    rec = {"tool_calls": [], "model_calls": 0, "tokens": {}, "error": None, "answer": ""}
    try:
        p = subprocess.run(argv, cwd=str(ws), env=child_env({"ENABLE_CLAUDEAI_MCP_SERVERS": "false", "CLAUDE_BRAIN_NO_HOOK": "1"}),
                           input=PROMPT.format(q=q), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=TIMEOUT)
        rec["exit"] = p.returncode
        events = []
        for line in p.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        rec["events"] = [e for e in events if e.get("type") in ("assistant", "user", "result")]
        for e in events:
            if e.get("type") == "assistant":
                rec["model_calls"] += 1
                for block in (e.get("message") or {}).get("content") or []:
                    if block.get("type") == "tool_use":
                        rec["tool_calls"].append(block.get("name"))
            elif e.get("type") == "result":
                rec["answer"] = e.get("result") or ""
                rec["tokens"] = {"usage": e.get("usage"), "estimated_cost_usd": e.get("total_cost_usd"),
                                 "duration_ms": e.get("duration_ms"), "num_turns": e.get("num_turns")}
                if e.get("is_error"):
                    rec["error"] = str(e.get("subtype") or e.get("result"))[:600]
        if p.returncode and not rec["answer"]:
            rec["error"] = (p.stderr or p.stdout)[-600:]
    except subprocess.TimeoutExpired:
        rec["error"] = f"timeout after {TIMEOUT}s"
    finally:
        rec["wall_s"] = round(time.monotonic() - t0, 1)
        shutil.rmtree(ws, ignore_errors=True)
    return rec


ARMS = {"hermes": run_hermes, "claude": run_claude}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--arms", default="hermes,claude")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--max-turns", type=int, default=20)
    ap.add_argument("--hermes-base-url", default="http://127.0.0.1:8765",
                    help="where Hermes sends model calls; empty string = the real Anthropic API (needs --hermes-key-env)")
    ap.add_argument("--hermes-key-env", default="", help="name of the env var holding a real API key for the Hermes arm")
    a = ap.parse_args()

    tasks = json.loads((ROOT / "tasks.json").read_text(encoding="utf-8"))
    if a.tasks:
        tasks = [t for t in tasks if t["id"] in a.tasks.split(",")]
    backend = {"ANTHROPIC_API_KEY": os.environ[a.hermes_key_env] if a.hermes_key_env else "shim-placeholder"}
    if a.hermes_base_url:
        backend["ANTHROPIC_BASE_URL"] = a.hermes_base_url
    out_dir = ROOT / "results" / a.label
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = out_dir / "runs.jsonl"
    done = set()
    if runs.exists():
        for line in runs.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["arm"], r["task"], r["rep"]))
    (out_dir / "meta.json").write_text(json.dumps({
        "model": a.model, "max_turns": a.max_turns, "reps": a.reps, "arms": a.arms,
        "hermes_backend": a.hermes_base_url or "api.anthropic.com", "prompt": PROMPT}, indent=2), encoding="utf-8")

    for rep in range(1, a.reps + 1):
        for task in tasks:
            for arm in a.arms.split(","):
                if (arm, task["id"], rep) in done:
                    continue
                rec = ARMS[arm](task["q"], a.model, a.max_turns, backend)
                rec.update(arm=arm, task=task["id"], rep=rep, kind=task["kind"])
                with runs.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                tail = re.sub(r"\s+", " ", rec["answer"])[-90:]
                print(f"[rep{rep}] {arm:6} {task['id']:3} {rec['wall_s']:6.1f}s tools={len(rec['tool_calls'])} "
                      f"err={bool(rec['error'])} | {tail}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
