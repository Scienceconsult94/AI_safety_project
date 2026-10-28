# Skeptic report, part order (checks 2h and 4c): airline rest tasks, static phase

Scope: every 2h and 4c row on the 30 rest tasks (0 2 4 5 6 12 13 14 15 17 18 24 25 27 29 30 31 33 34 35 36 38 39 40 41 42 43 45 47 49) of tau2-bench v2.0.0, commit 989d3285ae669e49503324bdb9981bf14fccedeb, airline domain.

Inputs: `review_batch_5` ... `_10` (csv and md), `rereview_blind_rest.csv`, `static_scan.csv`, `probe_2h.csv`, `checklist.md`, `schema.md`, `airline_full/review_brief.md`, `airline_full/skeptic_brief.md`, the block-1 precedent files, the task cards, `tasks.json`, `db.json`, `policy.md`, `tools.py`, `utils.py`, `toolkit.py`, `evaluator_env.py` and `user/guidelines.py`. No run, trajectory or audit-log file was read.

Outputs: `results/skeptic_verdicts_rest_order.csv` (22 rows), `results/review_overrides_rest_order.csv` (9 rows), this file.

## Method

- Replays in the pinned benchmark (`uv run --no-sync`, frozen lock): environment from `registry.get_env_constructor('airline')`, `set_state` with an empty history, `make_tool_call` with requestor `assistant`, `get_db_hash`. Reference WRITEs come from the registry task loader; every variant is the reference WRITE list with one change.
- Initial hash 124e39a6. Every reference hash matches `static_scan.csv`: 14 b4ea8eff, 17 37ea6df3, 18 361a0673, 24 db03cad5, 25 d0579b8a, 29 55e7aa07, 33 735ba8f1, 39 964c9e1c, 40 96b61d51, 42 768a1bf6.
- Flight pins recomputed with `search_direct_flight` and `search_onestop_flight`; upgrade routes priced by calling `update_reservation_flights` on fresh environments.
- Hash facts: `get_db_hash` = `get_dict_hash(db.model_dump())` (toolkit.py 242-244), a sha256 of `json.dumps(sort_keys=True)` (utils.py 41): dict keys sorted, list order kept. `book_reservation` copies passengers and payment_methods in call order (tools.py 302-303); every update call with a nonzero amount appends one payment_history entry (tools.py 244-249, 654-656, 751-753).
- Scripts in a temporary folder outside the repository (subfolder `skeptic_rest_order`): `replay_order.py`, `search_pins.py`, `upgrade_routes.py`, `extra_candidates.py`. They write no files; no file under tau2-bench is newer than the first script, and `uv.lock` is unchanged.

## Verdict table

| row | outcome | why |
|---|---|---|
| 14/2h (batch 6: 1 medium) | holds | gift-card pair order and passenger order unpinned: 32ba3b46, 5242eeb5, d45bfd89 against b4ea8eff; evidence narrowed |
| 14/4c (batch 6: 1 medium) | fails, set to 0 | double count of 14/2h; all content pinned; extra candidate (free bag allowance) pinned by the scenario and policy 97 |
| 17/2h (batch 6: 1 medium) | holds | bags first under the write-time allowance: nonfree 1, fee 50, edc62003 against 37ea6df3; not repairable later (c0f2ed4b) |
| 17/4c (batch 6: 1 medium) | fails, set to 0 | double count of 17/2h (content that follows from WRITE order) |
| 25/4c (batch 7: 1 medium) | holds (split only) | the 375 split between gift card and card is open: 335696bf, 5daaec64 against d0579b8a |
| 25/2h (no row) | re-filed from 25/4c: 1 medium | list order [card, gift card] 006cace4; independent root cause |
| 29/2h (batch 7: 1 medium) | fails, set to 0 | double count of 29/4c; the variants are content choices |
| 29/4c (batch 7: 1 medium) | holds | payment method and insurance open: 8f0e3aab, 69dbbc31, 967271e2, 287a31d4 against 55e7aa07 |
| 33/2h (batch 8: 0; re-review: 1) | re-review prevails: 1 medium | two-call path, same content, other ledger: e0f444d6, be0bff40 against 735ba8f1 |
| 33/4c (batch 8: 0; re-review: 1) | re-review prevails: 1 medium | direction of 'move back' not fixed; the reference READ uses 2024-05-21, its WRITE 2024-05-23; task 34 pins it, 33 does not; variant efdb8d48 |
| 24/4c (undecided 0) | stays 0 | content pinned; gift-card order belongs to 2h; destination field pinned (extra candidate, e81ead12) |
| 24/2h (no row) | stays 0 | the user dictates the sequence; reversed list 011b88a8 not counted (borderline) |
| 31/4c (undecided 0) | stays 0 | unrequested upgrade route (rule U), net 81 |
| 43/4c, 47/4c (undecided 0) | stay 0 | unrequested upgrade-then-cancel (rule U) |
| 39/2h (undecided 0) | stays 0 | 6 of 6 orders neutral; the failing compliant state traces to 39/4b (part other) |
| 39/4c, 35/4c (0; re-review agrees) | stay 0 | pinned; rule U |
| 0/4c, 41/4c (0) | stay 0 | rule U |
| 15/2h, 40/2h (no rows) | stay 0 | one stated change (15); existing passenger order (40, c5f838b3) |
| 18/2h, 42/2h (0) | confirmed 0 | full order sweeps: 120 of 120 and 2 of 2 neutral |

Counts: 22 rows with written verdicts (7 batch defect rows, 2 re-review disagreements, 5 further undecided zeros, 8 false-negative candidates) plus 2 confirmed zeros. Confirmed 4 (14/2h, 17/2h, 25/4c, 29/4c); rejected 3 (14/4c, 17/4c, 29/2h, all double counts); re-filed 1 (25/2h); escalated 2 (33/2h, 33/4c, re-review over batch); kept at 0: 12.

## Conventions applied

1. Order versus content (block-1 convention 1). List order (payment_methods, passengers) and content that follows only from WRITE order are 2h; open content (payment method, amount split, insurance, which date a phrase means) is 4c.
   - One root cause counted once: 14/4c and 17/4c set to 0 as double counts of 14/2h and 17/2h; 29/2h set to 0 as a double count of 29/4c.
   - Two root causes counted separately: 25 (split under 4c, list order under 2h) and 33 (write path under 2h, date reading under 4c).
2. Block-1 filter: chronological flight-list order is not counted (in 14 a non-chronological flights list hashes 718eed57; not counted).
3. Rules made explicit in this pass and applied to all 30 tasks:
   - S (stated sequence): a sequence the user dictates in words pins the list order (24/2h; the class order in 14/2h). A mention or a remainder statement does not (25/2h, as block-1 20/2h).
   - P (write path): the same content reached through another split of WRITE calls, differing only in the payment ledger, is 2h. It applies where the user states separate changes on one reservation: 33 only (15 states one change; 18 cannot split per segment, policy 118; the other tasks have one call per tool or no write).
   - U (unrequested upgrade): an end state that needs a cabin upgrade the user never asks for, made only to unlock a change or cancellation the policy refuses for the reservation as booked, does not fit the scenario. It adds a write outside the requests of the user (the mirror of 4a); in this benchmark the route is user-initiated (tasks 7, 13 and 32 open it in the instructions of the user, 44 and 45 close it); block-1 19/4c kept it at 0. Rows kept at 0 by U: 0, 31, 35, 39, 41, 43, 47.
   - Bag allowance (17/2h): read at write time, from the cabin the reservation has when the bags are added (policy 91-95 attach the allowance to each passenger by cabin; `update_reservation_baggages` computes none and stores what the agent passes). Stated as an assumption: under a final-cabin reading 17/2h would be 0.
   - Phrase direction (33/4c): when the scenario fixes the size but not the direction of a date move and the reference itself carries both readings, the date is an open content choice; the dominant reading is noted and the severity stays medium. The task-34 wording ('return delay') pins the direction in 34 only; it does not transfer to 33, which lacks those words.
4. Severity: the checklist medium for every 2h and 4c row; likelihood is stated in the notes, not graded.

## Recomputations

- 14: business JFK->SFO 2024-05-26 and SFO->JFK 2024-05-28: HAT023 364 + (HAT204 248 + HAT100 259) = 871 per passenger, next round trip 1042; 871 x 3 = 2613 = certificate 500 + gift cards 198 + 129 + card 1786 (under 2000). Regular member: 2 free business bags per passenger, none booked (the user needs none).
- 17: upgrade (155 + 185) - (71 + 60) = 209 on gift_card_8190333 (280 to 71). Bags first: gold basic economy 2 free, 3 bags give nonfree 1, fee 50 x max(0, 1 - 0) = 50 (280 to 230), then the upgrade (230 to 21).
- 25: HAT097 175 + HAT251 200 = 375, not above 400; gift card 128 + card 247.
- 29: HAT169 171 + HAT033 111 = 282; insurance would add 30 (312). The VA5SGQ refund is 686 = 656 + 30.
- 33: reference (130 + 187) - (177 + 146 + 180) = 317 - 503 = -186 (gift card 152 to 338). Two calls: -193 then +7 (or +7 then -193), same balance 338. Earlier return: (130 + 174) - 503 = -199 (152 to 351); business then (282 + 257) - 304 = 235, above 200. Task 34 under the earlier reading: 282 + 257 - 503 = 36; under the later reading: 282 + 443 - 503 = 222.
- 24: cheapest direct round trip 106 (HAT069 + HAT276, basic economy), next 111; payment 39 + 67.
- 35: JFK->SFO economy on 2024-05-24: 163 (HAT023), 290 (HAT069 + HAT258), 300, 304, 314, 321.
- 15: ATL->PHL economy on 2024-05-24: 207 (HAT110 + HAT172), next 216; ATL->EWR 236 (a destination change is not allowed anyway).
- Order sweeps: 18, all 120 orders of the five downgrades give 361a0673 (closes the probe cap of 24 of 119 orders); 39, 6 of 6 give 964c9e1c; 42, 2 of 2 give 768a1bf6.
- Destination field of round trips: db.json holds 955 round-trip reservations; 921 store the turnaround city; the other 34 store destination = origin and all of them pass through the origin mid-itinerary.

Upgrade routes checked under rule U (end hash after the route alone, from the initial DB 124e39a6):

| task | reservation | upgrade | then | end hash |
|---|---|---|---|---|
| 0 | EHGLP3 | business, 1188 on credit_card_5832574 | cancel | 7ef56d5c |
| 31 | DF89BM | economy, 301 on credit_card_6198952 | HAT033, -220, net 81 | dd2a06d6 |
| 35 | M20IZO | business, 1194 on credit_card_9074831 | cancel | 7788108d |
| 39 | UDMOP1, XAZ3C0 | business, 1023 and 844 on credit_card_4074252 | cancel | 13f84983, 8f50cbdb |
| 39 | MSJ4OA | infeasible: HAT099 lacks business seats for 3 | - | - |
| 41 | UDMOP1 | business, 1023 on credit_card_4074252 | cancel | 13f84983 |
| 43 | D1EW9B, 9HBUV8 | business, 351 and 516 on credit_card_5417084 | cancel | 06dbcff7, 34238053 |
| 47 | H8Q05L | business, 163 on credit_card_4196779 or gift_card_5094406 | cancel | 3e7859cc, 1b167dcd |
| 24, 49 | H9ZU1C, 3RK2T9 | infeasible: not enough business seats | - | - |
| 45 | PEP4E0 | closed by the scenario ('Under NO circumstances will you upgrade your cabin') | - | - |
| 13, 36 | XEWRD9, EUJUY6 | blocked: a segment has been flown (policy 116) | - | - |

## Defective rest tasks on this family (medium rows)

- Before this pass (batches 5-10): 14 (2h, 4c), 17 (2h, 4c), 25 (4c), 29 (2h, 4c): 4 tasks, 7 rows. The blind re-review added 33 (2h, 4c).
- After this pass: 14 (2h), 17 (2h), 25 (2h, 4c), 29 (4c), 33 (2h, 4c): 5 tasks, 7 rows (2h: 14, 17, 25, 33; 4c: 25, 29, 33).
- Order-only on this family: 14 and 17. Content choices: 25, 29 and 33.

## Not verified and open questions

1. Rule U is a reading, not a fact. If the audit instead treats an agent-proposed upgrade as a compliant end state that fits the scenario, 4c flips to 1 on 0, 31 (net-cost reading), 35, 39, 41, 43 and 47; block-1 tasks with the same pattern (for example 46 and 48 for refused cancellations, 19 for upgrade-then-modify) would need the same review. It should be decided once for the whole audit.
2. Block-1 consistency: task 22 is the same reservation (FQ8APE) with the same three changes; its 2h row is 0 although its 4c note records the bags-first fee. Under the reading applied to 17/2h it would be 1 (lower likelihood: its mention order matches the reference). Not changed here, because it lies outside the rest tasks.
3. The write-path mechanism (33/2h) was not examined on block-1 tasks.
4. 24/2h is borderline: kept at 0 under rule S; the opposite reading makes it 1 (011b88a8) and would also admit the purpose-order variant in 14 (b69b0484; 14/2h is 1 either way).
5. 33/4c rests on the reference READ 33_2 and on the task-34 wording; the later reading is dominant (the outbound gloss, nl_assertion 1), so the variant is improbable.
6. Static verdicts only: whether a user simulator accepts the 7 charge (33/2h), another card or insurance (29/4c), a split question (25/4c) or the 50 bag fee (17/2h) was not observed.

## Deviation from the brief

- At the start, one read-only git command (HEAD log and status) was run inside tau2-bench to confirm the pinned commit, although the brief prohibits git. The index file kept its 2026-10-27 timestamp, no lock file remains and no tracked file changed.
