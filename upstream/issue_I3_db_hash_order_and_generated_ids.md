# DB hash depends on list order and on generated reservation ids, so equally valid solutions fail the DB check

| field | value |
|---|---|
| audit id | I3 |
| type | scoring validity |
| domain | airline (the hash is shared by every domain) |
| severity | medium |
| status | draft, not filed |

## Summary

The DB check compares a SHA-256 of `json.dumps(db.model_dump(), sort_keys=True)` for the predicted and the target database (DB). `sort_keys` orders dictionary keys, but lists keep the order in which tools stored them, and `book_reservation` takes new reservation ids from the fixed sequence `HATHAT`, `HATHAU`, `HATHAV` in call order. Booking the same passengers in another order, paying with the same payment methods listed in another order, or making the same bookings in another order therefore gives a different hash and a DB reward of 0, although `docs/evaluation.md` says that "any sequence of tool calls that produces an equivalent DB end state passes the DB check".

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/utils/utils.py` lines 36-42 (`get_dict_hash`), `src/tau2/utils/pydantic_utils.py` lines 15-21 (`get_pydantic_hash`), `src/tau2/environment/db.py` lines 28-30 (`DB.get_hash`).
- `src/tau2/domains/airline/tools.py` lines 131-144 (`_get_new_reservation_id`), lines 302-303 (`passengers` and `payment_history` stored in call order).
- `src/tau2/evaluator/evaluator_env.py` lines 117-129 (hash comparison).

## Reproduction

No model call. Each case replays the reference actions of an airline task as an agent trajectory and scores it with `EnvironmentEvaluator`; the variant changes only the order of a list. Run from the repository root with `uv run --no-sync python repro_I3.py`.

```python
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
```

Output:

```text
task 8 reference: db_reward = 1.0
task 8, the two passengers of 8_3 in the other order: db_reward = 0.0
task 20 reference: db_reward = 1.0
task 20, the two payment methods of 20_0 in the other order (same amounts): db_reward = 0.0
task 23 reference (cancel, then book Mohamed, Raj, Liam): ids {'Mohamed': 'HATHAT', 'Raj': 'HATHAU', 'Liam': 'HATHAV'}; db_reward = 1.0
task 23, same three bookings in the order Liam, Raj, Mohamed: ids {'Liam': 'HATHAT', 'Raj': 'HATHAU', 'Mohamed': 'HATHAV'}; db_reward = 0.0
```

## Observed vs expected

- Observed: DB reward 0.0 for task 8 with the two passengers in the other order, for task 20 with the two payment methods in the other order (same amounts), and for task 23 with the three bookings made in another order (the generated ids move with the call order).
- Expected: 1.0 wherever the scenario and the policy leave the order open. In task 8 neither the scenario nor the policy orders the passengers; in task 20 the amounts per payment method are fixed and only their order differs; in task 23 the scenario lists the three travellers but does not fix the order of the bookings, and the policy is silent.

## Impact on scores

- Reordering whole WRITE calls of the reference, on the 13 tasks of a 20-task airline sample that have two or more WRITE calls: 24 of 78 reorderings change the hash. 20 of the 24 (all in task 23) reach the same state up to which booking received which generated id. With the canonical form described below, 4 of 78 still differ, and those 4 are real outcome changes (tasks 7 and 32: a refund before an upgrade, a flight change before a cabin change).
- Order inside one call: passengers (task 8) and payment methods (tasks 20 and 23) change the hash.
- Reversing a reservation's `flights` list also changes the hash in 11 of the same 13 tasks. Itinerary order may be meant to matter, so this is listed for completeness only.
- In the audit's 76 recorded conversations (claude-haiku-5-5 agent and ground-truth agent), none of the 20 DB mismatches was order-only, so the property did not decide a recorded score in that sample. It rejects valid solutions that choose another order, and it makes the target depend on incidental call order.
- The same mechanism appears in retail through `modify_pending_order_items`, where the order of the (old, new) pairs inside one call changes the stored items (separate issue, audit id I11).

## Suggested fix

Compare a canonical form of the DB instead of the raw dump, for the DB check only:

- sort order-free lists by content (reservation `passengers`, `payment_history` as a multiset, user `saved_passengers`, user `reservations`);
- replace ids created during the episode (new reservation ids, new certificate ids) with ids derived from the object's content, and remap the references to them;
- round float amounts to cents;
- keep itinerary order (`flights`).

The audit used such a canonical hash as an overlay (`scripts/v2/scorer_v2.py`, `canonical_dump`). On the 76 recorded conversations it changed no reward, and it reduced the order-dependent reorderings from 24/78 to the 4 outcome-changing ones. A canonical form loses the chronology of `payment_history` within a reservation; if that chronology must be scored, it can be compared separately.

## Evidence (audit repository)

- `results/probe_2h.csv` (one row per task: permutations tried, permutations with a different hash).
- `results/skeptic_report.md` sections 2h and 4c (independent re-implementation of the hash and of the airline WRITE tools; variant hashes for tasks 8, 20, 23; the `flights` observation).
- `block2/summary_v2.md` (H2: 24/78 to 4/78; H3: 0 of 20 DB mismatches order-only).
- `scripts/probe_2h.py`, `scripts/v2/scorer_v2.py`, `upstream/repro/I3.py`.
