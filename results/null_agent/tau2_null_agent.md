# Null agent on tau2-bench: what the stock scorer awards to an agent that does nothing

tau2-bench commit `989d3285ae669e49503324bdb9981bf14fccedeb`, scan date 2026-10-27. Trajectory = the task's initial message history only (no agent turn, no tool call). Deterministic components (DB hash, env_assertions, ACTION, COMMUNICATE) are the stock evaluators; NL_ASSERTION needs an LLM judge and is not called: a task whose deterministic part passes and whose reward then depends on the judge is counted as judge-dependent. Wilson 95% intervals.

| task set | tasks | reward basis | null passes for certain | 95% CI | judge-dependent | reference raises on replay or fails its own assertions | errors |
|---|---|---|---|---|---|---|---|
| airline base | 50 | DB|COMMUNICATE | 23 (46.0%) | 33.0–59.6% | 0 | 0 | 0 |
| retail base | 114 | DB, DB|NL_ASSERTION | 6 (5.3%) | 2.4–11.0% | 5 | 15 | 0 |
| telecom base | 114 | ENV_ASSERTION, ENV_ASSERTION|ACTION | 0 (0.0%) | 0.0–3.3% | 0 | 0 | 0 |
| telecom full | 2285 | ENV_ASSERTION, ENV_ASSERTION|ACTION | 0 (0.0%) | 0.0–0.2% | 0 | 0 | 0 |
| banking_knowledge | 97 | ACTION, DB, DB|NL_ASSERTION | n/a | n/a | n/a | n/a | 97 (environment not constructible in the pinned venv: ModuleNotFoundError: No module named 'rank_bm25') |
| intake base | 200 | DB | 0 (0.0%) | 0.0–1.9% | 0 | 0 | 0 |

Reading: a task the null agent passes for certain cannot distinguish an agent that solved it from one that did nothing; the share is the floor that any reported pass rate on that set must be read against. Judge-dependent tasks pass or fail with the judge's reading of the empty transcript.

Retail cross-reference: of the 5 judge-dependent tasks, the live judge probe (results/retail/noop_judge_probe.csv) passed the empty transcript in 0 (none).

airline base, tasks the null agent passes for certain: 0, 1, 2, 4, 5, 6, 9, 10, 13, 26, 27, 28, 31, 34, 36, 38, 41, 43, 45, 46, 47, 48, 49

retail base, tasks the null agent passes for certain: 10, 12, 25, 50, 57, 65

Reference actions that raise on replay (intended negative steps included; the domain audits decide which) or reference end states failing the task's own env_assertions (15 tasks; first 60): retail/2 (replay errors 1, failing assertions 0), retail/3 (replay errors 1, failing assertions 0), retail/4 (replay errors 1, failing assertions 0), retail/35 (replay errors 1, failing assertions 0), retail/37 (replay errors 1, failing assertions 0), retail/38 (replay errors 1, failing assertions 0), retail/39 (replay errors 1, failing assertions 0), retail/46 (replay errors 2, failing assertions 0), retail/47 (replay errors 2, failing assertions 0), retail/54 (replay errors 1, failing assertions 0), retail/55 (replay errors 1, failing assertions 0), retail/64 (replay errors 1, failing assertions 0), retail/67 (replay errors 2, failing assertions 0), retail/68 (replay errors 1, failing assertions 0), retail/105 (replay errors 1, failing assertions 0)

Rows with evaluation errors (97; first 20): banking_knowledge/task_001: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_002: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_003: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_004: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_005: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_006: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_007: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_008: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_010: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_012: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_014: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_015: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_016: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_017: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_018: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_019: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_020: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_021: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_022: ModuleNotFoundError: No module named 'rank_bm25'; banking_knowledge/task_023: ModuleNotFoundError: No module named 'rank_bm25'
