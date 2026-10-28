# HAL's TAU-bench Airline leaderboard against the do-nothing floor

Checked on 2026-10-28.

**Question.** `external.md` measured that an agent that does nothing passes 19 of the 50 airline test tasks of the original tau-bench (38.0%). That run used `sierra-research/tau-bench` at `59a200c6` and the benchmark's own `Env.calculate_reward`. Can the scores that HAL publishes for TAU-bench Airline be compared with that floor?

## Answer

Yes for the rows of the "TAU-bench Tool Calling" scaffold. No for the rows of the "HAL Generalist Agent" scaffold.

Four Tool Calling rows sit below the floor. Each row is one run.

| model (label on the page) | accuracy | tasks passed, of 50 | Wilson 95% interval |
|---|---|---|---|
| Gemini 2.0 Flash High | 28.00% | 14 | 17.5–41.7% |
| o4-mini Low | 36.00% | 18 | 24.1–49.9% |
| GPT-4.1 | 36.00% | 18 | 24.1–49.9% |
| DeepSeek R1 | 36.00% | 18 | 24.1–49.9% |

The other nine Tool Calling rows score between 44% and 56%. An agent that does nothing, or that hands the customer over at step 0, scores 38.0% (19 of 50).

## Why the Tool Calling rows can be compared

1. **Same tasks.** HAL's harness runs airline task indices 0–49 of the test split (`hal/benchmarks/taubench.py` at `21d8dfd`). The HAL paper says it used the 50 public airline tasks of the original TAU-bench (arXiv 2510.11977, Appendices A4.1 and A10.9).
2. **Same scoring code.** HAL installs tau-bench from a fork, `benediktstroebl/tau-bench` at `807e348b` (the dependency pin in `pyproject.toml` from August 2025 on). This check read the fork's `tau_bench/envs/base.py` at that commit:
   - `calculate_reward` has the upstream logic: the database hash after replaying the reference actions, then the required outputs. The only change adds `taken_actions` to the result, which does not change the reward.
   - `step` ends the episode on a terminating tool such as the hand-over and then computes the reward, as upstream does.
3. **Same floor.** This check compared the fork's airline test file with upstream `59a200c6` task by task, with whitespace normalised. Only tasks 2, 8, 9, 10 and 23 differ.
   - On each file, the null-pass tasks were found by classifying every reference action as a write or a read by tool name and by checking for required outputs.
   - Both files give the same 19 tasks: 12, 13, 15, 17, 18, 21, 24, 29, 35, 36, 37, 38, 39, 40, 41, 42, 47, 48, 49. This is also the list measured by running the reward code on upstream.
   - So doing nothing scores 19 of 50 on HAL's version as well. This is a reading of the files; the fork was not run.
4. **Same accuracy.** HAL's accuracy is the sum of the 0-or-1 rewards divided by 50. A task that ends in an error or a timeout counts as 0. HAL's Tool Calling agent runs tau-bench's own `ToolCallingAgent` and returns `env.reward`, with no scorer of its own (`agents/taubench_tool_calling/tool_calling.py`).

## What this shows and what it does not

- **A count.** A run that scores 14 of 50 failed at least 5 of the 19 tasks that an immediate hand-over passes, because passing all 19 would give at least 19. Each run at 18 of 50 failed at least one of them.
- **Not a ranking against doing nothing.** Each row is one run. The 36% rows are one task below the floor, and both intervals contain 38%. Errors and timeouts count as failures, and their share in these runs is not known.
- **What it does show.** The page prints no floor, so a reader cannot tell that four published scores sit below what doing nothing earns on the same tasks.

## Rows that cannot be compared

Nine "HAL Generalist Agent" rows also score below 38%, between 10% and 32%. HAL's own note of 2026-10-05 explains why they do not count here:
- that scaffold rarely ends the episode, so most episodes get no reward and count as 0;
- HAL therefore calls these rows a lower bound and says they are not directly comparable with the Tool Calling rows.

Under that scaffold an agent that does nothing would also score 0, so the 38% floor does not apply.

## How this was checked

- **First, a desk check.** It read web pages and repository files at fixed commits. Nothing was cloned, installed or run.
- **Then these facts were checked again directly:**
  - the leaderboard text: the four rows, one run each, and the note on the Generalist rows;
  - the fork's `calculate_reward` and `step`;
  - the comparison of the two airline test files, task by task, and the null-pass list on each file.
- **Not checked again:**
  - which fork commit was installed when the runs were made. This comes from the dependency pin and the trace file names, which date the Tool Calling runs to October 2025. The traces are encrypted and were not opened.
  - the harness code for accuracy and errors, which the desk check read at the commits listed below.
- **What does not depend on those two points:**
  - every fork commit from 2025-02-23 on has the upstream reward logic, and the five changed tasks were edited in April 2025;
  - the 19 tasks are the same on the fork and upstream, so the floor is 19 of 50 for any fork version installed after that date.

## Other notes on the page (2026-10-05)

- Costs and token counts are overstated, by up to 2 times for affected models.
- `taken_actions` in the traces also contains the reference actions that were replayed during scoring.
- The harness repository is archived.

## Sources (accessed 2026-10-28)

- https://hal.cs.princeton.edu/taubench_airline
- https://arxiv.org/html/2510.11977
- https://raw.githubusercontent.com/princeton-pli/hal-harness/21d8dfd/hal/benchmarks/taubench.py
- https://raw.githubusercontent.com/princeton-pli/hal-harness/853cf33/pyproject.toml and https://github.com/princeton-pli/hal-harness/commit/edf9077 (the pin moved to `807e348`)
- https://raw.githubusercontent.com/princeton-pli/hal-harness/35acec3/agents/taubench_tool_calling/tool_calling.py
- https://raw.githubusercontent.com/princeton-pli/hal-harness/853cf33/hal/utils/local_runner.py and `vm_runner.py` at the same commit
- https://raw.githubusercontent.com/benediktstroebl/tau-bench/807e348b46a225242d5a045a8cecc690719e4b21/tau_bench/envs/base.py
- https://raw.githubusercontent.com/benediktstroebl/tau-bench/807e348b46a225242d5a045a8cecc690719e4b21/tau_bench/envs/airline/tasks_test.py
- https://github.com/benediktstroebl/tau-bench/commit/194bc1a (the task changes) and commits `cb7cf03`, `cd28da3`, `000e9ae` (history of the reward function)
- Local upstream clone: `../external_benchmarks/tau-bench/repo` at `59a200c6`.
