# How an agent exam fails: a validation audit of tau2-bench (airline and retail), and a stricter protocol laid over it

This repository asks one question of a widely used agent benchmark: when a task is marked "passed", did the agent do the job, or did the examination procedure let it through? It audits the airline domain of [tau2-bench](https://github.com/sierra-research/tau2-bench) at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`), then builds a stricter scoring protocol ("v2") as an overlay, re-scores the recorded conversations under both, and runs the benchmark again under v2. It then applies the same checklist to every task of the retail domain, and it measures what an agent that does nothing scores in every task set of the benchmark and on four external agent benchmarks. Every number is rebuilt from the CSV and JSON files by script; every paid run carries a provenance stamp; two adversarial reviews (one of the design, one of the results) are part of the record.

## Headline results

Block 1, the audit of the pinned benchmark (20 sampled tasks of 50, fixed checklist of 52 checks, blind re-review, adversarial review of every defect row):

| quantity | value |
|---|---|
| sampled tasks with at least one confirmed medium/high defect | 18/20 = 0.90 [0.70, 0.97] |
| by static reading and mechanical probes alone | 14/20 |
| tasks of the whole domain that an agent passes by doing nothing | 23/50 = 0.46 |
| agent solve rate (claude-haiku-5-5 as agent and user simulator), tasks passed 3/3 | 12/20 = 0.60 |
| ground-truth agent (sees the reference actions) reaches the target state | 11/16 |
| blind re-review agreement with the corrected labels | 29/29, Cohen's kappa 1.00 |

The defects concentrate in two categories: scoring validity (13/20 tasks: an end-state hash that depends on list order, a substring check that matches by accident, requirements stated only in free-text assertions that the default scorer never reads, an arithmetic error in a reference answer) and determinism (8/20: the user simulator departs from its scenario). The substring check concerns the substring scorer, which every run here selected; the v2.0.0 default is a semantic judge, and without that check the headline is 17/20.

The whole airline domain (report Section 13; pre-registration `airline_full/PLAN.md`): the same pipeline on the other 30 tasks, an adversarial review of every new defect row, and a consistency pass across the two blocks.

| quantity | sample (20) | rest (30) | all 50 |
|---|---|---|---|
| tasks with at least one confirmed medium/high defect | 18/20 | 26/30 | 44/50 = 0.88 [0.76, 0.94] |
| by static reading and mechanical probes alone | 14/20 | 23/30 | 37/50 |
| tasks an agent passes by doing nothing | 7/20 | 16/30 | 23/50 |
| agent tasks passed 3/3, stock protocol | 12/20 | 21/30 | 33/50 = 0.66 |
| ground-truth agent reaches the target state | 11/16 | 22/27 | 33/43 |

Eight of ten pre-registered predictions hold. Two do not:
- removing the payment sentence from task 32 does not help the ground-truth agent (2/10 with it and 2/10 without it);
- under the full v2 protocol the rest drops from 21/30 to 15/30 tasks passed 3/3, more than the predicted 0.10.

The consistency pass changed one block-1 row (task 22, check 2h). That moves the sample count from reading and probes from 13/20 to 14/20; the headline is unchanged.

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
| the same, all checks including the agent runs (run rows also adversarially reviewed) | 67/114 = 0.59 [0.50, 0.67] |
| all checks without the rows that blame the user simulator | 46/114 = 0.40 [0.32, 0.50] |
| tasks an agent passes by doing nothing | 6/114 = 0.05 |
| agent solve rate (claude-haiku-5-5), tasks passed 3/3; ground-truth agent | 75/114 = 0.66; 89/112 |
| judge replies the stock strict parser would reject (judge substituted by claude-haiku-5-5) | 103/169 = 0.61 |

Retail's judged assertions close most of airline's pass for doing nothing. The weight moves onto the tools, the judge and the user simulator:

- **Order rule.** 14 tasks reach the target through an order of changes that the policy forbids and the tools accept.
- **Tool bug.** One tool stores the wrong item in 5 tasks, so the score depends on the order of items inside a call.
- **User simulator.** It explains 12 of the 23 ground-truth failures, and the flips of 24 of the 32 unstable tasks run through it (21 departures from its scenario, 3 choices the scenario leaves open).

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

On HAL's public TAU-bench Airline leaderboard, four single runs of the tool-calling agent score below this 38% floor, on the same 50 tasks and with the same scoring code: one at 28% and three at 36% (`results/null_agent/hal_check.md`). With one run each, this does not show that these models do worse than doing nothing. It shows that the page, which prints no floor, gives a reader no way to tell.

Sixteen issue candidates are drafted in `issues_draft.md` (I1–I16, with file and line references and reproduction paths). Texts ready to file for I1 and I3–I16, grouped into nine issues with fourteen reproduction scripts and five patches, are in `upstream/`. Nothing has been filed. Three of the drafts (I6, I11 and part of I3) were already reported by others in the benchmark's issue tracker (report Section 8).

## What is in the repository

`STRUCTURE.md` is the map. In short:

- `checklist.md`, `schema.md`, `sample.json`, `audit_log.csv`: the checklist, the row schema, the sample, and the audit itself (one row per task and check).
- `summary_numbers.md`, `fig_defects.png`, `analysis.ipynb`: block-1 numbers and figure, generated.
- `block2/`: pre-registration (`PLAN.md`, with dated deviations), task fixes with their audit rows, the two adversarial reviews (`skeptic_design.md`, `skeptic_results.md`), the hand-check of judge verdicts, and the generated `summary_v2.md`.
- `airline_full/`: the whole airline domain (all 50 tasks). It holds the pre-registration with dated deviations, the briefs of the reviewers and adversarial reviewers, the 50-task audit log, the generated `summary_numbers.md`, the task-32 counterfactual, and the second blind hand-check of the judge.
- `retail/`, `scripts/retail/`, `results/retail/`: the retail audit. It holds the pre-registration with dated deviations, the per-check readings, the audit log, the generated `summary_numbers.md` and `comparison.md`, every script, the reviewer files, the runs and the re-judge.
- `scripts/null_agent/`, `results/null_agent/`, `null_agent/`: the null-agent table over every tau2 task set, a desk survey of nine external benchmarks, and the floors measured on four of them (the benchmarks themselves are installed outside the repository).
- `strong_vs_weak/`, `scripts/strong_vs_weak/`: the Sonnet-vs-Haiku check (pre-registration, summary, per-task table and figure).
- `scripts/demo/demo.py`: four reproductions for a live demo, offline and without a model call (about 12 seconds).
- `scripts/`, `scripts/v2/`: every script that produced a number; `scripts/runs/`, `scripts/v2/run_v2.py` and `scripts/retail/run_retail.py` are the paid runs.
- `results/`, `results/v2/`: recorded runs (`results.json` of every simulation), re-scores, gates, judge votes and raw replies, provenance stamps, probe transcripts.
- `ONE_PAGER.md`: the results on one page; `DEMO.md`: the five-minute demo script.
- `issues_draft.md`, `upstream/` (issue and pull-request texts ready to file, with reproductions and patches; not filed), `cost.md`, `COMMIT_MAP.md`.

Not in the repository: the upstream clone (pinned by commit; clone it next to the scripts as `tau2-bench/`), the API key, and the descriptions of scorer-bypass constructions (kept private by design; the aggregates and the rules are public).

## Reproducing

Offline parts need the tau2 virtual environment (for the scripts that import tau2) and Python 3.11 with `statsmodels` (for the summaries). The exact command sequences are in `STRUCTURE.md` ("Block 1 rebuild", "Block 2 rebuild", "Retail domain audit"). The judge and probe scripts replay from cached votes and make no model call once the caches exist; the live runs are the only steps that spend money and are listed in `cost.md` with their token counts.

Models used: `claude-haiku-5-5` as the agent, as the user simulator and as the judge of free-text assertions (the latter is a known self-evaluation risk; the reward-changing judge verdicts of block 2 were hand-checked by two readers, 46/46 agreement). In retail the same model replaces the stock judge, an OpenAI model, with the stock prompt and evaluator. The strong-vs-weak check uses `claude-sonnet-5-5` as the agent, with everything else unchanged.

## Limits

Airline: all 50 tasks; 20 were sampled before any run (block 1), and the other 30 were audited afterwards with the same pipeline (report Section 13). Retail: all 114 tasks; the findings from its agent runs went through their own adversarial review, and a few rest on readings that could go the other way (report Section 5). Required information is checked by the substring scorer in every run, not by the v2.0.0 default semantic judge; on the recorded airline runs the two agree on all 58 verdicts (check 2j). Every reviewer, adversarial reviewer and reader was a language model, not a person. One user-simulator model throughout. Two agent models, compared on 20 tasks with one run each. The benchmark documents the pass-by-refusal behaviour as intended, so the v2 protocol is a stricter alternative, not a correction of a bug. The OSWorld-Verified and original WebArena floors are counted from task files, not measured by running the evaluator. Dollar figures are own estimates from token counts at the published per-token prices; they were not reconciled with billing row by row (billing showed about $11 when the own estimate was $10.79).
