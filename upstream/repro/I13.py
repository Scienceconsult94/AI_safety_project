"""I13: retail reference-trajectory defects (tasks 2-4, 105, 26, 110, 18, 64, action ids from 95 on).

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I13.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

from tau2.registry import registry  # noqa: E402

ENV = registry.get_env_constructor("retail")
TASKS = {t.id: t for t in registry.get_tasks_loader("retail")("base")}


def replay(task):
    """Replay the reference like EnvironmentEvaluator does; return the env and the raising actions."""
    env = ENV()
    errors = []
    for a in task.evaluation_criteria.actions:
        try:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception as e:  # noqa: BLE001
            errors.append((a.action_id, a.name, str(e)))
    return env, errors


db = ENV().tools.db
initial_hash = ENV().get_db_hash()

# (a) a product id that exists nowhere
for tid in ("2", "3", "4"):
    acts = TASKS[tid].evaluation_criteria.actions
    bad = [a.action_id for a in acts if a.name == "get_product_details" and a.arguments["product_id"] not in db.products]
    print(f"(a) task {tid}: get_product_details on an unknown product id in {bad}; replay errors {replay(TASKS[tid])[1]}")
print(f"    task 2 action ids: {[a.action_id for a in TASKS['2'].evaluation_criteria.actions][:4]}")

# (b) task 105: the only reference action raises, so the target is the unchanged DB
task = TASKS["105"]
a = task.evaluation_criteria.actions[0]
order = db.orders[a.arguments["order_id"]]
old = {it.item_id: it.price for it in order.items}
diff = round(sum(db.products[next(it.product_id for it in order.items if it.item_id == o)].variants[n].price - old[o]
                 for o, n in zip(a.arguments["item_ids"], a.arguments["new_item_ids"])), 2)
card = db.users[order.user_id].payment_methods[a.arguments["payment_method_id"]]
env, errors = replay(task)
print(f"(b) task 105: {a.action_id} {a.name} pays a difference of {diff} with {card.id} (balance {card.balance}); "
      f"replay errors {errors}; target hash == initial hash: {env.get_db_hash() == initial_hash}")
print(f"    nl_assertions: {task.evaluation_criteria.nl_assertions}")

# (c) task 26: the transfer summary describes task 25's scenario
summary = TASKS["26"].evaluation_criteria.actions[-1].arguments["summary"]
print(f"(c) task 26 transfer summary: {summary!r}; 'amex' in task 26 scenario: "
      f"{'amex' in TASKS['26'].user_scenario.instructions.reason_for_call}; in task 25 scenario: "
      f"{'amex' in TASKS['25'].user_scenario.instructions.reason_for_call}")

# (d) task 110: the user-address write is a no-op
task = TASKS["110"]
a = next(x for x in task.evaluation_criteria.actions if x.name == "modify_user_address")
current = db.users[a.arguments["user_id"]].address.model_dump()
written = {k: v for k, v in a.arguments.items() if k != "user_id"}
print(f"(d) task 110: {a.action_id} writes the address the user already has: {current == written}; "
      f"assertion: {task.evaluation_criteria.nl_assertions[1]!r}")

# (e) task 18: the fallback presupposes that the ordered chair is unavailable
task = TASKS["18"]
a = task.evaluation_criteria.actions[-1]
order = db.orders[a.arguments["order_id"]]
chair = next(it for it in order.items if it.item_id == a.arguments["item_ids"][0])
print(f"(e) task 18: ordered chair {chair.item_id} available in db.json: "
      f"{db.products[chair.product_id].variants[chair.item_id].available}; reference exchanges it for {a.arguments['new_item_ids']}")

# (f) task 64: a reference exchange on a pending order
print(f"(f) task 64: replay errors {replay(TASKS['64'])[1]}")

# (g) action ids that carry another task's number
mismatch = [t.id for t in TASKS.values() if any(not x.action_id.startswith(f"{t.id}_") for x in t.evaluation_criteria.actions or [])]
print(f"(g) tasks whose action ids do not start with their own id: {mismatch}")
print(f"    task 104 action ids: {[x.action_id for x in TASKS['104'].evaluation_criteria.actions]}")
