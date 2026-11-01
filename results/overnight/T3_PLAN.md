# T3 plan: sensitivity of recorded verdicts to copies of the judge (written before any judge call)

Added 2026-11-01 (overnight branch). Kickoff definition, kept as is: for a fixed set of recorded agent runs, a "copy" re-draws scoring details that should not affect the capability measured, with every copy still checked against the reference answer. Statistic per agent and task set: share of passes lost and share of fails gained across copies, with the run-to-run spread next to it.

## Recorded runs used (nothing is re-run; only the NL-assertion judge is called again)

Airline, scored under V2 (tasks v2 + hash_canon + comm_boundary + nl_enforce; the reference verdicts are the cached ones behind `block2/summary_v2.md` and `airline_full/`):

| set | file | agent | sims | judge-decisive sims (DB and communicate parts pass under V2) | V2 passes (reference) |
|---|---|---|---|---|---|
| A1 recorded sample | `results/runs/sample20_pass3_haiku.results.json`, re-scored in `results/v2/rescore.csv` | claude-haiku-5-5 | 60 | 45 | 44 |
| A2 recorded rest 30 | `results/runs/rest30_pass3_haiku.results.json`, `results/v2/rescore_rest30.csv` | claude-haiku-5-5 | 90 | 76 | 68 |
| A3 fresh v2 sample | `results/v2/runs/v2_sample20_pass3_haiku/results.json`, `results/v2/rescore_fresh.csv` | claude-haiku-5-5 | 60 | 47 | 47 |
| A4 fresh v2 rest 30 | `results/v2/runs/v2_rest30_pass3_haiku/results.json`, `results/v2/rescore_fresh_rest30.csv` | claude-haiku-5-5 | 90 | 72 | 64 |
| A5 recorded sample, stronger model | `results/runs/sample20_sonnet_t3.results.json`, `results/v2/rescore_sonnet.csv` | claude-sonnet-5-5 | 60 | 54 | 53 |

Every airline simulation has agent text and every task v2 has assertions (counted 2026-10-31: 360 judged trajectory–assertion pairs, 0 empty-rule trajectories). Under V2 the reward is DB x communicate x NL, so a judge copy can change a verdict only in the judge-decisive simulations; the others are reported in the denominators but cannot move.

Retail (T4 in its partial form), scored as published: stock scorer, judge model claude-haiku-5-5 in the stock `role: content` view, reward = DB x NL for the tasks whose reward basis includes NL_ASSERTION. Reference verdict = the 3-vote majority of the recorded re-judge (`results/retail/judge_cache_rejudge.json`, check 2j); the live single vote is reported as one more copy.

| set | file | sims with reward-gating assertions and normal termination | judge-decisive sims |
|---|---|---|---|
| B1 retail pass^3 | `results/retail/runs/retail_pass3_haiku/results.json` | 120 | 107 |
| B2 retail ground-truth agent | `results/retail/runs/retail_gt_haiku/results.json` | 39 | (computed in the run) |

## Copies

Judge calls (every copy: 3 votes, majority of determined votes, one re-ask when an assertion is missing from the reply; undetermined counts as unmet, as in V2):

| copy | system prompt | assertion list in the user prompt | transcript view | draw |
|---|---|---|---|---|
| P0.1, P0.2 | the V2 prompt (`scripts/v2/scorer_v2.py`, `_SYSTEM_PROMPT`: tau2's wording plus a numbered list and an `index` field) | numbered | airline: with tool calls (V2); retail: stock | two independent draws |
| P1.1, P1.2 | tau2's stock prompt, verbatim (`tau2-bench/src/tau2/evaluator/evaluator_nl_assertions.py`), stock user-prompt format (the Python list of assertions) | plain list | same | two independent draws |
| P2.1, P2.2 | a paraphrase with the same instructions in different words (text in `scripts/overnight/t3_judge_copies.py`) | numbered | same | two independent draws |

"Judge seed/temperature" cannot be re-drawn: current Anthropic models reject a non-default temperature (audit issue I5) and the API exposes no seed. Two independent draws of the same prompt take its place. Results are mapped to assertions by index, then exact text, then position (the V2 mapping); for P1 there is no index.

Offline copies, computed from the same ballots without further calls:

- Pass threshold per assertion: majority of 3 (reference rule), unanimous (3 of 3 met), any (at least 1 of 3 met).
- Floor definition (airline only): credited passes exclude the tasks a do-nothing agent passes. Floor "empty conversation": 0 tasks under V2 (nothing excluded), 23 under the stock scorer. Floor "refusal-only agent": the 14 tasks of `results/v2/noop_judge_probe.csv` (`refusal_bot_pass` = 1). Statistic: share of credited passes lost when the floor definition changes.

## Statistic

Per set and copy k, against the reference R: passes lost = (sims passing under R and failing under k) / (sims passing under R); fails gained = (sims failing under R and passing under k) / (sims failing under R), also with the judge-decisive fails as denominator. Across the six copies: mean and range. Per-simulation flip rate between any two copies (pairwise discordance, all pairs incl. R).

Run-to-run spread, same scoring R: pairwise discordance of the verdict between the three trials of the same task (3 pairs per task), i.e. how often two runs of the same agent on the same task disagree. The judge-copy flip rate is read next to it: a judge copy that flips verdicts far less often than a re-run of the agent is a small part of the noise; one that flips as often is not.

## Prediction (recorded before the first call)

Base facts: under the current prompt the three votes were unanimous on 92 to 98 percent of assertion verdicts (judge_votes*.csv: 262/271, 283/289, 70/76, 12/12, 202/207); the retail re-judge with three votes flipped the reward of 1 of 159 simulations against the live single vote.

- Same prompt, new draw (P0.1 vs R, P0.1 vs P0.2): 2 to 4 percent of judge-decisive simulations change verdict; passes lost about 2 percent, fails gained about 2 percent of judge-decisive fails.
- Other wording (P1, P2 vs R): 4 to 8 percent of judge-decisive simulations change verdict; the stock unnumbered format (P1) loses more passes than it gains fails (missing or paraphrased results map worse, and undetermined counts as unmet).
- Unanimous threshold: 5 to 10 percent of reference passes lost; "any" threshold: 10 to 20 percent of judge-decisive fails gained.
- Run-to-run spread under R: 15 to 30 percent of trial pairs disagree (from the published pass^1 vs pass^3 gap).
- Retail: same-prompt redraw changes 1 to 3 percent of judge-decisive verdicts; other wording 3 to 6 percent.
- Cost: about 9,350 judge calls (360 airline pairs x 18, 159 retail pairs x 18) plus re-asks; own estimate 9 to 12 USD at $0.10/$0.50 per MTok (the own estimate has been above the billed figure so far); 2 to 3 hours with 4 workers.

## Outputs

`results/overnight/T3_sensitivity.md` (tables, prediction next to result), `T3_verdicts.csv` (one row per simulation x copy: NL verdict under the three thresholds, DB, communicate, reward), `T3_votes.csv` (one row per assertion x vote), `judge_cache_T3.json` (every ballot; the analysis reruns offline from it), `T3_provenance.json`, cost rows in `cost_overnight.md`. Script: `scripts/overnight/t3_judge_copies.py`, run from `tau2-bench/` with `uv run --no-sync python ../scripts/overnight/t3_judge_copies.py --sets airline|retail|all [--no-judge] [--workers 4] [--budget-usd 30]`.

## Note added after the run and the reviews (2026-10-31, evening)

The retail reference R (the check 2j re-judge, `scripts/retail/rejudge.py`) used tau2's stock prompt and list format. For retail, therefore, the same-prompt copy is P1 and the other-wording copies are P0 and P2; for airline the reference is the V2 prompt and the same-prompt copy is P0. The prediction lines above are left exactly as written before the run; `T3_sensitivity.md` labels the pooled retail rows accordingly. Also found after the run: 5 of the 7 airline passes lost under the unanimous threshold have no unmet vote, only an undetermined ballot in the reference (the old parser gap), so that threshold row compares a reference with undetermined ballots against copies without any.
