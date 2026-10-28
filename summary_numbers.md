# Summary numbers

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb`

Intervals: 95% Wilson.

Table 1. Headline shares

| quantity | share |
|---|---|
| defective tasks, sampled tasks | 18/20 = 0.900 [0.699, 0.972] |
| defective tasks, sampled tasks, static and probe checks only (method ≠ agent_run) | 14/20 = 0.700 [0.481, 0.855] |
| defective tasks, sampled tasks, agent_run checks only (1e, 4f, 5c, 5d, 5e, 5f) | 9/20 = 0.450 [0.258, 0.658] |
| defective tasks, sampled tasks, agent_run checks excluding 5d (user-simulator deviations) | 6/20 = 0.300 [0.145, 0.519] |
| tasks whose only confirmed defects come from agent_run checks (new versus the static phase) | 4/20 = 0.200 [0.081, 0.416] |
| defective tasks, sampled tasks, excluding the documented no-op class (checks 2a, 2b) | 16/20 = 0.800 [0.584, 0.919] |
| defective tasks, sampled tasks, excluding check 2g (it applies only to the substring communicate scorer the runs selected; the v2.0.0 default is a semantic judge) | 17/20 = 0.850 [0.640, 0.948] |
| defective tasks, sampled tasks, excluding every defect that derives from the no-op design (checks 2a, 2b, and 2k rows on tasks with noop_pass = 1 in results/static_scan.csv) | 11/20 = 0.550 [0.342, 0.742] |
| no-op pass, all airline tasks | 23/50 = 0.460 [0.330, 0.596] |
| no-op pass, sampled tasks | 7/20 = 0.350 [0.181, 0.567] |
| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | 1 |

Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category

| category | share of sampled tasks |
|---|---|
| 1 Solvability | 1/20 = 0.050 [0.009, 0.236] |
| 2 Scoring validity | 13/20 = 0.650 [0.433, 0.819] |
| 3 Isolation and leaks | 0/20 = 0.000 [0.000, 0.161] |
| 4 Specification clarity | 4/20 = 0.200 [0.081, 0.416] |
| 5 Determinism | 8/20 = 0.400 [0.219, 0.613] |
| 6 Reporting | 0/20 = 0.000 [0.000, 0.161] |

Table 2b. Confirmed defect rows by check (all methods)

| check | defect rows (high/medium) | sampled tasks |
|---|---|---|
| 1e | 1 | 1/20 |
| 2a | 7 | 7/20 |
| 2b | 7 | 7/20 |
| 2g | 2 | 2/20 |
| 2h | 4 | 4/20 |
| 2k | 6 | 6/20 |
| 4a | 1 | 1/20 |
| 4c | 2 | 2/20 |
| 4e | 1 | 1/20 |
| 4f | 2 | 2/20 |
| 5c | 3 | 3/20 |
| 5d | 7 | 7/20 |

Table 3. Low-severity defects, by category (informational)

| category | rows | sampled tasks |
|---|---|---|
| 1 Solvability | 0 | 0/20 |
| 2 Scoring validity | 0 | 0/20 |
| 3 Isolation and leaks | 0 | 0/20 |
| 4 Specification clarity | 0 | 0/20 |
| 5 Determinism | 0 | 0/20 |
| 6 Reporting | 0 | 0/20 |

Table 4. Agent runs (claude-haiku-5-5 agent and user, substring scorer)

| quantity | value |
|---|---|
| pass^1, sampled tasks (first 1 trial(s) all reward 1.0) | 16/20 = 0.800 [0.584, 0.919] |
| pass^2, sampled tasks (first 2 trial(s) all reward 1.0) | 13/20 = 0.650 [0.433, 0.819] |
| pass^3, sampled tasks (first 3 trial(s) all reward 1.0) | 12/20 = 0.600 [0.387, 0.781] |
| tasks solved in 0/3 trials | 3/20 = 0.150 [0.052, 0.360] |
| tasks solved in 1/3 or 2/3 trials (unstable) | 5/20 = 0.250 [0.112, 0.469] |
| tasks solved in 3/3 trials | 12/20 = 0.600 [0.387, 0.781] |
| ground-truth agent reaches the target state (reward 1.0) | 11/16 = 0.688 [0.444, 0.858] |
| Haiku passes ≥1 trial, ground-truth agent fails | 2 |
| ground-truth agent passes, Haiku 0/3 | 0 |
| infrastructure_error simulations excluded | 0 |

- ground-truth agent fails on tasks: 7, 16, 23, 32, 44
- Haiku passes ≥1 trial, ground-truth agent fails: 16, 23
- ground-truth agent passes, Haiku 0/3: none

Table 5. Blind re-review of 3 sampled tasks (labels compared on defect 0/1 per task x check)

| comparison | agreement | Cohen's kappa |
|---|---|---|
| blind vs original reviewer labels | 27/29 = 0.931 | 0.758 |
| blind vs skeptic-corrected labels | 29/29 = 1.000 | 1.000 |

- tasks: 10, 23, 37; rows: 29; disagreements listed in results/rereview_summary.md

Rule of three (k = 0)

- category 3 Isolation and leaks: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 6 Reporting: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
