# Default `llm_args` send `temperature: 0.0`, which current Anthropic models reject; the run then reports success with every simulation excluded, and agent cost is never reported

| field | value |
|---|---|
| audit id | I5 |
| type | bug (harness robustness, reporting) |
| domain | all |
| severity | medium |
| status | draft, not filed |

## Summary

The default `llm_args` for agent and user are `{"temperature": 0.0}`. Current Anthropic models reject a non-default `temperature` with HTTP 400 (observed with `claude-haiku-5-5`: "`temperature` is deprecated for this model."), so a plain `tau2 run --agent-llm anthropic/claude-haiku-5-5 --user-llm anthropic/claude-haiku-5-5` fails every simulation after 4 attempts. The runner then prints "Successfully completed all simulations!" and "Average Reward 0.0000", with the failures visible only as "Infra Errors 5 (excluded from metrics below)", and exits with code 0. Separately, `agent_cost` is `None` for every half-duplex simulation, because the greeting that opens the conversation carries no cost, so "Avg Cost/Conversation" is "n/a" in every run that evaluates any simulation.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/config.py` lines 28-31 (`DEFAULT_LLM_ARGS_AGENT`, `DEFAULT_LLM_ARGS_USER`); `src/tau2/cli.py` lines 90-95 (`--agent-llm-args` default); `src/tau2/data_model/run_config.py` lines 331-335 and 517-521 (config defaults).
- `src/tau2/utils/llm_utils.py` line 72 (`litellm.drop_params = True`, which does not drop a parameter the provider mapping lists as supported).
- `src/tau2/runner/progress.py` lines 19-110 (`run_with_retry`: retries, then an `INFRASTRUCTURE_ERROR` placeholder); `src/tau2/metrics/agent_metrics.py` lines 217-236 (such simulations are excluded from the metrics); `src/tau2/runner/batch.py` lines 1081-1084 and 1169-1172 (the success line is printed unconditionally).
- `src/tau2/orchestrator/orchestrator.py` lines 146-153 (`initial_agent_message` builds the greeting without `cost`, unlike `DEFAULT_FIRST_AGENT_MESSAGE` at lines 48-50, which has `cost=0.0`); `src/tau2/runner/build.py` line 609 and 654 (every text run sets a call context, so this greeting is always used); `src/tau2/utils/llm_utils.py` lines 740-766 (`get_cost` returns `None` for a side when any of its messages has no cost).

## Reproduction

No model call: the provider error is raised by a stub with the error text recorded on 2026-10-27 (below). Run from the tau2-bench root with `PYTHONUTF8=1 uv run --no-sync python <path to repro>/I5.py` (the script is `upstream/repro/I5.py` in the audit repository).

```python
"""I5: default llm_args send temperature 0.0, which current Anthropic models reject (HTTP 400); the run
then reports success with every simulation excluded as an infrastructure error. Separately, the
agent cost of every half-duplex simulation is None because the greeting message carries no cost.

No model call: the provider error is raised by a stub with the text recorded in the failed run.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I5.py
"""

import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

import litellm  # noqa: E402

from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.data_model.simulation import TerminationReason, TextRunConfig  # noqa: E402
from tau2.metrics.agent_metrics import compute_metrics  # noqa: E402
from tau2.registry import registry  # noqa: E402
from tau2.runner.build import build_text_orchestrator  # noqa: E402
from tau2.runner.progress import run_with_retry  # noqa: E402
from tau2.utils.llm_utils import get_cost  # noqa: E402

MODEL = "anthropic/claude-haiku-5-5"
config = TextRunConfig(domain="airline", agent="llm_agent", llm_agent=MODEL, user="user_simulator", llm_user=MODEL)
print(f"default llm_args_agent = {config.llm_args_agent}, llm_args_user = {config.llm_args_user}")
print(f"litellm.drop_params = {litellm.drop_params}; 'temperature' is a supported Anthropic param in litellm: "
      f"{'temperature' in litellm.get_supported_openai_params(model='claude-haiku-5-5', custom_llm_provider='anthropic')}")

# The provider's reply recorded on 2026-10-27 for every request of a default run.
recorded = '{"type":"error","error":{"type":"invalid_request_error","message":"`temperature` is deprecated for this model."}}'


def failing_simulation():
    raise litellm.BadRequestError(message="AnthropicException - " + recorded, model=MODEL, llm_provider="anthropic")


tasks = registry.get_tasks_loader("airline")("base")[:5]
sims = [run_with_retry(failing_simulation, task=t, trial=0, seed=300, max_retries=config.max_retries,
                       retry_delay=0.0, console_display=False) for t in tasks]
print(f"{len(sims)} simulations, termination reasons: {sorted({s.termination_reason.value for s in sims})}")
metrics = compute_metrics(SimpleNamespace(simulations=sims))
print(f"compute_metrics: avg_reward = {metrics.avg_reward}, infra_error_count = {metrics.infra_error_count}, "
      f"total_simulations = {metrics.total_simulations}")
# run_tasks then prints "Successfully completed all simulations!" without looking at these counts
# (src/tau2/runner/batch.py:1169-1172; the worker branch at 1081-1084 does the same).

# Agent cost: the greeting that opens every half-duplex run.
orchestrator = build_text_orchestrator(config, tasks[0], seed=300)
greeting = orchestrator.initial_agent_message
print(f"greeting {greeting.content!r}: cost = {greeting.cost}")
messages = [greeting, UserMessage(role="user", content="hi", cost=0.002),
            AssistantMessage(role="assistant", content="ok", cost=0.001)]
print(f"get_cost([greeting, user turn costing 0.002, agent turn costing 0.001]) = {get_cost(messages)}")
assert all(s.termination_reason == TerminationReason.INFRASTRUCTURE_ERROR for s in sims)
```

Output (the console retry messages, 4 attempts per simulation, are omitted):

```text
default llm_args_agent = {'temperature': 0.0}, llm_args_user = {'temperature': 0.0}
litellm.drop_params = True; 'temperature' is a supported Anthropic param in litellm: True
5 simulations, termination reasons: ['infrastructure_error']
compute_metrics: avg_reward = 0.0, infra_error_count = 5, total_simulations = 0
greeting 'Hi! How can I help you today?': cost = None
get_cost([greeting, user turn costing 0.002, agent turn costing 0.001]) = (None, 0.002)
```

Recorded on 2026-10-27 in a 5-task airline run with the default `llm_args` (`tau2 run`, agent and user `anthropic/claude-haiku-5-5`, `--communicate-scorer substring`): every request returned

```text
litellm.BadRequestError: AnthropicException - {"type":"error","error":{"type":"invalid_request_error","message":"`temperature` is deprecated for this model."},...}
```

then "Task 1 failed after 4 attempts", then "Successfully completed all simulations!", "Total Simulations 5", "Infra Errors 5 (excluded from metrics below)", "Average Reward 0.0000", and exit code 0.

## Observed vs expected

- Observed: the default arguments are sent to a provider that rejects them; the run ends with a success message and a reward of 0.0 computed over zero evaluated simulations. In every completed run of the audit, `agent_cost` is `None` (60 of 60 simulations in the 3-trial airline run, where `user_cost` is filled; in the retail and block-2 runs `user_cost` is 0.0, because the cost lookup failed there and `get_response_cost` returns 0.0 on an error).
- Expected: either defaults that the selected provider accepts, or a clear failure; an end-of-run message that says no simulation was evaluated; an agent cost that sums the model calls.

## Impact on scores

- A default run with a current Anthropic model evaluates nothing, and the console output reads as a completed run with a score of 0.0000. The audit worked around it with `--agent-llm-args '{}' --user-llm-args '{}'` (provider-default sampling), which also means its runs were not at temperature 0.
- Any run where only some simulations hit infrastructure errors is reported as a success with those simulations dropped from the denominator; the count is printed, but the success line does not reflect it.
- Cost reporting: "Avg Cost/Conversation" is "n/a" for every run that evaluates any simulation, whatever the provider, because the greeting has no cost.

## Suggested fix

- Sampling defaults: choose provider-aware defaults (for example, omit `temperature` for models that accept only the default), or fail before the first simulation with a message that names `--agent-llm-args` / `--user-llm-args`. This is a policy decision for the maintainers (it affects comparability with earlier runs at temperature 0), so the attached patch does not change it.
- Reporting: make the end-of-run line depend on the infrastructure-error count (all failed: say that nothing was evaluated; some failed: say how many were excluded). Optionally return a non-zero exit code when nothing was evaluated.
- Cost: give the language-pack greeting `cost=0.0`, as `DEFAULT_FIRST_AGENT_MESSAGE` already has.

The last two points are in `pr_I5.md` / `patches/I5.patch`.

## Evidence (audit repository)

- `results/runs/pilot_attempt1_FAILED.log` (lines 21-68 the 400 errors and "failed after 4 attempts"; line 141 "Successfully completed all simulations!"; lines 145-146 "Total Simulations 5", "Infra Errors 5"; line 180 exit code 0).
- `results/runs/pilot_5_haiku_FAILED_temperature_2026-10-27.results.json` (5 simulations, `termination_reason` `infrastructure_error`, `llm_args` `{"temperature": 0.0}`).
- `results/runs/sample20_pass3_haiku.results.json` (`agent_cost` `None` in 60 of 60 simulations; the first assistant message of each has `cost` `None`); `results/runs/sample20.log` ("Avg Cost/Conversation n/a").
- `checklist.md` (conventions: the `'{}'` workaround), `cost.md`.
- `upstream/repro/I5.py`.
