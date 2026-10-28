"""Checks 2b and 2c for retail with the stock scorer and the substituted judge (retail/PLAN.md §2, checklist deltas).

For every retail task:
  2b  empty answer: the canned greeting + one user turn, no tool call, no further agent text;
  2c  transfer only: greeting, one user turn, `transfer_to_human_agents` (GENERIC, not replayed by the DB evaluator)
      and the policy's transfer sentence.
Both trajectories go through the real `EnvironmentEvaluator` (DB part) and, where the task has `nl_assertions` and
NL_ASSERTION is in the basis, through the stock `NLAssertionsEvaluator` with the judge overlay (one vote, stock
prompt). Tasks without assertions need no judge call (NL part 1.0 by construction). Rewards are the product, as
`evaluate_simulation` computes it for EvaluationType.ALL.
Output: results/retail/noop_judge_probe.csv (one row per task and probe), noop_judge_probe.md (summary),
judge_calls_noop.json (every judge reply with strict_ok). SPENDS MONEY: <= 2 x 40 judge calls (own estimate < $0.05).
Run from inside tau2-bench:  uv run --no-sync python ../scripts/retail/noop_judge_probe.py [--dry]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
OUT = ROOT / "results" / "retail"

import judge_overlay as jo  # noqa: E402
from tau2.data_model.message import AssistantMessage, ToolCall, ToolMessage, UserMessage  # noqa: E402
from tau2.data_model.tasks import RewardType  # noqa: E402
from tau2.evaluator.evaluator_env import EnvironmentEvaluator  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.orchestrator.orchestrator import DEFAULT_FIRST_AGENT_MESSAGE  # noqa: E402
from tau2.registry import registry  # noqa: E402

TRANSFER_TEXT = "YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON."


def user_turn(task) -> str:
    ins = task.user_scenario.instructions
    return (getattr(ins, "reason_for_call", None) or "Hello, I need help with my order.").strip()


def traj_empty(task):
    return [AssistantMessage(role="assistant", content=DEFAULT_FIRST_AGENT_MESSAGE.content, turn_idx=0),
            UserMessage(role="user", content=user_turn(task), turn_idx=1)]


def traj_transfer(task):
    tc = ToolCall(id="probe_transfer_1", name="transfer_to_human_agents", arguments={"summary": "Customer request outside the agent's scope."}, requestor="assistant")
    return traj_empty(task) + [
        AssistantMessage(role="assistant", content=None, tool_calls=[tc], turn_idx=2),
        ToolMessage(id="probe_transfer_1", role="tool", content="Transfer successful", requestor="assistant", turn_idx=3),
        AssistantMessage(role="assistant", content=TRANSFER_TEXT, turn_idx=4),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="no judge call; rows carry only the DB part and the by-construction NL part")
    args = ap.parse_args()
    prov = jo.install()
    env_ctor = registry.get_env_constructor("retail")
    tasks = registry.get_tasks_loader("retail")("base")
    rows, calls = [], []
    for task in tasks:
        ec = task.evaluation_criteria
        nl = list(ec.nl_assertions or []) if ec else []
        nl_gates = bool(nl) and bool(ec) and RewardType.NL_ASSERTION in (ec.reward_basis or [])
        for probe, traj in (("2b", traj_empty(task)), ("2c", traj_transfer(task))):
            db = EnvironmentEvaluator.calculate_reward(env_ctor, task, full_trajectory=traj)
            db_r = float(db.reward)
            nl_r, nl_detail, judged = 1.0, "", 0
            if nl_gates and db_r == 1.0 and not args.dry:
                ri = NLAssertionsEvaluator.calculate_reward(task=task, full_trajectory=traj)
                nl_r = float(ri.reward)
                nl_detail = "; ".join(f"[{'met' if c.met else 'unmet'}] {c.nl_assertion[:60]}" for c in (ri.nl_assertions or []))
                judged = 1
                for c in jo.drain():
                    calls.append({"task_id": task.id, "probe": probe, **c})
            elif nl_gates and db_r == 1.0:
                nl_r = float("nan")
            reward = db_r * nl_r if db_r == 1.0 else 0.0
            rows.append({"task_id": task.id, "probe": probe, "db_reward": db_r, "nl_gates": int(nl_gates), "judged": judged,
                         "nl_reward": nl_r, "reward": reward, "passes": int(reward == 1.0), "nl_detail": nl_detail})
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "noop_judge_probe.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT / "judge_calls_noop.json").write_text(json.dumps(calls, indent=0, ensure_ascii=False), encoding="utf-8")
    tot = jo.totals()
    n = len(tasks)
    L = ["# No-op and transfer-only probes, retail, stock scorer with the substituted judge", "",
         f"Provenance: {json.dumps(prov)}", "", f"judge calls: {tot['calls']}, strict-parser rejections: {tot['strict_rejected']}, unparsed: {tot['unparsed']}, "
         f"replies with fewer results than assertions: {tot['results_short']}; tokens in/out {tot['in_tokens']}/{tot['out_tokens']}; own estimate ${tot['own_estimate_usd']:.3f}", ""]
    for probe, label in (("2b", "empty answer (greeting + one user turn)"), ("2c", "transfer only")):
        R = [r for r in rows if r["probe"] == probe]
        p = [r for r in R if r["passes"]]
        byc = [r for r in p if not r["nl_gates"]]
        byj = [r for r in p if r["nl_gates"]]
        L += [f"## {probe} {label}", "",
              f"- passes: {len(p)}/{n}; by construction (DB unchanged, no assertions): {len(byc)} -> {', '.join(r['task_id'] for r in byc) or 'none'}; "
              f"judge accepted the assertions: {len(byj)} -> {', '.join(r['task_id'] for r in byj) or 'none'}",
              f"- DB part 1.0 but assertions exist (judged): {sum(1 for r in R if r['nl_gates'] and r['db_reward'] == 1.0)} tasks; judge failed them: "
              f"{sum(1 for r in R if r['nl_gates'] and r['db_reward'] == 1.0 and r['reward'] == 0.0)}", ""]
        for r in R:
            if r["judged"]:
                L.append(f"  - task {r['task_id']}: nl_reward={r['nl_reward']} {r['nl_detail']}")
        L.append("")
    (OUT / "noop_judge_probe.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))
    print(f"written {OUT.relative_to(ROOT)}/noop_judge_probe.csv/.md, judge_calls_noop.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
