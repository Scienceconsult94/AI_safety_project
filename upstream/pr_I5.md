# runner: say so when simulations ended in infrastructure errors; give the greeting a zero cost so agent cost is reported

Status: draft, not opened. Patch: `patches/I5.patch` (paths relative to the repository root; base tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Issue text: `issue_I5_default_temperature_and_run_reporting.md`.

This is a partial fix. It does not change the default `llm_args` (`{"temperature": 0.0}`), which current Anthropic models reject: that default affects comparability with earlier runs and is left to the maintainers (options are listed in the issue).

## Description

Two reporting problems that the default-temperature failure exposed:

1. `run_tasks` printed "Successfully completed all simulations!" unconditionally, also when every simulation had ended as an infrastructure error and nothing was evaluated (`src/tau2/runner/batch.py`, local and worker branches).
2. `agent_cost` was `None` for every half-duplex simulation: the greeting built by `Orchestrator.initial_agent_message` from the language pack had no `cost`, unlike `DEFAULT_FIRST_AGENT_MESSAGE` (`cost=0.0`), and `get_cost` returns `None` for a side when any of its messages lacks a cost. Every text run sets a call context, so this greeting is always the one used, and "Avg Cost/Conversation" was "n/a" in every run that evaluated any simulation.

Changes:

- `src/tau2/runner/batch.py`: new `completion_message(simulations)`; both end-of-run prints use it. All simulations failed: a red line saying that no simulation was evaluated. Some failed: a yellow line with the count excluded from the metrics. None failed: the old green line, unchanged.
- `src/tau2/orchestrator/orchestrator.py`: `initial_agent_message` sets `cost=0.0`.
- `tests/test_runner/test_run_reporting.py` (new): the three message cases; the greeting of a built text orchestrator has cost 0.0, and `get_cost` then returns the agent side.

## Testing done

- `git apply --check` against `v2.0.0`: clean.
- On a copy of `v2.0.0` with the patch applied (pytest 9.0.2, CPython 3.12.16):
  - `tests/test_runner/test_run_reporting.py`: 4 passed (on unpatched `v2.0.0` the file fails at import, since `completion_message` does not exist).
  - `tests/test_runner/test_elicitation_integration.py`, `tests/test_orchestrator.py` and the new file: 63 passed, 6 skipped.
  - Together with the other four patches of this audit: 160 passed, 6 skipped (see `pr_I11.md` for the file list).
- Reproduction script of the issue (`repro/I5.py`) on the patched copy (retry messages omitted):

```text
default llm_args_agent = {'temperature': 0.0}, llm_args_user = {'temperature': 0.0}
litellm.drop_params = True; 'temperature' is a supported Anthropic param in litellm: True
5 simulations, termination reasons: ['infrastructure_error']
compute_metrics: avg_reward = 0.0, infra_error_count = 5, total_simulations = 0
greeting 'Hi! How can I help you today?': cost = 0.0
get_cost([greeting, user turn costing 0.002, agent turn costing 0.001]) = (0.001, 0.002)
```

- `completion_message` on 5 infrastructure errors, on 4 completed plus 1 error, and on 5 completed (patched copy):

```text
'\n[bold red]All 5 simulations ended with an infrastructure error; no simulation was evaluated.[/bold red]\nEach simulation records its error in `info`. To review the simulations, run: [bold blue]tau2 view[/bold blue]'
'\n[bold yellow]Completed; 1 of 5 simulations ended with an infrastructure error and are excluded from the metrics.[/bold yellow]\nTo review the simulations, run: [bold blue]tau2 view[/bold blue]'
'\n[bold green]Successfully completed all simulations![/bold green]\nTo review the simulations, run: [bold blue]tau2 view[/bold blue]'
```

No live run was made with the patch.

## Risk

- Console output only, for the message; scripts that grep for "Successfully completed all simulations!" will no longer find it on runs with infrastructure errors. The exit code is unchanged (still 0); a non-zero exit code when nothing was evaluated would be a further, behaviour-changing step.
- `agent_cost` becomes a number where it was `None`, so "Avg Cost/Conversation" (the mean of `agent_cost`) appears in the metrics and `results.json` carries the agent cost. Model calls that LiteLLM cannot price still count as 0.0, as before (`get_response_cost` logs the error and returns 0.0), so a reported cost can be an undercount.
