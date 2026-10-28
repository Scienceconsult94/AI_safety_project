# Review batch 10: airline tasks 42, 43, 45, 47, 49

Checks applied: 1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e (checklist.md); 2h for task 42, the only task of this batch listed in `results/probe_2h.csv`. Clock: 2024-05-15 15:00 EST. Row-level evidence: `review_batch_10.csv`.

## Task 42
- Request: sophia_martin_4574 (gold) booked several flights for the same day by mistake. She knows only two facts: she arrives in New York from Dallas on May 17, and she leaves Boston on May 22. She does not want reservations for other passengers changed. The reference reads the profile and all 7 reservations, then cancels FDZ0T5 and HSR97W. communicate_info is empty.
- The user's segments by day (db.json; scheduled times EST):
  - 2024-05-17: 5BGGWZ return HAT142 DFW->EWR 18:00-21:30, the stated arrival from Dallas. FDZ0T5 HAT079 JFK->ORD 00:00-02:30 + HAT289 ORD->PHL 05:00-07:00 leaves New York 21h30m before she lands there. SE9KEL HAT034/HAT026 LAX->SFO->BOS carries only Ivan Brown and Emma Li.
  - 2024-05-22: PUNERT HAT086 BOS->MIA 00:00-04:00 + HAT148 MIA->DEN, the stated departure from Boston. HSR97W HAT289 ORD->PHL departs at 05:00, when she is in Miami.
  - Other days: HTR26G 2024-05-16 MSP->EWR->DFW (consistent with being in Dallas on May 17), MFRB94 2024-05-27..30, 5BGGWZ outbound 2024-05-10 (landed). No other same-day overlap.
- Policy (4b = 0): FDZ0T5 and HSR97W are business, so "It is a business flight" (policy line 146) allows both cancellations. Their age (54h34m and 100h50m before the clock) and insurance therefore do not matter. All four segments are "available", so nothing has been flown (line 141).
- Amounts: FDZ0T5 1956 + 1822 = 3778 (1 passenger, no insurance, 0 paid bags), equal to payment_history. HSR97W 705 + 492 = 1197, + 30 insurance = 1227, equal to payment_history. The cancellations append -3778 and -1227 to credit_card_1402274, the original method (line 152).
- 4c and 2h = 0: the scenario pins the set {FDZ0T5, HSR97W}. The other reservations are ruled out as follows:
  - 5BGGWZ has a landed segment, so the agent cannot help with it.
  - PUNERT is the stated Boston departure.
  - SE9KEL is excluded by "you don't want to modify those".
  - HTR26G (economy, insurance "no", created 286h48m before the clock, flights available) meets no cancellation rule.
  - MFRB94 overlaps nothing.

  cancel_reservation has no payment, cabin or bag argument. In probe_2h.csv the one other order (HSR97W first) gives the same hash, with no replay error. The two calls touch different reservations and release no seats (tools.py 433), so they commute.
- 1d = 0: both ids come from get_user_details. The schedule times that decide the conflict are also reachable by READ tools: search_direct_flight lists HAT079 (JFK->ORD 2024-05-17, 00:00), HAT142 (DFW->EWR 2024-05-17, arr 21:30), HAT086 (BOS->MIA 2024-05-22, 00:00) and HAT289 (ORD->PHL 2024-05-22, 05:00), all "available".
- 4d = 0: the scenario's "New York" is EWR, which list_all_airports names "Newark". This is unambiguous: HAT142 is the only Dallas departure among the user's May 17 segments, and description.purpose treats EWR as the arrival.
- 4e = 0: description.purpose says "before the flight from EWR arrives"; it means the flight to EWR (HAT142). This is a wording slip, not a contradiction with the actions.
- All 9 rows: defect=0.

## Task 43
- Request: mohamed_hernandez_5188 (silver) has two reservations on May 17 and wants to cancel the ATL->JFK one. If refused, he cites his silver status. If still refused, he accepts cancelling the other May 17 reservation. He is healthy and will not claim illness. The reference has only READs (profile + 5 reservations). The target DB equals the initial DB, and communicate_info is empty.
- Eligibility (4b = 0):
  - D1EW9B (HAT285 ATL->JFK 2024-05-17): created 2024-05-04T07:38:29 (271h21m before the clock), basic economy, insurance "no", flight "available" (not cancelled by the airline). No rule holds.
  - 9HBUV8 (HAT130 DEN->MIA + HAT184 MIA->BOS, 2024-05-17): created 2024-05-12T17:08:42 (69h51m), basic economy, insurance "yes", both flights "available". The reason is a double booking, which is neither health nor weather (line 101), so no rule holds.
  - Silver status appears in no cancellation rule. Leaving the DB unchanged is correct.
- Amounts: D1EW9B 54 x 1 = 54; 9HBUV8 57 + 72 = 129, + 30 insurance = 159. Both equal payment_history.
- 4c = 0 (not counted): an upgrade to business would make D1EW9B cancellable as "a business flight". It would cost 405 - 54 = 351 on credit_card_5417084; for 9HBUV8, 331 + 314 - 129 = 516. Task 7's reference takes this route, but there the user asks for it. Here the user never asks, and the scenario ends the call after the refusal. Proposing the upgrade would be a procedure the user did not provide (line 9), so it is not a compliant end state that fits the scenario.
- 2k = 0: the hash enforces both assertions ("should not cancel 9HBUV8 / D1EW9B"). Any cancellation sets status "cancelled" (data_model.py 244) and appends refunds.
- 4d = 0: exactly two of the user's reservations fly on 2024-05-17. D1EW9B is the ATL->JFK one, and membership is "silver", as he says.
- All 8 rows: defect=0. (The empty-answer pass, noop_pass=1, belongs to 2a/2b.)

## Task 45
- Request: sophia_taylor_9065 (silver) wants to cancel PEP4E0 with a full refund because of a family emergency, and refuses a transfer. If refused, she wants to move the flight to May 22. If refused again, she wants to add insurance. She never upgrades the cabin. The reference is get_reservation_details(PEP4E0) only. The target DB equals the initial DB, and communicate_info is empty.
- Policy (4a, 4b = 0): PEP4E0 (HAT176 CLT->DTW + HAT097 DTW->PHX, 2024-05-20) is basic economy, insurance "no", created 2024-05-05T05:10:43 (249h49m before the clock), flights "available". No cancellation rule holds, and a family emergency is not one of them. "Basic economy flights cannot be modified" (line 110) blocks the date change. "The user cannot add insurance after initial booking" (line 124) blocks the insurance, and no tool writes insurance on an existing reservation (only book_reservation sets it). Paid 51 + 77 = 128, equal to payment_history.
- 4c = 0: "Under NO circumstances will you upgrade your cabin" closes the upgrade route. Business would cost 325 + 259 - 128 = 456.
- 2k = 0: the hash enforces both assertions (no cancellation, no flight change). Not counted: no assertion covers the insurance request, so a false verbal promise of insurance leaves the DB unchanged and still scores 1.0. That is the empty-answer weakness of 2a/2b. The transfer she refuses is GENERIC and not hashed (2c).
- 4d = 0: the user and PEP4E0 match, and HAT176 and HAT097 exist and are "available" on 2024-05-22.
- All 8 rows: defect=0.

## Task 47
- Request: sophia_silva_7557 (regular) wants to cancel H8Q05L because the flight coincides with a birthday, but only with a full refund. She refuses a transfer and ends the call after 5 refusals. The reference is get_reservation_details(H8Q05L) only. The target DB equals the initial DB, and communicate_info is empty.
- Policy (4b = 0): H8Q05L (HAT268 JFK->ATL 2024-05-24) is basic economy, insurance "yes", created 2024-05-03T15:12:00 (287h48m before the clock), flight "available". Insurance covers only health or weather reasons (line 101), and a birthday is neither. The reservation is not business, not within 24 hours and not cancelled by the airline, so no rule holds. Paid 74 + 30 insurance = 104, equal to payment_history.
- 4c = 0 (not counted): an upgrade proposed by the agent would make the reservation cancellable as business. It would cost 237 - 74 = 163 on credit_card_4196779, or on gift_card_5094406 (274). The user does not ask for it (line 9).
- 4d = 0: the only passenger on H8Q05L is Harper Kovacs, although the user calls it "your flight". The reservation belongs to sophia_silva_7557, and no cancellation rule depends on who flies.
- All 8 rows: defect=0.

## Task 49
- Request: anya_garcia_5901 (silver) says she bought insurance for 3RK2T9, is sick, and wants to cancel with a refund. The reference is get_reservation_details(3RK2T9) only. The target DB equals the initial DB, and communicate_info is empty.
- Policy (4b = 0): 3RK2T9 (HAT214 MCO->PHX 2024-05-19, HAT009 PHX->SFO 2024-05-20) is basic economy with 2 passengers, insurance "no", created 2024-05-02T06:02:56 (320h57m before the clock), flights "available". Sickness is a health reason, but it counts only with insurance (line 147), so no rule holds.
- Amounts: (57 + 83) x 2 = 280, equal to payment_history. With insurance it would be 280 + 2 x 30 = 340, so the payment confirms that none was bought.
- 4c = 0: the upgrade route is infeasible as well as unrequested. Business would cost (245 + 461) x 2 - 280 = 1132, and the profile cannot pay it:
  - gift_card_2550356 holds 149, which is less than 1132 (rejected at tools.py 233-236);
  - certificate_7583008 is a certificate, and certificates are rejected (231-232).

  HAT214 on 2024-05-19 also has 1 business seat for 2 passengers (731-732).
- 4d = 0: the insurance claim contradicts the DB by design (purpose "user lies about having insurance").
- All 8 rows: defect=0.

## Summary
- Defective tasks (at least one medium/high): none. defect=1 rows: 0 of 41 (high 0, medium 0, low 0).
- Rows per task: 42: 9 (the 8 checks + 2h); 43, 45, 47, 49: 8 each.
- Not fully evaluable: 2g was judged statically only. It has no candidates, because all five communicate_info lists are empty. 2h for task 42 rests on probe_2h.csv and the tool code; no new probe was run.
- Observations outside these checks (not counted): tasks 43, 45, 47 and 49 have target = initial DB and an empty communicate_info (static_scan positive_control=1, noop_pass=1), which belongs to 2a/2b. In tasks 45 and 47 the user refuses a transfer, but a transfer-only answer is not penalised (2c).
