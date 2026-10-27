# Summary numbers

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb`

Intervals: 95% Wilson.

Table 1. Headline shares

| quantity | share |
|---|---|
| defective tasks, sampled tasks | 18/20 = 0.900 [0.699, 0.972] |
| defective tasks, sampled tasks, static and probe checks only (method ≠ agent_run) | 13/20 = 0.650 [0.433, 0.819] |
| defective tasks, sampled tasks, agent_run checks only (1e, 4f, 5c, 5d, 5e, 5f) | 9/20 = 0.450 [0.258, 0.658] |
| defective tasks, sampled tasks, agent_run checks excluding 5d (user-simulator deviations) | 5/20 = 0.250 [0.112, 0.469] |
| tasks whose only confirmed defects come from agent_run checks (new versus the static phase) | 5/20 = 0.250 [0.112, 0.469] |
| defective tasks, sampled tasks, excluding the documented no-op class (checks 2a, 2b) | 16/20 = 0.800 [0.584, 0.919] |
| defective tasks, sampled tasks, excluding every defect that derives from the no-op design (checks 2a, 2b, and 2k rows on tasks with noop_pass = 1 in results/static_scan.csv) | 11/20 = 0.550 [0.342, 0.742] |
| no-op pass, all airline tasks | 23/50 = 0.460 [0.330, 0.596] |
| no-op pass, sampled tasks | 7/20 = 0.350 [0.181, 0.567] |
| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | 0 |

Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category

| category | share of sampled tasks |
|---|---|
| 1 Solvability | 0/20 = 0.000 [0.000, 0.161] |
| 2 Scoring validity | 10/20 = 0.500 [0.299, 0.701] |
| 3 Isolation and leaks | 0/20 = 0.000 [0.000, 0.161] |
| 4 Specification clarity | 6/20 = 0.300 [0.145, 0.519] |
| 5 Determinism | 8/20 = 0.400 [0.219, 0.613] |
| 6 Reporting | 0/20 = 0.000 [0.000, 0.161] |

Table 2b. Confirmed defect rows by check (all methods)

| check | defect rows (high/medium) | sampled tasks |
|---|---|---|
| 2a | 7 | 7/20 |
| 2b | 7 | 7/20 |
| 2g | 1 | 1/20 |
| 2h | 1 | 1/20 |
| 2k | 6 | 6/20 |
| 4a | 1 | 1/20 |
| 4c | 5 | 5/20 |
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

Rule of three (k = 0)

- category 1 Solvability: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 3 Isolation and leaks: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 6 Reporting: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
