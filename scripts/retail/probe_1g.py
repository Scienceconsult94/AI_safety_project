"""Check 1g (added 2026-10-27 during the retail review): does a WRITE tool store the state its documentation describes?

Found by a reviewer reading tools.py: in `modify_pending_order_items` the loop that rewrites the order items uses the
variable `variant` left over from the validation loop, i.e. the LAST new variant, so with two or more items every
modified item receives the last variant's price and options (tools.py, the "Modify the order" loop). The payment
difference is computed correctly; the stored items are wrong. The target state of every task whose reference modifies
>= 2 items in one call is therefore a corrupted order, and the agent is scored against that corrupted state.

For every reference `modify_pending_order_items` call this script replays the reference up to and including that call
and compares each modified item's stored price and options with the variant the call named. Output:
results/retail/probe_1g.csv (one row per modified item). No LLM calls.
Run from inside tau2-bench:  uv run --no-sync python ../scripts/retail/probe_1g.py
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "retail" / "probe_1g.csv"


def main() -> int:
    env_ctor = registry.get_env_constructor("retail")
    tasks = registry.get_tasks_loader("retail")("base")
    rows = []
    for task in tasks:
        actions = list((task.evaluation_criteria.actions or []) if task.evaluation_criteria else [])
        for k, a in enumerate(actions):
            if a.name != "modify_pending_order_items":
                continue
            env = env_ctor()
            env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
            err = ""
            for b in actions[: k + 1]:
                try:
                    env.make_tool_call(tool_name=b.name, requestor=b.requestor, **b.arguments)
                except Exception as e:  # noqa: BLE001
                    err = f"{b.name}: {type(e).__name__}: {e}"
            if err:
                rows.append({"task_id": task.id, "action_id": a.action_id, "n_items": len(a.arguments["item_ids"]), "new_item_id": "", "stored_price": "",
                             "variant_price": "", "stored_options": "", "variant_options": "", "matches": "", "replay_error": err[:120]})
                continue
            db = env.tools.db
            order = db.orders[a.arguments["order_id"]]
            for new_id in a.arguments["new_item_ids"]:
                item = next((it for it in order.items if it.item_id == new_id), None)
                var = db.products[item.product_id].variants[new_id] if item else None
                rows.append({"task_id": task.id, "action_id": a.action_id, "n_items": len(a.arguments["item_ids"]), "new_item_id": new_id,
                             "stored_price": item.price if item else "", "variant_price": var.price if var else "",
                             "stored_options": str(dict(item.options)) if item else "", "variant_options": str(dict(var.options)) if var else "",
                             "matches": int(bool(item and var and item.price == var.price and dict(item.options) == dict(var.options))), "replay_error": ""})
    # pair-order dependence: the same (old, new) pairs listed in another order inside the one call
    import itertools
    perm_rows = []
    for task in tasks:
        actions = list((task.evaluation_criteria.actions or []) if task.evaluation_criteria else [])
        for k, a in enumerate(actions):
            if a.name != "modify_pending_order_items" or len(a.arguments["item_ids"]) < 2:
                continue
            pairs = list(zip(a.arguments["item_ids"], a.arguments["new_item_ids"]))

            def run(order_pairs):
                env = env_ctor()
                env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
                err = 0
                for j, b in enumerate(actions):
                    args = dict(b.arguments)
                    if j == k:
                        args["item_ids"] = [x for x, _ in order_pairs]
                        args["new_item_ids"] = [y for _, y in order_pairs]
                    try:
                        env.make_tool_call(tool_name=b.name, requestor=b.requestor, **args)
                    except Exception:  # noqa: BLE001
                        err += 1
                return env.get_db_hash(), err

            gold, _ = run(pairs)
            n = n_diff = 0
            for perm in itertools.permutations(pairs):
                if list(perm) == pairs:
                    continue
                n += 1
                h, _ = run(list(perm))
                n_diff += h != gold
                if n >= 120:
                    break
            perm_rows.append({"task_id": task.id, "action_id": a.action_id, "n_pairs": len(pairs), "n_pair_orders_tried": n, "n_hash_differs": n_diff})
    with open(OUT.with_name("probe_1g_pair_order.csv"), "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=["task_id", "action_id", "n_pairs", "n_pair_orders_tried", "n_hash_differs"])
        w.writeheader()
        w.writerows(perm_rows)
    print("pair-order dependence (same pairs, another order inside the call):", [(r["task_id"], f"{r['n_hash_differs']}/{r['n_pair_orders_tried']}") for r in perm_rows])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bad = [r for r in rows if r["matches"] == 0]
    multi = {r["task_id"] for r in rows if int(r["n_items"]) >= 2}
    print(f"modify_pending_order_items calls: {len({(r['task_id'], r['action_id']) for r in rows})} in {len({r['task_id'] for r in rows})} tasks; "
          f"multi-item calls in tasks {sorted(multi, key=int)}; items stored with a wrong price or options: {len(bad)} in tasks {sorted({r['task_id'] for r in bad}, key=int)}")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
