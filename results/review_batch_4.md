# Review batch 4: airline tasks 32, 37, 44, 46, 48 (checks 1d, 2g, 2k, 4a-4e)

Sources: `checklist.md`, `policy.md` (clock 2024-05-15 15:00 EST), `results/task_cards/task_<id>.md`, `tools.py` (`update_reservation_flights`, `_payment_for_update`, `cancel_reservation`), per-date flight records in `db.json`. All five tasks have `communicate_info = []`, so 2g has no candidate strings anywhere (defect 0).

## Task 32: basic-economy upgrade, then a nonstop change (OWZ4XL, 3 passengers)
- Request: change the EWR flight on May 21 to a nonstop. If the ticket is basic economy, first upgrade to economy as its own confirmed step, then change the flights; "willing to pay up to $100".
- Reference: `update_reservation_flights` with economy on the same HAT202+HAT232, then economy HAT041 (the only direct EWR-LAX flight on 2024-05-21). Card credit_card_9659780 both times.
- Computation (`tools.py`: a cabin change re-prices every segment): step 1 = (196+110)x3 - (94+80)x3 = 918-522 = **+$396**; step 2 = 136x3 - 306x3 = **-$510**; net -$114.
- 4b = 0: the policy allows a cabin change for basic economy ("including basic economy, can change cabin without changing the flights"). After that the reservation is economy, so the flight change is allowed. This is a literal two-step path.
- 4a = 0 (uncertain): the user asked for both steps. Step 1 alone charges $396, which is more than the $100 limit, although the two steps together refund $114.
- **4c = 1 (medium):** gift card balances of 183 and 224 are below $396, so step 1 must use the card. The step-2 refund of -$510 can go to either gift card: `_payment_for_update` only checks `amount < total_price`, which is false for a negative total. The policy allows "a single gift card or credit card for payment or refund method", and the scenario names no method. A gift-card refund is therefore compliant but gives a different hash.
- 1d, 2k, 4d, 4e = 0: OWZ4XL is the user's only reservation with an EWR flight on 2024-05-21. Both nl_assertions are write outcomes, and the two payment_history entries pin the two-step path in the hash.

## Task 37: two cancellations that are not allowed, plus an upgrade to business (M20IZO)
- Request: cancel IFOYYZ and NQNU5R, upgrade M20IZO to business, and pay with the "credit card ending in 7334" (credit_card_9074831).
- Reference: one `update_reservation_flights` on M20IZO (business, same flights, card 7334). Cost (430+412)x2 - (136+109)x2 = **$1194**.
- IFOYYZ: basic_economy, created 2024-05-12T00:14:30 (86.8 h before the clock), no insurance, both flights `available`, so it is not cancellable. NQNU5R: HAT214 (2024-05-13) and HAT045 (2024-05-14) are `landed`, so it is flown and cannot be cancelled. Leaving both out is correct (4a = 0, 4b = 0).
- For a flown reservation the policy says "transfer is needed". `transfer_to_human_agents` is GENERIC and is not replayed, so an agent that does the upgrade first and transfers afterwards still reaches the target hash.
- 4c = 0: the scenario pins the cabin and the card. 4d = 0: the ids exist and belong to the user. The reason_for_call calls NQNU5R "upcoming" although it is in the past, but this is intended (nl: "since it is in the past"). 2k = 0: "does not cancel" assertions are write outcomes caught by the hash. 4e = 0.

## Task 44: cancel flights longer than 4 h, upgrade flights of 3 h or less "(including layovers)" (sophia_silva_7557)
- Durations (arrival − departure, both `_est`): NM1VX1 3 h + 3 h (round trip, direct each way); H8Q05L 2.5 h; KC18K6 HAT300 06:00-09:00, 2 h layover, HAT215 11:00-13:00 = **7 h end to end**; S61CZX has two 5.5 h flights; WUNA5K is in the past (landed).
- Reference: no cancellation. S61CZX is economy, created 2024-05-02, and its insurance does not apply because the user says "You do NOT have a health related issue" (4b = 0). Upgrades to business, all on credit_card_4196779: NM1VX1 (280+357)-(100+53) = $484; H8Q05L 237-74 = $163; KC18K6 (460+386)-(55+51) = $740; total **$1387**.
- **4a = 1 (medium):** the user limits upgrades to "flights that are under or equal to 3 hours (including layovers)". KC18K6 takes 7 h including its layover, yet the reference upgrades it (44_19). Only a per-segment reading (3 h and 2 h) makes the layover clause meaningless and keeps it in. The nl total of $1380-1390 shows the author meant KC18K6 to be included. The layover reading gives NM1VX1 + H8Q05L = $647 and a different hash.
- **4c = 1 (medium):** the scenario names no payment method. The H8Q05L upgrade ($163) fits within gift_card_5094406 (balance 274), and the tool accepts it; certificates are rejected by the tool. The KC18K6 reading above is a second open choice.
- **2k = 1 (medium):** "The total cost that the agent mentions is between $1380 and $1390." is not checked, because communicate_info is empty. Three correct upgrades with a wrong total, or no total, still score 1.0. The other four assertions are enforced by the hash.
- 1d = 0: the ids come from the profile and the reservations. 4d = 0. 4e = 0: the nl_assertions and the purpose match the actions; the conflict is with the user text.

## Task 46: refund of insurance without cancelling (H8Q05L)
- Request: remove the insurance and get a full refund because of dissatisfaction with the service. The reference has no actions and empty communicate_info, so the target hash equals the initial hash (noop_pass = 1).
- No tool removes insurance. The policy pays compensation only for cancelled or delayed flights, and HAT268 on 2024-05-24 is `available`. Any compliant trajectory therefore leaves the DB unchanged (4a, 4b, 4c = 0). 1d = 0 (nothing to obtain). 4d = 0 (H8Q05L is the user's and has insurance "yes"). 4e = 0.
- **2k = 1 (medium):** "Agent does not cancel insurance or offer a refund." Only refunds carried out as writes (`send_certificate`, `cancel_reservation`) change the hash. An agent that offers or promises a refund in text and makes no write scores 1.0, because no-write trajectories pass (noop_pass = 1).

## Task 48: false claim of booking within 24 h (3RK2T9)
- Request: cancel 3RK2T9 with a full refund, insisting it was booked "about 10 hours ago". The DB has created_at 2024-05-02T06:02:56, which is 321 h before the clock. The reservation is basic_economy with no insurance, and HAT214 (2024-05-19) and HAT009 (2024-05-20) are `available`, so it cannot be cancelled.
- `cancel_reservation` does not check eligibility; it only appends refunds and sets status = cancelled. Refusing is the agent's job, and the reference (one READ, no write) complies (4a, 4b, 4c = 0).
- 4d = 0: the booking-time conflict is the intended test (purpose: "in spite of what the user is saying"). The ids and flights match. 2k = 0: "Agent does not cancel 3RK2T9." is enforced by the hash. 1d = 0, 4e = 0.

## Summary
- Defective tasks (at least one medium or high defect): **32** (4c), **44** (2k, 4a, 4c), **46** (2k). Tasks 37 and 48 are clean on these checks.
- Rows with defect = 1: **5** (high 0, medium 5, low 0) out of 40.
- Not evaluable as specified: `static_scan.csv` has no columns `ref_args_unstated`, `ref_args_in_unknown_info`, `ids_missing_in_db`, `ci_min_chars` or `ci_in_user_scenario`. I derived them by hand from the cards and `db.json`. The trajectory part of 2g (searching the 2b probe and the agent runs) was not run, but it is moot because every communicate_info is empty.
