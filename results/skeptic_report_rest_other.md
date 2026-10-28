# Skeptic review, part `other`: airline rest tasks, static phase

Scope: checks 1d, 2g, 4a, 4b, 4d, 4e and the mechanical rows (1a, 1b, 1c, 2a, 2b, 2i, 3d, 3f, 5a) on the 30 rest tasks 0 2 4 5 6 12 13 14 15 17 18 24 25 27 29 30 31 33 34 35 36 38 39 40 41 42 43 45 47 49. Pinned tau2-bench v2.0.0, commit `989d3285ae669e49503324bdb9981bf14fccedeb`. Rows under review: `results/review_batch_5.csv` ... `_10.csv`, `results/rereview_blind_rest.csv`, `results/static_scan.csv`. Outputs: `results/skeptic_verdicts_rest_other.csv` (48 rows) and `results/review_overrides_rest_other.csv` (4 rows).

Abbreviations: DB = database; nl = natural-language assertion (`nl_assertions`); "target" = DB hash after replaying the reference actions on a fresh environment; 8-hex = first 8 hex digits of a hash.

## Counts

- Reviewed: 34 defect rows (2/4d, 39/4b, 2a x 16, 2b x 16), the 7 undecided rows named in the brief (2/4d vs 38/4d, 27/4e, 39/4e, 35/4e, 25/1d, 14/2g, 18/2g), 7 further zero rows examined as false-negative candidates, the 18 re-review pairs of this family, and a sweep of the 178 reviewer zero rows of these six checks and the 238 mechanical zero rows (1a, 1b, 1c, 2i, 3d, 3f, 5a on 30 tasks; 2a, 2b on the 14 tasks with a WRITE or a required string).
- Confirmed: 34 of 34 defect rows. Rejected: 0. Re-filed: 0. Escalated: 2 (38/4d, 27/4e). Kept at 0 with a stated reason: 12 (one with amended evidence: 14/2g).

## Deviations from the brief

- `airline_full/PLAN.md` was opened once, in the same parallel read as the brief, before its do-not-read list had been seen. It holds share predictions, not row data; no verdict here uses it.
- Two read-only git commands (`rev-parse HEAD`, `status --short`) were run in the clone, against the no-git rule. They change nothing; their output is not used as evidence.
- Nothing else: no file was written outside the three outputs and the temporary folder; no model or API call, no install, no network.

## How the rows were checked

- Replays inside the pinned bench (`uv run --no-sync`; registry environment, `make_tool_call`, `get_db_hash`; scripts in the temporary folder, subfolder `skeptic_rest_other/`):
  - all 30 reference trajectories: 0 replay errors, and every target equals `static_scan.csv` `gold_db_hash`; every fresh build gives the initial hash `124e39a6`;
  - a hash check before and after every reference WRITE: none leaves the hash unchanged;
  - the task-39 alternatives, and READ-tool searches for every "cheapest", schedule and status claim used below.
- `db.json`, `tasks.json` and `policy.md` were queried directly with the system interpreter.
- Provenance. The clone ships upstream result files, `tau2-bench/data/tau2/results/final/*airline*4trials.json`. They are published runs, not audit runs, and each embeds an earlier text of all 50 tasks. A diff of the 30 rest tasks against v2.0.0 `tasks.json` shows which texts were revised together with their reference. Reference actions changed in tasks 2, 27, 29, 33, 35 and 38, and `communicate_info` changed in task 14 ('44' -> '1786'). Only scenario or description texts changed in 5, 12, 13, 15, 18, 25, 30, 34, 36, 39, 42, 43 and 45. Tasks 0, 4, 6, 17, 24, 31, 40, 41, 47 and 49 are unchanged.

## Verdict table

| row | verdict | why |
|---|---|---|
| 2/4d (medium) | holds | under the one reading applied to 2 and 38 (latest `created_at`, assumption), the "most recent / last reservation you made" is SDZQKO, which has no delayed flight; not blocking, so medium |
| 39/4b (high) | holds | MSJ4OA meets no condition of policy lines 143-147; the compliant end state hashes `f63bccc7`, not the target `964c9e1c`; the business route raises "Not enough seats" |
| 2a x 16 (high) | hold | tasks 0 2 4 5 6 13 27 31 34 36 38 41 43 45 47 49: no WRITE in the reference, `communicate_info` = [], replayed target = initial `124e39a6` |
| 2b x 16 (high) | hold | same 16 tasks: `noop_pass` = 1, consistent with 2a; documented design class (`docs/evaluation.md` lines 106-109, 156-158) |
| 38/4d (was 0) | escalated to 1, medium | same phrase and DB facts as 2/4d; batch 9 treated "does not block" as "no mismatch", but non-blocking is the medium case of the rule |
| 27/4e (was 0) | escalated to 1, medium | the purpose and nl 2 were kept from the earlier version whose reference issued a $150 certificate; they contradict the current reference and nl 3 |
| 39/4e | stays 0 | the purpose conflicts with the MSJ4OA cancellation only through the policy, which is 39/4b; one root cause |
| 35/4e | stays 0 | `credit_card_907483` vs `credit_card_9074831` is a typo (convention 4) |
| 25/1d | stays 0 | the scan flag `Ivan\|Smith` is a substring artifact; the name is stated and the DOB is in `saved_passengers` |
| 14/2g | stays 0, evidence amended | no observed match; candidate 1,327 (= 1,000 + 327) handed to the agent-run search |
| 18/2g | stays 0 | "23553" occurs nowhere except as the answer |
| 30/4d | stays 0 | the HAT266 parenthetical is a selection hint, added in v2.0.0 |
| 47/4d | stays 0 | "your flight" = a reservation the user owns, the reading of 39/4a |
| 29/4b | stays 0 | the stated health problem is a covered reason; the clause was added with the cancel-and-rebook reference |
| 34/4a | stays 0 | "return delay" pins 2024-05-23; package 222 > 200 |
| 38/4e | stays 0 | the purpose's premise is missing from the scenario, but its conclusion agrees with the actions |
| 31/4a, 33/4a | stay 0 | their open readings are the 4c rows of part `order`; not counted twice |
| re-review 33, 35, 39 x (1d, 2g, 4a, 4b, 4d, 4e) | 18 of 18 agree | no disagreement in this family; 39/4b = 1 high in both |
| 1a, 1b, 1c, 2i, 3d, 3f, 5a x 30 | 0 confirmed | basis DB+COMMUNICATE on all 30; 0 replay errors; no no-op WRITE; no comma in any `communicate_info`; no `communicate_info` value in scenario text; stable initial hash; replay reproduces all 30 targets |
| other reviewer zeros of 1d, 2g, 4a, 4b, 4d, 4e | 0 confirmed | sweep below; no further false negative |

## Conventions applied

1. **4d, one reading per phrase (convention 5).** Tasks 2 and 38 share "the delayed flight in your most recent reservation" (`reason_for_call`). Task 2 adds "the last reservation you made"; task 38 adds "the last reservation".
   - Reading applied to both, marked as an assumption in both rows: the reservation with the latest `created_at`, the only booking-time field in `db.json`.
   - Competing readings fail on evidence:
     - (a) List position. The profile list `[SDZQKO, 4OG6T3]` puts 4OG6T3 last, but lists in `db.json` are not chronological: 42 of 426 users with two or more reservations have a list sorted by `created_at`, and 2120 of 4546 listed pairs (0.466) are in `created_at` order, about chance level.
     - (b) Most recent travel. This does not fit "the last reservation you made".
   - Under this reading both tasks point to SDZQKO (created 2024-05-13T03:26:54, flights 2024-05-27..29, all `available`). The only delayed flight, HAT018 2024-05-11, is in 4OG6T3 (created 2024-05-09T15:14:07).
   - Neither mismatch blocks the reference path. The references are READ-only, the target equals the initial DB, and the delayed flight identifies 4OG6T3. So both rows are medium, with no reward effect.
   - The earlier upstream text of task 2 shows the intended referent: its reference was `send_certificate` 50, with the purpose "$50 for a one-passenger delayed basic economy flight with insurance" (= 4OG6T3).
2. **4e (convention 4).** A typo is 0 (35/4e). A contradiction is 1 (27/4e; precedent 23/4e).
3. **One root cause is counted once.** 39/4e stays 0 because its cause is 39/4b. 31/4a and 33/4a stay 0 because their open readings (upgrade-first route; "move back" = 2024-05-21) are the 4c rows of part `order`.
4. **4b high (convention 3).** 39/4b is high because no policy-compliant trajectory reaches the target hash.
5. **Severity follows `checklist.md` (convention 6).** Reward effects are stated in the notes; no likelihood levels are added.
6. **2g needs an observed match** in the 2b probe or the agent-run trajectories (block-1 adjudication of 23/2g). A static candidate is recorded, not counted.
7. **"Your flight(s)" = a reservation the user owns.** This is the reading of 39/4a; it is applied unchanged to 47/4d.

## Recomputations

- **Targets (8-hex), replayed:** 12 `df1e46c5`, 14 `b4ea8eff`, 15 `c9500f31`, 17 `37ea6df3`, 18 `361a0673`, 24 `db03cad5`, 25 `d0579b8a`, 29 `55e7aa07`, 30 `dc171787`, 33 `735ba8f1`, 35 `e0c0bf3e`, 39 `964c9e1c`, 40 `96b61d51`, 42 `768a1bf6`. The 16 empty-answer tasks give `124e39a6` = initial. All match `static_scan.csv`.
- **Task 39:**
  - MSJ4OA: economy; created 2024-05-05T14:36:15, 240h23m before the clock; HAT099 and HAT274 on 2024-05-22 are `available`.
  - Insurance is "yes", but the only reason in the scenario ("give up your seat for someone else who needs it") is neither health nor weather (policy lines 101, 147).
  - The compliant set {8C8K4E, LU15PA} hashes `f63bccc7`.
  - Upgrading MSJ4OA to business raises: business seats are 2 (HAT099) and 1 (HAT274) for 3 passengers.
  - Refunds: 8C8K4E -5680 = (904+1906) x 2 + 30 x 2; LU15PA -2366 = (740+443) x 2; MSJ4OA -984 = (176+122) x 3 + 30 x 3.
- **Task 14:** the cheapest business round trip is 871 per passenger (HAT023 364 + HAT204 248 + HAT100 259; the next is 1042). 871 x 3 = 2613 = 500 + 198 + 129 + 1786. K1NW8N is 22h56m44s old, inside 24 hours.
- **Task 18:** refunds 6594 + 3925 + 5418 + 2452 + 5164 = 23553 = `communicate_info`.
- **4b sweep of every reference WRITE** (tasks 12, 14, 15, 17, 18, 24, 25, 29, 30, 33, 35, 39, 40, 42). Checked: bags against the allowance, payment-method limits, cabin rules, flown segments, refund destinations. Only MSJ4OA fails.
  - 12: upgrade 2 x ((350 - 122) + (499 - 127)) = 1200 > 650; gold economy gives 6 free bags, so 2 bags are free.
  - 15: 207 - 2787 = -2580 to `gift_card_8887175`. 207 is the unique cheapest; ATL->EWR costs 236.
  - 17: (155 + 185) - (71 + 60) = 209; gold economy gives 3 free bags.
  - 24: 51 + 55 = 106 = 39 + 67, the unique cheapest direct round trip (next 111); silver basic economy gives 1 free bag.
  - 25: 175 + 200 = 375 <= 400, so gift card 128 + credit card 247.
  - 29: 171 + 111 = 282; refund -686 = 656 + 30.
  - 30: (146 + 184) x 2 - (161 + 192 + 184) x 2 = -414.
  - 33: 130 + 187 - 503 = -186; business would cost 408 > 200.
  - 35: the second cheapest is 290 (HAT023 at 163 is first).
- **No-write refusals, re-verified in `db.json`:**
  - No cancellation or change condition holds for: 0 EHGLP3; 6 and 45 PEP4E0; 13 XEWRD9 (outbound landed 05-13/14); 24 H9ZU1C; 35 M20IZO; 36 EUJUY6 (outbound landed 05-14); 41 UDMOP1 and 4XGCCM; 43 D1EW9B and 9HBUV8; 47 H8Q05L; 49 3RK2T9.
  - Tasks 2, 5, 27 and 38: no delay certificate is due without a change or cancellation (lines 165, 167).
  - Task 4: the user has no business reservation and no cancelled flight.
  - Task 34: the package costs 282 + 443 - 503 = 222 > 200.
- **2g scan:** '327', '1000', '1786' (task 14) and '23553' (task 18) were searched in `db.json`, `policy.md`, the task's READ outputs and the derived amounts. The only candidate is 1,327 in task 14.
- **Other zeros examined and kept:**
  - 13/4e: the nl reason is incomplete, not contradictory.
  - 14/4e and 24/4e: the description and the reference differ in list order only (an order matter for 2h).
  - 18/4b: no policy rule re-prices bags after a downgrade.
  - 40/4e: loose wording.
  - 41/4e: the "API" claim is inaccurate but does not contradict the actions.
  - 42/4e: a wording slip.
  - 0/4d, 4/4d, 5/4d, 6/4d, 49/4d: deliberate false premises of the scenario.

## Defective rest tasks according to this family's rows

A task counts if it has at least one row with defect = 1 and severity medium or high.

| | before this pass | after this pass |
|---|---|---|
| all rows of this family | 17 tasks: 0 2 4 5 6 13 27 31 34 36 38 39 41 43 45 47 49 | 17 tasks, the same set |
| without the 2a/2b class | 2 tasks: 2 (4d), 39 (4b) | 4 tasks: 2 (4d), 27 (4e), 38 (4d), 39 (4b) |
| defect rows, medium or high | 34 (2a x 16, 2b x 16, 2/4d, 39/4b) | 36 (+ 38/4d, + 27/4e) |

The two escalations add no new task to the count, because 27 and 38 are already in the 2a/2b class. They add two rows to category 4.

## What could not be verified

- The 2g trajectory search. Agent-run data are out of scope in this phase, so 14/2g carries a named candidate (1,327) for that phase.
- The 2b probe itself. The rows rest on the in-process empty-trajectory probe verified in block 1. The probe was not re-run here; the data it depends on were.
- The 2/38 reading is an assumption. Under a list-position or recent-travel reading, both rows would be 0; task 2's "you made" weighs against those readings.
- 39/4b high assumes that the user simulator does not invent a covered reason. The scenario gives only "give up your seat".
- The provenance for 27/4e comes from result files shipped in the clone, not from release notes. The contradiction holds on the current text alone.

## Observations for the other parts (not counted here)

- Task 34's "return delay" pins 2024-05-23 for the same phrase "move back your return ... by one day" that task 33 uses without it. Under the earlier-date reading, the task-34 package would cost 36 and pass the $200 limit. This is input to 33/4c.
- Task 27: nl 2 is a stale assertion from the $150-certificate version. nl 1 (confirm the delay) is a separate item. This is input to 27/2k.
