"""Live runs on the v2 benchmark (tasks v2 + scorer v2) through tau2's own runner (block2/PLAN.md H4, H5).

Same settings as the block-1 runs (results/runs/*.results.json info): agent and user
anthropic/claude-haiku-5-5 with llm_args {} (issue I5), seed 300, max_steps 200, max_errors 10,
substring communicate scorer, max_concurrency 3, timeout 900, workers 0 (threads only: the
overlay lives in this process). Output lands OUTSIDE the clone in results/v2/runs/<name>/.

  --part pass3   llm_agent, 20 sampled tasks x 3 trials      (~60 simulations)
  --part gt      llm_agent_gt, tasks with reference actions   (16 of the 20)
  --part both    pass3 then gt
  --dry-run      build everything, print the plan, call no model
  --tasks        default: sample.json task_ids

Run from inside tau2-bench:  uv run --no-sync python ../scripts/v2/run_v2.py --part both
SPENDS MONEY (agent + user simulator + NL judge). Block-2 ceiling $5 (PLAN.md §3.7).
"""

from __future__ import annotations

import argparse
import csv
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
OUT = ROOT / "results" / "v2" / "runs"

import scorer_v2 as s2  # noqa: E402
import tasks_v2  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.simulation import TextRunConfig  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType  # noqa: E402
from tau2.metrics.agent_metrics import compute_metrics  # noqa: E402
from tau2.runner.batch import _load_run_tasks, run_tasks  # noqa: E402

MODEL = "anthropic/claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50


def overlay_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def make_config(part: str, task_ids: list[str], trials: int, seed: int, save_to: str) -> TextRunConfig:
    return TextRunConfig(
        domain="airline",
        task_set_name=tasks_v2.TASK_SET_NAME,
        task_split_name="base",
        task_ids=task_ids,
        num_trials=trials if part == "pass3" else 1,
        seed=seed,
        agent="llm_agent" if part == "pass3" else "llm_agent_gt",
        llm_agent=MODEL,
        llm_args_agent={},
        user="user_simulator",
        llm_user=MODEL,
        llm_args_user={},
        max_steps=200,
        max_errors=10,
        max_concurrency=3,
        timeout=900,
        workers=0,
        communicate_scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING),
        save_to=save_to,
        log_level="ERROR",
    )


def usage_totals(results) -> dict:
    tot = {"agent_in": 0, "agent_out": 0, "user_in": 0, "user_out": 0, "agent_cost": 0.0, "user_cost": 0.0}
    for sim in results.simulations:
        tot["agent_cost"] += float(sim.agent_cost or 0.0)
        tot["user_cost"] += float(sim.user_cost or 0.0)
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


def run_part(part: str, task_ids: list[str], trials: int, seed: int, name: str, dry: bool) -> dict:
    cfg = make_config(part, task_ids, trials, seed, name)
    cfg.validate()
    tasks = _load_run_tasks(cfg)
    save_dir = OUT / name
    plan = {
        "part": part, "agent": cfg.agent, "task_set": cfg.task_set_name, "n_tasks": len(tasks), "task_ids": [t.id for t in tasks],
        "num_trials": cfg.num_trials, "seed": cfg.seed, "switches": vars(s2.SWITCHES).copy(), "judge": s2.JUDGE_MODEL,
        "nl_in_basis": all("NL_ASSERTION" in [str(b.value if hasattr(b, 'value') else b) for b in t.evaluation_criteria.reward_basis] for t in tasks),
        "save_dir": str(save_dir.relative_to(ROOT)), "overlay_commit": overlay_commit(),
    }
    print(json.dumps(plan, indent=1))
    if dry:
        return plan
    save_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    results = run_tasks(cfg, tasks, save_path=save_dir / "results.json", save_dir=save_dir, evaluation_type=EvaluationType.ALL, results_format="json")
    metrics = compute_metrics(results)
    summ = {
        **plan, "seconds": round(time.time() - t0), "n_sims": len(results.simulations),
        "infra_errors": sum(1 for s in results.simulations if str(s.termination_reason) .endswith("infrastructure_error") or getattr(s.termination_reason, "value", "") == "infrastructure_error"),
        "avg_reward": metrics.avg_reward, "pass_hat_k": {str(k): v for k, v in metrics.pass_hat_ks.items()},
        "usage": usage_totals(results),
        "judge": {**s2.JUDGE_COST, "own_estimate_usd": s2.JUDGE_COST["in_tokens"] / 1e6 * PRICE_IN + s2.JUDGE_COST["out_tokens"] / 1e6 * PRICE_OUT},
    }
    (save_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if s2.JUDGE_LOG:
        with open(save_dir / "judge_votes.csv", "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(s2.JUDGE_LOG[0]))
            w.writeheader()
            w.writerows(s2.JUDGE_LOG)
        s2.JUDGE_LOG.clear()
    print(json.dumps({k: summ[k] for k in ("n_sims", "infra_errors", "avg_reward", "pass_hat_k", "seconds")}, indent=1))
    return summ


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["pass3", "gt", "both"], default="both")
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--seed", type=int, default=300)
    ap.add_argument("--prefix", default="v2")
    ap.add_argument("--no-nl", action="store_true", help="switch nl_enforce off (not the pre-registered v2)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    task_ids = args.tasks or json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"]
    s2.install()
    s2.SWITCHES.set(True, True, not args.no_nl)
    s2.set_judge_cache(ROOT / "results" / "v2" / "judge_cache_live.json")
    tasks_v2.register()
    parts = ["pass3", "gt"] if args.part == "both" else [args.part]
    for part in parts:
        name = f"{args.prefix}_{'sample20_pass3' if part == 'pass3' else 'sample20_gt'}_haiku"
        run_part(part, task_ids, args.trials, args.seed, name, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
