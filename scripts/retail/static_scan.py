"""Static pre-screen over all retail tasks of tau2-bench (pinned tag v2.0.0) — the retail reading of scripts/static_scan.py.

For every task of the `base` split (114):
  1. build a fresh retail environment as `EnvironmentEvaluator` does, record the initial DB hash, replay
     `evaluation_criteria.actions` action by action and record the target ("gold") hash; a second independent
     replay checks determinism (5a); WRITE actions that leave the hash unchanged are listed (1c);
  2. run the real `EnvironmentEvaluator` on an EMPTY trajectory and derive the no-op verdict of the stock scorer
     without calling the judge: reward = DB part x NL part, where the NL part is 1.0 by construction when the task
     has no `nl_assertions` (or NL_ASSERTION is not in the basis) and "needs the judge" otherwise
     (`noop_needs_judge`; the judged verdict comes from scripts/retail/noop_judge_probe.py);
  3. text pre-screen columns of retail/checklist.md: reference argument values not stated in the user scenario,
     scenario ids missing from the DB, communicate_info / nl numbers present in the scenario text, whether every
     communicate_info string is covered by an nl_assertion (string match), upstream-recorded issues.

No LLM is called. Output: results/retail/static_scan.csv plus a summary on stdout.
Run from inside the tau2-bench checkout:  cd tau2-bench && uv run --no-sync python ../scripts/retail/static_scan.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "WARNING")

from tau2.data_model.tasks import RewardType  # noqa: E402
from tau2.environment.toolkit import ToolType  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]  # repo root (this file lives in scripts/retail/)
BENCH = ROOT / "tau2-bench"
OUT = ROOT / "results" / "retail" / "static_scan.csv"
DOMAIN = "retail"
SPLIT = "base"
TRANSFER = "transfer_to_human_agents"


def bench_commit() -> str:
    return subprocess.check_output(["git", "-C", str(BENCH), "rev-parse", "HEAD"], text=True).strip()


def fresh_env(env_ctor, task):
    """Mirror EnvironmentEvaluator.calculate_reward's gold-environment setup."""
    init = task.initial_state
    env = env_ctor()
    env.set_state(
        initialization_data=getattr(init, "initialization_data", None) if init else None,
        initialization_actions=getattr(init, "initialization_actions", None) if init else None,
        message_history=list(getattr(init, "message_history", None) or []) if init else [],
        strict=True,
    )
    return env


def leaves(obj):
    """Scalar leaf values of a nested arguments dict/list, as strings."""
    if isinstance(obj, dict):
        for v in obj.values():
            yield from leaves(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from leaves(v)
    elif obj is not None and not isinstance(obj, bool):
        yield str(obj)


def norm(text: str) -> str:
    return text.lower().replace(",", "")


def scenario_text(task) -> tuple[str, str]:
    """(all user-scenario text, unknown_info text), lowercased, commas stripped."""
    us = task.user_scenario
    ins = getattr(us, "instructions", None)
    parts = [str(getattr(us, "persona", "") or "")]
    unknown = ""
    if ins is not None:
        if isinstance(ins, str):
            parts.append(ins)
        else:
            for k in ("task_instructions", "domain", "reason_for_call", "known_info", "unknown_info"):
                parts.append(str(getattr(ins, k, "") or ""))
            unknown = str(getattr(ins, "unknown_info", "") or "")
    return norm(" ".join(parts)), norm(unknown)


def db_id_sets(env):
    db = env.tools.db
    users = set(db.users.keys())
    orders = set(db.orders.keys())
    items = {vid for p in db.products.values() for vid in p.variants.keys()}
    products = set(db.products.keys())
    emails = {u.email.lower() for u in db.users.values()}
    return users, orders, items, products, emails


def ids_missing_in_db(raw_text: str, users: set, orders: set, items: set, products: set, emails: set) -> list[str]:
    """Ids named in the scenario text that do not exist in the DB (input to check 4d)."""
    missing = {m for m in re.findall(r"\b[a-z]+_[a-z]+_\d{4}\b", raw_text) if m not in users}
    missing |= {m for m in re.findall(r"#w\d{7}", raw_text) if m.upper() not in orders}
    missing |= {m for m in re.findall(r"\b\d{10}\b", raw_text) if m not in items and m not in products}
    missing |= {m for m in re.findall(r"[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]+", raw_text) if m not in emails}
    return sorted(missing)


def main() -> int:
    commit = bench_commit()
    sample_ids = set(json.load(open(ROOT / "retail" / "sample.json", encoding="utf-8"))["task_ids"])
    env_ctor = registry.get_env_constructor(DOMAIN)
    tasks = registry.get_tasks_loader(DOMAIN)(SPLIT)
    raw_tasks = {str(t["id"]): t for t in json.load(open(BENCH / "data" / "tau2" / "domains" / DOMAIN / "tasks.json", encoding="utf-8"))}
    users_db, orders_db, items_db, products_db, emails_db = db_id_sets(env_ctor())

    rows = []
    for task in tasks:
        ec = task.evaluation_criteria
        actions = list(ec.actions or []) if ec else []
        comm = list(ec.communicate_info or []) if ec else []
        nl = list(ec.nl_assertions or []) if ec else []
        basis = [str(getattr(b, "value", b)) for b in (ec.reward_basis or [])] if ec else []
        nl_in_basis = int(bool(ec) and RewardType.NL_ASSERTION in (ec.reward_basis or []))
        comm_in_basis = int(bool(ec) and RewardType.COMMUNICATE in (ec.reward_basis or []))

        # 1. reference replay, same code path as the evaluator, action by action
        env = fresh_env(env_ctor, task)
        init_hash = env.get_db_hash()
        init_hash_stable = fresh_env(env_ctor, task).get_db_hash() == init_hash  # 3f
        counts = {"read": 0, "write": 0, "generic": 0, "think": 0, "unknown": 0}
        errors, write_noop_ids = [], []
        for a in actions:
            is_write = False
            try:
                tt = env.tools.tool_type(a.name)
                key = tt.value if isinstance(tt, ToolType) else str(tt)
                counts[key] += 1
                is_write = key == "write"
            except Exception:
                counts["unknown"] += 1
            before = env.get_db_hash()
            try:
                env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
            except Exception as e:  # the evaluator only logs a warning here (1b)
                errors.append(f"{a.name}: {type(e).__name__}: {e}")
            if is_write and env.get_db_hash() == before:
                write_noop_ids.append(a.action_id)  # 1c
        gold_hash = env.get_db_hash()
        env2 = fresh_env(env_ctor, task)  # 5a: second independent replay
        for a in actions:
            try:
                env2.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
            except Exception:
                pass
        replay_stable = env2.get_db_hash() == gold_hash

        # 2. the real DB evaluator on an empty trajectory; NL part by construction
        db_ri = EnvironmentEvaluator.calculate_reward(env_ctor, task, full_trajectory=[])
        nl_by_construction = 1.0 if (not nl or not nl_in_basis) else None  # None = the judge decides
        noop_needs_judge = int(float(db_ri.reward) == 1.0 and nl_by_construction is None)
        noop_reward = float(db_ri.reward) * (nl_by_construction if nl_by_construction is not None else 0.0)
        noop_pass = int(float(db_ri.reward) == 1.0 and nl_by_construction == 1.0)

        # 3. text pre-screen (inputs to 1d, 2k, 3d, 4d)
        text, unknown = scenario_text(task)
        ref_leaves = sorted({v for a in actions for v in leaves(a.arguments)})
        unstated = [v for v in ref_leaves if norm(v) not in text]
        in_unknown = [v for v in ref_leaves if unknown and norm(v) in unknown]
        ci_norm = [norm(c) for c in comm]
        nl_norm = norm(" ".join(nl))
        comm_covered = int(bool(comm) and all(c in nl_norm for c in ci_norm))
        nl_numbers = re.findall(r"\d+(?:\.\d+)?", nl_norm)
        issues = raw_tasks.get(task.id, {}).get("issues") or []

        rows.append({
            "task_id": task.id,
            "bench_commit": commit,
            "in_sample": int(task.id in sample_ids),
            "n_actions": len(actions),
            "n_read": counts["read"],
            "n_write": counts["write"],
            "n_generic": counts["generic"] + counts["think"],
            "n_unknown": counts["unknown"],
            "n_transfer": sum(1 for a in actions if a.name == TRANSFER),
            "action_names": "|".join(a.name for a in actions),
            "replay_errors": len(errors),
            "replay_error_msgs": " || ".join(errors),
            "init_db_hash": init_hash,
            "gold_db_hash": gold_hash,
            "db_changed": int(gold_hash != init_hash),
            "init_hash_stable": int(init_hash_stable),
            "replay_stable": int(replay_stable),
            "write_noop_ids": "|".join(write_noop_ids),
            "reward_basis": "|".join(basis),
            "nl_in_basis": nl_in_basis,
            "comm_in_basis": comm_in_basis,
            "comm_len": len(comm),
            "ci_min_chars": min((len(c) for c in comm), default=""),
            "ci_has_comma": int(any("," in c for c in comm)),
            "ci_numeric_only": int(bool(comm) and all(c.replace(".", "").isdigit() for c in comm)),
            "ci_in_user_scenario": int(any(c in text for c in ci_norm)),
            "nl_count": len(nl),
            "nl_numbers_in_user_scenario": "|".join(sorted({n for n in nl_numbers if n in text and len(n) >= 2})),
            "comm_covered_by_nl": comm_covered,
            "ref_args_unstated": "|".join(unstated),
            "ref_args_in_unknown_info": "|".join(in_unknown),
            "ids_missing_in_db": "|".join(ids_missing_in_db(text, users_db, orders_db, items_db, products_db, emails_db)),
            "gt_eligible": int(len(actions) > 0),
            "noop_db_reward": db_ri.reward,
            "noop_nl_by_construction": "" if nl_by_construction is None else nl_by_construction,
            "noop_needs_judge": noop_needs_judge,
            "noop_reward": noop_reward,
            "noop_pass": noop_pass,
            "positive_control": int(gold_hash == init_hash and (not nl or not nl_in_basis)),
            "upstream_issues": len(issues),
            "scan_date": date.today().isoformat(),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    noop = [r for r in rows if r["noop_pass"]]
    print(f"bench_commit={commit}  domain={DOMAIN} split={SPLIT}  tasks={n}")
    print(f"no-op pass by construction (empty trajectory, stock scorer, no judge needed): {len(noop)}/{n} ->", ", ".join(r["task_id"] for r in noop))
    print(f"no-op verdict depends on the judge (DB unchanged, assertions exist): {sum(r['noop_needs_judge'] for r in rows)}/{n} ->",
          ", ".join(r["task_id"] for r in rows if r["noop_needs_judge"]))
    print(f"db unchanged by reference replay: {sum(1 for r in rows if not r['db_changed'])}/{n}")
    print(f"reward_basis values: {sorted({r['reward_basis'] for r in rows})}; nl_in_basis={sum(r['nl_in_basis'] for r in rows)}; comm_in_basis={sum(r['comm_in_basis'] for r in rows)}")
    print(f"communicate_info non-empty: {sum(1 for r in rows if r['comm_len'])}/{n}; of which every string covered by an nl_assertion (string match): {sum(r['comm_covered_by_nl'] for r in rows)}")
    print(f"nl_assertions non-empty: {sum(1 for r in rows if r['nl_count'])}/{n}; total assertions: {sum(r['nl_count'] for r in rows)}")
    print(f"replay errors (1b): {sum(1 for r in rows if r['replay_errors'])} tasks ->",
          ", ".join(f"{r['task_id']}[{r['replay_error_msgs'][:80]}]" for r in rows if r["replay_errors"]) or "none")
    print(f"init hash unstable (3f): {sum(1 for r in rows if not r['init_hash_stable'])}/{n}; replay unstable (5a): {sum(1 for r in rows if not r['replay_stable'])}/{n}")
    print("WRITE actions that left the DB unchanged (1c):", [(r["task_id"], r["write_noop_ids"]) for r in rows if r["write_noop_ids"]] or "none")
    print(f"gt_eligible: {sum(r['gt_eligible'] for r in rows)}/{n}; positive_control == noop_pass everywhere:",
          all(r["positive_control"] == r["noop_pass"] for r in rows))
    print("communicate_info value present in user-scenario text (3d):", [r["task_id"] for r in rows if r["ci_in_user_scenario"]] or "none")
    print("nl numbers present in user-scenario text (3d):", [(r["task_id"], r["nl_numbers_in_user_scenario"]) for r in rows if r["nl_numbers_in_user_scenario"]] or "none")
    print("ids named in scenario but missing in db (4d):", [(r["task_id"], r["ids_missing_in_db"]) for r in rows if r["ids_missing_in_db"]] or "none")
    print("reference args named in unknown_info (1d):", [(r["task_id"], r["ref_args_in_unknown_info"]) for r in rows if r["ref_args_in_unknown_info"]] or "none")
    print("upstream-recorded issues:", [(r["task_id"], r["upstream_issues"]) for r in rows if r["upstream_issues"]])
    print("consistency checks:")
    print("  db_changed==0 but n_write>0 :", [r["task_id"] for r in rows if not r["db_changed"] and r["n_write"] > 0] or "none")
    print("  db_changed==1 but n_write==0:", [r["task_id"] for r in rows if r["db_changed"] and r["n_write"] == 0] or "none")
    print("  unknown tool names in actions:", [r["task_id"] for r in rows if r["n_unknown"]] or "none")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
