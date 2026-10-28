"""I6: airline task 7 requires the total "1628", which is the amount paid for all four upcoming
reservations, including the two the same conversation cancels; the scenario asks for the user's
other upcoming flights, whose total after the cancellations is 708.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I6.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.data_model.message import AssistantMessage  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("airline")("base")}["7"]
tools = registry.get_env_constructor("airline")().tools
now = tools._get_datetime()
user = tools.db.users["daiki_muller_1116"]
cancelled = {a.arguments["reservation_id"] for a in task.evaluation_criteria.actions if a.name == "cancel_reservation"}

print("task 7 instruction:", [s for s in task.user_scenario.instructions.task_instructions.split("\n") if "upcoming" in s][0])
print("task 7 communicate_info:", task.evaluation_criteria.communicate_info)
print(f"clock: {now}; reservations cancelled by the reference: {sorted(cancelled)}")
upcoming = {}
for rid in user.reservations:
    r = tools.db.reservations[rid]
    if max(f.date for f in r.flights) >= now[:10]:
        upcoming[rid] = sum(p.amount for p in r.payment_history)
print("upcoming reservations, amount paid:", upcoming)
print("sum of all upcoming:", sum(upcoming.values()))
print("sum of the other upcoming (not cancelled):", sum(v for k, v in upcoming.items() if k not in cancelled))

# A sentence from message 32 of the recorded trial whose DB matched the target (7_haiku_t0); the run scored 0.
answer = ("Both reservations are cancelled, and your upcoming reservations are 7WPL39 ($402) and "
          "3EMQJ6 ($306), for a total of $708.")
check = CommunicateEvaluator.evaluate_communicate_info(
    [AssistantMessage(role="assistant", content=answer)], task.evaluation_criteria.communicate_info,
    scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING))[0]
print(f"recorded answer '...total of $708.' -> required '{check.info}' met: {check.met}")
