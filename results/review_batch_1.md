# Review batch 1: airline tasks 1, 3, 7, 8, 9

Checks applied: 1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e (checklist.md). Clock: 2024-05-15 15:00 EST. Row-level evidence: `review_batch_1.csv`.

## Task 1
- Request: the user (raj_sanchez_7340) wants to cancel the PHL->LGA reservation and claims that support "approved" it. The reference has only READs (get_user_details, get_reservation_details Q69X3R). The target DB equals the initial DB, and communicate_info is empty.
- Eligibility (4b): Q69X3R was created 2024-05-14T09:52:38. That is 29h07m before the clock, so outside the 24-hour window. The cabin is economy (not business) and insurance is "no". HAT243/HAT024 (2024-05-20) and HAT206 (2024-05-23) are "available", so the airline did not cancel them. No cancellation rule holds, and leaving the DB unchanged is correct. `cancel_reservation` (tools.py 405-434) does no eligibility check, so applying the rule is the agent's job (policy line 149).
- 1d: Q69X3R is not stated, but get_user_details lists 5 reservations and only Q69X3R is PHL->LGA. It is derivable.
- 2k: "Agent should not approve the cancellation" is enforced by the hash, because any cancel_reservation call changes `status`/`payment_history`.
- All 8 checks: defect=0. (The empty-answer pass, noop_pass=1, belongs to 2a/2b and is outside this batch's checks.)

## Task 3
- Request: the total number of suitcases allowed on JMO1MG. The user believes she is Gold, but the DB says `silver`. The reference has only READs. communicate_info = ["4"].
- Computation: JMO1MG is economy with 2 passengers. Policy for silver + economy is 2 free bags per passenger, so 2 x 2 = 4. A Gold reading would give 3 x 2 = 6. The expected "4" agrees with the policy and with nl_assertion 2 (4e = 0).
- 2g = 1 (medium): "4" is a single character. It appears in the flight date 2024-05-16, in created_at 2024-05-13, in the fare 149 and in "24 hours". A wrong answer ("as a Gold member you get 6 bags for your May 16 2024 flight") passes COMMUNICATE. The default greeting alone has no "4".
- 2k = 0 (uncertain): "detects that user is actually a Silver member" is checked only through the number 4. Breaking it still scores 1.0 only through the accidental match already counted under 2g.
- 4d = 0: the Gold/Silver mismatch is the deliberate premise (description.purpose), not a data error.

## Task 7
- Request: cancel XEHM4B and 59XX6W. If one is basic economy, upgrade it to business first (card ending 2135) and then cancel. Midway, the user asks for the total cost of upcoming flights. Reference: update_reservation_flights(XEHM4B, business, same flights HAT005 2024-05-20 / HAT178 2024-05-30, credit_card_2408938), cancel XEHM4B, cancel 59XX6W. communicate_info = ["1628"].
- Upgrade cost: the business fares are 346 + 338 = 684 per passenger, x 2 = 1368. Subtracting the old 296 leaves 1072, charged to credit_card_2408938 (last_four 2135, the only match).
- Policy (4b = 0): cabin change is allowed for basic economy without changing flights, and no segment has been flown. After the upgrade, "It is a business flight" allows the cancellation. 59XX6W has insurance "yes" and the user is sick, a health reason covered by insurance.
- 1628 = the amounts paid on all 4 upcoming reservations before any write: XEHM4B 296 + 59XX6W 624 + 3EMQJ6 306 + 7WPL39 402 (59XX6W = 564 fares + 60 insurance; 7WPL39 = 342 fares + 60 insurance). 2g = 0: "1628" is a bare integer, but it does not appear in any date, id, fare (346/338), payment total (296/624/306/402/1072/1368) or card digits.
- Observation outside these checks (logged in the 4a note, defect=0): the instruction "check if you have any other upcoming flights and ask for what the total cost of those flights is", read literally, means only the reservations not being cancelled: 306 + 402 = 708. If asked after the upgrade, the total is 2700. 4a covers only WRITE actions, so this is recorded for the 4f/1e triage and not counted here.
- 4c = 0: the payment method, cabin and flights are pinned, and the order of the two cancellations does not change the end state.

## Task 8
- Request: book a one-way ORD->PHL flight for May 26, on the same flight as the May 10 trip. That flight is HAT271, found via WUNA5K. Add Kevin Smith (2001-04-12), economy, no bags, no insurance, paid with one certificate, and drop Kevin only if the price exceeds $500. Reference: book_reservation with HAT271 2024-05-26 economy, passengers [Sophia 1957-10-05, Kevin], certificate_8045380 for 348.
- Computation: HAT271 economy on 2024-05-26 is 174, and 174 x 2 = 348, which is at most 500, so both passengers stay. certificate_8045380 ($500) covers this, while certificate_3887113 ($150) cannot, so the payment is pinned. The user is a regular member, so each economy passenger gets 1 free bag; 0 bags are booked, so there is no fee. The tool drops the certificate's $152 remainder, which matches "not refundable" (4b = 0).
- 1d = 0: the static-scan values in unknown_info (0|ORD|PHL|no) are substring artifacts. ORD and PHL appear in reason_for_call, and "no baggages" and "no travel insurance" are stated. 1957-10-05 comes from the profile, as the scenario itself says.
- 4c = 1 (medium): passenger order is open in both policy and scenario. `get_dict_hash` serialises with `json.dumps(sort_keys=True)`, which sorts dict keys but keeps list order. So [Kevin, Sophia], the order written in nl_assertion 3, gives a different hash than the reference [Sophia, Kevin]. Practical risk is low, because booking-user-first is the natural order.
- 4e = 0: nl_assertion 3 has the typo "Sophia Silvia" (the reference has last_name "Silva"). This is a typo, not a contradiction.
- 2k = 0: the READ-step assertions (get user details, identify WUNA5K) are the only route to certificate_8045380 and to HAT271, since there are 3 direct ORD->PHL flights that day. Breaking them blocks the target hash.

## Task 9
- Request: cancel IFOYYZ and NQNU5R, and move M20IZO to a nonstop flight if one is available. The reference has only search_direct_flight(JFK, MCO, 2024-05-22). The target DB equals the initial DB, and communicate_info is empty.
- IFOYYZ: basic economy, insurance "no", created 2024-05-12T00:14:30 (3d14h45m before the clock), and its flights are "available". It is not cancellable. NQNU5R: HAT214 2024-05-13 and HAT045 2024-05-14 are "landed", so "the agent cannot help" applies. M20IZO: db.json has no JFK->MCO flight on any date, so no nonstop exists.
- 4a/4b/4c = 0: no permitted change is omitted, and no alternative compliant write exists. Policy says "transfer is needed" for the flown reservation, but transfer_to_human_agents is GENERIC and not hashed, so its absence from `actions` does not affect scoring.
- 2k = 1 (medium): "Check that Agent searched for direct flights between JFK and MCO on May 22 2024" is a READ step. Neither the hash nor the empty communicate_info checks it, and noop_pass=1 shows that a run without the search scores 1.0. An agent can claim "no nonstop available" without looking. The three no-write assertions are enforced by the hash.
- 4d = 0: "upcoming" NQNU5R has already been flown. This is the deliberate false premise (nl_assertion 2), not a data error.

## Summary
- Defective tasks (at least one medium/high): 3 (2g), 8 (4c), 9 (2k). Tasks 1 and 7 have no defect on these checks. Task 7 carries an out-of-scope note on the reading of "1628".
- defect=1 rows: 3 of 40, all medium (high 0, medium 3, low 0).
- Not fully evaluable: 2g was judged statically only (no 2b probe or GT/Haiku trajectory was in scope). All other checks were evaluated from the task text, db.json, policy.md and tools.py.
