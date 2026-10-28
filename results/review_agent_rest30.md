# Trajectory review of the rest-task agent runs (checks 1e, 4f, 5c, 5d)

Scope: the 19 trajectories listed in `results/agent_triage_rest30.md` (tau2-bench v2.0.0, airline, split base; agent and user simulator both claude-haiku-5-5; substring communicate scorer; GT = `llm_agent_gt`, one run per eligible task). The successful trials of flipped tasks were read for comparison. Row-level evidence is in `results/review_agent_rest30.csv`.

Cause classes: A = agent slip; B = user simulator deviation; C = defensible alternative reading by the agent; D = reference or scoring problem. Turn numbers refer to the `[n]` markers in `results/trajectories/<task>_<run>_t<k>.md`.

Conventions carried over from the block-1 review (`results/review_agent.md`): a GT failure caused by a simulator deviation (class B) gets 1e = 0 and is recorded under 5d; a task whose failures are all class D gets 4f = 0, and the D cause is recorded under 1e; 5c = 1 when at least one flip traces to the simulator.

Environment facts seen again in these runs: `cancel_reservation` only appends negative payment entries, so certificates and gift-card balances used by a booking are not restored (14 GT, turn 44). `update_reservation_flights` does not check origin or destination (29 t2, 42 t0).

## Per-trajectory readings

### Task 14, GT run (`14_gt_t0.md`), class B (A contributing)
The user wants the gift-card and certificate totals and then the cheapest business round trip on the same dates as K1NW8N (basic economy, three passengers, booked within 24 h). The GT agent gives $327 and $1,000 (turn 11). At turn 27 it proposes exactly the reference: cancel K1NW8N; book HAT023 + HAT204 + HAT100 for all three passengers; pay with the $500 certificate, both gift cards and $1,786 on the Mastercard. The user then asks to drop Raj Sanchez and Liam Wilson. The user also says not to use credit_card_2198526, which is the Mastercard the user wants to pay with (turn 28). Nothing in the scenario mentions passengers. The agent cancels K1NW8N and books a one-passenger HATHAT, putting $44 on the Visa by mistake (turn 33). It then cancels HATHAT. The rebooking fails because the certificate is gone (turns 42 to 45). It books HATHAU with a $250 certificate and $621 on the Mastercard, and transfers the user (turn 53). Decisive turn: 28. The invented passenger change makes the target unreachable on its own.

### Task 14, Haiku trial 1 (`14_haiku_t1.md`), class A
The agent finds the same itinerary but treats basic-economy K1NW8N as modifiable. It quotes a $2,046 difference on a single card (turn 17) and says certificates cannot be used (turn 19). The user declines because the charge is over $2,000, and the reservation stays unchanged (turns 20 to 24). The agent never cancels and rebooks, so "1786" is never produced. Decisive turns: 17 and 19.

### Task 14, Haiku trial 2 (`14_haiku_t2.md`), class B (A contributing)
The agent states the basic-economy restriction, then cancels and rebooks the reference flights for all three passengers with the reference payment split ($1,786 on the Mastercard, turn 31). At turn 25 it asked "each business passenger gets 2 free checked bags. Do you need any bags beyond that?". The user answered "I don't need any checked bags beyond the included ones" (turn 26) and confirmed a summary with "6 total" bags (turn 32). The booking has total_baggages 6, while the reference has 0. The scenario says "You do not need baggage". In t0 the user said so directly, and the agent booked 0 bags. Decisive turns: 26 and 32. The agent's leading question contributed.

### Task 15, Haiku trial 2 (`15_haiku_t2.md`), class A
The user wants the cheapest economy flight on the day after M05KNL. The agent searches only the legs of the current connection, ATL-ORD and ORD-PHL (turn 9), and books HAT227 + HAT139 for $216 (turns 14, 18). The reference HAT110 + HAT172 costs $207. The successful trials found it with `search_onestop_flight(ATL, PHL)`. The simulator claims "My original booking was in Economy" and asks for the refund not to go to the gift card (turn 13). Both claims are wrong, and neither changed the outcome. Decisive turns: 9 and 14.

### Task 17, Haiku trial 2 (`17_haiku_t2.md`), class A (B contributing)
The user asks for three changes on the New York to Chicago trip. The agent reads all four reservations. It then says "None of them is a New York to Chicago trip that matches your request", although FQ8APE (EWR to ORD) is listed. It adds that "basic economy reservations cannot be modified" and that the passenger "is also not you", and asks for another reservation id (turn 11). The user says the booking should be under the user's name and suggests it may be on another account. The user then ends the chat before any change is made (turns 12, 14). In t0 and t1 the agent asked whether FQ8APE was the reservation meant, and the user recognised it. Decisive turn: 11.

### Task 24, GT run (`24_gt_t0.md`), class B (A contributing)
The GT agent correctly refuses to remove Ethan and to cancel H9ZU1C (turns 2, 9). The scenario says "If agent says cancellation is not possible, accept it and move on". Instead, the user asks for "someone who can actually fix this" (turn 10), and the agent transfers at once (turn 11). Its reference includes the booking that is still to come. After the transfer the simulator keeps talking for twelve more turns and gives the whole booking request (turns 18, 20). The agent declines to act because the transfer has already been made. No write takes place. Decisive turns: 10 and 11.

### Task 24, Haiku trial 0 (`24_haiku_t0.md`), class A
The agent refuses the passenger removal and the cancellation, and the user moves on (turn 7). The agent then books the reference flights, cabin, passenger, payment split and one free bag, but passes `destination: "JFK"` for the JFK to SEA round trip (turn 32). The reference has "SEA", and t1 and t2 used "SEA". The `book_reservation` docstring does not define the destination of a round trip. In `db.json`, 34 of 955 round trips have origin equal to destination. This is a weak D component and is not counted. Decisive turn: 32.

### Task 29, GT run (`29_gt_t0.md`), class D
The user wants VA5SGQ (DTW to LGA) moved to nonstop flights to JFK and asks for a change-fee waiver on health grounds. The GT agent explains that the destination cannot change. It offers two options: cancel under the insurance, or book a separate new trip (turns 7, 9). The user does not want to cancel (turn 8) and picks the new booking only (turn 10). The agent proposes HAT169 + HAT033 in economy for $282, with one bag, on the Visa ending 6521 (turn 14), and asks the user to confirm the date of birth (turn 16). The scenario does not give a date of birth. The user goes to "check my ID" and ends the chat (turns 17 to 25). The reference needs `cancel_reservation(VA5SGQ)`, but the scenario never authorises a cancellation. All four runs of this task declined it. Decisive turns: 8 and 10 (cancellation), 17 (date of birth).

### Task 29, Haiku trials 0 and 1 (`29_haiku_t0.md`, `29_haiku_t1.md`), class D
Both agents explain the destination rule and offer the reference route: cancel for health under the insurance, then book HAT169 and HAT033 (t0 turns 7, 12, 14; t1 turns 9, 15, 17). Both users decline to cancel and keep VA5SGQ (t0 turns 8, 13, 15, 17; t1 turns 8, 10, 18, 20). In t1 the agent also asks which of four payment methods to use (turn 17); the scenario names none (static 4c). No write takes place in either run.

### Task 29, Haiku trial 2 (`29_haiku_t2.md`), class A
The agent says twice that the destination cannot change (turns 7, 9). It then changes VA5SGQ to HAT169 on 2024-05-17 and HAT033 on 2024-05-20 (turn 22) and adds one bag (turn 24). This breaks the policy rule on destination changes, and the agent later notes that "The reservation header still lists LaGuardia" (turn 26). It also picked a return on the 20th without asking; the scenario specifies the 19th. The simulator invents that the original booking was "supposed to be a nonstop" (turn 8). Decisive turn: 22.

### Task 30, Haiku trial 1 (`30_haiku_t1.md`), class A
The agent identifies HAT266 as the nonstop replacement. It then says the change would cost $292 and leave $225 unpaid on the $67 gift card (turns 13, 17). The real difference is a refund of $414: (146 - 161 - 192) x 2. Trials t0 and t2 report this refund. The user keeps the reservation (turn 18). The simulator named HAT266 before the agent had shown it (turn 8); the scenario text itself calls HAT266 "your upcoming one-stop flight". Decisive turn: 13.

### Task 33, Haiku trial 1 (`33_haiku_t1.md`), class B (A contributing)
The agent first proposes the return on 2024-05-21, and the user corrects it to 2024-05-23 (turns 12, 13). The user then picks "the gift card with the higher balance", gift_card_1646646. This contradicts "You are ok with paying for it using the original form of payment". The user also asks for the change fee to be waived, although the agent never asked for a fee (turn 15). The agent says it cannot waive fees and does not see any change fee in the policy (turn 16). The user demands a supervisor (turn 17), and the agent transfers before making any change (turn 18). Decisive turns: 15 and 17.

### Task 33, Haiku trial 2 (`33_haiku_t2.md`), class B (A contributing)
The flight change matches 33_3 (turn 14). The agent states that no change fee was charged (turn 16). The user keeps disputing the waiver and asks for a supervisor (turns 17, 19), and the agent transfers (turn 20). The upgrade and two-bag request, which the scenario places right after the flight change, comes only after the transfer (turns 25 to 41). The agent no longer acts on it, and the episode ends with ###OUT-OF-SCOPE###. In t0 the waiver never came up, and the bags were added. Decisive turns: 17 and 19.

### Task 39, GT run and Haiku trials 0 and 1 (`39_gt_t0.md`, `39_haiku_t0.md`, `39_haiku_t1.md`), class D
The user wants every upcoming reservation cancelled, refund or not, to free the seats. The user gives "change of plan" as the reason (GT, t0, t1, turn 13). All three agents cancel 8C8K4E and LU15PA (business) and refuse UDMOP1 and XAZ3C0 (basic economy, no insurance). They also refuse MSJ4OA: it is economy with insurance, and "a change of plan isn't covered" (GT turns 18 to 22; t0 turns 14, 19; t1 turn 14). The reference cancels MSJ4OA (39_10), but the policy lets insurance cover only health or weather reasons. The GT agent refused this action even though it was in its own reference. The only reward-1 trial (t2) cancels MSJ4OA for "change of plan" (turn 19), which breaks the policy. Decisive turn: the MSJ4OA refusal in each run.

### Task 42, GT run (`42_gt_t0.md`), class A (B contributing)
The user says "Anything that doesn't fit that is the mistake" (turn 13), which is broader than the scenario's "multiple flights for the same day". The GT agent marks MFRB94 (2024-05-27 to 2024-05-30) as "Doesn't match your plan" (turn 14). Its reference cancels only FDZ0T5 and HSR97W. The agent cancels MFRB94, HSR97W and FDZ0T5 (turns 18 to 22). The user also calls HTR26G a mistake and asks for a review, and the run ends in a transfer (turns 15, 17, 24). Decisive turn: 14.

### Task 42, Haiku trial 0 (`42_haiku_t0.md`), class A
The agent cancels FDZ0T5 and HSR97W correctly (turns 17, 19). It had also offered to drop the MIA to DEN leg of PUNERT. It does so with `update_reservation_flights(PUNERT, [HAT086])` (turn 23), which changes the reservation's destination, and the agent notes that "The reservation summary still lists DEN" (turn 25). In t1 and t2 the agent refused exactly this change (t1 turn 14, t2 turn 16). The agent also proposed cancelling SE9KEL, which has other passengers (turn 15); the user declined. Decisive turn: 23.

## Verdicts per task and check

| task | 1e (GT) | 4f | 5c | 5d | classes of failed trajectories |
|---|---|---|---|---|---|
| 14 | 0 | 0 | **1** (borderline) | **1** | GT B/A, t1 A, t2 B/A |
| 15 | n/a (GT passed) | 0 | 0 | **1** (borderline) | t2 A |
| 17 | n/a (GT passed) | 0 | 0 | **1** (borderline) | t2 A/B |
| 24 | 0 | 0 | 0 | **1** | GT B/A, t0 A |
| 29 | **1** | 0 | 0 (0/3, no flip) | **1** (borderline) | GT D, t0 D, t1 D, t2 A |
| 30 | n/a (GT passed) | 0 | 0 | 0 | t1 A |
| 33 | n/a (GT passed) | 0 | **1** | **1** | t1 B/A, t2 B/A |
| 39 | **1** | 0 | 0 | 0 | GT D, t0 D, t1 D |
| 42 | 0 | 0 | 0 | **1** (borderline) | GT A/B, t0 A |

Counts of defect=1: 1e 2 of 5 (tasks 29 and 39); 4f 0 of 9; 5c 2 of 9 (14 and 33); 5d 7 of 9 (all except 30 and 39). Of the seven 5d rows, four are borderline or outcome-irrelevant (15, 17, 29, 42). Three are outcome-decisive (14, 24, 33).

Summary of the 19 primary classes: A 8, B 5, D 6, C 0.

## Comparison with the static findings (`review_batch_5..10.csv`, `rereview_blind_rest.csv`)

- **Agreement, task 39.** Static 4b = 1 (high, both reviews) says the MSJ4OA cancellation conflicts with the policy. The runs confirm it: three policy-compliant runs refuse the cancellation, and the only success breaks the policy.
- **Disagreement, task 29.** Static 4a = 0, with the note "the cancellation is not requested in words but is the policy route". The runs show the simulator declining the cancellation in 4 of 4 runs, so it is recorded here as 1e = 1. Static 4c = 1 (payment method and insurance of the new booking open) is corroborated: t1 turn 17 asks the user to choose among four methods.
- **Corroboration, task 33.** Static 4c = 1 flags two things: "move back" can mean an earlier date, and the refund destination is pinned only by a sentence about the upgrade. Both appear in t1: the agent first proposes 2024-05-21 (turn 12), and the user picks gift_card_1646646 (turn 15). Neither decided the outcome; the supervisor escalation did.
- **Corroboration, task 15.** The static 4a note gives HAT227 + HAT139 = $216 as the next-cheapest option, and that is exactly what t2 booked.
- **Corroboration, task 30.** The static 4d note calls the HAT266 parenthetical ambiguous. In t1 the simulator presents HAT266 as the current one-stop flight (turn 8). The outcome was not affected.
- **Not exercised:** static 4c/2h for task 14 (payment-entry order) and task 17 (bags before the upgrade), and static 2h for task 33 (two separate flight updates). Every run that wrote used the reference order or a single call.
- **New, not in the static rows:** task 24, round-trip `destination` is a hashed free-text field that the static 4c list of open choices does not include (24 t0). Task 14, booking the free bag allowance against "no baggage" (t2) is a hashed choice that the static rows treat as pinned.

## Observations beyond the checklist

1. **The scorer rewards a policy violation in task 39.** Three of four runs, including the GT agent, which was shown the reference, refuse to cancel MSJ4OA for "change of plan". The single reward-1 trial cancels it. Under the current reference, pass^k for task 39 measures whether the agent ignores the insurance-reason rule.
2. **A scenario without the fallback that the reference needs (task 29).** The reference cancels and rebooks, but the scenario only asks for a change and a fee waiver. A faithful simulator does not authorise the cancellation, and none did, in 4 of 4 runs. Task 24, by contrast, states its fallback ("If change is not possible, you want the agent to cancel"). Task 29 also gives no date of birth and no "look it up in my profile" line, unlike tasks 17 and 24. The GT run stalled when the agent asked the user to confirm the date of birth.
3. **"Change fee" waivers for fees that do not exist (tasks 29 and 33).** Neither the policy nor the tools define a change fee. The agents gave hedged answers, such as "I can't waive any change fees" and "I can't say what the fee would be". These kept the dispute going. In task 33 both failures come from the simulator escalating it to a supervisor, although the scenario makes the waiver conditional on the agent asking for a fee. In the passing trial the topic never came up.
4. **Escalation, immediate transfer, and talk after the transfer.** The simulator asks for a human or a supervisor in 24 GT, 33 t1, 33 t2, 39 GT, 39 t1 and 42 GT. The agent complies at once, even with in-scope work still pending (the booking in 24 GT, the bags in 33 t2). In 24 GT and 33 t2 the simulator keeps talking for 10 or more turns after "YOU ARE BEING TRANSFERRED", instead of sending ###TRANSFER###. It repeats the pending request, and the agent declines because the transfer has been made. Those episodes cannot reach the target.
5. **Route-changing modifications.** In 29 t2 (LGA to JFK) and 42 t0 (PUNERT minus its last leg), the agent calls `update_reservation_flights` with a new origin or destination, which the tool does not check. Both agents then noticed the stale origin or destination field. The hash caught both runs.
6. **Recurring agent errors.** The agent treats a fare difference as a charge in 30 t1, the same error as in block-1 task 16 t1. It treats basic economy as modifiable in 14 t1. It searches only the legs of the current connection in 15 t2. It denies a matching reservation in 17 t2.
7. **Free-bag defaults decide the hash.** In task 24 the scenario asks for "all your free baggage allowance" and the reference books 1 free bag. In task 14 the scenario says "You do not need baggage" and the reference books 0. Whether the agent books the free allowance by default is therefore a hashed choice. In 14 t2 it was resolved through a leading question and the simulator's loose answer.
8. **Communicate strings.** Of the reviewed tasks, only task 14 has `communicate_info` ("327", "1000", "1786"). All three appear in GT, t0 and t2. "1786" is missing only in t1, where the agent never reached the cancel-and-rebook step. No string is unreachable.
9. **Simulator inventions that did not decide the outcome.** The original cabin in 15 t2 (turn 13), the "nonstop" original booking in 29 t2 (turn 8), and HTR26G as a mistake in 42 GT (turn 15). The "original payment method is not the gift card" misreading, seen in block-1 tasks 11 and 16, recurs in 15 t2 (turns 13, 15).
