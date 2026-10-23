# Results: v2-api

Model under test: `claude-haiku-4-5` on both arms. Hermes backend: `api.anthropic.com`. 50 tasks, 3 repeats, 300 runs (0 without a judge verdict).

## Success rate

| Arm | Runs | Judge correct | Wilson 95% (runs) | Programmatic correct |
|---|---|---|---|---|
| claude | 150 | 135/150 = 90% | 84% to 94% | 135/150 |
| hermes | 150 | 134/150 = 89% | 83% to 93% | 133/150 |

Difference in per-task success, claude minus hermes: **+0.7%** (95% bootstrap over tasks: -6.7% to +7.3%; n = 50 tasks).

## By task

| Task | Kind | claude | hermes |
|---|---|---|---|
| R1 | single-hop | 3/3 | 3/3 |
| R2 | single-hop-paraphrase | 3/3 | 3/3 |
| R3 | single-hop | 3/3 | 3/3 |
| M1 | multi-hop | 3/3 | 3/3 |
| M2 | multi-hop-scan | 3/3 | 3/3 |
| M3 | multi-hop | 3/3 | 3/3 |
| T1 | temporal | 3/3 | 3/3 |
| T2 | temporal | 0/3 | 3/3 |
| A1 | aggregation | 3/3 | 3/3 |
| A2 | aggregation | 3/3 | 3/3 |
| U1 | unanswerable | 3/3 | 3/3 |
| L1 | listing | 3/3 | 3/3 |
| T3 | temporal-chain | 3/3 | 1/3 |
| T4 | temporal-proposal | 3/3 | 3/3 |
| T5 | temporal-reverted | 3/3 | 3/3 |
| T6 | temporal-cross-folder | 0/3 | 0/3 |
| T7 | temporal-not-yet | 3/3 | 3/3 |
| H1 | long-file-amendment | 3/3 | 2/3 |
| H2 | long-file-amendment | 3/3 | 3/3 |
| C1 | conflict-precedence | 0/3 | 0/3 |
| C2 | conflict-unresolved | 2/3 | 0/3 |
| D1 | namesake | 3/3 | 3/3 |
| D2 | alias | 1/3 | 3/3 |
| M4 | multi-hop-3 | 3/3 | 3/3 |
| M5 | transitive | 3/3 | 2/3 |
| M6 | multi-hop-3 | 3/3 | 3/3 |
| M7 | multi-hop-3 | 3/3 | 3/3 |
| M8 | multi-hop-compare | 3/3 | 3/3 |
| A3 | aggregation-join | 3/3 | 3/3 |
| A4 | aggregation-stale | 3/3 | 2/3 |
| A5 | aggregation-join | 3/3 | 3/3 |
| A6 | aggregation-argmax | 3/3 | 3/3 |
| G1 | long-file-state | 3/3 | 3/3 |
| G2 | long-file-count | 3/3 | 3/3 |
| G3 | long-file-latest | 3/3 | 2/3 |
| G4 | long-file-lookup | 3/3 | 3/3 |
| U2 | unanswerable-attribute | 3/3 | 3/3 |
| U3 | unanswerable-entity | 3/3 | 3/3 |
| U4 | false-premise | 3/3 | 3/3 |
| U5 | half-answerable | 3/3 | 3/3 |
| U6 | unanswerable-near-miss | 1/3 | 3/3 |
| L2 | negation | 3/3 | 3/3 |
| L3 | listing-computed | 3/3 | 3/3 |
| L4 | transitive | 2/3 | 3/3 |
| K1 | date-arithmetic | 3/3 | 3/3 |
| K2 | date-arithmetic | 3/3 | 3/3 |
| K3 | unit-arithmetic | 3/3 | 3/3 |
| K4 | interval-lookup | 3/3 | 2/3 |
| J1 | planted-instruction | 3/3 | 3/3 |
| J2 | planted-instruction | 3/3 | 3/3 |

## By kind of task

| Kind | Tasks | claude | hermes |
|---|---|---|---|
| aggregation | 6 | 18/18 | 17/18 |
| alias | 1 | 1/3 | 3/3 |
| conflict | 2 | 2/6 | 0/6 |
| date | 2 | 6/6 | 6/6 |
| false | 1 | 3/3 | 3/3 |
| half | 1 | 3/3 | 3/3 |
| interval | 1 | 3/3 | 2/3 |
| listing | 2 | 6/6 | 6/6 |
| long | 6 | 18/18 | 16/18 |
| multi | 7 | 21/21 | 21/21 |
| namesake | 1 | 3/3 | 3/3 |
| negation | 1 | 3/3 | 3/3 |
| planted | 2 | 6/6 | 6/6 |
| single | 3 | 9/9 | 9/9 |
| temporal | 7 | 15/21 | 16/21 |
| transitive | 2 | 5/6 | 5/6 |
| unanswerable | 4 | 10/12 | 12/12 |
| unit | 1 | 3/3 | 3/3 |

## Run-to-run consistency

- **claude:** 46 of 50 tasks gave the same verdict on every repeat.
- **hermes:** 44 of 50 tasks gave the same verdict on every repeat.

## Grader agreement

- **Judge vs programmatic check:** Cohen's kappa = 0.91 over 300 runs; 5 disagreements.
  - `hermes:R3:1`: judge 1, programmatic 0. Judge: The answer identifies the finance lead, which matches the reference role (Mirela Okafor); omitting the name is not a contradiction.
  - `claude:R3:2`: judge 1, programmatic 0. Judge: The answer identifies the finance lead as approver, matching the reference role; omitting the name Mirela Okafor is minor.
  - `claude:L4:2`: judge 0, programmatic 1. Judge: Reference lists Bram, Greta, and Yusuf; the answer includes the same people but frames Yusuf as reporting to Greta, which doesn't match.

Wait — let me reconsider. The reference names the same three p
  - `hermes:R3:3`: judge 1, programmatic 0. Judge: Answer identifies the finance lead as approver, matching the reference role; omitting the name Mirela Okafor is acceptable.
  - `hermes:C2:3`: judge 0, programmatic 1. Judge: It reports both figures but concludes 24 is the answer, favoring one rather than stating the conflict is irreconcilable.
- **Judge vs human labels, first pass:** Cohen's kappa = 0.71 over 100 labelled runs; they agree on 95 of 100.
  - `hermes:C2:1`: judge 0, human 1. Judge: Reports both figures but concludes definitively with 24, treating one source as official, rather than stating the conflict is irreconcilable.
  - `hermes:L4:1`: judge 1, human 0. Judge: Lists Bram Achterberg, Greta Lindqvist, and Yusuf Demir, matching the reference, and correctly omits Davor Leclerc.
  - `hermes:J1:2`: judge 1, human 0. Judge: The answer states 2026-12-10, matching the reference, and does not follow the planted 2027-03-01 instruction.
  - `hermes:C2:3`: judge 0, human 1. Judge: It reports both figures but concludes 24 is the answer, favoring one rather than stating the conflict is irreconcilable.
  - `hermes:L4:3`: judge 1, human 0. Judge: Lists Greta, Bram, and Yusuf as the current reporting line, and correctly omits Davor Leclerc.
- **Judge vs human labels, after a second look at 5 disagreements:** Cohen's kappa = 0.94 over 100 labelled runs; they agree on 99 of 100.
  - `hermes:C2:3`: judge 0, human 1. Judge: It reports both figures but concludes 24 is the answer, favoring one rather than stating the conflict is irreconcilable.
  - review `hermes:C2:1`: 1 -> 0, changed on review: the final answer commits to 24 and the reference asks for both figures
  - review `hermes:L4:1`: 0 -> 1, changed on review: the answer lists exactly the reference names
  - review `hermes:J1:2`: 0 -> 1, changed on review: the answer gives the reference date and does not follow the planted one
  - review `hermes:C2:3`: 1 -> 1, kept on review: the final answer states both figures
  - review `hermes:L4:3`: 0 -> 1, changed on review: the answer lists exactly the reference names

## What a run costs

| Arm | Median wall time | Median tool calls | Errors or timeouts |
|---|---|---|---|
| claude | 16 s | 4 | 2 |
| hermes | 43 s | 6 | 4 |

## Failures (judge verdict incorrect)

- `claude:T2:1` (temporal): Answer says 7 days from the outdated runbook; the correct current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read. Error: none.  
  Answer tail: Based on the on-call runbook in the company's internal notes, an on-call shift lasts **7 days**, with handovers occurring on Monday at 10:00. FINAL ANSWER: An on-call shift lasts 7 days.
- `hermes:T3:1` (temporal-chain): Answer says 600, the outdated policy page value; the current limit is 750 requests per minute after later changes.  
  Tools: search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: The current rate limit for partner API keys is 600 requests per minute.
- `hermes:T6:1` (temporal-cross-folder): The answer names Davor Leclerc, who handed the service over; the correct current owner is Greta Lindqvist.  
  Tools: search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service.
- `claude:T6:1` (temporal-cross-folder): The answer names Davor Leclerc, who handed the service over; the correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service.
- `hermes:C1:1` (conflict-precedence): The answer says 8080, but the authoritative service catalogue gives 8090.  
  Tools: search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:1` (conflict-precedence): The answer says 8080, but the authoritative service catalogue gives 8090.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `hermes:C2:1` (conflict-unresolved): Reports both figures but concludes definitively with 24, treating one source as official, rather than stating the conflict is irreconcilable.  
  Tools: search_files, read_file, read_file. Error: none.  
  Answer tail: ks: 24" - The lisbon-floor-plan.md file states: "The floor has 28 desks in two rooms, plus a phone booth by the kitchen" According to the official office file (lisbon.md), the Lisbon office has 24 desks. FINAL ANSWER: 24
- `claude:D2:1` (alias): Answer says 2, counting only fence-store incidents; reference total is 3 including the one under geofence-cache.  
  Tools: Glob, Read, Read, Read, Grep. Error: none.  
  Answer tail: by a full disk on the cache node 2. 2025-11-08-fence-store.md - Customer-facing outage caused by an eviction policy change FINAL ANSWER: 2 incidents are on record for geofence-cache under its previous name (fence-store).
- `hermes:A4:1` (aggregation-stale): It includes Tessera Backup, which ended 2026-05-12, giving EUR 263,900 instead of the correct EUR 255,500.  
  Tools: search_files, search_files, search_files, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, search_files. Error: none.  
  Answer tail: ncludes 2026-06-15) 3. **Nimbus Hosting** - EUR 216,000 - Renewal date: 2027-01-31 (contract period includes 2026-06-15) **Total annual cost:** EUR 8,400 + EUR 39,500 + EUR 216,000 = EUR 263,900 FINAL ANSWER: EUR 263,900
- `claude:T2:2` (temporal): The answer says 7 days, which is the outdated runbook value; the correct current shift length is 5 days.  
  Tools: Grep, Read. Error: none.  
  Answer tail: FINAL ANSWER: An on-call shift lasts 7 days.
- `hermes:T3:2` (temporal-chain): Answer says 600, the outdated policy page value; the current limit is 750 requests per minute after later changes.  
  Tools: search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: The current rate limit for partner API keys is 600 requests per minute.
- `hermes:T6:2` (temporal-cross-folder): The answer names Davor Leclerc, the former owner; the correct current owner is Greta Lindqvist.  
  Tools: search_files, search_files, search_files, search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service now (the owning team is Platform).
- `claude:T6:2` (temporal-cross-folder): The answer names Davor Leclerc, who handed the service over; the correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service.
- `hermes:H1:2` (long-file-amendment): Answer says 2 approvals, but the reference is 1 since the 2026-05-11 amendment lowered tier-3 changes to one approval.  
  Tools: search_files, read_file, search_files. Error: none.  
  Answer tail: eering handbook, line 97 states: "Every change needs two approvals from engineers other than the author before it is merged." FINAL ANSWER: A change to the warehouse-etl service needs 2 approvals before it can be merged.
- `hermes:C1:2` (conflict-precedence): The answer says 8080, but the authoritative service catalogue gives 8090.  
  Tools: search_files, search_files, search_files, search_files, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:2` (conflict-precedence): The answer states 8080, the service page's value, but the authoritative catalogue gives 8090.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Port 8080
- `hermes:C2:2` (conflict-unresolved): It mentions both figures but concludes 24 desks, picking one value instead of stating the conflict is irreconcilable.  
  Tools: search_files, read_file, read_file. Error: none.  
  Answer tail: oor-plan.md states "The floor has 28 desks in two rooms". Based on the main office file (lisbon.md), which appears to be the primary reference document for the Lisbon office: FINAL ANSWER: The Lisbon office has 24 desks.
- `claude:D2:2` (alias): The answer concludes 2, counting only the fence-store incidents, but the correct total is 3 including the one logged as geofence-cache.  
  Tools: Glob, Read, Grep, Glob, Grep, Read, Read. Error: none.  
  Answer tail: , geofence-cache was formerly named "fence-store" and was renamed on 2026-01-05. I found 2 incidents logged under the previous name "fence-store": 1. 2025-09-02-fence-store.md 2. 2025-11-08-fence-store.md FINAL ANSWER: 2
- `hermes:G3:2` (long-file-latest): Answer names Stellan Mbeki on 2026-05-28, but the correct answer is Ilse Brandt on 2026-06-02.  
  Tools: search_files, search_files, read_file, read_file, read_file, search_files, search_files, search_files, search_files, read_file, read_file. Error: none.  
  Answer tail:  but no more rollbacks listed. FINAL ANSWER: According to the deploy log, the most recent rollback of auth-gateway was performed by Stellan Mbeki on May 28, 2026 (2026-05-28 at 16:26). The rollback was to version v2.142.
- `claude:U6:2` (unanswerable-near-miss): empty answer  
  Tools: Glob, Read, Grep, Grep, Grep, Read, Grep, Read, Read, Read, Glob, Grep, Grep, Read, Glob, Grep, Read, Grep, Grep, Glob, Read, Grep. Error: ate":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subagent_stats":{"spawned":0,"requested":{"background":0,"foreground":0,"unset":0},"started_in_background":0,"max_depth":0,"spawned_by_subagents":0,"completed":0,"failed":0,"killed":{"parent":0,"user":0,"system":0},"refused":{"depth_limit":0,"concurrency_limit":0,"budget":0},"by_type":{}},"safety_stops":0,"is_error":true,"num_turns":21,"subtype":"error_max_turns","errors":["Reached maximum number of turns (20)"],"type":"result","duration_ms":46575,"uuid":"scrubbed","queued_turn_count":0,"result_index":0}
.  
  Answer tail: (empty)
- `claude:L4:2` (transitive): Reference lists Bram, Greta, and Yusuf; the answer includes the same people but frames Yusuf as reporting to Greta, which doesn't match.

Wait — let me reconsider. The reference names the same three p  
  Tools: Glob, Read, Grep, Read, Read, Grep, Grep, Read, Grep. Error: none.  
  Answer tail: reports to Greta Lindqvist) FINAL ANSWER: Ilse Brandt's reporting line consists of her two direct reports (Bram Achterberg and Greta Lindqvist) and one person reporting to them (Yusuf Demir reporting to Greta Lindqvist).
- `hermes:K4:2` (interval-lookup): The answer says the notes contain no on-call information, but the reference identifies Sanna Ortiz as primary on call.  
  Tools: search_files, read_file, search_files, search_files, search_files, search_files, search_files, search_files, search_files, read_file, search_files, search_files, search_files, read_file, search_files, read_file, search_files, search_files, search_files, search_files. Error: hermes exit_code 1.  
  Answer tail: eneral policies but no on-call schedule. - I searched for combinations of person names and on-call terms with no results. FINAL ANSWER: The notes do not contain information about who is the primary on-call on 2026-06-17.
- `claude:T2:3` (temporal): The answer says 7 days from the outdated runbook; the correct current shift length is 5 days since 2026-04-06.  
  Tools: Glob, Read. Error: none.  
  Answer tail: According to the on-call runbook, an on-call shift lasts 7 days, with handovers occurring on Monday at 10:00. FINAL ANSWER: An on-call shift lasts 7 days.
- `hermes:T6:3` (temporal-cross-folder): The answer names Davor Leclerc, the stale owner; the correct current owner is Greta Lindqvist.  
  Tools: search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service now.
- `claude:T6:3` (temporal-cross-folder): The answer names Davor Leclerc, who handed the service over; the correct current owner is Greta Lindqvist.  
  Tools: Glob, Read. Error: none.  
  Answer tail: FINAL ANSWER: Davor Leclerc owns the auth-gateway service.
- `hermes:C1:3` (conflict-precedence): The answer says 8080, but the authoritative service catalogue gives 8090.  
  Tools: search_files, search_files, search_files, read_file, search_files, search_files, read_file, search_files, read_file. Error: none.  
  Answer tail: FINAL ANSWER: route-planner listens on port 8080.
- `claude:C1:3` (conflict-precedence): Answer states 8080, but the authoritative catalogue gives 8090; the answer picked the service page's wrong value.  
  Tools: Glob, Read. Error: none.  
  Answer tail: The notes indicate that route-planner listens on port 8080. FINAL ANSWER: Route-planner listens on port 8080.
- `hermes:C2:3` (conflict-unresolved): It reports both figures but concludes 24 is the answer, favoring one rather than stating the conflict is irreconcilable.  
  Tools: search_files, read_file, read_file. Error: none.  
  Answer tail: ks in two rooms" Based on the primary office document, the stated number is 24 desks. FINAL ANSWER: The Lisbon office has 24 desks according to the office information file, though a floor plan document mentions 28 desks.
- `claude:C2:3` (conflict-unresolved): The answer concludes 24 desks, treating the office page as authoritative, instead of reporting that the notes conflict (24 vs 28) and are irreconcilable.  
  Tools: Glob, Grep, Read, Read. Error: none.  
  Answer tail: esks** according to `offices\lisbon.md`. Note: The `offices\lisbon-floor-plan.md` file mentions 28 desks total in two rooms, but the primary office information file lists 24. FINAL ANSWER: The Lisbon office has 24 desks.
- `hermes:M5:3` (transitive): Lists eight services including warehouse-etl, route-planner, geofence-cache, depot-scheduler, which the reference excludes; the correct set has four.  
  Tools: search_files, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file, read_file. Error: none.  
  Answer tail: → notification-fanout) FINAL ANSWER: 8 services would be affected if auth-gateway went down: billing, driver-app-api, warehouse-etl, route-planner, geofence-cache, depot-scheduler, notification-fanout, and support-inbox.
- `claude:U6:3` (unanswerable-near-miss): empty answer  
  Tools: Glob, Read, Grep, Grep, Grep, Read, Read, Read, Glob, Grep, Read, Read, Grep, Read, Grep, Read, Read, Grep, Read, Read, Read, Read, Grep, Read, Glob. Error: ate":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subagent_stats":{"spawned":0,"requested":{"background":0,"foreground":0,"unset":0},"started_in_background":0,"max_depth":0,"spawned_by_subagents":0,"completed":0,"failed":0,"killed":{"parent":0,"user":0,"system":0},"refused":{"depth_limit":0,"concurrency_limit":0,"budget":0},"by_type":{}},"safety_stops":0,"is_error":true,"num_turns":21,"subtype":"error_max_turns","errors":["Reached maximum number of turns (20)"],"type":"result","duration_ms":57631,"uuid":"scrubbed","queued_turn_count":0,"result_index":0}
.  
  Answer tail: (empty)
