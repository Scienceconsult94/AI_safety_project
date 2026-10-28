"""Live retail runs through tau2's own runner, stock scorer, judge model substituted (retail/PLAN.md §2).

Settings as in block 1: agent and user anthropic/claude-haiku-5-5 with llm_args {} (issue I5), seed 300, max_steps 200,
max_errors 10, substring communicate scorer (unused: COMMUNICATE is not in any retail basis), max_concurrency 3,
timeout 900, workers 0 (threads only: the judge overlay lives in this process), EvaluationType.ALL (the `tau2 run`
default at this commit). Output lands OUTSIDE the clone in results/retail/runs/<name>/ (results.json, summary.json,
judge_calls.json with every judge reply and its strict_ok flag).

  --part pass3   llm_agent, all 114 tasks x 3 trials   (342 simulations)
  --part gt      llm_agent_gt, the 112 tasks with reference actions, 1 trial
  --part all     pass3 then gt
  --task-ids ... restrict to the given tasks (smoke tests)
  --dry-run      build everything, print the plan, call no model

Run from inside tau2-bench:  uv run --no-sync python ../scripts/retail/run_retail.py --part all
SPENDS MONEY. Retail ceiling $15; stop if pass3 alone exceeds $10 (PLAN.md §4).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
OUT = ROOT / "results" / "retail" / "runs"

import judge_overlay as jo  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.simulation import TextRunConfig  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType  # noqa: E402
from tau2.metrics.agent_metrics import compute_metrics  # noqa: E402
from tau2.runner.batch import _load_run_tasks, run_tasks  # noqa: E402

MODEL = "anthropic/claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50
PARTS = {
    "pass3": {"agent": "llm_agent", "trials": 3, "name": "retail_pass3_haiku"},
    "gt": {"agent": "llm_agent_gt", "trials": 1, "name": "retail_gt_haiku"},
}


def make_config(agent: str, task_ids, trials: int, seed: int, save_to: str) -> TextRunConfig:
    return TextRunConfig(
        domain="retail", task_split_name="base", task_ids=task_ids, num_trials=trials, seed=seed,
        agent=agent, llm_agent=MODEL, llm_args_agent={}, user="user_simulator", llm_user=MODEL, llm_args_user={},
        max_steps=200, max_errors=10, max_concurrency=3, timeout=900, workers=0,
        communicate_scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING), save_to=save_to, log_level="ERROR",
    )


def usage_totals(results) -> dict:
    tot = {"agent_in": 0, "agent_out": 0, "user_in": 0, "user_out": 0}
    for sim in results.simulations:
        for m in sim.messages or []:
            u = getattr(m, "usage", None)
            if not u:
                continue
            side = "agent" if m.role == "assistant" else "user" if m.role == "user" else None
            if side:
                tot[f"{side}_in"] += int(u.get("prompt_tokens", 0) or 0)
                tot[f"{side}_out"] += int(u.get("completion_tokens", 0) or 0)
    tot["own_estimate_usd"] = (tot["agent_in"] + tot["user_in"]) / 1e6 * PRICE_IN + (tot["agent_out"] + tot["user_out"]) / 1e6 * PRICE_OUT
    return tot


def overlay_commit() -> dict:
    try:
        c = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "scripts/retail", "retail"], text=True).strip())
        bench = subprocess.check_output(["git", "-C", str(ROOT / "tau2-bench"), "rev-parse", "HEAD"], text=True).strip()
        bench_dirty = bool(subprocess.check_output(["git", "-C", str(ROOT / "tau2-bench"), "status", "--porcelain"], text=True).strip())
        return {"overlay_commit": c, "overlay_dirty": dirty, "bench_commit": bench, "bench_dirty": bench_dirty}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def run_part(part: str, task_ids, seed: int, dry: bool) -> dict:
    P = PARTS[part]
    cfg = make_config(P["agent"], task_ids, P["trials"], seed, P["name"])
    cfg.validate()
    tasks = _load_run_tasks(cfg)
    save_dir = OUT / P["name"]
    plan = {"part": part, "agent": cfg.agent, "domain": cfg.domain, "n_tasks": len(tasks), "task_ids": [t.id for t in tasks], "num_trials": cfg.num_trials,
            "seed": cfg.seed, "evaluation_type": "all", "judge": jo.provenance(), **overlay_commit(), "save_dir": str(save_dir.relative_to(ROOT)),
            "nl_in_basis_tasks": sum(1 for t in tasks if any(str(getattr(b, "value", b)) == "NL_ASSERTION" for b in t.evaluation_criteria.reward_basis)),
            "tasks_with_assertions": sum(1 for t in tasks if t.evaluation_criteria.nl_assertions)}
    print(json.dumps({k: v for k, v in plan.items() if k != "task_ids"}, indent=1, default=str))
    if dry:
        return plan
    save_dir.mkdir(parents=True, exist_ok=True)
    jo.reset_totals()
    t0 = time.time()
    results = run_tasks(cfg, tasks, save_path=save_dir / "results.json", save_dir=save_dir, evaluation_type=EvaluationType.ALL, results_format="json")
    metrics = compute_metrics(results)
    calls = jo.drain()
    summ = {**plan, "seconds": round(time.time() - t0), "n_sims": len(results.simulations),
            "infra_errors": sum(1 for s in results.simulations if str(getattr(s.termination_reason, "value", s.termination_reason)) == "infrastructure_error"),
            "avg_reward": metrics.avg_reward, "pass_hat_k": {str(k): v for k, v in metrics.pass_hat_ks.items()},
            "usage": usage_totals(results), "judge": {**plan["judge"], **jo.totals(), "n_logged_calls": len(calls)}}
    (save_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    (save_dir / "judge_calls.json").write_text(json.dumps(calls, indent=0, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: summ[k] for k in ("n_sims", "infra_errors", "avg_reward", "pass_hat_k", "seconds", "usage", "judge")}, indent=1, default=str))
    return summ


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=[*PARTS, "all"], default="all")
    ap.add_argument("--seed", type=int, default=300)
    ap.add_argument("--task-ids", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    jo.install()
    ids = args.task_ids or json.loads((ROOT / "retail" / "sample.json").read_text(encoding="utf-8"))["task_ids"]
    for part in (list(PARTS) if args.part == "all" else [args.part]):
        run_part(part, ids, args.seed, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
