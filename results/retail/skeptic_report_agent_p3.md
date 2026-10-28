# Adversarial review of the retail agent-run rows, part p3

Date: 2026-10-28. Tasks: 55, 59, 64, 66, 71, 72, 80, 82, 83, 87, 91. Object: their 55 rows in `results/retail/review_agent.csv` (21 with defect=1), filed by trajectory batches C (55, 59) and D (the other nine). Row-level verdicts: `skeptic_verdicts_agent_p3.csv`. Changed values: `review_agent_overrides_p3.csv`.

Read: the 20 failed trajectories that `results/retail/agent_triage.md` lists for these tasks, the 14 successful trials of the flipped tasks (34 transcripts), the GT run of task 91 from the run results (it is not rendered as a transcript), the 11 task cards, `policy.md`, the text scaffold in `guidelines.py`, the static rows of these tasks in `retail/audit_log.csv`, `results/retail/skeptic_report.md`, the airline precedents, the reviewer readings in `results/retail/review_agent_C.md` and `review_agent_D.md`, `rejudge.csv` and `rejudge_summary.md`, and the persona recorded per simulation (see section 9). No model call, no replay, no command inside `tau2-bench/`.

Terms: GT = the ground-truth agent run (`llm_agent_gt`, which sees the reference actions); t0, t1, t2 = the three pass^3 trials (`retail_pass3_haiku`); DB = database; [n] = turn marker in the transcript. Classes: A agent slip, B simulator deviation, C defensible alternative reading, D reference or scoring problem (here: scenario gap), E judge error.

## 1. Verdicts

| task | check | filed | verdict | why |
|---|---|---|---|---|
| 55 | 5c | 1 medium | holds (5c-infidelity) | t2 [18], [26], [28] keeps items and [36] stops with the boots unreturned, against "return everything from the orders that have been delivered"; agent turns as in t0, t1 |
| 55 | 5d | 1 medium | holds | same turns; the cited [20] quote matches "you don't remember exactly which items you ordered" and carries no weight on its own |
| 59 | 5c | 1 medium | holds (5c-infidelity) | t1 [9] the simulator names #W2702727 as the older order before any agent framing; the address instruction pins the older order as #W8268610 |
| 59 | 5d | 1 medium | holds | t1 cancels the order it re-addressed; t2 [17] moves the address change to #W8268610 (induced by the agent's label at t2 [10]) |
| 64 | 1e | 1 medium | holds | GT failure through the colour gap of static 64/4c (rule 5); reachable if the user picks black (rule 7); "B contributing" not supported |
| 64 | 5d | 1 medium | fails, set to 0 | the colour statements are choices inside the gap (rule 1, airline 8/5d); the GT event stays under 1e (rule 8) |
| 66 | 5c | 1 medium | holds (5c-infidelity) | t0 [1], [18] replace the coat goal with a luggage swap; in t2 the agent turns are the same and the simulator rejects the variants and falls back |
| 66 | 5d | 1 medium | holds | t0 [1] "I ordered a coat"; t2 [16] invented luggage preference |
| 71 | 5c | 1 medium | holds (5c-infidelity, A contributing) | same clean confirmation request (t1 [20], t2 [25]); only t2 switches to PayPal; t1 [22] the agent answers and writes in one turn |
| 71 | 5d | 1 medium | holds | t1 [21] keeps the gift card at the trigger |
| 72 | 5c | 1 medium | fails, set to 0 ("agent") | t2 [19] merges the payment question and the confirmation, then writes; t0 and t1 ask separately; rule 3 needs alike agent turns (airline 22/5c) |
| 72 | 5d | 1 medium | holds | ordering instruction ignored at [1] in all three trials; t2 [20] does not switch at a confirmation request |
| 80 | 5d | 1 medium | holds (borderline) | GT [20] refuses the exact requested exchange on a condition the scenario does not contain, against its trait "patient"; the persona escalation alone would not count |
| 82 | 5c | 1 medium | holds (5c-infidelity) | t0 [22], t2 [18] put a human request ahead of the instructed fallback; t1 [20] applies it; agent turns alike |
| 82 | 5d | 1 medium | holds | human requests replace the fallback (rule 2); invented "I paid with my credit card" |
| 83 | 5c | 1 medium | holds (5c-infidelity, A contributing) | t1 and t2 have alike agent turns [15], [17]; t1 refuses the gift card and escalates, t2 accepts |
| 83 | 5d | 1 medium | holds | t0 [22], t1 [18], [20] withhold the fallback at its trigger |
| 87 | 5c | 1 medium | holds (5c-infidelity) | t2 [15], [17] invented security concern, never points to the order, stops; t0, t1 point to the order |
| 87 | 5d | 1 medium | holds | GT [16], [18] reject the scenario's address; t2 invented concern and early stop |
| 91 | 5c | 1 medium | holds (5c-infidelity) | t0 [23] confirms the plain e-reader return and raises the exchange at [27] after the write; t1, t2 [17] (and GT [17]) raise it first |
| 91 | 5d | 1 medium | holds | t0 [23], [27]: instruction withheld at its trigger (as airline 23/5d) |

Counts: 55 rows reviewed (21 with defect=1, 34 with defect=0); 19 confirmed; 2 rejected (64/5d, 72/5c); 0 re-filed; 0 escalated.

The 34 zero rows stay 0:
- 1e: GT reached reward 1.0 on 55, 59, 66, 71, 72, 83, 91. The GT failures of 80, 82 and 87 are class B (section 4).
- 4f: no read trajectory shows a class D event that the static rows do not carry; the only D failures (task 64) sit in static 64/4c. Two notes are imprecise, but their value holds. 59/4f says "already in 4a", yet static 59/4a is 0 (it records the older order as fixed by the address request); 4f is 0 because the event is a simulator contradiction (rule 8). 66/4f says "already in 1d/4c"; 66/1d was re-filed to 0, so the pointer is 66/4c, and no trajectory failed through the cancel-reason gap (t1 and t2 chose "no longer needed").
- 5c: 64 (0/3) and 80 (3/3) are stable.
- 2j: ten tasks have no `nl_assertions`; for 59 the live verdicts match the transcripts and the 3-vote majority (section 5).

## 2. Rules as applied

All ten rules were applied as fixed, with no departure. Four readings needed a ruling.

- **Rules 1 and 2 and the persona.** The persona was read per simulation from the run results (`language_context.persona`).
  - Tasks 80, 82, 83 and 87 ran with `priya_patil` in every run. Its clauses include "When you're not getting somewhere fast, asking for a supervisor or a timeline early is characteristic" and "Can I just talk to someone who can actually fix this".
  - The other seven tasks ran with `mamadou_diallo`, whose declines are gentle ("Honestly I'd rather not do that if there's another way").
  - Persona wording was never counted by itself. A request for a human counted only where it replaced an instruction the scenario gives for that situation (82 and 83: the explicit fallback "refund to GC").
  - In 80 the counted element is the refusal of the exact requested exchange on a condition the scenario does not contain; the supervisor request alone would not count.
  - In 55 the persona supplies the wording of the decline at t2 [26] ("Honestly I'd rather not send something back if there's another way to handle it"), not the decision to keep items the scenario returns.
- **Rule 3, "the agent behaved alike".** Read at the decisive turn, the agent turn the simulator answers differently. Agent slips after that point are recorded as A contributing and do not void 5c (71 t1 [22]; 83 t0 [15] to [19]). A different agent turn at the decisive point voids 5c (72 t2 [19]), as in airline 22/5c.
- **Gap or infidelity (rules 1, 3, 5).**
  - 59: the scenario never names the older order. The address instruction ("For order #W2702727 ... because you plan to move prior to its delivery next month") pins it as #W8268610, which is how the static review read it (59/4a = 0, 59/4c = 0). So t1 [9] is a contradiction, not a gap choice. Under the gap reading, 59/5c would carry the tag 5c-gap, 59/5d would stay 1 through t2 [17], and 59/4f would become 1 medium, because no static defect row carries the mechanism.
  - 91: availability of the same e-reader was not stated before t0 [23], and the scenario gives no timing for the exchange wish. It was ruled infidelity for three reasons. Three of four runs (t1, t2, GT) raise the exchange at the same kind of confirmation request. t0 [27] shows that the simulator held the preference. And when the same item is available, as 9494281769 is, the scenario's end state is an exchange. Under the gap reading, 91/5c would carry 5c-gap, 91/5d would become 0, and 91/4f would become 1 medium.
- **Rule 8.** The GT failure of 64 is filed under 1e, so the same colour choice is not also 5d. Static 64/4c and run 64/1e both stay, because they come from different methods.
- **Rules 9 and 10.** Every severity is the checklist's medium. Every amount cited was recomputed: 55: 880.39, 1186.47, 1429.81, 1030.40; 59: 625.60; 64: 35.53, 20.78; 66: 3.42, 1464.00; 71 and 72: 10.84, 3.22, 14.06, 16.64; 80: 7.99, 18.99; 82: 4293.43; 91: 728.04, 8.66.

## 3. Per-trajectory cause classes after this pass

| task | persona | run | reward | class | 5c tag | decisive turns |
|---|---|---|---|---|---|---|
| 55 | mamadou_diallo | t2 | 0 | B | 5c-infidelity | [18], [26], [28], [36] |
| 55 | mamadou_diallo | t0, t1 | 1 | - | | t0 [27], t1 [20]: return everything |
| 59 | mamadou_diallo | t1 | 0 | B | 5c-infidelity | [9], [14], [18] |
| 59 | mamadou_diallo | t2 | 0 | A (B) | | [10] agent invents the date label; [17] |
| 59 | mamadou_diallo | t0 | 1 | - | | [14] |
| 64 | mamadou_diallo | GT | 0 | D (gap, static 64/4c) | stable 0/3 | [16], [21], [22] |
| 64 | mamadou_diallo | t0, t1, t2 | 0 | D (gap) | | t0 [20], t1 [20], t2 [17] |
| 66 | mamadou_diallo | t0 | 0 | B | 5c-infidelity | [1], [18], [24] |
| 66 | mamadou_diallo | t1 | 1 | - | | [14], [16], [17] |
| 66 | mamadou_diallo | t2 | 1 | - (B without reward effect) | | [1], [16], [20] |
| 71 | mamadou_diallo | t0 | 0 | A | | [32] wrong item 6309044598 |
| 71 | mamadou_diallo | t1 | 0 | B (A) | 5c-infidelity | [20], [21]; A at [22] |
| 71 | mamadou_diallo | t2 | 1 | - | | [25], [26] |
| 72 | mamadou_diallo | t2 | 0 | B and A, co-causes | not attributed (agent) | [19], [20] |
| 72 | mamadou_diallo | t0, t1 | 1 | - (B at [1], no reward effect) | | t0 [23], [24]; t1 [21], [22] |
| 80 | priya_patil | GT | 0 | B | stable 3/3 | [20] |
| 82 | priya_patil | GT | 0 | B | | [19], [21] |
| 82 | priya_patil | t0, t2 | 0 | B | 5c-infidelity | t0 [22]; t2 [18] |
| 82 | priya_patil | t1 | 1 | - | | [20] |
| 83 | priya_patil | t0 | 0 | B (A) | | A at [15], [17], [19]; B at [22] |
| 83 | priya_patil | t1 | 0 | B (A) | 5c-infidelity | A at [15]; B at [18], [20] |
| 83 | priya_patil | t2 | 1 | - | | [18] |
| 87 | priya_patil | GT | 0 | B | | [16], [18], [20] |
| 87 | priya_patil | t2 | 0 | B | 5c-infidelity | [15], [17], [19] |
| 87 | priya_patil | t0, t1 | 1 | - | | t0 [15]; t1 [9] |
| 91 | mamadou_diallo | t0 | 0 | B | 5c-infidelity | [22], [23], [27] |
| 91 | mamadou_diallo | t1, t2 | 1 | - | | [17], [21] |

Failed trajectories by primary class (20):
- A: 2 (59 t2, 71 t0);
- B: 14 (55 t2, 59 t1, 66 t0, 71 t1, 72 t2, 80 GT, 82 GT, 82 t0, 82 t2, 83 t0, 83 t1, 87 GT, 87 t2, 91 t0); A contributes in 71 t1, 72 t2, 83 t0 and 83 t1;
- D: 4 (64 GT, t0, t1, t2);
- C and E: 0.

The review had "B contributing" in 64 GT and t1. Those statements are choices inside the gap, so they are not B.

## 4. GT failures, unstable tasks, flips through the simulator

- GT failures, 4 of 11:
  - 64: class D (colour gap), 1e = 1 medium;
  - 80: B;
  - 82: B;
  - 87: B. The GT agent proposed the address at [15] before the user named it, which may have prompted the rejection; this does not break the policy.
- Unstable tasks (1 or 2 passes of 3): 55, 59, 66, 71, 72, 82, 83, 87, 91 (9).
- Flips through the simulator: 8 (55, 59, 66, 71, 82, 83, 87, 91). All 8 are 5c-infidelity; none is 5c-gap. The flip of 72 is not attributed to the simulator alone, because the agent is a co-cause.
- Stable: 64 (0/3) and 80 (3/3).

## 5. 2j cross-check

Only task 59 has `nl_assertions` (two). This part has no judge-only failure: 59 t1 and t2 also fail the DB check.

| run | assertion | live | 3-vote majority | DB | reading of the transcript |
|---|---|---|---|---|---|
| t0 | refund for the cancelled desk lamp order is $164.28 | met | met 3-0 | match | met: [15], [21] |
| t0 | total price of #W2702727 is $625.60 | met | met 3-0 | match | met: [15], [21] |
| t1 | $164.28 refund | unmet | unmet 0-3 | no match | unmet: the desk lamp order was not cancelled; [21] and [23] give $164.28 only as its price |
| t1 | $625.60 total | met | met 3-0 | no match | met: [13] |
| t2 | $164.28 refund | unmet | unmet 0-3 | no match | unmet: [18] and [22] give $164.28 as the order total, not as a refund |
| t2 | $625.60 total | met | met 3-0 | no match | met: [10], [12] |
| GT | both | met | met 3-0 each | match | reward 1.0 |

The live votes, the majority and the transcript reading agree on all 8 verdicts, so 59/2j = 0 holds. The other ten tasks have no assertions, so the judge is not involved.

## 6. Open question 6 of the static review: task 91, minimal-change reading

- Two 32GB variants are available: 7609274509 (8-inch, Wi-Fi, $243.40, which changes storage only) and 4273929280 (7-inch, Wi-Fi + Cellular, $244.95).
- In t1 [20] and t2 [20] the agent lists both, 4273929280 first and 7609274509 third. The simulator picks 7609274509 both times ([21]).
- The GT agent offered only 7609274509 (GT [20], steered by its reference), so the GT run does not test the reading. t0 never reached the choice.

Both unsteered choices (2 of 2) follow the minimal-change reading, and no trajectory fails through the variant choice. This supports static 91/4c = 0. Caveat: these are two samples of one simulator model.

## 7. Effect on the counts of this part

- Agent-run defect rows: 21 -> 19 (5c 9 -> 8, 5d 11 -> 10, 1e 1, 4f 0, 2j 0).
- Defective tasks: 11/11 before and after (64 keeps 4c and 1e; 72 keeps 2e, 2m and 5d).
- Without the simulator-attributed checks 5c and 5d: 4/11 (64, 66, 71, 72).
- Seven tasks are defective only through 5c and 5d: 55, 59, 80, 82, 83, 87, 91. Task 80 rests on one row, 80/5d, which is borderline.

## 8. Not verified

- How the simulator would behave in counterfactuals, which needs model calls:
  - 72 t2 with a separate confirmation turn;
  - 71 t1 if the agent had waited at [22];
  - how often the simulator names #W2702727 as the older order in task 59;
  - how often the 91 simulator raises the exchange before confirming a plain return;
  - 80 GT without the persona's escalation clause.
- The full simulator system prompt was not re-rendered. The persona clauses come from `language_context.persona` in the run results, the scaffold from `guidelines.py` (`_TEXT_PLAIN`).
- The silver end state of task 64 was not replayed. The four runs record db_match=False on 6117189161, and the static review replayed the substitution.
- The simulator's sampling settings are unknown; the counts treat trials as independent draws.
- The GT conversations of the seven GT successes were not read, except 91 (for section 6).

## 9. Disclosures

- Files opened outside the listed inputs:
  - `results/retail/runs/retail_gt_haiku/results.json` and `results/retail/runs/retail_pass3_haiku/results.json`. A read-only Python script read them for the persona of each simulation of the p3 tasks (`language_context.persona`) and for the GT conversation of task 91, which is not rendered under `trajectories/`.
  - `tau2-bench/AGENTS.md` was shown as attached context when `tau2-bench/src/tau2/user/guidelines.py` was read. It was not used.
- Directory listings of `results/retail/` and `retail/` showed file names, including files on the do-not-open list. None of those files was opened, and no file of the other parts was opened.
- One long query result over `retail/audit_log.csv` was stored by the environment in a session file and read from there.
- Commands inside `tau2-bench/`: none. Two files under it were read with a file reader (`policy.md`, `guidelines.py`). No replay, no model or API call, no network, no git, nothing installed or edited.
- One scratch file, a dump of the p3 rows of `review_agent.csv`, was written to the temporary folder and deleted at once. Only the three outputs remain there.
