# Adversarial review of the retail agent-run rows, part p2

Date: 2026-10-28. Tasks 30, 31, 32, 34, 38, 39, 43, 46, 49, 51, 52. Object: their 55 rows in `results/retail/review_agent.csv` (checks 1e, 4f, 5c, 5d, 2j; 18 rows with defect=1), the readings in `results/retail/review_agent_B.md` (tasks 30-34) and `results/retail/review_agent_C.md` (tasks 38-52), and the 3-vote re-judge (`results/retail/rejudge.csv`).

Read directly: all 37 trajectories of these tasks in `results/retail/trajectories/` (every failed GT and Haiku run, and every trial of the flipped tasks); the 11 task cards; `tau2-bench/data/tau2/domains/retail/policy.md`; `tau2-bench/src/tau2/user/guidelines.py` (text scaffold); `tau2-bench/src/tau2/evaluator/evaluator_nl_assertions.py` (judge view); `checklist.md`, `retail/checklist.md`, the dated deviations of `retail/PLAN.md`, `retail/review_agent_brief.md`; `results/retail/agent_triage.md`, `agent_runs_summary.md`, `haiku_pass.csv`, `rejudge.csv`, `rejudge_summary.md`; the static rows of these tasks in `retail/audit_log.csv`; `results/retail/skeptic_report.md`; the airline precedents `results/skeptic_report_agent.md` and `results/consistency_pass.md`. The persona assigned to each simulation was read from the run results (section 9). No model call, no replay, no git command, nothing changed under `tau2-bench/`.

Terms: GT = ground-truth agent `llm_agent_gt` (sees the reference actions); t0, t1, t2 = Haiku trials 0-2; DB = database; `[n]` = turn marker in the transcript. Classes: A agent slip, B simulator deviation, C defensible alternative reading, D reference or scoring problem, E judge error.

## 1. Verdicts

| task | check | filed | verdict | why |
|---|---|---|---|---|
| 30 | 5c | 1 medium | holds, 5c-infidelity | the agent asks the reason with both values in all trials (t0 [28], t1 [26], t2 [27]); t1 [27] "Ordered by mistake" against a motive that pins "no longer needed" (static 30/4c); t0 and t2 pass |
| 30 | 5d | 1 medium | holds | t1 [27] is decisive; the "cracked screen" detail is wording without bearing and is not counted |
| 31 | 4f | 1 medium | holds | t0 [17] transfers at once; policy l.24 ("transfer ... if and only if the request cannot be handled within the scope of your actions") supports it; the scenario and reference assume refuse-and-continue; no static row of 31 carries it |
| 31 | 5d | 1 medium | holds on replaced evidence | cited t1 [19] and t2 [17] are not counted deviations; t1 [25] "Ordered by mistake, I guess ... Either one works" is (weak, no effect) |
| 32 | 5d | 1 medium | holds | GT [17], t1 [21], t2 [19] accept a transfer at the "If not" trigger instead of the scripted cancellations and return; t0 [27] refuses the kettle cancellation the scenario asks for |
| 34 | 4f | 1 medium | rejected | rule 8: same event as 34/5d (fabricated rejections of the read-back address); the address is pinned (static 34/1d, 34/4c) |
| 34 | 5c | 1 medium | holds, 5c-infidelity | the same proposal is accepted in t0 [19] and t2 [15]; t1 [19], [23] invent that the address is not the user's |
| 34 | 5d | 1 medium | holds | GT [21], [23] and t1 [19], [23]; t2 [21] "I thought I paid by card" has no bearing |
| 38 | 1e | 1 medium | holds | the GT run fails only on the cancel reason, a gap (static 38/4c); reachable when the simulator says "no longer needed", so medium |
| 39 | 5c | 1 medium | holds, 5c-infidelity | t0 [9], [11] turn the current address on the order into the "old address"; t2 [9] asks the agent to read the order and passes; t1 borderline gap |
| 39 | 5d | 1 medium | holds | GT [9] and t0 [9], [11] (decisive) |
| 43 | 5c | 1 medium | holds, 5c-infidelity | t1 [18] and t2 [16] end through a transfer before the scenario's last request; t0 [14] raises it first; the agent's transfer offer is the same |
| 43 | 5d | 1 medium | holds | as 5c; t2 [16] "like 256GB" is a weak, agent-prompted fabrication |
| 46 | 5c | 1 medium | holds, weak, 5c-infidelity | t2 [21] narrows the scripted question to the canister vacuum; t1 [23] asks it as scripted; A contributing |
| 46 | 5d | 1 medium | holds | GT [19] refuses the return on a 3-day condition the scenario does not contain ("After the return is complete"); t2 [21] weak |
| 49 | 5d | 1 medium | holds | GT [19] replaces "the cheapest earbud item from the rest of that order" with the cheapest catalogue IPX4 variant and invents the IPX4 fact |
| 51 | 5d | 1 medium | holds | t0 [11], t1 [10] "I didn't order an air purifier ..."; t1 [18] a cancellation the scenario does not contain; the t2 part is not counted |
| 52 | 1e | 1 high | re-filed, medium | the reference write is policy-compliant and reached when the user resolves the scenario's constraint conflict for zoom; rule 7 gives high only when no policy-compliant conversation reaches the reference |

Escalations: none.

Counts: 18 rows reviewed; 16 confirmed (one of them, 31/5d, on replaced evidence); 1 rejected (34/4f); 1 re-filed (52/1e, high to medium); 0 escalated.

Override file `review_agent_overrides_p2.csv` (9 rows): value changes 34/4f (1 to 0) and 52/1e (high to medium); evidence replaced on 31/5d; note-only rows that add the rule-3 tag to 30, 34, 39, 43 and 46 5c, and that correct the note of 34/1e (it named class D and pointed to the rejected 4f row).

Note for the builder: this brief defines `skeptic_ok` = 0 for a row that "belongs under another ... severity", so 52/1e carries 0 while its override row keeps defect=1 medium. The static phase marked such severity re-filings 1. Read 52/1e as a confirmed medium row.

## 2. Rules as applied

1. Rule 1 (5d).
   - Counted: fabricated facts or preferences that bear on what the agent must do (30 t1 [27]; 31 t1 [25]; 34 GT [21], [23], t1 [19], [23]; 49 GT [19]; 51 t0 [11], t1 [10], [18]; 43 t2 [16]; 46 GT [19]); contradictions of scenario facts or instructions (32 t0 [27], 32 t1 [17], 39 GT [9], t0 [9], [11], 46 t2 [21]); instructions withheld at their trigger (32 GT [17], t1 [21], t2 [19]); ending with an unconditional scenario request unmade and no scenario reason to stop (43 t1 [18], t2 [16]).
   - Not counted: wording without bearing (30 "cracked screen"; 31 t2 [17] "lost it on the way", after [1] "I just received a tablet and I lost it"; 34 t2 [21] "paid by card"); faithful statements of scenario unknowns (51 t2 [21] e-mail; 34 t1 [21] "I don't know the street"); accepting an agent offer that the scenario's wish covers (31 t1 [19]: the agent offers the refund the scenario asks for and the user restates the loss; the off-reference return is the agent's); choices inside a gap (38 cancel reason; 52 constraint conflict).
2. Persona. Nine of the eleven tasks ran with the female-caller persona `priya_patil` (`language_context.persona` in the run results), whose clauses include "When you're not getting somewhere fast, asking for a supervisor or a timeline early is characteristic" and "Can I just talk to someone who can actually fix this"; 38 and 49 ran with `mamadou_diallo`. Supervisor or transfer requests are not counted by themselves (rules 1 and 2, airline block-1 precedent). They count where they replace the instruction the scenario gives for that situation (32: the "If not" branch; 46 GT: the return that the scenario completes) and where the conversation ends with an unconditional request unmade (43). The persona scripts the escalation, not a dropped request.
3. Rule 3 (5c). The tag is set per failing trial; a task takes the tag of its decisive failing trial (table in section 3). 31/5c stays 0 ("agent"): t0's immediate transfer and t1's return of a lost tablet are agent actions that the t2 agent did not take. 51/5c stays 0 ("agent"): the simulator's claim is the same in t0 [11] and t1 [10], and t1 differs by the agent's unasked cancel offer at [17].
4. Rule 4. 31 t0 is class C, supported by policy l.24 (quoted in section 1). 31 t1 is class A: a return of an item the user reports lost is not a compliant alternative (static 31/4c), and the t0 and t2 agents say that a return requires sending the item back.
5. Rule 5. 38 (cancel reason; "so that you can order again" pins neither value) and 52 (two stated constraints that no available variant satisfies) are choices the scenario leaves open; the static log carries both (38/4c, 52/4a), so 4f = 0 "already in". In 30 and 31 the motive "because it goes with the tablet" pins "no longer needed" (static cancel-reason rule), so the simulator's "ordered by mistake" is infidelity, not a gap.
6. Rule 7. Read as written: high only when no policy-compliant conversation reaches the reference. The 52 reference write (9228757377, PayPal for +170.68) is policy-compliant (static 52/4b) and is the only available 10x variant, so it is reached whenever the user puts the scenario's "maximum zoom capacity ... has to be maximized" before "all the other specifications ... the same". The filed reading (high, because a simulator that holds the specifications never confirms it) adds a fidelity condition that rule 7 does not state. Under that reading 52/1e stays high; the task is defective through 52/4a either way.
7. Rule 8. 34 had the same event (GT and t1 rejecting the read-back address) under 5d (B) and 4f (D contributing). The rejections carry fabricated facts, and the address is the user's only New York 10108 address on file, so the event is fidelity and 4f goes to 0. In 31, 4f (agent transfer, t0 [17]) and 5d (simulator, t1 [25]) are different events.
8. Rule 10. Recomputed: 38 order 1166.98, cheapest total 466.75 + 288.82 + 135.24 + 46.66 + 193.38 = 1130.85 > 950, camera 481.50 the most expensive item; 46 refund 652.61 + 473.43 = 1126.04, remaining 622.12 + 329.85 + 545.68 = 1497.65 = 2623.69 - 1126.04; 49 reference 258.97 - 232.49 = 26.48, GT 258.97 - 226.49 = 32.48; 52 3066.23 - 2895.55 = 170.68, 2895.55 - 2714.51 = 181.04; 34 office items 235.13 + 346.97 + 511.24 = 1093.34; 32 kettle and boots 143.72 + 253.54 = 397.26.

Departures from the rules of the brief: none. The readings in points 2, 3 and 6 are stated so that the other parts can be compared.

## 3. Per-trajectory cause classes after this pass

| trajectory | reward | class | 5c | decisive turns |
|---|---|---|---|---|
| 30_haiku_t0 | 1 | success | - | [29] "No longer needed" |
| 30_haiku_t1 | 0 | B | 5c-infidelity | [27] "Ordered by mistake" |
| 30_haiku_t2 | 1 | success | - | [28] "No longer needed" |
| 31_haiku_t0 | 0 | C (A contributing) | agent | [16]-[17] immediate transfer |
| 31_haiku_t1 | 0 | A (B at [25], no effect) | agent | [18]-[20] return of the lost tablet |
| 31_haiku_t2 | 1 | success | - | [18]-[19] |
| 32_gt_t0 | 0 | B (A contributing) | - | [16]-[18] transfer accepted, cancellations deferred |
| 32_haiku_t0 | 0 | B | stable 0/3 | [27] keeps the kettle |
| 32_haiku_t1 | 0 | B (A contributing) | stable 0/3 | [17], [20]-[22] |
| 32_haiku_t2 | 0 | B | stable 0/3 | [18]-[19] |
| 34_gt_t0 | 0 | B | - | [19]-[23] |
| 34_haiku_t0 | 1 | success | - | [18]-[19] |
| 34_haiku_t1 | 0 | B | 5c-infidelity | [19], [23] |
| 34_haiku_t2 | 1 | success ([21] not counted) | - | [14]-[15] |
| 38_gt_t0 | 0 | D (gap, 38/4c) | - | [31], [34] |
| 38_haiku_t0 | 0 | D | stable 0/3 | [25], [28] |
| 38_haiku_t1 | 0 | D | stable 0/3 | [30], [31] |
| 38_haiku_t2 | 0 | D | stable 0/3 | [31], [32] |
| 39_gt_t0 | 0 | B (A contributing) | - | [9]-[10] |
| 39_haiku_t0 | 0 | B (A contributing) | 5c-infidelity | [9]-[11] |
| 39_haiku_t1 | 0 | B, borderline (A contributing) | 5c-gap, borderline | [17]-[23] |
| 39_haiku_t2 | 1 | success | - | [9]-[16] |
| 43_haiku_t0 | 1 | success | - | [14]-[17] |
| 43_haiku_t1 | 0 | B (A contributing) | 5c-infidelity | [17]-[19] |
| 43_haiku_t2 | 0 | B (A contributing) | 5c-infidelity | [15]-[17] |
| 46_gt_t0 | 0 | B (A contributing) | - | [17]-[19] |
| 46_haiku_t0 | 0 | A | agent | [25]-[26] |
| 46_haiku_t1 | 1 | success | - | [23]-[24] |
| 46_haiku_t2 | 0 | B, weak (A contributing) | 5c-infidelity | [21]-[22] |
| 49_gt_t0 | 0 | B (A contributing) | - | [18]-[19], [22] |
| 51_haiku_t0 | 1 | success (B at [11], no effect) | - | [11]-[16] |
| 51_haiku_t1 | 0 | B (A contributing) | agent (rule 3) | [10], [17]-[19] |
| 51_haiku_t2 | 1 | success | - | [11]-[16] |
| 52_gt_t0 | 0 | D (conflict, 52/4a) | - | [14]-[17] |
| 52_haiku_t0 | 0 | D | stable 0/3 | [17]-[18] |
| 52_haiku_t1 | 0 | D | stable 0/3 | [17]-[20] |
| 52_haiku_t2 | 0 | D | stable 0/3 | [17]-[20] |

Failing trajectories: 27. Primary class: A 2 (31 t1, 46 t0), B 16, C 1 (31 t0), D 8 (38 and 52, four each), E 0. The primary classes agree with the reviewers'; the contributing classes change on 34 GT and t1 (D removed) and 31 t1 (B removed).

## 4. GT failures, unstable tasks, flips through the simulator

- GT failures: 7 (32, 34, 38, 39, 46, 49, 52). B 5 (32 with A, 34, 39 with A, 46 with A, 49 with A); D 2 (38: cancel-reason gap; 52: scenario constraint conflict); A 0; C 0; E 0. GT passes: 30, 31, 43, 51.
- Unstable tasks (1 or 2 of 3 trials pass): 30 (1 0 1), 31 (0 0 1), 34 (1 0 1), 39 (0 0 1), 43 (1 0 0), 46 (0 1 0), 51 (1 0 1): 7 tasks.
- Through the simulator: 5 tasks (30, 34, 39, 43, 46), all 5c-infidelity at task level. By failing trial: 6 infidelity (30 t1, 34 t1, 39 t0, 43 t1, 43 t2, 46 t2, the last one weak) and 1 borderline gap (39 t1, agent contributing).
- Through the agent: 31 (t0 C with A, t1 A), 51 (t1), and 46 t0. Stable: 32, 38, 52 (0 of 3), 49 (3 of 3).

## 5. 2j cross-check

Judge-only failures (DB matched, an assertion unmet) in these tasks: 46 t0 and 46 t2.

| run | assertion | live vote | 3-vote majority | transcript | reading |
|---|---|---|---|---|---|
| 46 t0 | "Agent should tell the user the total paid for remaining items is $1,497.65." | unmet | unmet (0 of 3 met) | never in a message; 1,497.65 appears only in the `transfer_to_human_agents` summary argument at [26], which the judge does not see (`evaluator_nl_assertions.py` l.75-77 renders `role: content` only) | agree: unmet; agent omission (A) |
| 46 t2 | same | unmet | unmet (0 of 3 met) | [22] gives 622.12 (canister vacuum) and 2623.69 (whole order), never 1497.65 | agree: unmet |

All other judged assertions of these tasks (38, both assertions, 4 runs; 39, 4 runs; 43, three assertions, 4 runs; 46 assertion 1, 4 runs; 46 t1 assertion 2) are met by the live vote and by 3 of 3 votes, and the transcripts state them. No class E; every 2j row stays 0.

## 6. Rows filed 0, checked

- 1e: 30, 31, 43, 51 reached 1.0; 32 (B, A), 34 (B), 39 (B, A), 46 (B, A), 49 (B, A) hold at 0.
- 4f: 30, 32, 38 (already in 38/4c), 39, 43, 46, 49, 51, 52 (already in 52/4a) hold at 0.
- 5c: 31 and 51 ("agent"), 32, 38, 52 (0 of 3) and 49 (3 of 3) hold at 0.
- 5d: 38 (an allowed reason chosen inside a gap) and 52 (the user holds a stated constraint; supervisor requests in a situation without instruction, persona-scripted) hold at 0.
- 2j: all eleven hold at 0.

## 7. Effect on the p2 rows

| check | filed defect rows | after this part |
|---|---|---|
| 1e | 2 (38 medium, 52 high) | 2 (38 medium, 52 medium) |
| 4f | 2 (31, 34) | 1 (31) |
| 5c | 5 (30, 34, 39, 43, 46) | 5 |
| 5d | 9 (30, 31, 32, 34, 39, 43, 46, 49, 51) | 9 |
| 2j | 0 | 0 |
| total | 18 | 17 |

All eleven tasks keep at least one agent-run defect row. Without the simulator checks 5c and 5d, the p2 tasks with an agent-run defect row go from 4 (31, 34, 38, 52) to 3 (31, 38, 52). Task 34 has no static medium or high row, so it leaves the count that excludes 5c and 5d.

## 8. Could not verify; open questions

Could not verify:
- Simulator behaviour under counterfactuals (model calls prohibited): whether the simulator accepts 9228757377 in 52 when the conflict is stated plainly (4 of 4 runs refused); whether it confirms the profile address in 34 when it does not know the street (2 of 4 accepted); how often 39's "Your current address should be in your recent order" is read as the old address (2 of 4 runs).
- Hash effects were taken from `db_match` and from the static probes (probe_2d row 30_8; the static replay of 38_10), not replayed. The extra writes in 31 t1 (return) and 51 t1 (cancel) change an order status, so their hash difference follows from the tool semantics.
- The simulator system prompt was not re-rendered; persona clauses come from `language_context.persona`. The end of an episode after a transfer was taken from `guidelines.py` and the transcripts, not from the orchestrator code.

Open questions:
1. 52/1e severity: medium under rule 7 as written; high under a reading that requires a scenario-faithful simulator.
2. 39: if "Your current address should be in your recent order" (after "your address is still the old one") is judged ambiguous task text, rule 8 moves the event from fidelity to task text: 39/5d to 0, 39/4f to 1 medium, 39/5c tag to 5c-gap. Here it is read as plain: "current" stands against "old", and the order is the user's only source of the new address.
3. 43: if accepting a transfer with an unconditional request still unmade counts as part of the scripted escalation, 43/5c becomes 5c-gap and 43/5d rests only on the weak t2 [16] fabrication.
4. 46/5c is weak: if t2 [21] is read as wording, the tag becomes 5c-gap; if the agent's partial answer is taken as decisive, 46/5c becomes 0 ("agent").
5. Observation: tasks 34 ("an interesting guy called Noah Patel") and 43 ("a lonely man") ran with the female-caller persona; no verdict here depends on it.
6. Builder convention for 52/1e `skeptic_ok` (section 1).

## 9. Disclosures

- Opened outside the listed inputs: `results/retail/runs/retail_pass3_haiku/results.json` and `results/retail/runs/retail_gt_haiku/results.json`, through Python only, for the top-level and per-simulation keys and, for the p2 simulations, `task_id`, `trial`, `termination_reason`, reward and `language_context.persona` (id, gender, pragmatics clauses); the embedded task list was not printed. The tool harness displayed `tau2-bench/AGENTS.md` and `tau2-bench/src/tau2/evaluator/AGENTS.md` when files in those folders were read. Directory listings of `retail/`, `results/retail/`, `results/retail/runs/` and the trajectory folder; the section headings of `results/retail/review_agent_A.md` while locating the batches.
- Commands inside `tau2-bench/`: one read-only `grep -n` on `src/tau2/evaluator/evaluator_nl_assertions.py`. No `uv`, no replay, no git, no edit.
- Temporary folder: a helper script for printing transcripts was created and deleted before any output was written; the folder holds only the three outputs.
- Not opened: `tasks.json`, `task_issues/`, `report.md`, `README.md`, `ONE_PAGER.md`, `retail/summary_numbers.md`, `retail/comparison.md`, and the folders and outputs of the other parts.
