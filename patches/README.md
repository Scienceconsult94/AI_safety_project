# Local patches to the pinned tau2-bench checkout (recorded deviations)

| patch | what it changes | why | applied |
|---|---|---|---|
| `nl_judge_haiku.patch` | `src/tau2/config.py`: `DEFAULT_LLM_NL_ASSERTIONS` gpt-5.4-mini → `anthropic/claude-haiku-5-5`; judge args `{"reasoning_effort": "low"}` → `{"temperature": 0.0}` | the audit runs Anthropic models only; the diagnostic NL-assertion judge has no CLI override and would otherwise call OpenAI | **not applied, not needed for runs**: at v2.0.0 `tau2 run` / `run-pass3` / `evaluate-trajs` score with `EvaluationType.ALL` (`src/tau2/runner/batch.py:367`, `src/tau2/runner/simulation.py:23`), which calls the NL judge only for tasks whose `reward_basis` contains `NL_ASSERTION` and that carry assertions: no airline task, 40 of the 114 retail tasks (112 have `NL_ASSERTION` in their basis). The retail runs replaced that judge in-process with `scripts/retail/judge_overlay.py` (`anthropic/claude-haiku-5-5`, args `{}`), not with this patch. Kept only for an optional diagnostic NL pass over saved trajectories (`EvaluationType.ALL_WITH_NL_ASSERTIONS`), outside the plan. |

The NL-assertion judge is diagnostic only: `nl_assertions` never gate reward for airline tasks (`docs/evaluation.md`). bench_commit stays 989d3285ae669e49503324bdb9981bf14fccedeb; every result produced with a patch applied carries `patched=nl_judge_haiku` in its note.
