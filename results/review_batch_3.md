# Review batch 3: airline tasks 21, 22, 23, 26, 28 (checks 1d, 2g, 2k, 4a–4e)

Sources: task cards, `policy.md`, `tools.py`, and `db.json` at tag v2.0.0. The flight search was replayed read-only, using the same filters as `search_direct_flight` and `search_onestop_flight`. `static_scan.csv` has no columns `ref_args_unstated`, `ref_args_in_unknown_info`, `ids_missing_in_db`, `ci_min_chars` or `ci_in_user_scenario`. Those inputs were therefore taken by hand from the cards and `db.json`.

## Task 21: change the return of OBUT9V to the fastest same-day economy return, add 1 bag, pay with the smallest gift card
- The request: OBUT9V flies IAH to DEN, round trip, in economy. The user is a silver member. The outbound legs on 2024-05-27 are HAT078 (01:00–03:30) and HAT118 (04:00–06:00), arriving in DEN at 06:00. The new return must leave DEN after 06:00 on 05-27.
- Return options from DEN to IAH on 05-27, by total time:
  - HAT229 + HAT266: 11:00 to 16:00, 5 h. HAT229 has 0 economy seats.
  - HAT290 + HAT175: 14:00 to 20:00, 6 h. This is the reference choice and the only option at 6 h.
  - HAT229 + HAT175: 9 h.
  - The options that use HAT084 leave at 04:00, before the outbound arrives.
- The fare difference is computed by `update_reservation_flights`. The outbound legs are kept at their old prices because the cabin does not change. The new return costs (142 + 170) and the old return cost (122 + 131), so the difference is 312 − 253 = **59**.
- Payment:
  - The gift card with the smallest balance is gift_card_7480005 at 6.0. It cannot pay, because 6 < 59 and the tool raises "Gift card balance is not enough".
  - The reference uses the next smallest card, gift_card_6276644 at 113.0.
  - 4a is therefore 0 with an "uncertain:" note. The literal value cannot work, and the chosen card matches the stated purpose, "reason about payment amounts".
- Bags: the reservation has 1 bag and the user adds 1, for a total of 2. A silver economy passenger gets 2 free bags, so nonfree = 0 and the fee is 0. Because the fee is 0, the payment_id given for the bag change does not affect the hash.
- 1d: OBUT9V appears only in unknown_info. It can be found through `get_user_details`, as policy line 107 directs.
- 4b, 4c, 4d, 4e and 2k: each is 0. All 3 nl_assertions describe writes, so the DB hash enforces them.

## Task 22: FQ8APE: change the passenger to the user, upgrade from basic economy to economy, set 3 bags, pay by gift card
- The reference makes 3 writes on FQ8APE:
  - a cabin change to economy on the same flights, HAT056 and HAT138 on 2024-05-25;
  - a passenger change to Omar Rossi, born 1970-06-06, as in the profile;
  - a bag change to total 3, nonfree 0.
- Cabin change cost: economy fares (155 + 185) minus basic economy fares (71 + 60) gives 340 − 131 = **209**. Every fare is repriced because the cabin changes.
  - gift_card_8190333 (280.0) can pay this. gift_card_6490722 (127.0) cannot.
  - So "prefer gift card" leads to exactly one card, and 4c is 0.
- Policy line 117 allows a cabin change on a basic economy reservation. The passenger count stays at 1. A gold economy passenger gets 3 free bags, so nonfree = 0. 4b is 0.
- 4c note (uncertain): suppose the bags are added before the upgrade, while the cabin is still basic economy. Gold basic economy gives 2 free bags, so the result is nonfree = 1 and a 50 charge. That end state has a different hash. The scenario does not fix the order of the steps. This is the subject of 2h.
- 4d note (uncertain): the user says "New York to Chicago". The reservation is EWR to ORD, and `list_all_airports` calls EWR "Newark". FQ8APE is still the user's only matching reservation, so the path is not blocked.
- 1d, 2g (communicate_info is empty), 2k (all 3 nl_assertions describe writes), 4a and 4e: each is 0.

## Task 23: give the gift card and certificate totals; cancel K1NW8N; book 3 business round trips, JFK–SFO, 05-26 / 05-28
- Totals the user asks for:
  - gift cards: 198 + 129 = **327**;
  - certificates: 500 + 250 + 250 = **1000**.
- Cheapest business fares on the same dates:
  - outbound: HAT023 at 364. The one-stop options cost at least 771.
  - return: HAT204 + HAT100 at 248 + 259 = 507. The next cheapest is HAT204 + HAT276 at 678. The current return, HAT204 + HAT021, costs 701.
  - total per passenger: 871, a unique minimum. The business seats are enough for 3 bookings of 1 passenger each.
- Mastercard charge: 3 × 871 = 2613, and 2613 − 1000 − 327 = **1286**. This matches the reference payments of 44 + 621 + 621.
- The new return is a different flight. Basic economy flights cannot be modified, so the reference cancels and rebooks.
  - K1NW8N was created at 2024-05-14T16:03:16, which is 22 h 57 min before the clock time. It is therefore inside the 24-hour window.
  - `cancel_reservation` checks no eligibility rule, so the agent must check it. The reference is compliant. Each booking uses 1 certificate, 1 credit card and at most 2 gift cards.
- **4e = 1 (medium).** nl_assertion 4 says "outbound flights HAT023 and HAT204 on 2024-05-26". The reference books HAT204 on 2024-05-28, as the SFO–SEA return leg. Assertion 5 also contains a stray double quote, which is a typo.
- **4c = 1 (medium).** Two choices are left open, and both change the hash.
  - Booking order: `_get_new_reservation_id` hands out HATHAT, HATHAU and HATHAV in the order the calls are made.
  - Order of the payment list: the tool stores `payment_history=deepcopy(payment_methods)`, and `get_dict_hash` (`json.dumps(sort_keys=True)`) keeps list order.
  - Neither the scenario nor the policy fixes either order. Booking the Raj reservation first is compliant, but it gives a different hash and reward 0.
  - The flights, the certificate split, the bags and the insurance are all fixed by the task. A 2h probe should confirm the effect.
- 2g = 0, with candidates listed:
  - "327" is 3 characters, and "1000" and "1286" are bare integers.
  - "327" also occurs inside "1327", which is certificates plus gift cards.
  - No flight number, and no fare on the itineraries searched, contains any of the three strings.
  - A match by accident is possible but not clearly likely in an ordinary wrong answer.
- 2k = 0: nl_assertions 1, 2 and 8 match communicate_info, and nl_assertions 3–7 are writes. 1d, 4a, 4b and 4d are each 0.

## Task 26: cancel MCO–CLT with a refund. The reference makes no write.
- The reservation is 3FRNFB:
  - cabin basic_economy;
  - created 2024-05-06T13:25:06, more than 24 h before the clock time;
  - insurance "no";
  - HAT028 and HAT277 on 2024-05-28 both have status "available", so the airline has not cancelled them.
- None of the 4 cancellation conditions in policy lines 143–147 holds. Refusing is correct, and leaving the DB unchanged is the only compliant end state. 4a, 4b and 4c are each 0.
- 2k: a refund requires a write, either `cancel_reservation` or `send_certificate`, and any write changes the target hash. The nl_assertion is therefore enforced, in line with the convention in the brief.
  - A verbal offer with no write would not be caught.
  - The stated reason is not checked either.
- 1d is n/a, because there are no actions. 2g is n/a, because communicate_info is empty. 4d and 4e are each 0.
- Note: noop_pass = 1. An empty answer passes, which belongs to 2a/2b and is outside this batch.

## Task 28: cancel SI5UKW with a refund, from a persistent user. The reference makes no write.
- The reservation is SI5UKW:
  - cabin basic_economy;
  - created 2024-05-11T00:08:57, more than 24 h before the clock time;
  - insurance "no";
  - HAT062 on 05-16 and HAT284 on 05-17 are "available".
- Cancellation is not allowed. The user is a regular member with no insurance flying basic economy, so policy line 157 also forbids compensation. A gift card, a voucher or a partial refund would each need a write, and that write would break the hash.
- 4a, 4b and 4c are each 0. 2k is 0, because both nl_assertions are enforced by the unchanged hash. A verbal offer with no write would not be caught.
- 1d and 2g are n/a. 4d is 0: SI5UKW belongs to amelia_rossi_1297, and its cabin matches "basic economy ticket". 4e is 0.
- Note: noop_pass = 1. This belongs to 2a/2b and is outside this batch.

## Summary
- Defective tasks (at least one medium or high defect): **23** (4c medium, 4e medium). Tasks 21, 22, 26 and 28 have no defect=1 row. Their uncertain notes are 21-4a, 22-4c and 22-4d.
- Rows with defect=1: **2** of 40, both medium, with none high and none low.
- Every check could be evaluated statically. 2g was checked against the task text and the DB only, because the 2b probe and the GT and Haiku trajectories were not part of this batch. The static_scan input columns named in the brief are missing from `static_scan.csv`, so they were derived by hand.
