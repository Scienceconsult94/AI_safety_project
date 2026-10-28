# Trajectory review, retail batch E (checks 1e, 4f, 5c, 5d, 2j)

Scope: tasks 98, 99, 100, 101, 103, 104, 105, 108, 110, 112. Runs `retail_pass3_haiku` (three trials per task, agent `llm_agent`) and `retail_gt_haiku` (one trial, agent `llm_agent_gt`); tau2-bench v2.0.0, commit `989d3285ae669e49503324bdb9981bf14fccedeb`; agent, user simulator and NL judge `claude-haiku-5-5`; stock scorer (`EvaluationType.ALL`). `results/retail/agent_triage.md` lists 21 failed trajectories for these tasks; all 21 were read, plus the 12 successful trials of the flipped tasks (98 t0/t2, 99 t1/t2, 101 t0, 104 t0/t1, 108 t1/t2, 110 t0, 112 t0/t1). Row-level evidence is in `results/retail/review_agent_E.csv`.

Cause classes: A agent slip; B user-simulator deviation; C defensible alternative reading; D reference or scoring problem; E judge error. A second class in brackets contributes. Turn numbers are the `[n]` markers in `results/retail/trajectories/<task>_<run>_t<k>.md`.

Simulator rules used (`tau2-bench/src/tau2/user/guidelines.py`, text mode): follow the scenario strictly; do not make up information that the scenario does not give, treat it as unknown; disclose progressively; stop with `###STOP###` when the goal is met.

## Per-trajectory readings

### Task 98, GT run (`98_gt_t0.md`), class D
The user wants two exchanges (bicycle + puzzle in #W3916020, camera in #W4689314) and the skateboard order cancelled, and "If the agent asks for confirmation, mention that you'd prefer the other card". The GT agent finds the reference items and proposes the Mastercard 8484, the card both orders were paid with and the one the reference uses (turn 22). The user answers "not the Mastercard ending 8484. I'd prefer the other card" (turn 23); the agent confirms the Visa 6791 (turn 24) and writes both exchanges with credit_card_3951670 (turns 26, 28). The cancellation matches (turn 30). Divergence: turn 23. The cause is the known static 4c problem: "the other card" is defined only relative to the card the agent proposes, and the reference fits only an agent that proposes the Visa first. Side note: at turn 7 the user says the skateboard is "in that other order, the one with the camera", a placement the scenario does not give (no effect).

### Task 98, Haiku trial 1 (`98_haiku_t1.md`), class D
The agent lists all three payment methods without proposing one (turns 14, 18). The user resolves "the other card" as "not the one this order was paid with" and asks which card that was (turn 19); the agent answers the Mastercard and books the bicycle + puzzle exchange on the Visa (turns 20, 22). For the camera the user switches to the Mastercard "this time" (turn 29), which matches the reference for that exchange only. At turn 25 the user places the skateboard "in that same order" as the camera (not in the scenario; no effect). Decisive turn: 19, a valid reading of the ambiguous instruction (4c).

### Task 98, Haiku trials 0 and 2 (`98_haiku_t0.md`, `98_haiku_t2.md`), success
In t0 the agent proposes the Visa for both exchanges (turn 21) and the user asks for "the other card, the Mastercard ending 8484" (turn 22): the reference. In t2 the agent lists three methods as in t1 (turn 19) and the user picks the Mastercard "instead of the one you suggested first" (turn 20), although nothing had been suggested. The t1/t2 contrast is the same agent turn read two ways by the simulator. In t0 the user also states that the camera is "in the same order" as the bicycle (turns 1, 9) and, after the writes, asks for a transfer over the cancellation refund (turns 30, 31); neither changes the DB.

### Task 99, Haiku trial 0 (`99_haiku_t0.md`), class B
Same user and orders as task 98; the puzzle should keep the difficulty with "1000 more pieces", art preferred over animals. The user tells the agent "same difficulty, intermediate, but with 1000 pieces" (turn 17). The agent searches 1000-piece intermediate puzzles, finds the art one unavailable and offers fantasy 3112842858 (turn 25); the user accepts a theme the scenario never mentions (turn 26) and the exchange is written (turn 27). The camera exchange and the "do not cancel the whole order" handling match. Decisive turn: 17. The user also claims the bicycle, puzzle and camera are in one order (turn 7).

### Task 99, Haiku trials 1 and 2 (`99_haiku_t1.md`, `99_haiku_t2.md`), success
Both users say "1000 more pieces" (t1 turn 16, t2 turn 16); the same agent search yields the 1500-piece art puzzle 5546244844 (t1 turn 22, t2 turn 24), Visa for both orders, no cancellation. In t1 the user places the skateboard in the bicycle order (turn 9) and in t2 the camera (turn 7); the agent checks the orders in both.

### Task 100, GT run (`100_gt_t0.md`), class D (B contributing)
The user wants the luggage set in red, the skateboard changed to `{'length': '34 inch', 'design': 'custom'}` (pending #W3295833, so an item modification paid by the credit card), and the hiking boots returned. Two available skateboards match the stated options: bamboo 6956751343 ($217.06, the reference, which keeps the current bamboo deck) and plastic 9594745976 ($184.13). The GT agent lists both and asks (turn 24). The user, who has no deck instruction, asks for the difference and a warranty (turns 25, 27) and picks plastic "I'd rather get the $11.02 back" (turn 29). The modification is written with 9594745976 (turn 32); the return to PayPal matches (turn 34). The tool stores the luggage line with the skateboard's options and price (turn 33, the static 1g bug); the agent notices it and transfers (turns 38 to 44), which does not change the DB. Decisive turn: 29.

### Task 100, Haiku trials 0, 1 and 2 (`100_haiku_t0.md`, `_t1.md`, `_t2.md`), class D (B contributing)
All three repeat the GT pattern. The agent lists bamboo and plastic (t0 turn 17, t1 turn 20, t2 turn 19) and refuses to recommend. The user picks plastic as the cheaper one (t0 turn 20, t1 turn 25, t2 turn 22), and 9594745976 is written (t0 turn 23, t1 turn 28, t2 turn 23). All three see the corrupted luggage line and end in a transfer (t0 turn 33, t1 turn 32, t2 turn 33). The simulator also invents history: "I already got burned on this order once" (t0 turn 30), "I've had problems with orders before" (t1 turns 9, 21), "this order has already been wrong once" (t2 turn 20). In 4 runs out of 4, an agent that correctly asks about the unstated deck material ends on the non-reference variant. Static 4c saw the open option but filed it as defect=0.

### Task 101, GT run (`101_gt_t0.md`), class A (B contributing)
The user wants the two-watch order #W4219264 sent to "your New York address (... it's in your other order)", the silicone watch changed to metal white, and the purifier in the purifier+speaker order changed. The profile lists three orders (turn 9). Asked for the address, the user says it is on "my other order" (turn 13); the agent reads only #W6729841 (turn 14). The user then places the address on the purifier and speaker order (turn 17), which the scenario does not say. The agent re-reads that order and twice states "There is no New York address on either of your orders" (turns 18, 22), never reading #W3445693, which holds 144 Lakeview Drive, New York. The purifier is modified as in the reference (turn 28). The user then holds the watch swap so as not to lose the address change (turn 35) and stops (turn 41). Address change and watch swap are missing. Decisive turns: 18 and 22.

### Task 101, Haiku trial 1 (`101_haiku_t1.md`), class A (B contributing)
The agent finds the New York address on #W3445693 and changes the address, then the watch (turns 17 to 25). For the second order the user gives "#W3445693, the one that's already delivered" and calls it the one with the air purifier and speaker (turn 28). The id comes from the agent's own turn 17; the scenario gives no id. The agent had read that the order holds sneakers, a helmet and a purifier, not a speaker (turn 13). It still proposes an exchange there, saying "The Bluetooth speaker on this order will not change" (turn 31), and writes it (turn 33). It corrects itself after the write (turn 35), modifies the right order #W6729841 (turn 43) and transfers about the wrong exchange (turn 45). The extra exchange breaks the hash. Decisive turns: 31 and 33.

### Task 101, Haiku trial 2 (`101_haiku_t2.md`), class B (A contributing)
The user defers the address ("I can give you that one once we get there", turn 9). The agent reads all three orders, #W3445693 included (turns 12 to 16), and swaps the watch first (turn 21). The user then dictates "245 East 62nd Street, Apartment 3B, New York, NY 10065" (turn 26), an address the scenario does not contain. The agent writes it on #W4219264 after the items change (turn 31), against policy l.110 (the tool accepts it; static 2e). The purifier change matches (turn 33). Decisive turn: 26. Agent contributions: it did not offer the New York address it had read, and it changed the address after the items.

### Task 101, Haiku trial 0 (`101_haiku_t0.md`), success
The user says the address is "on my other order, so you can grab it from there" (turn 15). The agent, which had read all three orders (turns 10 to 13), uses 144 Lakeview Drive, changes the address before the items (turns 20, 22) and modifies the purifier (turn 30). Against t2, the difference is the simulator's disclosure.

### Task 103, GT run (`103_gt_t0.md`), class B (A contributing)
The DB matched: both returns (turns 18, 24) and the address and item change on #W4860251 (turns 32, 34). The only unmet item is "Agent should provide the tracking number 286422338955". The user first asks for "the tracking number for the order I cancelled", then withdraws it: "I didn't actually cancel anything, right? ... the tracking number for the return" (turn 37). The agent gives the outbound tracking 682308736931 of #W6239298 and notes that #W1154986 is cancelled (turn 38). The user replies "I didn't cancel that one ... I don't need anything else on it" (turn 39). The scenario says "You want to get the tracking number of your cancelled order". The agent had read 286422338955 on #W1154986 (turn 13) and could have offered it at turn 38. The judge's verdict matches the transcript.

### Task 104, Haiku trial 2 (`104_haiku_t2.md`), class B
All three returns match (turns 18, 24, 30). For pending #W4860251 the user raises only the colour change (turn 33). The agent warns twice that no further change is possible after the item modification (turns 36, 38); the user confirms (turn 39) and the item change is written (turn 40). The user then asks for the Chicago address (turn 43), and the agent correctly refuses under policy l.110 (turn 44). The order keeps the New York address. The agent also writes the profile address with values identical to the stored ones (turn 48), and it gives the tracking number 286422338955 (turn 52), so the assertion is met. Decisive turn: 39. The simulator withheld the second change at the moment the agent announced the lock.

### Task 104, Haiku trials 0 and 1 (`104_haiku_t0.md`, `104_haiku_t1.md`), success
In both trials the user names the colour and the address change in one turn (t0 turn 28, t1 turn 27). t0 writes the address and then the items (turns 33, 37). t1 writes the items and then the address (turns 34, 36), the order policy l.110 forbids, and still scores 1.0 (static 2e).

### Task 105, GT run and Haiku trials 0, 1, 2 (`105_gt_t0.md`, `105_haiku_t0.md`, `_t1.md`, `_t2.md`), class D
In every run the user asks for both kettles as specified (GT turn 9, t0 turn 12, t1 turn 11, t2 turn 12). The agent finds 3761330360 and 9647374798 and computes the $21.10 difference. Because gift_card_7245904, the only payment method, holds $17.00, it refuses (GT turn 16, t0 turn 13, t1 turn 14, t2 turn 13); it also declines a one-kettle exchange followed by a second one later (t1 turn 16, t2 turn 15). The user keeps the order unchanged. The DB equals the initial state, which is the scored target, and the judge correctly marks "Agent should exchange both tea kettles (same style) to the items requested" as unmet. This is the known static 1b/1c/4b/4e problem: no compliant conversation satisfies both the hash and the assertion.

### Task 108, GT run (`108_gt_t0.md`), class B
The user opens with "Everything in it except the tablet" (turn 1), then narrows to "so just the E-Reader" (turn 9). The GT agent proposes the reference return (E-Reader, Jigsaw Puzzle, T-Shirt, $346.93, PayPal; turn 14). The user rejects it: "No, that's not what I asked ... I only want to return the E-Reader" (turn 15). The E-Reader-only return is written (turn 18). The scenario reads "You want to return everything but a tablet". Decisive turn: 15. The judge marked "$346.93" unmet. The agent did say $346.93, but as the total of the proposal the user rejected; the refund it stated for the executed return is $244.02 (turns 16, 20). This verdict is borderline, and the DB fails anyway.

### Task 108, Haiku trial 0 (`108_haiku_t0.md`), class B (A contributing)
After "Everything except the tablet" (turn 1), the user restates the request as "return the E-Reader and keep the tablet" (turn 7). The agent proposes only the E-Reader at $244.02 (turn 14), leaving out the first statement. The user accepts: "$244.02 is what I wanted to know" (turn 15), and the return is written (turn 16). The agent then asks about the puzzle and shirt (turn 18); the user wants them (turn 19), but the order now has status "return requested" and the agent cannot add a second return (turn 20). The run ends in a transfer (turn 22). Decisive turns: 7 and 15 (simulator), 14 (agent).

### Task 108, Haiku trials 1 and 2 (`108_haiku_t1.md`, `108_haiku_t2.md`), success
In both trials the agent lists all three items and the $346.93 total (t1 turns 14 and 16, t2 turn 14). The user confirms, and the reference return is written (t1 turn 20, t2 turn 18).

### Task 110, Haiku trials 1 and 2 (`110_haiku_t1.md`, `110_haiku_t2.md`), class D (judge involved)
The user wants the old-address order moved to the new home, the default address changed to the new home, and the cheapest tablet. The agent finds the new address 760 Elm Avenue, Suite 564 on the tablet order and reports that the profile default already is that address, so no change is needed (t1 turn 13, t2 turn 13). It changes #W1092119's address and the tablet as in the reference (t1 turns 15 and 21, t2 turns 15 and 21). The DB matched. The judge marks "Agent should modify user address" unmet, which is literally true. The cause is the false premise recorded in static 4d.

### Task 110, Haiku trial 0 (`110_haiku_t0.md`), success through a judge error
The agent behaves exactly as in t1 and t2: "your account's default address is already the new place. No change is needed there" (turn 14, again at turn 26), and makes no modify_user_address call. The judge nevertheless marks "Agent should modify user address" as met, and the trial scores 1.0. The verdict on identical agent behaviour flips between trials, so the 1/3 pass rate of this task follows the judge.

### Task 112, Haiku trial 2 (`112_haiku_t2.md`), class B
The user wants the laptop order #W3730488 sent to the NYC address (found on delivered #W3964602), the laptop changed to 9844888101 and the watch changed to black dial with a leather strap. The agent proposes 555 Highland Drive, Suite 872 and notes that the espresso machine in the same order moves too (turn 18). The user refuses: "I don't want that going to New York too" (turn 19), then "let's leave that order at Houston" (turn 21). This is a constraint the scenario does not contain ("You want to modify your laptop order to your NYC address"). Both item changes are written as in the reference (turns 31, 33). The address is missing. Decisive turns: 19 and 21.

### Task 112, Haiku trials 0 and 1 (`112_haiku_t0.md`, `112_haiku_t1.md`), success
In t0 the agent gives the same espresso-machine note (turn 19) and the user accepts (turn 20). The agent then writes the laptop items before the address (turns 21, 23), the forbidden order, and the trial still scores 1.0 (static 2e). In t1 the address is written before the items (turns 25, 27).

## Per-task cause classes

| task | pass3 rewards | GT | failed trajectories read: class | 1e | 4f | 5c | 5d | 2j |
|---|---|---|---|---|---|---|---|---|
| 98 | 1 0 1 | 0 | GT: D; t1: D | 1 medium (D, 4c) | 0 (already in 4c) | 0 (D, see 4c) | 1 medium | 0 (not involved) |
| 99 | 0 1 1 | 1 | t0: B | 0 | 0 | 1 medium | 1 medium | 0 (not involved) |
| 100 | 0 0 0 | 0 | GT, t0, t1, t2: D (B) | 1 medium | 1 medium (deck material) | 0 (stable) | 1 medium | 0 (not involved) |
| 101 | 1 0 0 | 0 | GT: A (B); t1: A (B); t2: B (A) | 0 (A) | 0 (already in 2e) | 1 medium | 1 medium | 0 (not involved) |
| 103 | 1 1 1 | 0 | GT: B (A) | 0 (B) | 0 | 0 (stable) | 1 medium | 0 (matches) |
| 104 | 1 1 0 | 1 | t2: B | 0 | 0 (already in 2e) | 1 medium | 1 medium | 0 (matches) |
| 105 | 0 0 0 | 0 | GT, t0, t1, t2: D | 1 high (D, 1b/1c/4b/4e) | 0 (already in 4e) | 0 (stable) | 0 | 0 (matches) |
| 108 | 0 1 1 | 0 | GT: B; t0: B (A) | 0 (B) | 0 | 1 medium | 1 medium | 0 (matches; GT borderline) |
| 110 | 1 0 0 | 1 | t1, t2: D (judge-gated, 4d); t0 success by E | 0 | 0 (already in 4d) | 0 (judge, see 2j) | 0 | 1 medium |
| 112 | 1 1 0 | 1 | t2: B | 0 | 0 (already in 2e) | 1 medium | 1 medium | 0 (not involved) |

## Calls that rest on a judgement

- 98 5c: the flip between t1 and t2 comes from one agent turn that the simulator read two ways. Both readings of "the other card" are allowed by the scenario, so the row is filed as D (static 4c) and not as a simulator deviation. A stricter reading of 5c ("the flip traces to the simulator") would give defect=1.
- 100: classed D with B contributing, not B alone. The simulator does invent a price preference, but the scenario gives no deck material in all four runs and the reference fixes one of two matching variants, the same shape as the static 98/4c row.
- 104 t2: classed B. The scenario allows piecemeal disclosure ("You like to say one thing at a time"), but the simulator confirmed the item change after two explicit lock warnings, which made its own address request impossible.
- 108 GT 2j: the judge's "unmet" on $346.93 is borderline. The amount was said once, as the total of a proposal the user rejected. The reward is 0 through the DB in any case.
