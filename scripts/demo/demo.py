"""Five-minute demo: four ways the tau2-bench exam fails, reproduced offline with no model call (under a minute in all).

  1. An empty conversation gets full reward on 23 of the 50 airline tasks (stock scorer).
  2. Retail task 72: a change order that the policy forbids reaches the same scored state as the compliant one.
  3. Retail task 20: modify_pending_order_items stores the last variant's price and options in every modified item.
  4. Retail task 105: the only reference action fails, so no conversation can pass the task.

Run from inside tau2-bench (pinned v2.0.0 clone):
    PYTHONUTF8=1 uv run --no-sync python ../scripts/demo/demo.py            # all four
    PYTHONUTF8=1 uv run --no-sync python ../scripts/demo/demo.py --only 2   # one of them
Reads only the benchmark's own data and code; changes nothing.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

os.environ.setdefault("LOGURU_LEVEL", "ERROR")
from loguru import logger  # noqa: E402

logger.remove()
logger.add(sys.stderr, level="ERROR")

from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402


def banner(n: int, title: str) -> None:
    print("\n" + "=" * 100 + f"\n{n}. {title}\n" + "=" * 100)


def fresh(env_ctor):
    env = env_ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    return env


def demo_empty_airline() -> None:
    banner(1, "Airline: what does an agent get for saying nothing?")
    env_ctor = registry.get_env_constructor("airline")
    tasks = registry.get_tasks_loader("airline")("base")
    scoring = CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)
    passed = []
    for t in tasks:
        traj = list(t.initial_state.message_history or []) if t.initial_state else []
        db = EnvironmentEvaluator.calculate_reward(env_ctor, t, full_trajectory=traj).reward
        comm = CommunicateEvaluator.calculate_reward(task=t, full_trajectory=traj, scoring=scoring).reward
        if db * comm == 1.0:
            passed.append(t.id)
    print("The conversation is empty: no agent message, no tool call. The stock scorer compares the final database with")
    print("the reference's final database and looks for the required strings.")
    print(f"\n  full reward on {len(passed)} of {len(tasks)} tasks: {', '.join(passed)}")
    print("\nThese tasks expect the agent to refuse or only to look things up, so the database does not change and nothing")
    print("is required to be said. The exam cannot tell a correct refusal from an agent that did nothing.")


def demo_forbidden_order() -> None:
    banner(2, "Retail task 72: the order of changes the policy forbids scores the same")
    env_ctor = registry.get_env_constructor("retail")
    task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["72"]
    acts = list(task.evaluation_criteria.actions)
    addr = next(a for a in acts if a.name == "modify_pending_order_address")
    items = next(a for a in acts if a.name == "modify_pending_order_items")
    reads = [a for a in acts if a not in (addr, items)]
    order_id = addr.arguments["order_id"]

    def run(seq, label):
        env = fresh(env_ctor)
        print(f"\n  {label}")
        for a in seq:
            before = env.tools.db.orders[order_id].status if a in (addr, items) else None
            try:
                env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
                res = "accepted"
            except Exception as e:  # noqa: BLE001
                res = f"rejected ({e})"
            if a in (addr, items):
                print(f"    {a.name:<32} order status before: {before!r:<26} -> {res}")
        return env.get_db_hash()

    print("policy.md, line 110, on modifying items: \"The agent will not be able to modify or cancel the order anymore.\"")
    h_ref = run(acts, "reference order (address first, then items):")
    h_bad = run(reads + [items, addr], "forbidden order (items first, then address):")
    print(f"\n  final database identical: {h_ref == h_bad}")
    print("\nThe address tool accepts the status 'pending (item modified)' because it tests the status by substring.")
    print("The scorer compares only the end state, so it cannot see the violation: 14 retail tasks behave like this.")


def demo_tool_bug() -> None:
    banner(3, "Retail task 20: the tool stores the wrong item")
    env_ctor = registry.get_env_constructor("retail")
    task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["20"]
    acts = list(task.evaluation_criteria.actions)
    k = next(i for i, a in enumerate(acts) if a.name == "modify_pending_order_items")
    env = fresh(env_ctor)
    for a in acts[: k + 1]:
        env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
    db = env.tools.db
    call = acts[k].arguments
    order = db.orders[call["order_id"]]
    print(f"One modify_pending_order_items call swaps {len(call['item_ids'])} items in order {call['order_id']}. Stored afterwards:\n")
    print(f"  {'requested variant':<18} {'product':<16} {'catalogue price':>15} {'stored price':>13}  stored options")
    wrong = 0
    for new_id in call["new_item_ids"]:
        it = next(i for i in order.items if i.item_id == new_id)
        prod = db.products[it.product_id]
        var = prod.variants[new_id]
        ok = it.price == var.price and dict(it.options) == dict(var.options)
        wrong += not ok
        print(f"  {new_id:<18} {prod.name[:16]:<16} {var.price:>15.2f} {it.price:>13.2f}  {dict(it.options)}{'' if ok else '   <- wrong'}")
    print(f"\n  {wrong} of {len(call['new_item_ids'])} items carry another variant's price and options.")
    print("\nThe loop that writes the items reuses the last variant from the validation loop. The reference's target state is")
    print("this corrupted order, so an agent that lists the same swaps in another order gets a different state and scores 0.")


def demo_unreachable() -> None:
    banner(4, "Retail task 105: a task no conversation can pass")
    env_ctor = registry.get_env_constructor("retail")
    task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["105"]
    acts = list(task.evaluation_criteria.actions)
    env = fresh(env_ctor)
    h0 = env.get_db_hash()
    a = acts[0]
    db = env.tools.db
    order = db.orders[a.arguments["order_id"]]
    gc = db.users[order.user_id].payment_methods[a.arguments["payment_method_id"]]
    index = {vid: v for p in db.products.values() for vid, v in p.variants.items()}
    old = sum(next(i.price for i in order.items if i.item_id == x) for x in a.arguments["item_ids"])
    new = sum(index[x].price for x in a.arguments["new_item_ids"])
    print(f"The only reference action: {a.name} on {a.arguments['order_id']}, paid with {a.arguments['payment_method_id']}.")
    print(f"  price difference to pay: {new - old:.2f}; gift card balance: {gc.balance:.2f}")
    try:
        env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        print("  reference action accepted")
    except Exception as e:  # noqa: BLE001
        print(f"  reference action rejected: {e}")
    print(f"  scored target state equals the starting state: {env.get_db_hash() == h0}")
    print(f"\n  the task's assertion: {task.evaluation_criteria.nl_assertions}")
    print("\nTo pass the hash the database must stay unchanged; to pass the assertion the exchange must happen. Both cannot hold.")


DEMOS = {1: demo_empty_airline, 2: demo_forbidden_order, 3: demo_tool_bug, 4: demo_unreachable}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, choices=sorted(DEMOS))
    args = ap.parse_args()
    t0 = time.time()
    for n, fn in DEMOS.items():
        if args.only in (None, n):
            fn()
    print(f"\n(done in {time.time() - t0:.0f} s; tau2-bench v2.0.0, no model call)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
