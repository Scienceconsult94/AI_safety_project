# Review batch 7: airline tasks 18, 24, 25, 27, 29

Checks applied: 1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e (checklist.md), plus 2h for tasks 18 and 29 (listed in `probe_2h.csv`). Clock: 2024-05-15 15:00 EST. Row-level evidence: `review_batch_7.csv`.

## Task 18
- Request: the user (omar_davis_3817, regular member) wants every business reservation downgraded to economy, with the same flights and passengers. Refunds go to the original payment of each reservation, and the user wants the total saving. Reference: five update_reservation_flights calls (JG7FMM, 2FBBAH, X7BYG1, EQ1G6C, BOH180) to economy with unchanged flights, each refunded to its original payment. LQ940Q is already economy and is left alone. communicate_info = ["23553"].
- Computation: when the cabin changes, the tool reprices every segment at today's economy fare (tools.py 704-748).
  - JG7FMM: (140 + 101 - 1859 - 1679) x 2 = -6594, to credit_card_2929732.
  - 2FBBAH: (107 + 141 + 108 + 109) - (537 + 996 + 1440 + 1417) = -3925, to gift_card_3481935 (balance 22 -> 3947).
  - X7BYG1: (162 + 153 - 1505 - 1519) x 2 = -5418, to credit_card_2929732.
  - EQ1G6C: (172 + 136) - (1820 + 940) = -2452, to gift_card_6847880 (balance 31 -> 2483).
  - BOH180: (117 + 102 - 1981 - 820) x 2 = -5164, to credit_card_9525117.
  - Total saving: 6594 + 3925 + 5418 + 2452 + 5164 = 23553. This equals communicate_info and nl_assertion 6 (4e = 0).
- Policy (4b = 0): all 12 segments are "available" between 2024-05-21 and 2024-05-30. No flight has been flown, so the cabin change is allowed and the lower price is refunded. Observation: JG7FMM keeps 3 checked bags (nonfree 0) for 2 passengers. That is one more than the regular-member economy allowance (1 per passenger), but the policy has no rule that re-prices bags on a downgrade, so it is not counted.
- 2g = 0: "23553" appears nowhere in db.json. It is also absent from every figure an agent would quote: per-reservation refunds, paid totals 7136/4420/6108/2790/5662 and their sum 26116, new gift-card balances, dates, ids and card digits. The greeting has no digit.
- 2h = 0: the probe ran 24 of the 119 non-reference orders (MAX_PERMS = 24), and none changed the hash. The other orders commute too: each call writes only its own reservation, the two refunds to credit_card_2929732 go to different reservations, and the two gift cards are different. No choice is left open, because refund method, cabin and flights are pinned.
- All 9 checks: defect = 0.

## Task 24
- Request, in order:
  - Remove Ethan from H9ZU1C. If that is not possible, cancel H9ZU1C; if that is not possible either, move on.
  - Book the cheapest direct round trip from JFK or EWR to the West Coast, out 2024-05-20 and back 2024-05-25, in basic economy if it is cheaper.
  - Pay first with the smaller gift card, then with the larger one. Use all free bags, buy no insurance, and take the DOB from the profile.
- Reference: one book_reservation (JFK-SEA, HAT069 + HAT276, basic economy, Mia Kim 1965-06-09, gift_card_7359776 39 + gift_card_7773485 67, 1 bag, nonfree 0, insurance no).
- H9ZU1C: the number of passengers cannot change (policy 127). The reservation is not cancellable: created 2024-05-01T04:50:18 (14d10h before the clock), economy, insurance "no", and both flights are "available". Leaving it untouched is correct (4b = 0), and nl_assertion 1 is enforced by the hash (2k = 0).
- Search:
  - Direct flights on 2024-05-20: JFK-SFO HAT023, JFK-SEA HAT069 and HAT083, EWR-LAX HAT041.
  - Direct flights on 2024-05-25: SEA-JFK HAT021, HAT089, HAT100, HAT276 and LAX-EWR HAT012, HAT228. There is no direct SFO-New York flight that day.
  - Cheapest round trip: JFK-SEA HAT069 + HAT276 in basic economy, 51 + 55 = 106. Next come 111 (HAT069 + HAT021) and EWR-LAX at 163; the cheapest economy round trip is 253. The flight choice is unique, and basic economy is the cheaper cabin.
- Payment: 39 (the whole smaller card) + 67 = 106. A silver member in basic economy gets 1 free bag (policy 88), so the booking has 1 bag with nonfree 0.
- 4c = 0, borderline: the only remaining freedom is the order of the two gift cards in payment_methods. The hash keeps list order, so [gift_card_7773485 67, gift_card_7359776 39] fails. The defect rule is not counted as holding, because "first use up your smaller GC and then the larger one" fixes the reference order. However, nl_assertion 3 itself names the larger card first, which suggests the order was not meant to matter.
- All 8 checks: defect = 0.

## Task 25
- Request: book the same itinerary as G72NSF (DTW-SEA one way, HAT097 + HAT251 on 2024-05-17, economy) for Ivan Smith alone, a saved passenger in the profile, with no bags and no insurance. Use the certificate only if the price is above $400; otherwise use the gift card and the credit card. The user also asks how much certificate balance will remain. Reference: book_reservation with gift_card_8516878 128 + credit_card_3563913 247.
- Computation: today's economy fares are 175 + 200 = 375 for one passenger. That is not above 400, so the certificate is not used (with insurance the price would have been 405). The gift card holds exactly 128, and 375 - 128 = 247 goes to the credit card. A gold member gets 3 free bags in economy; 0 are booked.
- 4c = 1 (medium): the scenario fixes the two payment methods and the total. It does not fix how 375 is split or the order in which the two payments are listed. Any gift-card share from 1 to 128, or the order [credit card, gift card], is compliant and fits the scenario. Only the reference split and order reach the target hash. Using up the gift card first is the usual default, so the practical risk is low to moderate.
- Outside these checks (noted under 2k): the certificate-balance question is checked by neither communicate_info nor an nl_assertion. The answer is $500, unchanged; had the certificate been used, its remainder would have been forfeited (policy 79).
- Other checks: defect = 0.

## Task 27
- Request: the user complains that HAT039 (ATL-SEA) is delayed, wants the reason and compensation, and does not want to change or cancel. Reference: get_user_details only. The target DB equals the initial DB and communicate_info is empty, so an empty answer passes (that is 2a/2b).
- Facts:
  - HAT039 on 2024-05-15 is "delayed": estimated departure 2024-05-16 00:50 instead of 22:00, i.e. 2h50m late.
  - It belongs to M61CQM (economy, no insurance, 3 passengers), together with HAT223, which is "flying".
  - The user is silver, and db.json gives no reason for the delay.
- Policy (4a/4b = 0): a delay certificate ($50 x 3 = $150 here) is allowed only after changing or cancelling the reservation (policy 165). No compensation is allowed for any other reason (policy 167). The user refuses both, so making no write is the compliant outcome.
- 2k = 1 (medium): nl_assertions 1 (confirm the delay) and 2 (confirm eligibility through Silver status) require the agent to tell the user something. Neither the hash nor COMMUNICATE checks this, and a run that says nothing scores 1.0. description.notes ("Action to check that flight has been delayed should be added.") admits the gap. nl_assertion 3 (no certificate) is enforced by the hash.
- 4e = 0, with tension: nl_assertion 2 and the purpose ("Assess that agent correctly issues compensation.") lean toward compensation, while the policy, nl_assertion 3 and the reference give none. They agree only if nl_assertion 2 is read as "eligible if the reservation were changed or cancelled". No assertion forbids or requires a write that conflicts with the reference.

## Task 29
- Request: change VA5SGQ (DTW-LGA round trip, economy, insured) to nonstop DTW-JFK flights on the same dates, arriving before 07:00, at the cheapest economy fare, with the return leaving on the 19th and 1 checked bag added. The user mentions a health problem to get fees waived.
- Reference: get_reservation_details(VA5SGQ), cancel_reservation(VA5SGQ), then book_reservation (DTW-JFK round trip, economy, HAT169 2024-05-17 + HAT033 2024-05-19, Raj Brown, credit_card_8003957 282, 1 bag, nonfree 0, insurance no).
- Search:
  - DTW-JFK on 2024-05-17 has three nonstops. Only HAT169 (04:00-06:00, economy 171) arrives before 07:00.
  - JFK-DTW on 2024-05-19 has four nonstops that arrive before 07:00: HAT033 111, HAT092 154, HAT088 185, HAT212 192.
  - Total: 171 + 111 = 282 for one passenger. A regular member gets 1 free economy bag, so the booking has 1 bag with nonfree 0.
- Policy (4b = 0): a modification cannot change the destination (policy 111), so the trip is cancelled and rebooked. The cancellation is allowed: no segment has been flown, insurance is "yes", and health is a covered reason (policy 101, 147). The refund of 686 (fares 656 + insurance 30) goes back to credit_card_8003957.
- 4c = 1 and 2h = 1 (medium, same cause): the scenario says nothing about how to pay for the new booking or whether to insure it. The profile holds three credit cards and a $279 gift card, and the user simulator treats preferences that the scenario does not state as unknown. Paying with another card, or buying insurance (312), is compliant and allowed by the scenario, but it changes payment_history or insurance and scores 0. The probe's only permutation (book before cancel) does not change the hash.
- 2k = 1 (medium): nl_assertion 1 requires telling the user that the reservation cannot be changed. An agent that cancels and rebooks without saying so still reaches the target hash. The refusal itself (no in-place change of VA5SGQ) is enforced.
- 4d = 0: static_scan's ids_missing_in_db (HAT033|HAT169 here, HAT039 in task 27) is a regex artifact. The scan matches 6-character tokens against reservation ids, while these are flights that exist in db.json.

## Summary
- Defective tasks (at least one medium/high): 25 (4c), 27 (2k), 29 (2h, 2k, 4c). Tasks 18 and 24 have no defect on these checks; task 24 carries a borderline 4c note on the order of the gift cards.
- defect=1 rows: 5 of 42, all medium (high 0, medium 5, low 0). Rows per task: 18: 9, 24: 8, 25: 8, 27: 8, 29: 9.
- Not fully evaluable:
  - 2g and 2h were judged statically; no agent trajectory and no rescoring run was in scope.
  - The task 29 2h verdict rests on the hash covering payment_history and insurance (tools.py, utils.py).
  - The task 18 2h verdict extends the 24 probed orders to all 120 by a commutation argument.
- Borderline verdicts written as 0: 24/4c (gift-card list order) and 27/4e (assertion 2 and purpose vs. no compensation).
