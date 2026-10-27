"""Probe 2h: does the order of independent WRITE reference actions change the target DB hash?

For every airline task with >= 2 WRITE actions, replay the reference trajectory with the
WRITE actions in every other order (READ/GENERIC actions keep their positions) through
the same code path as EnvironmentEvaluator, and compare the resulting DB hash with the
gold hash. A differing hash means an agent that performs the same writes in another order
is scored 0. Whether that order is "allowed by the scenario" is judged separately per task
(checklist.md, 2h). No LLM calls. Output: results/probe_2h.csv.
Run from inside tau2-bench:  uv run --no-sync python ../probe_2h.py
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

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "probe_2h.csv"
MAX_PERMS = 24  # 4! - enough for airline (max 3-4 writes per task)


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
    env_ctor = registry.get_env_constructor("airline")
    tasks = registry.get_tasks_loader("airline")("base")
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
        rows.append({
            "task_id": task.id,
            "n_write": len(writes),
            "write_names": "|".join(a.name for a in writes),
            "same_tool_writes": int(len({a.name for a in writes}) < len(writes)),
            "n_permutations": n_perm,
            "n_hash_differs": n_diff,
            "n_with_replay_error": n_err,
            "orders_that_differ": "|".join(diff_orders),
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"tasks with >=2 WRITE actions: {len(rows)}")
    for r in rows:
        print(f"  task {r['task_id']:>2}: writes={r['n_write']} [{r['write_names']}] perms={r['n_permutations']} "
              f"hash_differs={r['n_hash_differs']} replay_err={r['n_with_replay_error']}")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
