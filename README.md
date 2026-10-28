# How an agent exam fails: a validation audit of tau2-bench (airline and retail), and a stricter protocol laid over it

This repository asks one question of a widely used agent benchmark: when a task is marked "passed", did the agent do the job, or did the examination procedure let it through? It audits the airline domain of [tau2-bench](https://github.com/sierra-research/tau2-bench) at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`), then builds a stricter scoring protocol ("v2") as an overlay, re-scores the recorded conversations under both, and runs the benchmark again under v2. It then applies the same checklist to every task of the retail domain, and it measures what an agent that does nothing scores in every task set of the benchmark and on four external agent benchmarks. Every number is rebuilt from the CSV and JSON files by script; every paid run carries a provenance stamp; two adversarial reviews (one of the design, one of the results) are part of the record.

## Headline results

Block 1, the audit of the pinned benchmark (20 sampled tasks of 50, fixed checklist of 52 checks, blind re-review, adversarial review of every defect row):

| quantity | value |
|---|---|
| sampled tasks with at least one confirmed medium/high defect | 18/20 = 0.90 [0.70, 0.97] |
| by static reading and mechanical probes alone | 13/20 |
| tasks of the whole domain that an agent passes by doing nothing | 23/50 = 0.46 |
| agent solve rate (claude-haiku-5-5 as agent and user simulator), tasks passed 3/3 | 12/20 = 0.60 |
| ground-truth agent (sees the reference actions) reaches the target state | 11/16 |
| blind re-review agreement with the corrected labels | 29/29, Cohen's kappa 1.00 |

The defects concentrate in two categories: scoring validity (12/20 tasks: an end-state hash that depends on list order, a substring check that matches by accident, requirements stated only in free-text assertions that the default scorer never reads, an arithmetic error in a reference answer) and determinism (8/20: the user simulator departs from its scenario).

Block 2, the stricter protocol and the re-run (pre-registered hypotheses H1–H5, one variable at a time):

| hypothesis | verdict |
|---|---|
| H1 — an empty trajectory passes | 23/50 under the stock scorer → 0/50 under v2; a refusal-only agent still passes 14/23 of those tasks, which the benchmark documents as intended |
| H2 — the DB hash is order-sensitive | reference-action permutations with a differing hash 24/78 → 4/78 under a canonical hash (the 4 change the outcome) |
| H3 — re-scoring the 76 recorded conversations | the deterministic switches change no recorded reward (the mechanisms are shown by construction, not by a flip); enforcing the free-text assertions through a 3-vote judge flips one pass to a fail; a corrected reference answer flips one fail to a pass |
| H4 — the ground-truth agent passes the three text-fixed tasks | task 7: 4/4; task 44: 3/4; task 32: **failed**, 1/4 (the new scenario sentence exposed a systematic agent error the pre-test did not cover) |
| H5 — the agent's pass^3 changes under v2 | no difference: 0.60 → 0.60; pass^1 0.73 → 0.78, inside the run-to-run noise measured on the untouched tasks |

Read together: the benchmark's defects are real and reproducible, and they are nearly invisible in the headline numbers. An agent's score moved by less than the noise floor while the examination underneath it changed substantially. That is the point of the audit: the procedure has to be checked directly, because the leaderboard will not show its faults.

Retail, the whole domain (all 114 tasks, pre-registered in `retail/PLAN.md`):

| quantity | value |
|---|---|
| tasks with at least one medium/high defect, static reading and probes (every row adversarially reviewed) | 44/114 = 0.39 [0.30, 0.48] |
| the same, all checks including the agent runs (run rows not adversarially reviewed) | 67/114 = 0.59 [0.50, 0.67] |
| all checks without the rows that blame the user simulator | 48/114 = 0.42 [0.33, 0.51] |
| tasks an agent passes by doing nothing | 6/114 = 0.05 |
| agent solve rate (claude-haiku-5-5), tasks passed 3/3; ground-truth agent | 75/114 = 0.66; 89/112 |
| judge replies the stock strict parser would reject (judge substituted by claude-haiku-5-5) | 103/169 = 0.61 |

Retail's judged assertions close most of airline's pass for doing nothing. The weight moves onto the tools, the judge and the user simulator:

- **Order rule.** 14 tasks reach the target through an order of changes that the policy forbids and the tools accept.
- **Tool bug.** One tool stores the wrong item in 5 tasks, so the score depends on the order of items inside a call.
- **User simulator.** It explains 12 of the 23 ground-truth failures and the flips of 23 of the 32 unstable tasks.

Strong vs weak (pre-registered in `strong_vs_weak/PLAN.md`): the same 20 airline tasks with `claude-sonnet-5-5` as the agent.

| | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| tau2 pass^1, stock scorer | 0.733 | 0.850 |
| tasks passed 3/3, stock scorer | 12/20 | 16/20 |
| tau2 pass^1, full v2 | 0.733 | 0.883 |

On the stock exam the stronger model is ahead on 6 tasks and behind on 1, but the difference is not significant (sign test p = 0.125). Nine of the 20 tasks tie both models by construction: 7 pass for doing nothing and 2 cannot be passed. Under v2 the gap widens to +0.150 (p = 0.039, uncorrected for the three configurations compared).

What an agent that does nothing scores, by task set (stock scorer, no model call; `results/null_agent/tau2_null_agent.md`):

| airline | retail | telecom (base / full) | intake |
|---|---|---|---|
| 23/50 = 46% | 6/114 = 5% | 0/114 / 0/2,285 | 0/200 |

The same floor on four external agent benchmarks, each scored offline with its own code (`results/null_agent/external.md`). The refusal agent does nothing except give the benchmark's "cannot be done" answer:

| benchmark | doing nothing | only refusing |
|---|---|---|
| BFCL V4 | 10.00 of 100 overall points | 10.00 of 100 |
| tau-bench (original), airline test | 19/50 = 38% | 19/50 |
| tau-bench (original), retail test | 7/115 = 6% | 7/115 |
| OSWorld-Verified | not measured (needs the virtual machine) | 30/369 = 8.1% as released, 26/369 = 7.0% now (counted from task files) |
| WebArena-Verified | 0/812 | 24/812 = 3.0% |
| WebArena, original task file | not measured (needs the live sites) | 36/812 = 4.4% for the answer "N/A" (counted) |

Original tau-bench retail task 106 is tau2 retail task 105: its only reference action is rejected for an insufficient gift-card balance. The original gives it to an agent that does nothing; tau2 added an assertion that demands the exchange and made it impossible.

Sixteen issue candidates are drafted in `issues_draft.md` (I1–I16, with file and line references and reproduction paths); none has been filed yet.

## What is in the repository

`STRUCTURE.md` is the map. In short:

- `checklist.md`, `schema.md`, `sample.json`, `audit_log.csv`: the checklist, the row schema, the sample, and the audit itself (one row per task and check).
- `summary_numbers.md`, `fig_defects.png`, `analysis.ipynb`: block-1 numbers and figure, generated.
- `block2/`: pre-registration (`PLAN.md`, with dated deviations), task fixes with their audit rows, the two adversarial reviews (`skeptic_design.md`, `skeptic_results.md`), the hand-check of judge verdicts, and the generated `summary_v2.md`.
- `retail/`, `scripts/retail/`, `results/retail/`: the retail audit. It holds the pre-registration with dated deviations, the per-check readings, the audit log, the generated `summary_numbers.md` and `comparison.md`, every script, the reviewer files, the runs and the re-judge.
- `scripts/null_agent/`, `results/null_agent/`, `null_agent/`: the null-agent table over every tau2 task set, a desk survey of nine external benchmarks, and the floors measured on four of them (the benchmarks themselves are installed outside the repository).
- `strong_vs_weak/`, `scripts/strong_vs_weak/`: the Sonnet-vs-Haiku check (pre-registration, summary, per-task table and figure).
- `scripts/demo/demo.py`: four reproductions for a live demo, offline and without a model call (about 12 seconds).
- `scripts/`, `scripts/v2/`: every script that produced a number; `scripts/runs/`, `scripts/v2/run_v2.py` and `scripts/retail/run_retail.py` are the paid runs.
- `results/`, `results/v2/`: recorded runs (`results.json` of every simulation), re-scores, gates, judge votes and raw replies, provenance stamps, probe transcripts.
- `issues_draft.md`, `cost.md`, `COMMIT_MAP.md`.

Not in the repository: the upstream clone (pinned by commit; clone it next to the scripts as `tau2-bench/`), the API key, and the descriptions of scorer-bypass constructions (kept private by design; the aggregates and the rules are public).

## Reproducing

Offline parts need the tau2 virtual environment (for the scripts that import tau2) and Python 3.11 with `statsmodels` (for the summaries). The exact command sequences are in `STRUCTURE.md` ("Block 1 rebuild", "Block 2 rebuild", "Retail domain audit"). The judge and probe scripts replay from cached votes and make no model call once the caches exist; the live runs are the only steps that spend money and are listed in `cost.md` with their token counts.

Models used: `claude-haiku-5-5` as the agent, as the user simulator and as the judge of free-text assertions (the latter is a known self-evaluation risk; the reward-changing judge verdicts of block 2 were hand-checked by two readers, 46/46 agreement). In retail the same model replaces the stock judge, an OpenAI model, with the stock prompt and evaluator. The strong-vs-weak check uses `claude-sonnet-5-5` as the agent, with everything else unchanged.

## Limits

Airline: 20 of 50 tasks sampled before any run, and the free-text assertions of the 30 unsampled tasks were not audited. Retail: all 114 tasks, but the rows from its agent runs were not adversarially reviewed. One user-simulator model throughout. Two agent models, compared on 20 tasks with one run each. The benchmark documents the pass-by-refusal behaviour as intended, so the v2 protocol is a stricter alternative, not a correction of a bug. The OSWorld-Verified and original WebArena floors are counted from task files, not measured by running the evaluator. Dollar figures are own estimates from token counts at the published per-token prices; they were not reconciled with billing row by row (billing showed about $11 when the own estimate was $10.79).
