# agent-harness-eval

A small head-to-head evaluation of two agent harnesses on the same model: Hermes Agent and
Claude Code run headless. The question it asks is narrow: with the model, the prompt and the
files held fixed, does the harness around the model change how often a notes-lookup task is
answered correctly, how consistently, and at what cost per run?

Status: pilot. 12 tasks, 3 repeats per arm. See `results/<label>/report.md`.

## Design

- **Same model on both arms.** Neither harness exposes temperature or a seed, so "same" means the
  same model id; run-to-run variance is measured with repeats instead of being suppressed.
- **Fresh state per run.** Each run gets a private copy of the corpus. Hermes gets a new profile
  (own sessions, memory, skills, state database) that is deleted afterwards, with skill creation,
  memory nudges, background review and the curator switched off. Claude Code runs with no saved
  session, no MCP servers, no user or project settings and no CLAUDE.md in the working directory.
  Without this, a second run can recall the first run's answer.
- **Same class of tools.** Hermes: its `file` toolset (`read_file`, `search_files`, `write_file`,
  `patch`). Claude Code: `Read`, `Grep`, `Glob`. The tasks are read-only. Each harness keeps its
  own shipped system prompt; that is part of what is being compared.
- **Synthetic corpus.** `corpus_gen.py` builds 66 markdown notes for an invented company from one
  seed. Nothing in it is answerable from training data, and the gold answers are computed from the
  same tables that generate the notes.
- **Task kinds.** Single-hop lookup, paraphrased lookup, two-hop joins, scan-and-compare, temporal
  supersession (a newer note overrides an older one that was never updated), aggregation over a
  folder, an unanswerable question with a tempting wrong answer nearby, and a listing task.
- **Two graders.** A programmatic check on the text after `FINAL ANSWER:` and an LLM judge that is
  a different model from the one under test and never sees the arm. Their agreement is reported as
  Cohen's kappa. `judge.py` also writes a blind, shuffled sheet for human labels; once filled,
  `stats.py` reports judge-vs-human kappa.
- **Intervals.** Per-arm success with a Wilson interval over runs (readable, but too narrow because
  repeats of a task are correlated), and the arm difference with a bootstrap over tasks, which is
  the unit actually sampled.

## Run it

```
python corpus_gen.py                      # corpus/ and tasks.json
python run.py --label pilot --reps 3      # results/pilot/runs.jsonl (resumable)
python judge.py --label pilot             # grades + hand_labels.csv
python stats.py --label pilot             # report.md
```

`run.py` expects a Hermes dev checkout with its runtime next to this folder (`../hermes-eval`, or
set `HERMES_EVAL_DIR`), and the `claude` CLI on PATH. By default the Hermes arm sends model calls
to `http://127.0.0.1:8765`; pass `--hermes-base-url "" --hermes-key-env ANTHROPIC_API_KEY` to use
the provider API directly.

## Known limits

- **Twelve tasks.** The task-level interval on the arm difference is wide by construction. The
  pilot exists to prove the pipeline and to size the full set, not to rank the harnesses.
- **One corpus, one domain, short files.** No long-context, code or terminal tasks yet.
- **Backend for the Hermes arm.** Runs labelled `-shim` sent Hermes' model calls through a local
  translation layer onto a headless CLI. In those runs the model chose tools from schemas pasted as
  text, history was flattened, and timing and token figures are not Hermes' own. Accuracy from a
  `-shim` run is a pipeline check, not a result about Hermes.
- **Tool sets are similar, not identical.** Hermes' file toolset includes two write tools that
  Claude Code was not given.
- **The LLM judge is unvalidated until the human labels are in.**
