"""Static no-op scan and pre-screen over all airline tasks of tau2-bench (pinned tag v2.0.0).

For every task in the `base` split this script:
  1. builds a fresh airline environment exactly as `EnvironmentEvaluator` does,
     records the initial DB hash, replays `evaluation_criteria.actions` (the
     reference trajectory) action by action and records the resulting "gold" DB
     hash; a second independent replay checks determinism of the target state;
  2. runs the real evaluators on an EMPTY trajectory - an agent that neither
     speaks nor calls tools - with the substring communicate scorer, i.e. the
     "empty answer" probe of the audit checklist;
  3. records READ / WRITE / GENERIC counts of the reference actions, WRITE actions
     that left the DB unchanged, the number of `communicate_info` strings and of
     `nl_assertions`, and the text pre-screen columns of checklist.md
     (reference argument values not stated in the user scenario, ids named in the
     scenario but missing from the DB, communicate_info values present in the
     scenario text, short / numeric communicate_info strings).

No LLM is called. Output: results/static_scan.csv plus a summary on stdout.
Run from inside the tau2-bench checkout so tau2 resolves its data directory:
    cd tau2-bench && uv run --no-sync python ../static_scan.py
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

from tau2.data_model.semantic_communication import (  # noqa: E402
    CommunicateScorer,
    CommunicateScoring,
)
from tau2.environment.toolkit import ToolType  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parent
BENCH = ROOT / "tau2-bench"
OUT = ROOT / "results" / "static_scan.csv"
DOMAIN = "airline"
SPLIT = "base"


def bench_commit() -> str:
    return subprocess.check_output(
        ["git", "-C", str(BENCH), "rev-parse", "HEAD"], text=True
    ).strip()


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
    """Sets of user ids, reservation ids and flight numbers in the loaded DB."""
    db = env.tools.db

    def ids(coll, key):
        if hasattr(coll, "keys"):
            return set(coll.keys())
        return {getattr(x, key) for x in coll}

    return ids(db.users, "user_id"), ids(db.reservations, "reservation_id"), ids(db.flights, "flight_number")


def ids_missing_in_db(raw_text: str, users: set, reservations: set, flights: set) -> list[str]:
    """Ids named in the scenario text that do not exist in the DB (input to check 4d)."""
    missing = {m for m in re.findall(r"\b[a-z]+_[a-z]+_\d{4}\b", raw_text) if m not in users}
    missing |= {m.upper() for m in re.findall(r"\bhat\d{3}\b", raw_text) if m.upper() not in flights}
    for m in re.findall(r"(?<![a-z0-9])[a-z0-9]{6}(?![a-z0-9])", raw_text):
        if re.search(r"\d", m) and not m.isdigit() and m.upper() not in reservations:
            missing.add(m.upper())
    return sorted(missing)


def main() -> int:
    commit = bench_commit()
    sample_ids = set(json.load(open(ROOT / "sample.json", encoding="utf-8"))["task_ids"])
    env_ctor = registry.get_env_constructor(DOMAIN)
    tasks = registry.get_tasks_loader(DOMAIN)(SPLIT)
    substring = CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)
    users_db, res_db, flights_db = db_id_sets(env_ctor())

    rows = []
    for task in tasks:
        ec = task.evaluation_criteria
        actions = list(ec.actions or []) if ec else []
        comm = list(ec.communicate_info or []) if ec else []
        nl = list(ec.nl_assertions or []) if ec else []
        basis = [str(getattr(b, "value", b)) for b in (ec.reward_basis or [])] if ec else []

        # 1. reference replay, same code path as the evaluator, action by action
        env = fresh_env(env_ctor, task)
        init_hash, init_user_hash = env.get_db_hash(), env.get_user_db_hash()
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
        gold_hash, gold_user_hash = env.get_db_hash(), env.get_user_db_hash()
        env2 = fresh_env(env_ctor, task)  # 5a: second independent replay
        for a in actions:
            try:
                env2.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
            except Exception:
                pass
        replay_stable = env2.get_db_hash() == gold_hash

        # 2. the real evaluators on an empty trajectory (agent does nothing)
        db_ri = EnvironmentEvaluator.calculate_reward(env_ctor, task, full_trajectory=[])
        comm_ri = CommunicateEvaluator.calculate_reward(task, [], scoring=substring)
        noop_reward = float(db_ri.reward) * float(comm_ri.reward)

        # 3. text pre-screen (inputs to 1d, 2g, 2i, 3d, 4d)
        text, unknown = scenario_text(task)
        ci_norm = [norm(c) for c in comm]
        ref_leaves = sorted({v for a in actions for v in leaves(a.arguments)})
        unstated = [v for v in ref_leaves if norm(v) not in text]
        in_unknown = [v for v in ref_leaves if unknown and norm(v) in unknown]

        rows.append(
            {
                "task_id": task.id,
                "bench_commit": commit,
                "in_sample20": int(task.id in sample_ids),
                "n_actions": len(actions),
                "n_read": counts["read"],
                "n_write": counts["write"],
                "n_generic": counts["generic"] + counts["think"],
                "n_unknown": counts["unknown"],
                "action_names": "|".join(a.name for a in actions),
                "replay_errors": len(errors),
                "replay_error_msgs": " || ".join(errors),
                "init_db_hash": init_hash,
                "gold_db_hash": gold_hash,
                "db_changed": int(gold_hash != init_hash),
                "user_db_changed": int(gold_user_hash != init_user_hash),
                "init_hash_stable": int(init_hash_stable),
                "replay_stable": int(replay_stable),
                "write_noop_ids": "|".join(write_noop_ids),
                "n_book_reservation": sum(1 for a in actions if a.name == "book_reservation"),
                "comm_len": len(comm),
                "ci_min_chars": min((len(c) for c in comm), default=""),
                "ci_has_comma": int(any("," in c for c in comm)),
                "ci_numeric_only": int(bool(comm) and all(c.replace(".", "").isdigit() for c in comm)),
                "ci_in_user_scenario": int(any(c in text for c in ci_norm)),
                "ref_args_unstated": "|".join(unstated),
                "ref_args_in_unknown_info": "|".join(in_unknown),
                "ids_missing_in_db": "|".join(ids_missing_in_db(text, users_db, res_db, flights_db)),
                "gt_eligible": int(len(actions) > 0),
                "nl_count": len(nl),
                "reward_basis": "|".join(basis),
                "noop_db_reward": db_ri.reward,
                "noop_comm_reward": comm_ri.reward,
                "noop_reward": noop_reward,
                "noop_pass": int(noop_reward == 1.0),
                "positive_control": int(gold_hash == init_hash and len(comm) == 0),
                "scan_date": date.today().isoformat(),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    noop = [r for r in rows if r["noop_pass"]]
    print(f"bench_commit={commit}  domain={DOMAIN} split={SPLIT}  tasks={n}")
    print(f"no-op pass (empty trajectory gets reward 1.0): {len(noop)}/{n}")
    print("  task ids:", ", ".join(r["task_id"] for r in noop))
    print(f"  of which in sample20: {sum(r['in_sample20'] for r in noop)}/{sum(r['in_sample20'] for r in rows)}")
    print(f"db unchanged by reference replay: {sum(1 for r in rows if not r['db_changed'])}/{n}")
    print(f"communicate_info empty: {sum(1 for r in rows if r['comm_len'] == 0)}/{n}")
    print(f"replay errors (1b): {sum(1 for r in rows if r['replay_errors'])} tasks ->",
          ", ".join(f"{r['task_id']}[{r['replay_error_msgs'][:80]}]" for r in rows if r["replay_errors"]) or "none")
    print(f"init hash unstable (3f): {sum(1 for r in rows if not r['init_hash_stable'])}/{n}")
    print(f"replay unstable (5a): {sum(1 for r in rows if not r['replay_stable'])}/{n}")
    print("WRITE actions that left the DB unchanged (1c):",
          [(r["task_id"], r["write_noop_ids"]) for r in rows if r["write_noop_ids"]] or "none")
    print(f"gt_eligible: {sum(r['gt_eligible'] for r in rows)}/{n}; positive_control == noop_pass everywhere:",
          all(r["positive_control"] == r["noop_pass"] for r in rows))
    print("communicate_info value present in user-scenario text (3d):",
          [r["task_id"] for r in rows if r["ci_in_user_scenario"]] or "none")
    print("ids named in scenario but missing in db (4d):",
          [(r["task_id"], r["ids_missing_in_db"]) for r in rows if r["ids_missing_in_db"]] or "none")
    print("reference args named in unknown_info (1d):",
          [(r["task_id"], r["ref_args_in_unknown_info"]) for r in rows if r["ref_args_in_unknown_info"]] or "none")
    print("tasks with >1 book_reservation (2h):", [r["task_id"] for r in rows if r["n_book_reservation"] > 1] or "none")
    print("consistency checks:")
    print("  db_changed==0 but n_write>0 :", [r["task_id"] for r in rows if not r["db_changed"] and r["n_write"] > 0] or "none")
    print("  db_changed==1 but n_write==0:", [r["task_id"] for r in rows if r["db_changed"] and r["n_write"] == 0] or "none")
    print("  noop_pass != (db unchanged and comm empty):",
          [r["task_id"] for r in rows if r["noop_pass"] != int((not r["db_changed"]) and r["comm_len"] == 0)] or "none")
    print("  unknown tool names in actions:", [r["task_id"] for r in rows if r["n_unknown"]] or "none")
    print("  reward_basis values:", sorted({r["reward_basis"] for r in rows}))
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
