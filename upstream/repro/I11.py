"""I11: retail `modify_pending_order_items` stores the last new variant's price and options in every
modified item, so the target hash depends on the order of the (old, new) pairs inside one call; the
stored price difference is not rounded to cents.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I11.py
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


def trajectory(task, calls):
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


def reference_calls(task):
    return [(a.name, dict(a.arguments)) for a in task.evaluation_criteria.actions]


# 1. Task 20: the reference modifies four items of one pending order in one call.
task = TASKS["20"]
calls = reference_calls(task)
k = next(i for i, (name, _) in enumerate(calls) if name == "modify_pending_order_items")
env, messages = trajectory(task, calls)
args = calls[k][1]
order = env.tools.db.orders[args["order_id"]]
print(f"task 20, reference call {task.evaluation_criteria.actions[k].action_id}: {len(args['item_ids'])} (old, new) pairs")
for new_id in args["new_item_ids"]:
    item = next(it for it in order.items if it.item_id == new_id)
    variant = env.tools.db.products[item.product_id].variants[new_id]
    print(f"  item {new_id} ({env.tools.db.products[item.product_id].name}): stored price {item.price}, "
          f"variant price {variant.price}; stored options == variant options: {dict(item.options) == dict(variant.options)}")
print(f"  payment_history[-1]: {order.payment_history[-1].transaction_type} {order.payment_history[-1].amount!r}")
print(f"task 20, reference trajectory: db_reward = {db_reward(task, messages)}")

# 2. The same four pairs listed in reverse order inside the one call: same intended swaps, same payment.
pairs = list(zip(args["item_ids"], args["new_item_ids"]))[::-1]
reordered = list(calls)
reordered[k] = (calls[k][0], {**args, "item_ids": [a for a, _ in pairs], "new_item_ids": [b for _, b in pairs]})
_, messages_reordered = trajectory(task, reordered)
print(f"task 20, same pairs in reverse order inside the call: db_reward = {db_reward(task, messages_reordered)}")

# 3. Task 15: a single-item modification; the stored refund is not rounded to cents.
task = TASKS["15"]
env, _ = trajectory(task, reference_calls(task))
order = env.tools.db.orders["#W5199551"]
print(f"task 15, payment_history[-1]: {order.payment_history[-1].transaction_type} {order.payment_history[-1].amount!r}")
