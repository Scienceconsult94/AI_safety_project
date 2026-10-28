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
