# Summary numbers — retail

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb`; all 114 tasks of the base split (no sampling).

Intervals: 95% Wilson.

Table 1. Headline shares

| quantity | share |
|---|---|
| defective tasks (≥1 confirmed medium/high row) | 57/114 = 0.500 [0.410, 0.590] |
| defective tasks, static and probe checks only (method ≠ agent_run) | 44/114 = 0.386 [0.302, 0.478] |
| defective tasks, agent_run checks only (1e, 4f, 5c, 5d, 5e, 5f) | 23/114 = 0.202 [0.138, 0.285] |
| defective tasks, agent_run checks excluding 5d (user-simulator deviations) | 23/114 = 0.202 [0.138, 0.285] |
| tasks whose only confirmed defects come from agent_run checks | 13/114 = 0.114 [0.068, 0.185] |
| defective tasks, excluding the no-op class (checks 2a, 2b, 2c) | 51/114 = 0.447 [0.359, 0.539] |
| defective tasks, excluding every defect that derives from the no-op design (2a, 2b, 2c, and 2k on no-op tasks) | 51/114 = 0.447 [0.359, 0.539] |
| no-op pass by construction (empty answer = full reward), all tasks | 6/114 = 0.053 [0.024, 0.110] |
| no-op verdict left to the judge (DB unchanged, assertions exist) | 5/114; the judge failed all of them in the probe |
| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | 23 |

Table 2. Tasks with ≥1 confirmed defect (high/medium), by category

| category | share of all tasks |
|---|---|
| 1 Solvability | 29/114 = 0.254 [0.183, 0.341] |
| 2 Scoring validity | 30/114 = 0.263 [0.191, 0.351] |
| 3 Isolation and leaks | 0/114 = 0.000 [0.000, 0.033] |
| 4 Specification clarity | 17/114 = 0.149 [0.095, 0.226] |
| 5 Determinism | 0/114 = 0.000 [0.000, 0.033] |
| 6 Reporting | 0/114 = 0.000 [0.000, 0.033] |

Table 2b. Confirmed defect rows by check (all methods)

| check | defect rows (high/medium) | tasks |
|---|---|---|
| 1b | 1 | 1/114 |
| 1d | 2 | 2/114 |
| 1e | 23 | 23/114 |
| 1g | 5 | 5/114 |
| 2a | 6 | 6/114 |
| 2b | 6 | 6/114 |
| 2c | 2 | 2/114 |
| 2e | 14 | 14/114 |
| 2h | 5 | 5/114 |
| 2k | 3 | 3/114 |
| 2m | 5 | 5/114 |
| 4a | 1 | 1/114 |
| 4b | 1 | 1/114 |
| 4c | 11 | 11/114 |
| 4d | 3 | 3/114 |
| 4e | 2 | 2/114 |

Benchmark-level defect rows (task_id = ALL): 1g (medium), 2e (medium), 2m (medium), 5b (low), 6d (low), 6f (low), 6g (low)

Table 3. Low-severity defects, by category (informational)

| category | rows | tasks |
|---|---|---|
| 1 Solvability | 4 | 4/114 |
| 2 Scoring validity | 0 | 0/114 |
| 3 Isolation and leaks | 0 | 0/114 |
| 4 Specification clarity | 2 | 2/114 |
| 5 Determinism | 0 | 0/114 |
| 6 Reporting | 0 | 0/114 |

Table 4. Agent runs (claude-haiku-5-5 agent and user; stock scorer; NL judge claude-haiku-5-5, one vote, in the loop)

| quantity | value |
|---|---|
| pass^1, all tasks (first 1 trial(s) all reward 1.0) | 93/114 = 0.816 [0.735, 0.876] |
| pass^2, all tasks (first 2 trial(s) all reward 1.0) | 84/114 = 0.737 [0.649, 0.809] |
| pass^3, all tasks (first 3 trial(s) all reward 1.0) | 75/114 = 0.658 [0.567, 0.739] |
| pass^1, tau2 estimator (mean over tasks of C(c,k)/C(n,k); k = 1 is the average reward tau2 prints) | 0.807 (n = 114 tasks) |
| pass^2, tau2 estimator (mean over tasks of C(c,k)/C(n,k); k = 1 is the average reward tau2 prints) | 0.713 (n = 114 tasks) |
| pass^3, tau2 estimator (mean over tasks of C(c,k)/C(n,k); k = 1 is the average reward tau2 prints) | 0.658 (n = 114 tasks) |
| tasks solved in 0/3 trials | 7/114 = 0.061 [0.030, 0.121] |
| tasks solved in 1/3 or 2/3 trials (unstable) | 32/114 = 0.281 [0.206, 0.369] |
| tasks solved in 3/3 trials | 75/114 = 0.658 [0.567, 0.739] |
| Haiku trials failed by the judge alone (DB matched, an assertion unmet) | 9/342 = 0.026 [0.014, 0.049] of evaluated trials |
| ground-truth agent reaches reward 1.0 | 89/112 = 0.795 [0.711, 0.859] |
| ground-truth runs failed by the judge alone (DB matched) | 3/112 = 0.027 [0.009, 0.076] |
| Haiku passes ≥1 trial, ground-truth agent fails | 16 |
| ground-truth agent passes, Haiku 0/3 | 0 |
| infrastructure_error simulations excluded | 0 |

- ground-truth agent fails on tasks: 1, 15, 16, 19, 27, 32, 34, 38, 39, 46, 49, 52, 64, 80, 82, 87, 93, 98, 100, 101, 103, 105, 108
- Haiku passes ≥1 trial, ground-truth agent fails: 1, 15, 16, 19, 34, 39, 46, 49, 80, 82, 87, 93, 98, 101, 103, 108
- ground-truth agent passes, Haiku 0/3: none

Table 5. Blind re-review of 12 tasks (labels compared on defect 0/1 per task x check)

| comparison | agreement | Cohen's kappa |
|---|---|---|
| blind vs original reviewer labels | 97/98 = 0.990 | 0.852 |
| blind vs skeptic-corrected labels | 98/98 = 1.000 | 1.000 |

- tasks: 3, 7, 12, 15, 21, 24, 31, 43, 77, 83, 84, 98; rows: 102; disagreements listed in results/retail/rereview_summary.md

Table 6. The judge inside the score (check 2j)

| quantity | value |
|---|---|
| live judge replies the stock strict parser would reject | 103/169 = 0.609 [0.534, 0.680] |
| live replies with fewer results than assertions (silently uncounted by the stock code) | 0/169 |
| simulations re-judged with 3 votes | 0 |
| assertion verdicts where the live vote differs from the majority | 0/0 |
| rewards that flip under the majority (pass→fail / fail→pass) | 0 (0 / 0) of 0 |

Table 7. Upstream-recorded open issues (tasks.json → issues) against the audit rows

| task | upstream issue (title) | audit: confirmed defect rows on the task |
|---|---|---|
| 4 | Task looks for number 10, but user does not ask for a number. It is happy with "various" or a description. | 4d |
| 5 | Domain level issue. Agent is allowed to do user level actions e.g. look-up their order info, without authentic | none |
| 7 | For tasks where user does not know order ID, mention explicitly that user does not know th | none |

Table 8. Pre-registered predictions (retail/PLAN.md §3) against the measurements

| id | prediction | measured |
|---|---|---|
| P1 | no-op pass 6/114 by construction; refusal/transfer passes only where the judge accepts | static 6/114; probe 2b 6/114; probe 2c 6/114 (judge accepted the assertions of an empty answer in 0 tasks) |
| P2 | 2k only where no enforced assertion covers the communicate_info fact; certain for 30, 31, 32 | 2k confirmed on 3 tasks: 30, 31, 32 |
| P3 | 0 tasks flip on WRITE order (except shared payment_history) | 2h confirmed on 5 tasks |
| P4 | process requirements unscored (benchmark-level 2m) | 2m benchmark-level defect rows: 1; per-task 2m: 5 |
| P5 | upstream issues on 4, 5, 7 re-found | 4: 4d / 5: none / 7: none |
| P6 | some judge replies fail the strict parser; re-judge flips some verdicts | 103/169 = 0.609 [0.534, 0.680] rejected; reward flips 0 (0 / 0) of 0 |
| P7 | defective share, no numeric prediction | 57/114 = 0.500 [0.410, 0.590] (airline sample: 18/20) |

Rule of three (k = 0)

- category 3 Isolation and leaks: 0/114 → upper bound by the rule of three ≈ 3/114 = 0.026
- category 5 Determinism: 0/114 → upper bound by the rule of three ≈ 3/114 = 0.026
- category 6 Reporting: 0/114 → upper bound by the rule of three ≈ 3/114 = 0.026
