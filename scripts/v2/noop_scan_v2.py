"""H1 and H2 of block2/PLAN.md, no model calls.

H1  no-op pass under v2: for all 50 airline tasks, does an empty trajectory score 1?
    v1: DB(gold == initial, raw hash) and communicate_info empty.
    v2: canonical hash, communicate_info empty, and the empty-trajectory rule for nl_assertions
        (an assertion cannot be met by a trajectory with no assistant text).
    -> results/v2/noop_scan_v2.csv ; cross-checked against results/static_scan.csv (noop_pass).
H2  WRITE-order permutation probe (same procedure as scripts/probe_2h.py) under raw and canonical
    hash -> results/v2/probe_2h_v2.csv ; cross-checked against results/probe_2h.csv.

Run from inside tau2-bench:  uv run --no-sync python ../scripts/v2/noop_scan_v2.py
"""

from __future__ import annotations

import csv
import itertools
import os
import sys
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "ERROR")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
OUT = ROOT / "results" / "v2"

import scorer_v2 as s2  # noqa: E402
from tau2.environment.toolkit import ToolType  # noqa: E402
from tau2.registry import registry  # noqa: E402

MAX_PERMS = 24


def replay(env_ctor, actions):
    env = env_ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    errors = 0
    for a in actions:
        try:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception:  # noqa: BLE001
            errors += 1
    return env.tools.db, errors


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    env_ctor = registry.get_env_constructor("airline")
    tasks = registry.get_tasks_loader("airline")("base")
    initial = env_ctor().tools.db
    raw0, canon0 = s2.raw_hash(initial), s2.canonical_hash(initial)

    # ---- H1
    old = {}
    p = ROOT / "results" / "static_scan.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            old[r["task_id"]] = r.get("noop_pass")
    rows = []
    for t in tasks:
        ec = t.evaluation_criteria
        gold, errs = replay(env_ctor, ec.actions or [])
        db_v1 = int(s2.raw_hash(gold) == raw0)
        db_v2 = int(s2.canonical_hash(gold) == canon0)
        comm = int(not (ec.communicate_info or []))
        nl_v2 = int(not (ec.nl_assertions or []))  # empty-trajectory rule
        rows.append({"task_id": t.id, "n_actions": len(ec.actions or []), "replay_errors": errs, "db_unchanged_v1": db_v1,
                     "db_unchanged_v2": db_v2, "comm_empty": comm, "n_nl_assertions": len(ec.nl_assertions or []),
                     "noop_pass_v1": db_v1 & comm, "noop_pass_v1_static_scan": old.get(t.id, ""), "noop_pass_v2": db_v2 & comm & nl_v2})
    with open(OUT / "noop_scan_v2.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n1 = sum(r["noop_pass_v1"] for r in rows)
    n2 = sum(r["noop_pass_v2"] for r in rows)
    agree = sum(1 for r in rows if str(r["noop_pass_v1"]) == str(r["noop_pass_v1_static_scan"]))
    print(f"H1 no-op pass: v1 {n1}/{len(rows)} (static_scan.csv agrees on {agree}/{len(rows)}), v2 {n2}/{len(rows)}; "
          f"db_unchanged v1 vs v2 differ on {sum(1 for r in rows if r['db_unchanged_v1'] != r['db_unchanged_v2'])} tasks")

    # ---- H2
    oldp = {}
    p = ROOT / "results" / "probe_2h.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            oldp[r["task_id"]] = r
    probe_env = env_ctor()
    prows = []
    for t in tasks:
        actions = list(t.evaluation_criteria.actions or [])
        widx = [i for i, a in enumerate(actions) if probe_env.tools.tool_type(a.name) == ToolType.WRITE]
        if len(widx) < 2:
            continue
        gold, _ = replay(env_ctor, actions)
        g_raw, g_can = s2.raw_hash(gold), s2.canonical_hash(gold)
        writes = [actions[i] for i in widx]
        n_perm = d_raw = d_can = n_err = 0
        can_orders = []
        for perm in itertools.permutations(range(len(writes))):
            if list(perm) == list(range(len(writes))):
                continue
            if n_perm >= MAX_PERMS:
                break
            n_perm += 1
            variant = list(actions)
            for slot, src in zip(widx, perm):
                variant[slot] = writes[src]
            db, err = replay(env_ctor, variant)
            n_err += err > 0
            d_raw += s2.raw_hash(db) != g_raw
            if s2.canonical_hash(db) != g_can:
                d_can += 1
                can_orders.append("".join(map(str, perm)))
        prows.append({"task_id": t.id, "n_write": len(writes), "write_names": "|".join(a.name for a in writes), "n_permutations": n_perm,
                      "n_hash_differs_raw": d_raw, "n_hash_differs_raw_probe_2h": oldp.get(t.id, {}).get("n_hash_differs", ""),
                      "n_hash_differs_canonical": d_can, "n_with_replay_error": n_err, "orders_that_differ_canonical": "|".join(can_orders)})
    with open(OUT / "probe_2h_v2.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(prows[0]))
        w.writeheader()
        w.writerows(prows)
    agree = sum(1 for r in prows if str(r["n_hash_differs_raw"]) == str(r["n_hash_differs_raw_probe_2h"]))
    print(f"H2 permutation probe: {len(prows)} tasks; raw differs in {sum(r['n_hash_differs_raw'] for r in prows)} of "
          f"{sum(r['n_permutations'] for r in prows)} permutations (probe_2h.csv agrees on {agree}/{len(prows)} tasks); "
          f"canonical differs in {sum(r['n_hash_differs_canonical'] for r in prows)}")
    for r in prows:
        print(f"  task {r['task_id']:>2}: writes={r['n_write']} raw={r['n_hash_differs_raw']} canonical={r['n_hash_differs_canonical']} "
              f"replay_err={r['n_with_replay_error']} [{r['write_names']}]")
    print(f"written {OUT.relative_to(ROOT)}/noop_scan_v2.csv, probe_2h_v2.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
