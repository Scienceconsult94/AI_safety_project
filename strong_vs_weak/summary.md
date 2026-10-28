# Strong vs weak: Sonnet and Haiku as the agent on the 20 sampled airline tasks

Pre-registration: `strong_vs_weak/PLAN.md`, committed before any result of the Sonnet run was read. tau2-bench v2.0.0, same user simulator (claude-haiku-5-5), seed, scorer (stock, substring communicate check) and run settings; one run per model, a day apart. Intervals: 95% Wilson; tests: exact two-sided.

Table 1. Pass rates (stock scorer, as recorded)

| quantity | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| tau2 pass^1 (mean over tasks of C(c,1)/C(n,1)) | 0.733 | 0.850 |
| tau2 pass^2 (mean over tasks of C(c,2)/C(n,2)) | 0.650 | 0.817 |
| tau2 pass^3 (mean over tasks of C(c,3)/C(n,3)) | 0.600 | 0.800 |
| tasks passed 3 of 3 | 12/20 = 0.600 [0.387, 0.781] | 16/20 = 0.800 [0.584, 0.919] |
| passing trials (trials are not independent; interval for orientation only) | 44/60 = 0.733 [0.610, 0.829] | 51/60 = 0.850 [0.739, 0.919] |
| tasks solved in 0 of 3 | 3 | 2 |
| infrastructure errors (excluded) | 0 | 0 |
| terminations | {'user_stop': 60} | {'user_stop': 60} |

Table 2. Paired per-task comparison (Sonnet relative to Haiku; successes out of 3 per task)

| tasks | n | Sonnet ahead | behind | equal | sign test p | 3/3 only Sonnet | 3/3 only Haiku | McNemar p | tau2 pass^1 Haiku → Sonnet | tasks 3/3 Haiku → Sonnet |
|---|---|---|---|---|---|---|---|---|---|---|
| all 20 sampled tasks | 20 | 6 | 1 | 13 | 0.125 | 5 | 1 | 0.219 | 0.733 → 0.850 | 12 → 16 |
| the 7 no-op tasks (empty trajectory passes) | 7 | 0 | 0 | 7 | 1.000 | 0 | 0 | 1.000 | 1.000 → 1.000 | 7 → 7 |
| the 13 other tasks | 13 | 6 | 1 | 6 | 0.125 | 5 | 1 | 0.219 | 0.590 → 0.769 | 5 → 9 |

No-op tasks of the sample: 1, 9, 10, 26, 28, 46, 48.

Table 3. Per task (1 = trial passed, in trial order)

| task | no-op | Haiku | Sonnet | block-1 task defect |
|---|---|---|---|---|
| 1 | yes | 111 | 111 |  |
| 3 |  | 111 | 111 |  |
| 7 |  | 000 | 000 | yes |
| 8 |  | 100 | 111 |  |
| 9 | yes | 111 | 111 |  |
| 10 | yes | 111 | 111 |  |
| 11 |  | 110 | 111 |  |
| 16 |  | 101 | 111 |  |
| 19 |  | 001 | 111 |  |
| 20 |  | 111 | 111 |  |
| 21 |  | 111 | 111 |  |
| 22 |  | 101 | 111 |  |
| 23 |  | 111 | 101 |  |
| 26 | yes | 111 | 111 |  |
| 28 | yes | 111 | 111 |  |
| 32 |  | 000 | 100 | yes |
| 37 |  | 111 | 111 |  |
| 44 |  | 000 | 000 | yes |
| 46 | yes | 111 | 111 |  |
| 48 | yes | 111 | 111 |  |

Table 4. The same conversations re-scored (block-2 configurations; `results/v2/rescore.csv`, `rescore_sonnet.csv`)

| configuration | tau2 pass^1 Haiku | tau2 pass^1 Sonnet | gap | tasks 3/3 Haiku | tasks 3/3 Sonnet | Sonnet ahead / behind / equal | sign test p |
|---|---|---|---|---|---|---|---|
| stock scorer, tasks v1 (as recorded) | 0.733 | 0.850 | +0.117 | 12 | 16 | 6 / 1 / 13 | 0.125 |
| stock scorer, tasks v2 (corrected criteria) | 0.750 | 0.900 | +0.150 | 12 | 17 | 7 / 1 / 12 | 0.070 |
| full v2 (canonical hash, word-boundary check, 3-vote judge on assertions) | 0.733 | 0.883 | +0.150 | 11 | 16 | 8 / 1 / 11 | 0.039 |

Replay check: the v1 re-score of the Sonnet run reproduces the recorded rewards on every task: yes.
Multiplicity: three configurations are compared on the same conversations, so a p value below 0.05 in one of them is not corrected; with a Bonferroni correction over the three the threshold is 0.017.
Tasks whose counts change between the stock scorer and full v2: task 9: Haiku 3→2, Sonnet 3→3; task 7: Haiku 0→1, Sonnet 0→3; task 8: Haiku 1→1, Sonnet 3→2.

Table 5. Tokens and cost (own estimate from the recorded usage; claude-api reference prices)

| quantity | claude-haiku-5-5 run | claude-sonnet-5-5 run |
|---|---|---|
| agent input / output tokens | 7,140,245 / 298,051 | 7,282,187 / 213,336 |
| agent output tokens per simulation | 4,968 | 3,556 |
| user-simulator input / output tokens | 1,020,917 / 76,254 | 1,094,479 / 79,283 |
| cost of the run, agent and user simulator | $1.00 | $16.85 |

Table 6. Pre-registered predictions against the measurements

| id | prediction | measured | verdict |
|---|---|---|---|
| P1 | Sonnet's tau2 pass^1 above Haiku's 0.733, likely by +0.05 to +0.15 | 0.733 → 0.850 (+0.117) | held |
| P2 | the paired sign test does not reach p < 0.05 | p = 0.125 (6 ahead, 1 behind, 13 equal) | held |
| P3 | both close to 3/3 on the 7 no-op tasks; the gap sits in the 13 others | no-op tasks pass^1 1.000 / 1.000; others 0.590 / 0.769; tasks with a different count: no-op 0, others 7 | held |
| P4 | at least 2 of tasks 7, 32, 44 stay at 0/3 for Sonnet | 7: 0/3, 32: 1/3, 44: 0/3 | held |
| P5 | the gap does not shrink under v2 | gap +0.117 (v1) → +0.150 (V2) | held |
