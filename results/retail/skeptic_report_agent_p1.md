# Adversarial review of the retail agent-run rows, part p1

Date: 2026-10-28. Tasks 0, 1, 5, 9, 11, 15, 16, 19, 21, 27, 28, 29. Object: their 60 rows in `results/retail/review_agent.csv` (1e, 4f, 5c, 5d, 2j per task; 16 with defect=1), filed by trajectory batches A (0-19) and B (21-29). Every one of the 35 rendered trajectories of these tasks was read (all failed runs and every trial of the flipped tasks). Every amount a row depends on was recomputed from the task-card catalog. Row verdicts: `skeptic_verdicts_agent_p1.csv`; value changes: `review_agent_overrides_p1.csv`.

Terms: GT = ground-truth agent (`llm_agent_gt`, sees the reference actions); t0/t1/t2 = Haiku trials; DB = database; [n] = turn marker. Classes: A agent slip, B simulator deviation, C defensible alternative reading, D reference or scoring problem, E judge error.

## 1. Verdicts

| task | check | filed | verdict | why |
|---|---|---|---|---|
| 0 | 4f | 1 medium | holds | t0 [14]-[17]: the scenario's "Google Home" is absent from the catalog (only Google Assistant); whether the substitute satisfies the requirement is a yes/no the scenario never settles and the reference fixes (rule 5); static 0/4d = 0 |
| 1 | 1e | 1 medium | holds | GT [14]-[19]: compliant GT agent cannot confirm Google Home, the user declines, no write; reachable (t2), so medium |
| 1 | 4f | 1 medium | holds | same gap stops GT, t0, t1; no static defect row (1/4d = 0) |
| 1 | 5c | 0 | escalated to 1 medium (5c-gap) | agent alike in t0 [14], t1 [14], t2 [13]; only the simulator's choice inside the gap differs (rule 3, airline task 8) |
| 5 | 5c | 1 medium | holds (5c-infidelity) | same two-step confirmation in all trials; t1 [24], t2 [22] approve the lamp exchange, t0 [24] switches to the return |
| 5 | 5d | 1 medium | holds | second-confirmation instruction withheld at its trigger in t1 and t2 |
| 11 | 5c | 1 medium | holds (5c-infidelity) | same refusal and offer in all trials; t2 [15] asks for a human instead of agreeing |
| 11 | 5d | 1 medium | holds | rule 2: the human request replaces "then agree to return all things with the original payment method"; persona wording does not exempt it |
| 15 | 4f | 1 medium | fails, set to 0 | same event as 15/5d (rule 8); the material-change reading is the simulator's addition, not a gap (rule 5); no agent read the task differently |
| 15 | 5c | 1 medium | holds (5c-infidelity) | all agents offer 3613716226; t2 [1], [17] invents a leather wish and a keep-the-boots fallback |
| 15 | 5d | 1 medium | holds | GT [21] size 9 against "size 8"; GT [1], [19] and t2 [1], [17] fabricated material change |
| 16 | 1e | 1 medium | holds | refund destination open (static 16/4c); the GT end state is the other compliant state; A contributes ([20] unsupported timing claim) |
| 16 | 5d | 1 medium | fails, set to 0 | GT [15] speed preference is gap-filling for the open refund destination (rule 1 exclusion); same event as 16/1e (rule 8) |
| 19 | 5d | 1 medium | holds, weak | rule 2: GT [20] insists on both and asks for a human where the scenario says to prefer the bigger saving and ask both savings; agent-made dead end |
| 21 | 5c | 1 medium | holds (5c-infidelity) | same combined proposal ($41.92, $44.08 left) in all trials; t2 [27]-[29] backs out of the keyboard swap |
| 21 | 5d | 1 medium | holds | t2 [29] declines the keyboard swap the scenario requests, with an invented reason; decisive |
| 29 | 5d | 1 medium | holds on t2 [18] only | false "the hose in there is a different item" after the agent named the correct pending-order hose; the opener "not the one I ordered" has no bearing and would not count alone |

Counts: 16 defect=1 rows reviewed; 14 confirmed; 2 rejected (15/4f, 16/5d); 0 re-filed; 1 escalation (1/5c). No severity change. Every defect=0 row of the twelve tasks was also checked against the rules; apart from 1/5c none changes (the borderline ones are in section 2).

## 2. Rules as applied

**Rule 1 and rule 2 (5d).** Counted: 5 (instruction withheld at its trigger), 11 and 19 (human request replacing the scenario's instruction for that situation), 15 (fabricated material change and contradicted size), 21 (contradicts the stated request), 29 t2 [18] (false statement that redirects the agent). Not counted:
- 0 and 1: declining an unconfirmed Google Assistant thermostat is a choice inside a gap.
- 16 GT [15]: "as soon as possible" only resolves the open refund destination (gap-filling, airline 44 precedent).
- 27 (all runs): escalation after an agent-made dead end; the scenario's instruction for that case ("prefer the exchange") is stated (GT [22], t0 [22]).
- 28 t2 [26], [28]: escalation after the agent made the backpack return impossible ([21], [23]). The scenario has no instruction for a refused return. The simulator holds the remaining returns behind the impossible one, which is the gap-filling that airline 44 did not count. Borderline; kept at 0.
- 29 [1] in all trials: "not the one I ordered" has no bearing on what the agent must do.
- 5 t0 [22]: quotes the scenario without contradicting it.

**Simulator personas (new to the retail rows).** The retail runs assign the same two personas as airline. Source: `language_context.persona` in both `results.json` files.
- `priya_patil`: tasks 9, 11, 16, 19, 27 and 28.
- `mamadou_diallo`: tasks 0, 1, 5, 15, 21 and 29.

The trajectory reviewers did not check the persona.
- Escalation sentences that copy the `priya_patil` clauses word for word ("Can I just talk to someone who can actually fix this", "No, that doesn't work for me", "Okay, like I literally just told you") occur in 11 t2 [15], 19 GT [20], 27 GT [24], 27 t1/t2 [24] and 28 t2 [26]/[28]. Rule 2 decides each case: counted in 11 and 19, not counted in 27 and 28.
- The `mamadou_diallo` decline style ("Honestly I'd rather not do that if there's another way", give a reason) appears in 21 t2 [17]/[29] and 15 t2 [17]. It scripts how to decline, not whether, so it does not excuse declining what the scenario asks for.

**Rule 3 (5c).**
- Task 1 is escalated to 5c-gap.
- Task 0 stays 0 (note: "agent"): the agent's framing of the gap differs in a way that bears on the outcome. t0 [14] says the catalog has no Google Home option. t1 [14] asserts an equivalence the catalog does not state ("Google Home is listed as Google Assistant"). t2 [12] lists the variants neutrally.
- Tasks 9, 28 and 29 flip on agent slips: 9 t0 [19] falsely says the AC/battery high-brightness lamps are unavailable (7624783998 is available at $154.17); 28 t2 [21]/[23] splits one return into two; 29 t0/t1 [17]/[21] omit the $180.10 option.

**Rule 5, the uneven gap filing named in the brief.** Tasks 0, 1 and 15 are in this part; 98 and 100 are in p4.
- 0 and 1: gap (D). 4f = 1 on both tasks, 1e = 1 on task 1, 5d = 0. 5c is 1 (gap) for 1 and 0 for 0.
- 15: not a gap. The text names no change of material, and its plain reading gives the reference. Filed as B: 5d = 1, 5c = 1 (infidelity), 4f set to 0, 1e = 0.

The difference: in 0/1 both accepting and declining the substitute are faithful to the scenario, while in 15 the failing reading needs content that the text does not contain.

**Interpretation stated.** In rule 5, "the static log already carries the same mechanism" is read as a static row with defect=1. Static 0/4d and 1/4d mention the Google Home naming difference but log it as defect=0 ("harmless"), so the 4f rows stay at 1.

**Rules 6-10.**
- No class E (section 5).
- 1e severity is medium for 1 and 16, because a compliant conversation reaches the target in both (1 t2; 16 Haiku 3/3).
- Rule 8 decided 15/4f and 16/5d.
- Severities follow the checklists.
- Amounts recomputed:

| task | amounts |
|---|---|
| 0 | 3.17 + 13.46 = 16.63 |
| 5 | +12.07 |
| 9 | 7624783998 available at 154.17 |
| 15 | 0.35; 2648909398 unavailable |
| 16 | 3131.10 + 4777.75 + 367.38 = 8276.23 |
| 19 | 14.18 + 27.46 = 41.64; refund 54.04 |
| 21 | 8.28 + 33.64 = 41.92; 86.00 - 41.92 = 44.08; 86.00 - 8.28 = 77.72 |
| 28 | 918.43 |
| 29 | 180.10, 189.57, 208.60; 5206946487 = 50ft vinyl black |

**Departures from the rules:** none.

## 3. Cause classes per trajectory after this pass

| task | trajectory | reward | DB | class | 5c tag | decisive turns |
|---|---|---|---|---|---|---|
| 0 | t0 | 0 | no | D | - | [14]-[17], [20] |
| 0 | t1, t2 | 1 | yes | success (t1 passes after an unsupported equivalence claim, [14]) | | |
| 1 | GT | 0 | no | D | | [14]-[19] |
| 1 | t0 | 0 | no | D | 5c-gap | [15]-[17] |
| 1 | t1 | 0 | no | D | 5c-gap | [15]-[19] |
| 1 | t2 | 1 | yes | success | | [13]-[14] |
| 5 | t1 | 0 | no | B | 5c-infidelity | [23]-[25] |
| 5 | t2 | 0 | no | B | 5c-infidelity | [21]-[23] |
| 5 | t0 | 1 | yes | success | | [23]-[27] |
| 9 | t0 | 0 | no | A | | [17], [19] |
| 9 | t1, t2 | 1 | yes | success | | |
| 11 | t2 | 0 | no | B | 5c-infidelity | [15] |
| 11 | t0, t1 | 1 | yes | success | | |
| 15 | GT | 0 | no | B | | [1], [19], [21] |
| 15 | t2 | 0 | no | B | 5c-infidelity | [1], [17] |
| 15 | t0, t1 | 1 | yes | success | | |
| 16 | GT | 0 | no | D (A) | | [14], [15], [20], [21], [24] |
| 19 | GT | 0 | yes | A (B) | | [15], [19], [20] |
| 21 | t2 | 0 | no | B | 5c-infidelity | [27], [29], [32] |
| 21 | t0, t1 | 1 | yes | success (1g corruption visible, already in 21/1g) | | |
| 27 | GT, t0, t1, t2 | 0 | no | A | | GT [15]-[20]; t0 [17]-[21]; t1, t2 [17]-[22] |
| 28 | t2 | 0 | no | A (simulator escalation borderline, not counted) | | [21], [23], [26], [28] |
| 28 | t0, t1 | 1 | yes | success | | |
| 29 | t0, t1 | 0 | yes | A | | [17], [21] |
| 29 | t2 | 1 | yes | success (B at [18], no reward effect) | | |

Failed trajectories: 20; A 9, B 6, D 5, C 0, E 0. The changes from the batch readings: 15 GT and 15 t2 drop the D contribution; 16 GT carries A rather than B as the contributing class.

## 4. GT failures and unstable tasks

- GT failures (5): D 2 (1, 16); B 1 (15); A 2 (19, 27). Rule 7 gives 1e = 1 medium for 1 and 16, and 0 for the rest.
- Unstable tasks (1 or 2 of 3): 0, 1, 5, 9, 11, 15, 21, 28, 29 (9 tasks).
  - Flips through the simulator: 5. Infidelity: 4 (5, 11, 15, 21). Gap: 1 (1).
  - Flips on the agent: 9, 28, 29.
  - Task 0: the flip follows the agent's framing of a gap; the gap itself is carried by 0/4f.
- Stable failure: 27 (0/3, all class A). A compliant path exists: say that only one of the two actions is possible, and the scenario makes the user choose the exchange.

## 5. 2j cross-check (live single vote against the 3-vote majority in `rejudge.csv`)

| run, task, trial | DB | assertion | live | 3 votes (met/unmet) | transcript | verdict |
|---|---|---|---|---|---|---|
| GT 19 | yes | $54.04 refund | met | 3/0 | [15], [19] state 54.04 | agree |
| GT 19 | yes | exchange saves $41.64 | unmet | 0/3 | 41.64 in no agent turn | agree, judge-only failure, class A (B) |
| pass3 29 t0 | yes | $180.10, $189.57, $208.60 | unmet | 0/3 | 180.10 only in the tool result; [21] "the only 28-inch bamboo options" | agree, judge-only failure, class A |
| pass3 29 t1 | yes | same | unmet | 0/3 | same, [21] | agree, judge-only failure, class A |
| pass3 21 t2 | no | balance $44.08 | unmet | 0/3 | 44.08 only as a conditional at [26]; balance stated $77.72 at [30], [34] | agree |
| pass3 28 t2 | no | total $918.43 | unmet | 0/3 | no total stated | agree |
| all passing runs of 16, 19, 21, 28, 29 and GT 16 | | | met | 3/0 | the amounts appear in assistant turns (checked in `results.json` for the unrendered 16 and 19 Haiku trials and the GT runs) | agree |

Live votes equal the majority on every assertion of these tasks; the transcripts support both. No class E.

## 6. Effect on counts (part p1 only)

- Defect=1 run rows: 16 -> 15. By check:
  - 1e: 2 -> 2
  - 4f: 3 -> 2 (15 leaves)
  - 5c: 4 -> 5 (1 enters)
  - 5d: 7 -> 6 (16 leaves)
- Defective tasks counting all rows: 9 of 12, unchanged (0, 1, 5, 11, 15, 16, 19, 21, 29).
- Defective tasks counting all rows except 5c and 5d: 5 -> 4 (0, 1, 16, 21). Task 15 leaves, because it has no static medium/high row.

## 7. Observations without a defect row

- 15: "want the material" is ungrammatical, and 2 of 4 runs misread it. The text is a weak spot, but the failures are carried as B.
- 0 t1: the pass rests on an agent claim that policy.md l.18 forbids. The DB hash cannot see statements; this is the benchmark-level 2m blind spot.
- 21 t0, t1: the 1g corruption shows in the order record. The agent reports it and transfers, and the task still scores 1.0 (already in 21/1g).
- 27: an agent that ran the exchange before the return would end in the reference state without ever telling the user that only one action is possible. The end state still matches the user's stated preference, so this is not a scoring defect.

## 8. Could not verify, and open questions

Could not verify:
- No counterfactual simulator samples were run, because they need model calls. Three questions stay open:
  - how often the simulator raises Google Home when the agent lists neutrally (tasks 0 and 1);
  - how often it reads "want the material" as a change (task 15);
  - whether it would have asked about the savings in 19 if the one-of-two limit had been stated before the return.
- The Haiku trials of 16 and 19 are not rendered. Only the asserted amounts and the recorded verdicts were checked in `results.json`, not the whole conversations.
- The rendered simulator system prompt was not reconstructed. The persona clauses come from `pack.yaml`, and the assignment from `results.json`.
- The upstream `issues` entry of task 5 was not opened (by rule), so it is unknown whether it describes the double-confirmation mechanism.

Open questions:
1. 0/5c: if "the agent behaved alike" means the same proposed items, regardless of how the gap is framed, then 0/5c = 1 (5c-gap) as in task 1.
2. 15: if the coordinator treats ungrammatical scenario text as task-side, as task 70 was routed to 4f, the alternative is 4f = 1, 1e = 1 medium, 5c tagged gap, and 5d resting on GT [21] alone. In that case task 15 returns to the count without 5c/5d.
3. 28/5d: borderline. Under the reading "the human request replaced the next scenario step that the agent offered (keyboard and bed, [25], [27])", it would be 1 medium (no reward effect).
4. Static 0/4d and 1/4d log the Google Home / Google Assistant mismatch as harmless, but it decides 4 of 7 runs. Static 18/4d was escalated on a similar presupposition. Static rows are outside this part's object, so no change is proposed here.

## 9. Disclosures

- **Files opened outside the listed inputs.**
  - `results/retail/runs/retail_pass3_haiku/results.json` and `results/retail/runs/retail_gt_haiku/results.json`. Read by script only, for three things: the per-simulation persona and caller gender; the assistant-message text of tasks 16, 19, 21, 28 and 29, to check the asserted amounts; the recorded nl verdicts. The embedded task list was not printed.
  - `tau2-bench/data/tau2/multilingual/en/pack.yaml` (persona clauses), plus a directory listing of `tau2-bench/data/tau2/multilingual/en/`. `retail_tasks_en.json` in that folder was not opened.
  - The forbidden files were not opened. Directory listings showed the names of `retail/summary_numbers.md` and `retail/comparison.md`, and neither was read.
- **Commands run inside `tau2-bench/`** (all read-only, no replay):
  - `cat -n` on `data/tau2/domains/retail/policy.md`
  - `cat -n`, `sed -n` and `wc -l` on `src/tau2/user/guidelines.py`
  - `grep -n`, `sed -n` and `wc -l` on `src/tau2/evaluator/evaluator_nl_assertions.py`
  - `grep -n -A 60` for the definition of return_delivered_order_items in `src/tau2/domains/retail/tools.py`
  - `ls`, `wc -l`, `grep -n` and `sed -n 1,160p` on `data/tau2/multilingual/en/` and its `pack.yaml`

  No `uv`, no install, no git, no model or network call, nothing edited.
- **Files created outside the three outputs (departure from the brief's file rule).** Four read-only helper scripts are in a sibling scratch folder, `<temporary folder>\skeptic_retail_p1_work\` (`keys.py`, `persona.py`, `tx.py`, `amounts.py`). They render transcripts and extract fields; they change no file.
