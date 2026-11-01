Agent benchmarks, exams for AI agents, rank models by pass rate (share of tasks completed) and support deployment decisions. Do they measure the agent? This work audits tau2-bench v2.0.0, a widely used customer-service exam (airline: all 50 tasks, 20 sampled first and the other 30 audited afterwards with the same method; retail: all 114 tasks). It also measures a do-nothing agent's score on tau2 and on four external benchmarks (BFCL V4, the original tau-bench, OSWorld-Verified, WebArena in two versions).

The audit uses a fixed checklist of 49 checks (retail added two): reading the task and its scoring, tests with known outcomes, and paid agent runs. Each task gets the 23 to 28 checks that apply to a single task, checks about the benchmark as a whole are done once, and hypotheses and predictions were recorded before reading results. Every finding about a task went through adversarial review (an attempt to overturn it); a second model reviewer re-labelled 18 sampled tasks blind (earlier labels hidden) and agreed with the original labels on 147 of 153 (96%), and the adversarial review settled the 6 differences, each in favour of the blind reader. Scripts rebuild every number from recorded files, except a few counts taken from review reports and the leaderboard scores read from a web page.

34 of 50 airline tasks carry at least one confirmed medium- or high-severity defect (44 of 50 counting the pass for doing nothing), and an agent that does nothing passes 23 of 50 airline tasks of the pinned benchmark ([airline_full/summary_numbers.md](https://github.com/Scienceconsult94/AI_safety_project/blob/main/airline_full/summary_numbers.md), [summary_numbers.md](https://github.com/Scienceconsult94/AI_safety_project/blob/main/summary_numbers.md)).

In retail, 61 of 114 tasks carry such a defect (38 from reading and probes alone; the 6 tasks that pass for doing nothing counted on their own line) ([retail/summary_numbers.md](https://github.com/Scienceconsult94/AI_safety_project/blob/main/retail/summary_numbers.md)).

On the original tau-bench airline set an agent that does nothing scores 38% (19 of 50) with the benchmark's own reward code; four published runs on the HAL leaderboard score below that floor, at 28%, 36%, 36% and 36% ([results/null_agent/external.md](https://github.com/Scienceconsult94/AI_safety_project/blob/main/results/null_agent/external.md), [results/null_agent/hal_check.md](https://github.com/Scienceconsult94/AI_safety_project/blob/main/results/null_agent/hal_check.md)).

Limitations (from the repository's README):

- Airline: all 50 tasks; 20 were sampled before any run (block 1), and the other 30 were audited afterwards with the same pipeline (report Section 13).
- Retail: all 114 tasks; the findings from its agent runs went through their own adversarial review, and a few rest on readings that could go the other way (report Section 5).
- Required information is checked by the substring scorer in every run, not by the v2.0.0 default semantic judge; on the recorded airline runs the two agree on all 58 verdicts (check 2j).
- Every reviewer, adversarial reviewer and reader was a language model, not a person.
- One user-simulator model throughout.
- v2 has two parts: corrected task texts (a wrong reference answer, a scenario that contradicted its reference), which fix defects, and a stricter scoring rule for the pass by doing nothing, which the benchmark documents as intended; that second part is a stricter alternative, not a correction of a bug.
- The OSWorld-Verified and original WebArena floors are counted from task files, not measured by running the evaluator.
- The telecom task set of tau2-bench was not audited; only its do-nothing floor was measured.

Revising the airline exam (v2: corrected task texts and a stricter scoring protocol) cut do-nothing passes from 23 to 0 (by rule), yet the agent's score on the 20 sampled tasks stayed at 0.60; on the other 30 tasks it fell from 0.70 to 0.50, mostly because v2 also reads the requirements written only in free text. A leaderboard (public model ranking) cannot show its exam's faults. A pass rate measures three things at once: in retail the simulated customer, not the agent, explains about half the failures of an agent that knows the answer. On a public leaderboard, four published airline scores (one run each) sit below the 38% that doing nothing earns on the same tasks, and the page shows no floor to compare with. The proposal is to publish next to every agent leaderboard the do-nothing and refuse-only floors, a replay of each task's reference solution (official correct actions) as a control, the task-file version behind each score, and, with a simulated customer, the share of failures it causes.

---

## Sources for every number (not part of the post)

Line numbers refer to README.md and ONE_PAGER.md at main a3fd7e1; on the overnight branch README lines are shifted by 8 (the reviewer block added after the title).

Question paragraph
- tau2-bench v2.0.0 (version): ONE_PAGER.md line 3; README.md line 18 (tag `v2.0.0`).
- airline all 50 tasks, 20 sampled first, the other 30: ONE_PAGER.md line 3.
- retail all 114 tasks: ONE_PAGER.md line 3.
- four external benchmarks; BFCL V4; WebArena in two versions: ONE_PAGER.md line 3.

Method paragraph
- checklist of 49 checks (retail added two): ONE_PAGER.md line 5.
- 23 to 28 checks per task: ONE_PAGER.md line 5.
- 18 sampled tasks re-labelled blind: ONE_PAGER.md line 5 (cross-check: 3 + 3 + 12 tasks in results/rereview_summary.md line 1, results/rereview_summary_rest.md line 1, results/retail/rereview_summary.md line 3).
- 147 of 153 (96%): ONE_PAGER.md line 5; README.md line 5.
- the 6 differences: ONE_PAGER.md line 5.

Headline numbers
- airline 34 of 50 tasks with a confirmed medium- or high-severity defect: README.md line 5; ONE_PAGER.md line 12; linked file airline_full/summary_numbers.md line 9 (34/50 = 0.680).
- airline 44 of 50 counting the pass for doing nothing: README.md line 5; ONE_PAGER.md line 12; airline_full/summary_numbers.md line 15 (44/50 = 0.880).
- airline do-nothing passes 23 of 50: README.md line 4; ONE_PAGER.md line 13; summary_numbers.md line 20 (23/50 = 0.460); airline_full/summary_numbers.md line 17.
- retail 61 of 114: README.md line 6; ONE_PAGER.md line 14; retail/summary_numbers.md line 11 (61/114 = 0.535).
- retail 38 from reading and probes alone: README.md line 6; ONE_PAGER.md line 14; retail/summary_numbers.md line 12 (38/114 = 0.333).
- retail 6 pass for doing nothing: README.md line 6; ONE_PAGER.md line 14; retail/summary_numbers.md line 22 (6/114 = 0.053).
- original tau-bench airline do-nothing 38% (19 of 50): README.md line 8; ONE_PAGER.md lines 22 and 23; results/null_agent/external.md line 18 (19/50 = 38.0%).
- four published HAL runs below the floor at 28%, 36%, 36%, 36%: README.md line 8; ONE_PAGER.md line 23; results/null_agent/hal_check.md lines 11 and 15 to 18.

Limitations bullets (copied verbatim from README.md line 158, section "Limits")
- 50 airline tasks, 20 sampled, block 1, the other 30, report Section 13: README.md line 158.
- 114 retail tasks, report Section 5: README.md line 158.
- v2.0.0, all 58 verdicts, check 2j: README.md line 158.
- one user-simulator model: README.md line 158.
- v2 has two parts: README.md line 158.

Closing paragraph
- do-nothing passes 23 to 0 under v2 (by rule); 20 sampled tasks stayed at 0.60; other 30 tasks 0.70 to 0.50: ONE_PAGER.md line 27 (table: lines 18 and 19).
- three things at once; about half the failures: ONE_PAGER.md line 28 (12 of 23 at ONE_PAGER.md line 17).
- four published airline scores, one run each, below 38%: ONE_PAGER.md line 30.
- the proposal (floors, reference replay, task-file version, share of failures caused by the simulated customer; no number): ONE_PAGER.md line 32.
