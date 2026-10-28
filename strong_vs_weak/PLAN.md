# Strong vs weak: does the exam separate a stronger agent? (pre-registration)

Written 2026-10-28, after the paid run finished (06:43) and before any reward, transcript or summary line of it was read. Only the completion markers of `results/runs/sonnet_chain.log` were read: start times, the smoke-gate counts and "CHAIN DONE". This file is committed before the analysis script is run.

## Question

On the 20 sampled airline tasks (`sample.json`), does the stock score of tau2-bench v2.0.0 separate `claude-sonnet-5-5` from `claude-haiku-5-5` as the agent? The user simulator stays `claude-haiku-5-5` and every setting stays the same. And does the answer change in two cases?

- **(a)** The 7 sampled tasks that an empty trajectory passes are set aside.
- **(b)** The conversations are re-scored under the v2 protocol of block 2.

## Data

- **Weak agent:** `results/runs/sample20_pass3_haiku.results.json`, block 1, 60 simulations, recorded 2026-10-27.
- **Strong agent:** `tau2-bench/data/simulations/sample20_sonnet_t3/results.json`, copied to `results/runs/sample20_sonnet_t3.results.json`. It has 60 simulations, run on 2026-10-28 by `scripts/runs/run_sonnet20.ps1 -Trials 3`.

The two runs share the tau2 commit, the seed (300), the user model and its arguments, the substring communicate scorer, the concurrency and the timeout. The runs are a day apart, and the user simulator samples, so each run is one draw. The floor for run-to-run noise comes from block 2: on the 15 unchanged tasks, 6 of 45 Haiku trial slots changed outcome between two runs.

## Metrics (fixed now; computed by `scripts/strong_vs_weak/compare.py`)

1. **Pass rates.** Per model: tau2 pass^1 (mean over tasks of c/n) and pass^3 (tasks passed 3 of 3), with Wilson 95% intervals on the task shares.
2. **Paired per-task comparison.** For each task, the successes out of 3 for each model. Count the tasks where Sonnet is ahead, behind and equal. Run an exact two-sided sign test over the tasks that are not tied, and McNemar's exact test on pass^3 (passed 3 of 3 or not).
3. **Split by the no-op class.** The 7 no-op tasks of the sample (`results/static_scan.csv`, `noop_pass = 1`: 1, 9, 10, 26, 28, 46, 48) against the 13 others, with metrics 1 and 2 in each part.
4. **v2 re-score.** Re-score the Sonnet run with `scripts/v2/rescore.py` under the stock configuration and under full v2, with the same 3-vote judge rules as block 2. Report pass^1 and pass^3 of both models under both protocols, and the gap. The replay gate must reproduce every recorded Sonnet reward under the stock configuration.
5. **Cost.** Tokens times Sonnet 5.5 prices, and tokens per simulation against Haiku's.

## Predictions

- **P1.** Sonnet's tau2 pass^1 is above Haiku's 0.733, likely by +0.05 to +0.15.
- **P2.** With 20 tasks the paired sign test does not reach p < 0.05. That reads as "not separated on this sample", not as "no difference", because a test this small can only detect a large effect.
- **P3.** On the 7 no-op tasks both models score close to 3 of 3, so this class carries no information. Any gap sits in the 13 other tasks.
- **P4.** At least 2 of the 3 tasks whose text or reference is defective (7: wrong reference total; 32: the scenario forbids the reference path; 44: an ambiguous layover reading) stay at 0 of 3 for Sonnet under the stock scorer. The defect is in the task, not in the model.
- **P5.** Under v2 the Sonnet–Haiku gap does not shrink. v2 removes no-op passes for both models equally (re-scoring uses each conversation as recorded) and corrects task 7's total, which helps whichever model answers 708.

## Decision rule

"The exam separates the two models" is stated only if the paired sign test gives p < 0.05. Otherwise the result is reported as the observed difference with its interval and the test's p value, under the label "not separated on this sample". Either way the report states what the check cannot show: one run per model, 20 tasks, and a stochastic user simulator.
