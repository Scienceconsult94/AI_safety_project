"""Null-agent table for every tau2-bench domain: what the stock scorer awards to an agent that does nothing.

For every task of every registered task set the EMPTY trajectory (only the task's own initial message history, no agent
turn, no tool call) is pushed through the stock evaluators that the task's `reward_basis` names:
  DB / ENV_ASSERTION   EnvironmentEvaluator.calculate_reward (gold = initial state + reference actions; predicted = initial state)
  ACTION               ActionEvaluator.calculate_reward       (fails whenever the reference lists an action)
  COMMUNICATE          CommunicateEvaluator.calculate_reward, substring scorer (fails whenever communicate_info is non-empty)
  NL_ASSERTION         needs an LLM judge: not called here. A task whose deterministic components pass and whose reward
                       still depends on the judge is counted separately ("judge-dependent"); for retail the live verdicts
                       of results/retail/noop_judge_probe.csv are cross-referenced when present.
Positive controls per task: the reference actions replay without error (DB domains) and the reference end state satisfies
the task's own env_assertions (telecom); a task that fails its own reference is reported as such.

Outputs: results/null_agent/tau2_null_agent.csv (one row per task) and tau2_null_agent.md (per-domain table with Wilson 95% CIs).
Usage (from tau2-bench/, its venv):  uv run --no-sync python ../scripts/null_agent/tau2_null_agent.py [--sets airline,retail,...]
No model call, nothing under tau2-bench/ is modified. Read-only on the clone.
"""

from __future__ import annotations

import argparse
import csv
import math
import subprocess
import sys
import time
from copy import deepcopy
from datetime import date
from pathlib import Path

from loguru import logger

from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.tasks import RewardType  # noqa: E402
from tau2.evaluator.evaluator_action import ActionEvaluator  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "null_agent"
BENCH = ROOT / "tau2-bench"

# (label, domain key for the environment, task-set key, split name)
SETS = [
    ("airline base", "airline", "airline", "base"),
    ("retail base", "retail", "retail", "base"),
    ("telecom base", "telecom", "telecom", "base"),
    ("telecom full", "telecom", "telecom_full", None),
    ("banking_knowledge", "banking_knowledge", "banking_knowledge", None),
    ("intake base", "intake", "intake", "base"),
]
COLS = ["set", "domain", "split", "task_id", "reward_basis", "n_actions", "n_env_assertions", "nl_count", "comm_len",
        "null_db_match", "null_env_assert_reward", "null_action_reward", "null_comm_reward", "null_det_reward",
        "nl_needs_judge", "null_pass_certain", "null_pass_if_judge_passes", "gold_replay_errors", "gold_assertions_fail",
        "error", "bench_commit", "scan_date"]


def bench_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=BENCH, capture_output=True, text=True, check=True).stdout.strip()


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def gold_controls(env_ctor, task) -> tuple[int, int]:
    """Replay the reference on a fresh environment: (number of raising reference actions, number of failing env_assertions)."""
    ini = task.initial_state
    env = env_ctor()
    env.set_state(initialization_data=ini.initialization_data if ini else None,
                  initialization_actions=ini.initialization_actions if ini else None,
                  message_history=list(ini.message_history or []) if ini else [], strict=True)
    errors = 0
    for a in (task.evaluation_criteria.actions or []) if task.evaluation_criteria else []:
        try:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception:
            errors += 1
        env.sync_tools()  # the orchestrator syncs agent and user state after every turn; make_tool_call itself does not
    fails = 0
    for ea in (task.evaluation_criteria.env_assertions or []) if task.evaluation_criteria else []:
        try:
            if not env.run_env_assertion(ea, raise_assertion_error=False):
                fails += 1
        except Exception:
            fails += 1
    return errors, fails


def one_task(env_ctor, task, label: str, domain: str, split: str | None, commit: str) -> dict:
    ec = task.evaluation_criteria
    basis = list(ec.reward_basis) if ec and ec.reward_basis else []
    basis_s = "|".join(str(getattr(b, "value", b)) for b in basis)
    traj = list(task.initial_state.message_history or []) if task.initial_state else []
    row = {"set": label, "domain": domain, "split": split or "", "task_id": task.id, "reward_basis": basis_s,
           "n_actions": len(ec.actions or []) if ec else 0, "n_env_assertions": len(ec.env_assertions or []) if ec else 0,
           "nl_count": len(ec.nl_assertions or []) if ec else 0, "comm_len": len(ec.communicate_info or []) if ec else 0,
           "null_db_match": "", "null_env_assert_reward": "", "null_action_reward": "", "null_comm_reward": "",
           "null_det_reward": "", "nl_needs_judge": 0, "null_pass_certain": 0, "null_pass_if_judge_passes": 0,
           "gold_replay_errors": "", "gold_assertions_fail": "", "error": "", "bench_commit": commit, "scan_date": date.today().isoformat()}
    try:
        det = 1.0
        if RewardType.DB in basis or RewardType.ENV_ASSERTION in basis:
            ri = EnvironmentEvaluator.calculate_reward(env_ctor, task, full_trajectory=traj)
            row["null_db_match"] = int(bool(ri.db_check.db_match)) if ri.db_check else ""
            ea_reward = 1.0
            for c in ri.env_assertions or []:
                ea_reward *= c.reward
            row["null_env_assert_reward"] = ea_reward
            if RewardType.DB in basis:
                det *= float(ri.db_check.db_reward) if ri.db_check else 1.0
            if RewardType.ENV_ASSERTION in basis:
                det *= ea_reward
        if RewardType.ACTION in basis:
            r = ActionEvaluator.calculate_reward(task=task, full_trajectory=traj).reward
            row["null_action_reward"] = r
            det *= float(r)
        if RewardType.COMMUNICATE in basis:
            r = CommunicateEvaluator.calculate_reward(task=task, full_trajectory=traj, scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)).reward
            row["null_comm_reward"] = r
            det *= float(r)
        row["null_det_reward"] = det
        needs_judge = int(RewardType.NL_ASSERTION in basis and row["nl_count"] > 0)
        row["nl_needs_judge"] = needs_judge
        row["null_pass_certain"] = int(det == 1.0 and not needs_judge)
        row["null_pass_if_judge_passes"] = int(det == 1.0 and needs_judge)
        row["gold_replay_errors"], row["gold_assertions_fail"] = gold_controls(env_ctor, task)
    except Exception as e:  # keep the row, record the failure
        row["error"] = f"{type(e).__name__}: {str(e)[:200]}"
    return row


def retail_judge_crossref() -> dict[str, str]:
    """task_id -> live judge verdict on the empty trajectory (results/retail/noop_judge_probe.csv), when present."""
    p = ROOT / "results" / "retail" / "noop_judge_probe.csv"
    if not p.exists():
        return {}
    out = {}
    with open(p, encoding="utf-8", newline="") as fp:
        for r in csv.DictReader(fp):
            if r.get("probe", "") in ("2b", "empty", "noop") or "probe" not in r:
                out[r["task_id"]] = r.get("reward", r.get("nl_reward", ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="", help="comma-separated labels (default: all)")
    args = ap.parse_args()
    logger.remove()
    logger.add(sys.stderr, level="ERROR")
    OUT.mkdir(parents=True, exist_ok=True)
    commit = bench_commit()
    want = {s.strip() for s in args.sets.split(",") if s.strip()}
    rows: list[dict] = []
    for label, domain, tasks_key, split in SETS:
        if want and label not in want:
            continue
        t0 = time.time()
        try:
            env_ctor = registry.get_env_constructor(domain)
            tasks = registry.get_tasks_loader(tasks_key)(split) if split else registry.get_tasks_loader(tasks_key)()
        except Exception as e:
            print(f"{label}: could not load ({type(e).__name__}: {str(e)[:160]})")
            continue
        for task in tasks:
            rows.append(one_task(env_ctor, task, label, domain, split, commit))
        print(f"{label}: {len(tasks)} tasks in {time.time() - t0:.0f}s")
    with open(OUT / "tau2_null_agent.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    judge = retail_judge_crossref()
    L = ["# Null agent on tau2-bench: what the stock scorer awards to an agent that does nothing", "",
         f"tau2-bench commit `{commit}`, scan date {date.today().isoformat()}. Trajectory = the task's initial message history only "
         "(no agent turn, no tool call). Deterministic components (DB hash, env_assertions, ACTION, COMMUNICATE) are the stock "
         "evaluators; NL_ASSERTION needs an LLM judge and is not called: a task whose deterministic part passes and whose reward "
         "then depends on the judge is counted as judge-dependent. Wilson 95% intervals.", "",
         "| task set | tasks | reward basis | null passes for certain | 95% CI | judge-dependent | reference raises on replay or fails its own assertions | errors |",
         "|---|---|---|---|---|---|---|---|"]
    for label, *_ in SETS:
        sub = [r for r in rows if r["set"] == label]
        if not sub:
            continue
        n = len(sub)
        k = sum(r["null_pass_certain"] for r in sub)
        j = sum(r["null_pass_if_judge_passes"] for r in sub)
        bad_gold = sum(1 for r in sub if (r["gold_replay_errors"] not in ("", 0)) or (r["gold_assertions_fail"] not in ("", 0)))
        errs = sum(1 for r in sub if r["error"])
        bases = sorted({r["reward_basis"] for r in sub})
        lo, hi = wilson(k, n)
        if errs == n:
            L.append(f"| {label} | {n} | {', '.join(bases)} | n/a | n/a | n/a | n/a | {errs} (environment not constructible in the pinned venv: {sub[0]['error'][:60]}) |")
            continue
        L.append(f"| {label} | {n} | {', '.join(bases)} | {k} ({100 * k / n:.1f}%) | {100 * lo:.1f}–{100 * hi:.1f}% | {j} | {bad_gold} | {errs} |")
    L += ["", "Reading: a task the null agent passes for certain cannot distinguish an agent that solved it from one that did "
          "nothing; the share is the floor that any reported pass rate on that set must be read against. Judge-dependent tasks "
          "pass or fail with the judge's reading of the empty transcript."]
    ret = [r for r in rows if r["set"] == "retail base" and r["null_pass_if_judge_passes"]]
    if ret and judge:
        passed = [r["task_id"] for r in ret if judge.get(r["task_id"], "") in ("1", "1.0")]
        L += ["", f"Retail cross-reference: of the {len(ret)} judge-dependent tasks, the live judge probe (results/retail/noop_judge_probe.csv) "
              f"passed the empty transcript in {len(passed)} ({', '.join(passed) if passed else 'none'})."]
    for label, *_ in SETS:
        sub = [r for r in rows if r["set"] == label and r["null_pass_certain"]]
        if sub and len(sub) <= 60:
            L += ["", f"{label}, tasks the null agent passes for certain: " + ", ".join(str(r["task_id"]) for r in sub)]
    bad = [r for r in rows if (r["gold_replay_errors"] not in ("", 0)) or (r["gold_assertions_fail"] not in ("", 0))]
    if bad:
        L += ["", f"Reference actions that raise on replay (intended negative steps included; the domain audits decide which) or reference end states failing the task's own env_assertions ({len(bad)} tasks; first 60): " + ", ".join(
            f"{r['set'].split()[0]}/{r['task_id']} (replay errors {r['gold_replay_errors']}, failing assertions {r['gold_assertions_fail']})" for r in bad[:60])]
    errs = [r for r in rows if r["error"]]
    if errs:
        L += ["", f"Rows with evaluation errors ({len(errs)}; first 20): " + "; ".join(f"{r['set']}/{r['task_id']}: {r['error'][:80]}" for r in errs[:20])]
    (OUT / "tau2_null_agent.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
