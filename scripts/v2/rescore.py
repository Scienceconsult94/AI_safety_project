"""Offline re-score of the recorded block-1 simulations under scorer v2 (block2/PLAN.md §4, H3).

Stages
  A  replay gate: the stock scorer (no switch) must reproduce the recorded reward of every
     simulation -> results/v2/replay_check.csv; the script stops if any differs (unless --force).
  B  judge pre-computation (unless --no-judge): nl_assertions of tasks v1 and tasks v2 judged on
     every recorded trajectory, 3 votes each, cached in results/v2/judge_cache.json (re-runs cost
     nothing). Only this stage calls a model.
  C  configurations (one switch at a time, all together, tasks v1 vs v2):
       v1        tasks v1, stock scorer (= stage A)
       S_hash    tasks v1, hash_canon
       S_comm    tasks v1, comm_boundary
       S_nl      tasks v1, nl_enforce
       S_all_t1  tasks v1, all three switches
       T2_stock  tasks v2, stock scorer  (effect of the text/communicate_info fixes alone)
       V2        tasks v2, all three switches  (the v2 benchmark)
     -> results/v2/rescore.csv (one row per simulation), judge_votes.csv, rescore_summary.md
Also per simulation: the raw DB diff gold vs predicted under v1 and whether canonicalisation
closes it (db_order_only), and gold-action replay errors.

Run from inside tau2-bench (needs the tau2 venv; .env is read by tau2 for the judge):
    uv run --no-sync python ../scripts/v2/rescore.py [--no-judge] [--force] [--workers 3]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
RUNS = ROOT / "results" / "runs"
OUT = ROOT / "results" / "v2"

import scorer_v2 as s2  # noqa: E402
import tasks_v2  # noqa: E402
from loguru import logger  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.data_model.tasks import RewardType  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation  # noqa: E402
from tau2.orchestrator.modes import CommunicationMode  # noqa: E402
from tau2.registry import registry  # noqa: E402

SETS = {
    # recorded block-1 runs (v1 benchmark): gate = stock scorer reproduces the recorded reward
    "recorded": {"dir": RUNS, "files": {"haiku": "sample20_pass3_haiku.results.json", "gt": "sample20_gt_haiku.results.json"}, "gate_cfg": "v1", "suffix": ""},
    # fresh block-2 runs (v2 benchmark, scored live by V2): gate = V2 reproduces the recorded reward
    "fresh": {"dir": OUT / "runs", "files": {"haiku": "v2_sample20_pass3_haiku/results.json", "gt": "v2_sample20_gt_haiku/results.json"}, "gate_cfg": "V2", "suffix": "_fresh"},
}
CONFIGS = [  # name, tasks, hash, comm, nl
    ("v1", "t1", 0, 0, 0),
    ("S_hash", "t1", 1, 0, 0),
    ("S_comm", "t1", 0, 1, 0),
    ("S_nl", "t1", 0, 0, 1),
    ("S_all_t1", "t1", 1, 1, 1),
    ("T2_stock", "t2", 0, 0, 0),
    ("V2", "t2", 1, 1, 1),
]
PRICE_IN, PRICE_OUT = 0.10, 0.50  # USD per MTok, claude-haiku-5-5 (own estimate; litellm cannot price the judge call)

GOLD_WARNINGS: list[str] = []
logger.remove()
logger.add(sys.stderr, level="ERROR")
logger.add(lambda m: GOLD_WARNINGS.append(str(m).strip()), level="WARNING", filter=lambda r: "golden actions" in r["message"])


def evaluate(sim, task, comm_scoring):
    return evaluate_simulation(
        simulation=sim, task=task, evaluation_type=EvaluationType.ALL, solo_mode=False, domain="airline",
        mode=CommunicationMode.HALF_DUPLEX, env_kwargs=None, strict_replay=False, communicate_scoring=comm_scoring,
    )


def components(ri):
    bd = ri.reward_breakdown or {}
    db = None if ri.db_check is None else int(ri.db_check.db_match)
    comm = bd.get(RewardType.COMMUNICATE)
    nl = bd.get(RewardType.NL_ASSERTION)
    return ri.reward, db, None if comm is None else int(comm), None if nl is None else int(nl)


def db_dumps(sim, task):
    """Raw gold and predicted DB dumps (stock replay path), for the diff column."""
    ctor = registry.get_env_constructor("airline")
    pred = ctor()
    pred.set_state(initialization_data=None, initialization_actions=None, message_history=list(sim.messages), strict=False)
    gold = ctor()
    gold.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=False)
    errs = []
    for a in task.evaluation_criteria.actions or []:
        try:
            gold.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception as e:  # noqa: BLE001
            errs.append(f"{a.name}: {e}")
    return gold.tools.db.model_dump(), pred.tools.db.model_dump(), errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--votes", type=int, default=s2.JUDGE_VOTES)
    ap.add_argument("--set", choices=list(SETS), default="recorded")
    args = ap.parse_args()
    S = SETS[args.set]
    SUF = S["suffix"]
    OUT.mkdir(parents=True, exist_ok=True)
    s2.install()
    s2.set_judge_cache(OUT / "judge_cache.json")
    tasks_v2.register()
    s2.SWITCHES.set(False, False, False)
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}  # plain tasks v2 (NL basis added per config below)
    t1_stock = {t.id: t for t in registry.get_tasks_loader("airline")(None)}

    loaded = []
    for agent, fn in S["files"].items():
        p = S["dir"] / fn
        if not p.exists():
            print(f"missing {p} - skipped")
            continue
        res = Results.load(p)
        if args.set == "recorded":
            t1 = {t.id: t for t in res.tasks}
            assert all(t1[k].model_dump() == t1_stock[k].model_dump() for k in t1), "embedded tasks differ from the pinned loader"
        else:
            t1 = {k: t1_stock[k] for k in {s.task_id for s in res.simulations}}
        loaded.append((agent, fn, res, t1))
    if not loaded:
        return 1
    comm_scoring = loaded[0][2].info.effective_communicate_scoring

    # ---- stage A: replay gate (the configuration that produced the recorded reward must reproduce it)
    gate = dict(zip(("name", "tasks", "h", "c", "n"), next(c for c in CONFIGS if c[0] == S["gate_cfg"])))
    s2.SWITCHES.set(bool(gate["h"]), bool(gate["c"]), bool(gate["n"]))
    gate_rows, mism = [], 0
    for agent, fn, res, t1 in loaded:
        for sim in res.simulations:
            task = (t1 if gate["tasks"] == "t1" else t2)[sim.task_id]
            if gate["n"]:
                task = s2.with_nl_basis(task)
            ri = evaluate(sim, task, comm_scoring)
            rec = sim.reward_info.reward if sim.reward_info else None
            ok = rec is not None and abs(ri.reward - rec) < 1e-9
            mism += not ok
            gate_rows.append({"file": fn, "agent": agent, "task_id": sim.task_id, "trial": sim.trial, "recorded_reward": rec, "recomputed_reward": ri.reward, "match": int(ok)})
    s2.SWITCHES.set(False, False, False)
    with open(OUT / f"replay_check{SUF}.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(gate_rows[0]))
        w.writeheader()
        w.writerows(gate_rows)
    print(f"stage A replay gate: {len(gate_rows) - mism}/{len(gate_rows)} recorded rewards reproduced")
    if mism and not args.force:
        print("replay gate FAILED - stopping (use --force to continue)")
        return 2

    # ---- stage B: judge pre-computation
    key_meta: dict[str, dict] = {}
    if not args.no_judge:
        jobs = []
        for agent, fn, res, t1 in loaded:
            for sim in res.simulations:
                variants = {"t1": t1[sim.task_id].evaluation_criteria.nl_assertions or [], "t2": t2[sim.task_id].evaluation_criteria.nl_assertions or []}
                for tv, asserts in variants.items():
                    k = s2.judge_key(sim.messages, asserts)
                    if k in key_meta:
                        continue
                    key_meta[k] = {"agent": agent, "task_id": sim.task_id, "trial": sim.trial, "tasks": tv, "n_assertions": len(asserts)}
                    jobs.append((sim.messages, asserts))
        print(f"stage B judge: {len(jobs)} distinct (trajectory, assertions) pairs x {args.votes} votes")
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(s2.judge_nl_assertions, m, a, args.votes) for m, a in jobs]
            for i, f in enumerate(as_completed(futs), 1):
                f.result()
                if i % 10 == 0 or i == len(futs):
                    print(f"  judged {i}/{len(futs)}  calls={s2.JUDGE_COST['calls']}  in={s2.JUDGE_COST['in_tokens']} out={s2.JUDGE_COST['out_tokens']}  {time.time() - t0:.0f}s")

    # ---- stage C: configurations
    rows = []
    cfgs = [c for c in CONFIGS if not (args.no_judge and c[4])]
    for agent, fn, res, t1 in loaded:
        for sim in res.simulations:
            row = {"file": fn, "agent": agent, "task_id": sim.task_id, "trial": sim.trial, "seed": sim.seed, "termination": str(sim.termination_reason.value if hasattr(sim.termination_reason, 'value') else sim.termination_reason),
                   "recorded_reward": sim.reward_info.reward if sim.reward_info else None, "n_messages": len(sim.messages or [])}
            GOLD_WARNINGS.clear()
            gold, pred, gerrs = db_dumps(sim, t1[sim.task_id])
            raw_diff = s2.db_diff(gold, pred, limit=8)
            canon_equal = s2.db_diff(s2.canonical_dump(gold), s2.canonical_dump(pred), limit=1) == []
            row["db_raw_match"] = int(not raw_diff)
            row["db_order_only"] = int(bool(raw_diff) and canon_equal)
            row["db_diff_v1"] = " | ".join(raw_diff)[:400]
            row["gold_action_errors"] = " | ".join(gerrs)[:200]
            for name, tv, h, c, n in cfgs:
                s2.SWITCHES.set(bool(h), bool(c), bool(n))
                task = (t1 if tv == "t1" else t2)[sim.task_id]
                if n:
                    task = s2.with_nl_basis(task)
                try:
                    ri = evaluate(sim, task, comm_scoring)
                    r, db, comm, nl = components(ri)
                    if n and ri.nl_assertions:
                        row[f"{name}_nl_failed"] = "; ".join(a.nl_assertion[:60] for a in ri.nl_assertions if not a.met)[:300]
                    if c is not None and ri.communicate_checks:
                        row[f"{name}_comm_failed"] = "; ".join(ch.info for ch in ri.communicate_checks if not ch.met)
                except Exception as e:  # noqa: BLE001
                    r, db, comm, nl = None, None, None, None
                    row[f"{name}_error"] = repr(e)[:200]
                row[f"{name}_reward"], row[f"{name}_db"], row[f"{name}_comm"], row[f"{name}_nl"] = r, db, comm, nl
            rows.append(row)
    s2.SWITCHES.set(False, False, False)

    fields = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(OUT / f"rescore{SUF}.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    if s2.JUDGE_LOG:
        with open(OUT / f"judge_votes{SUF}.csv", "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(s2.JUDGE_LOG[0]))
            w.writeheader()
            w.writerows(s2.JUDGE_LOG)

    # ---- summary
    cost = s2.JUDGE_COST["in_tokens"] / 1e6 * PRICE_IN + s2.JUDGE_COST["out_tokens"] / 1e6 * PRICE_OUT
    lines = ["# Offline re-score of the recorded block-1 simulations (scorer v2)", "",
             f"Inputs ({args.set}): {', '.join(fn for _, fn, _, _ in loaded)} ({len(rows)} simulations). Replay gate ({S['gate_cfg']} reproduces the recorded reward): {len(gate_rows) - mism}/{len(gate_rows)}.",
             f"Judge: {s2.JUDGE_MODEL}, {args.votes} votes per assertion, {s2.JUDGE_COST['calls']} calls this run, "
             f"{s2.JUDGE_COST['in_tokens']:,} in / {s2.JUDGE_COST['out_tokens']:,} out tokens, own cost estimate ${cost:.3f} "
             f"(${PRICE_IN}/{PRICE_OUT} per MTok). Cached verdicts reused from judge_cache.json cost nothing.", "",
             "## Pass counts per configuration", "", f"| config | tasks | switches | haiku ({sum(1 for r in rows if r['agent'] == 'haiku')} sims) | haiku tasks 3/3 | gt ({sum(1 for r in rows if r['agent'] == 'gt')} sims) | all {len(rows)} |", "|---|---|---|---|---|---|---|"]
    by_task_cfg = defaultdict(dict)
    for name, tv, h, c, n in cfgs:
        hk = [r for r in rows if r["agent"] == "haiku"]
        gt = [r for r in rows if r["agent"] == "gt"]
        ph = sum(1 for r in hk if r.get(f"{name}_reward") == 1.0)
        pg = sum(1 for r in gt if r.get(f"{name}_reward") == 1.0)
        per_task = Counter(r["task_id"] for r in hk if r.get(f"{name}_reward") == 1.0)
        full = sum(1 for t in {r["task_id"] for r in hk} if per_task[t] == 3)
        for r in rows:
            by_task_cfg[(r["agent"], r["task_id"])].setdefault(name, []).append(r.get(f"{name}_reward"))
        sw = "+".join(x for x, v in (("hash", h), ("comm", c), ("nl", n)) if v) or "stock"
        lines.append(f"| {name} | {tv} | {sw} | {ph}/{len(hk)} | {full}/{len({r['task_id'] for r in hk})} | {pg}/{len(gt)} | {ph + pg}/{len(rows)} |")
    lines += ["", "## Flips per simulation, v1 -> V2", ""]
    flips = Counter()
    for r in rows:
        a, b = r.get("v1_reward"), r.get("V2_reward")
        if a is not None and b is not None and a != b:
            flips[(r["agent"], r["task_id"], "1->0" if a > b else "0->1")] += 1
    if flips:
        lines += ["| agent | task | direction | sims |", "|---|---|---|---|"]
        for (a, t, d), n in sorted(flips.items(), key=lambda x: (x[0][0], int(x[0][1]), x[0][2])):
            lines.append(f"| {a} | {t} | {d} | {n} |")
    else:
        lines.append("(no flips or V2 not computed)")
    lines += ["", "## DB failures under v1 that are order-only", ""]
    oo = [r for r in rows if r["db_order_only"]]
    lines.append(f"{len(oo)} of {sum(1 for r in rows if not r['db_raw_match'])} v1 DB mismatches disappear under canonicalisation: "
                 + ", ".join(f"{r['agent']}/{r['task_id']}/t{r['trial']}" for r in oo))
    ge = [r for r in rows if r["gold_action_errors"]]
    lines += ["", f"Gold-action replay errors: {len(ge)} simulations" + ("; tasks " + ", ".join(sorted({r['task_id'] for r in ge}, key=int)) if ge else "")]
    if s2.JUDGE_LOG:
        votes = defaultdict(list)
        for v in s2.JUDGE_LOG:
            votes[(v["key"], v["assertion_idx"])].append(v["met"])
        unanimous = sum(1 for vs in votes.values() if len(set(vs)) == 1)
        lines += ["", "## Judge agreement", "", f"{unanimous}/{len(votes)} assertion verdicts unanimous across {args.votes} votes (this run's calls only; cached pairs not re-voted)."]
    (OUT / f"rescore_summary{SUF}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten {OUT.relative_to(ROOT)}/rescore{SUF}.csv, replay_check{SUF}.csv, rescore_summary{SUF}.md" + (f", judge_votes{SUF}.csv" if s2.JUDGE_LOG else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
