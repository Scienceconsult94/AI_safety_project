# Adversarial review of the retail agent-run rows, part p4

Date: 2026-10-28. Tasks 93, 98, 99, 100, 101, 103, 104, 105, 108, 110, 112. Object: their 55 rows in `results/retail/review_agent.csv` (1e, 4f, 5c, 5d, 2j per task; 19 with defect=1), filed by trajectory batch D (task 93) and batch E (the other ten), and the 3-vote re-judge (`results/retail/rejudge.csv`). Brief: `retail/skeptic_brief_agent_parts.md`. Outputs: `skeptic_verdicts_agent_p4.csv`, `review_agent_overrides_p4.csv` and this report.

Method. All 34 rendered trajectories of these tasks were read: the 22 failed ones listed in `results/retail/agent_triage.md` and the 12 successful trials of the flipped tasks (98 t0/t2, 99 t1/t2, 101 t0, 104 t0/t1, 108 t1/t2, 110 t0, 112 t0/t1). Also read: every task card; `policy.md`; `tools.py` (exchange balance check); `guidelines.py` (text scaffold); `evaluator_nl_assertions.py`; the static rows of these tasks in `retail/audit_log.csv`; the trajectory readings in `review_agent_D.md` (task 93) and `review_agent_E.md`. The assigned simulator persona of each of the 44 simulations was read from the run files (section 9). Every amount a row depends on was recomputed from the cards. No model call, no replay, nothing changed under `tau2-bench/`.

Terms: GT = ground-truth agent (one trial); t0-t2 = the three trials of the generic agent; [n] = turn markers of the transcripts. Classes: A agent slip, B simulator deviation, C defensible alternative reading, D reference or scoring problem (including scenario gaps), E judge error.

## 1. Counts

| | rows |
|---|---|
| defect=1 rows reviewed | 19 |
| confirmed (skeptic_ok = 1: the row holds as it stands after the override file) | 17 |
| of which with a corrected class or tag, value unchanged | 2 (100/1e, 104/5c) |
| rejected (set to 0) | 2 (100/5d, 104/5d) |
| re-filed under another check | 0 |
| escalated from 0 | 1 (98/5c, medium, 5c-gap) |
| defect=0 rows checked that stay 0 | 35 |
| note or evidence corrections with unchanged value | 98/5d, 105/1e, 104/4f, 105/4f; tag 5c-infidelity added to 99/5c, 101/5c, 108/5c, 112/5c |

The override file has 13 rows; 3 change a value (98/5c 0 -> 1 medium; 100/5d 1 -> 0; 104/5d 1 -> 0), the other 10 correct a note, a tag or the evidence and say so.

Run-row defects of these tasks after the pass: 18 (1e 3: 98 medium, 100 medium, 105 high; 4f 1: 100 medium; 5c 6; 5d 7; 2j 1: 110), against 19 as filed. Each of the 11 tasks keeps at least one confirmed run row, so no task leaves the defective set through this pass.

## 2. Verdicts

| row | filed | verdict | why |
|---|---|---|---|
| 93/5d | 1 medium | holds | GT [15], [17] invent a mismatch between the laptop received and the record that the scenario's '15-inch, 32GB' matches; the human request at [17] is the persona's and is not counted on its own |
| 98/1e | 1 medium | holds | the GT failure runs through the 'other card' gap of static 98/4c: the agent proposes the reference Mastercard [22], the user takes 'the other card' = Visa [23]; reachable when the Visa is proposed first (t0) |
| 98/5c | 0 | escalated: 1 medium, 5c-gap | t1 [19] and t2 [20] answer the same agent turn (three methods, none proposed) with the two readings of 'the other card' |
| 98/5d | 1 medium | holds, weak; evidence corrected | fabricated item placements GT [7], t0 [1]/[9], t1 [25]; the t2 [20] card remark belongs to the gap and is moved out |
| 99/5c | 1 medium | holds, 5c-infidelity | t0 [17] '1000 pieces' against '1000 more pieces'; the agent applies the stated count in all three trials |
| 99/5d | 1 medium | holds | t0 [17] decides the hash |
| 100/1e | 1 medium | holds as D; class corrected | deck-material gap (bamboo 6956751343 vs plastic 9594745976); the price pick is a choice inside the gap, not class B |
| 100/4f | 1 medium | holds | the gap is not carried by a static defect row (100/4c = 0); 4/4 runs end on plastic |
| 100/5d | 1 medium | fails | the deck pick is inside the gap and already filed under 1e/4f (rule 8); the history remarks are persona-scripted and bear on nothing the agent must do |
| 101/5c | 1 medium | holds, 5c-infidelity (A contributing) | t2 [26] dictates an invented New York address; t0 [15] 'you can grab it from there' |
| 101/5d | 1 medium | holds | t2 [26]; GT [17] and t1 [28] are weaker and scenario-induced |
| 103/5d | 1 medium | holds | GT [37], [39] drop and deny the cancelled-order request |
| 104/5c | 1 medium | holds; re-tagged 5c-gap | the item-first disclosure is what 'You like to say one thing at a time' allows; the order mechanism is static 104/2e |
| 104/5d | 1 medium | fails | no trigger fired for the address request (the agent asked about items only; the scenario names no condition) |
| 105/1e | 1 high | holds; note corrected | 21.10 > 17.00, the tool raises, the assertion demands the exchange: no compliant conversation reaches reward 1.0 |
| 108/5c | 1 medium | holds, 5c-infidelity (A contributing) | t0 [7] narrows the return and [15] confirms an E-Reader-only list |
| 108/5d | 1 medium | holds | GT [9], [15] contradict 'You want to return everything but a tablet' |
| 110/2j | 1 medium | holds | 'Agent should modify user address' met in t0 with no write; unmet in t1/t2 on the same agent statements |
| 112/5c | 1 medium | holds, 5c-infidelity | the same espresso-machine note is accepted in t0 [20] and refused in t2 [19] |
| 112/5d | 1 medium | holds | t2 [19], [21], [36] refuse the address change the scenario asks for |

Defect=0 rows that stay 0 (35): 93 1e/4f/5c/2j; 98 4f/2j; 99 1e/4f/2j; 100 5c/2j; 101 1e/4f/2j; 103 1e/4f/5c/2j; 104 1e/4f/2j; 105 4f/5c/5d/2j; 108 1e/4f/2j; 110 1e/4f/5c/5d; 112 1e/4f/2j. Notes corrected on 104/4f (t2 is class D, not B) and 105/4f (static 1c is 0).

## 3. Rules as applied

- **Rule 1 (5d).** Counted: fabricated facts that bear on what the agent must do (93 GT mismatch; item placements in 98 and 99; the invented New York address in 101 t2; the espresso-machine constraint in 112 t2), contradictions of scenario facts (99 t0 piece count; 103 GT 'I didn't cancel that one'; 108 GT 'I only want to return the E-Reader'), and instructions withheld at a trigger that fired (108 t0 [15]: the agent asked to confirm the item list, which is the subject of 'return everything but a tablet'; 103 GT [37]: the request was raised, then dropped). Not counted: choices inside a scenario gap (100 deck material, 98 card), persona-scripted remarks and escalation, and a disclosure order the scenario leaves open (104 t2).
- **Persona.** The persona of every simulation was read from `language_context.persona`: persona id `priya_patil` on 93, 98, 99, 100, 108, 112 (clauses include 'Like I said, the order's been wrong twice now', 'asking for a supervisor or a timeline early is characteristic', 'That's not what I asked', 'Can I just talk to someone who can actually fix this'); persona id `mamadou_diallo` on 101, 103, 104, 105, 110. Remarks that reproduce these clauses (the 100 history remarks, the 93 GT [17] request for a human, 98 t0 [30], the 100 transfer requests) are not counted.
- **Rule 1 trigger, task 104.** The trigger is read as the rule defines it: the agent asked, or a situation the scenario names occurred. In 104 t2 the agent's question [38] concerned items, the address request is unconditional, and the scenario adds 'You like to say one thing at a time' with the item change listed first. The late address request is therefore a disclosure the scenario does not fix (5c-gap), not a withheld instruction. Airline 23/5d differs: its scenario tied the instruction to a trigger that fired. Under the broader reading (the lock warning as trigger) 104/5d would stay 1 and 104/5c would be 5c-infidelity; task 104 stays defective either way (static 104/2e, 104/4e).
- **Rule 2.** No request for a human in these tasks replaces a scenario instruction; each is persona-scripted or follows the agent's own offer (93 GT [16]-[17], 98 t0 [29]-[30], 100 in all four runs, 108 t0 [21]).
- **Rule 3.** Tags: 5c-infidelity on 99, 101, 108 and 112; 5c-gap on 98 (new) and 104 (re-tagged). 110/5c stays 0 with 'judge, see 2j'. In 101 t2 and 108 t0 the agent contributes (class A), but its differing turns follow the simulator's differing words; in airline 22/5c, by contrast, the agent's false statement came first and caused the simulator's reaction.
- **Rule 4.** The agent refusals in these tasks are backed by policy: 105 (l.134, gift-card balance) and 104 t2 [44] (l.110, no change after an item modification). No class C.
- **Rule 5.** Tasks 98 and 100 were decided explicitly. 98: the card gap stays under task text (static 98/4c; run 98/1e = 1 medium; 98/4f = 0 'already in 98/4c'); its flip gives 98/5c = 1 (5c-gap); 98/5d = 1 rests on a different event (item placements). 100: the deck gap goes under task text only (100/1e = 1 and 100/4f = 1, both medium, since no static defect row carries it); 100/5d = 0; 100/5c = 0 (no flip). Both now carry the gap under task text, as 0 and 1 do. The order-of-actions gap of 104 is carried by static 104/2e (104/4f = 0).
- **Rule 6.** 110 t0 is class E (an assertion marked met that the transcript does not satisfy). 103 GT is not E: the agent never stated 286422338955 and the user had withdrawn the request. 108 GT is not E: $346.93 was said only as the total of the three-item proposal the user rejected [14], and the refund stated for the executed return is $244.02 [16], [20]; the DB fails anyway.
- **Rule 7.** 105/1e high: no conversation can execute the exchange (the tool raises on the balance) and the assertion demands it, so no policy-compliant conversation reaches reward 1.0. 98/1e and 100/1e medium: the reference is reached when the Visa is proposed first or bamboo is chosen.
- **Rule 8.** 100: the deck event leaves 5d and stays under 1e and 4f. Static and run rows on one cause both stay (98: 4c and 1e; 105: 1b, 4b, 4e and 1e; 104: 2e and the 5c-gap flip).
- **Rules 9-10.** Checklist severities kept. Amounts recomputed from the cards: 93 60.78; 98 14.54 + 6.01 = 20.55 and 71.59; 99 17.45 (t0) and 14.96 (t1, t2); 100 +47.01, +21.91 or -11.02, nets 68.92 or 35.99; 101 +11.58, -121.20, +24.24 (wrong exchange in t1); 103/104 +17.86; 105 6.32 + 14.78 = 21.10 > 17.00; 108 244.02 + 52.03 + 50.88 = 346.93; 110 -114.73; 112 -242.15 and -77.15. All match the agents' figures except the t0 slip in 100 ($46.01, corrected to $47.01 at [19]).
- **Conventions and departures.** skeptic_ok = 1 means the row holds as it stands after the override file, as in the static review; note-only override rows say 'verdict unchanged' or 'value unchanged'. No departure from the fixed rules.

## 4. Cause classes per trajectory after this pass

| trajectory | reward | class after this pass | as filed | decisive turns |
|---|---|---|---|---|
| 93 GT | 0 | B | B | [15], [17] |
| 98 GT | 0 | D (gap, 98/4c) | D | [22]-[23] |
| 98 t0 | 1 | success (agent proposed the Visa [21], user took the Mastercard [22]) | - | [21]-[22] |
| 98 t1 | 0 | D (gap); flip, 5c-gap | D | [18]-[19] |
| 98 t2 | 1 | success (user picked the Mastercard [20]) | - | [19]-[20] |
| 99 t0 | 0 | B; flip, 5c-infidelity | B | [17] |
| 99 t1, t2 | 1 | success | - | [16] |
| 100 GT | 0 | D (gap) | D (B) | [24], [29] |
| 100 t0 | 0 | D (gap) | D (B) | [17], [20] |
| 100 t1 | 0 | D (gap) | D (B) | [20], [25] |
| 100 t2 | 0 | D (gap) | D (B) | [19], [22] |
| 101 GT | 0 | A (B contributing) | A (B) | [14], [18], [22] |
| 101 t0 | 1 | success | - | [15], [20] |
| 101 t1 | 0 | A (B contributing) | A (B) | [31], [33] |
| 101 t2 | 0 | B (A contributing); flip, 5c-infidelity | B (A) | [26], [31] |
| 103 GT | 0 | B (A contributing) | B (A) | [37]-[39] |
| 104 t0 | 1 | success | - | [28], [33], [37] |
| 104 t1 | 1 | success through the forbidden write order (2e) | - | [34], [36] |
| 104 t2 | 0 | D (order-of-actions gap, 104/2e); flip, 5c-gap | B | [33], [39], [43]-[44] |
| 105 GT | 0 | D | D | [16] |
| 105 t0 | 0 | D | D | [13] |
| 105 t1 | 0 | D | D | [14] |
| 105 t2 | 0 | D | D | [13] |
| 108 GT | 0 | B | B | [9], [15] |
| 108 t0 | 0 | B (A contributing); flip, 5c-infidelity | B (A) | [7], [14], [15] |
| 108 t1, t2 | 1 | success | - | [14] |
| 110 t0 | 1 | success through a judge error (E) | E | [14], [26] |
| 110 t1 | 0 | D (judge-gated, static 110/4d) | D | [13] |
| 110 t2 | 0 | D (judge-gated, static 110/4d) | D | [13], [19] |
| 112 t0 | 1 | success through the forbidden write order (2e) | - | [21], [23] |
| 112 t1 | 1 | success | - | [25], [27] |
| 112 t2 | 0 | B; flip, 5c-infidelity | B | [19], [21] |

Failed trajectories (22): A 2, B 7, C 0, D 13, E 0. As filed: A 2, B 8, D 12 (the four 100 runs as D with B contributing). Changes: 104 t2 B -> D (gap); the four 100 runs lose 'B contributing'.

## 5. GT failures and unstable tasks

GT failures (7 of the 11 tasks): A 1 (101), B 3 (93, 103, 108), D 3 (98 card gap, 100 deck gap, 105 raising reference with an unsatisfiable assertion). 1e = 1 on the three D cases (98 medium, 100 medium, 105 high); A and B give 1e = 0. 99, 104, 110 and 112 reached reward 1.0 with the GT agent.

Unstable tasks (1 or 2 of 3 trials pass): 98, 99, 101, 104, 108, 110, 112 (7). Flips through the simulator: 6, of which infidelity 4 (99, 101, 108, 112) and gap 2 (98, 104); through the judge: 1 (110). As filed: 5 through the simulator, all as class B, and 98 as 0. In 101 and 108 the agent contributes (class A) to the failing trial.

## 6. 2j cross-check against the 3-vote re-judge

| simulation | assertion | live | re-judge met/unmet | majority | transcript | believed |
|---|---|---|---|---|---|---|
| 103 GT (DB matched) | 'Agent should provide the tracking number 286422338955.' | unmet | 0/3 | unmet | the agent's turns give only 682308736931 [38]; 286422338955 appears only in a tool result [13] | unmet (agree) |
| 105 GT, t0, t1, t2 (DB matched) | 'Agent should exchange both tea kettles (same style) to the items requested' | unmet | 0/3 each | unmet | every agent refuses the exchange (GT [16], t0 [13], t1 [14], t2 [13]) | unmet (agree) |
| 110 t1 (DB matched) | 'Agent should modify user address' | unmet | 2/1 | met (reward flip 0 -> 1) | no modify_user_address call; [13] 'no update is needed' | unmet: the majority reads the outcome (the default already is the new home), not the action the assertion names |
| 110 t2 (DB matched) | same | unmet | 0/3 | unmet | no call; [13], [19] 'I left it unchanged' | unmet (agree) |
| 110 t0 (passed) | same | met | 3/0 | met | no call; [14] 'No change is needed there' | unmet: class E, the 110/2j row |
| 108 GT (DB failed) | 'Agent should tell the user the refund amount is $346.93.' | unmet | 0/3 | unmet | $346.93 only as the total of the rejected three-item proposal [14]; executed refund $244.02 [16], [20] | unmet (agree; borderline; reward 0 through the DB anyway) |
| 108 t0 (DB failed) | same | unmet | 0/3 | unmet | $346.93 never stated; $244.02 [14], [18] | unmet (agree) |

Judge-only failures in these tasks: 7 simulations (103 GT; 105 GT, t0, t1, t2; 110 t1, t2). The re-judge majority agrees with the transcript on 6 and disagrees on 110 t1. With 110 t0, the judge gives 5 'met' votes out of 9 on three trials whose agent turns say the same thing (no write, default already correct). The 110/2j row holds under either reading of the assertion: read literally, the t0 'met' is the error; read as an outcome, the t1 and t2 'unmet' verdicts are. The literal reading is the one believed here, because the assertion names an action and the agent states in every trial that it did not take it.

## 7. Open question 6 of the static review: the minimal-change reading of task 100

Static 100/4c = 0 rests on the reading that a scenario naming only the changed options keeps the others, here the bamboo deck of 5312063289. The trajectories do not support it:
- all four runs, including the GT agent, which had the bamboo reference 101_0 in view, present the deck material as an open choice (GT [24], t0 [17], t1 [20], t2 [19]);
- asked to choose, the simulator never answers 'keep the current deck' and ends on plastic every time (GT [29], t0 [20], t1 [25], t2 [22]);
- the scenario sentence itself treats the two items differently: the luggage is 'the exact same item but with red color', the skateboard 'a new one with features {'length': '34 inch', 'design': 'custom'}'.

The deck material is therefore a gap in the sense of rule 5 ('an item variant among those that match the stated options'), and 100/4f = 1 medium carries it at run level. If the coordinator re-opens static 100/4c to 1, rule 5 turns 100/4f into 0 'already in 100/4c', and 100/1e stays (rule 8). Task 100 is defective either way (static 1g and 2h).

## 8. Could not verify

- No replay was run. Hash claims rest on the recorded db_match and on the static probes (98 card: probe_2d; 101, 104 and 112 write order: probe_2d write_order; 105: the static replay of the raising reference).
- Counterfactuals that need model calls were not tested: whether the simulator would accept bamboo if an agent proposed it as the unchanged material (100); whether it would raise the address if the agent asked 'anything else for this order?' (104 t2); whether the 108 t0 simulator would still narrow the return if the agent listed all three items (GT [15] suggests it would).
- The persona text was taken from `language_context.persona` (persona id, gender, pragmatics clauses); the full rendered simulator prompt was not re-rendered. Sampling settings were not checked; trials are treated as independent draws.
- The judge's reasoning texts were not opened; the cross-check uses the vote counts in `rejudge.csv` only.
- The outputs of the other parts are not visible here. The reading of the rule-1 trigger (task 104) is the decision most exposed to a difference between parts.

## 9. Disclosures

- Files opened outside the listed inputs: `results/retail/runs/retail_pass3_haiku/results.json` and `results/retail/runs/retail_gt_haiku/results.json`, read with Python for the 44 simulations of these tasks (persona id, gender and pragmatics clauses; reward; termination). The top-level `tasks` entry of these files was not read or printed.
- The first listing of the temporary folder showed the folder names of two other parts (`skeptic_retail_p2`, `skeptic_retail_p3`); neither was opened.
- Commands run inside `tau2-bench/`: read-only `grep`, `sed` and `wc` on `src/tau2/domains/retail/tools.py`, `src/tau2/user/guidelines.py`, `src/tau2/evaluator/evaluator_nl_assertions.py` and `data/tau2/domains/retail/policy.md`. No git, no uv, no Python, no replay; nothing changed.
- No model or API call and no network access. Inline Python ran from standard input with `-I`; files were created only in this part's temporary folder (the three outputs).
- Not opened: `tasks.json`, `task_issues/`, `report.md`, `README.md`, `ONE_PAGER.md`, `retail/summary_numbers.md`, `retail/comparison.md`.
