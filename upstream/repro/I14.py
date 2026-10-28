"""I14: the NL reward is `all(met)` over whatever results the judge returns. An assertion that the
judge leaves out is never checked, so it counts as met; a reply with an empty `results` list gives
reward 1.0.

No model call: the judge call (`generate`) is replaced by a stub returning fixed reply texts.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I14.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["62"]
assertions = task.evaluation_criteria.nl_assertions
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="###STOP###"),
]
print(f"task 62 has {len(assertions)} nl_assertions: {assertions}")

replies = {
    "verdict for both assertions, second unmet": [
        {"expectedOutcome": assertions[0], "reasoning": "-", "metExpectation": True},
        {"expectedOutcome": assertions[1], "reasoning": "-", "metExpectation": False},
    ],
    "verdict for the first assertion only (second omitted)": [
        {"expectedOutcome": assertions[0], "reasoning": "-", "metExpectation": True},
    ],
    "empty results list": [],
}
for label, results in replies.items():
    content = json.dumps({"results": results})
    nl_module.generate = lambda content=content, **kwargs: SimpleNamespace(content=content)
    info = NLAssertionsEvaluator.calculate_reward(task, trajectory)
    print(f"{label}: reward {info.reward}, verdicts recorded {len(info.nl_assertions)} of {len(assertions)}")
