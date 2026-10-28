"""I9: the NL-assertion judge sees the conversation as `role: content` lines, so a tool call is
rendered as `assistant: None` and the judge cannot see which tool was called with which arguments.

No model call: the judge call (`generate`) is replaced by a stub that records the prompt.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I9.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, ToolCall, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("airline")("base")}["9"]
assertion = task.evaluation_criteria.nl_assertions[2]
reference = task.evaluation_criteria.actions[0]  # search_direct_flight(JFK, MCO, 2024-05-22)

env = registry.get_env_constructor("airline")()
call = ToolCall(id="call_0", name=reference.name, arguments=dict(reference.arguments), requestor="assistant")
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="Are there direct flights from JFK to MCO on May 22?"),
    AssistantMessage(role="assistant", content=None, tool_calls=[call]),
    env.get_response(call),
]

prompts = []


def fake_generate(**kwargs):
    prompts.append(kwargs["messages"][-1].content)
    return SimpleNamespace(content=json.dumps({"results": []}))


nl_module.generate = fake_generate
NLAssertionsEvaluator.evaluate_nl_assertions(trajectory, [assertion])
conversation = prompts[0].split("expectedOutcomes:")[0]
print("assertion:", assertion)
print("tool call made:", f"{call.name}({json.dumps(call.arguments)})")
print("conversation as sent to the judge:")
for line in conversation.strip().splitlines():
    print("   ", line.strip())
print("tool name in judge prompt:", call.name in prompts[0], "| arguments in judge prompt:", "2024-05-22" in prompts[0])
