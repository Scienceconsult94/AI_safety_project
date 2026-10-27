# Benchmark-level static review (task_id = ALL)

Checkout: `tau2-bench` at commit 989d3285ae669e49503324bdb9981bf14fccedeb (tag v2.0.0), airline domain. Paths are relative to the checkout. Static reading only; no run was made.

## 2l - defect 0
- Inspected: `src/tau2/evaluator/evaluator_env.py:85-121`.
- Quote: `gold_environment = environment_constructor(**deepcopy(env_kwargs))`.
- Verdict: n/a by construction (defect 0).

## 3a - defect 0
- Inspected: all 15 `@is_tool` bodies in `src/tau2/domains/airline/tools.py`, plus helpers `utils/text_match.py`, `domains/airline/region.py`.
- Grep for `open(`, `os.`, `subprocess`, `socket`, `requests`, `http`, `datetime.now`, `environ`, `random`: no hits. Clock is a constant: `return "2024-05-15T15:00:00"` (tools.py:158).
- Only side effect: `logger.debug/info/warning` (tools.py:419, 431, 433, 783, 784) - logging only, does not touch state.
- Verdict: no defect.

## 3b - defect 0
- Inspected: `calculate` in `src/tau2/domains/airline/tools.py:386-402`.
- Whitelist: `"0123456789+-*/(). "`; call: `eval(expression, {"__builtins__": None}, {})`.
- No letters or `_` admitted, so no names, attributes or calls are reachable. Verdict: no defect.
- Side note: `**` is admitted; `_check_timeout` (orchestrator.py:238-249) runs between steps, so the `--timeout 900` bound in the checklist does not interrupt one long `eval`.

## 3c - defect 0
- Inspected: `create_llm_agent` (`src/tau2/agent/llm_agent.py:499-516`), `LLMAgent.system_prompt` (89-91), `build_agent` (`src/tau2/runner/build.py:100-177`), `Tool.openai_schema` (`src/tau2/environment/tool.py:140-147`), `AirlineTools.get_tools` (tools.py:76-89).
- Quote: `return SYSTEM_PROMPT.format(domain_policy=self.domain_policy, agent_instruction=AGENT_INSTRUCTION)`. `task=task` is passed by build.py:173 but `create_llm_agent` reads only `llm`, `llm_args`, `additional_stop_tool_names`.
- The policy string is `localized_transfer_policy(policy)` + language guidance (build.py:86-89); for English this may append the pack clause `Respond in English using Latin script; ...` (data/tau2/multilingual/en/pack.yaml:6) - generic, not task data. All 50 tasks have `initial_state` null, so no seeded history.
- Tool schemas: docstrings + params; regional rewrites only when `regional_settings` is set (None on the default path). Cross-check of 105 distinct action-argument / `communicate_info` strings against tools.py text: only enum values (`economy`, `business`, `basic_economy`, `one_way`, `round_trip`) match.
- Verdict (static): no defect. Static only; confirm from --verbose-logs after the first run.

## 3e - defect 0
- Inspected: grep `task\.description|\.annotations|"annotations"` over `src/tau2`; `build_user` (`src/tau2/runner/build.py:180-234`); `data/tau2/domains/airline/tasks.json`.
- Quote: `"instructions": str(task.user_scenario),` (build.py:221) - the user simulator receives only `user_scenario`.
- `description` is read only in display/manual-mode code; `annotations` is null in all 50 tasks and unread. Verdict: no defect.

## 3f - defect 0
- Inspected: `src/tau2/domains/airline/environment.py:18-38`, `tools.py` (class body, `_get_new_reservation_id` 131-143, `_get_new_payment_id` 146-153), module-level assignments in `src/tau2/domains/airline/*.py`, `global`/`lru_cache` grep in `domains/airline` and `environment/`.
- Quote: `db = FlightDB.load(AIRLINE_DB_PATH)` / `db = db.model_copy(deep=True)`; `if reservation_id not in self.db.reservations: return reservation_id`.
- Module level holds only `Literal`/`Annotated` aliases (data_model.py) and path constants (utils.py:3-6); no `global`, no caches. Tool state lives in `self.db`.
- Verdict (static part): no defect.

## 3g - defect 0
- Inspected: `src/tau2/config.py:70-72`, `src/tau2/utils/llm_utils.py:87-110`, grep for `LLM_CACHE_ENABLED|enable_cache` over `src/tau2`.
- Quote: `LLM_CACHE_ENABLED = False`; else-branch `litellm.disable_cache()`.
- Verdict: no defect.

## 3h - defect 0
- Inspected: `src/tau2/domains/airline/environment.py:34-38`, `src/tau2/environment/environment.py:85-98, 150-156, 284-291`, `src/tau2/runner/build.py:92-97`.
- Quote: `if self.user_tools is None: raise ValueError("User tools not available")`; `user_tools_for_task` catches it and returns None.
- Verdict: no defect.

## 3i - defect 0
- Inspected: `src/tau2/registry.py:302-307`, `src/tau2/agent/llm_agent.py:176-300`.
- Quote: `for i, action in enumerate(self.task.evaluation_criteria.actions):` - the GT agent is given the reference by design.
- Verdict: n/a by construction (defect 0).

## 3j - defect 0
- Inspected: tool surface from 3a; `llm_utils.generate` call path.
- Verdict: n/a by construction (defect 0).

## 5b - defect 1, severity low
- Inspected: `src/tau2/agent/base/llm_config.py:41-48`, `src/tau2/orchestrator/orchestrator.py:542-545`, `src/tau2/runner/batch.py:873-883`, `src/tau2/utils/llm_utils.py:72, 660-680`.
- Quote: `self.llm_args["seed"] = seed`; `seeds = [random.randint(0, 1000000) for _ in range(config.num_trials)]`; `litellm.drop_params = True`. The seed is passed as a `completion(**kwargs)` argument.
- The Anthropic Messages API accepts model, messages, system, max_tokens, temperature, top_p, top_k, stop_sequences, tools, tool_choice, thinking, metadata, stream - no seed. With `drop_params=True` LiteLLM drops unsupported OpenAI params for the Anthropic provider; this last step is UNVERIFIED in litellm 1.81.11 (source not available).
- `request_data["kwargs"]` (llm_utils.py:664-672) is built before `completion`, so the tau2 log shows `seed` even when it is dropped; only the provider-level request can confirm.
- Verdict: defect 1, low - the seed does not reach Anthropic models; reproducibility of the user simulator relies on temperature 0.0 only.

## 6a - defect 0
- Inspected: `is_successful` (`src/tau2/metrics/agent_metrics.py:12-16`), `src/tau2/evaluator/evaluator.py:123-140, 217-283`.
- Quote: `return (1 - 1e-6) <= reward <= (1 + 1e-6)`; `if task_reward_basis & env_bases: ... reward *= env_reward_info.reward`.
- Verdict: no defect (static).

## 6b - defect 0
- Inspected: `pass_hat_k` and `get_tasks_pass_hat_k` (`src/tau2/metrics/agent_metrics.py:113-191`), `compute_metrics` (238-245).
- Quote: `return math.comb(success_count, k) / math.comb(num_trials, k)`; per-task `n` is the task's own evaluated row count.
- Verdict: no defect (static); numeric comparison pending a results.json.

## 6c - defect 0
- Inspected: `src/tau2/config.py:12`, `docs/leaderboard-submission.md:30-31` ("For 1.x text, at least 4 trials per domain are strongly preferred"), `src/tau2/cli.py:868-875`, `get_metrics_df` (`agent_metrics.py:152-166`).
- Quote: `Setting max k to {min_k}.` - after infra exclusions a task with fewer trials silently lowers max k (warning only).
- Verdict: no defect (static); per-task counts to be checked on recorded results.

## 6d - defect 1, severity low
- Inspected: grep over `src/tau2/metrics/` and `src/tau2/`; `AgentMetrics` (`agent_metrics.py:19-110`).
- Hits outside metrics are unrelated (`sys.stderr` log sinks, `interruption_check_interval_seconds`, `judges/fidelity.py:52` finding confidence).
- Verdict: defect 1, low - only point estimates (`avg_reward`, `pass_hat_ks`).

## 6e - defect 0
- Inspected: `get_metrics_df` (`agent_metrics.py:129-166`), `compute_metrics` (217-236), `evaluator.py:123-133`, metrics table in `src/tau2/utils/display.py:936-965`.
- Quote: `f"[red]{metrics.infra_error_count}[/] (excluded from metrics below)"`; `TerminationReason.TIMEOUT` is not AGENT_STOP/USER_STOP, so reward 0.0 and it stays in the denominator.
- Verdict: no defect (static).

## 6h - defect 0
- Inspected: `src/tau2/utils/display.py:516-540, 976-1003`, `docs/evaluation.md:168-186`.
- Quote (docs/evaluation.md:176-177): similarity signal against one reference trajectory, not a correctness verdict.
- Read/Write Actions are shown as `correct/total (x%)` under a separate `Action Metrics` header, not as success. Verdict: no defect (static).

## Could not verify

- 5b: that LiteLLM 1.81.11 drops `seed` for the Anthropic provider under `drop_params=True` (LiteLLM source not available); the Anthropic Messages API itself has no seed parameter.
- 3c: the exact agent prompt and tool schemas sent in a real run (including whether the English language-pack clause is appended); confirm from --verbose-logs after the first run.
- 3b: behaviour of a pathological `**` expression in a real run (nothing besides the between-step `_check_timeout` was found that would stop it).
- 3g: that `config.py` is unmodified in the checkout used for the audit runs (no runtime override exists in source).
- 6a, 6b, 6c, 6e, 6h: verdicts are static; numeric checks (pass^k recompute, per-task trial counts, infra-error exclusions, wording of the published numbers) need a recorded results.json.
- 6f, 6g, 5g: skipped by scope (need a recorded results.json).
