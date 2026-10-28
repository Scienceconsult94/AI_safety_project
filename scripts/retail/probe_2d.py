"""Probes 2d and 2e (retail): can the end-state hash tell a wrong solution from the reference?

2d — argument perturbation. For every WRITE reference action and every scalar argument that has a natural
alternative in the DB, replace that one value, replay the whole reference on a fresh environment and compare
the resulting hash with the gold hash. Alternatives tried:
  payment_method_id  -> every other payment method of the order's user (and the order's original method)
  reason             -> the other allowed cancellation reason
  new_item_ids[k]    -> every other available variant of the same product (one position at a time)
  item_ids           -> drop one item from the list (returns/exchanges/modifications with >= 2 items)
  address fields     -> the user's default address (for order address writes) / the order address (for user address writes)
A perturbation whose replay raises is recorded as "rejected by the tool" (the scorer never sees it).
A perturbation that replays AND yields the gold hash is a blind spot: the scorer cannot distinguish it (2d defect).

2e — hidden intermediate write. For tasks whose reference writes an address, a wrong address write on the same
target is inserted before the reference write; the final hash is compared with the gold hash. Equal = the
end-state comparison hides the earlier wrong write (2e per-task evidence).
2e — forbidden write order (added 2026-10-27 after the reviewers found it): for tasks whose reference changes the
address of an order and then its items, the two writes are swapped. policy.md l.110 forbids any modification after
the items change; the address tool accepts the status "pending (item modified)". Equal hash without error = the
policy-violating order scores 1.0.

No LLM calls. Output: results/retail/probe_2d.csv (one row per perturbation) and a summary on stdout.
Run from inside tau2-bench:  uv run --no-sync python ../scripts/retail/probe_2d.py
"""

from __future__ import annotations

import copy
import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.environment.toolkit import ToolType  # noqa: E402
from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "retail" / "probe_2d.csv"
DOMAIN = "retail"
ADDRESS_FIELDS = ("address1", "address2", "city", "state", "country", "zip")
WRONG_ADDRESS = {"address1": "1 Probe Street", "address2": "", "city": "Nowhere", "state": "ZZ", "country": "USA", "zip": "00000"}


def fresh(env_ctor):
    env = env_ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    return env


def replay(env_ctor, actions) -> tuple[str, str]:
    """(hash, first error message or '')."""
    env = fresh(env_ctor)
    err = ""
    for a in actions:
        try:
            env.make_tool_call(tool_name=a["name"], requestor="assistant", **a["arguments"])
        except Exception as e:  # noqa: BLE001
            err = err or f"{a['name']}: {type(e).__name__}: {e}"
    return env.get_db_hash(), err


def as_dicts(actions) -> list[dict]:
    return [{"action_id": a.action_id, "name": a.name, "arguments": copy.deepcopy(a.arguments)} for a in actions]


def main() -> int:
    env_ctor = registry.get_env_constructor(DOMAIN)
    tasks = registry.get_tasks_loader(DOMAIN)("base")
    db = fresh(env_ctor).tools.db
    tool_type = fresh(env_ctor).tools.tool_type
    rows = []

    def add(task_id, check, action, field, original, alternative, kind, h_gold, h_var, err):
        rows.append({"task_id": task_id, "check": check, "action_id": action["action_id"], "tool": action["name"], "field": field,
                     "original": str(original)[:80], "alternative": str(alternative)[:80], "kind": kind,
                     "replay_error": err[:120], "hash_equals_gold": "" if err else int(h_var == h_gold)})

    for task in tasks:
        ref = as_dicts(task.evaluation_criteria.actions or []) if task.evaluation_criteria else []
        if not ref:
            continue
        gold, gold_err = replay(env_ctor, ref)
        for idx, a in enumerate(ref):
            if tool_type(a["name"]) != ToolType.WRITE:
                continue
            args = a["arguments"]
            order = db.orders.get(args.get("order_id", "")) if "order_id" in args else None
            user = db.users.get(order.user_id) if order else db.users.get(args.get("user_id", ""))

            def variant_with(field, value):
                v = copy.deepcopy(ref)
                v[idx]["arguments"][field] = value
                return v

            # payment method alternatives
            if "payment_method_id" in args and user is not None:
                for pm in user.payment_methods:
                    if pm == args["payment_method_id"]:
                        continue
                    kind = "other payment method of the same user"
                    if order is not None and order.payment_history and pm == order.payment_history[0].payment_method_id:
                        kind = "order's original payment method"
                    h, err = replay(env_ctor, variant_with("payment_method_id", pm))
                    add(task.id, "2d", a, "payment_method_id", args["payment_method_id"], pm, kind, gold, h, err)
            # cancellation reason
            if "reason" in args:
                other = "ordered by mistake" if args["reason"] == "no longer needed" else "no longer needed"
                h, err = replay(env_ctor, variant_with("reason", other))
                add(task.id, "2d", a, "reason", args["reason"], other, "other allowed cancel reason", gold, h, err)
            # new item variants
            if "new_item_ids" in args and order is not None:
                for k, (old_id, new_id) in enumerate(zip(args.get("item_ids", []), args["new_item_ids"])):
                    item = next((it for it in order.items if it.item_id == old_id), None)
                    product = db.products.get(item.product_id) if item else None
                    if product is None:
                        continue
                    for vid, var in product.variants.items():
                        if vid in (old_id, new_id) or not var.available:
                            continue
                        new_list = list(args["new_item_ids"])
                        new_list[k] = vid
                        h, err = replay(env_ctor, variant_with("new_item_ids", new_list))
                        add(task.id, "2d", a, f"new_item_ids[{k}]", new_id, vid, "other available variant of the same product", gold, h, err)
            # drop one item
            if "item_ids" in args and len(args["item_ids"]) >= 2:
                for k in range(len(args["item_ids"])):
                    v = copy.deepcopy(ref)
                    v[idx]["arguments"]["item_ids"] = [x for j, x in enumerate(args["item_ids"]) if j != k]
                    if "new_item_ids" in args:
                        v[idx]["arguments"]["new_item_ids"] = [x for j, x in enumerate(args["new_item_ids"]) if j != k]
                    h, err = replay(env_ctor, v)
                    add(task.id, "2d", a, f"item_ids[-{k}]", args["item_ids"][k], "(dropped)", "one item fewer", gold, h, err)
            # address alternatives and the hidden intermediate write (2e)
            if all(f in args for f in ADDRESS_FIELDS):
                alt = None
                if a["name"] == "modify_pending_order_address" and user is not None:
                    alt, kind = user.address, "user's default address instead of the requested one"
                elif a["name"] == "modify_user_address" and user is not None and user.orders:
                    o = db.orders.get(user.orders[0])
                    alt, kind = (o.address if o else None), "address of the user's first order instead of the requested one"
                if alt is not None:
                    alt_d = {f: getattr(alt, f) for f in ADDRESS_FIELDS}
                    if alt_d != {f: args[f] for f in ADDRESS_FIELDS}:
                        v = copy.deepcopy(ref)
                        v[idx]["arguments"].update(alt_d)
                        h, err = replay(env_ctor, v)
                        add(task.id, "2d", a, "address", args["address1"], alt_d["address1"], kind, gold, h, err)
                v = copy.deepcopy(ref)
                wrong = {"action_id": a["action_id"] + "_probe", "name": a["name"], "arguments": {**copy.deepcopy(args), **WRONG_ADDRESS}}
                v.insert(idx, wrong)
                h, err = replay(env_ctor, v)
                add(task.id, "2e", a, "address", args["address1"], WRONG_ADDRESS["address1"], "wrong address written first, then the reference write", gold, h, err)

        # 2e, forbidden write order: policy.md l.110 forbids any further modification of an order once its items were
        # modified, but modify_pending_order_address accepts status "pending (item modified)" (_is_pending_order). For every
        # task whose reference modifies the address of an order BEFORE modifying its items, swap the two writes and replay.
        by_order = {}
        for idx, a in enumerate(ref):
            if a["name"] in ("modify_pending_order_address", "modify_pending_order_items"):
                by_order.setdefault(a["arguments"].get("order_id"), []).append((idx, a["name"]))
        for oid, writes in by_order.items():
            names = [n for _, n in writes]
            if "modify_pending_order_address" in names and "modify_pending_order_items" in names:
                i_addr = next(i for i, n in writes if n == "modify_pending_order_address")
                i_items = next(i for i, n in writes if n == "modify_pending_order_items")
                if i_addr < i_items:
                    v = copy.deepcopy(ref)
                    v[i_addr], v[i_items] = v[i_items], v[i_addr]
                    h, err = replay(env_ctor, v)
                    add(task.id, "2e", ref[i_addr], "write_order", "address then items", "items then address",
                        "items modified before the address change (forbidden by policy.md l.110; the tool accepts it)", gold, h, err)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    d = [r for r in rows if r["check"] == "2d"]
    e = [r for r in rows if r["check"] == "2e"]
    blind = [r for r in d if r["hash_equals_gold"] == 1]
    rejected = [r for r in d if r["replay_error"]]
    print(f"2d perturbations: {len(d)} over {len({r['task_id'] for r in d})} tasks; rejected by the tool: {len(rejected)}; "
          f"replayed and hash differs: {sum(1 for r in d if r['hash_equals_gold'] == 0)}; replayed and hash EQUALS gold (blind spot): {len(blind)}")
    for r in blind:
        print(f"  BLIND task {r['task_id']} {r['tool']} {r['field']}: {r['original']} -> {r['alternative']} ({r['kind']})")
    ea = [r for r in e if r["field"] == "address"]
    eo = [r for r in e if r["field"] == "write_order"]
    print(f"2e hidden-write probes: {len(ea)} over {len({r['task_id'] for r in ea})} tasks; final hash equals gold: {sum(1 for r in ea if r['hash_equals_gold'] == 1)}; "
          f"rejected: {sum(1 for r in ea if r['replay_error'])}")
    print(f"2e forbidden write order (items before address, same order): {len(eo)} tasks probed; replays to the gold hash without error: "
          f"{sum(1 for r in eo if r['hash_equals_gold'] == 1)} -> {[r['task_id'] for r in eo if r['hash_equals_gold'] == 1]}; rejected: {sum(1 for r in eo if r['replay_error'])}")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
