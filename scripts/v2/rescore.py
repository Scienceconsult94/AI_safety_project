"""Offline re-score of recorded simulations under scorer v2 (block2/PLAN.md §4, H3).

Stages
  A  replay gate: the configuration that produced the recorded reward must reproduce it for every
     simulation (recorded block-1 runs: the stock scorer; fresh block-2 runs: V2 with the live judge
     cache) -> results/v2/replay_check[_fresh].csv; the script stops on any difference (unless --force).
  A2 engagement gate (no cost): four perturbations of real trajectories must flip as designed
     (task 8 passengers reversed, task 20 payment methods reversed, task 23 bookings swapped: stock 0 ->
     hash_canon 1; task 23 with "$1,327" only: stock communicate 1 -> comm_boundary 0)
     -> results/v2/engagement_gate.csv; stops on failure.
  B  judge pre-computation (unless --no-judge): nl_assertions of tasks v1 and tasks v2 judged on every
     trajectory, 3 votes each, cached (results/v2/judge_cache.json; fresh runs: judge_cache_live.json,
     written by run_v2.py, so for them this stage is a replay). Only this stage calls a model.
  C  configurations (one switch at a time, all together, tasks v2 with the stock scorer, V2):
       v1, S_hash, S_comm, S_nl, S_all_t1 (tasks v1), T2_stock, V2 (tasks v2)
     -> results/v2/rescore[_fresh].csv (one row per simulation; per config: reward, db, comm, nl, the
        upper-bound reward with undetermined judge verdicts counted as met, the reward with process-class
        assertions excluded, per-assertion judge detail), judge_votes[_fresh].csv, judge_raw[_fresh].json,
        rescore_summary[_fresh].md, provenance[_fresh].json.
Per simulation also: the raw DB diff gold vs predicted under v1, whether canonicalisation closes it
(db_order_only), gold-action replay errors.

Reading rule (design review E3): a flip is attributed to its component (criteria text, hash, comm, nl);
the task-7 trial that flips 0 -> 1 under tasks v2 does so by construction of the fix.

Run from inside tau2-bench (tau2 venv; .env is read by tau2 for the judge):
    uv run --no-sync python ../scripts/v2/rescore.py [--set recorded|fresh|sonnet|rest30|fresh_rest30] [--no-judge] [--force] [--workers 3]
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import re
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
from tau2.data_model.message import AssistantMessage  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.data_model.tasks import RewardType  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation  # noqa: E402
from tau2.orchestrator.modes import CommunicationMode  # noqa: E402
from tau2.registry import registry  # noqa: E402

SETS = {
    "recorded": {"dir": RUNS, "files": {"haiku": "sample20_pass3_haiku.results.json", "gt": "sample20_gt_haiku.results.json"},
                 "gate_cfg": "v1", "suffix": "", "cache": OUT / "judge_cache.json"},
    "fresh": {"dir": OUT / "runs", "files": {"haiku": "v2_sample20_pass3_haiku/results.json", "gt": "v2_sample20_gt_haiku/results.json",
                                             "gt3": "v2_gt3_haiku/results.json"},
              "gate_cfg": "V2", "suffix": "_fresh", "cache": OUT / "judge_cache_live.json"},
    # strong-vs-weak check (strong_vs_weak/PLAN.md): the Sonnet agent on the 20 sampled tasks x 3, recorded under the stock scorer
    "sonnet": {"dir": RUNS, "files": {"sonnet": "sample20_sonnet_t3.results.json"},
               "gate_cfg": "v1", "suffix": "_sonnet", "cache": OUT / "judge_cache_sonnet.json", "label": "sonnet"},
    # the 30 airline tasks outside the sample (airline_full/PLAN.md, Q5): stock runs under the stock scorer, fresh v2 runs
    "rest30": {"dir": RUNS, "files": {"haiku": "rest30_pass3_haiku.results.json", "gt": "rest30_gt_haiku.results.json"},
               "gate_cfg": "v1", "suffix": "_rest30", "cache": OUT / "judge_cache_rest30.json"},
    "fresh_rest30": {"dir": OUT / "runs", "files": {"haiku": "v2_rest30_pass3_haiku/results.json", "gt": "v2_rest30_gt_haiku/results.json"},
                     "gate_cfg": "V2", "suffix": "_fresh_rest30", "cache": OUT / "judge_cache_live.json"},
}
PASS3_AGENTS = ("haiku", "sonnet")  # run keys of Pass^3 runs; every other key is a ground-truth run
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


def load_classes() -> dict[tuple[str, int], str]:
    p = ROOT / "block2" / "nl_assertion_classes.csv"
    if not p.exists():
        return {}
    return {(r["task_id"], int(r["idx"])): r["class"] for r in csv.DictReader(open(p, encoding="utf-8"))}


# ---------------------------------------------------------------------------------------------
# engagement gate: perturbations of real trajectories that the switches must flip
# ---------------------------------------------------------------------------------------------


def _perturb(sim, how: str):
    s = sim.model_copy(deep=True)
    if how == "passengers_reversed":
        for m in s.messages:
            if isinstance(m, AssistantMessage) and m.tool_calls:
                for tc in m.tool_calls:
                    if tc.name == "book_reservation":
                        tc.arguments["passengers"] = list(reversed(tc.arguments["passengers"]))
    elif how == "payments_reversed":
        for m in s.messages:
            if isinstance(m, AssistantMessage) and m.tool_calls:
                for tc in m.tool_calls:
                    if tc.name == "book_reservation":
                        tc.arguments["payment_methods"] = list(reversed(tc.arguments["payment_methods"]))
    elif how == "bookings_swapped":
        idx = [i for i, m in enumerate(s.messages) if isinstance(m, AssistantMessage) and m.tool_calls and any(tc.name == "book_reservation" for tc in m.tool_calls)]
        a, b = idx[0], idx[-1]
        s.messages[a].tool_calls, s.messages[b].tool_calls = s.messages[b].tool_calls, s.messages[a].tool_calls
        # keep ToolMessage ids paired with the swapped calls
        ra = next(m for m in s.messages[a + 1:] if m.role == "tool")
        rb = next(m for m in s.messages[b + 1:] if m.role == "tool")
        ra.id, rb.id = rb.id, ra.id
    elif how == "comm_1327_only":
        for m in s.messages:
            if isinstance(m, AssistantMessage) and m.has_text_content() and "327" in m.content:
                m.content = re.sub(r"\$327\b", "$1,327", m.content)
                m.content = re.sub(r"(?<![\d,.])327(?!\d)", "1,327", m.content)
    return s


def engagement_gate(loaded, t1, comm_scoring, path: Path) -> bool:
    plan = [  # (agent file, task, trial filter, perturbation, switch, expect stock (reward or comm), expect switched)
        ("gt", "8", None, "passengers_reversed", "hash", 0.0, 1.0),
        ("gt", "20", None, "payments_reversed", "hash", 0.0, 1.0),
        ("haiku", "23", None, "bookings_swapped", "hash", 0.0, 1.0),
        ("haiku", "23", None, "comm_1327_only", "comm", 1, 0),
    ]
    rows, ok_all = [], True
    for agent, tid, _, how, sw, exp0, exp1 in plan:
        res = next((r for a, _, r, _ in loaded if a == agent), None)
        sim = next((x for x in res.simulations if x.task_id == tid and x.reward_info and x.reward_info.reward == 1.0), None) if res else None
        if sim is None:
            rows.append({"perturbation": how, "task": tid, "status": "no passing trajectory available", "ok": 0})
            ok_all = False
            continue
        p = _perturb(sim, how)
        s2.SWITCHES.set(False, False, False)
        r0 = evaluate(p, t1[tid], comm_scoring)
        s2.SWITCHES.set(sw == "hash", sw == "comm", False)
        r1 = evaluate(p, t1[tid], comm_scoring)
        s2.SWITCHES.set(False, False, False)
        v0 = r0.reward if sw == "hash" else components(r0)[2]
        v1 = r1.reward if sw == "hash" else components(r1)[2]
        ok = (v0 == exp0) and (v1 == exp1)
        ok_all &= ok
        rows.append({"perturbation": how, "task": tid, "trial": sim.trial, "agent": agent, "switch": sw, "stock": v0, "switched": v1,
                     "expected": f"{exp0}->{exp1}", "ok": int(ok)})
    with open(path, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"  engagement {r['perturbation']:>19} task {r['task']}: {r.get('stock')} -> {r.get('switched')} expected {r.get('expected')} {'ok' if r['ok'] else 'FAIL'}")
    return ok_all


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
    if not args.no_judge:
        s2.require_clean("rescore (judge stage)")
    prov = s2.provenance()
    s2.install()
    s2.set_judge_cache(S["cache"])
    tasks_v2.register()
    s2.SWITCHES.set(False, False, False)
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}  # plain tasks v2 (NL basis added per config below)
    t1_stock = {t.id: t for t in registry.get_tasks_loader("airline")(None)}
    classes = load_classes()

    loaded = []
    for agent, fn in S["files"].items():
        p = S["dir"] / fn
        if not p.exists():
            print(f"missing {p} - skipped")
            continue
        res = Results.load(p)
        if args.set in ("recorded", "sonnet", "rest30"):  # runs on the pinned tasks: the embedded tasks must equal the loader's
            t1 = {t.id: t for t in res.tasks}
            assert all(t1[k].model_dump() == t1_stock[k].model_dump() for k in t1), "embedded tasks differ from the pinned loader"
        else:
            t1 = {k: t1_stock[k] for k in {s.task_id for s in res.simulations}}
        loaded.append((agent, fn, res, t1))
    if not loaded:
        return 1
    comm_scoring = loaded[0][2].info.effective_communicate_scoring

    # ---- stage A: replay gate
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
    print(f"stage A replay gate ({S['gate_cfg']}): {len(gate_rows) - mism}/{len(gate_rows)} recorded rewards reproduced; judge calls so far {s2.JUDGE_COST['calls']}")
    if mism and not args.force:
        print("replay gate FAILED - stopping (use --force to continue)")
        return 2

    # ---- stage A2: engagement gate (recorded set only: it needs block-1 trajectories)
    if args.set == "recorded":
        if not engagement_gate(loaded, t1_stock, comm_scoring, OUT / "engagement_gate.csv") and not args.force:
            print("engagement gate FAILED - stopping")
            return 3

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
        print(f"stage B judge: {len(jobs)} distinct (trajectory, assertions) pairs x {args.votes} votes (cached pairs cost nothing)")
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(s2.judge_nl_assertions, m, a, args.votes) for m, a in jobs]
            for i, f in enumerate(as_completed(futs), 1):
                f.result()
                if i % 10 == 0 or i == len(futs):
                    print(f"  judged {i}/{len(futs)}  calls={s2.JUDGE_COST['calls']} retries={s2.JUDGE_COST['retries']} in={s2.JUDGE_COST['in_tokens']} out={s2.JUDGE_COST['out_tokens']}  {time.time() - t0:.0f}s")

    # ---- stage C: configurations
    rows = []
    cfgs = [c for c in CONFIGS if not (args.no_judge and c[4])]
    for agent, fn, res, t1 in loaded:
        for sim in res.simulations:
            row = {"file": fn, "agent": agent, "task_id": sim.task_id, "trial": sim.trial, "seed": sim.seed,
                   "termination": str(getattr(sim.termination_reason, "value", sim.termination_reason)),
                   "recorded_reward": sim.reward_info.reward if sim.reward_info else None, "n_messages": len(sim.messages or []),
                   "scorer_version": prov["scorer_version"], "overlay_commit": prov["overlay_commit"], "overlay_dirty": int(prov["overlay_dirty"])}
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
                base_task = (t1 if tv == "t1" else t2)[sim.task_id]
                task = s2.with_nl_basis(base_task) if n else base_task
                try:
                    ri = evaluate(sim, task, comm_scoring)
                    r, db, comm, nl = components(ri)
                    if c is not None and ri.communicate_checks:
                        row[f"{name}_comm_failed"] = "; ".join(ch.info for ch in ri.communicate_checks if not ch.met)
                    if n:
                        asserts = base_task.evaluation_criteria.nl_assertions or []
                        det = s2.judge_nl_assertions(sim.messages, asserts)  # cached: no call
                        row[f"{name}_nl_failed"] = "; ".join(a[:60] for a, d in zip(asserts, det) if d["met"] is not True)[:300]
                        row[f"{name}_nl_detail"] = json.dumps([{"i": i, "met": d["met"], "vm": d["votes_met"], "vu": d["votes_unmet"], "vn": d["votes_undetermined"], "rule": d["rule"]} for i, d in enumerate(det)])
                        undet = sum(1 for d in det if d["met"] is None)
                        row[f"{name}_nl_undetermined"] = undet
                        base = float((db or 0) * (1 if comm is None else comm))
                        nl_upper = all(d["met"] is not False for d in det)  # undetermined counted as met
                        row[f"{name}_reward_upper"] = base * float(nl_upper)
                        nl_noproc = all(d["met"] is True for i, d in enumerate(det) if classes.get((sim.task_id, i), "") != "process")
                        row[f"{name}_reward_noproc"] = base * float(nl_noproc) if classes else ""
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
        (OUT / f"judge_raw{SUF}.json").write_text(json.dumps(s2.RAW_REPLIES, indent=0, ensure_ascii=False), encoding="utf-8")
    (OUT / f"provenance{SUF}.json").write_text(json.dumps({**prov, "set": args.set, "judge_cost": s2.JUDGE_COST, "votes": args.votes}, indent=1, default=str), encoding="utf-8")

    # ---- summary
    cost = s2.JUDGE_COST["in_tokens"] / 1e6 * PRICE_IN + s2.JUDGE_COST["out_tokens"] / 1e6 * PRICE_OUT
    hk = [r for r in rows if r["agent"] in PASS3_AGENTS]
    gt = [r for r in rows if r["agent"] not in PASS3_AGENTS]
    lab = S.get("label", "haiku")
    n_tasks = len({r["task_id"] for r in hk})
    lines = [f"# Re-score of the {args.set} simulations under scorer v2", "",
             f"Inputs: {', '.join(fn for _, fn, _, _ in loaded)} ({len(rows)} simulations). Replay gate ({S['gate_cfg']} reproduces the recorded reward): {len(gate_rows) - mism}/{len(gate_rows)}.",
             f"Provenance: scorer {prov['scorer_version']}, overlay commit {prov['overlay_commit']}{' (DIRTY)' if prov['overlay_dirty'] else ''}, judge {prov['judge_model']} args {prov['judge_args']} view {prov['judge_view']} prompt {prov['judge_prompt_sha256']}, {args.votes} votes.",
             f"Judge calls this run: {s2.JUDGE_COST['calls']} ({s2.JUDGE_COST['retries']} re-asks), {s2.JUDGE_COST['in_tokens']:,} in / {s2.JUDGE_COST['out_tokens']:,} out tokens, own cost estimate ${cost:.3f} (${PRICE_IN}/{PRICE_OUT} per MTok).", "",
             "## Pass counts per configuration", "",
             f"| config | tasks | switches | {lab} sims ({len(hk)}) | {lab} tasks 3/3 ({n_tasks}) | gt sims ({len(gt)}) | all ({len(rows)}) | upper bound (undetermined→met) | without process-class assertions |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, tv, h, c, n in cfgs:
        ph = sum(1 for r in hk if r.get(f"{name}_reward") == 1.0)
        pg = sum(1 for r in gt if r.get(f"{name}_reward") == 1.0)
        per_task = Counter(r["task_id"] for r in hk if r.get(f"{name}_reward") == 1.0)
        full = sum(1 for t in {r["task_id"] for r in hk} if per_task[t] == 3)
        sw = "+".join(x for x, v in (("hash", h), ("comm", c), ("nl", n)) if v) or "stock"
        up = sum(1 for r in rows if r.get(f"{name}_reward_upper") == 1.0) if n else ph + pg
        npc = sum(1 for r in rows if r.get(f"{name}_reward_noproc") == 1.0) if n and classes else (ph + pg if not n else "n/a")
        lines.append(f"| {name} | {tv} | {sw} | {ph} | {full} | {pg} | {ph + pg} | {up} | {npc} |")
    undet_total = sum(int(r.get("V2_nl_undetermined") or 0) for r in rows)
    lines += ["", f"Undetermined judge verdicts under V2 (after re-asks): {undet_total} assertion(s) across {len(rows)} simulations.", ""]
    lines += ["## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward", "",
              "| agent | task | trial | v1 | V2 | component(s) | detail |", "|---|---|---|---|---|---|---|"]
    nflip = 0
    for r in rows:
        a, b = r.get("v1_reward"), r.get("V2_reward")
        if a is None or b is None or a == b:
            continue
        nflip += 1
        comp = [n for n, k in (("criteria text (T2_stock)", "T2_stock_reward"), ("hash_canon", "S_hash_reward"), ("comm_boundary", "S_comm_reward"), ("nl_enforce", "S_nl_reward")) if r.get(k) not in (None, "") and r.get(k) != a]
        detail = r.get("V2_nl_failed") or r.get("V2_comm_failed") or ""
        if r["task_id"] == "7" and b > a:
            detail = "by construction: communicate_info 1628 -> 708; " + detail
        lines.append(f"| {r['agent']} | {r['task_id']} | {r['trial']} | {a} | {b} | {', '.join(comp) or 'interaction'} | {detail[:160]} |")
    if not nflip:
        lines.append("| (none) | | | | | | |")
    oo = [r for r in rows if r["db_order_only"]]
    lines += ["", "## DB failures under v1 that are order-only", "",
              f"{len(oo)} of {sum(1 for r in rows if not r['db_raw_match'])} v1 DB mismatches disappear under canonicalisation" + (": " + ", ".join(f"{r['agent']}/{r['task_id']}/t{r['trial']}" for r in oo) if oo else "."),
              f"Communicate flips from comm_boundary alone: {sum(1 for r in rows if r.get('S_comm_reward') not in (None, '') and r['v1_reward'] != r['S_comm_reward'])}.",
              f"Gold-action replay errors: {sum(1 for r in rows if r['gold_action_errors'])} simulations."]
    if s2.JUDGE_LOG:
        votes = defaultdict(list)
        for v in s2.JUDGE_LOG:
            votes[(v["key"], v["assertion_idx"])].append(v["met"])
        unanimous = sum(1 for vs in votes.values() if len(set(vs)) == 1)
        modes = Counter(v["mode"] for v in s2.JUDGE_LOG)
        lines += ["", "## Judge as an instrument (this run's calls only; cached pairs were not re-voted)", "",
                  f"{unanimous}/{len(votes)} assertion verdicts unanimous across {args.votes} votes; mapping modes {dict(modes)}; re-asks {s2.JUDGE_COST['retries']}. "
                  "Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md)."]
    (OUT / f"rescore_summary{SUF}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten {OUT.relative_to(ROOT)}/rescore{SUF}.csv, replay_check{SUF}.csv, rescore_summary{SUF}.md, provenance{SUF}.json" + (f", judge_votes{SUF}.csv, judge_raw{SUF}.json" if s2.JUDGE_LOG else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
