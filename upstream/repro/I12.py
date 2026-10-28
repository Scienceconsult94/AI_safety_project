"""I12: retail `modify_pending_order_address` accepts an order whose items were already modified
(status "pending (item modified)"), although policy.md says no further modification is possible;
the forbidden order of writes reaches the same target hash as the reference.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I12.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

from tau2.data_model.message import AssistantMessage, ToolCall  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

DOMAIN = "retail"
ENV = registry.get_env_constructor(DOMAIN)
TASKS = {t.id: t for t in registry.get_tasks_loader(DOMAIN)("base")}


def trajectory(calls):
    """Execute (name, arguments) pairs on a fresh environment and record them as an agent trajectory."""
    env = ENV()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[])
    messages = []
    for i, (name, args) in enumerate(calls):
        call = ToolCall(id=f"call_{i}", name=name, arguments=args, requestor="assistant")
        messages.append(AssistantMessage(role="assistant", content=None, tool_calls=[call]))
        messages.append(env.get_response(call))
    return env, messages


def db_reward(task, messages):
    info = EnvironmentEvaluator.calculate_reward(environment_constructor=ENV, task=task, full_trajectory=messages)
    return info.db_check.db_reward


task = TASKS["41"]
reference = [(a.action_id, a.name, dict(a.arguments)) for a in task.evaluation_criteria.actions]
ids = [r[0] for r in reference]
order_id = "#W4082615"

# Reference order: address of #W4082615 (41_5) before its items (41_9).
_, messages = trajectory([(n, a) for _, n, a in reference])
print(f"task 41, reference order {ids}: db_reward = {db_reward(task, messages)}")

# Same calls, address of #W4082615 moved after its item modification.
moved = [r for r in reference if r[0] != "41_5"] + [r for r in reference if r[0] == "41_5"]
env, messages = trajectory([(n, a) for _, n, a in moved[:-1]])
status = env.tools.db.orders[order_id].status
late_call = ToolCall(id="call_late", name=moved[-1][1], arguments=moved[-1][2], requestor="assistant")
late = env.get_response(late_call)
messages += [AssistantMessage(role="assistant", content=None, tool_calls=[late_call]), late]
print(f"task 41, address moved after the item change {[r[0] for r in moved]}: "
      f"order status before the address call = {status!r}; "
      f"address call error = {late.error}; db_reward = {db_reward(task, messages)}")

# The other two follow-up writes on the same order after the item change.
user = env.tools.db.users[env.tools.db.orders[order_id].user_id]
original = env.tools.db.orders[order_id].payment_history[0].payment_method_id
other = next(pid for pid in user.payment_methods if pid != original)
for name, args in [("modify_pending_order_payment", {"order_id": order_id, "payment_method_id": other}),
                   ("cancel_pending_order", {"order_id": order_id, "reason": "no longer needed"})]:
    response = env.get_response(ToolCall(id=name, name=name, arguments=args, requestor="assistant"))
    print(f"after the item change, {name}: {response.content if response.error else 'accepted'}")
