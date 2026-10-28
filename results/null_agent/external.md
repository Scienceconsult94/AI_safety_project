# Null-agent and refusal-agent floors on four external agent benchmarks

Measurement date 2026-10-28. No model was called and no paid API was used. Every benchmark was installed in its own folder under `../external_benchmarks/<name>/` (a sibling of the project folder, outside the repository) with its own virtual environment; the reading and writing scripts are in `scripts/null_agent/external/` and were run in isolated mode (`python -I`). Per-task and per-category outputs are in `results/null_agent/external_raw/`.

Terms:
- **Null agent**: does nothing (empty answer, empty trajectory, or ends at step 0).
- **Refusal agent**: does nothing except give the benchmark's "cannot be done" answer (no function call in BFCL, hand-over to a human in tau-bench, `FAIL` in OSWorld, an error status in WebArena-Verified, `N/A` in the original WebArena).
- **Measured by the evaluator**: the benchmark's own scoring code was run on the null or refusal output. **Counted from task definitions**: the score follows from the scoring code and the task files without running the evaluator.
- Intervals are Wilson 95% intervals over tasks (a task set treated as a sample of tasks); on the fixed task set itself the floor is exact.

Reference point: on tau2-bench (commit `989d3285`) the null agent passes 23/50 airline, 6/114 retail and 0 telecom tasks (`results/null_agent/tau2_null_agent.md`).

## Summary table

| benchmark | repository, commit / package version | tasks | null-agent floor | refusal-agent floor | method | caveats |
|---|---|---|---|---|---|---|
| BFCL V4 | ShishirPatil/gorilla `6ea57973` (2026-03-23), folder berkeley-function-call-leaderboard; PyPI `bfcl-eval` 2026.3.23 (identical code and data) | 5,106 entries in the 22 scoring categories | **10.00 / 100 overall** (irrelevance 240/240, live irrelevance 884/884, every other category 0) | **10.00 / 100** (a refusal sentence without a call scores the same in every category) | measured by the evaluator (`bfcl evaluate`, all 22 scoring categories offline, overall from the evaluator's own `data_overall.csv`) | a registered model name is needed only to pick the decoder (prompt and function-calling decoders give the same result); `soundfile` added to the venv for an import-time dependency; format-sensitivity (non-scoring) not run |
| tau-bench, airline test | sierra-research/tau-bench `59a200c6` (2026-03-18) | 50 | **19/50 = 38.0%** [25.9–51.8] | **19/50 = 38.0%** (hand-over at step 0) | measured by the benchmark's reward code (`Env.calculate_reward`; refusal through `Env.step`) | gold-action positive control 50/50 = 1.0; the reward is the database hash plus required outputs, so no user simulator is involved |
| tau-bench, retail test | same | 115 | **7/115 = 6.1%** [3.0–12.0] | **7/115 = 6.1%** | same | positive control 115/115; 2 of the 7 passes are tasks whose only reference write is rejected by the environment on replay |
| tau-bench, retail train | same | 500 | **5/500 = 1.0%** [0.4–2.3] | **5/500 = 1.0%** | same | positive control 500/500; all 5 passes are tasks whose only reference write is rejected on replay (insufficient gift-card balance) |
| tau-bench, retail dev | same | 20 | **1/20 = 5.0%** [0.9–23.6] | **1/20 = 5.0%** | same | positive control 20/20; small split |
| OSWorld-Verified, current | xlang-ai/OSWorld `044bc339` (2026-10-24), `evaluation_examples/test_all.json` | 369 (361 without Google Drive) | not measured (needs the virtual machine) | **26/369 = 7.0%** [4.9–10.1]; 26/361 = 7.2% without Google Drive | counted from task definitions + quoted scoring code | the do-nothing run (DONE at step 0) needs the VM and was not run |
| OSWorld-Verified, as released | xlang-ai/OSWorld `00804f81` (2025-07-29; task files unchanged 2025-07-24 to 2025-07-31) | 369 (361) | not measured | **30/369 = 8.1%** [5.8–11.4]; 30/361 = 8.3% | counted from task definitions | 5 tasks changed from "infeasible" to a real checker after release, 1 the other way |
| WebArena-Verified | ServiceNow/webarena-verified `6473f72d` (2026-02-07, tag v1.2.3) | 812 | **0/812 = 0.0%** [0.0–0.5] (empty answer, start-page trace); with a zero-entry trace all 812 are evaluation errors | **24/812 = 3.0%** [2.0–4.4] for the best single fixed refusal (retrieve, `NOT_FOUND_ERROR`); 31/812 = 3.8% [2.7–5.4] if the right type and error status are chosen per task | measured by the evaluator (`webarena-verified eval-tasks`, offline, synthetic start-page network trace) | network trace synthesised (start page only); tasks 699, 700, 811 raise an evaluator error in every variant; task 319 cannot be passed by any response tried; supplementary: reporting navigate/`SUCCESS` at step 0 passes 10/812 (1.2%) |
| WebArena (original task file) | `assets/dataset/test.raw.json` in the WebArena-Verified repository; scoring code web-arena-x/webarena `dce04686` | 812 | not measured (needs the live sites and, for an empty answer on "N/A" tasks, an LLM judge) | **36/812 = 4.4%** [3.2–6.1] (answer "N/A") | counted from task definitions + quoted scoring code | the 36 "N/A" tasks are all string-match tasks scored by exact match, no LLM call |

## BFCL V4

What was run. `bfcl-eval` 2026.3.23 was installed from PyPI into `../external_benchmarks/bfcl/.venv` (Python 3.11). Its code and data are identical, apart from line endings, to the `bfcl_eval` folder of the gorilla repository at commit `6ea57973` (sparse clone in `../external_benchmarks/bfcl/gorilla`). Result files were written for every entry of the 22 scoring categories (`TEST_COLLECTION_MAPPING["all_scoring"]`), with entry IDs and turn counts taken from the package's own loader (`load_dataset_entry(..., include_prereq=False)`, the same call the evaluator makes). Response per entry: an empty string for single-turn entries, a list with one `[""]` per user turn for multi-turn entries (the turn count equals the ground-truth turn count, so no entry is treated as force-terminated), `[[""]]` for agentic (memory, web search) entries. Three variants: null response under a prompt-mode decoder, null response under a function-calling decoder, and the refusal sentence "I cannot help with this request." under the prompt-mode decoder.

Commands (from the project root; `BFCL_PROJECT_ROOT` set to a per-variant work folder under `../external_benchmarks/bfcl/work/`, as the README requires for a PyPI install):

```
../external_benchmarks/bfcl/.venv/Scripts/python.exe -I -X utf8 scripts/null_agent/external/bfcl.py write --model Qwen/Qwen3-8B --response ""
PYTHONUTF8=1 ../external_benchmarks/bfcl/.venv/Scripts/bfcl.exe evaluate --model Qwen/Qwen3-8B --test-category all_scoring
../external_benchmarks/bfcl/.venv/Scripts/python.exe -I -X utf8 scripts/null_agent/external/bfcl.py summarize --model Qwen/Qwen3-8B --out-csv results/null_agent/external_raw/bfcl_categories.csv --label null_prompt
```
(the same for `Qwen/Qwen3-8B-FC` and for the refusal sentence).

Result (identical for all three variants):

| category group | entries | null score |
|---|---|---|
| non-live AST (simple python/java/javascript, multiple, parallel, parallel multiple) | 1,150 | 0.00% |
| live AST (simple, multiple, parallel, parallel multiple) | 1,351 | 0.00% |
| irrelevance (non-live 240 + live 884) | 1,124 | 100.00% |
| live relevance (displayed, not in the overall score) | 16 | 0.00% |
| multi-turn (base, miss func, miss param, long context) | 800 | 0.00% |
| agentic: web search (base, no snippet) | 200 | 0.00% |
| agentic: memory (kv, vector, recursive summarisation) | 465 | 0.00% |
| **overall** (evaluator's `data_overall.csv`) | | **10.00%** |

How the overall score is assembled: `eval_runner_helper.generate_leaderboard_csv` computes overall = 10% non-live AST (unweighted mean of simple, multiple, parallel, parallel multiple; simple = mean of python, java, javascript) + 10% live AST (entry-weighted mean of the four live AST categories) + 10% irrelevance (unweighted mean of non-live and live irrelevance) + 30% multi-turn (unweighted mean of the four) + 40% agentic (mean of web-search mean and memory mean). Live relevance is shown but has no weight. The recomputation from the per-category score files gives the same 10.00. Every failed entry fails for a content reason recorded by the evaluator (wrong number of calls, empty turn response, no final message or answer not found, decoder failure on the refusal sentence); no entry failed with an inference error or a turn-count mismatch, so the result files were accepted as model output (under the prompt decoder the Java and JavaScript entries are labelled `decoder_wrong_output_format`, the evaluator's label for an empty decoded call list). All 22 scoring categories were scored offline; none needed a live service: web-search and memory entries are scored on the final message only, and multi-turn scoring executes the ground-truth calls against the package's in-process simulated backends.

Deviations from the survey: the 10.0/100 figure is confirmed by the evaluator. The irrelevance entry count is 1,124 (240 + 884), not 1,122 (240 + 882); live relevance has 16 entries, not 18 (the 18 was a V2-release figure). The survey's expectation that multi-turn and agentic categories give 0 for an empty response is confirmed.

Setup deviations: (1) the evaluator imports every model handler on start-up; `qwen-agent` 0.0.34, a declared dependency, imports `soundfile`, which is not declared, so `soundfile` 0.14.0 was added to the BFCL venv. (2) The evaluator constructs the handler of the named model; OpenAI handlers raise "Missing credentials" without an API key, so locally hosted model names were used (`Qwen/Qwen3-8B` with the default prompt decoder, `Qwen/Qwen3-8B-FC` with a function-calling decoder), whose handlers need no credentials. The model name only selects how the stored response is decoded; no model was loaded or run.

## tau-bench (original)

What was run. The repository was cloned (`59a200c6`, 2026-03-18) and installed non-editable into `../external_benchmarks/tau-bench/.venv`. For every task of every split the environment accepts (airline: test; retail: test, train, dev) three trajectories were scored with the benchmark's own code:
- null: a fresh environment with no action, then `Env.calculate_reward()`; this hashes the untouched database, reloads it, replays the reference actions through `Env.step`, compares the two hashes, and checks the required outputs against the agent's `respond` messages (there are none);
- refusal: a fresh environment and one `env.step(transfer_to_human_agents)` at step 0; the environment ends the episode on this terminate tool and computes the reward itself;
- positive control: a fresh environment, every reference action replayed through `env.step` (the terminate tool is skipped; it does not touch the data), one `respond` message per required output containing the output verbatim, then `Env.calculate_reward()`.

The user simulator was built with the benchmark's "human" strategy, whose constructor makes no call; `reset()` was never called and the reference actions contain no `respond` action, so no model and no console input were reached.

Command (from the project root):

```
LITELLM_LOCAL_MODEL_COST_MAP=True ../external_benchmarks/tau-bench/.venv/Scripts/python.exe -I -X utf8 scripts/null_agent/external/tau_bench.py --repo ../external_benchmarks/tau-bench/repo --out-csv results/null_agent/external_raw/tau_bench_tasks.csv
```

Result:

| split | tasks | reference leaves the database unchanged | of these, with required outputs | null passes | refusal passes | positive control |
|---|---|---|---|---|---|---|
| airline test | 50 | 20 | 1 (task 44) | 19 (38.0%, 25.9–51.8) | 19 | 50/50 |
| retail test | 115 | 11 | 4 (24, 62, 67, 68) | 7 (6.1%, 3.0–12.0) | 7 | 115/115 |
| retail train | 500 | 5 | 0 | 5 (1.0%, 0.4–2.3) | 5 | 500/500 |
| retail dev | 20 | 1 | 0 | 1 (5.0%, 0.9–23.6) | 1 | 20/20 |

Null-pass task indices: airline 12, 13, 15, 17, 18, 21, 24, 29, 35, 36, 37, 38, 39, 40, 41, 42, 47, 48, 49 (7 with no reference action, 12 with read-only reference actions); retail test 10, 12, 25, 50, 57, 65, 106; retail train 161, 214, 229, 288, 349; retail dev 17. No task failed the positive control.

Where the retail passes come from: 1 task has no reference action (test 57), 4 have only read actions (test 10, 25, 50, 65), and 7 contain a write action that the environment rejects when the reference is replayed, so the reference end state equals the initial state: test 12 (refund to PayPal rejected, then hand-over; the instruction anticipates the refusal) and test 106 and train 161, 214, 229, 288, 349 (exchange or modification rejected for insufficient gift-card balance; each has this single write as its only reference action). Whether these six rejections are intended by the task authors was not reviewed. Cross-check: classifying tools by name (read-only versus write) and counting tasks with no write action and no required output gives 19 airline test, 5 retail test (10, 25, 50, 57, 65), 0 retail train and 1 retail dev; adding the 2 + 5 tasks with rejected writes reproduces the counts from the reward code. Across all retail splits 38 tasks contain at least one rejected reference write; in 29 of them other writes still change the database.

Why the refusal floor equals the null floor: in the shipped runner (`agents/tool_calling_agent.py`) the reward is taken from the step that ends the episode; an episode that reaches the step limit without ending keeps reward 0. The empty-trajectory reward is therefore realised only when the episode ends with the database untouched, which a hand-over at step 0 does deterministically (or the user simulator ending the conversation, which depends on the simulator model and was not run).

Deviations from the survey and comparisons: the survey gave no count for the original files and used tau2's 23/50 as indicative. The original airline test split gives 19/50 (38.0%); the tau2 airline set was rewritten and reordered, so task indices do not align and 23 vs 19 is a comparison of counts only. On retail, the six tau2 null passes (10, 12, 25, 50, 57, 65) are null passes in the original test split under the same indices, and the original adds task 106. The survey's HAL reference figure (28.00% on TAU-bench Airline for a cheap model) is 10 points below the 38.0% that an agent doing nothing obtains on the 50 original airline test tasks, if HAL scores these task files with this reward code (not verified here). Setup deviation: `setup.py` reads `README.md` with the platform default encoding, which fails on Windows; the install was run with `PYTHONUTF8=1`, and the scanner with `-X utf8` because the data loader opens the JSON files the same way. The legacy files `envs/airline/tasks.py` and `envs/retail/tasks.py` are not referenced by the environment and were not scored.

## OSWorld-Verified

What was run. A sparse checkout of `evaluation_examples/` and `desktop_env/` at the current head (`044bc339`, 2026-10-24) and, for the comparison with the release, a second checkout of `evaluation_examples/` at `00804f81` (committed 2025-07-29 06:48 UTC). The last change to `evaluation_examples/` before that commit is dated 2025-07-24 and the next 2025-07-31, so this checkout holds the task files as of the OSWorld-Verified release (2025-07-28). The script reads the index files and counts tasks whose evaluator `func` is `"infeasible"`. Nothing was executed from the download.

Command:

```
python -I scripts/null_agent/external/osworld.py --checkout HEAD_044bc33=../external_benchmarks/osworld/repo/evaluation_examples --checkout release_00804f8=../external_benchmarks/osworld/repo_2025-07-28/evaluation_examples
```

Code path that grants success to a `FAIL` action on infeasible tasks (`desktop_env/desktop_env.py`, `DesktopEnv.evaluate`, lines 487–497 at `044bc339`):

```python
        if self.evaluator['func'] == "infeasible":
            if len(self.action_history) > 0:
                last_action = self.action_history[-1]
                if last_action == "FAIL" or (type(last_action) == dict and last_action.get('action_type') == 'FAIL'):
                    return 1
            return 0
        else:
            if len(self.action_history) > 0:
                last_action = self.action_history[-1]
                if last_action == "FAIL" or (type(last_action) == dict and last_action.get('action_type') == 'FAIL'):
                    return 0
```

`DesktopEnv.step` appends every action, including `FAIL`, to `action_history` and ends the episode on `FAIL`. An agent that emits `FAIL` at step 0 therefore scores 1 on every infeasible task and 0 on every other task: the refusal floor equals the infeasible share by construction. At `00804f81` the same branch exists (lines 438–445) but accepts only the string form `"FAIL"`.

Result:

| checkout | test_all (369) | test_nogdrive (361) | by domain |
|---|---|---|---|
| current `044bc339` | 26 (7.0%, 4.9–10.1) | 26 (7.2%, 5.0–10.3) | gimp 9, os 5, vs_code 4, chrome 3, vlc 2, libreoffice_calc 1, libreoffice_writer 1, multi_apps 1 |
| release `00804f81` | 30 (8.1%, 5.8–11.4) | 30 (8.3%, 5.9–11.6) | gimp 10, os 5, vs_code 5, chrome 3, vlc 3, thunderbird 1, libreoffice_calc 1, libreoffice_writer 1, multi_apps 1 |

The null run (`DONE` at step 0, scoring every task whose checker is satisfied by the initial state) needs the OSWorld virtual machine and was not run.

Deviations from the survey: the survey's 30/369 matches the task files as released. At the current head the count is 26/369: five tasks were changed from `infeasible` to a real checker (chrome `93eabf48` to `match_in_list`, gimp `dbbf4b99` to `check_include_exclude`, thunderbird `a1af9f1c` to `check_thunderbird_smtp_only`, vlc `5ac2891a` to `check_play_and_exit`, vs_code `7aeae0e2` to `check_include_exclude`) and one task was changed to `infeasible` (chrome `480bcfea`, previously `check_enabled_experiments`). The current `test_infeasible.json` lists 25 tasks and omits chrome `480bcfea`, which is infeasible in `test_all.json`. A leaderboard number therefore carries a refusal floor of 8.1% or 7.0% depending on the task-file version it was scored on. At the current head none of the infeasible tasks has a `postconfig`, so the branch above is reached without a setup step.

## WebArena-Verified

What was run. The repository the survey cites was cloned (`6473f72d`, 2026-02-07, tag v1.2.3) and installed non-editable into `../external_benchmarks/webarena-verified/.venv`; its offline evaluator `webarena-verified eval-tasks` scores a folder of `<task_id>/agent_response.json` + `<task_id>/network.har` without contacting any site. A config with placeholder environment URLs (standard WebArena ports on localhost) was supplied, because the evaluator renders and de-renders URL templates; nothing listens on those ports and nothing was contacted. Variants, each over all 812 tasks:
- `null_emptytrace`: empty `agent_response.json`, HAR with zero entries;
- `null`: empty `agent_response.json`, HAR holding only the start-page load (one `GET` per rendered start URL, status 200, `text/html`), which is what a harness records for an agent that ends at once;
- 15 fixed refusal agents: `{"task_type": <retrieve|mutate|navigate>, "status": <one of the five documented error statuses>, "retrieved_data": null}` with the start-page trace;
- `refusal_oracle`: per task the expected task type and, on tasks that expect an error status, that status (otherwise `NOT_FOUND_ERROR`), start-page trace: the upper bound for any agent that only refuses;
- supplementary, the analogue of OSWorld's `DONE` at step 0: `{"task_type": <type>, "status": "SUCCESS", "retrieved_data": null}` with the start-page trace (`claimdone_<type>`).

Commands (from `../external_benchmarks/webarena-verified`, with that folder's venv; `<project>` is the project root):

```
.venv/Scripts/python.exe -I <project>/scripts/null_agent/external/webarena_verified.py count --dataset repo/assets/dataset
.venv/Scripts/python.exe -I <project>/scripts/null_agent/external/webarena_verified.py write --out-root work --dataset repo/assets/dataset
PYTHONUTF8=1 .venv/Scripts/webarena-verified.exe eval-tasks --config work/config.json --output-dir work/<variant>
.venv/Scripts/python.exe -I <project>/scripts/null_agent/external/webarena_verified.py summarize --out-root work --out-csv <project>/results/null_agent/external_raw/webarena_verified_variants.csv
```

Task definitions: 40 of 812 tasks (4.9%) expect a non-`SUCCESS` status (28 `NOT_FOUND_ERROR`, 11 `ACTION_NOT_ALLOWED_ERROR`, 1 `PERMISSION_DENIED_ERROR`); 8 of them also require a network event (visiting the order-history page or the forum list), so 32 (3.9%, 2.8–5.5) can be passed by the status alone. In the original task file (`test.raw.json`, shipped in the same repository) 36 tasks (4.4%, 3.2–6.1) have the reference answer `"N/A"`, all `string_match` tasks; all 36 expect a non-`SUCCESS` status in Verified, and Verified adds 4 more (8, 319, 805, 807).

Result (evaluator output):

| variant | passes | share (Wilson 95%) | passed task ids |
|---|---|---|---|
| null, zero-entry trace | 0 (812 evaluation errors: "HAR file contains no entries") | 0.0% | none |
| null, start-page trace | 0 | 0.0% (0.0–0.5) | none |
| refusal retrieve + `NOT_FOUND_ERROR` (best fixed refusal) | 24 | 3.0% (2.0–4.4) | 8, 22, 24, 101, 115, 166, 168, 183, 191, 201, 218, 219, 225, 234, 235, 247, 253, 313, 368, 376, 382, 723, 726, 789 |
| refusal mutate + `ACTION_NOT_ALLOWED_ERROR` | 4 | 0.5% (0.2–1.3) | 491, 790, 805, 807 |
| refusal retrieve + `ACTION_NOT_ALLOWED_ERROR` | 2 | 0.2% (0.1–0.9) | 792, 793 |
| refusal retrieve + `PERMISSION_DENIED_ERROR` | 1 | 0.1% (0.0–0.7) | 783 |
| the other 11 fixed refusals (any type with `DATA_VALIDATION_ERROR` or `UNKNOWN_ERROR`; navigate with any error; mutate with `NOT_FOUND_ERROR` or `PERMISSION_DENIED_ERROR`) | 0 | 0.0% | none |
| refusal oracle (right type and status per task) | 31 | 3.8% (2.7–5.4) | the 24 + 4 + 2 + 1 above |
| supplementary: claim done, navigate + `SUCCESS` | 10 | 1.2% (0.7–2.3) | 356, 757, 758, 761, 762, 763, 764, 765, 766, 767 |
| supplementary: claim done, retrieve or mutate + `SUCCESS` | 0 | 0.0% | none |

The evaluator's own `eval_results.json` totals equal the per-task counts above for every variant. Further observations:
- Tasks 699, 700 and 811 end in an evaluator error in every variant with a start-page trace: the `NetworkEventEvaluator` rejects the task's own expected POST data, which contains a single-item list (`website_ids: [1]`, `customer_group_ids: [1]`, `assignee_ids: [2330]`) that the value normaliser reads as a list of alternatives ("Alternatives require 2+ items"). Whether a real trajectory reaches the same error was not tested.
- Task 319 expects `NOT_FOUND_ERROR`, but its expected response omits the `retrieved_data` key; the evaluator then reports "Missing keys in actual object: ['retrieved_data']" for every response tried (with `retrieved_data` null, absent, `[]` and `[0]`), so the measured oracle refusal reaches 31, not the 32 counted from the task file, and the best fixed refusal 24, not 25.
- The 10 navigate passes are map tasks ("Show on the map the route / directions / walking route ...") whose only network check is a navigation to the map's base URL (`__MAP__`), which the start-page load already satisfies; the requested route itself is not checked by that evaluator entry. This depends on the synthesised start-page trace, which a harness that opens the map at its base URL would also record.

Original WebArena harness (`evaluation_harness/evaluators.py`, `StringEvaluator.__call__`, web-arena-x/webarena `dce04686`): for a `fuzzy_match` reference equal to `"N/A"` the score is `exact_match("N/A", answer)`; only when that fails is the LLM judge `llm_ua_match` called. An agent answering exactly "N/A" therefore scores 1 on the 36 N/A tasks with no LLM call; its result on the other 299 string-match tasks (exact or substring match against "n/a") was not computed, and its result on the 477 tasks scored only by `url_match`/`program_html` checks depends on the live sites and was not measured. An empty answer on an N/A task goes to the LLM judge and was not measured.

Deviations from the survey: the survey's count of 36 unachievable tasks in the original paper version (inferred from the 1/36 pattern of its Table 2) is confirmed by the task file; the secondary-source figure of 161 is not. The survey's statement that Verified scoring is re-computable offline from the final response plus a HAR trace is confirmed, with one qualification: the evaluator rejects a trace with zero entries ("HAR file contains no entries"), so a literally empty trajectory scores 0 as an evaluation error, and the null and refusal agents were scored with a synthetic start-page trace instead. The "status-only" refusal baseline the survey anticipated is small: the best single fixed refusal answer passes 24 of 812 tasks (3.0%).
