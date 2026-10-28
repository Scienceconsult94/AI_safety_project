"""I10: the NL-assertion evaluator parses the judge reply with bare `json.loads(...)` and then
`.get("results")`; a reply in a markdown code fence raises JSONDecodeError and a bare top-level JSON
array raises AttributeError. `extract_json_from_llm_response` also mangles a bare array.

No model call: the judge call (`generate`) is replaced by a stub returning fixed reply texts.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I10.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402
from tau2.utils.llm_utils import extract_json_from_llm_response  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["62"]
assertions = task.evaluation_criteria.nl_assertions
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="###STOP###"),
]
results = [{"expectedOutcome": a, "reasoning": "not stated", "metExpectation": False} for a in assertions]
replies = {
    "JSON object (the format the prompt asks for)": json.dumps({"results": results}),
    "same object inside a ```json code fence": "```json\n" + json.dumps({"results": results}, indent=2) + "\n```",
    "bare top-level JSON array": json.dumps(results),
}

for label, content in replies.items():
    nl_module.generate = lambda content=content, **kwargs: SimpleNamespace(content=content)
    try:
        info = NLAssertionsEvaluator.calculate_reward(task, trajectory)
        outcome = f"reward {info.reward}, {len(info.nl_assertions)} verdicts"
    except Exception as e:  # noqa: BLE001
        outcome = f"{type(e).__name__}: {e}"
    print(f"{label}: {outcome}")

bare = json.dumps(results)
extracted = extract_json_from_llm_response(bare)
try:
    json.loads(extracted)
    status = "valid JSON"
except json.JSONDecodeError as e:
    status = f"invalid JSON ({e.msg})"
print(f"extract_json_from_llm_response(bare array) -> starts {extracted[:2]!r}, ends {extracted[-2:]!r}: {status}")
