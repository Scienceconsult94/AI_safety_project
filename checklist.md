# τ²-bench airline: validation checklist

Pinned: `sierra-research/tau2-bench` tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`; domain `airline`, split `base` (task ids "0".."49").
All paths are relative to `tau2-bench/`.

## Conventions

- `$RUN` = `--domain airline --task-split-name base --agent-llm anthropic/claude-haiku-5-5 --user-llm anthropic/claude-haiku-5-5 --communicate-scorer substring --max-concurrency 3 --timeout 900`.
  Seed 300 is the default (`src/tau2/config.py`). The default `{"temperature": 0.0}` for both models is rejected by current Anthropic models (HTTP 400, see issues_draft.md I5), so all runs pass `--agent-llm-args '{}' --user-llm-args '{}'` (provider-default sampling). Output: `data/simulations/<save_to>/results.json`.
- Probe: a copy of a recorded `results.json` in which the `messages` of one simulation are edited. Each tool call stays paired with its tool message by id, and `termination_reason` is set to `user_stop`.
  The copy is rescored with `tau2 evaluate-trajs <probe.json> -o <dir>`. Per `src/tau2/scripts/evaluate_trajectories.py`, this uses `EvaluationType.ALL`, the scorer recorded in `info.communicate_scoring`, `strict_replay=False`, and the tasks embedded in the file.
  Substring rescoring makes no LLM calls. Concrete scorer-bypass constructions live in the private folder; the rows below name only the check.
- `audit_log.csv` mapping: `category` = section number; `check` = `check_id`; `method` and `severity` as listed; `defect` = 1 when `defect_if` holds.
  A task is defective if it has ≥1 defect of severity medium or high. Benchmark-level and "n/a, by construction" rows are logged once with `task_id` = `ALL`.
- Agent runs: only 1e (`audit_gt`) and 1f (`audit_haiku_p3`). Checks 4f and 5c–5f reuse their trajectories, and every probe starts from one of them.
- DB = database; GT = ground truth; CI = confidence interval.

## 1. Solvability

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 1a | The task carries evaluation criteria with the expected reward basis. | static | `data/tau2/domains/airline/tasks.json`: `evaluation_criteria` is non-null and `reward_basis` == `["DB","COMMUNICATE"]`. `src/tau2/evaluator/evaluator.py` returns reward 1.0 when the criteria are null. | criteria are null or the basis differs | high |
| 1b | The reference actions replay without error on a fresh environment. | static | Pre-screen replay through `get_environment()` (`src/tau2/domains/airline/environment.py`) + `make_tool_call`. `src/tau2/evaluator/evaluator_env.py` swallows replay exceptions as `logger.warning("Error in golden actions ...")`, which silently changes the target. | any reference action raises | high |
| 1c | Every WRITE reference action changes the DB. | static | Pre-screen: hash before and after each action (`get_db_hash()`). Tool types come from `@is_tool(ToolType.READ/WRITE/GENERIC)` in `src/tau2/domains/airline/tools.py`; only WRITE tools mutate state. | a WRITE action leaves the hash unchanged, or the target hash equals the initial hash although a WRITE is listed | high |
| 1d | Every value the reference needs can be obtained by a legitimate agent. | static | Each reference argument (`user_id`, `reservation_id`, `flight_number`, `date`, payment id, passenger fields) is looked up in `user_scenario.instructions` (`known_info`, `reason_for_call`, `task_instructions`). If absent there, check that READ tools reach it from user-given ids in `data/tau2/domains/airline/db.json`. Values listed in `unknown_info` do not count as stated. | a required value is neither stated nor derivable | high |
| 1e | The GT agent, which sees the reference actions, reaches the target state. | agent_run | `tau2 run $RUN --agent llm_agent_gt --save-to audit_gt`. The registry filter `LLMGTAgent.check_valid_task` (`src/tau2/agent/llm_agent.py`) skips tasks with empty `actions`. Read `reward_info.db_check` and `termination_reason`. The GT prompt contains `actions` only, not `communicate_info`. | DB check fails and the cause traces to the task (target unreachable, user simulator lacks a needed value, reference conflicts with policy), not to an agent slip | high |
| 1f | Baseline solve rate with the audited model. | agent_run | `tau2 run-pass3 $RUN --save-to audit_haiku_p3`. Generic mode forces 3 trials (`add_pass3_args` in `src/tau2/runner/cli.py`). | none on its own; fills `haiku_pass` = k/3. A result of 0/3 together with a 1e failure goes to the 1e triage | — |

## 2. Scoring validity

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 2a | Positive control: an empty answer is guaranteed full reward. | static | Pre-screen `initial_db_hash`, `target_db_hash`, `communicate_info`. Documented case: task `1` in `docs/evaluation.md` ("intended τ-bench scoring"); the check must flag it. | `target_db_hash` == `initial_db_hash` AND `communicate_info` is empty | high |
| 2b | An empty or trivial answer passes. | probe | Keep only the default greeting (`DEFAULT_FIRST_AGENT_MESSAGE` in `src/tau2/orchestrator/orchestrator.py`) and one user turn, then rescore. | reward 1.0. A disagreement with 2a means the pre-screen or the scoring pipeline is wrong (log it in `note`) | high |
| 2c | An answer that only transfers to a human passes. | probe | The agent's first action is `transfer_to_human_agents`. That tool is GENERIC and `mutates_state=False`, so `Environment.set_state` (`src/tau2/environment/environment.py`) does not replay it. Rescore. | reward 1.0 while the reference and `description.purpose` expect resolution, not a transfer | high |
| 2d | A deliberately wrong solution passes. | probe | Take a recorded GT or Haiku trajectory and alter one WRITE call so that it breaks `data/tau2/domains/airline/policy.md` or the user's request (wrong reservation, flight, cabin, payment, or a forbidden write on a task where the agent should refuse). Rescore. | reward 1.0 | high |
| 2e | The end-state-only DB comparison hides forbidden intermediate writes. | probe | Scorer-bypass check (see the private folder). Can a trajectory that contains a policy-violating write still end at the target hash? `evaluator_env.py` compares final hashes only. | such a trajectory exists for the task and scores 1.0 | medium |
| 2f | An information dump passes COMMUNICATE. | probe | Scorer-bypass check on tasks with non-empty `communicate_info`. The substring scorer (`src/tau2/evaluator/evaluator_communicate.py`) tests `info.lower() in content.lower().replace(",", "")` over `AssistantMessage` text only and has no rule against contradictions. Rescore agent text in which the required strings appear among conflicting candidates. | reward 1.0 | high |
| 2g | Short expected strings match by accident. | static | List `communicate_info` strings that are ≤3 characters or bare integers. Search for them in non-answer positions (dates, ids, prices, greeting) in the 2b probe and in the GT and Haiku trajectories. | a match occurs in a non-answer position, or in the 2b probe | medium |
| 2h | A correct solution is rejected because the DB hash depends on order or on free choices. | probe | `get_pydantic_hash` hashes the whole DB (`src/tau2/utils/pydantic_utils.py`). New reservation ids come from the fixed sequence `HATHAT, HATHAU, HATHAV` (`_get_new_reservation_id` in `tools.py`). Permute independent WRITE calls (e.g. several `book_reservation`) or vary choices the scenario leaves open (payment method, passenger order), then rescore. | a policy-compliant variant that the scenario allows scores 0 | medium |
| 2i | A correct communication is rejected by the substring scorer. | static | For each expected string, check natural correct renderings: thousands separators other than the comma, decimals, currency signs, spelled-out numbers. Commas are stripped from agent text only, never from the expected string. | the expected string contains a comma (it can never match), or a natural correct rendering fails | medium |
| 2j | The choice of scorer changes the outcome. | probe | In a copy of `results.json`, set `info.communicate_scoring` to `{"scorer":"semantic","judge":{"model":"anthropic/claude-haiku-5-5","model_args":{}}}` (settings model in `src/tau2/data_model/semantic_communication.py`). Rescore and compare with the substring verdicts. | the verdict differs on any trial | medium |
| 2k | A requirement stated only in `nl_assertions` is not enforced. | static | Compare `nl_assertions` with `actions` and `communicate_info`. At this commit, `tau2 run` scores with `EvaluationType.ALL` (the `run_tasks` default in `src/tau2/runner/batch.py`), so NL assertions are not evaluated at all. | an assertion demands a behaviour (inform X, refuse Y) that neither the DB hash nor `communicate_info` checks, and breaking it still yields 1.0 | medium |
| 2l | Editing the tests, hardcoding answers, or reading the scorer. | static | n/a, by construction: the agent emits only text and in-process tool calls; scoring runs after the episode on fresh environments rebuilt from the task file. | — | — |

## 3. Isolation and leaks

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 3a | Tools have no file, network, process, environment-variable or clock access. | static | Grep the tool bodies in `src/tau2/domains/airline/tools.py` for `open(`, `os.`, `subprocess`, `socket`, `requests`, `http`, `datetime.now`, `environ`. | any hit inside a tool | high |
| 3b | `calculate` evaluates arithmetic only. | static | `calculate` in `tools.py` runs `eval(expression, {"__builtins__": None}, {})` after a character whitelist `0123456789+-*/(). `. Run time is bounded by `--timeout 900`. | the whitelist admits identifier characters | high |
| 3c | No reference or evaluation data reaches the tested agent. | static | `create_llm_agent` (`src/tau2/agent/llm_agent.py`) receives tools and policy and ignores `task`. Its system prompt is `AGENT_INSTRUCTION` + `data/tau2/domains/airline/policy.md`. Confirm in the logged requests (`--verbose-logs --llm-log-mode all`). | any `actions` argument, `communicate_info` value, `description` or `nl_assertions` text appears in the agent prompt or tool schemas | high |
| 3d | The user simulator's prompt does not contain the answer. | static | The user prompt is `str(task.user_scenario)` (`src/tau2/runner/build.py`; `UserScenario.__str__` in `src/tau2/data_model/tasks.py`): persona, domain, `reason_for_call`, `known_info`, `unknown_info`, `task_instructions`, plus the rules in `src/tau2/user/guidelines.py`. Search it for `communicate_info` values, computed amounts and statements of the target state. | found. The agent can echo the value, and the semantic judge also reads user turns | medium |
| 3e | `description` and `annotations` reach neither participant. | static | Grep for consumers: only `src/tau2/utils/display.py` and `src/tau2/scripts/manual_mode.py` use them. `annotations` is null in all 50 tasks. | a run-path consumer appears | high |
| 3f | No state carries over between simulations. | static | `get_environment()` loads `db.json` per simulation, deep-copying any DB object passed in. `AirlineTools` keeps state only in `self.db`; the id sequences are computed from the instance DB. Pre-screen: build the environment twice and compare `initial_db_hash`. | a tool writes module-level mutable state, or the initial hash differs between builds | high |
| 3g | The shared response cache is off. | static | `LLM_CACHE_ENABLED = False` in `src/tau2/config.py`. When it is on, a Redis or local LiteLLM cache is shared across trials (`src/tau2/utils/llm_utils.py`). | enabled during audit runs (trials would not be independent and pass^k would be inflated) | medium |
| 3h | The user simulator cannot change the DB. | static | `get_environment()` builds `Environment` without user tools, so `user_tools_for_task` (`src/tau2/runner/build.py`) returns None and `get_user_db_hash()` is None on both sides of the DB check. | user tools exist for airline | high |
| 3i | The GT agent sees the reference. | static | n/a, by construction: `llm_agent_gt` exists to measure solvability; its runs are never counted in `haiku_pass`. | — | — |
| 3j | Network, shared package repositories, credentials in the environment, access to the scorer and logs. | static | n/a, by construction: no agent code runs and there is no sandbox. API keys exist only in the harness process (LiteLLM), and no tool reads them (covered by 3a). | — | — |

## 4. Specification clarity

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 4a | The user's request matches the reference. | static | `reason_for_call` + `task_instructions` against the reference WRITE actions and their arguments. | the reference makes a change the user did not ask for, omits a permitted change the user asked for, or uses different values | medium |
| 4b | The reference complies with the policy. | static | Check each WRITE against `policy.md`: cancellation eligibility, basic-economy change rules, baggage, payment and certificate rules, and the clock "2024-05-15 15:00:00 EST" (policy line 3; `_get_datetime` in `tools.py`). | the reference violates the policy; escalate to high if no compliant trajectory reaches the target hash | medium |
| 4c | Choices the scenario leaves open are not fixed by the reference. | static | List the choices the reference fixes (payment method, flight among equal options, cabin, insurance, bag count). Check whether the scenario or the policy pins each one. | ≥2 compliant end states fit the scenario and only one hash passes | medium |
| 4d | Scenario facts match the DB. | static | Ids, names, dates and amounts in `known_info` / `task_instructions` against `db.json`: the user exists, the reservation belongs to the user, the flight exists on that date with that status. | mismatch; escalate to high if it blocks the reference path (see 1d) | medium |
| 4e | `nl_assertions` and `description` agree with the reference. | static | `nl_assertions`, `description.purpose`, `description.notes` against `actions` / `communicate_info`. | contradiction (e.g. an assertion forbids a write that the reference makes) | medium |
| 4f | A failure follows a defensible reading of the task text. | agent_run | Classify each failed GT or Haiku trajectory: is the agent's interpretation defensible under the scenario and policy, yet different from the reference? | yes for at least one trajectory | medium |

## 5. Determinism

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 5a | Replaying the reference is deterministic. | static | Replay `actions` on two fresh environments. The tools use a fixed clock (`_get_datetime` → `2024-05-15T15:00:00`) and fixed id lists (`_get_new_reservation_id`, `_get_new_payment_id`). | the two hashes differ | high |
| 5b | `--seed` reaches the models. | static | `set_seed` stores `llm_args["seed"]` (`src/tau2/agent/base/llm_config.py`). Per-trial seeds are `random.randint` values drawn after `random.seed(config.seed)` (`src/tau2/runner/batch.py`). `litellm.drop_params = True` (`llm_utils.py`), and the Anthropic API has no seed parameter. Check the logged request kwargs. | the seed is absent from Anthropic requests (the user simulator is then reproducible only through temperature 0.0) | low |
| 5c | The outcome is stable across trials. | agent_run | Per-task success vector in `audit_haiku_p3` (`pass_hat_k`, `src/tau2/metrics/agent_metrics.py`). | 1 or 2 successes out of 3, and the flip traces to the user simulator (different disclosure, early `###STOP###`, invented facts) rather than to the agent | medium |
| 5d | The user simulator follows its scenario. | agent_run | In every failed or flipped trajectory, compare user turns with `user_scenario` and with the rules in `src/tau2/user/guidelines.py` (use only stated info; do not stop before the request is done). | the simulator invents, withholds or contradicts scenario facts | medium |
| 5e | Wall-clock time and step limits do not decide the result. | agent_run | Read `termination_reason`: anything other than `agent_stop` / `user_stop` scores 0 (`evaluator.py`). `timeout` comes from `--timeout 900` (`orchestrator.py`); `max_steps` is 200 and `max_errors` 10 (`config.py`); `infrastructure_error` is excluded from the metrics. | the same task ends in `timeout`, `max_steps` or `too_many_errors` in ≥2 trials (a single occurrence: rerun and note) | medium |
| 5f | Re-deriving the agent's end state by replay matches the live run. | agent_run | The scored state is rebuilt from the trajectory by `Environment.set_state` (`src/tau2/environment/environment.py`). It re-executes only mutating calls, skips unknown tool names and calls marked `rejected`, and in live scoring (`strict=True`) raises when a replayed output differs from the recorded one. Scan the run logs and `reward_info` for replay mismatches. | a replay mismatch occurs, or `reward_info` is missing for a run that ended with `agent_stop` / `user_stop` | medium |
| 5g | Versions are pinned. | static | Every `results.json`: `info.git_commit` == `989d3285ae669e49503324bdb9981bf14fccedeb`; `info.language_tasks` task hashes; model ids in `info.agent_info` / `info.user_info` (alias or dated snapshot). LiteLLM version from `uv.lock`. | any mismatch: the row's evidence is invalid, rerun | — |

## 6. Reporting

| check_id | check | method | how | defect_if | severity |
|---|---|---|---|---|---|
| 6a | Reward and success definitions. | static | Reward is the product over `reward_basis` (`evaluator.py`). Success means reward within 1 ± 1e-6 (`is_successful`, `src/tau2/metrics/agent_metrics.py`). | published or audit numbers use another success rule | low |
| 6b | The pass^k formula. | static | `pass_hat_k` = C(c,k)/C(n,k) per task, then the mean over tasks (`agent_metrics.py`, after arXiv 2406.12045). Recompute it from `results.json` and compare with `tau2 view`. | mismatch | low |
| 6c | The number of trials. | static | `DEFAULT_NUM_TRIALS = 1` (`config.py`). `docs/leaderboard-submission.md`: 2.0 benchmarks are scored at one trial (pass@1); for 1.x text, 4 trials are preferred. `run-pass3` forces 3. Unequal per-task counts silently lower the maximum k (a warning in `get_metrics_df`). | unequal per-task trial counts, or k reported above the number of trials run | low |
| 6d | Confidence intervals. | static | Grep `src/tau2/metrics/` (and the whole of `src/tau2/`) for `confidence`, `interval`, `bootstrap`, `wilson`, `stderr`: no hits at this commit. The outputs are point estimates (`avg_reward`, `pass_hat_ks`). | no interval is reported (benchmark-level row, `task_id` = `ALL`) | low |
| 6e | Exclusions and denominators. | static | `infrastructure_error` runs are dropped from the metrics (`get_metrics_df`; `infra_error_count` in `compute_metrics`), while timeouts count as 0. | exclusions > 0 and not disclosed next to the score | low |
| 6f | Cost is recorded. | static | Each simulation's `agent_cost` / `user_cost` in `results.json` comes from LiteLLM `completion_cost`. A model missing from the price map gives 0.0 and a logged error (`get_response_cost`, `llm_utils.py`). | cost is 0.0 for Anthropic calls (cost unreported; take token usage from `agent_usage`) | low |
| 6g | The scorer is disclosed. | static | `info.communicate_scoring` in `results.json`; `effective_communicate_scoring` treats an unrecorded scorer as substring. The default is the semantic judge `gpt-5.5` (`config.py`). | a score is reported without its scorer, or substring and semantic scores are pooled | low |
| 6h | Diagnostics are kept apart from the score. | static | `tau2 view` prints `Partial Action Reward: m/n` (`action_checks`, computed under `EvaluationType.ALL`). `docs/evaluation.md` defines it as similarity to one reference path, not correctness. | partial action reward or NL-assertion output is reported as a success rate | low |

## Static pre-screen over all 50 tasks

One row per task, built in-process with `get_environment()` and the task list from `get_tasks("base")` (`src/tau2/domains/airline/environment.py`). Replay follows `evaluator_env.py`: `make_tool_call(name, requestor=action.requestor, **arguments)`.

- `task_id`
- `criteria_null`, `reward_basis`: whether `evaluation_criteria` is null, and the basis as listed (1a).
- `initial_db_hash`: `get_db_hash()` of a fresh environment; also built a second time for 3f (`initial_db_hash_rebuild`).
- `target_db_hash`: hash after replaying `evaluation_criteria.actions`; `target_db_hash_rerun` from a second replay (5a).
- `replay_errors`: reference actions that raised, with the message (1b).
- `target_eq_initial`: `target_db_hash` == `initial_db_hash` (2a).
- `n_actions`, `n_read`, `n_write`, `n_generic`: counts by `ToolType` from `get_tool_types(env.tools)` (`src/tau2/environment/toolkit.py`).
- `write_noop_ids`: WRITE actions that left the hash unchanged (1c).
- `n_book_reservation`: count of `book_reservation` in `actions` (2h).
- `ci_len`, `ci_min_chars`, `ci_has_comma`: number of `communicate_info` strings, length of the shortest, any comma (2g, 2i).
- `nl_count`: number of `nl_assertions` (2k, 4e).
- `ci_in_user_scenario`: any `communicate_info` value (lowercased, commas stripped) occurring in `known_info`, `unknown_info`, `task_instructions` or `reason_for_call` (3d).
- `ref_args_unstated`: reference argument values absent from the `user_scenario` text (input to 1d); `ref_args_in_unknown_info`: those named in `unknown_info`.
- `ids_missing_in_db`: user, reservation and flight ids named in `user_scenario` but absent from `db.json` (4d).
- `gt_eligible`: `n_actions` > 0 (the `llm_agent_gt` task filter; tasks with no actions get no 1e run).
- `positive_control`: `target_eq_initial` AND `ci_len` == 0.
- Output: `prescreen.csv`, one row per task, with `bench_commit` set to the pinned commit. It pre-fills the static rows 1a–1c, 2a, 2g, 2i, 3d, 3f, 4d and 5a in `audit_log.csv`. Checks 1d, 2k, 4a–4c and 4e start from its columns and are finished by reading the task.
- Sanity 1: task `1` must have `positive_control` = 1 (the documented case).
- Sanity 2: the name-only count (no WRITE tool in `actions` and empty `communicate_info`) is 23 tasks. The hash-based `positive_control` can differ from it only through tasks that 1b or 1c flag.
- Sanity 3: `gt_eligible` = 1 for 43 tasks, and `ci_len` > 0 for 6 tasks, as stated in `tasks.json`.
