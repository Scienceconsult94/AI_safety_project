# How an agent exam fails: a validation audit of tau2-bench airline, and a stricter protocol laid over it

This repository asks one question of a widely used agent benchmark: when a task is marked "passed", did the agent do the job, or did the examination procedure let it through? It audits the airline domain of [tau2-bench](https://github.com/sierra-research/tau2-bench) at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`), then builds a stricter scoring protocol ("v2") as an overlay, re-scores the recorded conversations under both, and runs the benchmark again under v2. Every number is rebuilt from the CSV and JSON files by script; every paid run carries a provenance stamp; two adversarial reviews (one of the design, one of the results) are part of the record.

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

Ten issue candidates are drafted in `issues_draft.md` (I1–I10, with file and line references and reproduction paths); none has been filed yet.

## What is in the repository

`STRUCTURE.md` is the map. In short:

- `checklist.md`, `schema.md`, `sample.json`, `audit_log.csv`: the checklist, the row schema, the sample, and the audit itself (one row per task and check).
- `summary_numbers.md`, `fig_defects.png`, `analysis.ipynb`: block-1 numbers and figure, generated.
- `block2/`: pre-registration (`PLAN.md`, with dated deviations), task fixes with their audit rows, the two adversarial reviews (`skeptic_design.md`, `skeptic_results.md`), the hand-check of judge verdicts, and the generated `summary_v2.md`.
- `scripts/`, `scripts/v2/`: every script that produced a number; `scripts/runs/` and `scripts/v2/run_v2.py` are the paid runs.
- `results/`, `results/v2/`: recorded runs (`results.json` of every simulation), re-scores, gates, judge votes and raw replies, provenance stamps, probe transcripts.
- `issues_draft.md`, `cost.md`, `COMMIT_MAP.md`.

Not in the repository: the upstream clone (pinned by commit; clone it next to the scripts as `tau2-bench/`), the API key, and the descriptions of scorer-bypass constructions (kept private by design; the aggregates and the rules are public).

## Reproducing

Offline parts need the tau2 virtual environment (for the scripts that import tau2) and Python 3.11 with `statsmodels` (for the summaries). The exact command sequences are in `STRUCTURE.md` ("Block 1 rebuild", "Block 2 rebuild"). The judge and probe scripts replay from cached votes and make no model call once the caches exist; the live runs are the only steps that spend money and are listed in `cost.md` with their token counts.

Models used: `claude-haiku-5-5` as the agent, as the user simulator and as the judge of free-text assertions (the latter is a known self-evaluation risk; the reward-changing judge verdicts were hand-checked by two readers, 46/46 agreement).

## Limits

One domain, 20 of 50 tasks sampled before any run, one agent model, one user-simulator model. The free-text assertions of the 30 unsampled tasks were not audited. The benchmark documents the pass-by-refusal behaviour as intended, so the v2 protocol is a stricter alternative, not a correction of a bug. Dollar figures are own estimates from token counts at an assumed price and were not reconciled with billing.
