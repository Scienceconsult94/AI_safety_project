# Summary numbers

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb`

Intervals: 95% Wilson.

Table 1. Headline shares

| quantity | share |
|---|---|
| defective tasks, sampled tasks | 13/20 = 0.650 [0.433, 0.819] |
| defective tasks, sampled tasks, excluding the documented no-op class (checks 2a, 2b) | 9/20 = 0.450 [0.258, 0.658] |
| no-op pass, all airline tasks | 23/50 = 0.460 [0.330, 0.596] |
| no-op pass, sampled tasks | 7/20 = 0.350 [0.181, 0.567] |
| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | 27 |

Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category

| category | share of sampled tasks |
|---|---|
| 1 Solvability | 0/20 = 0.000 [0.000, 0.161] |
| 2 Scoring validity | 10/20 = 0.500 [0.299, 0.701] |
| 3 Isolation and leaks | 0/20 = 0.000 [0.000, 0.161] |
| 4 Specification clarity | 5/20 = 0.250 [0.112, 0.469] |
| 5 Determinism | 0/20 = 0.000 [0.000, 0.161] |
| 6 Reporting | 0/20 = 0.000 [0.000, 0.161] |

Table 3. Low-severity defects, by category (informational)

| category | rows | sampled tasks |
|---|---|---|
| 1 Solvability | 0 | 0/20 |
| 2 Scoring validity | 0 | 0/20 |
| 3 Isolation and leaks | 0 | 0/20 |
| 4 Specification clarity | 0 | 0/20 |
| 5 Determinism | 0 | 0/20 |
| 6 Reporting | 0 | 0/20 |

Rule of three (k = 0)

- category 1 Solvability: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 3 Isolation and leaks: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 5 Determinism: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
- category 6 Reporting: 0/20 → upper bound by the rule of three ≈ 3/20 = 0.150
