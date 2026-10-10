# agent-harness-eval

A small head-to-head evaluation of two agent harnesses on the same model: Hermes Agent and
Claude Code run headless. The question it asks is narrow: with the model, the prompt and the
files held fixed, does the harness around the model change how often a notes-lookup task is
answered correctly, how consistently, and at what cost per run?

Status: task set v2 (50 tasks) built and audited; the head-to-head on v2 has not been run yet.
The v1 pilot (12 tasks, 3 repeats per arm) is in `results/pilot-shim/`.

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
- **Synthetic corpus.** `corpus_gen.py` builds 94 markdown notes (175 KB) for an invented company
  from fixed tables and one seed. Nothing in it is answerable from training data. Gold answers are
  computed from the same tables that write the notes, and the generator asserts the properties the
  harder tasks depend on, including that every reference answer passes its own programmatic check.
- **Task kinds (v2, 50 tasks).** See the table below. Each run directory keeps a frozen copy of the
  task list it was given, so old runs are always graded against their own questions.
- **Two graders.** A programmatic check on the text after `FINAL ANSWER:` and an LLM judge that is
  a different model from the one under test and never sees the arm. Their agreement is reported as
  Cohen's kappa. `judge.py` also writes a blind, shuffled sheet for human labels; once filled,
  `stats.py` reports judge-vs-human kappa.
- **Intervals.** Per-arm success with a Wilson interval over runs (readable, but too narrow because
  repeats of a task are correlated), and the arm difference with a bootstrap over tasks, which is
  the unit actually sampled.

## What the tasks test

| Family | Tasks | What goes wrong if the harness or model is careless |
|---|---|---|
| Lookup and two-note joins | R1-R3, M1-M3 | Anchors; expected to be near ceiling |
| Stale versus current | T1-T7 | Answers from the first page found. Shapes: a later decision, a chain of three, a trial that was reverted, a proposal never decided, a change not yet in effect, a hand-over recorded only on a person's page |
| Long files | G1-G4, H1-H2 | A 1,755-line deploy log too large for one read; a handbook whose amendment sits 500 lines after the rule it changes |
| Conflicts and names | C1, C2, D1, D2 | Two pages disagree with a stated precedence rule; two disagree with none; two people share a surname; a service was renamed |
| Joins of three or more | M4-M8 | Stops one hop short; follows dependencies only one level |
| Aggregation | A1-A6 | Counts from a partial read; includes a contract that ended |
| Unanswerable | U1-U6 | Fills the gap with a nearby value: missing attribute, missing entity, false premise, half-answerable, a rota that stops before the date asked |
| Listing and negation | L1-L4 | Incomplete or over-complete lists; computed membership |
| Arithmetic | K1-K4 | Dates, units, which interval a date falls in |
| Planted instructions | J1, J2 | Obeys text in a file that is addressed to an AI reader |

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

- **Fifty tasks, written by one person.** The task-level interval on the arm difference is still
  wide, and the mix of task families is a choice, not a sample of real work. Per-family numbers
  rest on two to seven tasks each.
- **One corpus, one domain, read-only.** Two long files, but no code, terminal or write tasks.
- **Some reference answers are judgement calls.** C2 (report both figures), T7 (a change not yet in
  effect) and the planted-instruction tasks have a defensible gold, not a provable one. They are
  the tasks where the judge and the human labels matter most.
- **The programmatic check is loose on purpose for "not recorded" answers** and cannot tell a
  hedged answer from a committed one; the LLM judge is the grader of record and the programmatic
  check is its cross-check.
- **Backend for the Hermes arm.** Runs labelled `-shim` sent Hermes' model calls through a local
  translation layer onto a headless CLI. In those runs the model chose tools from schemas pasted as
  text, history was flattened, and timing and token figures are not Hermes' own. Accuracy from a
  `-shim` run is a pipeline check, not a result about Hermes.
- **Tool sets are similar, not identical.** Hermes' file toolset includes two write tools that
  Claude Code was not given.
- **The LLM judge is unvalidated until the human labels are in.**
