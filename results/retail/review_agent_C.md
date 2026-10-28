# Trajectory review, retail batch C (checks 1e, 4f, 5c, 5d, 2j)

Scope: tasks 38, 39, 43, 46, 49, 51, 52, 55, 59 of tau2-bench v2.0.0 retail (commit `989d3285ae669e49503324bdb9981bf14fccedeb`); agent and user simulator `claude-haiku-5-5`, stock scorer, NL judge `claude-haiku-5-5`. Read: the 21 trajectories that `results/retail/agent_triage.md` lists for these tasks, plus the 8 successful trials of the flipped tasks (39 t2, 43 t0, 46 t1, 51 t0, 51 t2, 55 t0, 55 t1, 59 t0). Per-run judge verdicts and action matches were taken from `reward_info` in `results/retail/runs/*/results.json`. Row-level evidence is in `results/retail/review_agent_C.csv`.

Cause classes: A = agent slip; B = user-simulator deviation; C = defensible alternative reading; D = reference or scoring problem; E = judge error. A second class in brackets contributes. Turn numbers are the `[n]` markers in `results/retail/trajectories/<task>_<run>_t<k>.md`. The simulator runs under the text, no-tools scaffold of `tau2-bench/src/tau2/user/guidelines.py` (use only scenario facts, treat everything else as unknown, keep going until the task is complete).

## Per-trajectory readings

### Task 38, GT run (`38_gt_t0.md`), class D
The user cannot pay a $1,166.98 order with $950 of credit and walks through the scenario's four branches: split payment (refused, one payment method; [16]), the most expensive item (Action Camera $481.50, no single-item cancel; [18]), the cheapest options (agent reads all five products, lowest total $1,130.85; [30]), then cancellation. The agent names both allowed reasons at [16], [18] and [30]; the user answers "ordered by mistake" I guess ([31]); the agent confirms and cancels with that reason ([34]). The reference cancels with "no longer needed" (38_10). Both nl_assertions are met; the DB differs only in `cancel_reason`. The scenario states no reason ("so that you can order again"), so the reference fixes one of two compliant end states (static 38/4c).

### Task 38, Haiku trials 0, 1, 2 (`38_haiku_t0.md`, `_t1.md`, `_t2.md`), class D
Same course as the GT run. The reason "ordered by mistake" comes from the user at t0 [25], t1 [30] (after the agent asks which reason applies, [29]) and t2 [31] (asked at [30]); the cancel at t0 [28], t1 [31], t2 [32] carries it. All branch answers are correct; t0 [24] misdescribes two of the cheapest variants (T-shirt "red, XXL, crew neck" for the red L v-neck at $46.66; desk lamp "silver, low" for the black medium at $135.24) without effect on the total or the score.

### Task 39, GT run (`39_gt_t0.md`), class B (A contributing)
The user moved from Florida to Phoenix, wants the default address updated from the address on the recent order (which the scenario says holds the current address and which the user will not read out), and asks for the cheapest T-shirt. Authentication with the old zip works ([4]). At [9] the user says "my old address is on my recent order, but I'd rather not read that out, so you can pull it from there"; the agent replies that it will not use the order address "since that's your old address" ([10]) without reading #W5285031, which ships to 157 Oak Street, Suite 258, Phoenix, AZ 85033. The T-shirt answer ($46.66, [16]) is correct. The user stops at [21] with the address unchanged. Decisive: [9] (the simulator turns "current" into "old") and [10] (the GT agent, which saw get_order_details and the reference write, does not look).

### Task 39, Haiku trial 0 (`39_haiku_t0.md`), class B (A contributing)
Same pattern: [9] "my old address should be on my most recent order, if that helps you find my account"; [10] the agent declines to use "the old address on your most recent order"; [11] the user confirms it means the old address and will not read it out. T-shirt $46.66 at [16]; stop at [19] without the update.

### Task 39, Haiku trial 1 (`39_haiku_t1.md`), class B (A contributing, borderline)
The user gives city, state, zip and country but not the street ([9]); the agent asks for the street ([10]). At [17] and [19] the user says the street is on the recent order confirmation and that it will "dig it out" and come back; the agent does not offer to read the order. The user stops at [23]. The simulator mentions the order but treats it as its own lookup and ends with the main request open; the agent misses the pointer.

### Task 39, Haiku trial 2 (`39_haiku_t2.md`), success
At [9] the user asks what the agent needs "to pull up my recent order, so I can check the new address there"; the agent reads #W5285031 ([10]), shows the Phoenix address ([12]), the user confirms without reading it out ([13], [15]), and the agent writes the reference address ([16]). T-shirt $46.66 at [24]. Reward 1.0.

### Task 43, Haiku trial 1 (`43_haiku_t1.md`), class B (A contributing)
The user wants the shipping address, tracking number and transit status of the order sent to the daughter, the tablet storage, and lastly a default-address change to the daughter's address. The agent reports the Chicago address ([15]), tracking 840887978435 ([17]) and status delivered, and offers a transfer for the missing delivery ([15], [17]). The user accepts ([18]), asks for the tablet storage first, gets 64GB ([19]) and is transferred in the same turn ([19]; message and tool call together). The address change is never raised. All three nl_assertions are met; the DB lacks 43_4.

### Task 43, Haiku trial 2 (`43_haiku_t2.md`), class B (A contributing)
The agent reports both orders with tracking, Chicago address and 64GB ([13], [15]) and offers an exchange or a transfer ([15]). The user invents "I was pretty sure I ordered the bigger one, like 256GB" and asks for a transfer ([16]); transfer at [17]. The address change is never raised.

### Task 43, Haiku trial 0 (`43_haiku_t0.md`), success
The agent gives all facts at [13] and offers a transfer at [15], as in t1 and t2. The user raises the address change at [14], before asking for the investigation; the agent writes 43_4 ([17]) and then transfers ([19]). Reward 1.0.

### Task 46, GT run (`46_gt_t0.md`), class B (A contributing)
The user returns the air purifier and the robotic vacuum from #W9502127 and must ask for a refund within 3 days and the refund total, then, after the return, the total paid for the remaining items. The GT agent runs the scripted wrong lookups itself ([6], [8], [10]) without asking for the order id, finds the order, gets "the robotic one" ([13]), quotes $1,126.04 ([16]) and declines the 3-day promise. The user asks for a supervisor ([17]), refuses to confirm until someone guarantees 3 days ([19]) and is transferred ([20]). The return is never filed; assertion 2 ($1,497.65) is never reached. Decisive: [17] and [19]; the scenario continues "After the return is complete", so the return is meant to go through.

### Task 46, Haiku trial 0 (`46_haiku_t0.md`), class A (B contributing)
Scripted order-id sequence ([7], [13]), robotic vacuum and air purifier ([17]), confirmation and the reference return ([19], [20]); DB matches. The agent declines the 3-day promise and offers a transfer ([24]). At [25] the user accepts and in the same message asks for the total paid for the remaining items; the agent transfers at [26] without answering. $1,497.65 appears only inside the transfer summary argument, not in a message to the user. The judge's "unmet" on assertion 2 is correct.

### Task 46, Haiku trial 2 (`46_haiku_t2.md`), class B (A contributing, borderline)
Return filed as in the reference ([18]); DB matches. At [21] the user asks for "the total I paid for the remaining items in the same order" and then narrows it: "The canister vacuum cleaner is still with me, so what was the total I paid for that one?" The agent answers $622.12 for the canister vacuum and says the payment cannot be split by item ([22]); the patio umbrella and dumbbell set are not mentioned. The user then asks for a supervisor ([23]); transfer at [24]. The narrowing at [21] is the simulator's; the agent still had the full question in the same turn.

### Task 46, Haiku trial 1 (`46_haiku_t1.md`), success
Same agent course as t0 and t2 up to the return ([20]). At [23] the user asks the remaining-items question as scripted; the agent lists the three items and gives $1,497.65 ([24]). Reward 1.0.

### Task 49, GT run (`49_gt_t0.md`), class B (A contributing)
The user wants the IPX7 earbud exchanged for "the cheapest earbud item from the rest of that order" (1646531091, IPX4, $232.49 per the reference). The agent reads all orders and the product ([10]-[17]) and at [18] lists six catalogue variants without IPX7, describing #W3470184 as also holding "a Water Bottle and a Bookshelf" (the two other earbuds, 1646531091 and 6452271382, go unmentioned). The user picks "Blue, 8-hour battery, IPX4 at $226.49" ([19]), justified by "the same IPX4 water resistance as my other earbuds", a fact it was never told. The agent confirms and exchanges to 8555936349 ([22]). Decisive: [19] against the scenario's selection rule, made easier by [18].

### Task 51, Haiku trial 1 (`51_haiku_t1.md`), class B (A contributing)
The user returns the digital camera, giving #W8855135 as an uncertain order id. #W8855135 is pending and holds other items ([9]). The user invents "I didn't order an air purifier or hiking boots or any of that" ([10]). The agent finds the camera in #W4689314 and files the reference return to the original Mastercard ([15]). It then offers, unasked, to cancel #W8855135 "if you didn't place that order" ([17]); the user accepts with "ordered by mistake" ([18]); cancel at [19]. The extra cancellation alone breaks the DB match. The invented claim also appears in t0 ([11]) without effect; the agent's offer is what differs.

### Task 51, Haiku trials 0 and 2 (`51_haiku_t0.md`, `51_haiku_t2.md`), success
Both reach the reference return ([16]). In t0 the user makes the same invented claim ([11]) and the agent only searches for the camera. In t2 the user afterwards invents an unrecognised account e-mail and asks for a transfer ([21]-[23]); the transfer follows the return and does not affect the score.

### Task 52, GT run (`52_gt_t0.md`), class D
The user wants the camera (24MP, 3x, SD card) exchanged for the maximum zoom with "all the other specifications ... the same", paying by PayPal. The agent proposes the reference item 9228757377 (30MP, 10x, SD) ([14]); the user rejects it because the resolution changes ([15]). The agent confirms that no available 24MP SD model has more zoom and offers 4326528037 (24MP, 5x, CF) or 9228757377 ([16]); the user declines both and asks for a supervisor ([17]); transfer at [18]. Known reference conflict (static 52/4a): no variant meets both stated constraints, and the reference silently gives up "same resolution".

### Task 52, Haiku trials 0, 1, 2 (`52_haiku_t0.md`, `_t1.md`, `_t2.md`), class D
Same course: the agent proposes 9228757377 (t0/t1/t2 [17]), the user rejects 30MP ([18]), the agent confirms no 24MP/SD alternative ([19]); t0 ends with no exchange ([24]), t1 and t2 with a transfer after a supervisor request ([20], [21]). No write in any run.

### Task 55, Haiku trial 2 (`55_haiku_t2.md`), class B
The user, under financial strain, must cancel all pending orders and "return everything from the orders that have been delivered" after the agent lists the items. Authentication through the second e-mail works ([4], [6]); both pending orders are cancelled with "no longer needed" ([21], [23]), as in the reference. The agent lists the delivered items with prices ([19]). The user then returns only the air purifier and smart watch of #W4597054 ([20], [26], [28]; return at [29]), keeps the coffee maker and water bottle, says it does not remember buying the hiking boots, asks for a partial refund on them and leaves #W7773202 untouched. Decisive: [20]-[28], against the scenario's "return everything".

### Task 55, Haiku trials 0 and 1 (`55_haiku_t0.md`, `55_haiku_t1.md`), success
Same agent course (verification, full listing, cancellations, ask which items to return). The user asks to return everything (t0 [27], t1 [20]); both reference returns follow. Reward 1.0.

### Task 59, Haiku trial 1 (`59_haiku_t1.md`), class B
Two pending orders: cancel "the older order" if the agent cannot guarantee processing within 5 days, and re-address #W2702727 to Springfield. Only #W8268610 (desk lamp) is consistent with keeping #W2702727 for the address change; the scenario does not name the older order. At [9] the user calls #W2702727 the order "placed much earlier in the year". The agent declines a 5-day guarantee and asks which order to cancel ([13]), as in t0. The user confirms the address change on #W2702727 ([14]; write at [15]) and then the cancellation of the same order ([18]; cancel at [19]), keeping the desk lamp order. The judge correctly marks "refund for the cancelled desk lamp order is $164.28" unmet; "$625.60" is met ([13]).

### Task 59, Haiku trial 2 (`59_haiku_t2.md`), class A (B contributing)
The user's opening names both orders without saying which is older ([1]). The agent's summary labels #W2702727 "(placed earlier in the year)" ([10]) and in the same message says its tools show no order dates. The user adopts the label ([11]), cancels #W2702727 ([13]; cancel at [14], announced in the same turn as the tool call), then moves the address change to #W8268610 ("I'm actually thinking about #W8268610 for the new address", [17]); write at [20]. Decisive: [10] (invented fact by the agent) and [17] (the simulator abandons "For order #W2702727, you intend to switch the shipping address").

### Task 59, Haiku trial 0 (`59_haiku_t0.md`), success
The agent asks which order to cancel and wrongly proposes the address change for #W8268610 ([13]); the user corrects it, assigning the address change to #W2702727 and the cancel to #W8268610 ([14]). Both reference writes follow ([17], [19]); both assertions met ([15], [21]). Reward 1.0.

## Verdicts per task and check

| task | pass3 | 1e (GT) | 4f | 5c | 5d | 2j | classes of failed trajectories |
|---|---|---|---|---|---|---|---|
| 38 | 0/3 | **1** medium (D) | 0 (already in 4c) | 0 (stable) | 0 | 0 | GT D, t0 D, t1 D, t2 D |
| 39 | 1/3 | 0 (B, A) | 0 | **1** medium | **1** medium | 0 | GT B/A, t0 B/A, t1 B/A |
| 43 | 1/3 | 0 (GT 1.0) | 0 | **1** medium | **1** medium | 0 | t1 B/A, t2 B/A |
| 46 | 1/3 | 0 (B, A) | 0 | **1** medium (t2) | **1** medium | 0 | GT B/A, t0 A/B, t2 B/A |
| 49 | 3/3 | 0 (B, A) | 0 | 0 (stable) | **1** medium | n/a | GT B/A |
| 51 | 2/3 | 0 (GT 1.0) | 0 | 0 (agent) | **1** medium | n/a | t1 B/A |
| 52 | 0/3 | **1** high (D) | 0 (already in 4a) | 0 (stable) | 0 | n/a | GT D, t0 D, t1 D, t2 D |
| 55 | 2/3 | 0 (GT 1.0) | 0 | **1** medium | **1** medium | n/a | t2 B |
| 59 | 1/3 | 0 (GT 1.0) | 0 (already in 4a) | **1** medium (t1) | **1** medium | 0 | t1 B, t2 A/B |

2j: no class E in this batch. Every judged assertion (tasks 38, 39, 43, 46, 59) agrees with the transcript, including the unmet "$1,497.65" in 46 GT/t0/t2 (never told to the user; in t0 only inside a tool argument) and the unmet desk-lamp refund in 59 t1/t2 (that order was not cancelled).

Severity notes. 38/1e is medium because the reference becomes reachable whenever the simulator happens to say "no longer needed". 52/1e is high because the reference requires the user to give up a constraint the scenario states; a simulator that keeps the scenario never confirms 9228757377 (4 of 4 runs refuse it). The underlying task-level row 52/4a stays medium.

## Undecided or borderline

- 46 t2: filed B (A contributing). The narrowing at [21] is the simulator's, but the same message also carries the full question, which the agent left unanswered. If read as A, 46/5c would fall to 0 (t0 is A as well).
- 51 t1: filed B (A contributing) with 5c = 0, because the only difference from the successful t0 is the agent's unasked cancel offer at [17]; the simulator's invented claim is the same in t0 [11].
- 39 t1: filed B (A contributing). The simulator mentions the recent order but frames it as its own lookup and ends the conversation; the agent does not offer to read the order. 39/5c holds on t0 alone in any case.
- 59 t2: filed A (B contributing). The agent invents the order age at [10]; the simulator adopts it and then moves the address change to the other order ([17]) against the scenario.
- 38: choosing "ordered by mistake" when the agent asks is not counted as a simulator invention (the policy requires a reason, the scenario gives none); if it were, 38/5d would become 1.

## Observations beyond the checklist

- The scenario wording of task 39 ("Your address is still the old one ... Your current address should be in your recent order") was read as "the old address is on the order" in 2 of 4 runs. It is filed as simulator deviation; a wording that names the new address explicitly would remove the ambiguity.
- In task 59 the scenario never names the older order; static 59/4a already notes that it follows only from the address request. Runs t1 (simulator) and t2 (agent label) both resolve it the wrong way.
- Unscored policy deviations by the agent appear in most runs: several tool calls in one turn (e.g., 38 t0 [20], 43 t1 [10], 49 GT [10], 52 t0 [10], 55 t1 [27]) and a message sent with a tool call in the same turn (43 t1 [19], 55 t2 [10], 59 t2 [14]), against "at most make one tool call at a time ... should not respond to the user at the same time". 46 GT [12] mentions "an existing gift card on your profile" for a user without one. None of these changes a reward here.
