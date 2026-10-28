"""Probe 2h (retail): does the order of WRITE reference actions change the target DB hash?

Same design as scripts/probe_2h.py: for every retail task with >= 2 WRITE actions, replay the reference
with the WRITE actions in every other order (READ/GENERIC keep their positions) through the evaluator's
code path and compare the hash with the gold hash. No LLM calls. Output: results/retail/probe_2h.csv.
Run from inside tau2-bench:  uv run --no-sync python ../scripts/retail/probe_2h.py
"""

from __future__ import annotations

import csv
import itertools
import os
import sys
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.environment.toolkit import ToolType  # noqa: E402
from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "retail" / "probe_2h.csv"
DOMAIN = "retail"
MAX_PERMS = 120  # 5! - 1; retail has at most 5 WRITE actions per task


def replay_hash(env_ctor, actions) -> tuple[str, int]:
    env = env_ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    errors = 0
    for a in actions:
        try:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception:
            errors += 1
    return env.get_db_hash(), errors


def main() -> int:
    env_ctor = registry.get_env_constructor(DOMAIN)
    tasks = registry.get_tasks_loader(DOMAIN)("base")
    probe_env = env_ctor()
    rows = []
    for task in tasks:
        actions = list((task.evaluation_criteria.actions or []) if task.evaluation_criteria else [])
        write_idx = [i for i, a in enumerate(actions) if probe_env.tools.tool_type(a.name) == ToolType.WRITE]
        if len(write_idx) < 2:
            continue
        gold, _ = replay_hash(env_ctor, actions)
        writes = [actions[i] for i in write_idx]
        n_perm = n_diff = n_err = 0
        diff_orders = []
        for perm in itertools.permutations(range(len(writes))):
            if list(perm) == list(range(len(writes))):
                continue
            if n_perm >= MAX_PERMS:
                break
            n_perm += 1
            variant = list(actions)
            for slot, src in zip(write_idx, perm):
                variant[slot] = writes[src]
            h, err = replay_hash(env_ctor, variant)
            n_err += err > 0
            if h != gold:
                n_diff += 1
                diff_orders.append("".join(str(p) for p in perm))
        same_order = len({a.arguments.get("order_id") for a in writes if "order_id" in a.arguments}) < sum(1 for a in writes if "order_id" in a.arguments)
        rows.append({
            "task_id": task.id,
            "n_write": len(writes),
            "write_names": "|".join(a.name for a in writes),
            "same_tool_writes": int(len({a.name for a in writes}) < len(writes)),
            "writes_share_an_order": int(same_order),
            "n_permutations": n_perm,
            "n_hash_differs": n_diff,
            "n_with_replay_error": n_err,
            "orders_that_differ": "|".join(diff_orders[:20]),
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"tasks with >=2 WRITE actions: {len(rows)}; tasks where some reordering changes the hash: {sum(1 for r in rows if r['n_hash_differs'])}")
    for r in rows:
        if r["n_hash_differs"] or r["n_with_replay_error"]:
            print(f"  task {r['task_id']:>3}: writes={r['n_write']} [{r['write_names']}] perms={r['n_permutations']} "
                  f"hash_differs={r['n_hash_differs']} replay_err={r['n_with_replay_error']} share_order={r['writes_share_an_order']}")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
