# agent-harness-eval

A small head-to-head evaluation of two agent harnesses on the same model: Hermes Agent and
Claude Code run headless. The question it asks is narrow: with the model, the prompt and the
files held fixed, does the harness around the model change how often a notes-lookup task is
answered correctly, how consistently, and at what cost per run?

## Result

On 50 tasks with 3 repeats per arm (300 runs, `claude-haiku-4-5` on both sides, real provider
API), the two harnesses are not distinguishable on accuracy.

| Arm | Judge correct | Wilson 95% (runs) | Tasks with the same verdict on all 3 repeats | Median wall time | Median tool calls |
|---|---|---|---|---|---|
| Claude Code | 135/150 = 90% | 84% to 94% | 46 of 50 | 16 s | 4 |
| Hermes Agent | 134/150 = 89% | 83% to 93% | 44 of 50 | 43 s | 6 |

Difference in per-task success, Claude Code minus Hermes: **+0.7 points** (95% bootstrap over
tasks: -6.7 to +7.3). With 50 tasks the interval is about 7 points either side, so a real gap
smaller than that would not show up here. The full tables are in
[`results/v2-api/report.md`](results/v2-api/report.md).

The equal totals hide different failures. What the traces show:

1. **37 tasks are solved 3/3 by both arms, 2 are failed 0/3 by both, and 11 differ.** On five of
   the 11 the majority verdict flips: Hermes wins T2 (stale runbook), D2 (renamed service) and U6
   (rota that stops before the date asked); Claude Code wins T3 (a chain of three changes) and C2
   (two pages that disagree with no precedence rule). The other six are single-repeat misses, five
   of them on the Hermes side, which is where its lower consistency comes from.
2. **Both arms usually start with a file listing; what differs is what their searches return.**
   The first call was a listing in 142 of 150 Claude Code runs (`Glob`) and in 101 of 150 Hermes
   runs (`search_files` with `target: files`; 37 of those listings came back empty). Hermes's
   content search returns the matching lines, and it ran one in 119 of 150 runs. Claude Code's
   `Grep` returns only file names unless it asks for lines: it searched contents in 81 runs, saw
   matching lines in 29, and ran no content search at all in 69. On T2 Claude Code listed the
   files in two runs and grepped for "on-call" in one, getting seven file names back; either way
   the path of the meeting note that overrides the runbook was in front of it, and all three
   times it read only `runbooks/on-call.md` and answered from it in two tool calls. Hermes's
   content search returned the meeting note's line about the shift change in all three runs (in
   one, after two listing attempts that came back empty), and it was right three times out of
   three. This is a reading of three traces per arm, not a tested cause, and searching for lines
   is not a general advantage: on T3 Hermes read the policy page and stopped in two of three
   runs, while Claude Code read the later notes every time.
3. **The two shared failures are at least partly the model.** On T6 (ownership handed over on a
   person's page) and C1 (a catalogue that states it is authoritative) both arms read the
   service page and stopped, 0/3 each. In the gold audit, the same Claude Code harness with a
   larger model answered both correctly, one run each. Hermes was not run on the larger model, so
   this shows the model can change the outcome, not that the harness plays no part.
4. **The harnesses behave differently at the turn limit.** Both were capped at 20 turns. Hermes
   reached the cap in 4 runs, exited with code 1, and still returned a final answer in all four;
   three were correct. Claude Code reached it in 2 runs and returned an empty result both times.
   Those two empty results are the whole of Claude Code's deficit on U6, so part of what this
   eval scores as accuracy is a budget policy.
5. **Hermes is slower here, and about half of that is tool execution.** Its tool calls took a
   median 3.7 s per search and 2.3 s per file read, 49% of wall time in the median run, plus about
   4 s outside the agent loop. The runs were made on Windows, so this is a measurement of this
   setup and not of Hermes in general.
6. **Cost per run is about the same.** Claude Code reported a median of $0.024 per run ($4.59 for
   150). Hermes reports token counts but no price; at list prices its runs come to a median of
   $0.019 to $0.023 ($4.07 to $5.35 in total), depending on which cache-write rate applies.
7. **Neither arm obeyed text addressed to an AI reader.** J1 and J2 were 6/6 on both.

### How far to trust the grading

The LLM judge (a different, larger model, blind to the arm) and the programmatic check agree on
295 of 300 runs, Cohen's kappa 0.91. The five disagreements:

- Three R3 answers name "the finance lead" without the person's name. The check requires the
  name; the judge accepted the role. Two are Hermes runs, one is Claude Code.
- `claude:L4:2` lists the three correct people and is marked wrong by the judge, whose own
  explanation starts to retract the verdict. This looks like a judge error against Claude Code.
- `hermes:C2:3` mentions both figures but commits to one. The check passed it; the judge did not.

Scoring those five the strict way gives 135/150 and 132/150, which is inside the same interval.

**Against a human.** I labelled a random 100 of the 300 answers by hand, blind to arm and to both
graders. The sheet `results/v2-api/hand_labels.csv` is in a seeded random order, and the sample is
its first 100 rows: 9 of them are judge-incorrect, against 31 of 300 overall. On the first pass
the judge and I agree on 95 of 100, **Cohen's kappa 0.71**. Kappa sits well below the raw
agreement because only about one answer in ten is wrong, so a handful of disagreements weighs a
lot.

I then took a second look at the five disagreements. Four were my errors, not the judge's: two
L4 answers that list exactly the reference names, a J1 answer that gives the reference date
(I had passed a near-identical answer later in the sheet), and a C2 answer that commits to 24
alone. After that review
agreement is 99 of 100, kappa 0.94. The one that remains is `hermes:C2:3`, which names both
figures but leans on one; the judge fails it and I pass it, and it is the same case the
programmatic check splits on above. Because only the disagreements were reviewed, the second
figure can only go up, so the first pass is the honest headline. The reviews and their reasons
are in `results/v2-api/hand_adjudicated.csv`; `hand_labels.csv` keeps the first pass as entered.

What this says about the judge: on this sample it was more consistent with the written rule than
I was on a first pass, and where it and a human still differ, the cause is a reference answer
(C2) that leaves room for judgement.

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
- **Same turn limit.** 20 turns on both arms. A turn may contain several tool calls, so a run can
  make more than 20 calls.
- **Synthetic corpus.** `corpus_gen.py` builds 94 markdown notes (175 KB) for an invented company
  from fixed tables and one seed. Nothing in it is answerable from training data. Gold answers are
  computed from the same tables that write the notes, and the generator asserts the properties the
  harder tasks depend on, including that every reference answer passes its own programmatic check.
- **Task kinds (v2, 50 tasks).** See the table below. Each run directory keeps a frozen copy of the
  task list it was given, so old runs are always graded against their own questions.
- **Two graders.** A programmatic check on the text after `FINAL ANSWER:` and an LLM judge that is
  a different model from the one under test and never sees the arm. Their agreement is reported as
  Cohen's kappa. `judge.py` also writes a blind, shuffled sheet for human labels, and `stats.py`
  reports judge-vs-human kappa over whatever part of it is filled, first pass and after review.
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

## Runs in this repo

| Label | What it is |
|---|---|
| `results/v2-api` | The result above: 50 tasks, 3 repeats, both arms, provider API |
| `results/v2-audit-sonnet` | Gold audit: Claude Code arm with a larger model, one repeat. 49/50 by the judge, 50/50 by the programmatic check |
| `results/v2-calib-haiku` | Difficulty check before the head-to-head: Claude Code arm, one repeat, 45/50 |
| `results/v2-smoke-api` | One task, one repeat per arm, to prove the provider API path before the full run |
| `results/pilot-shim` | v1 pilot, 12 tasks, Hermes behind a local translation layer. A pipeline check only; see Known limits |

The raw traces in `runs.jsonl` are as the harnesses emitted them, except that the local account
name in file paths, session and message identifiers, and thinking signatures have been replaced.

## Run it

```
python corpus_gen.py                      # corpus/ and tasks.json
python run.py --label pilot --reps 3      # results/pilot/runs.jsonl (resumable)
python judge.py --label pilot             # grades + hand_labels.csv
python label.py --label pilot --first 100 # optional: hand-label a random 100 in the terminal
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
- **Three repeats per task.** Enough to see that a task is unstable, not enough to estimate how
  unstable. The trace observations in the Result section describe what happened in these runs.
- **One model, one corpus, one domain, read-only.** A small model on notes lookup. Two long files,
  but no code, terminal or write tasks, which is most of what either harness is built for.
- **The turn limit is part of the score.** The two harnesses count and handle the limit
  differently (finding 4), and no run was scored with the limit raised.
- **Timing was measured on Windows.** Hermes' tool calls were slow there; the wall-time gap should
  be re-measured on Linux before it is read as a property of the harness.
- **Harness versions.** Hermes Agent at commit `af90026a`. The Claude Code version was not recorded
  in the run metadata.
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
- **The judge is validated on 100 runs, by one labeller.** One person labelled them, so there is
  no human-human agreement to compare the judge with, and nine wrong answers in the sample is few:
  one more or one fewer disagreement moves kappa by several points.

## What I would do next

Label the other 200 answers and add a second labeller, so the judge can be compared with
human-human agreement rather than with one person. Re-score with the turn limit
raised, so that budget policy and accuracy are separated. Add tasks to the stale and conflict
families, since that is where all the disagreement between the arms sits and each family has only
a handful of tasks. Repeat on a second model to see whether the T6 and C1 failures follow the
model as the audit suggests.
