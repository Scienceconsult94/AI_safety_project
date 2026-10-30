# How an agent exam fails: a validation audit of tau2-bench (airline and retail), and a stricter protocol laid over it

**Key results.**
- An agent that does nothing passes 23 of 50 airline tasks of the pinned benchmark; under the stricter v2 protocol it passes 0 of 50, and a refusal-only agent still passes 14 of those 23 (`summary_numbers.md`, `block2/summary_v2.md`).
- 34 of 50 airline tasks carry at least one confirmed medium- or high-severity defect (16 of 20 in the sampled block; 44 of 50 counting the pass for doing nothing); a blind second reader agreed with the original labels on 147 of 153 rows (`airline_full/summary_numbers.md`, `results/rereview_summary.md`, `results/rereview_summary_rest.md`, `results/retail/rereview_summary.md`).
- Retail: 61 of 114 tasks carry such a defect (38 from reading and probes alone; 6 pass for doing nothing) (`retail/summary_numbers.md`).
- A stronger agent model is ahead of a weaker one on 6 of 20 airline tasks and behind on 1 under the stock scorer (pass^1, the share of trials passed, 0.850 against 0.733, p = 0.125); under v2 the gap is +0.150 (p = 0.039, uncorrected for the three comparisons) (`strong_vs_weak/summary.md`).
- On the original tau-bench airline set an agent that does nothing scores 38% (19 of 50) with the benchmark's own reward code; four published runs on the HAL leaderboard score below that floor, at 28%, 36%, 36% and 36% (`results/null_agent/external.md`, `results/null_agent/hal_check.md`).

Full report: `report.md` · One page: `ONE_PAGER.md` · Demo (under a minute, no model call): `DEMO.md` · Reproduce: `STRUCTURE.md`.

**If you have 5 minutes:** read the key results above, then the Block 1 and Block 2 tables under "Headline results".
**If you have 15 minutes:** read `ONE_PAGER.md`. It gives the method, the results, what they mean and the limits on one page. Then run the demo in `DEMO.md`: one command, under a minute, no model call. The expected output is printed there.
**If you have an hour:** read `report.md`, the full write-up, section by section. `STRUCTURE.md` links every number to the files and scripts that produce it. `audit_log.csv` holds every verdict on every task, and `schema.md` explains its columns.

This repository asks one question of a widely used agent benchmark: when a task is marked "passed", did the agent do the job, or did the examination procedure (the way the benchmark checks the result) let it through?

The benchmark is [tau2-bench](https://github.com/sierra-research/tau2-bench) at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`). It is a customer-service exam: an agent talks to a simulated customer and changes a database through tools. The work has four parts.

1. The airline domain is audited with a fixed checklist of 49 checks. The audit covers 20 sampled tasks first, then the other 30.
2. A stricter scoring protocol ("v2") is added on top of the benchmark; the benchmark's own code is not changed. The recorded conversations are scored again, once under the original scoring and once under v2. Then the benchmark is run again under v2.
3. The same checklist is applied to every task of the retail domain (114 tasks).
4. The score of an agent that does nothing (the floor) is measured in five of the benchmark's six task sets: airline, retail, telecom base, telecom full and intake. The sixth, banking_knowledge, could not be built. The floor is also measured on four external benchmarks: BFCL V4, the original tau-bench, OSWorld-Verified and WebArena in two versions. On three of the four the benchmark's own scoring code was run (for WebArena, on one of its two versions). On OSWorld-Verified and on the original WebArena nothing was run: the floor counted from the task files is that of an agent that only answers "cannot be done".

A script rebuilds every number from the recorded runs out of the CSV and JSON files. There are two exceptions: a few counts taken from review reports, and the leaderboard figures, which were read from the leaderboard's web page. Every paid run is stored with the commit, the settings and the time it was made. The record also includes adversarial reviews: readings whose only job was to try to overturn each finding. They cover the defect rows of the audit log and the v2 design and results.

**Who did what.** The audit is the author's work, carried out with Claude Code (language-model assistants). The author chose the question and the benchmark, set the scope (every airline and retail task), wrote the rules the assistants worked under (the checklist, the severity definitions, the headline rule that counts the pass for doing nothing on its own line, the review and adversarial-review procedures), took the definitional decisions and settled the disputed points, and read, checked and corrected every file in this repository. The assistants drafted the texts and scripts, filled the audit logs, ran the reviews, re-reviews and paid agent runs, and reported back; wherever this repository says that a reviewer, adversarial reviewer or reader was a language model, that is what it means.

## Headline results

Block 1, the audit of the pinned benchmark (20 sampled tasks of 50, fixed checklist of 49 checks, blind re-review, adversarial review of every medium or high defect row):

| quantity | value |
|---|---|
| sampled tasks with at least one confirmed medium/high defect (the pass for doing nothing counted on its own line) | 16/20 = 0.80 [0.58, 0.92]; 18/20 counting the pass for doing nothing |
| by static reading and mechanical probes alone | 12/20 |
| tasks of the whole domain that an agent passes by doing nothing | 23/50 = 0.46 |
| agent solve rate (claude-haiku-5-5 as agent and user simulator), tasks passed 3/3 | 12/20 = 0.60 |
| ground-truth agent (sees the reference actions) reaches the target state | 11/16 |
| blind re-review by a second model reader, agreement with the original labels | 27/29, Cohen's kappa (agreement corrected for chance) 0.76; the adversarial review settled the 2 differences in favour of the blind reader |

The defects concentrate in two categories: scoring validity (11/20 tasks: an end-state hash that depends on list order, a substring check that matches by accident, requirements stated only in free-text assertions that the default scorer never reads) and determinism (8/20: the user simulator departs from its scenario); the arithmetic error in a reference answer (task 7) is logged under specification clarity. The substring check concerns the substring scorer, which every run here selected; the v2.0.0 default is a semantic judge, and without that check the headline is 15/20.

The whole airline domain (report Section 13; pre-registration `airline_full/PLAN.md`): the same pipeline on the other 30 tasks, an adversarial review of every new defect row, and a consistency pass across the two blocks.

| quantity | sample (20) | rest (30) | all 50 |
|---|---|---|---|
| tasks with at least one confirmed medium/high defect (the pass for doing nothing counted on its own line) | 16/20 | 18/30 | 34/50 = 0.68 [0.54, 0.79] |
| by static reading and mechanical probes alone | 12/20 | 15/30 | 27/50 |
| tasks an agent passes by doing nothing | 7/20 | 16/30 | 23/50 |
| tasks with a defect, counting the pass for doing nothing | 18/20 | 26/30 | 44/50 |
| agent tasks passed 3/3, stock protocol | 12/20 | 21/30 | 33/50 = 0.66 |
| ground-truth agent reaches the target state | 11/16 | 22/27 | 33/43 |

Eight of ten pre-registered predictions hold. Two do not:
- removing the payment sentence from task 32 does not help the ground-truth agent (2/10 with it and 2/10 without it);
- under the full v2 protocol the rest drops from 21/30 to 15/30 tasks passed 3/3, more than the predicted 0.10.

The consistency pass changed one block-1 row (task 22, check 2h). That moves the sample count from reading and probes from 11/20 to 12/20; the headline is unchanged.

Block 2, the stricter protocol and the re-run (pre-registered hypotheses H1–H5, one variable at a time):

| hypothesis | verdict |
|---|---|
| H1 — an empty trajectory passes | 23/50 under the stock scorer → 0/50 under v2; a refusal-only agent still passes 14/23 of those tasks, which the benchmark documents as intended |
| H2 — the DB hash (one code computed from the database's end state) is order-sensitive (it changes when the same records are stored in a different order) | reference-action permutations with a differing hash 24/78 → 4/78 under a canonical hash (the 4 change the outcome) |
| H3 — re-scoring the 76 recorded conversations | the deterministic switches change no recorded reward (the mechanisms are shown by construction, not by a flip); enforcing the free-text assertions through a 3-vote judge flips one pass to a fail; a corrected reference answer flips one fail to a pass |
| H4 — the ground-truth agent passes the three text-fixed tasks | task 7: 4/4; task 44: 3/4; task 32: **failed**, 1/4 (a later test did not tie the failures to the new scenario sentence: the ground-truth agent passed 2 of 10 trials with it and without it) |
| H5 — the agent's pass^3 (the share of tasks passed in all three trials) changes under v2 | no difference: 0.60 → 0.60; pass^1 0.73 → 0.78 (a fresh run under v2), inside the run-to-run noise measured on the untouched tasks |

Read together: the benchmark's defects are real and reproducible, and on the 20 sampled tasks they are nearly invisible in the headline number: the agent's score moved by less than the noise floor while the examination underneath it changed substantially. On the other 30 tasks the score fell from 0.70 to 0.50, mostly because v2 also scores the requirements written only in free text (report Section 13). Either way the procedure has to be checked directly, because the leaderboard will not show its faults.

Retail, the whole domain (all 114 tasks, pre-registered in `retail/PLAN.md`):

| quantity | value |
|---|---|
| tasks with at least one medium/high defect, static reading and probes (every row adversarially reviewed) | 38/114 = 0.33 [0.25, 0.42] |
| the same, all checks including the agent runs (run rows also adversarially reviewed) | 61/114 = 0.54 [0.44, 0.62] |
| all checks without the rows that blame the user simulator | 40/114 = 0.35 [0.27, 0.44] |
| tasks an agent passes by doing nothing (counted on its own line; with them the three counts above are 44, 67 and 46) | 6/114 = 0.05 |
| agent solve rate (claude-haiku-5-5), tasks passed 3/3; ground-truth agent | 75/114 = 0.66; 89/112 |
| judge replies the stock strict parser would reject (judge substituted by claude-haiku-5-5) | 103/169 = 0.61 |

Retail's judged assertions close most of airline's pass for doing nothing. The weight moves onto the tools, the judge and the user simulator:

- **Order rule.** 14 tasks reach the target through an order of changes that the policy forbids and the tools accept.
- **Tool bug.** One tool stores the wrong item in 5 tasks, so the score depends on the order of items inside a call.
- **User simulator.** It explains 12 of the 23 ground-truth failures, and the flips of 24 of the 32 unstable tasks run through it (21 departures from its scenario, 3 choices the scenario leaves open).

Strong vs weak (predictions in `strong_vs_weak/PLAN.md`, written after the run and before its results were read): the same 20 airline tasks with `claude-sonnet-5-5` as the agent.

| | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| tau2 pass^1, stock scorer | 0.733 | 0.850 |
| tasks passed 3/3, stock scorer | 12/20 | 16/20 |
| tau2 pass^1, full v2 (the recorded conversations re-scored) | 0.733 | 0.883 |

On the stock exam the stronger model is ahead on 6 tasks and behind on 1, but the difference is not significant (sign test p = 0.125). Nine of the 20 tasks tie both models by construction: 7 pass for doing nothing and 2 have defective reference answers that both models fail in every trial. Under v2 the gap widens to +0.150 (p = 0.039, uncorrected for the three configurations compared).

What an agent that does nothing scores, by task set (stock scorer, no model call; `results/null_agent/tau2_null_agent.md`):

| airline | retail | telecom (base / full) | intake |
|---|---|---|---|
| 23/50 = 46% | 6/114 = 5% | 0/114 / 0/2,285 | 0/200 |

The same floor on four external agent benchmarks, six rows because tau-bench has two task sets and WebArena two versions (`results/null_agent/external.md`): the rows marked "counted" come from the task files and the quoted scoring code; the others ran the benchmark's own scoring code offline. The refusal agent does nothing except give the benchmark's "cannot be done" answer:

| benchmark | doing nothing | only refusing |
|---|---|---|
| BFCL V4 | 10.00 of 100 overall points | 10.00 of 100 |
| tau-bench (original), airline test | 19/50 = 38% | 19/50 |
| tau-bench (original), retail test | 7/115 = 6% | 7/115 |
| OSWorld-Verified | not measured (needs the virtual machine) | 30/369 = 8.1% as released, 26/369 = 7.0% now (counted from task files) |
| WebArena-Verified | 0/812 | 24/812 = 3.0% |
| WebArena, original task file | not measured (needs the live sites) | at least 36/812 = 4.4% for the answer "N/A" (counted; the other tasks were not computed) |

The tau-bench floors were reported before: Zhu et al. (2025), *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (arXiv:2507.02825) give 38% of the airline subset and 6% of the retail subset as tasks that an agent that does nothing passes. Here they are re-measured with the benchmark's own reward code, and the airline floor is compared with published leaderboard scores (next section).

Original tau-bench retail task 106 is tau2 retail task 105: its only reference action is rejected for an insufficient gift-card balance. The original gives it to an agent that does nothing; tau2 added an assertion that demands the exchange and made it impossible.

On HAL's public TAU-bench Airline leaderboard, four single runs of the tool-calling agent score below this 38% floor, on the same 50 tasks and with the same scoring code: one at 28% and three at 36% (`results/null_agent/hal_check.md`). With one run each, this does not show that these models do worse than doing nothing. It shows that the page, which prints no floor, gives a reader no way to tell.

Sixteen issue candidates are drafted in `issues_draft.md` (I1–I16, with file and line references and reproduction paths). Texts ready to file for I1 and I3–I16, grouped into nine issues with fourteen reproduction scripts and five patches, are in `upstream/`. Nothing has been filed. Three of the drafts (I6, I11 and part of I3) were already reported by others in the benchmark's issue tracker (report Section 8).

## Relation to prior work

- *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (Zhu et al., 2025, arXiv:2507.02825; the Agentic Benchmark Checklist, ABC) assesses agent benchmarks with a checklist and reports that an agent that does nothing passes 38% of the original tau-bench airline tasks and 6% of retail. Here that documented pass is the positive control the checklist had to catch; the 38% is re-measured with the benchmark's own reward code (19 of 50); the same floor is measured on tau2-bench (23 of 50 airline, 6 of 114 retail) and, with their own scoring code, on BFCL V4 and WebArena-Verified, counted from task files on OSWorld-Verified and the original WebArena, and compared with published leaderboard scores. The talk and post "AI Agent Benchmarks are Broken" (Kang, 2025) present the same work.
- [tau2-bench-verified](https://github.com/amazon-agi/tau2-bench-verified) (Amazon) publishes a corrected and human-verified version of the tau2-bench tasks. This repository does not correct the task set; it measures, on the unmodified v2.0.0 tasks, how much of the score the examination procedure itself gives (the pass for doing nothing, the judge, the user simulator) and what a stricter protocol changes; the three task-text fixes used in v2 are documented in `block2/task_fixes.md`. The two task sets were not compared task by task.
- The benchmark's own issue tracker already reports three of the findings here (I6, I11 and the payment-order part of I3; report Section 8); nothing from this repository has been filed.

## What is in the repository

`STRUCTURE.md` is the map. In short:

- `checklist.md`, `schema.md`, `sample.json`, `audit_log.csv`: the checklist, the row schema, the sample, and the audit itself (one row per task and check).
- `summary_numbers.md`, `fig_defects.png`, `analysis.ipynb`: block-1 numbers and figure, generated.
- `block2/`: pre-registration (`PLAN.md`, with dated deviations), task fixes with their audit rows, the two adversarial reviews (`skeptic_design.md`, `skeptic_results.md`), the check of judge verdicts by two model readers, and the generated `summary_v2.md`.
- `airline_full/`: the whole airline domain (all 50 tasks). It holds the pre-registration with dated deviations, the briefs of the reviewers and adversarial reviewers, the 50-task audit log, the generated `summary_numbers.md`, the task-32 counterfactual, and the second blind check of the judge by two model readers.
- `retail/`, `scripts/retail/`, `results/retail/`: the retail audit. It holds the pre-registration with dated deviations, the per-check readings, the audit log, the generated `summary_numbers.md` and `comparison.md`, every script, the reviewer files, the runs and the re-judge.
- `scripts/null_agent/`, `results/null_agent/`, `null_agent/`: the null-agent table over every tau2 task set, a desk survey of nine external benchmarks, and the floors on four of them, measured with their own code on three and counted from the task files on OSWorld-Verified and the original WebArena (the benchmarks themselves are installed outside the repository).
- `strong_vs_weak/`, `scripts/strong_vs_weak/`: the Sonnet-vs-Haiku check (plan with predictions, summary, per-task table and figure).
- `scripts/demo/demo.py`: four reproductions for a live demo, offline and without a model call (under a minute).
- `scripts/`, `scripts/v2/`: every script that produced a number; `scripts/runs/`, `scripts/v2/run_v2.py` and `scripts/retail/run_retail.py` are the paid runs.
- `results/`, `results/v2/`: recorded runs (`results.json` of every simulation), re-scores, gates, judge votes and raw replies, provenance stamps, probe transcripts.
- `ONE_PAGER.md`: the results on one page; `DEMO.md`: the five-minute demo script.
- `issues_draft.md`, `upstream/` (issue and pull-request texts ready to file, with reproductions and patches; not filed), `cost.md`, `COMMIT_MAP.md`.

Not in the repository: the upstream clone (pinned by commit; clone it next to the scripts as `tau2-bench/`), the API key, and the descriptions of scorer-bypass constructions (kept private by design; the aggregates and the rules are public).

## Reproducing

Offline parts need the tau2 virtual environment (for the scripts that import tau2) and Python 3.11 with `statsmodels` (for the summaries). The exact command sequences are in `STRUCTURE.md` ("Rebuild everything (offline, no API calls)", "Block 2 rebuild (offline parts)", "Retail domain audit (all 114 tasks)"). The judge and probe scripts replay from cached votes and make no model call once the caches exist; the live runs are the only steps that spend money and are listed in `cost.md` with their token counts.

Models used: `claude-haiku-5-5` as the agent, as the user simulator and as the judge of free-text assertions (the latter is a known self-evaluation risk; the reward-changing judge verdicts of block 2 were checked by two model readers, 46/46 agreement). In retail the same model replaces the stock judge, an OpenAI model, with the stock prompt and evaluator. The strong-vs-weak check uses `claude-sonnet-5-5` as the agent, with everything else unchanged.

## Limits

Airline: all 50 tasks; 20 were sampled before any run (block 1), and the other 30 were audited afterwards with the same pipeline (report Section 13). Retail: all 114 tasks; the findings from its agent runs went through their own adversarial review, and a few rest on readings that could go the other way (report Section 5). Required information is checked by the substring scorer in every run, not by the v2.0.0 default semantic judge; on the recorded airline runs the two agree on all 58 verdicts (check 2j). Every reviewer, adversarial reviewer and reader was a language model, not a person. One user-simulator model throughout. Two agent models, compared on 20 tasks with one run each. v2 has two parts: corrected task texts (a wrong reference answer, a scenario that contradicted its reference), which fix defects, and a stricter scoring rule for the pass by doing nothing, which the benchmark documents as intended; that second part is a stricter alternative, not a correction of a bug. The OSWorld-Verified and original WebArena floors are counted from task files, not measured by running the evaluator. Dollar figures are own estimates from token counts at the published per-token prices, about $33 for the whole project (`cost.md`); they were not reconciled with billing row by row, and the one billing checkpoint available showed about $11 when the running estimate was $10.79. The telecom task set of tau2-bench was not audited; only its do-nothing floor was measured. The strong-vs-weak comparison rests on 20 tasks with one run per model: Wilson 95% intervals are [0.61, 0.83] for pass^1 0.733 (44 of 60 trials) and [0.74, 0.92] for 0.850 (51 of 60); for tasks passed in all three trials, 12 of 20 [0.39, 0.78] against 16 of 20 [0.58, 0.92].
