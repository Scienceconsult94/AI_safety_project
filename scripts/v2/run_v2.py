"""Live runs on the v2 benchmark (tasks v2 + scorer v2) through tau2's own runner (block2/PLAN.md H4, H5).

Same settings as the block-1 runs (results/runs/*.results.json info): agent and user
anthropic/claude-haiku-5-5 with llm_args {} (issue I5), seed 300, max_steps 200, max_errors 10,
substring communicate scorer, max_concurrency 3, timeout 900, workers 0 (threads only: the
overlay lives in this process). Output lands OUTSIDE the clone in results/v2/runs/<name>/.
The dry run also diffs the run Info against the block-1 Info (design review E7).

  --part pass3   llm_agent, 20 sampled tasks x 3 trials      (~60 simulations)
  --part gt      llm_agent_gt, tasks with reference actions   (16 of the 20), 1 trial
  --part gt3     llm_agent_gt on the three text-fixed tasks 7, 32, 44, 3 trials (H4 by mechanism)
  --part all     pass3, gt, gt3
  --part pass3_rest30, gt_rest30   the same two runs on the 30 tasks outside the sample (airline_full/PLAN.md, Q5)
  --part cf32_A, cf32_B            llm_agent_gt on task 32, 10 trials: the v2.1 text, and the same text without
                                   its payment sentence (airline_full/PLAN.md, Q3)
  --dry-run      build everything, print the plan and the Info diff, call no model

Run from inside tau2-bench:  uv run --no-sync python ../scripts/v2/run_v2.py --part all
SPENDS MONEY (agent + user simulator + NL judge). Block-2 ceiling $5 (PLAN.md §3.7).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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
BLOCK1_INFO = ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json"

import scorer_v2 as s2  # noqa: E402
import tasks_v2  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.simulation import TextRunConfig  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType  # noqa: E402
from tau2.metrics.agent_metrics import compute_metrics  # noqa: E402
from tau2.runner.batch import _load_run_tasks, run_tasks  # noqa: E402

MODEL = "anthropic/claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50
PARTS = {
    "pass3": {"agent": "llm_agent", "trials": 3, "tasks": None, "name": "v2_sample20_pass3_haiku"},
    "gt": {"agent": "llm_agent_gt", "trials": 1, "tasks": None, "name": "v2_sample20_gt_haiku"},
    "gt3": {"agent": "llm_agent_gt", "trials": 3, "tasks": ["7", "32", "44"], "name": "v2_gt3_haiku"},
    # airline_full/PLAN.md: the rest of the domain (Q5) and the task-32 counterfactual (Q3)
    "pass3_rest30": {"agent": "llm_agent", "trials": 3, "tasks": "rest", "name": "v2_rest30_pass3_haiku"},
    "gt_rest30": {"agent": "llm_agent_gt", "trials": 1, "tasks": "rest", "name": "v2_rest30_gt_haiku"},
    "cf32_A": {"agent": "llm_agent_gt", "trials": 10, "tasks": ["32"], "name": "v2_cf32_A_gt_haiku"},
    "cf32_B": {"agent": "llm_agent_gt", "trials": 10, "tasks": ["32"], "name": "v2_cf32_B_gt_haiku",
               "drop_sentence": "Any charge or refund should go to your Visa credit card ending in 1777."},
}
BLOCK2_PARTS = ("pass3", "gt", "gt3")  # what --part all runs (block 2 as pre-registered)


def drop_sentence(task, sentence: str):
    """A copy of `task` whose task_instructions lack `sentence` (must occur exactly once); nothing else changes."""
    instr = task.user_scenario.instructions
    text = instr.task_instructions
    assert text.count(sentence) == 1, f"task {task.id}: the sentence must occur exactly once"
    i = text.index(sentence)
    new = (text[:i].rstrip(" ") + text[i + len(sentence):].lstrip(" ")).strip()
    us = task.user_scenario.model_copy(update={"instructions": instr.model_copy(update={"task_instructions": new})})
    return task.model_copy(update={"user_scenario": us})


def make_config(agent: str, task_ids: list[str], trials: int, seed: int, save_to: str) -> TextRunConfig:
    return TextRunConfig(
        domain="airline", task_set_name=tasks_v2.TASK_SET_NAME, task_split_name="base", task_ids=task_ids,
        num_trials=trials, seed=seed, agent=agent, llm_agent=MODEL, llm_args_agent={},
        user="user_simulator", llm_user=MODEL, llm_args_user={},
        max_steps=200, max_errors=10, max_concurrency=3, timeout=900, workers=0,
        communicate_scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING), save_to=save_to, log_level="ERROR",
    )


def info_diff(cfg: TextRunConfig) -> dict:
    """Fields of the block-1 Info that this config would change (excluding the task set and language pins)."""
    b1 = json.loads(BLOCK1_INFO.read_text(encoding="utf-8"))["info"]
    mine = {"max_steps": cfg.max_steps, "max_errors": cfg.max_errors, "seed": cfg.seed, "language": cfg.language,
            "agent_llm": cfg.llm_agent, "agent_llm_args": cfg.llm_args_agent, "user_llm": cfg.llm_user, "user_llm_args": cfg.llm_args_user,
            "user_impl": cfg.user, "communicate_scoring": cfg.communicate_scoring.model_dump(mode="json")}
    theirs = {"max_steps": b1["max_steps"], "max_errors": b1["max_errors"], "seed": b1["seed"], "language": b1["language"],
              "agent_llm": b1["agent_info"]["llm"], "agent_llm_args": b1["agent_info"]["llm_args"], "user_llm": b1["user_info"]["llm"],
              "user_llm_args": b1["user_info"]["llm_args"], "user_impl": b1["user_info"]["implementation"], "communicate_scoring": b1["communicate_scoring"]}
    return {k: {"block1": theirs[k], "v2": mine[k]} for k in mine if mine[k] != theirs[k]}


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


def run_part(part: str, sample_ids: list[str], rest_ids: list[str], seed: int, dry: bool) -> dict:
    P = PARTS[part]
    task_ids = rest_ids if P["tasks"] == "rest" else P["tasks"] or sample_ids
    cfg = make_config(P["agent"], task_ids, P["trials"], seed, P["name"])
    cfg.validate()
    tasks = _load_run_tasks(cfg)
    if P.get("drop_sentence"):
        tasks = [drop_sentence(t, P["drop_sentence"]) for t in tasks]
    save_dir = OUT / P["name"]
    plan = {"part": part, "agent": cfg.agent, "task_set": cfg.task_set_name, "n_tasks": len(tasks), "task_ids": [t.id for t in tasks],
            "num_trials": cfg.num_trials, "seed": cfg.seed, "provenance": s2.provenance(),
            "nl_in_basis": all(any(str(getattr(b, "value", b)) == "NL_ASSERTION" for b in t.evaluation_criteria.reward_basis) for t in tasks),
            "info_diff_vs_block1": info_diff(cfg), "save_dir": str(save_dir.relative_to(ROOT))}
    if part.startswith("cf32"):
        plan["task_instructions"] = tasks[0].user_scenario.instructions.task_instructions
    print(json.dumps(plan, indent=1, default=str))
    if dry:
        return plan
    save_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    results = run_tasks(cfg, tasks, save_path=save_dir / "results.json", save_dir=save_dir, evaluation_type=EvaluationType.ALL, results_format="json")
    metrics = compute_metrics(results)
    summ = {**plan, "seconds": round(time.time() - t0), "n_sims": len(results.simulations),
            "infra_errors": sum(1 for s in results.simulations if str(getattr(s.termination_reason, "value", s.termination_reason)) == "infrastructure_error"),
            "avg_reward": metrics.avg_reward, "pass_hat_k": {str(k): v for k, v in metrics.pass_hat_ks.items()}, "usage": usage_totals(results),
            "judge": {**s2.JUDGE_COST, "own_estimate_usd": s2.JUDGE_COST["in_tokens"] / 1e6 * PRICE_IN + s2.JUDGE_COST["out_tokens"] / 1e6 * PRICE_OUT}}
    (save_dir / "summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    if s2.JUDGE_LOG:
        with open(save_dir / "judge_votes.csv", "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(s2.JUDGE_LOG[0]))
            w.writeheader()
            w.writerows(s2.JUDGE_LOG)
        (save_dir / "judge_raw.json").write_text(json.dumps(s2.RAW_REPLIES, indent=0, ensure_ascii=False), encoding="utf-8")
        s2.JUDGE_LOG.clear()
        s2.RAW_REPLIES.clear()
    for k in ("calls", "retries", "in_tokens", "out_tokens", "cost"):
        s2.JUDGE_COST[k] = 0
    print(json.dumps({k: summ[k] for k in ("n_sims", "infra_errors", "avg_reward", "pass_hat_k", "seconds")}, indent=1))
    return summ


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=[*PARTS, "all"], default="all")
    ap.add_argument("--seed", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.dry_run:
        s2.require_clean("run_v2")
    sample = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))
    sample_ids = sample["task_ids"]
    rest_ids = [t for t in sample["population_ids"] if t not in sample_ids]
    s2.install()
    s2.SWITCHES.set(True, True, True)
    s2.set_judge_cache(ROOT / "results" / "v2" / "judge_cache_live.json")
    tasks_v2.register()
    for part in (BLOCK2_PARTS if args.part == "all" else [args.part]):
        run_part(part, sample_ids, rest_ids, args.seed, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
