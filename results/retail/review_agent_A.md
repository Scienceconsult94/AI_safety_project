# Trajectory review, retail batch A (tasks 0, 1, 5, 9, 11, 15, 16, 19; checks 1e, 4f, 5c, 5d, 2j)

Scope: the 12 trajectories listed for these tasks in `results/retail/agent_triage.md` (tau2-bench v2.0.0, commit `989d3285`, retail; agent and user simulator `claude-haiku-5-5`; stock scorer `ALL`; NL judge `claude-haiku-5-5`), plus the 10 successful trials of the flipped tasks 0, 1, 5, 9, 11 and 15. Tasks 16 and 19 have no failed Haiku trial (3/3), so only their GT runs were read. Row-level evidence: `results/retail/review_agent_A.csv`.

Cause classes as in `retail/review_agent_brief.md`: A agent slip, B user-simulator deviation, C defensible alternative reading, D reference or scoring problem, E judge error. Turn numbers are the `[n]` markers in `results/retail/trajectories/<task>_<run>_t<k>.md`. Policy line numbers refer to `tau2-bench/data/tau2/domains/retail/policy.md`. The user simulator runs on the text template without tools (`_TEXT_PLAIN` in `tau2-bench/src/tau2/user/guidelines.py`): follow the scenario strictly, never make up information that the scenario does not give, disclose progressively, emit `###STOP###` when the goal is met and `###OUT-OF-SCOPE###` when the scenario does not cover the situation.

## Per-trajectory readings

### Task 0, Haiku trial 0 (`0_haiku_t0.md`), reward 0, class D
The user wants two exchanges on delivered order #W2378156: the keyboard to clicky (fallback: no backlight if clicky/RGB/full size is missing) and the thermostat to "compatible with Google Home instead of Apple HomeKit". The agent finds the clicky/no-backlight/full-size keyboard 7706410293 and writes that the catalog has no "Google Home" option, the closest being Google Assistant black 7747408585 (turn 14). The user asks whether the Google Assistant model works with Google Home and says it would rather keep the HomeKit one otherwise (turn 15). The agent answers that it can only state what the catalog lists and cannot confirm Google Home (turn 16), which is what policy.md l.18 requires. The user chooses the keyboard-only exchange (turn 17), and the agent exchanges only 1151293680 -> 7706410293 (turn 20), while the reference 0_4 exchanges both items. Decisive turns: 14 to 17. The scenario names an option value that the catalog does not have, so once the gap is raised, a policy-compliant agent cannot close it and the simulator has no instruction to accept the substitute.

### Task 0, Haiku trials 1 and 2 (`0_haiku_t1.md`, `0_haiku_t2.md`), reward 1
In t1 the agent writes "Google Home is listed as 'Google Assistant' in our system" (turn 14), which the catalog does not state; the user accepts and the exchange equals 0_4 (turn 16). In t2 the agent lists every available variant without comment (turn 12) and the user picks Google Assistant black (turn 13); the exchange equals 0_4 (turn 16). The three trials differ in how the agent words the Google Home gap; none of the agent turns is a slip, and the outcome follows whether the gap becomes a question.

### Task 1, GT run (`1_gt_t0.md`), reward 0, class D
Same order as task 0. The keyboard fallback here is "only exchange the thermostat". The GT agent correctly leaves the keyboard alone and proposes Google Assistant black 7747408585, but adds that it cannot confirm Google Home compatibility (turn 14). The user asks for confirmation (turn 15), the agent cannot give it (turn 16), and the user holds off (turns 17, 19). No WRITE is made, so the DB stays at its initial state and the reference 1_4 (4983901480 -> 7747408585 on credit_card_9513926) is not reached. The GT agent saw the reference action and still did not claim an equivalence that the tools do not show.

### Task 1, Haiku trials 0 and 1 (`1_haiku_t0.md`, `1_haiku_t1.md`), reward 0, class D
In both trials the agent proposes the reference exchange without raising the naming question (turn 14). The user asks whether the thermostat works with Google Home (turn 15), the agent cannot confirm (turn 16), and the user declines (turn 17). In t1 the agent also checks the full list and reports that no thermostat is listed as Google Home compatible (turn 18). Both end without a WRITE (turn 19).

### Task 1, Haiku trial 2 (`1_haiku_t2.md`), reward 1
The agent's proposal is the same as in t0 and t1 (turn 13). The user does not raise Google Home; it only checks the item id and the e-mail on file (turns 14, 16) and confirms (turn 20). The exchange equals 1_4 (turn 21). The flip between t0/t1 and t2 lies in whether the simulator asks the Google Home question. Both behaviours stay within the scenario, so this is the task-text gap of 4f, not a simulator deviation.

### Task 5, Haiku trial 1 (`5_haiku_t1.md`), reward 0, class B
The scenario has two triggers: at the first confirmation request, exchange only the desk lamp; at the second, exchange nothing and return the water bottle. The agent proposes both exchanges and asks for a yes (turn 21); the user narrows to the lamp (turn 22), as the first trigger says. The agent asks for confirmation again (turn 23); the user says "Go ahead and proceed with the desk lamp exchange" (turn 24) instead of switching to the return. The agent exchanges 8384507844 -> 7453605304 (turn 25). The later request to return the bottle (turn 28) is correctly refused, because the order is now "exchange requested" (turn 29). Decisive turn: 24.

### Task 5, Haiku trial 2 (`5_haiku_t2.md`), reward 0, class B
Same course. First confirmation at turn 19, lamp-only answer at turn 20, second confirmation at turn 21, "Yes, that's the one. Go ahead and submit the lamp exchange" at turn 22, exchange at turn 23. Two smaller departures without effect on the reward: "Please don't go with AC" (turn 15), although the scenario ranks AC last rather than excluding it, and an invented wish to keep glass and black. Decisive turn: 22.

### Task 5, Haiku trial 0 (`5_haiku_t0.md`), reward 1
The agent follows the same pattern: a first confirmation (turn 21) and a second one for the lamp-only exchange (turn 23). This time the user follows the second trigger and asks for the return (turn 24). The agent confirms and returns 8538875209 to paypal_7644869 (turns 25 to 27), which equals 5_4. At turn 22 the simulator steps out of its role ("The scenario says: if the agent asks for confirmation, only exchange the desk lamp"); this does not contradict the scenario.

### Task 9, Haiku trial 0 (`9_haiku_t0.md`), reward 0, class A
The user wants a brighter lamp (AC adapter > battery > USB) and a bigger bottle, then keeps only the lamp at the confirmation. The tool result at turn 16 lists 7624783998 (black, high, AC adapter) as available at $154.17. The agent offers only the white high-brightness USB lamp "with the same white color" (turn 17). When the user asks for AC or battery, the agent states that "The high-brightness versions with an AC adapter or battery are unavailable" (turn 19); only the white ones are. The user accepts USB as the last choice and changes its mind about the bottle at the confirmation (turn 20), as the scenario says. The agent exchanges to 9083642334 (turn 25), while reference 9_5 uses 7624783998. Decisive turns: 17 and 19.

### Task 9, Haiku trials 1 and 2 (`9_haiku_t1.md`, `9_haiku_t2.md`), reward 1
Both list the two brighter variants, including black/high/AC (turn 17). The user picks AC (turn 18), drops the bottle at the confirmation (turn 20), and the exchange equals 9_5 (turn 23).

### Task 11, Haiku trial 2 (`11_haiku_t2.md`), reward 0, class B
The user wants to return everything with each order refunded to the other order's payment method; if that is impossible, it should swear a few times and then agree to the original methods. The agent refuses the cross refund under policy.md l.124 and offers the returns to the original methods (turn 14). The user swears once and asks for a human (turn 15). The agent transfers (turns 16 to 18), and the user ends with `###TRANSFER###` (turn 19). No WRITE is made. The transfer on an explicit request is defensible under policy.md l.24. The decisive deviation is turn 15, where the scenario says to agree. Decisive turn: 15.

### Task 11, Haiku trials 0 and 1 (`11_haiku_t0.md`, `11_haiku_t1.md`), reward 1
The agent refuses in the same way (t0 turns 13, 15, 17; t1 turns 13, 15). The user swears and then agrees (t0 turn 18; t1 turn 16), and both returns equal 11_4 and 11_5.

### Task 15, GT run (`15_gt_t0.md`), reward 0, class B (D contributing)
The scenario reads "modify the pending boots to a size 8, and want the material, but do not care about waterproof or not". The simulator opens with "change the size to an 8 and also switch the material" (turn 1). The GT agent finds #W5199551. It reports that the only size-8 variant in stock is 3613716226 (synthetic, not waterproof) and that size-8 leather is out of stock, and offers the choice (turn 18). The user declines synthetic and asks for leather in other sizes (turn 19). It then picks size 9 leather 8106223139 (turn 21), contradicting the scenario's size 8. The agent modifies 1615379700 -> 8106223139 on PayPal (turn 24); reference 15_6 is 3613716226. The GT agent served the user's stated wishes correctly. Decisive turns: 1, 19 and 21.

### Task 15, Haiku trial 2 (`15_haiku_t2.md`), reward 0, class B (D contributing)
The simulator again opens with "maybe switch up the material" (turn 1). The agent offers the only size-8 variant, synthetic (turn 16). The user says "I do want the material to be leather" and keeps the boots (turn 17), and no WRITE follows (turns 18, 19). Decisive turn: 17.

### Task 15, Haiku trials 0 and 1 (`15_haiku_t0.md`, `15_haiku_t1.md`), reward 1
Here the simulator reads the phrase as "make sure they're the right material" (turn 1). The agent offers the same synthetic size-8 variant with PayPal or gift card (turn 16). The user keeps synthetic and asks for PayPal (turn 17), and the modification equals 15_6 (t0 turn 20, t1 turn 18). The phrase "want the material" thus led to opposite readings in two of four runs. Under the material-change reading, the target cannot be reached, because the only other material, leather, has no available size 8 (2648909398 available=false).

### Task 16, GT run (`16_gt_t0.md`), reward 0, class D (B contributing), already in static 4c
The user wants all pending orders cancelled as "no longer needed", the received watch returned and the total refund stated. The GT agent computes $8,276.23 and lists the actions. For the watch refund it offers paypal_5364164 or gift_card_1675628, as policy.md l.122 and l.124 require (turn 14). The user asks which option is faster and says "I want the money back as soon as possible" (turn 15), a preference the scenario does not state. The agent cancels both pending orders as in 16_6 and 16_7 (turns 16, 18). It then says the gift card is faster (turn 20), carrying the immediacy rule for cancellations and payment changes (policy.md l.92, l.106) over to returns, for which the policy states no timing. The user picks the gift card (turn 21), and the return goes to gift_card_1675628 (turn 24), while 16_8 uses paypal_5364164. The end state is policy-compliant but does not match the hash; this is the open choice of static 4c. The NL assertion ($8,276.23) is satisfied at turns 14 and 26, and the judge marked it met.

### Task 19, GT run (`19_gt_t0.md`), reward 0 with db_match=True, class A (B contributing)
The user wants to return the water bottle and exchange the pet bed and office chair to their cheapest versions. All three items are on the same delivered order, so only one of the two actions is possible. If only one is possible, the scenario says to pick the bigger saving and to ask how much each option saves. The GT agent proposes only the water bottle return (2366567022, $54.04, credit_card_1061405) and does not mention that this blocks the exchange (turn 15). The user agrees (turn 16), the return is made (turn 17, equal to 19_6), and only afterwards does the agent say that the exchange is impossible (turn 19). The user insists on both and asks for a human (turn 20) instead of asking for the savings, then accepts the transfer (turns 22 to 26). The exchange saving of $41.64 appears in no agent turn. The judge marks assertion 2 ("saves $41.64 total") unmet and assertion 1 ($54.04) met, which matches the transcript.

## Per-task cause classes

| task | trajectory | reward | db_match | class | decisive turns |
|---|---|---|---|---|---|
| 0 | Haiku t0 | 0 | False | D | 14-17 |
| 0 | Haiku t1, t2 | 1 | True | (success) | t1 14 (unsupported equivalence), t2 12-13 |
| 1 | GT | 0 | False | D | 14-19 |
| 1 | Haiku t0 | 0 | False | D | 15-17 |
| 1 | Haiku t1 | 0 | False | D | 15-19 |
| 1 | Haiku t2 | 1 | True | (success) | user does not raise Google Home |
| 5 | Haiku t1 | 0 | False | B | 24 |
| 5 | Haiku t2 | 0 | False | B | 22 |
| 5 | Haiku t0 | 1 | True | (success) | 24 |
| 9 | Haiku t0 | 0 | False | A | 17, 19 |
| 9 | Haiku t1, t2 | 1 | True | (success) | 17-18 |
| 11 | Haiku t2 | 0 | False | B | 15 |
| 11 | Haiku t0, t1 | 1 | True | (success) | t0 18, t1 16 |
| 15 | GT | 0 | False | B (D) | 1, 19, 21 |
| 15 | Haiku t2 | 0 | False | B (D) | 1, 17 |
| 15 | Haiku t0, t1 | 1 | True | (success) | 1, 17 |
| 16 | GT | 0 | False | D (B), static 4c | 15, 20, 21 |
| 19 | GT | 0 | True | A (B) | 15, 19, 20 |

## Rows with defect=1

| task | check | severity | one line |
|---|---|---|---|
| 0 | 4f | medium | The scenario asks for Google Home compatibility; the catalog has only Google Assistant; the gap decides t0 (static 4d logged it as harmless) |
| 1 | 1e | medium | GT fails on the same Google Home gap; the reference can be reached (Haiku t2), hence medium |
| 1 | 4f | medium | Same gap; 3 of 4 runs (GT, t0, t1) end without a WRITE after the agent cannot confirm Google Home |
| 5 | 5c | medium | t1 and t2 withhold the second-confirmation instruction; the same agent behaviour succeeds in t0 |
| 5 | 5d | medium | t1 turn 24, t2 turn 22 approve the lamp exchange against "If the agent asks for confirmation again, do not exchange anything, and return the water bottle instead" |
| 11 | 5c | medium | t2 asks for a human instead of agreeing to the original-method returns; the same agent refusal succeeds in t0 and t1 |
| 11 | 5d | medium | t2 turn 15 replaces "then agree to return all things with the original payment method" by a transfer request |
| 15 | 4f | medium | "want the material" admits a material-change reading under which the target cannot be reached; 2 of 4 runs take it |
| 15 | 5c | medium | t2 follows the material-change reading with an invented leather preference; the same agent offer succeeds in t0 and t1 |
| 15 | 5d | medium | GT turn 21 picks size 9 against "size 8"; GT turn 1 and t2 turn 17 invent a material change to leather |
| 16 | 1e | medium | GT ends on the gift card refund after an invented speed preference; open refund choice of static 4c; reachable (Haiku 3/3) |
| 16 | 5d | medium | GT turn 15 "I want the money back as soon as possible", which the scenario does not state, decides the refund destination |
| 19 | 5d | medium | GT turn 20 asks for a human instead of "Ask the agent how much money you can save in both options" |

No class E was found: in the two GT runs with assertions (16, 19), the judge verdicts match the transcripts.

## Judgement calls

- Tasks 0 and 1: the refusals after "cannot confirm Google Home" are filed as D, not B. The simulator applies the scenario's stated requirement, Google Home compatibility, to a product the agent cannot confirm. Its guideline-compliant alternative, `###OUT-OF-SCOPE###`, would also leave the DB unchanged. As a result 5c and 5d are 0 for these tasks (5c note "D, see 4f"). Under the airline-checklist wording of 5c ("the flip traces to the user simulator (different disclosure ...) rather than to the agent"), task 1 could be read as a 5c defect, because its three agent proposals are identical and only the simulator's question differs.
- Task 15: the material-change reading is filed as B with D contributing, not as D. The natural reading ("want [to keep] the material, but do not care about waterproof") supports the reference, and the GT run also departs from the stated size 8. The wording problem is still filed under 4f, because it trips 2 of 4 runs.
- Task 16 1e: the provisional mechanical row said high. The reference can be reached by a compliant conversation (Haiku 3/3), so the row is medium.
- Task 19 1e: the provisional row said defect=1 high. The GT failure is an agent omission (the agent never states the $41.64 exchange saving) with a simulator deviation on top, so the row is 0.
