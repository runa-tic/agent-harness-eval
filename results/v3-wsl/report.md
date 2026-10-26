# Results: v3-wsl

Model under test: `claude-haiku-4-5` on both arms. Hermes backend: `api.anthropic.com`. 50 tasks, 3 repeats, 300 runs (0 without a judge verdict).

## Success rate

| Arm | Runs | Judge correct | Wilson 95% (runs) | Programmatic correct |
|---|---|---|---|---|
| claude | 150 | 140/150 = 93% | 88% to 96% | 139/150 |
| hermes | 150 | 134/150 = 89% | 83% to 93% | 137/150 |

Difference in per-task success, claude minus hermes: **+4.0%** (95% bootstrap over tasks: -1.3% to +9.3%; n = 50 tasks).

## By task

| Task | Kind | claude | hermes |
|---|---|---|---|
| R1 | single-hop | 3/3 | 3/3 |
| R2 | single-hop-paraphrase | 3/3 | 2/3 |
| R3 | single-hop | 3/3 | 3/3 |
| M1 | multi-hop | 3/3 | 2/3 |
| M2 | multi-hop-scan | 3/3 | 3/3 |
| M3 | multi-hop | 3/3 | 3/3 |
| T1 | temporal | 3/3 | 3/3 |
| T2 | temporal | 0/3 | 1/3 |
| A1 | aggregation | 3/3 | 3/3 |
| A2 | aggregation | 3/3 | 3/3 |
| U1 | unanswerable | 3/3 | 3/3 |
| L1 | listing | 3/3 | 3/3 |
| T3 | temporal-chain | 3/3 | 2/3 |
| T4 | temporal-proposal | 3/3 | 3/3 |
| T5 | temporal-reverted | 3/3 | 3/3 |
| T6 | temporal-cross-folder | 0/3 | 2/3 |
| T7 | temporal-not-yet | 3/3 | 3/3 |
| H1 | long-file-amendment | 3/3 | 2/3 |
| H2 | long-file-amendment | 3/3 | 2/3 |
| C1 | conflict-precedence | 0/3 | 0/3 |
| C2 | conflict-unresolved | 3/3 | 2/3 |
| D1 | namesake | 3/3 | 3/3 |
| D2 | alias | 3/3 | 3/3 |
| M4 | multi-hop-3 | 3/3 | 3/3 |
| M5 | transitive | 3/3 | 2/3 |
| M6 | multi-hop-3 | 3/3 | 3/3 |
| M7 | multi-hop-3 | 3/3 | 3/3 |
| M8 | multi-hop-compare | 3/3 | 3/3 |
| A3 | aggregation-join | 3/3 | 3/3 |
| A4 | aggregation-stale | 3/3 | 3/3 |
| A5 | aggregation-join | 3/3 | 2/3 |
| A6 | aggregation-argmax | 3/3 | 3/3 |
| G1 | long-file-state | 3/3 | 3/3 |
| G2 | long-file-count | 3/3 | 3/3 |
| G3 | long-file-latest | 3/3 | 3/3 |
| G4 | long-file-lookup | 3/3 | 3/3 |
| U2 | unanswerable-attribute | 3/3 | 3/3 |
| U3 | unanswerable-entity | 3/3 | 3/3 |
| U4 | false-premise | 3/3 | 3/3 |
| U5 | half-answerable | 3/3 | 3/3 |
| U6 | unanswerable-near-miss | 2/3 | 3/3 |
| L2 | negation | 3/3 | 3/3 |
| L3 | listing-computed | 3/3 | 2/3 |
| L4 | transitive | 3/3 | 2/3 |
| K1 | date-arithmetic | 3/3 | 3/3 |
| K2 | date-arithmetic | 3/3 | 3/3 |
| K3 | unit-arithmetic | 3/3 | 3/3 |
| K4 | interval-lookup | 3/3 | 3/3 |
| J1 | planted-instruction | 3/3 | 3/3 |
| J2 | planted-instruction | 3/3 | 3/3 |

## By kind of task

| Kind | Tasks | claude | hermes |
|---|---|---|---|
| aggregation | 6 | 18/18 | 17/18 |
| alias | 1 | 3/3 | 3/3 |
| conflict | 2 | 3/6 | 2/6 |
| date | 2 | 6/6 | 6/6 |
| false | 1 | 3/3 | 3/3 |
| half | 1 | 3/3 | 3/3 |
| interval | 1 | 3/3 | 3/3 |
| listing | 2 | 6/6 | 5/6 |
| long | 6 | 18/18 | 16/18 |
| multi | 7 | 21/21 | 20/21 |
| namesake | 1 | 3/3 | 3/3 |
| negation | 1 | 3/3 | 3/3 |
| planted | 2 | 6/6 | 6/6 |
| single | 3 | 9/9 | 8/9 |
| temporal | 7 | 15/21 | 17/21 |
| transitive | 2 | 6/6 | 4/6 |
| unanswerable | 4 | 11/12 | 12/12 |
| unit | 1 | 3/3 | 3/3 |

## Run-to-run consistency

- **claude:** 49 of 50 tasks gave the same verdict on every repeat.
- **hermes:** 38 of 50 tasks gave the same verdict on every repeat.

## Grader agreement

- **Judge vs programmatic check:** Cohen's kappa = 0.83 over 300 runs; 8 disagreements.
  - `hermes:R2:1`: judge 0, programmatic 1. Judge: The final conclusion says notes lack raw GPS ping retention info, rather than stating 45 days; it hedges and denies the reference fact.
  - `hermes:T3:1`: judge 0, programmatic 1. Judge: Final conclusion hedges between 600 and 750, presenting conflicting records instead of stating 750 as the current limit.
  - `hermes:H1:1`: judge 0, programmatic 1. Judge: The answer declines to give a number, saying warehouse-etl's tier is undocumented, whereas the reference is 1 approval (tier 3).
  - `hermes:H2:1`: judge 0, programmatic 1. Judge: The answer declines to conclude, saying billing's tier is unknown, instead of stating the reference's 2 approvals for tier 1.
  - `hermes:R3:2`: judge 1, programmatic 0. Judge: Answer identifies the finance lead as approver, matching the reference role, though it omits the name Mirela Okafor.
  - `hermes:R3:3`: judge 1, programmatic 0. Judge: Answer identifies the finance lead as the approver, matching the reference; omitting the name Mirela Okafor is not a conflict.
  - `claude:R3:3`: judge 1, programmatic 0. Judge: Answer identifies the finance lead as approver, matching the reference; omitting the name Mirela Okafor is acceptable since the role matches.
  - `hermes:L4:3`: judge 0, programmatic 1. Judge: Omits Yusuf Demir as a member of the reporting line? No: includes him, but misclassifies him as reporting to Greta, whereas reference lists him as a direct report.

Correction: the reference lists Bra
- **Judge vs human labels:** not available; `hand_labels.csv` has no labels filled in yet.

## What a run costs

| Arm | Median wall time | Median tool calls | Errors or timeouts |
|---|---|---|---|
| claude | 17 s | 4 | 1 |
| hermes | 19 s | 7 | 3 |

## Failures (judge verdict incorrect)

- `hermes:R2:1` (single-hop-paraphrase): The final conclusion says notes lack raw GPS ping retention info, rather than stating 45 days; it hedges and denies the reference fact.  
  Tools: search_files, read_file, search_files. Error: none.  
  Answer tail: etention periods for raw GPS pings specifically. FINAL ANSWER: The notes state that location traces from driver devices are purged after 45 days, but do not contain information specifically about raw GPS pings retention.
- `claude:T2:1` (temporal): The answer states 7 days, taken from the outdated runbook; the correct current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read, Read, Read. Error: none.  
  Answer tail: Based on the company's internal notes, I found the answer in the on-call runbook. FINAL ANSWER: An on-call shift lasts 7 days, handing over on Monday at 10:00.
- `hermes:T3:1` (temporal-chain): Final conclusion hedges between 600 and 750, presenting conflicting records instead of stating 750 as the current limit.  
  Tools: search_files, read_file, search_files, search_files, read_file, read_file. Error: none.  
  Answer tail: ere are conflicting records: the policy file states 600 requests per minute, but the most recent meeting decision (May 25, 2026) set the rate limit to 750 requests per minute for partner API keys after a May 21 incident.
- `hermes:T6:1` (temporal-cross-folder): The answer names Davor Leclerc, the outdated owner; the correct current owner is Greta Lindqvist.  
  Tools: search_files, search_files, search_files, search_files, search_files, search_files, read_file, search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service now.
- `claude:T6:1` (temporal-cross-folder): Answer names Davor Leclerc, the outdated owner; correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: Based on the markdown files in this directory, the auth-gateway service documentation clearly states the owner. FINAL ANSWER: Davor Leclerc owns the auth-gateway service now.
- `hermes:H1:1` (long-file-amendment): The answer declines to give a number, saying warehouse-etl's tier is undocumented, whereas the reference is 1 approval (tier 3).  
  Tools: search_files, read_file, search_files, search_files, search_files, read_file, search_files, search_files, read_file, search_files, search_files, search_files. Error: none.  
  Answer tail: exact number of approvals required. The handbook states that tier-3 services need 1 approval while tier-1 and tier-2 services need 2 approvals, but warehouse-etl's classification is not documented in the available files.
- `hermes:H2:1` (long-file-amendment): The answer declines to conclude, saying billing's tier is unknown, instead of stating the reference's 2 approvals for tier 1.  
  Tools: search_files, search_files, search_files, read_file, search_files, search_files, search_files, search_files, read_file, search_files, search_files, search_files. Error: none.  
  Answer tail: umber of approvals needed. The general rule requires two approvals, but tier-3 services only need one approval (as of the 2026-05-11 amendment), and the billing service's tier is not specified in the available documents.
- `hermes:C1:1` (conflict-precedence): The answer states port 8080, but the correct port is 8090 per the authoritative service catalogue.  
  Tools: search_files, search_files, search_files, search_files, search_files. Error: none.  
  Answer tail: Perfect! I found the answer in the services documentation. FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:1` (conflict-precedence): The answer says 8080, but the correct authoritative port from the service catalogue is 8090.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `hermes:A5:1` (aggregation-join): Answer says 1 (only Greta); reference is 2 (Bram Achterberg and Greta Lindqvist), and it omits Bram.  
  Tools: search_files, read_file, search_files, search_files, search_files, search_files, search_files, search_files, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file. Error: none.  
  Answer tail: -04, so no longer on Platform team) Since Davor Leclerc moved from the Platform team to the Data team on 2026-05-04, the current Platform team members based in the Lisbon office is only: - Greta Lindqvist FINAL ANSWER: 1
- `hermes:T2:2` (temporal): The answer says 7 days, which is the outdated runbook value; the current shift length is 5 days.  
  Tools: search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days.
- `claude:T2:2` (temporal): Answer says 7 days, the outdated runbook value; the current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days, handing over on Monday at 10:00.
- `claude:T6:2` (temporal-cross-folder): The answer names Davor Leclerc, the outdated owner; the correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service (Platform team).
- `hermes:C1:2` (conflict-precedence): The answer says 8080, but the correct authoritative port from the service catalogue is 8090.  
  Tools: search_files, search_files, search_files, search_files, search_files, read_file, read_file, read_file, read_file, read_file, search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:2` (conflict-precedence): The answer says 8080, but the authoritative service catalogue gives 8090, so the conclusion is wrong.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Route-planner listens on port 8080.
- `hermes:M5:2` (transitive): Includes extra services (warehouse-etl, route-planner, geofence-cache, depot-scheduler) that don't depend on auth-gateway; correct set is four services.  
  Tools: search_files, search_files, read_file, read_file, search_files, search_files, search_files, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file. Error: none.  
  Answer tail: 8 other services would be affected: billing, driver-app-api (directly); and warehouse-etl, route-planner, geofence-cache, depot-scheduler, notification-fanout, and support-inbox (indirectly through the dependency chain).
- `claude:U6:2` (unanswerable-near-miss): empty answer  
  Tools: Glob, Read, Read, Grep, Grep, Grep, Read, Grep, Glob, Grep, Read, Read, Glob, Grep, Glob, Grep, Glob, Glob, Read, Grep. Error: :{}},"safety_stops":0,"is_error":true,"num_turns":21,"subtype":"error_max_turns","errors":["Reached maximum number of turns (20)"],"type":"result","duration_ms":44872,"uuid":"scrubbed","queued_turn_count":0,"result_index":0,"model_usage_since_last_result":{"claude-haiku-4-5":{"inputTokens":162,"outputTokens":2657,"cacheReadInputTokens":677064,"cacheCreationInputTokens":43339,"webSearchRequests":0,"costUSD":0.13532715,"contextWindow":200000,"maxOutputTokens":32000,"thinkingTokens":1066,"canonicalModel":"claude-haiku-4-5","provider":"firstParty","costBasis":"list"}}}
.  
  Answer tail: (empty)
- `hermes:L3:2` (listing-computed): Omits Lumen Translate (2026-06-23); the answer lists only Corvid Maps and Brightline SMS.  
  Tools: search_files, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file. Error: none.  
  Answer tail: in June 2026 are: - **Corvid Maps**: Deadline 2026-06-17 (June 17, 2026) - **Brightline SMS**: Deadline 2026-06-01 (June 1, 2026) FINAL ANSWER: Corvid Maps and Brightline SMS have notice deadlines that fall in June 2026.
- `hermes:M1:3` (multi-hop): The answer fails to give 4417 or identify Tomas Vrana; it concludes the notes lack enough information.  
  Tools: search_files, search_files, search_files, search_files, search_files, search_files, read_file, read_file, search_files, read_file, search_files, search_files, search_files, read_file, search_files, read_file, search_files, search_files, read_file, search_files, search_files. Error: hermes exit_code 1.  
  Answer tail: he notes do not contain enough information in the files I was able to read to definitively answer this question. A `./services/billing.md` file exists that likely contains the answer, but I could not access its contents.
- `hermes:T2:3` (temporal): The answer says 7 days, which is the outdated runbook value; the current shift length is 5 days.  
  Tools: search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days.
- `claude:T2:3` (temporal): Answer states 7 days from the outdated runbook; the correct current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read, Read. Error: none.  
  Answer tail: Based on the on-call runbook in the company's internal notes: FINAL ANSWER: An on-call shift lasts 7 days, handing over on Monday at 10:00.
- `claude:T6:3` (temporal-cross-folder): The answer names Davor Leclerc, the stale owner; the correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service.
- `hermes:C1:3` (conflict-precedence): The answer says 8080, but the correct port is 8090 per the authoritative service catalogue.  
  Tools: search_files, search_files, read_file. Error: none.  
  Answer tail: Perfect! I found the answer in the route-planner service documentation. FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:3` (conflict-precedence): The answer says 8080, but the correct authoritative port from the service catalogue is 8090.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `hermes:C2:3` (conflict-unresolved): The answer states only 28 desks, omitting the conflicting 24 figure from the office page; the reference requires reporting both.  
  Tools: search_files, search_files. Error: none.  
  Answer tail: Perfect! I found the information about the Lisbon office's desks in the `./offices/lisbon-floor-plan.md` file. FINAL ANSWER: The Lisbon office has 28 desks.
- `hermes:L4:3` (transitive): Omits Yusuf Demir as a member of the reporting line? No: includes him, but misclassifies him as reporting to Greta, whereas reference lists him as a direct report.

Correction: the reference lists Bra  
  Tools: search_files, search_files, search_files, read_file, read_file, read_file, search_files, read_file. Error: none.  
  Answer tail: indqvist) I found no one reporting to Bram Achterberg in the notes. FINAL ANSWER: Ilse Brandt's direct reports are Bram Achterberg and Greta Lindqvist. Their direct report is Yusuf Demir (who reports to Greta Lindqvist).
