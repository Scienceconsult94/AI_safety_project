# Review batch 2: airline tasks 10, 11, 16, 19, 20 (checks 1d, 2g, 2k, 4a-4e)

Sources: task cards, `policy.md` (clock 2024-05-15 15:00 EST), `tools.py` (book_reservation, update_reservation_flights, cancel_reservation, _payment_for_update), `db.json`, `static_scan.csv`. Prices below are the `db.json` per-date prices that the search tools return. "Price per passenger" = sum of the segment prices.

## Task 10 (liam_khan_2521, reservation 4NQLHD, 3 passengers, economy, round trip)
- Ask: move the IAH-SEA outbound from May 23 to May 24 and upgrade it to business. Upgrading both directions is accepted only after a refusal, and only "if the total extra cost is less than $1000". Reference: `actions=[]`, `communicate_info=[]` (noop_pass=1).
- Paid now: (126+139+148+114)=527 per passenger x 3 = 1581. The tool re-prices every segment when the cabin changes.
- Date change + business on all 4 segments: outbound May 24 HAT190 464 + HAT047 202 = 666; return HAT021 290 + HAT279 241 = 531; (666+531) x 3 = 3591; extra = 3591-1581 = **2010** > 1000. Cabin only, no date change: (249+333+531) x 3 - 1581 = 1758 > 1000. So the user declines, and the unchanged DB is the only end state that fits (4a, 4c = 0).
- **2k = 1 (medium):** the assertion "Agent does not offer to change cabin for only some of the flights" is checked by neither the DB hash nor communicate_info. A violating offer (business on the IAH-SEA segments only, May 24) costs (666-265) x 3 = **1203** >= 1000, so the user declines, no write happens, and the reward is 1.0. Only an executed violation would be caught.
- 1d: no reference arguments. 2g: no strings. 4b: no write. 4d: user, reservation and flights match. 4e: purpose and assertion agree with the empty reference.

## Task 11 (james_patel_9828, GV1N64, 3 passengers, business, round trip LAS-DEN)
- Ask: remove passenger Sophia. This is not permitted ("cannot modify the number of passengers"). Then "if and only if" told so, downgrade all passengers to basic economy, with the refund to the original payment method. Reference: `update_reservation_flights(GV1N64, basic_economy, HAT003 2024-05-19 + HAT290 2024-05-20, gift_card_1642017)`.
- Refund: paid (561+1339) x 3 = 5700; new basic economy price (53+99) x 3 = 456; difference 456-5700 = -5244. That is a refund of 5244 to the gift card (balance 128 -> 5372), which matches `communicate_info ["5244"]`.
- 1d: the reservation id is stated in task_instructions. The flights come from get_reservation_details. The gift card is the only payment method in the profile and the original one. 4b: a cabin change is allowed for any reservation, nothing has been flown, and the refund goes to a single gift card. Basic economy seats 15/18 >= 3. 3 bags stay within the gold basic-economy allowance (2 per passenger = 6).
- 2g: candidate `5244` (bare integer, 4 characters). It occurs 0 times in `db.json` and is not part of any date, id, flight number or other amount in this scenario (5700, 456, 5372, 128), so an accidental match is not plausible (0).
- 2k: all three assertions are enforced (no passenger removal and the downgrade by the hash; the refund by the hash plus "5244"). 4a, 4c, 4d, 4e: consistent, and every choice is pinned.

## Task 16 (aarav_garcia_1177, M05KNL, 1 passenger, business, one way ATL-PHL on 2024-05-23)
- Ask: the cheapest Economy (not Basic Economy) flight on the day after the original date, with the refund to the original payment method. Reference: `update_reservation_flights(M05KNL, economy, HAT110 + HAT172 on 2024-05-24, gift_card_8887175)`.
- 2024-05-24 ATL-PHL: there is no direct flight. The cheapest economy one-stop is HAT110 105 + HAT172 102 = **207**, which is unique; the next is HAT227+HAT139 = 216. Seats 9/2 >= 1. Refund 207-2787 = -2580 to the original gift card.
- 1d: every value is READ-derivable, and the scenario pins the searched choice. 4b: the business reservation may be modified, and origin, destination and trip type are kept. The tool rejects certificates for updates. 4c: flights, cabin, date and payment are all pinned. 2k: both assertions are enforced by the hash. 2g: no strings. 4a, 4d, 4e: consistent.

## Task 19 (olivia_gonzalez_2305, Z7GOZK, basic economy, round trip EWR-IAH on 2024-05-28)
- Ask: a later return flight to EWR the same day, or else the earliest flight the next day. "If basic economy cannot be modified", the user will cancel using the travel insurance because they feel unwell. Reference: `cancel_reservation(Z7GOZK)`.
- 4b: the booking was created 2024-05-13T19:41:32, which is 43 h before the clock, so the 24-hour rule does not apply. The reservation is not business and was not cancelled by the airline. Insurance is "yes" and the reason is health-related, which policy covers ("health or weather reasons"). Nothing has been flown. `cancel_reservation` checks no eligibility rule itself (policy line 149), so the reference is compliant (0).
- 1d: the reservation id is not stated, but it is derivable from get_user_details plus the reservation details (return HAT207 at 15:00 on the 28th). 2k: the single assertion is enforced by the hash. 2g: no strings.
- 4c = 0, uncertain: a second end state exists only if policy is read as allowing a cabin change on basic economy, followed by a flight change to HAT149 on 2024-05-29. The user text covers only the "cannot be modified" branch. There is no later IAH-EWR flight on 2024-05-28 after the 15:00 departure.
- 4d = 0, uncertain: known_info says "You currently reside in Newark", but the profile address is Los Angeles, CA. This is not an id, name, date or amount, and it does not affect the reference path. Everything else matches.

## Task 20 (mia_li_3668, gold, new one-way booking New York-Seattle on 2024-05-20)
- Reference: `book_reservation(JFK-SEA, one_way, economy, HAT136+HAT039 2024-05-20, Mia Li 1990-04-05, certificate_7504069 250 + credit_card_4421486 5, bags 3/0, insurance no)`.
- Flight choice: JFK direct flights (HAT069 06:00, HAT083 01:00) leave before 11:00 and are excluded. JFK one-stops at or after 11:00: HAT136+HAT039 = 152+103 = **255** and HAT218+HAT039 = 261. LGA options at or after 11:00 cost >= 287. EWR HAT213 (+HAT067/HAT234) is also 255, but HAT213 has 0 economy seats, so it cannot be booked. The choice is therefore unique (4a, 1d = 0).
- 4b: gold + economy gives 3 free bags per passenger, so nonfree = 0. Policy allows at most one certificate, so the larger one (250) is used plus the 7447 card for 5. 250 + 5 = 255, and no insurance. Compliant.
- **4c = 1 (medium):** `book_reservation` stores `payment_history = deepcopy(payment_methods)` in call order. `get_dict_hash` runs `json.dumps(sort_keys=True)`, which sorts dict keys but keeps list order. Listing `[credit_card_4421486: 5, certificate_7504069: 250]` is equally compliant and fits "pay the rest with your 7447 card", but it yields a different hash, and only the reference order passes. This is an order-only free choice, the same class as the 2h probe.
- 2k: both assertions are enforced by the hash. 2g: no strings. 4d: user, certificates (100, 250), the 7447 card and the dob all match. 4e: consistent.

## Summary
- Defective tasks (>=1 medium/high): **10** (2k), **20** (4c).
- Rows with defect=1: **2** (2 medium, 0 high, 0 low); 2 rows are defect=0 with an "uncertain:" note (19/4c, 19/4d).
- No check was left unevaluated. `static_scan.csv` does not have the input columns `ref_args_unstated`, `ref_args_in_unknown_info`, `ids_missing_in_db`, `ci_min_chars` and `ci_in_user_scenario`, so 1d, 2g and 4d were derived by hand from the task cards and `db.json`.
