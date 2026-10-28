"""I8: airline task 32's reference charges +396 and then refunds -510 to the same card, while the
scenario tells the user "You are willing to pay up to $100 for the change".

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I8.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

from tau2.data_model.message import AssistantMessage, ToolCall  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

ENV = registry.get_env_constructor("airline")
task = {t.id: t for t in registry.get_tasks_loader("airline")("base")}["32"]


def trajectory(calls):
    env = ENV()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[])
    messages = []
    for i, (name, args) in enumerate(calls):
        call = ToolCall(id=f"call_{i}", name=name, arguments=args, requestor="assistant")
        messages.append(AssistantMessage(role="assistant", content=None, tool_calls=[call]))
        messages.append(env.get_response(call))
    return env, messages


def db_reward(messages):
    info = EnvironmentEvaluator.calculate_reward(environment_constructor=ENV, task=task, full_trajectory=messages)
    return info.db_check.db_reward


print("task 32 instruction:", [s for s in task.user_scenario.instructions.task_instructions.split("\n") if "$100" in s][0])
reference = [(a.action_id, a.name, dict(a.arguments)) for a in task.evaluation_criteria.actions]
env = ENV()
for action_id, name, args in reference:
    before = len(env.tools.db.reservations["OWZ4XL"].payment_history)
    env.make_tool_call(tool_name=name, requestor="assistant", **args)
    new = env.tools.db.reservations["OWZ4XL"].payment_history[before:]
    if new:
        print(f"  {action_id} {name}(cabin={args['cabin']}, flights={[f['flight_number'] for f in args['flights']]}): "
              f"payment entries {[(p.payment_id, p.amount) for p in new]}")
_, messages = trajectory([(n, a) for _, n, a in reference])
print(f"reference path: db_reward = {db_reward(messages)}")
one_step = [(n, a) for i, n, a in reference if i != "32_3"]
_, messages = trajectory(one_step)
print(f"without 32_3 (one change straight to HAT041 economy): db_reward = {db_reward(messages)}")
