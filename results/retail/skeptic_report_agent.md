# Adversarial review of the retail agent-run rows: combined result

Date: 2026-10-28. Brief: `retail/skeptic_brief_agent_parts.md`.

The review ran in four parts on disjoint task sets, and the rules were fixed in advance. Each part's own files:
- verdicts: `skeptic_verdicts_agent_<part>.csv`;
- corrected rows: `review_agent_overrides_<part>.csv`;
- report: `skeptic_report_agent_<part>.md`.

The rows covered are checks 1e, 4f, 5c, 5d and 2j on the 45 tasks with a failed or flipped trajectory. All 74 rows with defect = 1 were reviewed, and every row with defect = 0 was checked under the same rules.

## Rows

| | p1 | p2 | p3 | p4 | all |
|---|---|---|---|---|---|
| tasks | 12 | 11 | 11 | 11 | 45 |
| defect rows reviewed | 16 | 18 | 21 | 19 | 74 |
| hold as filed | 14 | 16 | 19 | 17 | 66 |
| set to 0 | 2 | 1 | 2 | 2 | 7 |
| moved to another severity | 0 | 1 | 0 | 0 | 1 |
| raised from 0 to 1 | 1 | 0 | 0 | 1 | 2 |
| defect rows after the review | 15 | 17 | 19 | 18 | 69 |

The changed rows:

- **Set to 0:**
  - 15/4f and 34/4f: the same event was already filed as a simulator departure (15/5d, 34/5d), and rule 8 files one event once.
  - 16/5d, 64/5d and 100/5d: the simulator only made a choice the scenario leaves open, and that choice is already carried by a task-text row.
  - 72/5c: in the failing trial the agent behaved differently before the simulator replied.
  - 104/5d: the scenario's trigger for the withheld request never occurred.
- **Moved:** 52/1e from high to medium. The reference is policy-compliant and reachable if the user lets "maximum zoom" win over "all other specifications the same", which the scenario does not settle.
- **Raised:** 1/5c and 98/5c, both flips that run through a choice the scenario leaves open.

## What the counts become

| quantity | as filed | after the review |
|---|---|---|
| ground-truth failures (23): task or scoring (1e) / simulator / agent | 8 / 12 / 3 | 8 / 12 / 3 |
| ground-truth failures where no compliant conversation reaches the reference (1e high) | 52, 105 | 105 |
| unstable tasks (32) whose flip runs through the simulator (5c) | 23 | 24: 21 simulator departures, 3 choices the scenario leaves open (1, 98, 104) |
| reviewed tasks (45) with a simulator departure (5d) | 36 | 32 |
| findings the runs added to the static log (4f) | 6: 0, 1, 15, 31, 34, 100 | 4: 0, 1, 31, 100 |
| defective tasks, all checks | 67/114 | 67/114 |
| defective tasks, without 5c and 5d | 48/114 | 46/114 (15 and 34 leave) |
| defective tasks, static reading and probes only | 44/114 | 44/114 |

The other unstable tasks flip through the agent (7: 0, 9, 28, 29, 31, 51, 72) or through the judge (1: task 110).

The judge check (2j) keeps one row, 110/2j (medium). Across the three trials of task 110, the judge gave 5 "met" votes out of 9 on agent turns that say the same thing. On 110 t1 the 3-vote re-judge says "met" (2 to 1), while the transcript shows no address write, so the original "unmet" is kept. In the other judge-only failures of the 45 tasks, the verdict matches the transcript.

The only medium or high row in `retail/audit_log.csv` without an adversarial verdict is the benchmark-level 2j row (task_id ALL). It follows from counted parser rejections, not from a reading.

## Consistency across the parts

- **One convention fixed by the coordinator.**
  - Part p2 marked the re-filed 52/1e with `skeptic_ok` = 0 for the row as filed.
  - The static phase and part p4 mark a row that holds after its override with 1.
  - `skeptic_verdicts_consistency.csv` therefore marks the corrected medium row 1 and keeps the part's note. The value of the row is unchanged.
- **Rule 3** (the agent behaved alike) was read the same way in all parts. The agent's behaviour is compared at the decisive turn.
  - An agent slip that follows a simulator departure keeps the flip on the simulator (71, 101, 108).
  - An agent that behaves differently before the departure moves the flip to the agent (72, task 0).
- **Personas.** The retail runs also assign a simulator persona, as the airline runs do; `priya_patil` scripts a request for a supervisor. All parts counted such a request only where it replaces a scenario instruction or leaves a request unmade.

## Readings that could go the other way

| row | as decided | the other reading | effect of the other reading |
|---|---|---|---|
| tasks 15, 39, 59, 91 | the scenario sentence read as plain, so the simulator's reading is a departure | a garbled or loose sentence, so the gap is the task's | 4f = 1 on each, and 5d = 0 on 39 and 91; the count without 5c and 5d rises by up to 4 (to 50); for 15, the ground-truth failure moves from simulator to task (simulator 11 of 23) |
| 80/5d | holds: the simulator refused the exchange it asked for, on a condition the scenario never gives | part of the persona | task 80 has no other defect: all checks 67 to 66 |
| 28/5d | 0: gap filling | the request for a human replaced the agent's next step | all checks 67 to 68 |
| 104/5d | 0: trigger never fired | the agent's lock warning was the trigger | 5d 32 to 33; counts unchanged |
| 52/1e | medium | high, if the simulator must keep every stated constraint | counts unchanged |
| 0/5c, 43/5c, 46/5c | 0; infidelity; infidelity (weak) | 1 (gap); gap; gap or agent | 5c between 23 and 25 |

These readings decide single tasks. Taken together they move the all-checks count to between 66 and 68 of 114 and the count without 5c and 5d to at most 50. The count from reading and probes (44/114) does not depend on them.

## Disclosures from the parts

- Every part read the two run `results.json` files through read-only Python, for personas, rewards and stop reasons.
- Inside `tau2-bench/` the parts ran only read-only `cat`, `sed`, `grep`, `ls` and `wc`. There were no replays, no model calls, no network access and no git commands.
- Part p1 left four read-only helper scripts in a scratch folder outside its output folder.
- All reviewers are language models, not people.
