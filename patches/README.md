# Local patches to the pinned tau2-bench checkout (recorded deviations)

| patch | what it changes | why | applied |
|---|---|---|---|
| `nl_judge_haiku.patch` | `src/tau2/config.py`: `DEFAULT_LLM_NL_ASSERTIONS` gpt-5.4-mini → `anthropic/claude-haiku-5-5`; judge args `{"reasoning_effort": "low"}` → `{"temperature": 0.0}` | the audit runs Anthropic models only; the diagnostic NL-assertion judge has no CLI override and would otherwise call OpenAI | not yet (applied right before the first API run; `git -C tau2-bench apply ../patches/nl_judge_haiku.patch`) |

The NL-assertion judge is diagnostic only: `nl_assertions` never gate reward for airline tasks (`docs/evaluation.md`). bench_commit stays 989d3285ae669e49503324bdb9981bf14fccedeb; every result produced with a patch applied carries `patched=nl_judge_haiku` in its note.
