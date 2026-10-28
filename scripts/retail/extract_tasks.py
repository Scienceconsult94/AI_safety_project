"""One Markdown "task card" per retail task for static review and blind re-review.

Each card gathers: the author annotation, the user-simulator instructions, the reference trajectory, communicate_info
and nl_assertions (with the note whether they gate the reward), the DB
records the task touches (user with payment methods and orders; the orders named in the reference or the scenario
with items, status and payment history; the products whose variants the reference exchanges or modifies, with the
available variants and prices), and the static-scan numbers. The upstream-recorded `issues` field is deliberately left out
(retail/PLAN.md P5: it is compared with the review afterwards, not shown to the reviewers). No LLM calls.
Usage (from ==Project):  python -I scripts/retail/extract_tasks.py   -> results/retail/task_cards/task_<id>.md
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tau2-bench" / "data" / "tau2" / "domains" / "retail"
OUT = ROOT / "results" / "retail" / "task_cards"


def j(obj) -> str:
    return "```json\n" + json.dumps(obj, ensure_ascii=False, indent=1) + "\n```"


def main() -> None:
    tasks = json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))
    db = json.loads((DATA / "db.json").read_text(encoding="utf-8"))
    scan = {r["task_id"]: r for r in csv.DictReader(open(ROOT / "results" / "retail" / "static_scan.csv", encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)
    email_index = {u["email"].lower(): uid for uid, u in db["users"].items()}
    name_zip_index = {}
    for uid, u in db["users"].items():
        name_zip_index.setdefault((u["name"]["first_name"].lower(), u["name"]["last_name"].lower(), u["address"]["zip"]), []).append(uid)

    for t in tasks:
        tid = t["id"]
        ec = t.get("evaluation_criteria") or {}
        us = (t.get("user_scenario") or {}).get("instructions") or {}
        actions = ec.get("actions") or []
        basis = ec.get("reward_basis") or []
        text_blob = " ".join(str(us.get(k, "")) for k in ("task_instructions", "reason_for_call", "known_info", "unknown_info"))
        user_ids, order_ids, product_ids = set(), set(), set()
        for a in actions:
            args = a.get("arguments") or {}
            if "user_id" in args:
                user_ids.add(args["user_id"])
            if "order_id" in args:
                order_ids.add(args["order_id"])
            if "product_id" in args:
                product_ids.add(args["product_id"])
            if a.get("name") == "find_user_id_by_email" and args.get("email", "").lower() in email_index:
                user_ids.add(email_index[args["email"].lower()])
            if a.get("name") == "find_user_id_by_name_zip":
                key = (str(args.get("first_name", "")).lower(), str(args.get("last_name", "")).lower(), str(args.get("zip", "")))
                user_ids |= set(name_zip_index.get(key, []))
        user_ids |= {m for m in re.findall(r"\b[a-z]+_[a-z]+_\d{4}\b", text_blob) if m in db["users"]}
        order_ids |= {m for m in re.findall(r"#W\d{7}", text_blob) if m in db["orders"]}
        for m in re.findall(r"[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]+", text_blob):
            if m.lower() in email_index:
                user_ids.add(email_index[m.lower()])
        for oid in list(order_ids):
            o = db["orders"].get(oid)
            if o:
                user_ids.add(o["user_id"])
        for uid in list(user_ids):
            order_ids |= set(db["users"].get(uid, {}).get("orders") or [])
        # products whose variants the reference touches (exchange / modify), from the order items
        for a in actions:
            args = a.get("arguments") or {}
            if "item_ids" in args or "new_item_ids" in args:
                o = db["orders"].get(args.get("order_id", ""))
                for it in (o or {}).get("items", []):
                    if it["item_id"] in (args.get("item_ids") or []):
                        product_ids.add(it["product_id"])

        s = scan.get(tid, {})
        nl_gate = "NL_ASSERTION" in basis
        lines = [
            f"# Retail task {tid}",
            "",
            f"bench_commit: `{s.get('bench_commit', '')}` · reward_basis: {basis}",
            f"static scan: n_actions={s.get('n_actions')} (read={s.get('n_read')}, write={s.get('n_write')}, generic={s.get('n_generic')}), "
            f"db_changed={s.get('db_changed')}, comm_len={s.get('comm_len')} (not scored), nl_count={s.get('nl_count')} ({'gates the reward' if nl_gate else 'not in basis'}), "
            f"**noop_pass={s.get('noop_pass')}**, noop_needs_judge={s.get('noop_needs_judge')}",
            "",
            "## Task description (author annotation, not shown to the agent)",
            j(t.get("description")),
            "",
            "## User-simulator instructions",
            f"**persona:** {(t.get('user_scenario') or {}).get('persona')}",
            "",
            f"**reason_for_call:**\n\n{us.get('reason_for_call', '')}",
            "",
            f"**known_info:**\n\n{us.get('known_info', '')}",
            "",
            f"**unknown_info:**\n\n{us.get('unknown_info', '')}",
            "",
            f"**task_instructions:**\n\n{us.get('task_instructions', '')}",
            "",
            "## Reference trajectory (evaluation_criteria.actions)",
            j(actions),
            "",
            "## communicate_info (NOT in reward_basis: never scored by tau2 run)",
            j(ec.get("communicate_info")),
            "",
            f"## nl_assertions ({'gate the reward through the LLM judge' if nl_gate else 'not in basis'})",
            j(ec.get("nl_assertions")),
            "",
            "## DB records referenced",
        ]
        for uid in sorted(user_ids):
            u = db["users"].get(uid)
            if u:
                lines += [f"### user `{uid}`", j(u)]
        for oid in sorted(order_ids):
            o = db["orders"].get(oid)
            if o:
                lines += [f"### order `{oid}` (status: {o.get('status')})", j(o)]
        for pid in sorted(product_ids):
            p = db["products"].get(pid)
            if p:
                slim = {"name": p["name"], "product_id": pid,
                        "variants": {vid: {"options": v["options"], "available": v["available"], "price": v["price"]} for vid, v in p["variants"].items()}}
                lines += [f"### product `{pid}` ({p['name']}; all variants)", j(slim)]
        (OUT / f"task_{tid}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(tasks)} cards to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
