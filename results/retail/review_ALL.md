# Retail benchmark-level static review (task_id = ALL)

Checkout: `tau2-bench` at commit 989d3285ae669e49503324bdb9981bf14fccedeb (tag v2.0.0), domain `retail`, split `base` (114 tasks). Code paths are relative to `tau2-bench/src/tau2/` unless they start with `data/`, `docs/`, `results/` or `retail/` (the last two are relative to the project root). Every line reference was read on the retail code at this commit; none is copied from the airline review. Check 2j is not written here (it is filled after the runs). Rows are in `results/retail/review_ALL.csv`.

## 2e - defect 1, medium

The DB check rebuilds the agent's environment by replaying the trajectory and compares one hash of the whole final DB with the gold hash (`evaluator/evaluator_env.py:85-94, 118-129`; `environment/toolkit.py:242-244`). The two retail address tools overwrite the stored address and change no status, so they can be called again (`domains/retail/tools.py:484-497, 697-706`). The probe (`results/retail/probe_2d.csv`, check 2e) wrote a wrong address before each reference address write: 35 probes over 24 tasks, 34 replayed and ended at exactly the gold hash, 1 (task 39) is undecided because the reference itself contains a lookup that raises. The hidden write is therefore confirmed in all 23 tasks with a clean replay; in 16 of them the reward is the DB part alone, in 7 the judge also decides but sees only tool outputs, not tool-call arguments. The other WRITE tools refuse a second call, so the class is limited to the two address tools, but by the same overwrite a write-and-revert of any address leaves any task's end state unchanged (static reading, not probed). Note for readers of the probe file: `action_id` labels follow `tasks.json`, where some tasks carry ids of the next task (e.g. task 96 has action `97_0`).

## 2f - defect 0

No retail task has `COMMUNICATE` in `reward_basis` (112 tasks `["DB","NL_ASSERTION"]`, tasks 33 and 34 `["DB"]`), and `evaluate_simulation` calls the communicate evaluator only when it is in the basis (`evaluator/evaluator.py:216-223, 265-268`). An information dump against `communicate_info` therefore cannot change a retail reward; only the ignore-basis modes, which no run path uses by default, would score it. n/a for the reward.

## 2g - defect 0

Short expected strings exist (two-character strings in tasks 2, 3, 4, 40, 43; numeric-only strings in 27 tasks, `results/retail/static_scan.csv`), but the substring scorer never runs on retail, so an accidental match cannot reach the reward. Facts that are also `nl_assertions` are judged by the LLM, which belongs to 2j. n/a for the reward.

## 2i - defect 0

For the same reason a correct rendering can never be rejected by the substring scorer in retail; in addition, no expected string contains a comma (114/114). Renderings of amounts inside `nl_assertions` are a question for the judge (2j). n/a for the reward.

## 2l - defect 0

Both environments are rebuilt after the episode (`evaluator/evaluator_env.py:85-97`) and evaluation runs on the finished conversation (`runner/simulation.py:137`); the judge is called on the finished transcript (`evaluator/evaluator_nl_assertions.py:117-122`). n/a by construction, as in airline. The judge reads the agent's text verbatim, so text written for the judge is a separate surface that 2l does not cover; it was not probed.

## 2m - defect 1, medium

`data/tau2/domains/retail/policy.md` requires authentication first (line 10), one user per conversation (14), listed details and an explicit "yes" before every DB update (16), and one exchange/modify call per order (84). The tools enforce only the last one, and not fully: item modification, exchange, return and payment change refuse a repeat call through status or payment-history checks (`tools.py:527-528/585, 272-273/310, 735-736/755, 620-624`), while the order-address tool uses a substring status check and changes nothing (`tools.py:164-170, 484-486`). No tool receives or checks the authenticated identity, confirmation exists only as docstring text, and READ calls are skipped in replay (`environment/environment.py:393-397`), so these steps leave no DB footprint. The reward is DB x NL (`evaluator/evaluator.py:253-264`) and none of the 61 `nl_assertions` names any of these requirements, so a violation still scores 1.0. The optional authentication classifier runs only with `--auto-review`, is a diagnostic count and judges the outcome, not the order of steps. The upstream `issues` entry on task 5 (open) records the same authentication gap.

## 3a - defect 0

The grep over `domains/retail/tools.py` (797 lines) for `open(`, `os.`, `subprocess`, `socket`, `requests`, `http`, `datetime`, `environ`, `random` gives 3 hits, all on import lines 18-20 where `environ` matches the package name `tau2.environment`; no tool body matches. Retail tools read no clock at all and create no ids; the only `print` is under `__main__`. No defect.

## 3b - defect 0

`calculate` (`tools.py:186-188`) uses the same whitelist `"0123456789+-*/(). "` and `eval(expression, {"__builtins__": None}, {})` as airline, so no names, attributes or calls are reachable. No defect; `**` is admitted and the run timeout is checked only between steps (`orchestrator/orchestrator.py:238-249, 771`).

## 3c - defect 0

`create_llm_agent` ignores the task and builds the prompt from the policy and the generic agent instruction (`agent/llm_agent.py:89-92, 499-516`); tool schemas are name, docstring and parameters (`environment/tool.py:140-147`); no retail task has `initial_state` or `agent_opener`. A cross-check of 556 reference and `communicate_info` strings against the tool text finds only enum values, trivial substrings and the docstring example product id that tasks 2-4 copy into a failing reference lookup (a 1b matter, docstring to reference, not task data to the agent). No defect (static only; confirm from verbose logs).

## 3e - defect 0

`description`, `annotations` and the retail-only `issues` field are read only by display, manual-mode and viewer code and by `Task.__str__`, which no retail run path calls; the user simulator receives only `str(task.user_scenario)` (`runner/build.py:221`). `annotations` is null in all 114 tasks. No defect.

## 3f - defect 0

`get_environment()` loads `db.json` per simulation or deep-copies a passed DB (`domains/retail/environment.py:26-29`), the loader has no cache (`environment/db.py:14-17`), and module-level names in the retail package are type aliases and path constants. The pre-screen built the initial hash twice and replayed twice with identical hashes in 114/114 tasks. No defect (static part).

## 3g - defect 0

`LLM_CACHE_ENABLED = False` (`config.py:71`) selects `litellm.disable_cache()` (`utils/llm_utils.py:87-110`); there is no override, and the judge calls the same `generate()`. No defect, provided `config.py` stays unmodified (the run log records a clean checkout).

## 3h - defect 0

The retail environment is built without user tools (`domains/retail/environment.py:34-38`), so `user_tools_for_task` returns None and the user DB hash is None on both sides of the DB check. No retail task lists user tools. No defect.

## 3i - defect 0

`llm_agent_gt` is registered with a filter that skips tasks without actions and reads the reference into its prompt by design (`registry.py:302-306`; `agent/llm_agent.py:210-220, 277`). n/a by construction; GT runs measure solvability only.

## 3j - defect 0

No agent code runs and there is no sandbox; the only executable surface is the arithmetic-only `calculate`, and no tool reads environment variables or credentials. n/a by construction, as in airline.

## 5b - defect 1, low

The per-trial seed is stored in `llm_args["seed"]` and passed to LiteLLM (`agent/base/llm_config.py:41-48`; `orchestrator/orchestrator.py:543-545`; `runner/batch.py:874-875`). In the installed LiteLLM 1.81.11 the Anthropic provider does not list `seed` as supported, and with `litellm.drop_params = True` unsupported parameters are removed before the request (`litellm/llms/anthropic/chat/transformation.py:178-203`; `litellm/utils.py:3840, 3913-3918`; both under the installed package folder `tau2-bench/.venv/Lib/site-packages/`), so the seed does not reach Anthropic models; the judge call passes no seed at all. The tau2 request log is written before the drop and still shows the seed. Because the default temperature 0.0 is also rejected, the retail runs use provider-default sampling, and nothing pins the user simulator or the judge. Defect 1, low (the airline row's unverified step is now verified statically).

## 6a - defect 0

Success is reward within 1 +/- 1e-6 (`metrics/agent_metrics.py:16`); the reward is the product over the basis, in retail DB x NL (DB only for tasks 33, 34), with a binary NL part (`evaluator/evaluator.py:233-268`; `evaluator/evaluator_nl_assertions.py:47-48`); premature termination scores 0. No defect (static).

## 6b - defect 0

pass^k is C(c,k)/C(n,k) per task, averaged over tasks (`metrics/agent_metrics.py:126, 177-180, 244`). No defect (static); the numeric recompute follows on the retail results.

## 6c - defect 0

One trial is the default and the official 2.0 rule (`config.py:12`; `docs/leaderboard-submission.md:30-31`); the audit uses `run-pass3`. Unequal per-task counts lower the maximum k with only a warning (`metrics/agent_metrics.py:156-165`). No defect (static); counts are checked on the recorded results.

## 6d - defect 1, low

Nothing under `metrics/` mentions an interval, and no file in `src/tau2` computes one; the outputs are point estimates. Defect 1, low, as in airline; the audit adds its own Wilson intervals.

## 6e - defect 0

Infrastructure errors are excluded from the metrics and the exclusion is printed next to the score (`metrics/agent_metrics.py:138-145`; `utils/display.py:938-945`). Retail adds a path into that exclusion: the stock judge parser is a bare `json.loads` (`evaluator/evaluator_nl_assertions.py:123`), evaluation runs inside the retried unit, and a rejected reply re-runs the whole conversation up to 4 times before the trial becomes an infrastructure error (`runner/batch.py:608-618, 649-660`; `runner/progress.py:34-35, 52`; `config.py:65`). With 9 of 10 probe replies rejected by that parser, this path matters for the stock scorer; the audit overlay parses tolerantly and reports rejections under 2j. No defect (static); the retail runs are still in progress, and the exclusion count is filled by the agent-run rows.

## 6f - defect 1, low

`get_response_cost` returns 0.0 on any pricing error (`utils/llm_utils.py:153-157`), and every such error in the retail run log reads "LLM Provider NOT provided ... model=claude-haiku-5-5"; the judge's own cost is discarded by the NL evaluator and has no field in the results; and the greeting message carries no cost, which makes `agent_cost` None (`orchestrator/orchestrator.py:147-153`; `utils/llm_utils.py:755-757`). In the in-progress retail results every recorded simulation has `agent_cost` None and `user_cost` 0.0, and `agent_usage` is None in text mode. Defect 1, low: cost is unreported, so the audit derives it from per-message token usage.

## 6g - defect 1, low

`Info` in `results.json` records the communicate scorer but has no field for the evaluation type or for the NL judge model, arguments or prompt version (`data_model/simulation.py:942-1069`), and the judge model is a hard-coded constant with no CLI flag (`config.py:45-46`; `evaluator/evaluator_nl_assertions.py:117-122`). The judge decides the reward in 40 of 114 retail tasks (`NL_ASSERTION` is in 112 bases, but 72 of those have no assertions), yet a run scored with a different judge, as in this audit, produces a file that looks the same. The documentation states that the CLI runner defaults to `ALL_WITH_NL_ASSERTIONS` (`docs/evaluation.md:171`), while every CLI path calls `run_tasks`/`prepare_batch` without an evaluation type and gets `EvaluationType.ALL` (`cli.py:864`; `runner/batch.py:850, 1011, 1248-1254`); the mismatch is verified, changes no retail reward, and makes the "diagnostic only" sentence at `docs/evaluation.md:152-154` untrue for `tau2 run`. Severity low, because 6g is pre-registered as low and the judge's effect on the numbers is measured under 2j.

## 6h - defect 0

Partial action reward and read/write action counts are shown under their own headings, apart from Average Reward and Pass^k, and the docs call them a similarity signal (`utils/display.py:529-537, 976-1003`; `docs/evaluation.md:176-177`); NL assertions in retail are part of the reward. No defect (static).

## Could not verify

- 2e: the write-and-revert variant (any address changed and restored in a task whose target leaves it unchanged) follows from the overwrite code but was not probed; task 39 is undecided in the probe because its reference raises before the probed write is scored.
- 3c: the exact agent prompt and tool schemas sent in a real retail run; confirm from verbose logs.
- 5b: the seed drop is read from the installed LiteLLM source; no provider-level request was captured.
- 6f: the no-op probe outputs (`results/retail/noop_judge_probe.md`, `judge_calls_noop.json`) contain no cost-error lines; the pricing errors come from the in-progress run log, where agent, user and judge calls share one model id and cannot be told apart.
- 6a-6c, 6e, 6h: static verdicts; numeric checks need the finished retail `results.json`.
