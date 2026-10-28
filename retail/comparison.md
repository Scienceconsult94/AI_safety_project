# Airline beside retail

Same pinned benchmark (`989d3285ae669e49503324bdb9981bf14fccedeb`), same checklist, same models and run settings. Airline: 20 tasks sampled before any run out of 50; retail: all 114 tasks. Airline reward = DB hash × substring check of `communicate_info`; retail reward = DB hash × LLM-judged `nl_assertions` (judge model substituted by claude-haiku-5-5; the stock default is an OpenAI model). Retail adds checks 2c, 2d, 2e (probed), 2j and 2m; airline logged none of these per task, so the retail defective share is computed with and without them below. Intervals: 95% Wilson.

| quantity | airline (20 of 50, sampled) | retail (all 114) |
|---|---|---|
| tasks with ≥1 confirmed medium/high defect (all checks) | 18/20 = 0.900 [0.699, 0.972] | 57/114 = 0.500 [0.410, 0.590] |
| … static and probe checks only | 13/20 = 0.650 [0.433, 0.819] | 44/114 = 0.386 [0.302, 0.478] |
| … agent_run checks only | 9/20 = 0.450 [0.258, 0.658] | 23/114 = 0.202 [0.138, 0.285] |
| … excluding the no-op class (2a, 2b[, 2c]) | 16/20 = 0.800 [0.584, 0.919] | 51/114 = 0.447 [0.359, 0.539] |
| category 1 Solvability | 1/20 = 0.050 [0.009, 0.236] | 29/114 = 0.254 [0.183, 0.341] |
| category 2 Scoring validity | 12/20 = 0.600 [0.387, 0.781] | 30/114 = 0.263 [0.191, 0.351] |
| category 3 Isolation and leaks | 0/20 = 0.000 [0.000, 0.161] | 0/114 = 0.000 [0.000, 0.033] |
| category 4 Specification clarity | 4/20 = 0.200 [0.081, 0.416] | 17/114 = 0.149 [0.095, 0.226] |
| category 5 Determinism | 8/20 = 0.400 [0.219, 0.613] | 0/114 = 0.000 [0.000, 0.033] |
| category 6 Reporting | 0/20 = 0.000 [0.000, 0.161] | 0/114 = 0.000 [0.000, 0.033] |
| empty answer gets full reward (whole domain) | 23/50 = 0.460 [0.330, 0.596] | 6/114 = 0.053 [0.024, 0.110] |
| agent pass^1 (claude-haiku-5-5; first 1 trial(s) all reward 1.0) | 16/20 = 0.800 [0.584, 0.919] | 93/114 = 0.816 [0.735, 0.876] |
| agent pass^3 (claude-haiku-5-5; first 3 trial(s) all reward 1.0) | 12/20 = 0.600 [0.387, 0.781] | 75/114 = 0.658 [0.567, 0.739] |
| agent pass^1 (claude-haiku-5-5; tau2 estimator, mean of C(c,k)/C(n,k) over tasks) | 0.733 (n = 20) | 0.807 (n = 114) |
| agent pass^3 (claude-haiku-5-5; tau2 estimator, mean of C(c,k)/C(n,k) over tasks) | 0.600 (n = 20) | 0.658 (n = 114) |
| ground-truth agent reaches reward 1.0 | 11/16 = 0.688 [0.444, 0.858] | 89/112 = 0.795 [0.711, 0.859] |
| tasks with ≥1 confirmed defect, retail without the checks airline did not log per task (2c, 2d, 2e, 2m, 2j) | — | 47/114 = 0.412 [0.326, 0.504] |
| Haiku trials failed by the judge alone (DB matched) | — (no judge in airline scoring) | 9/342 = 0.026 [0.014, 0.049] |

Reading notes

- Airline's share is a sample estimate with a wide interval; retail's is the population value of the domain. The two are not the same quantity, and the retail figure carries no sampling error.
- Airline's no-op class (23/50 tasks passable by an empty answer) is the domain's largest defect class; retail's scorer enforces assertions on 40 tasks, which shrinks that class to the 6 tasks that have neither a write nor an assertion.
- Retail moves the weight onto the judge: whether a trial passes depends on one LLM vote whose reply the stock parser would often reject (Table 6 of retail/summary_numbers.md).
- Agent numbers are not comparable across domains (different tasks, different scorer); they are listed to show the noise floor each domain carries.
