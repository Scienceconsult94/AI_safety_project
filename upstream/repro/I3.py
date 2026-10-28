"""I3: the DB hash keeps list order and the ids handed out by the fixed sequence HATHAT/HATHAU/HATHAV,
so the same booking made with passengers, payment methods or bookings in another order fails the DB check.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I3.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

from tau2.data_model.message import AssistantMessage, ToolCall  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

DOMAIN = "airline"
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
        assert not messages[-1].error, messages[-1].content
    return env, messages


def db_reward(task, messages):
    info = EnvironmentEvaluator.calculate_reward(environment_constructor=ENV, task=task, full_trajectory=messages)
    return info.db_check.db_reward


def calls_of(task):
    return [(a.name, dict(a.arguments)) for a in task.evaluation_criteria.actions]


def variant(task, action_id, field):
    """The reference with one list argument of one call reversed."""
    out = []
    for a in task.evaluation_criteria.actions:
        args = dict(a.arguments)
        if a.action_id == action_id:
            args[field] = list(reversed(args[field]))
        out.append((a.name, args))
    return out


task = TASKS["8"]
print(f"task 8 reference: db_reward = {db_reward(task, trajectory(calls_of(task))[1])}")
print(f"task 8, the two passengers of 8_3 in the other order: db_reward = {db_reward(task, trajectory(variant(task, '8_3', 'passengers'))[1])}")

task = TASKS["20"]
print(f"task 20 reference: db_reward = {db_reward(task, trajectory(calls_of(task))[1])}")
print(f"task 20, the two payment methods of 20_0 in the other order (same amounts): "
      f"db_reward = {db_reward(task, trajectory(variant(task, '20_0', 'payment_methods'))[1])}")

task = TASKS["23"]
reference = calls_of(task)
env, messages = trajectory(reference)
ids = {r.passengers[0].first_name: r.reservation_id for r in env.tools.db.reservations.values() if r.reservation_id.startswith("HATHA")}
print(f"task 23 reference (cancel, then book Mohamed, Raj, Liam): ids {ids}; db_reward = {db_reward(task, messages)}")
reordered = [reference[0]] + reference[1:][::-1]
env, messages = trajectory(reordered)
ids = {r.passengers[0].first_name: r.reservation_id for r in env.tools.db.reservations.values() if r.reservation_id.startswith("HATHA")}
print(f"task 23, same three bookings in the order Liam, Raj, Mohamed: ids {ids}; db_reward = {db_reward(task, messages)}")
