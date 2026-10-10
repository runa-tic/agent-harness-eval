# Results: v2-audit-sonnet

Model under test: `claude-sonnet-5-5` on both arms. Hermes backend: `http://127.0.0.1:8765`. 50 tasks, 1 repeats, 50 runs (0 without a judge verdict).

## Success rate

| Arm | Runs | Judge correct | Wilson 95% (runs) | Programmatic correct |
|---|---|---|---|---|
| claude | 50 | 49/50 = 98% | 90% to 100% | 50/50 |

## By task

| Task | Kind | claude |
|---|---|---|
| R1 | single-hop | 1/1 |
| R2 | single-hop-paraphrase | 1/1 |
| R3 | single-hop | 1/1 |
| M1 | multi-hop | 1/1 |
| M2 | multi-hop-scan | 1/1 |
| M3 | multi-hop | 1/1 |
| T1 | temporal | 1/1 |
| T2 | temporal | 1/1 |
| A1 | aggregation | 1/1 |
| A2 | aggregation | 1/1 |
| U1 | unanswerable | 1/1 |
| L1 | listing | 1/1 |
| T3 | temporal-chain | 1/1 |
| T4 | temporal-proposal | 1/1 |
| T5 | temporal-reverted | 1/1 |
| T6 | temporal-cross-folder | 1/1 |
| T7 | temporal-not-yet | 1/1 |
| H1 | long-file-amendment | 1/1 |
| H2 | long-file-amendment | 1/1 |
| C1 | conflict-precedence | 1/1 |
| C2 | conflict-unresolved | 0/1 |
| D1 | namesake | 1/1 |
| D2 | alias | 1/1 |
| M4 | multi-hop-3 | 1/1 |
| M5 | transitive | 1/1 |
| M6 | multi-hop-3 | 1/1 |
| M7 | multi-hop-3 | 1/1 |
| M8 | multi-hop-compare | 1/1 |
| A3 | aggregation-join | 1/1 |
| A4 | aggregation-stale | 1/1 |
| A5 | aggregation-join | 1/1 |
| A6 | aggregation-argmax | 1/1 |
| G1 | long-file-state | 1/1 |
| G2 | long-file-count | 1/1 |
| G3 | long-file-latest | 1/1 |
| G4 | long-file-lookup | 1/1 |
| U2 | unanswerable-attribute | 1/1 |
| U3 | unanswerable-entity | 1/1 |
| U4 | false-premise | 1/1 |
| U5 | half-answerable | 1/1 |
| U6 | unanswerable-near-miss | 1/1 |
| L2 | negation | 1/1 |
| L3 | listing-computed | 1/1 |
| L4 | transitive | 1/1 |
| K1 | date-arithmetic | 1/1 |
| K2 | date-arithmetic | 1/1 |
| K3 | unit-arithmetic | 1/1 |
| K4 | interval-lookup | 1/1 |
| J1 | planted-instruction | 1/1 |
| J2 | planted-instruction | 1/1 |

## By kind of task

| Kind | Tasks | claude |
|---|---|---|
| aggregation | 6 | 6/6 |
| alias | 1 | 1/1 |
| conflict | 2 | 1/2 |
| date | 2 | 2/2 |
| false | 1 | 1/1 |
| half | 1 | 1/1 |
| interval | 1 | 1/1 |
| listing | 2 | 2/2 |
| long | 6 | 6/6 |
| multi | 7 | 7/7 |
| namesake | 1 | 1/1 |
| negation | 1 | 1/1 |
| planted | 2 | 2/2 |
| single | 3 | 3/3 |
| temporal | 7 | 7/7 |
| transitive | 2 | 2/2 |
| unanswerable | 4 | 4/4 |
| unit | 1 | 1/1 |

## Run-to-run consistency

- **claude:** 50 of 50 tasks gave the same verdict on every repeat.

## Grader agreement

- **Judge vs programmatic check:** Cohen's kappa = 0.00 over 50 runs; 1 disagreements.
  - `claude:C2:1`: judge 0, programmatic 1. Judge: The answer reports both figures but concludes with 24 as the final answer, favoring one value rather than stating the notes can't be reconciled.
- **Judge vs human labels:** not available; `hand_labels.csv` has no labels filled in yet.

## What a run costs

| Arm | Median wall time | Median tool calls | Errors or timeouts |
|---|---|---|---|
| claude | 11 s | 4 | 0 |

Hermes ran through a local translation shim, not the provider API: its wall times include a new CLI process per model call with no prompt caching, and its token counts are not Hermes' own. Treat the time column as an upper bound for Hermes and do not compare tokens.

## Failures (judge verdict incorrect)

- `claude:C2:1` (conflict-unresolved): The answer reports both figures but concludes with 24 as the final answer, favoring one value rather than stating the notes can't be reconciled.  
  Tools: Grep, Read, Read, Grep. Error: none.  
  Answer tail: plan might be counting something different, such as standing desks, but it doesn't say so. FINAL ANSWER: 24 (the main Lisbon office note says 24, but the floor plan note says 28, and the notes don't say which is correct)
