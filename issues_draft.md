# Issue candidates (drafts only — nothing is filed without explicit confirmation)

Rules: aggregates and reproducible rules only; no scorer-bypass recipes here (those stay in `private/`). The documented no-op pass ("intended τ-bench scoring", `docs/evaluation.md`) is a known design choice and is NOT an issue candidate; it serves as the positive control for the checklist.

| id | task_id(s) | category | one-line summary | evidence (path / rule) | status |
|---|---|---|---|---|---|
| I1 | ALL | 6 (reporting) | `docs/evaluation.md` says the CLI runner uses `EvaluationType.ALL_WITH_NL_ASSERTIONS` by default; at v2.0.0 the runner default is `EvaluationType.ALL` (`src/tau2/runner/batch.py:367`, `src/tau2/runner/simulation.py:23`), so `nl_assertions` are never evaluated by `tau2 run` and the configured NL judge model is never called | docs/evaluation.md, section "How to inspect action correctness anyway" vs src/tau2/runner/batch.py:367 | draft, low |
| I2 | ALL | 3/5 (harness robustness) | `calculate` (`src/tau2/domains/airline/tools.py:400-402`) whitelists `0123456789+-*/(). ` and then calls `eval`; the whitelist admits `**`, and `--timeout` is checked only between steps (`src/tau2/orchestrator/orchestrator.py:238-249, 759-771`), so a single agent tool call such as a nested power expression can stall a simulation past the timeout | tools.py:400-402; orchestrator.py:759-771 | draft, low; not reproduced at runtime (would require a deliberately pathological call) |
