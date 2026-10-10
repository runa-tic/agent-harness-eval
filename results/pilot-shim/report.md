# Results: pilot-shim

Model under test: `claude-haiku-4-5` on both arms. Hermes backend: `http://127.0.0.1:8765`. 12 tasks, 3 repeats, 72 runs (0 without a judge verdict).

## Success rate

| Arm | Runs | Judge correct | Wilson 95% (runs) | Programmatic correct |
|---|---|---|---|---|
| claude | 36 | 33/36 = 92% | 78% to 97% | 33/36 |
| hermes | 36 | 31/36 = 86% | 71% to 94% | 31/36 |

### Excluding 4 runs annotated as backend artifacts

| Arm | Runs | Judge correct | Wilson 95% (runs) |
|---|---|---|---|
| claude | 36 | 33/36 = 92% | 78% to 97% |
| hermes | 32 | 31/32 = 97% | 84% to 99% |

Annotated runs:
- `hermes:R1:2`: backend artifact: model tried to call search_files as a native function inside the CLI, got 'not available', and gave up; Hermes never received a tool call
- `hermes:A2:2`: backend artifact: same; reply cites 'No such tool available' errors that come from the CLI behind the shim, not from Hermes
- `hermes:T2:2`: backend artifact: model searched the shim's own working directory (claude-p-shim-cwd), which the CLI told it was the cwd, instead of the corpus
- `hermes:R3:3`: backend artifact: reply ended after a one-line preamble with no tool call, so Hermes treated it as the final answer

Difference in per-task success, claude minus hermes: **+5.6%** (95% bootstrap over tasks: -5.6% to +16.7%; n = 12 tasks).

## By task

| Task | Kind | claude | hermes |
|---|---|---|---|
| R1 | single-hop | 3/3 | 2/3 |
| R2 | single-hop-paraphrase | 3/3 | 3/3 |
| R3 | single-hop | 3/3 | 2/3 |
| M1 | multi-hop | 3/3 | 3/3 |
| M2 | multi-hop-scan | 3/3 | 3/3 |
| M3 | multi-hop | 3/3 | 3/3 |
| T1 | temporal | 3/3 | 3/3 |
| T2 | temporal | 0/3 | 1/3 |
| A1 | aggregation | 3/3 | 3/3 |
| A2 | aggregation | 3/3 | 2/3 |
| U1 | unanswerable | 3/3 | 3/3 |
| L1 | listing | 3/3 | 3/3 |

## By kind of task

| Kind | Tasks | claude | hermes |
|---|---|---|---|
| aggregation | 2 | 6/6 | 5/6 |
| listing | 1 | 3/3 | 3/3 |
| multi | 3 | 9/9 | 9/9 |
| single | 3 | 9/9 | 7/9 |
| temporal | 2 | 3/6 | 4/6 |
| unanswerable | 1 | 3/3 | 3/3 |

## Run-to-run consistency

- **claude:** 12 of 12 tasks gave the same verdict on every repeat.
- **hermes:** 8 of 12 tasks gave the same verdict on every repeat.

## Grader agreement

- **Judge vs programmatic check:** Cohen's kappa = 1.00 over 72 runs; 0 disagreements.
- **Judge vs human labels:** not available; `hand_labels.csv` has no labels filled in yet.

## What a run costs

| Arm | Median wall time | Median tool calls | Errors or timeouts |
|---|---|---|---|
| claude | 13 s | 3 | 0 |
| hermes | 49 s | 3 | 0 |

Hermes ran through a local translation shim, not the provider API: its wall times include a new CLI process per model call with no prompt caching, and its token counts are not Hermes' own. Treat the time column as an upper bound for Hermes and do not compare tokens.

## Failures (judge verdict incorrect)

- `claude:T2:1` (temporal): The answer says 7 days, which is the outdated runbook value; the correct current length is 5 days.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days, handing over on Monday at 10:00.
- `hermes:R1:2` (single-hop): The answer states it could not determine the port and never gives 7443.  
  Tools: none. Error: none.  
  Answer tail: nvironment. Without access to file search or directory listing tools, I cannot access the markdown files to answer your question. FINAL ANSWER: Unable to determine - no access to file search tools in current environment.
- `hermes:T2:2` (temporal): The answer found no notes and gave no shift length; it never states the correct 5 days.  
  Tools: search_files, search_files, search_files, search_files. Error: none.  
  Answer tail: down files or any other files. No company internal notes are present to search. FINAL ANSWER: The notes do not contain information about on-call shift length because no markdown files were found in the current directory.
- `claude:T2:2` (temporal): Answer says 7 days, which is the outdated runbook value; the current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days.
- `hermes:A2:2` (aggregation): The answer gives no total cost; it only says file access failed, never stating EUR 263,900.  
  Tools: none. Error: none.  
  Answer tail: I cannot access the files in the current directory because the file access tools are not available in this environment. The search_files and read_file actions returned "No such tool available" errors.
- `hermes:R3:3` (single-hop): The answer only states an attempt to locate files and never names Mirela Okafor or any approver.  
  Tools: none. Error: none.  
  Answer tail: Attempting to locate markdown files in the current directory.
- `hermes:T2:3` (temporal): Answer says 7 days (outdated runbook value); the current shift length is 5 days since 2026-04-06.  
  Tools: search_files, read_file. Error: none.  
  Answer tail: The on-call documentation clearly states that an on-call shift lasts 7 days, with handover occurring on Monday at 10:00. FINAL ANSWER: An on-call shift is 7 days long.
- `claude:T2:3` (temporal): The answer says 7 days, which is the outdated runbook value; the correct current length is 5 days.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days, handing over on Monday at 10:00.
