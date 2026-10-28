# Trajectory review, retail batch D (checks 1e, 4f, 5c, 5d, 2j)

Scope: tasks 64, 66, 71, 72, 80, 82, 83, 87, 91, 93. The 18 failed trajectories listed for them in `results/retail/agent_triage.md` (the assignment said 19; the list has 18), plus the 11 successful trials of the flipped tasks (66 t1, t2; 71 t2; 72 t0, t1; 82 t1; 83 t2; 87 t0, t1; 91 t1, t2), 29 transcripts in all. Runs: `retail_pass3_haiku` (3 trials per task, `llm_agent`) and `retail_gt_haiku` (`llm_agent_gt`), tau2-bench v2.0.0, commit `989d3285ae669e49503324bdb9981bf14fccedeb`, stock scorer. Row-level evidence is in `results/retail/review_agent_D.csv`.

Cause classes: A = agent slip; B = user-simulator deviation; C = defensible alternative reading; D = reference or scoring problem; E = judge error. Turn numbers refer to the `[n]` markers in `results/retail/trajectories/<task>_<run>_t<k>.md`.

Facts used throughout. None of the ten tasks has `nl_assertions`, so the NL judge is not involved and the reward equals the DB check. The simulator runs on the plain-text scaffold of `tau2-bench/src/tau2/user/guidelines.py` (`_TEXT_PLAIN`): it is told to follow the scenario strictly and to treat anything the scenario does not state as unknown. Unlike the voice scaffold, this one has no line saying "if asked for a preference that is not in your instructions, say you have no preference". Policy (`policy.md`): a refund for a return must go to the original payment method or to an existing gift card; a pending order can be modified only to variants of the same product; the item modification can be done once and locks the order.

## Per-trajectory readings

### Task 64, GT run (`64_gt_t0.md`), class D (B contributing)
The user wants to swap the camera on pending order #W7464385 (1080p, not waterproof, silver, $502.28) for the highest-resolution waterproof camera within the price paid. The agent lists the available variants. Two of them qualify: 4K waterproof black at $466.75 and 4K waterproof silver at $481.50 (turn 16). The user first leans to the cheaper black one (turn 17). At turn 19 the user says "You said you wanted to stay as close to what I paid", although that wish was the user's own (turn 17), and asks about silver. The user picks silver (turn 21). The agent runs `modify_pending_order_items` 1810466394 -> 6117189161 (turn 22). The reference 64_7 expects 6700049080 (black). The scenario names no colour, so both end states comply, and only the black one passes. This is the known static row 4c.

### Task 64, pass3 trials 0, 1, 2 (`64_haiku_t0/t1/t2.md`), class D (B contributing in t1)
All three trials follow the same path as the GT run. The agent offers both 4K waterproof variants (t0 turn 19, t1 turn 19, t2 turn 16). The simulator picks silver in every trial: t0 turn 20 ("closest match to what I paid"), t1 turn 20 ("I'd like to keep the same color as the original", a preference the scenario does not state), t2 turn 17 (no reason given). Each trial ends with `modify_pending_order_items` 1810466394 -> 6117189161 (t0 turn 23, t1 turn 23, t2 turn 20). No trial calls the raising 64_6 exchange. Reward 0/3, all for the reason in 4c.

### Task 66, pass3 trial 0 (`66_haiku_t0.md`), class B
The scenario: "change the luggage set in your order for a coat", then return the item if that is impossible, then cancel the whole order if there are issues. The simulator opens with "I ordered a coat, and I got a luggage set along with it, and I'd like to swap that luggage set out for something else" (turn 1). The agent finds no coat in either order and offers other luggage variants (turns 13, 17). The simulator picks the 3-piece blue softshell set because "Blue sounds good to me" (turn 18) and confirms (turn 20). The agent runs `modify_pending_order_items` 7160999700 -> 6301799585 (turn 21). The agent's actions are correct for what the simulator asked. The divergence is the simulator's misreading at turn 1 and the luggage preference it invents at turn 18.

### Task 66, pass3 trials 1 and 2 (`66_haiku_t1.md`, `66_haiku_t2.md`), reward 1
In t1 the simulator asks for the coat (turn 1). The agent explains that the product type cannot change (turn 14) and that a single item cannot be returned from a pending order (turn 16). The simulator cancels for "no longer needed" (turn 17), and the cancellation runs at turn 20. T2 starts with the same misreading as t0 (turn 1). The simulator then invents a "3-piece, black, hardshell" wish (turn 16) and rejects the available sets: "the black 2-piece isn't the size I need" (turn 20). It moves on to a return, which is refused, and then to cancellation with "no longer needed" (turns 20 to 25). Both successes depend on the simulator choosing the cancellation reason the reference fixes (static 1d/4c).

### Task 71, pass3 trial 0 (`71_haiku_t0.md`), class A
The address is changed to the Charlotte default (turn 16), as in 71_0. The user leaves the lamp unchanged and switches from the gift card to PayPal at the confirmation step (turns 27, 29), as the scenario asks. The agent then submits `modify_pending_order_items` 2492465580 -> **6309044598** (grey, large, polyester, hydration, $218.59) instead of the confirmed 5917587651 (grey, medium, polyester, laptop, $212.79) (turn 32). It reports its own error (turn 34) and transfers (turn 36). Decisive turn: 32.

### Task 71, pass3 trial 1 (`71_haiku_t1.md`), class B (A contributing)
The agent asks which payment method to use (turn 18), and the simulator answers with the gift card, which is correct (turn 19). At turn 20 the agent asks for confirmation: "Do you confirm the backpack change, with the price difference paid by gift card? (yes/no)". The scenario says that at this point the user switches to PayPal and keeps only the backpack. The simulator keeps the gift card ("Yes on the backpack too, with the difference on the gift card") and only drops the lamp (turn 21). It also asks to hear the final total "before you submit". The agent answers and submits in the same turn: the address change at turn 22, then `modify_pending_order_items` 2492465580 -> 5917587651 on gift_card_1711656 at turn 24. Answering and calling a tool in the same turn goes against the policy's one-action-per-turn rule. The simulator asks for PayPal only after the write (turn 27). Decisive turn: 21.

### Task 71, pass3 trial 2 (`71_haiku_t2.md`), reward 1
The address is changed first (turn 14). The simulator chooses the gift card when asked for a payment method (turn 22). At the confirmation request (turn 25) it switches to PayPal and to the backpack only (turn 26). The agent submits 5917587651 on paypal_7729105 (turn 29). The agent's behaviour is the same as in t1. Only the simulator's answer to the confirmation request differs.

### Task 72, pass3 trial 2 (`72_haiku_t2.md`), class B (A contributing)
The scenario adds one instruction to task 71: "first mention the modification then the address". The simulator mentions the address first (turn 1), as it does in t0 and t1. At turn 19 the agent lists the address change and both item changes in one message. That message asks for the payment method and for a yes/no at the same time. The simulator answers "the gift card works for the price difference. Yes, please go ahead" (turn 20). The agent changes the address (turn 21) and then submits both items on gift_card_1711656 (turn 23). The agent offered the payment choice without listing it among the details to confirm, so the confirmation came before the full details were stated (A contributing). The simulator did not switch even though a confirmation request was present, and it says so itself at turn 28: "I should have said that before you made the changes". Decisive turns: 19 and 20.

### Task 72, pass3 trials 0 and 1 (`72_haiku_t0.md`, `72_haiku_t1.md`), reward 1
In both trials the agent asks for the variant choices and the payment method first (t0 turn 19, t1 turns 12 and 19). It asks for confirmation in a separate turn (t0 turn 23, t1 turn 21). The simulator chooses the gift card first and then switches to PayPal and the backpack only (t0 turn 24, t1 turn 22). Both trials change the address before the items, so the order-dependence in 2e/2m is never exercised.

### Task 80, GT run (`80_gt_t0.md`), class B
The GT agent proposes exactly 80_0: T-shirt 5047954489 -> 9354168549, with the $7.99 difference refunded to gift_card_2611937 (turn 11). The simulator objects that it expected to pay the difference (turns 12, 14), even though the scenario only says "Use the gift card". It asks about refund timing and the return obligation (turn 18). Then it refuses to confirm and asks for a supervisor (turn 20), and the agent transfers (turn 21). The agent's statements are correct: the new price is lower, and it declines to guess the timing. The persona line "make the conversation as confusing as possible" explains the confusion, but not the refusal of the stated goal. The pass3 trials succeeded 3/3. Decisive turn: 20.

### Task 82, GT run (`82_gt_t0.md`), class B
The more expensive tablet is 6065192424 ($989.70) in #W9571698, which was paid with gift_card_7250692. The agent states that the refund cannot go to the credit card (turns 18, 20). The simulator claims "I paid with my credit card" (turn 19), a payment fact the scenario does not give. At the trigger it asks for a human (turn 21), although the scenario says: "If refund to credit card is not possible, you become angry and return everything on that order and refund to GC". The agent transfers (turn 22). Decisive turn: 21.

### Task 82, pass3 trials 0 and 2 (`82_haiku_t0.md`, `82_haiku_t2.md`), class B
The agent explains the refund rule correctly in both trials (t0 turns 17, 19, 21; t2 turns 15, 17). The simulator repeats "I paid with my credit card" (t0 turns 18, 20, 22; t2 turns 16, 18). It then asks for a human first and states the scenario's fallback only as a conditional: "If that's not possible, then fine, return everything" (t0 turn 22, t2 turn 18). The agent transfers (t0 turn 23, t2 turn 19). The agent's reading is literal and covered by the policy: the primary request, a credit-card refund, is out of scope, and a transfer was possible. The run fails because the simulator puts the human request ahead of the fallback.

### Task 82, pass3 trial 1 (`82_haiku_t1.md`), reward 1
The agent explanation is the same (turns 17, 19). The simulator applies the fallback directly (turn 20). The agent returns all four items of #W9571698 to gift_card_7250692 (turn 23). The item ids are passed in the order-listing sequence, not the reference sequence, and the DB still matches, so the return hash does not depend on that order.

### Task 83, pass3 trial 0 (`83_haiku_t0.md`), class B (A contributing)
The agent first lists the Mastercard as a possible refund destination (turn 15) and confirms a return to it (turn 17). Its call `return_delivered_order_items` with credit_card_1565124 fails with "Payment method should be the original payment method" (turn 19), and the DB does not change. The agent then states the correct rule and offers gift_card_7250692 (turn 21). The simulator refuses and asks for a human (turn 22), although the scenario says "If refund to credit card is not possible, you become angry and refund to GC". The agent transfers (turn 23). Decisive turn: 22. The agent's wrong offer at turns 15 and 17 contributes.

### Task 83, pass3 trial 1 (`83_haiku_t1.md`), class B (A contributing)
At turn 15 the agent again names the Mastercard as one of two refund options. It corrects this at turn 17. The simulator refuses the gift card twice and asks for a supervisor (turns 18, 20). The agent transfers (turn 21). Decisive turns: 18 and 20.

### Task 83, pass3 trial 2 (`83_haiku_t2.md`), reward 1
The agent mentions the Mastercard together with the gift-card-only rule (turn 15) and refuses the Mastercard (turn 17). The simulator is angry but accepts the gift card (turn 18). The return runs at turn 19. The agent's behaviour matches t0 and t1. Only the simulator's answer at the trigger differs.

### Task 87, GT run (`87_gt_t0.md`), class B
The GT agent proposes 565 Maple Drive, Suite 501, Washington, DC 20307, the address of the processed order #W1994898, for the three pending orders and the profile (turn 15). The simulator replies "No, that's not the right address" (turn 16). It then asks for "a different Washington, DC address" (turn 18) and ends with ###OUT-OF-SCOPE### (turn 20). The scenario says the DC address "is in one of the orders", and this is that address. Decisive turn: 16.

### Task 87, pass3 trial 2 (`87_haiku_t2.md`), class B
The agent asks for the new address (turn 14). The simulator never says that the address is on one of its orders. It raises chat-security concerns that the scenario does not contain (turns 15, 17), declines to continue (turn 19) and stops (turns 21, 23). The user never mentions Washington DC, so the agent has no basis for picking #W1994898 by itself. Decisive turn: 15.

### Task 87, pass3 trials 0 and 1 (`87_haiku_t0.md`, `87_haiku_t1.md`), reward 1
The agent behaves the same way: it asks for the new address (t0 turn 14, t1 turn 8). The simulator answers that the address is on one of its orders (t0 turn 15, t1 turn 9). The agent pulls the address from #W1994898 and applies 87_0 to 87_3 after a yes (t0 turns 18 to 24, t1 turns 19 to 25).

### Task 91, pass3 trial 0 (`91_haiku_t0.md`), class B
The skateboards and the smart watch are collected in one return (turns 14 to 16). The simulator adds the e-reader as a return (turn 17). The agent sets up two returns (turn 18), and the simulator confirms both: Return 1 at turn 19 and Return 2, the e-reader to the credit card, at turn 23. The e-reader return is executed (turn 24). The simulator raises the scenario's exchange preference only at turn 27, after the write. The agent then cannot convert the return into an exchange and transfers (turns 30, 32). Decisive turn: 23.

### Task 91, pass3 trials 1 and 2 (`91_haiku_t1.md`, `91_haiku_t2.md`), reward 1
The agent behaviour is the same: it lists the returns and asks for confirmation. The simulator raises the exchange before confirming (turn 17 in both). The agent explains that an identical unit cannot be exchanged and lists the variants (turn 20). The simulator chooses the 8-inch, Wi-Fi, 32GB e-reader (turn 21). The agent runs 91_1 and 91_0 (turns 24, 26).

### Task 93, GT run (`93_gt_t0.md`), class B
The GT agent finds laptop 2216662955 (15-inch, i5, 32GB, 256GB SSD) in #W4073673. It proposes exactly 93_0: 9844888101 (15-inch, i7, 8GB, 1TB SSD, black), with the $60.78 difference refunded to the Mastercard (turn 14). The simulator claims that the record "doesn't match what I received" (turn 15). The scenario identifies the laptop only as "15-inch, 32GB", which is what the record shows. The simulator then asks for a human (turn 17), and the agent transfers (turn 18). The pass3 trials succeeded 3/3. Decisive turn: 15.

## Per-task cause classes

| task | pass3 | GT | trajectory: class | 1e | 4f | 5c | 5d | 2j |
|---|---|---|---|---|---|---|---|---|
| 64 | 0/3 | 0 | gt: D (B); t0: D; t1: D (B); t2: D | 1 medium (D, 4c) | 0, already in 4c | 0, stable | 1 medium (weak) | 0, judge not involved |
| 66 | 2/3 | 1 | t0: B | 0 | 0, already in 1d/4c | 1 medium | 1 medium | 0 |
| 71 | 1/3 | 1 | t0: A; t1: B (A) | 0 | 0 | 1 medium (t1; t0 agent) | 1 medium | 0 |
| 72 | 2/3 | 1 | t2: B (A) | 0 | 0, 2e/2m not exercised | 1 medium | 1 medium | 0 |
| 80 | 3/3 | 0 | gt: B | 0 (B) | 0 | 0, stable | 1 medium | 0 |
| 82 | 1/3 | 0 | gt: B; t0: B; t2: B | 0 (B) | 0 | 1 medium | 1 medium | 0 |
| 83 | 1/3 | 1 | t0: B (A); t1: B (A) | 0 | 0 | 1 medium | 1 medium | 0 |
| 87 | 2/3 | 0 | gt: B; t2: B | 0 (B) | 0 | 1 medium | 1 medium | 0 |
| 91 | 2/3 | 1 | t0: B | 0 | 0 | 1 medium | 1 medium | 0 |
| 93 | 3/3 | 0 | gt: B | 0 (B) | 0 | 0, stable | 1 medium | 0 |

Primary class of each of the 18 failed trajectories:
- D: 64 gt, 64 t0, 64 t1, 64 t2 (4; all already in static 4c; B contributes in 64 gt and 64 t1)
- A: 71 t0 (1)
- B: 66 t0, 71 t1, 72 t2, 80 gt, 82 gt, 82 t0, 82 t2, 83 t0, 83 t1, 87 gt, 87 t2, 91 t0, 93 gt (13; A contributes in 71 t1, 72 t2, 83 t0, 83 t1)
- C, E: none

GT failures: 64 (D), 80, 82, 87, 93 (all B). Of the five provisional 1e "high" rows in `haiku_pass.csv`, one remains a defect (64, medium) and four become defect=0 (simulator).

## Borderline readings

- 72 t2: B is the primary class because the confirmation request was present at turn 19 and the scenario ties the switch to it. The agent's merged payment and confirmation turn is a procedural slip that the successful trials did not make, so an A reading is possible.
- 71 t1: B is primary (turn 21). The agent also answered and submitted in the same turn (turn 22), after the user had said yes but had asked to hear the total "before you submit".
- 64 5d: the only invented statement is a colour preference (t1 turn 20). The colour choice itself is forced by the 4c ambiguity, so this 5d row is weak and adds no independent failure cause.
- 82 t0 and t2: the agent transferred although the same user turn named an in-scope fallback. The policy permits a transfer when the primary request is out of scope, so the cause is filed as B without A.

## Note on the trajectory count

`results/retail/agent_triage.md` lists 18 failed trajectories for these ten tasks: 64 gt, t0, t1, t2; 66 t0; 71 t0, t1; 72 t2; 80 gt; 82 gt, t0, t2; 83 t0, t1; 87 gt, t2; 91 t0; 93 gt. The assignment named 19. All 18 listed entries and the 11 successful trials of the flipped tasks were read, 29 transcripts in all.
