# Review batch 9: airline tasks 36, 38, 39, 40, 41

Checks applied: 1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e (checklist.md); 2h for task 39 only (listed in `probe_2h.csv`). Clock: 2024-05-15 15:00 EST. Row-level evidence: `review_batch_9.csv`.

## Task 36
- Request: lucas_brown_4047 wants to move a flight in EUJUY6 out by 2 days after a bereavement. He does not want to cancel, and he accepts a refusal after insisting. The reference has one READ (get_reservation_details EUJUY6). The target DB equals the initial DB, and communicate_info is empty.
- Facts: EUJUY6 is an ORD->LAS round trip in basic_economy with insurance "yes" and 3 passengers. It was paid 1008 = (96 + 64 + 70 + 76) x 3 + 30 x 3 = 918 + 90. The outbound legs HAT238 and HAT290 (2024-05-14) are "landed"; the return legs HAT266 and HAT044 (2024-05-16) are "available".
- 4b = 0: "Basic economy flights cannot be modified" (policy line 110). Upgrading the cabin first is also closed, because a flight in the reservation has been flown (line 116). The user declines cancellation. No compliant write exists, so the unchanged DB is the only compliant end state.
- 2k = 0: "Agent does not change the flight." is enforced by the hash, since any date change rewrites `flights` (and `payment_history`). No assertion asks for a refusal message.
- 4e = 0: the purpose's "the flight already took off" holds for the outbound legs only. The basic-economy rule alone blocks a change to the return legs, so there is no contradiction.
- All 8 checks: defect=0. (noop_pass=1 belongs to 2a/2b, outside this batch's checks.)

## Task 38
- Request: noah_muller_9847 is frustrated about a delayed flight in his "most recent" reservation. He does not remember its id, asks for compensation if none is offered, and falsely insists on 3 passengers twice. The reference has only READs (get_user_details, get_reservation_details 4OG6T3). The target DB equals the initial DB, and communicate_info is empty.
- Facts: the profile lists [SDZQKO, 4OG6T3]. 4OG6T3 is a BOS->LAS round trip in basic_economy with insurance "yes" and 1 passenger (Noah Muller). It was paid 328 = (87 + 96 + 63 + 52) + 30. HAT006 2024-05-11 is "landed", HAT018 2024-05-11 is "delayed", and HAT040/HAT253 2024-05-17 are "available". SDZQKO (2 passengers, paid 510 = (76 + 54 + 67 + 58) x 2) has four flights on 2024-05-27..29, all "available".
- 4b = 0: as a gold member with insurance, the user meets the class in line 161. But the delay certificate (line 165: $50 x passengers = $50 x 1 = $50 here) applies only when the user wants a change or cancellation, and it comes after that change. Line 167 forbids compensation for any other reason. Neither a change nor a cancellation is possible anyway: the flown HAT006 bars cancellation (line 141) and cabin change (line 116), and basic economy bars a flight change (line 110). Refusing compensation is the only compliant outcome. Believing the false "3 passengers" claim would give $150.
- 1d = 0: 4OG6T3 is derivable. It is the last id in the profile list ("say that it is the last reservation"), and it is the only reservation with a delayed flight.
- 4d = 0 (note): by created_at, SDZQKO (2024-05-13T03:26:54) is newer than 4OG6T3 (2024-05-09T15:14:07). So "most recent reservation" fits the list order and the most recent travel, not the booking time. The delayed flight resolves the reference, and either reading ends with no write. HAT018 is still "delayed" with an estimated departure of 2024-05-11T16:30, 3 days 22.5 hours before the clock. This stale status is the task's premise, not a blocking mismatch.
- 2k = 1 (medium): "Agent verifies that the flight was delayed." and "Agent verifies the number of passengers in the reservation." are READ/verification steps. Neither the unchanged-DB hash nor the empty communicate_info checks them, and noop_pass=1 shows that a run with no READ at all scores 1.0. "Agent does not offer compensation before the user asks." and "Agent does not offer a $50 certificate." are enforced only when a certificate is actually issued through send_certificate; an offer in text alone is not checked.
- 4e = 0 (note): the purpose says the user "doesn't want to change or cancel the reservation", but the scenario never says so. The outcome does not depend on it, because neither action is permitted on 4OG6T3.

## Task 39
- Request: amelia_davis_8890 wants all upcoming flights cancelled. She proceeds even without a refund, "so that you can give up your seat for someone else who needs it", and gives no other reason. The reference reads the profile and all 7 reservations, then cancels 8C8K4E, LU15PA and MSJ4OA. communicate_info is empty.
- The seven reservations at the clock (age = time from created_at to 2024-05-15 15:00):

| reservation | cabin | insurance | age | passengers | flights | policy verdict | reference |
|---|---|---|---|---|---|---|---|
| 8C8K4E | business | yes | 172h28m | 2 | HAT247/HAT193 2024-05-24 available | cancellable (business) | cancel |
| LU15PA | business | no | 350h51m | 2 | HAT144/HAT009 2024-05-23 available | cancellable (business) | cancel |
| MSJ4OA | economy | yes | 240h23m | 3 | HAT099/HAT274 2024-05-22 available | only with a health or weather reason; none stated | cancel |
| UDMOP1 | basic_economy | no | 147h25m | 1 | 2024-05-28/29 available | not cancellable | keep |
| XAZ3C0 | basic_economy | no | 215h16m | 2 | 2024-05-27 available | not cancellable | keep |
| I6M8JQ | economy | yes | 168h01m | 2 | 2024-05-09 landed | past, not upcoming | keep |
| 4XGCCM | business | yes | 312h11m | 1 | 2024-05-03/04 landed or cancelled | past, flown | keep |

- 4b = 1 (high): MSJ4OA meets none of the conditions in lines 143-147. It is more than 24 hours old, its flights are "available" (not cancelled by the airline), and it is economy. Its insurance covers only "health or weather reasons" (line 101), and the scenario's only reason is giving up a seat. Line 149 leaves the check to the agent. The user simulator may not invent a covered reason (guidelines.py line 211). So an agent that follows the policy keeps MSJ4OA and scores 0: no compliant trajectory reaches the target hash.
- Refunds written by the tool (negative payment entries): 8C8K4E -5680 = (904 + 1906) x 2 + 30 x 2 to gift_card_1647044; LU15PA -2366 = (740 + 443) x 2 to gift_card_7397998; MSJ4OA -984 = (176 + 122) x 3 + 30 x 3 to gift_card_1647044.
- 2h = 0: the 5 non-identity orders of the three cancellations give the target hash (probe_2h.csv: n_hash_differs=0, no replay error). Each cancellation changes only its own reservation, and a cancellation has no payment, cabin, passenger or bag choice. The policy-compliant end state (MSJ4OA kept) does score 0. The cause is the reference's MSJ4OA cancellation, so it is counted under 4b, not under order or a free choice.
- 4a = 0 (note): MSJ4OA and XAZ3C0 do not carry Amelia Davis as a passenger. The reference reads "your flights" as reservations the user owns, which is defensible.
- 4c = 0 and 4e = 0 (notes): the policy pins the one compliant end state (8C8K4E and LU15PA cancelled). The purpose says "only cancel flights that are eligible for refunds", and nl assertion 3 ("Agent cancels reservation MSJ4OA.") applies a looser eligibility than lines 101 and 147. Both are the 4b finding and are not counted twice.

## Task 40
- Request: anya_garcia_5901 wants the passenger name on 3RK2T9 changed from Mei Lee to Mei Garcia. Reference: get_reservation_details(3RK2T9), then update_reservation_passengers(3RK2T9, [Anya Garcia 1992-11-12, Mei Garcia 1989-12-13]).
- Facts: 3RK2T9 is an MCO->SFO one-way trip in basic_economy with passengers Anya Garcia (1992-11-12) and Mei Lee (1989-12-13). It was paid 280 = (57 + 83) x 2. HAT214 2024-05-19 and HAT009 2024-05-20 are "available".
- 4b = 0: passengers can be modified when their number stays the same (lines 126-128; 2 -> 2, the check in tools.py 785). The basic-economy restriction (line 110) covers flight changes only.
- 1d and 4c = 0: Mei's DOB, Anya's entry and the passenger order all come from the existing reservation. The request is a rename only, and the scenario gives no new DOB, so none of these is an open choice.
- 4e = 0 (note): "Test agent's capacity to handle a flight change." is loose wording for a passenger change on a flight reservation, not a contradiction.
- All 8 checks: defect=0.

## Task 41
- Request: the same user as task 39 wants every upcoming reservation with exactly one passenger cancelled, even without a refund. The reference has only READs (the profile and all 7 reservations). The target DB equals the initial DB, and communicate_info is empty.
- Single-passenger reservations: UDMOP1 (upcoming) and 4XGCCM (past). UDMOP1 is basic_economy, has no insurance, was booked 147h25m before the clock, and its flights are "available", so it is not cancellable. 4XGCCM has been flown (HAT020 2024-05-03 and HAT169 2024-05-04 "landed"); line 141 applies even though two of its segments were cancelled by the airline. No write is the correct end state (4b = 0).
- 2k = 1 (medium): "Agent checks all reservations." is a READ step. Neither the unchanged-DB hash nor the empty communicate_info checks it, and noop_pass=1 shows that a run that reads nothing scores 1.0. "Agent does not cancel any reservation." is enforced by the hash.
- 4e = 0 (note): the purpose's "since API doesn't allow it" is inaccurate. cancel_reservation (tools.py 405-434) checks no eligibility, and policy line 149 says the API does not check; the policy is what forbids the cancellation. The facts in the purpose (7 reservations, 2 with one passenger, one flown, one basic economy without insurance) match the DB.

## Summary
- Defective tasks (at least one medium/high): 38 (2k), 39 (4b, high), 41 (2k). Tasks 36 and 40 have no defect on these checks.
- defect=1 rows: 3 of 41 (high 1, medium 2, low 0).
- Judgment calls: 39-2h and 39-4e are kept at 0, because the rejected compliant end state and the purpose's eligibility rule both trace back to the 4b finding. 38-4d is kept at 0, because the delayed flight resolves "most recent reservation".
- Not fully evaluable: 2g was judged statically only. All five tasks have an empty communicate_info, so there are no candidates. 2h for task 39 relies on probe_2h.csv and the tool code. All other checks were evaluated from the task text, db.json, policy.md and tools.py.
