# retail: an address change after an item change is accepted, although the policy forbids any further modification; the forbidden order reaches the target hash

| field | value |
|---|---|
| audit id | I12 |
| type | bug (policy and tool mismatch; scoring validity) |
| domain | retail |
| severity | medium |
| status | draft, not filed |

## Summary

`policy.md` says that modifying the items of a pending order changes its status and that "The agent will not be able to modify or cancel the order anymore"; `modify_pending_order_items` sets the status to `pending (item modified)`. `modify_pending_order_address` and `modify_pending_order_payment`, however, test the status with `"pending" in order.status`, so they accept that status. A trajectory that changes the items first and the address second therefore runs without error and reaches the same target hash as the compliant order, in every task whose reference changes an order's address and then its items. A payment change after an item change is rejected today, but only by an unrelated check (the order no longer has exactly one payment entry).

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/domains/retail/tools.py`: `_is_pending_order` (lines 164-170, a substring test whose docstring says it "is not a strict check"); `modify_pending_order_address` (line 485 uses it); `modify_pending_order_payment` (line 613 uses it; lines 620-624 are the one-payment check); `modify_pending_order_items` sets `pending (item modified)` (line 585) and itself requires `status == "pending"` (line 527), as does `cancel_pending_order` (line 209).
- `data/tau2/domains/retail/policy.md` line 96 ("An order can only be modified if its status is 'pending'") and line 110 ("... will change the order status to 'pending (items modifed)'. The agent will not be able to modify or cancel the order anymore."). The policy text also names the status differently from the tool (`items modifed` vs `item modified`).

## Reproduction

No model call. The reference actions of retail task 41 are replayed as an agent trajectory and scored with `EnvironmentEvaluator`, once in the reference order and once with the address change of order `#W4082615` moved after its item change. Run from the repository root with `uv run --no-sync python repro_I12.py`.

```python
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
```

Output:

```text
task 41, reference order ['41_0', '41_1', '41_2', '41_3', '41_4', '41_5', '41_6', '41_7', '41_8', '41_9']: db_reward = 1.0
task 41, address moved after the item change ['41_0', '41_1', '41_2', '41_3', '41_4', '41_6', '41_7', '41_8', '41_9', '41_5']: order status before the address call = 'pending (item modified)'; address call error = False; db_reward = 1.0
after the item change, modify_pending_order_payment: Error: There should be exactly one payment for a pending order
after the item change, cancel_pending_order: Error: Non-pending order cannot be cancelled
```

## Observed vs expected

- Observed: the address change on an order in status `pending (item modified)` succeeds, and the trajectory scores 1.0. The payment change fails with "There should be exactly one payment for a pending order", which is not the policy's reason.
- Expected: both modifications rejected with the same reason as the item and cancel tools ("Non-pending order cannot be modified"), so that the policy-violating order of writes does not reach the target.

## Impact on scores

- 14 retail tasks have a reference that changes an order's address and later its items (41, 42, 71, 72, 78, 96, 97, 101, 102, 103, 104, 109, 111, 112). Moving the address change after the item change reaches the target hash without a tool error in 14 of 14. The DB check cannot tell the forbidden order from the compliant one, and several of these scenarios are written to test exactly this rule (for example 41, 72, 97, 104).
- With the attached patch the moved address change is rejected in 14 of 14 tasks, and no retail target hash changes (no reference modifies an order after its items; checked in `tasks.json`, the English retail task file and the five regional retail files).

## Suggested fix

Make `_is_pending_order` an exact test (`order.status == "pending"`), which both tools use, and update its docstring. A patch with tests is in `pr_I12.md` / `patches/I12.patch`. Optionally, correct the status name in `policy.md` line 110; that changes the agent's prompt, so it is left out of the patch.

## Evidence (audit repository)

- `results/retail/probe_2d.csv` (rows with `field=write_order`), `scripts/retail/probe_2d.py`.
- `retail/audit_log.csv` rows 2e (14 tasks) and 2m; `results/retail/review_batch_12.md` (task 111 reading of policy lines 96 and 110).
- `upstream/repro/I12.py`.
