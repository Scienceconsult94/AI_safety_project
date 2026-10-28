"""Null-agent floor of the original tau-bench (sierra-research/tau-bench), computed with the benchmark's own reward code.

For every task of every split the environment accepts (airline: test; retail: test, train, dev):
  null      fresh environment, no action at all, then Env.calculate_reward()  (empty trajectory)
  refusal   fresh environment, one env.step(transfer_to_human_agents) at step 0; the benchmark's own step() ends the
            episode on this terminate tool and computes the reward (= "give up / hand over" agent)
  gold      positive control: fresh environment, every reference action replayed through env.step() (the terminate tool
            transfer_to_human_agents is skipped, it does not touch the data), then one `respond` message per required
            output appended to the action log with the output string verbatim (no user-simulator call), then
            Env.calculate_reward(). Expected reward 1.0 for every task.
Diagnostics per task: number of reference actions, number of required outputs, whether the reference replay changes the
database hash, and how many reference actions return an "Error" observation on replay.

The user simulator is built with the benchmark's "human" strategy, whose constructor makes no call; reset() is never
called, so no model and no input() is ever reached (the reference actions contain no `respond` action).

Usage (tau-bench venv, isolated mode, UTF-8 mode because the data loader opens JSON with the platform encoding):
  set LITELLM_LOCAL_MODEL_COST_MAP=True
  <venv>\Scripts\python.exe -I -X utf8 tau_bench.py --repo <clone> --out-csv <csv>
"""

from __future__ import annotations

import argparse
import csv
import math
import subprocess
from datetime import date

from tau_bench.envs import get_env
from tau_bench.types import Action, RESPOND_ACTION_NAME, RewardOutputInfo

SPLITS = [("airline", "test"), ("retail", "test"), ("retail", "train"), ("retail", "dev")]


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def make_env(domain: str, split: str, i: int):
    return get_env(domain, user_strategy="human", user_model=None, task_split=split, task_index=i)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out-csv", required=True)
    a = ap.parse_args()
    commit = subprocess.run(["git", "-C", a.repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    rows = []
    for domain, split in SPLITS:
        n = len(make_env(domain, split, 0).tasks)
        for i in range(n):
            env = make_env(domain, split, i)
            task = env.task
            init_hash = env.get_data_hash()
            # null: empty trajectory
            r_null = env.calculate_reward()
            # positive control on a fresh environment (also gives the reference end-state hash for the diagnostic)
            env_g = make_env(domain, split, i)
            n_err = 0
            n_resp_gold = 0
            for act in task.actions:
                if act.name == RESPOND_ACTION_NAME:
                    n_resp_gold += 1
                    continue
                if act.name in env_g.terminate_tools:
                    continue
                obs = env_g.step(act).observation
                if isinstance(obs, str) and obs.startswith("Error"):
                    n_err += 1
            gold_hash = env_g.get_data_hash()
            for out in task.outputs:
                env_g.actions.append(Action(name=RESPOND_ACTION_NAME, kwargs={"content": out}))
            r_gold = env_g.calculate_reward()
            # refusal: transfer to a human at step 0 through the benchmark's own step()
            env_r = make_env(domain, split, i)
            resp = env_r.step(Action(name="transfer_to_human_agents", kwargs={"summary": "I cannot help with this request."}))
            r_ref = resp.reward if resp.done else float("nan")
            gold_out_fail = ""
            if isinstance(r_gold.info, RewardOutputInfo):
                gold_out_fail = ";".join(k for k, v in r_gold.info.outputs.items() if not v)
            rows.append({
                "benchmark": "tau-bench", "domain": domain, "split": split, "task_index": i,
                "n_actions": len(task.actions), "n_outputs": len(task.outputs),
                "gold_changes_db": int(gold_hash != init_hash), "gold_replay_errors": n_err, "gold_respond_actions": n_resp_gold,
                "null_reward": r_null.reward, "refusal_reward": r_ref, "gold_reward": r_gold.reward,
                "gold_outputs_not_found": gold_out_fail, "outputs": "|".join(task.outputs),
                "commit": commit, "scan_date": date.today().isoformat(),
            })
    with open(a.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"commit {commit}")
    print("domain split tasks null_pass null_ci refusal_pass gold_pass gold_fail_ids no_db_change with_outputs replay_err_tasks")
    for domain, split in SPLITS:
        rs = [r for r in rows if r["domain"] == domain and r["split"] == split]
        n = len(rs)
        k = sum(1 for r in rs if r["null_reward"] == 1.0)
        kr = sum(1 for r in rs if r["refusal_reward"] == 1.0)
        kg = sum(1 for r in rs if r["gold_reward"] == 1.0)
        lo, hi = wilson(k, n)
        fails = [r["task_index"] for r in rs if r["gold_reward"] != 1.0]
        nodb = sum(1 for r in rs if not r["gold_changes_db"])
        wout = sum(1 for r in rs if r["n_outputs"] > 0)
        rerr = sum(1 for r in rs if r["gold_replay_errors"] > 0)
        print(f"{domain} {split} {n} {k} ({100*k/n:.1f}%) [{100*lo:.1f}-{100*hi:.1f}] {kr} {kg} {fails} {nodb} {wout} {rerr}")
        print("  null-pass ids:", [r["task_index"] for r in rs if r["null_reward"] == 1.0])


if __name__ == "__main__":
    main()
