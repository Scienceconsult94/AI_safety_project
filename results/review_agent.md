# Trajectory review of the agent runs (checks 1e, 4f, 5c, 5d)

Scope: the 21 trajectories listed in `results/agent_triage.md` (tau2-bench v2.0.0, airline, split base; agent and user simulator both claude-haiku-5-5; substring communicate scorer; GT = `llm_agent_gt`). Successful trials of flipped tasks were read for comparison. Row-level evidence is in `results/review_agent.csv`.

Cause classes: A = agent slip; B = user simulator deviation; C = defensible alternative reading by the agent; D = reference or scoring problem. Turn numbers refer to the `[n]` markers in `results/trajectories/<task>_<run>_t<k>.md`.

Environment facts used below (read in `tau2-bench/src/tau2/domains/airline/tools.py`): `_get_new_reservation_id` hands out only HATHAT, HATHAU and HATHAV and then raises "Too many reservations"; `book_reservation` removes used certificates, lowers gift-card balances and lowers seat counts; `cancel_reservation` only appends negative payment entries and sets the status, so balances and seats are not restored; `update_reservation_flights` multiplies fare differences by the number of passengers.

## Per-trajectory readings

### Task 23, GT run (`23_gt_t0.md`), class B (A contributing)
The user asks for the gift-card and certificate totals and to move reservation K1NW8N (basic economy, three passengers, booked within 24 h) to the cheapest business round trip on the same dates, paying certificates first. The GT agent reports $327 and $1,000 (turns 11, 16), finds HAT023 + HAT204 + HAT100 at $871 per passenger, states that each reservation can use only one certificate (turn 16) and proposes a single three-passenger booking. The user picks certificate_3765853 and confirms (turns 17, 19). The agent cancels K1NW8N and books HATHAT for all three passengers (turn 22), a booking that is not in its reference list. Only at turn 25 does the user raise the three-reservation idea that the scenario ties to the confirmation step. The agent cancels HATHAT and books Raj (HATHAU) and Liam (HATHAV); Mohamed's booking fails twice with "Too many reservations" (turns 35, 39), and the profile shows the certificates gone and both gift cards at $0 (turn 41). The run ends in a transfer (turn 44). Divergence: turns 17 to 22 (single booking instead of three) and turn 25 (late split). The environment cannot recover from the extra booking. The booking order Raj, Liam, Mohamed also differs from the reference order (Mohamed first), which by itself changes the hash (consistent with static 23/2h).

### Task 11, Haiku trial 2 (`11_haiku_t2.md`), class B
The user wants passenger Sophia removed from GV1N64. The agent explains that the passenger count cannot change (turn 12). The user asks to downgrade all three passengers to basic economy, with the refund going "to my original payment method, not a gift card" (turn 13). The agent quotes the reference change (HAT003 and HAT290 in basic economy, refund $5,244 to gift_card_1642017; turn 19) and explains that this gift card is the original and only payment method (turn 21). The user declines and stops (turns 20, 22). The agent's turns match those of the successful trials t0 and t1, where the user accepted the refund to the gift card. Decisive turns: 13 and 20 to 22, where the simulator invents that the original payment was not a gift card.

### Task 16, GT run (`16_gt_t0.md`), class B
The user wants the cheapest economy flight on the day after the original reservation. The GT agent proposes exactly the reference: HAT110 + HAT172 on 2024-05-24, refund to gift_card_8887175 (turn 14). The user replies "I don't want it going to the gift card" (turn 15), then refuses because the refund "would go to the gift card and not my original card" (turns 17, 21), and stops (turn 23). The scenario says "You are happy with original payment for refund", and M05KNL was paid with gift_card_8887175. Same pattern as task 11 trial 2.

### Task 16, Haiku trial 1 (`16_haiku_t1.md`), class A
The agent finds the reference itinerary, then states that "the $207 fare would be charged to it. Its listed balance is $35" (turn 12) and that the change cannot be completed (turn 14). In fact the price difference is -$2,580, a refund. The user keeps the business reservation (turn 15). The successful trials t0 and t2 executed the same `update_reservation_flights` call. Decisive turns: 12 and 14.

### Task 7, GT run (`7_gt_t0.md`), class C (borderline A)
The user asks to cancel XEHM4B and 59XX6W. The GT agent accepts the illness reason for 59XX6W (insurance) but refuses to upgrade XEHM4B to business and then cancel it, because that "would get around those rules" (turn 11). The reference contains exactly this path (7_2, 7_3). The policy text allows a cabin change on basic economy and allows cancelling a business reservation, so the refusal is an anti-circumvention judgment that the policy does not state. The agent cancels 59XX6W (turn 13). Asked about other upcoming flights, it reports 7WPL39, 3EMQJ6 and XEHM4B, totalling $1,004 (turn 23); the expected string is "1628". Decisive turns: 11 (DB) and 23 (communicate).

### Task 7, Haiku trial 0 (`7_haiku_t0.md`), class C
After an initial refusal (turn 8), the agent performs the upgrade ($1,072; turn 19) and both cancellations (turns 10, 21), and the DB matches the reference. The user asks about "any other upcoming flights" after both cancellations (turn 24). The agent answers 7WPL39 $402 + 3EMQJ6 $306 = $708 (turn 30). The expected "1628" is 402 + 296 + 624 + 306, the amounts paid on all four upcoming reservations, including the two the user is cancelling. A literal reading of "other" gives $708. Later the user insists that the 59XX6W refund go to a "card ending in 2408938" (turns 24, 31, 33, 37); this echoes the agent's own misreading of the payment id as card digits (turn 6), and the run ends in a transfer. That episode does not affect the reward. Decisive turn: 30.

### Task 7, Haiku trials 1 and 2 (`7_haiku_t1.md`, `7_haiku_t2.md`), class C (borderline A)
Both trials refuse the upgrade-then-cancel (t1 turns 10 and 27; t2 turns 10 and 29) and cancel 59XX6W for illness (t1 turn 14; t2 turn 16). Both report $1,004 for the still-active upcoming reservations (turn 25 in each). Trial 1 ends in a transfer (turn 31). The pattern is the same as in the GT run.

### Task 22, Haiku trial 1 (`22_haiku_t1.md`), class B (A contributing)
The user (reactive by instruction) wants "some changes" to the New York to Chicago trip. The agent finds FQ8APE (EWR to ORD, passenger Ivan Garcia, basic economy). It says "Basic economy flights cannot be modified" and asks about dates or passenger names, not about which change is wanted (turn 13). The user claims the reservation "should be under my name, Omar Rossi" (turn 14), although the scenario premise is to change the passenger to himself. The user asks for another search (turn 16) and ends the conversation (turns 18, 20) without stating the three changes. In t0, an almost identical agent summary led the user to recognise the reservation and state all three changes (turn 14). Decisive turn: 14.

### Task 44, GT run (`44_gt_t0.md`), class A (B contributing)
The GT agent uses the per-segment reading: NM1VX1, KC18K6 and H8Q05L are upgrade candidates, and S61CZX is the cancellation candidate (turn 20). The user says the reason is neither health nor weather and asks for the total first (turn 21). The agent says S61CZX cannot be cancelled and gives two wrong statements (turn 22): that KC18K6 has "no layovers", and a total of $1,346 (the business fare for KC18K6 is $460 + $386 = $846, not $805; the correct total is $1,387). The user questions the durations and asks for a supervisor (turn 23). The agent transfers (turn 24) while all three in-scope upgrades are still pending. Decisive turns: 22 to 24.

### Task 44, Haiku trial 0 (`44_haiku_t0.md`), class C (B contributing)
The agent measures KC18K6 end to end: 06:00 to 13:00 is 7 h including the 2 h layover. It therefore puts KC18K6 in the cancellation group and offers upgrades only for NM1VX1 and H8Q05L, $647 (turns 24, 26). The user insists on the cancellations and says "I'm not going to pay for any upgrades until the cancellations are sorted out", then asks for a supervisor (turn 27). Two transfers follow (turns 28, 38). Even if the upgrades had been confirmed, the layover reading excludes the reference action 44_19, so the DB would still not match. Decisive turn: 24.

### Task 44, Haiku trial 1 (`44_haiku_t1.md`), class B
The agent uses the per-segment reading and gives the correct total of $1,387 (turn 22). The user says "Go ahead with the three upgrades. Let the system figure out the payment" (turn 23). The agent lists a payment method per reservation (Visa for NM1VX1 and KC18K6; gift card or Visa for H8Q05L) and asks for a yes (turn 24). The user replies "Hold off on the upgrades until that's resolved" and asks for a supervisor (turn 25), and the agent transfers (turn 26). Decisive turn: 25.

### Task 44, Haiku trial 2 (`44_haiku_t2.md`), class C (A and B contributing)
The agent uses the layover reading: KC18K6 (7 h) goes to the cancellation group (turn 20). It first quotes $874, the full business price, and then corrects this to a $647 difference (turns 22, 24). The user asks for "a firm total in writing, including any taxes or fees" and for a transfer (turn 27), and the agent transfers (turn 28). Decisive turn: 20 (KC18K6 is excluded from the upgrades).

### Task 32, GT run (`32_gt_t0.md`), class D
The user agrees to upgrade OWZ4XL (basic economy, three passengers) first and change to the nonstop afterwards (turn 11). The GT agent quotes $132 for the upgrade (turn 15); this is the per-passenger figure, and the real charge is 3 × $132 = $396. The user refuses because the limit is $100 (turns 16, 18, 20). Later the user claims to have booked only for itself (turn 24) and accepts a transfer. Even the understated $132 is above the cap, so the arithmetic error does not change the outcome. Decisive turn: 16.

### Task 32, Haiku trial 0 (`32_haiku_t0.md`), class D
The agent explains both paths. The one-step change gives a $114 refund. The two-step path is +$396 for the upgrade, then -$510 for the flight change (turns 15, 20, 22, 24). The user insists on separate steps, as the scenario requires, and refuses the $396 first step (turns 21, 23, 25). The net refund was explained and still did not lead to acceptance. Decisive turns: 21 and 23.

### Task 32, Haiku trials 1 and 2 (`32_haiku_t1.md`, `32_haiku_t2.md`), class D
In t1 the agent first says that the flights stay unchangeable even after an upgrade (turn 17). It corrects this (turn 19) and quotes $396 (turn 22). The user refuses because of the $100 cap and claims to be the only passenger (turns 23, 27), and the agent transfers (turn 30). In t2 the agent quotes $396 without mentioning the net effect (turn 20), and the user refuses (turn 21). Both runs stop at the same point as the GT run.

### Task 8, Haiku trial 1 (`8_haiku_t1.md`), class B
The agent proposes exactly the reference booking: HAT271 economy, two passengers, $348 on certificate_8045380. It notes that seats cannot be selected (turn 16). The user answers "No, that doesn't work for me. I need an aisle and a middle seat together" and asks for someone who can set seats (turn 17). The agent transfers (turn 18). In t0 the same wish was declared "not a dealbreaker". Decisive turn: 17.

### Task 8, Haiku trial 2 (`8_haiku_t2.md`), class A
The search shows 3 economy seats on HAT271 (turn 13), but the agent states "Only one economy seat is left on HAT271" (turn 16). The user accepts basic economy for both passengers (turn 17), and the agent books basic economy for $166 (turn 20). Decisive turn: 16.

### Task 19, Haiku trial 0 (`19_haiku_t0.md`), class B (A contributing)
The agent finds Z7GOZK (basic economy, insured) and says the return flight cannot be changed (turn 12). The scenario tells the user to cancel under the insurance in that case. Instead the user asks for "someone who can actually fix this" (turn 13), and the agent transfers at once (turn 14), without mentioning the cancellation option. Decisive turn: 13.

### Task 19, Haiku trial 1 (`19_haiku_t1.md`), class B
The agent offers a cabin change or a cancellation (turn 12). The user cancels for health reasons (turns 13 to 17), and the agent cancels Z7GOZK (turn 18), matching the reference. The user then asks the agent to book a new flight home "today" (turn 21), although the scenario says "You will book the flight again yourself later" and the trip is on 2024-05-28. The agent books HATHAT on 2024-05-16 (turn 32). The extra reservation breaks the DB match. Decisive turn: 21.

## Verdicts per task and check

| task | 1e (GT) | 4f | 5c | 5d | classes of failed trajectories |
|---|---|---|---|---|---|
| 7 | 0 (unclear) | **1** | 0 (0/3, no flip) | 0 (unclear) | GT C/A, t0 C, t1 C/A, t2 C/A |
| 8 | n/a | 0 | **1** | **1** | t1 B, t2 A |
| 11 | n/a (GT passed) | 0 | **1** | **1** | t2 B |
| 16 | 0 | 0 | 0 | **1** | GT B, t1 A |
| 19 | n/a (GT passed) | 0 | **1** | **1** | t0 B, t1 B |
| 22 | n/a (GT passed) | 0 | **1** | **1** | t1 B |
| 23 | 0 | 0 | 0 (3/3, no flip) | **1** (borderline) | GT B/A |
| 32 | **1** | 0 | 0 (0/3, no flip) | **1** | GT D, t0 D, t1 D, t2 D |
| 44 | 0 (unclear) | **1** | 0 (0/3, no flip) | **1** | GT A, t0 C, t1 B, t2 C |

Counts of defect=1: 1e 1 of 5 (task 32); 4f 2 of 9 (7, 44); 5c 4 of 9 (8, 11, 19, 22); 5d 8 of 9 (all except 7).

Comparison with the static findings:
- **Agreements:** task 44: layover ambiguity (4a) and open payment for H8Q05L (4c), both visible in the runs; task 7: the literal "other upcoming flights" reading gives 708 (static 4a note); task 7: the policy allows the upgrade-then-cancel path (static 4b = 0); tasks 11, 16, 19 and 22: no task-side defect, and the failures come from the simulator or the agent.
- **Disagreement:** task 32. Static 4a was set to 0 with an "uncertain" note saying that a literal simulator may refuse step 1. The runs show this refusal in 4 of 4 runs, and it is recorded here as 1e = 1.
- **Corroboration:** task 23. Static 2h/4c (the hash depends on booking order) is corroborated by the GT run's booking order.

## Observations beyond the checklist

1. **The communicate string "1628" (task 7) appears in none of the 4 runs.** The values produced are $708 (literal "other upcoming flights", t0) and $1,004 (reservations still active at the time of asking: GT, t1 and t2). "1628" counts the two reservations that the same reference cancels, so it is right only if the question is answered before any cancellation and "other" is read as "all".
2. **Upgrade-then-cancel loophole (task 7).** Three of four runs refuse it, including the GT agent, which is shown the reference actions. The policy text permits each step. Under the current reference, the task rewards willingness to use a loophole rather than policy compliance.
3. **The environment does not let an agent recover from an extra booking (task 23).** There are only three new reservation ids per episode. Certificates and gift-card balances are consumed at booking and are not restored on cancellation, and seats are not released. One exploratory or non-reference booking makes the target hash unreachable; this is how the GT run failed.
4. **"Original payment method" read as "not the gift card" (tasks 11 t2 and 16 GT).** In both tasks the original payment was a gift card, and the simulator invented a separate card and abandoned a correct change. The same phrase appears in several airline scenarios.
5. **Escalation to a human after a policy denial.** The simulator itself asks for a supervisor or a human in task 44 (4/4 runs), 19 t0, 8 t1 and 7 t0; in 7 t1 and 32 t1 it accepts a transfer the agent offers. Agents usually comply at once, which ends the episode with in-scope work still pending (44 GT, 19 t0, 8 t1). The policy's "transfer if and only if the request cannot be handled within the scope of your actions" leaves it open whether a denied request counts as out of scope.
6. **Scenario constraints that conflict with the reference path.** In task 32, the $100 cap conflicts with a reference step of +$396 (followed by -$510), and all runs stall there. In task 44, the scenario gives no fallback for a cancellation that cannot be done, so the simulator conditions the upgrades on it. In task 8, the scenario contains a seat wish that no tool supports and does not say whether it is a deal-breaker.
7. **Simulator inventions and leaks.** The simulator invents facts about passengers in task 32 (GT turn 24; t1 turns 23 and 27), rebooks against the scenario in task 19 (t1 and t2), and leaks its instructions in task 19 t2 turn 37 ("The scenario gives me no date of birth to share"). The only success on task 19 (t2) is accidental: the same rebooking deviation happened there and was blocked only because the simulator refused to give a date of birth.
8. **The GT agent sees the reference actions but not the amounts.** It still makes arithmetic errors: $132 instead of $396 in task 32, and $805 instead of $846 for KC18K6 in task 44. Neither error decided the outcome here, but GT runs are not a clean test of whether a task can be solved when the user's decision depends on a quoted amount.
