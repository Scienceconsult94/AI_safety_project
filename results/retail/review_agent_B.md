# Trajectory review, retail batch B (tasks 21, 27, 28, 29, 30, 31, 32, 34; checks 1e, 4f, 5c, 5d, 2j)

Scope: the 17 trajectories that `results/retail/agent_triage.md` lists for these tasks, plus the 10 successful trials of the flipped tasks (21 t0/t1, 28 t0/t1, 29 t2, 30 t0/t2, 31 t2, 34 t0/t2), read for comparison. Runs: tau2-bench v2.0.0 (commit `989d3285`), agent and user simulator both `claude-haiku-5-5`, stock scorer, NL judge `claude-haiku-5-5`; GT = `llm_agent_gt`. Row-level evidence is in `results/retail/review_agent_B.csv`. Turn numbers refer to the `[n]` markers in `results/retail/trajectories/<task>_<run>_t<k>.md`.

Cause classes: A = agent slip; B = user-simulator deviation; C = defensible alternative reading by the agent; D = reference or scoring problem; E = judge error. A second class in brackets contributes.

Simulator framing used below (`tau2-bench/src/tau2/user/guidelines.py`, text mode without user tools = `_TEXT_PLAIN`): strictly follow the scenario; never make up information, and treat anything not in the scenario as unknown; disclose information progressively; continue until the task is complete; emit `###TRANSFER###` when transferred. The text-mode scaffold has no counterpart of the voice-mode rules "Do not end the conversation prematurely" and "verify that ALL items in your scenario instructions have been addressed".

Tool facts used below (`tau2-bench/src/tau2/domains/retail/tools.py`): `exchange_delivered_order_items` and `return_delivered_order_items` both require status exactly `delivered` (l.272, l.735), and each sets a new status, so one delivered order takes either one return or one exchange; `cancel_pending_order` stores the reason (l.234), which enters the hash.

## Per-trajectory readings

### Task 21 (exchange shoes to 4107812777 with the gift card; at final confirmation add 1656367028 -> 1421289881; ask for the gift-card balance)

**21_haiku_t2, reward 0 (db_match False, assertion "$44.08" unmet), class B.** All orders are pending or processed, so the agent correctly turns the "exchange" into a pending-order item modification (turns 14, 16). The user raises 1656367028 early as a possible shoe id (turn 15), which the scenario ties to the final confirmation. At the confirmation the user adds the keyboard request (turn 23); the agent combines both into one call, total $41.92 to gift_card_4332117, "$44.08 would remain" (turn 26). The user then hesitates (turn 27) and declines the keyboard swap with an invented reason about the 80% size (turn 29). The agent modifies only the shoes (turn 32) and reports a balance of $77.72 (turns 30, 34). Decisive turn: 29, which contradicts "also want to change item ID 1656367028 to item ID 1421289881".

**21_haiku_t0, reward 1.** Same agent path: shoe proposal (turn 20), keyboard added at confirmation (turn 21), one combined call in the reference pair order (turn 27). The returned order shows item 4107812777 with keyboard options at $268.77 (tool bug 1g); the agent says so, states the balance $44.08 (turn 31) and transfers (turn 33). The target state carries the same corruption, so the reward is 1.

**21_haiku_t1, reward 1.** Same as t0: the user adds the keyboard and the product-id hint at the confirmation (turn 19), one combined call (turn 26), the agent reports the corrupted shoe line and $44.08 (turn 28), transfer (turn 30).

### Task 27 (return hose and backpack and exchange the boots to the waterproof variant, all on #W7181492; if only one is possible, prefer the exchange)

**27_gt_t0, reward 0 (db_match False), class A.** The GT agent's reference holds only the exchange 8118291112 -> 8277474082. It nevertheless proposes both actions and says the order "qualifies for a return and an exchange" (turn 15). The user accepts both (turn 16). The return runs first (turn 17) and sets "return requested"; the exchange fails with "Non-delivered order cannot be exchanged" (turn 20). The agent cannot undo the return; the user asks for a human (turns 22, 24); transfer (turn 25). Decisive turn: 15 (the one-of-two constraint is never stated, so the scenario's trigger "if the agent says they can only do one" never fires).

**27_haiku_t0, reward 0, class A.** Same proposal (turn 17), adding the wrong claim "an order can only have one exchange and one return". Return executed (turn 19); the agent then declares the exchange impossible without trying (turn 21). The user says "I was clear that if you could only do one, I wanted the exchange" (turn 22), which had not been said before; no effect. Transfer (turn 23).

**27_haiku_t1, reward 0, class A.** Same: both proposed (turn 17), return (turn 19), exchange error (turn 22), transfer (turn 25).

**27_haiku_t2, reward 0, class A.** Same: both proposed (turn 17), return (turn 19), exchange error (turn 22); the agent admits it should have pointed out the conflict before the confirmation (turn 23); transfer (turn 25).

### Task 28 (return skateboard; then hose and backpack; then keyboard and bed; do not cancel the pending order; ask for the total, $918.43)

**28_haiku_t2, reward 0 (db_match False, assertion "$918.43" unmet), class A.** The agent groups the items correctly by order (turn 15) and the user declines the whole-order cancellation (turn 16). After the skateboard return (turn 19), the agent proposes the hose alone for #W7181492 (turn 21); the user agrees and asks for the backpack next (turn 22). The agent returns only 5753502325 (turn 23); the order becomes "return requested" and the backpack return is impossible (turn 25). The user insists and asks for a human (turns 26, 28) while the keyboard and bed returns are still open; transfer (turn 29). No total is ever stated, so the judge's "unmet" is correct. Decisive turn: 21/23 (one return split into two). The escalation at turn 28 is borderline for the simulator, but it follows an agent-made dead end for which the scenario gives no instruction.

**28_haiku_t0, reward 1.** Three return calls, the second with [5753502325, 9851293632] (turns 19-23); total $918.43 via `calculate` (turns 27, 29); pending order untouched.

**28_haiku_t1, reward 1.** Same three calls (turns 17-21); total $918.43 (turn 23).

### Task 29 (exchange the skateboard for a shorter bamboo one: list all options with prices and take the most expensive; exchange the received hose for the type in the pending order, 5206946487)

**29_haiku_t0, reward 0 (db_match True, assertion unmet), class A.** The agent lists only two of the three available 28-inch bamboo variants, $208.60 and $189.57, omitting 6843647669 (graphic, $180.10) (turn 17). Asked whether those are all (turn 18), it says they are "the only 28-inch bamboo options available" (turn 21). Both exchanges match the reference (turns 23, 25), so the hash matches; the assertion "prices ... $180.10, $189.57, and $208.60" is correctly unmet. The user's opener "I got a garden hose that's not the one I ordered" (turn 1) is an invented motive; no effect.

**29_haiku_t1, reward 0 (db_match True, assertion unmet), class A.** Same omission (turn 17) and the same wrong "only two" answer (turn 21); both exchanges correct (turns 23, 27; the order hose-first does not change the hash, static 2h). Same invented hose motive (turns 1, 18).

**29_haiku_t2, reward 1.** The agent lists all three 28-inch bamboo prices (turn 17). The user then rejects the correct 50ft black vinyl hose ("isn't the right one", turn 18) although the agent proposed no other item id, which is the scenario's only trigger for that rejection; the user retracts at turn 22. Both exchanges done (turns 23, 27).

### Task 30 (damaged tablet: tracking number first; exchange for the same item, else return; if returned, cancel the charger "because it goes with the tablet"; return the sneaker)

**30_haiku_t1, reward 0 (db_match False), class B.** Tracking number given (turn 16); same variant unavailable, so a return (turns 20, 22), as in the reference. For the charger the agent asks for the reason (turn 26) and the user answers "Ordered by mistake" (turn 27); the agent cancels with that reason (turn 28). Sneaker return correct (turn 34). The only difference from the reference is the cancel reason (reference 30_8: "no longer needed"), which enters the hash. Decisive turn: 27, which contradicts the stated motive. The cracked-screen detail (turn 1, also t0 and t2) is an embellishment of "damaged" with no effect.

**30_haiku_t0, reward 1.** Same agent path; the user answers "No longer needed, since the tablet is going back" (turn 29).

**30_haiku_t2, reward 1.** Same agent path; the user answers "No longer needed" (turn 28).

### Task 31 (lost tablet: tracking number; try for a refund or reorder; if not, cancel the charger; cancel the boot but keep the kettle, else leave that order alone; return the sneaker)

**31_haiku_t0, reward 0 (db_match False), class C (A contributing).** Tracking number and the return/exchange options are given (turn 15). The user refuses both and asks "Can you help with that, or not?" (turn 16). The agent calls `transfer_to_human_agents` at once (turn 17), and the episode ends (turn 20) before the charger, boot/kettle and sneaker requests come up. The transfer is supported by policy.md ("transfer ... if and only if the request cannot be handled within the scope of your actions"; a refund for a lost item is not one of the agent's actions), while the reference assumes a refusal and the "if not" branch. The agent's contribution: it neither answered the question nor asked whether anything else was needed before transferring. Decisive turn: 17.

**31_haiku_t1, reward 0 (db_match False), class A (B contributing).** The user asks for a refund for the lost tablet (turn 17). The agent answers with a return of #W2692684, presented as the refund, without saying that the tablet must be sent back (turn 18); the user accepts (turn 19) and the return is filed (turn 20), a write that is not in the reference. The rest matches the reference: charger cancelled with "no longer needed" although the user said "Ordered by mistake, I guess ... Either one works" (turns 25, 26); boot/kettle order left alone (turn 30); sneaker returned (turn 34). Decisive turns: 18 (agent) and 19 (the simulator accepts returning an item it says it lost).

**31_haiku_t2, reward 1.** The agent says return and exchange "both require the item to be sent back" (turn 18); the user declines and moves on (turn 19); charger cancelled with "no longer needed" (turn 22), boot/kettle order untouched (turn 26), sneaker returned (turn 30). The user says the tablet was lost "on the way" (turn 17), which contradicts "you just received"; no effect. The later transfer about the missing e-mail (turn 36) comes after all writes.

### Task 32 (lost tablet: tracking number; try for a refund or reorder; if not, cancel the charger, cancel the boot and kettle, return the sneaker)

**32_gt_t0, reward 0 (db_match False), class B (A contributing).** Tracking number given; refund or replacement refused; a transfer is offered (turns 14, 16). The user accepts and defers the rest: "I have a few other orders I need to cancel too, but I'll get to those once this tablet thing is handled" (turn 17). The GT agent, whose reference lists both cancellations and the return, transfers anyway (turn 18). No write. Decisive turn: 17 (the scenario says "If not, cancel the charger ...").

**32_haiku_t0, reward 0 (db_match False), class B.** Charger cancelled with "no longer needed" (turn 22), matching the reference. For the boots and kettle, which share #W5481803, the user says "I don't want to cancel the kettle. I only want the boots cancelled" (turn 27) and keeps the order (turn 29), against "Also cancel the boot and kettle". Sneaker return correct (turn 30). Decisive turn: 27.

**32_haiku_t1, reward 0 (db_match False), class B (A contributing).** Tracking number given (turns 16, 18); refund or reorder refused and a transfer offered (turn 20). The user accepts and adds "I also need to cancel a few other things while I'm at it" (turn 21); the agent transfers without handling them (turn 22). Decisive turn: 21.

**32_haiku_t2, reward 0 (db_match False), class B.** Tracking number and the refusal (turns 16, 18); the user accepts the offered transfer (turn 19); transfer (turn 20). The remaining requests are never raised. Decisive turn: 19.

### Task 34 (DB-only basis; pending #W1845024 ships to Seattle; partial cancellation impossible, so change the address to "your NYC place"; the user lives in 10108)

**34_gt_t0, reward 0 (db_match False), class B (D contributing).** Partial cancellation refused (turn 18), and the agent proposes the profile address 224 Elm Street, Suite 491, New York, NY 10108, which is the reference address (34_5). The user rejects it: "I never gave you 224 Elm Street" (turn 19), "I haven't lived there in a while" (turn 21), "that's not where I'm staying" (turn 23). The order stays in Seattle; the conversation ends with the $1,093.34 figure for a later return (turn 28). Decisive turns: 19 to 23. The simulator invents that the address is not its own (known_info: "living in the Big Apple in 10108"); the scenario also never gives it the street it must confirm.

**34_haiku_t1, reward 0 (db_match False), class B (D contributing).** Same proposal (turn 18); "No, that's not my address. I never gave you a street address" (turn 19); the user does not know the street (turn 21), asks the agent to note that 224 Elm Street "isn't mine" and asks for a supervisor (turn 23); transfer (turn 24), no write. Decisive turn: 19.

**34_haiku_t0, reward 1.** Same proposal (turn 18); the user accepts: "the address you read back is the right one" (turn 19); address changed (turn 20).

**34_haiku_t2, reward 1.** The agent offers the default New York address (turn 14); the user accepts (turn 15); address changed (turn 16). The user later says "I thought I paid by card" (turn 21), which is invented; no effect.

## Verdicts per task and check

| task | pass3 | GT | 1e | 4f | 5c | 5d | 2j | classes of failed trajectories |
|---|---|---|---|---|---|---|---|---|
| 21 | 1 1 0 | 1.0 | 0 | 0 (already in 1g) | **1** | **1** | 0 | t2 B |
| 27 | 0 0 0 | 0.0 | 0 (A) | 0 | 0 (0/3) | 0 | 0 (not involved) | GT A, t0 A, t1 A, t2 A |
| 28 | 1 1 0 | 1.0 | 0 | 0 | 0 (agent) | 0 (t2 borderline) | 0 | t2 A |
| 29 | 0 0 1 | 1.0 | 0 | 0 | 0 (agent) | **1** | 0 | t0 A, t1 A |
| 30 | 1 0 1 | 1.0 | 0 | 0 | **1** | **1** | 0 (not involved) | t1 B |
| 31 | 0 0 1 | 1.0 | 0 | **1** | 0 (agent) | **1** | 0 (not involved) | t0 C/A, t1 A/B |
| 32 | 0 0 0 | 0.0 | 0 (B) | 0 | 0 (0/3) | **1** | 0 (not involved) | GT B/A, t0 B, t1 B/A, t2 B |
| 34 | 1 0 1 | 0.0 | 0 (B) | **1** | **1** | **1** | 0 (not involved) | GT B/D, t1 B/D |

Counts of defect=1: 1e 0 of 8; 4f 2 of 8 (31, 34); 5c 3 of 8 (21, 30, 34); 5d 6 of 8 (all except 27, 28); 2j 0 of 8. The three provisional 1e rows (27, 32, 34: defect=1 high, mechanical) are replaced by defect=0: the GT failures trace to the agent (27) and to the simulator (32, 34), not to an unreachable reference.

Judge (2j): in the three tasks where the judge gates the reward (21, 28, 29; task 34 is DB-only and 27, 30, 31, 32 have no assertions), every live verdict on the read trajectories matches the transcript: the two judge-only failures of task 29 are real agent omissions of the $180.10 option, and the "$44.08" and "$918.43" failures of 21 t2 and 28 t2 come with a missing statement.

## Comparison with the static rows

- **Corroborated:** 21/1g (the corrupted shoe line is visible to the agent in t0 turn 31 and t1 turn 28; the reward is unaffected); 28/4a-4e and 29/4a-4e (no task-side problem; failures are agent slips); 27/4a ("the return ... is impossible after the exchange"; the runs show the mirror case, the exchange is impossible after the return).
- **Not exercised:** 21/2h and 21/4c (all three trials list the pairs in the reference order); 32/4c (no run reaches the boot/kettle cancellation with a reason chosen by the user).
- **New:** 31/4f (transfer clause vs a refuse-and-continue reference) and 34/4f (the reference writes a street that the scenario withholds from the user). Static 30/4c (the reason is implied by the motive) is kept: the one run that chose "ordered by mistake" is a simulator deviation, and two runs show the simulator mapping the motive to "no longer needed".

## Observations beyond the checklist

1. **Task 27 rewards the lucky order.** Both delivered-order tools require status `delivered`, so an agent that proposes both actions and happens to run the exchange first ends in the reference state (the return then fails), while running the return first scores 0. All four runs ran the return first, in the order the user named the requests.
2. **Lost-tablet tasks (31, 32) hinge on the transfer clause.** In 4 of the 6 failures of these two tasks the conversation ends in a transfer before the remaining requests (31 t0 unprompted; 32 GT, t1, t2 offered and accepted). The text-mode simulator scaffold lacks the "do not end prematurely / verify all items" rules that the voice scaffold carries, which fits the simulator accepting transfers with requests still open.
3. **Simulator embellishments without reward effect** recur across the batch: "the hose is not the one I ordered" (29, all trials), "cracked screen" (30, all trials), "lost it on the way" (31 t2), "I paid by card" (34 t2).
4. **The agent repeatedly makes parallel read calls** (four or five `get_order_details` in one turn, e.g. 27 GT turn 8, 32 t0 turn 10) against the policy's "at most one tool call at a time". This has no DB footprint and is not scored.
