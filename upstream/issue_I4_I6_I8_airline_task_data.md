# airline task data: accidental substring matches (tasks 3, 23), a required total that counts cancelled reservations (task 7), a budget clause that forbids the reference path (task 32)

| field | value |
|---|---|
| audit ids | I4, I6, I8 |
| type | task data (I4 also concerns the substring scorer) |
| domain | airline |
| severity | I4 medium, I6 medium, I8 high |
| status | draft, not filed; I6 is already reported as sierra-research/tau2-bench#495 (checked 2026-10-28); I4 and I8 were not found in the tracker |

## Summary

Three defects in `data/tau2/domains/airline/tasks.json` that one edit pass would fix. (I4) The required strings `"4"` (task 3) and `"327"` (task 23) are matched as substrings of the agent's text after commas are removed, so they are found inside dates, fares and larger amounts. (I6) Task 7 requires the total `"1628"`, the amount paid for all four upcoming reservations, including the two that the same conversation cancels; the scenario asks for the user's other upcoming flights, whose total after the cancellations is 708. (I8) Task 32's scenario says "You are willing to pay up to $100 for the change", while the only path to the target hash charges $396 and then refunds $510 to the same card.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `data/tau2/domains/airline/tasks.json`, tasks 3, 7, 23 and 32.
- `src/tau2/evaluator/evaluator_communicate.py` lines 165-191, substring branch (the test at lines 173-175: `info_str.lower() in message.content.lower().replace(",", "")`). This branch runs with `--communicate-scorer substring`, the original τ-bench scoring; the default at v2.0.0 is the semantic judge, which this report does not cover.
- `src/tau2/domains/airline/tools.py` lines 665 onward (`update_reservation_flights`) and 210 onward (`_payment_for_update`), for task 32's amounts.

## Reproduction

No model call. Run each from the repository root with `uv run --no-sync python <file>`.

### I4: short numeric strings (`repro_I4.py`)

Task 3 is shown statically (its correct answer is 4 suitcases). For task 23, the sentence is copied from a recorded ground-truth-agent run (message 26); it states 1,327 = certificates 1,000 + gift cards 327, a different quantity from the required gift-card total.

```python
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
```

Output:

```text
task 3 communicate_info = ['4']
  flight dates in db.json containing '4': 30 of 30
  reservation JMO1MG (the one the agent must read): date 2024-05-16, fare 149, created_at 2024-05-13T23:20:29
task 23 communicate_info = ['327', '1000', '1286']
  standalone '327' in the sentence: False
  substring verdicts on that one sentence: {'327': True, '1000': False, '1286': True}
```

### I6: task 7's required total (`repro_I6.py`)

The answer sentence is copied from a recorded run (claude-haiku-5-5 agent, trial 0, message 32) whose database matched the target.

```python
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
```

Output:

```text
task 7 instruction: In the middle of the conversation after the third agent message, you also want to check if you have any other upcoming flights and ask for what the total cost of those flights is.
task 7 communicate_info: ['1628']
clock: 2024-05-15T15:00:00; reservations cancelled by the reference: ['59XX6W', 'XEHM4B']
upcoming reservations, amount paid: {'7WPL39': 402, 'XEHM4B': 296, '59XX6W': 624, '3EMQJ6': 306}
sum of all upcoming: 1628
sum of the other upcoming (not cancelled): 708
recorded answer '...total of $708.' -> required '1628' met: False
```

### I8: task 32's budget clause (`repro_I8.py`)

```python
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
```

Output:

```text
task 32 instruction: You are willing to pay up to $100 for the change.
  32_3 update_reservation_flights(cabin=economy, flights=['HAT202', 'HAT232']): payment entries [('credit_card_9659780', 396)]
  32_4 update_reservation_flights(cabin=economy, flights=['HAT041']): payment entries [('credit_card_9659780', -510)]
reference path: db_reward = 1.0
without 32_3 (one change straight to HAT041 economy): db_reward = 0.0
```

## Observed vs expected

- I4, task 3: the required string is one digit, and every one of the 30 flight dates in `db.json` contains it, as do the fare (149) and the booking date of the reservation the agent must read. Expected: the check passes only when the answer (4 suitcases) is given.
- I4, task 23: `"327"` is met by "$1,327" in a sentence about a different quantity. Expected: the gift-card total must be stated.
- I6: besides cancelling XEHM4B and 59XX6W, the scenario asks (after the third agent message) whether the user has "any other upcoming flights" and for "the total cost of those flights". The reservations other than the two being cancelled are 7WPL39 (402) and 3EMQJ6 (306), total 708. The required `"1628"` = 402 + 296 + 624 + 306 adds the two cancelled reservations; the last `nl_assertion` repeats it ("total cost of upcoming flights is $1,628"). Expected: 708, or a scenario that asks for all upcoming reservations before any cancellation.
- I8: the reference changes the cabin first (+396 to `credit_card_9659780`) and the flight second (−510 to the same card), net −114. Removing the first step (one change straight to the nonstop) does not reach the target. Expected: a scenario that lets a faithful user accept the +396 step, or a reference that allows the one-step change.

## Impact on scores

From the audit's runs (claude-haiku-5-5 as agent and as user simulator; 3 trials per task plus one ground-truth-agent run, i.e. the agent that sees the reference actions):

- I4: in all 4 recorded runs of task 23 the first match of `"327"` was an explicit "$327", so no recorded reward depended on the accidental match; 2 of the 4 runs also produced the "$1,327" sentence unprompted, and rescoring those runs with every standalone "327" replaced still meets the check (one of them keeps reward 1.0). Task 3 has no WRITE, so the DB part is 1.0 for any conversation and the one-digit string carries the whole score.
- I6: no assistant message in the 4 recorded runs contains 1628. The trial whose DB matched the target answered 708 and scored 0 on this string alone. With the corrected total (708), the ground-truth agent passed 4 of 4 fresh runs, against 0 of 1 before.
- I8: 4 of 4 recorded runs failed the task (with imperfect agent explanations as well). In a pre-registered probe that replayed the conversation up to the user's request and added one plainly worded agent message (+$396, then −$510 to the same card, net $114 back), the claude-haiku-5-5 simulator refused the first step in 10 of 10 samples (two independent classifications agreed 10/10).

## Suggested fix

- I4: replace one-character and embedded numeric strings with values that cannot occur by accident (for task 3, rely on the assertion or on a phrase), or make the substring scorer match numbers as whole tokens, with thousands separators normalised on both sides. The audit's token-boundary variant is `comm_boundary` in `scripts/v2/scorer_v2.py`.
- I6: change `communicate_info` to `["708"]` and the scenario to "any other upcoming flights (other than the two reservations you are cancelling)"; correct the last `nl_assertion` accordingly. This was tested: the ground-truth agent went from 0/1 to 4/4.
- I8: make the budget a net cap and say when a temporary charge is acceptable. Wording tested with the same probe design (simulator authorisation of step 1, 10 samples per arm): "You are willing to pay up to $100 net for the change. A single step may charge more than that only if a later step in the same conversation refunds it so that the net result is within $100 (or a refund to you). Before you authorize any charge above $100, ask the agent to state the net amount after all steps, and agree only once the agent has stated it." It gave 8 of 10 authorisations when the agent stated the net, and 0 of 10 when the agent asked for the +$396 step without mentioning the refund. A sentence naming the refund card was also tested and is not recommended: it made the simulator reject agents that wrongly said the refund goes to the original payment method, and the task passed 2 of 7 fresh runs. Alternatively, accept the one-step change (basic economy straight to the nonstop in economy) as a second valid end state.

## Evidence (audit repository)

- I4: `results/skeptic_report.md` (3/2g), `results/skeptic_report_rereview.md` (23/2g, counterfactual rescoring), `results/trajectories/23_gt_t0.md` message 26, `audit_log.csv` rows 2g.
- I6: `results/trajectories/7_*.md`, `results/skeptic_report_agent.md` section 4, `block2/task_fixes.md` (task 7), `block2/summary_v2.md` (H4).
- I8: `results/probe_32/` (`protocol.md`, `samples.md`, `result.md`, two classification files), `results/skeptic_report_agent.md` section 3 (arithmetic and uniqueness of the path), `results/v2/probe_32_v2/result.md` (tested wordings), `block2/task_fixes.md` (task 32, post-run observation).
- `upstream/repro/I4.py`, `upstream/repro/I6.py`, `upstream/repro/I8.py`.
