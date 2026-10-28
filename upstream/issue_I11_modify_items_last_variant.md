# retail: `modify_pending_order_items` stores the last new variant's price and options in every modified item; the stored price difference is not rounded

| field | value |
|---|---|
| audit id | I11 |
| type | bug (environment correctness; scoring validity) |
| domain | retail |
| severity | medium |
| status | draft, not filed |

## Summary

In `modify_pending_order_items`, the loop that rewrites the order items uses the variable `variant` left over from the validation loop, which holds the last new variant. With two or more (old, new) pairs in one call, every modified item is stored with the last variant's price and options. The payment difference is computed correctly, but the stored order is wrong, and the target hash of every task whose reference modifies two or more items in one call depends on the order of the pairs inside that call. Separately, the price difference is stored without rounding (`exchange_delivered_order_items` rounds it), so `payment_history` carries amounts such as `71.96000000000001`.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/domains/retail/tools.py`, `modify_pending_order_items` (lines 500-587): the validation loop at lines 541-556 assigns `variant`; the "Modify the order" loop at lines 577-584 writes `item.price = variant.price` and `item.options = variant.options`; `diff_price` is accumulated at line 556 and stored at lines 566-572 without rounding. Compare `exchange_delivered_order_items`, line 299 (`diff_price = round(diff_price, 2)`).

## Reproduction

No model call. The reference actions of retail tasks 20 and 15 are replayed as an agent trajectory and scored with `EnvironmentEvaluator`. Run from the repository root with `uv run --no-sync python repro_I11.py`.

```python
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
```

Output:

```text
task 20, reference call 20_8: 4 (old, new) pairs
  item 4579334072 (Water Bottle): stored price 261.11, variant price 54.85; stored options == variant options: False
  item 1151293680 (Mechanical Keyboard): stored price 261.11, variant price 272.33; stored options == variant options: False
  item 4107812777 (Running Shoes): stored price 261.11, variant price 155.33; stored options == variant options: False
  item 2882812427 (Makeup Kit): stored price 261.11, variant price 261.11; stored options == variant options: True
  payment_history[-1]: payment 71.96000000000001
task 20, reference trajectory: db_reward = 1.0
task 20, same pairs in reverse order inside the call: db_reward = 0.0
task 15, payment_history[-1]: refund 0.3499999999999943
```

## Observed vs expected

- Observed: in task 20 a water bottle, a keyboard and a pair of shoes are stored at 261.11 with the makeup kit's options. Listing the same four swaps in reverse order inside the one call stores all four items with the water bottle's data, and the DB reward drops to 0.0. The stored payment is `71.96000000000001`; task 15 stores a refund of `0.3499999999999943`.
- Expected: each item stores the price and options of its own new variant; the result does not depend on the order of the pairs; stored amounts are in cents, as in the exchange tool.

## Impact on scores

- Over all 114 retail tasks, the reference modifies two or more items in one call in 5 tasks (20, 21, 36, 37, 100). In their targets, 9 items carry another variant's price and options (task 20: 3 of 4; 21: 1 of 2; 36: 2 of 3; 37: 2 of 3; 100: 1 of 2).
- Reordering the pairs inside that call changes the target hash in 18 of 23 orders for task 20, 1 of 1 for task 21, 4 of 5 for tasks 36 and 37, and 1 of 1 for task 100. An agent that makes the right swaps in another order scores 0.
- The agent reads the stored state back: in one recorded ground-truth-agent run (task 100), the agent noticed that `get_order_details` showed the luggage line with the skateboard's price and options, and transferred the user to a human.
- With the attached patch, the same probe finds 0 items with another variant's data and 0 order-dependent hashes. The patch changes the target hash of 35 of the 114 retail tasks (5 through the variant fix, the rest through rounding). Within one code version the gold and the predicted state are built by the same tool, so a trajectory's pass or fail changes only where the pair order mattered; but recorded `results.json` files re-graded with strict replay would see different tool outputs.

## Suggested fix

Keep the variant looked up for each pair and use it when writing the item, and round `diff_price` to cents after the validation loop, as `exchange_delivered_order_items` does. A patch with tests is in `pr_I11.md` / `patches/I11.patch`; the two changes are separate hunks and can be split.

## Evidence (audit repository)

- `results/retail/probe_1g.csv` (one row per modified item: stored vs variant price and options; the task 37 row is blank because its reference starts with an intended failing e-mail lookup, and direct replay in the adversarial review found 2 of 3 items wrong), `results/retail/probe_1g_pair_order.csv`, `scripts/retail/probe_1g.py`.
- `retail/audit_log.csv` rows 1g and 2h; `retail/PLAN.md` (item 6 of the deviation entry written after the adversarial review); `results/retail/review_agent_E.md` (task 100, ground-truth run).
- `upstream/repro/I11.py`.
