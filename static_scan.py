"""Static no-op scan over all airline tasks of tau2-bench (pinned tag v2.0.0).

For every task in the `base` split this script:
  1. builds a fresh airline environment exactly as `EnvironmentEvaluator` does,
     records the initial DB hash, replays `evaluation_criteria.actions` (the
     reference trajectory) and records the resulting "gold" DB hash;
  2. runs the real evaluators on an EMPTY trajectory - an agent that neither
     speaks nor calls tools - with the substring communicate scorer, i.e. the
     "empty answer" probe of the audit checklist;
  3. records READ / WRITE / GENERIC counts of the reference actions, the number
     of `communicate_info` strings and of `nl_assertions`.

No LLM is called. Output: results/static_scan.csv plus a summary on stdout.
Run from inside the tau2-bench checkout so tau2 resolves its data directory:
    cd tau2-bench && uv run --no-sync python ../static_scan.py
"""

from __future__ import annotations

import csv
import json
import os
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


def main() -> int:
    commit = bench_commit()
    sample_ids = set(json.load(open(ROOT / "sample.json", encoding="utf-8"))["task_ids"])
    env_ctor = registry.get_env_constructor(DOMAIN)
    tasks = registry.get_tasks_loader(DOMAIN)(SPLIT)
    substring = CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)

    rows = []
    for task in tasks:
        ec = task.evaluation_criteria
        actions = list(ec.actions or []) if ec else []
        comm = list(ec.communicate_info or []) if ec else []
        nl = list(ec.nl_assertions or []) if ec else []
        basis = [str(getattr(b, "value", b)) for b in (ec.reward_basis or [])] if ec else []

        # 1. reference replay, same code path as the evaluator
        env = fresh_env(env_ctor, task)
        init_hash, init_user_hash = env.get_db_hash(), env.get_user_db_hash()
        # determinism of the initial state: a second fresh env must hash identically
        init_hash_stable = fresh_env(env_ctor, task).get_db_hash() == init_hash
        counts = {"read": 0, "write": 0, "generic": 0, "think": 0, "unknown": 0}
        errors = []
        for a in actions:
            try:
                tt = env.tools.tool_type(a.name)
                counts[tt.value if isinstance(tt, ToolType) else str(tt)] += 1
            except Exception:
                counts["unknown"] += 1
            try:
                env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
            except Exception as e:  # the evaluator only logs a warning here
                errors.append(f"{a.name}: {type(e).__name__}: {e}")
        gold_hash, gold_user_hash = env.get_db_hash(), env.get_user_db_hash()

        # 2. the real evaluators on an empty trajectory (agent does nothing)
        db_ri = EnvironmentEvaluator.calculate_reward(env_ctor, task, full_trajectory=[])
        comm_ri = CommunicateEvaluator.calculate_reward(task, [], scoring=substring)
        noop_reward = float(db_ri.reward) * float(comm_ri.reward)

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
                "comm_len": len(comm),
                "nl_count": len(nl),
                "reward_basis": "|".join(basis),
                "noop_db_reward": db_ri.reward,
                "noop_comm_reward": comm_ri.reward,
                "noop_reward": noop_reward,
                "noop_pass": int(noop_reward == 1.0),
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
    print(f"communicate_info empty: {sum(1 for r in rows if r['comm_len']==0)}/{n}")
    print(f"replay errors: {sum(1 for r in rows if r['replay_errors'])} tasks ->",
          ", ".join(f"{r['task_id']}[{r['replay_error_msgs'][:80]}]" for r in rows if r["replay_errors"]) or "none")
    print(f"init hash unstable: {sum(1 for r in rows if not r['init_hash_stable'])}/{n}")
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
