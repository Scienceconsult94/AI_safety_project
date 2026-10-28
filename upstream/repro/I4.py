"""I4: short numeric communicate_info strings match by accident under the substring scorer
(`--communicate-scorer substring`), because the check is `info in text.replace(",", "")`.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I4.py
"""

import os
import re

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.data_model.message import AssistantMessage  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

TASKS = {t.id: t for t in registry.get_tasks_loader("airline")("base")}
SUBSTRING = CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)
db = registry.get_env_constructor("airline")().tools.db

# Task 3 (static): the required string is a single digit.
task = TASKS["3"]
dates = {d for flight in db.flights.values() for d in flight.dates}
reservation = db.reservations["JMO1MG"]
print(f"task 3 communicate_info = {task.evaluation_criteria.communicate_info}")
print(f"  flight dates in db.json containing '4': {sum('4' in d for d in dates)} of {len(dates)}")
print(f"  reservation JMO1MG (the one the agent must read): date {reservation.flights[0].date}, "
      f"fare {reservation.flights[0].price}, created_at {reservation.created_at}")

# Task 23 (recorded run): a sentence from the ground-truth run (message 26) that states a different
# quantity, 1,327 = certificates 1,000 + gift cards 327, satisfies the required "327".
task = TASKS["23"]
sentence = ("Your Mastercard would be charged **$1,286** in total, based on the $2,613 trip cost "
            "less $1,327 in certificates and gift cards.")
checks = CommunicateEvaluator.evaluate_communicate_info(
    [AssistantMessage(role="assistant", content=sentence)], task.evaluation_criteria.communicate_info, scoring=SUBSTRING)
print(f"task 23 communicate_info = {task.evaluation_criteria.communicate_info}")
standalone = re.search(r"(?<![\d,.])327(?!\d)", sentence) is not None  # "327" not inside a longer number
print(f"  standalone '327' in the sentence: {standalone}")
print("  substring verdicts on that one sentence:", {c.info: c.met for c in checks})
