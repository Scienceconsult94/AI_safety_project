"""T3 (overnight 2026-11-01): sensitivity of recorded verdicts to copies of the NL-assertion judge.

Plan and definitions: results/overnight/T3_PLAN.md. Nothing is re-run; only the judge is called again, on the recorded
trajectories, under six copies (three prompt wordings x two independent draws, three votes each). Every ballot is cached
in results/overnight/judge_cache_T3.json, so the analysis reruns offline with --no-judge.

Run from inside tau2-bench (its .env supplies the judge key; this script never reads it):
    uv run --no-sync python ../scripts/overnight/t3_judge_copies.py --sets airline|retail|all [--no-judge] [--dry]
                                                                     [--workers 4] [--budget-usd 30] [--max-calls N]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import combinations
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))
import scorer_v2 as s2  # noqa: E402
import tasks_v2  # noqa: E402
from tau2.data_model.message import SystemMessage, UserMessage  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.utils.llm_utils import generate  # noqa: E402

OUT = ROOT / "results" / "overnight"
CACHE_PATH = OUT / "judge_cache_T3.json"
COST_PATH = OUT / "cost_overnight.md"
PRICE_IN, PRICE_OUT = 0.10, 0.50  # USD per MTok, own-estimate convention of cost.md
VOTES = 3
RETRIES = 1
DRAWS = (1, 2)

# ---- the three prompt wordings -------------------------------------------------------------------------------------
_evaluator_src = (ROOT / "tau2-bench" / "src" / "tau2" / "evaluator" / "evaluator_nl_assertions.py").read_text(encoding="utf-8")
_m = re.search(r'system_prompt = """(.*?)"""', _evaluator_src, re.S)
assert _m, "stock prompt not found in the pinned evaluator"
STOCK_PROMPT = _m.group(1)  # verbatim, with tau2's indentation

PARAPHRASE_PROMPT = """
You are grading the transcript of an automated test of a customer-service agent.
Input: a conversation between the agent and a customer, and a numbered list of expected outcomes.
For every expected outcome decide whether the agent's behaviour in the conversation satisfies it. Judge each outcome
on its own, in the given order, and return exactly one verdict per outcome.
Answer with a JSON object of this shape:
{"results": [{"index": <number of the outcome as given>, "expectedOutcome": "<the outcome text>",
              "reasoning": "<one or two sentences>", "metExpectation": <true or false>}]}
"""

VARIANTS = {  # id -> (system prompt, user-prompt format)
    "P0": (s2._SYSTEM_PROMPT, "numbered"),
    "P1": (STOCK_PROMPT, "stock"),
    "P2": (PARAPHRASE_PROMPT, "numbered"),
}
COPIES = [f"{v}.{d}" for v in VARIANTS for d in DRAWS]
_NOOP_ROWS = list(csv.DictReader(open(ROOT / "results" / "v2" / "noop_judge_probe.csv", encoding="utf-8")))
REFUSAL_FLOOR = {r["task_id"] for r in _NOOP_ROWS if r["refusal_bot_pass"] == "1"}
EMPTY_FLOOR = {r["task_id"] for r in _NOOP_ROWS}  # the 23 no-op tasks


def user_prompt(traj_text: str, assertions: list[str], fmt: str) -> str:
    if fmt == "stock":  # tau2's f-string: the Python list of assertions, with the function's indentation
        return f"\n        conversation:\n        {traj_text}\n        \n        expectedOutcomes:\n        {assertions}\n        "
    numbered = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(assertions))
    return f"\nconversation:\n{traj_text}\n\nexpectedOutcomes:\n{numbered}\n"


# ---- units ----------------------------------------------------------------------------------------------------------
AIRLINE_SETS = [  # id, label, results file, rescore csv, agent key
    ("A1", "recorded sample 20x3, haiku", "results/runs/sample20_pass3_haiku.results.json", "results/v2/rescore.csv", "haiku"),
    ("A2", "recorded rest 30x3, haiku", "results/runs/rest30_pass3_haiku.results.json", "results/v2/rescore_rest30.csv", "haiku"),
    ("A3", "fresh v2 sample 20x3, haiku", "results/v2/runs/v2_sample20_pass3_haiku/results.json", "results/v2/rescore_fresh.csv", "haiku"),
    ("A4", "fresh v2 rest 30x3, haiku", "results/v2/runs/v2_rest30_pass3_haiku/results.json", "results/v2/rescore_fresh_rest30.csv", "haiku"),
    ("A5", "recorded sample 20x3, sonnet", "results/runs/sample20_sonnet_t3.results.json", "results/v2/rescore_sonnet.csv", "sonnet"),
]
RETAIL_SETS = [("B1", "retail pass^3 run, haiku: the 120 of 342 simulations whose reward is gated by assertions (all ended normally)", "retail_pass3_haiku"),
               ("B2", "retail ground-truth agent run: the 39 of 112 simulations whose reward is gated by assertions", "retail_gt_haiku")]
# The retail reference R (check 2j re-judge) used tau2's stock prompt and list format, so for retail the same-prompt copy is P1;
# for airline the reference is the V2 prompt, so it is P0.
SAME_PROMPT = {"airline": "P0", "retail": "P1"}


def airline_units() -> list[dict]:
    tasks_v2.register()
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}
    units = []
    for sid, label, rf, cf, agent in AIRLINE_SETS:
        res = Results.load(ROOT / rf)
        rows = {(r["agent"], r["task_id"], str(r["trial"])): r for r in csv.DictReader(open(ROOT / cf, encoding="utf-8"))}
        for sim in res.simulations:
            r = rows[(agent, sim.task_id, str(sim.trial))]
            asserts = t2[sim.task_id].evaluation_criteria.nl_assertions or []
            assert asserts and s2.has_agent_text(sim.messages)
            det = json.loads(r["V2_nl_detail"])
            assert len(det) == len(asserts)
            db, comm = int(r["V2_db"]), (1 if r["V2_comm"] in ("", "None") else int(r["V2_comm"]))
            ref_votes = [(d["vm"], d["vu"], d["vn"]) for d in det]
            ref_nl = all(d["met"] is True for d in det)
            assert abs(float(r["V2_reward"]) - float(db * comm * ref_nl)) < 1e-9, ("replay gate", sid, sim.task_id, sim.trial)
            units.append({"set": sid, "set_label": label, "domain": "airline", "agent": agent, "task_id": sim.task_id, "trial": sim.trial,
                          "traj": s2.trajectory_text(sim.messages), "assertions": asserts, "db": db, "comm": comm,
                          "votes": {"R": ref_votes}, "stock_reward": float(r["v1_reward"]) if r.get("v1_reward") not in (None, "") else None})
    return units


def retail_units() -> tuple[list[dict], dict]:
    cache = json.loads((ROOT / "results/retail/judge_cache_rejudge.json").read_text(encoding="utf-8"))
    units, gate = [], {"sims": 0, "majority_vs_live_flips": 0}
    for sid, label, run in RETAIL_SETS:
        data = json.loads((ROOT / "results/retail/runs" / run / "results.json").read_text(encoding="utf-8"))
        tasks = {str(t["id"]): t for t in data["tasks"]}
        for s in data["simulations"]:
            if str(s.get("termination_reason")) not in {"agent_stop", "user_stop"}:
                continue
            ec = tasks[str(s["task_id"])]["evaluation_criteria"]
            nl = ec.get("nl_assertions") or []
            if not nl or "NL_ASSERTION" not in (ec.get("reward_basis") or []):
                continue
            ri = s.get("reward_info") or {}
            traj = "\n".join(f"{m['role']}: {m.get('content')}" for m in s["messages"])
            key = hashlib.sha256((traj + json.dumps(nl)).encode("utf-8")).hexdigest()
            ballots = cache.get(key)
            if ballots is None:
                continue
            ref_votes = []
            for i, a in enumerate(nl):
                vs = [b.get(a) for b in ballots]
                if all(v is None for v in vs):  # the judge paraphrased the text: fall back to position
                    vs = [list(b.values())[i] if i < len(b) else None for b in ballots]
                ref_votes.append((sum(v is True for v in vs), sum(v is False for v in vs), sum(v is None for v in vs)))
            live = {c["nl_assertion"]: c["met"] for c in (ri.get("nl_assertions") or [])}
            live_votes = []
            for i, a in enumerate(nl):
                m = live.get(a)
                if m is None and i < len(ri.get("nl_assertions") or []):
                    m = (ri["nl_assertions"][i] or {}).get("met")
                m = None if m is None else str(m) == "True"
                live_votes.append((int(m is True), int(m is False), int(m is None)))
            db = int(bool((ri.get("db_check") or {}).get("db_match")))
            comm = int(float((ri.get("reward_breakdown") or {}).get("COMMUNICATE", 1.0) or 0) == 1.0)
            ref_nl = all(vm > vu for vm, vu, vn in ref_votes)
            live_nl = all(vm == 1 for vm, vu, vn in live_votes)
            gate["sims"] += 1
            gate["majority_vs_live_flips"] += int((db * comm * ref_nl) != (db * comm * live_nl))
            units.append({"set": sid, "set_label": label, "domain": "retail", "agent": "haiku" if run.endswith("pass3_haiku") else "gt",
                          "task_id": str(s["task_id"]), "trial": s.get("trial"), "traj": traj, "assertions": nl, "db": db, "comm": comm,
                          "votes": {"R": ref_votes, "L": live_votes}, "stock_reward": ri.get("reward")})
    return units, gate


# ---- judge calls ------------------------------------------------------------------------------------------------------
_LOCK = threading.Lock()
CACHE: dict[str, dict] = {}
COST = {"calls": 0, "in_tokens": 0, "out_tokens": 0, "retries": 0, "new_ballots": 0, "cached_ballots": 0}
_dirty = 0


def own_cost() -> float:
    return COST["in_tokens"] / 1e6 * PRICE_IN + COST["out_tokens"] / 1e6 * PRICE_OUT


def ballot_key(u: dict, variant: str, draw: int, vote: int) -> str:
    sp, fmt = VARIANTS[variant]
    cfg = f"{variant}|{draw}|{vote}|{s2.JUDGE_MODEL}|{fmt}|{hashlib.sha256(sp.encode()).hexdigest()[:12]}"
    return hashlib.sha256((cfg + "\n##\n" + u["traj"] + "\n##\n" + json.dumps(u["assertions"], ensure_ascii=False)).encode("utf-8")).hexdigest()


def save_cache(force: bool = False) -> None:
    global _dirty
    with _LOCK:
        if not force and _dirty < 25:
            return
        tmp = CACHE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(CACHE, ensure_ascii=False), encoding="utf-8")
        tmp.replace(CACHE_PATH)
        _dirty = 0


def one_ballot(u: dict, variant: str, draw: int, vote: int, budget: float, max_calls: int) -> dict | None:
    global _dirty
    key = ballot_key(u, variant, draw, vote)
    with _LOCK:
        if key in CACHE:
            COST["cached_ballots"] += 1
            return CACHE[key]
        if own_cost() >= budget or COST["calls"] >= max_calls:
            return None
    sp, fmt = VARIANTS[variant]
    up = user_prompt(u["traj"], u["assertions"], fmt)
    mapped, raws, attempts = [], [], 0
    for attempt in range(1 + RETRIES):
        attempts += 1
        reply = generate(model=s2.JUDGE_MODEL, messages=[SystemMessage(role="system", content=sp), UserMessage(role="user", content=up)],
                         call_name="nl_assertions_eval_t3", **s2.JUDGE_ARGS)
        usage = getattr(reply, "usage", None) or {}
        get = (lambda k: usage.get(k)) if isinstance(usage, dict) else (lambda k: getattr(usage, k, None))
        raw = reply.content or ""
        results, err = s2.parse_judge_reply(raw)
        mapped = s2._map_results(results, u["assertions"])
        raws.append({"attempt": attempt, "parse_error": err, "n_results": len(results), "raw": raw[:1500]})
        with _LOCK:
            COST["calls"] += 1
            COST["in_tokens"] += int(get("prompt_tokens") or 0)
            COST["out_tokens"] += int(get("completion_tokens") or 0)
        if all(m["met"] is not None for m in mapped):
            break
        with _LOCK:
            COST["retries"] += 1
    entry = {"met": [m["met"] for m in mapped], "modes": [m["mode"] for m in mapped], "attempts": attempts, "raws": raws,
             "set": u["set"], "task_id": u["task_id"], "trial": u["trial"], "variant": variant, "draw": draw, "vote": vote}
    with _LOCK:
        CACHE[key] = entry
        COST["new_ballots"] += 1
        _dirty += 1
    save_cache()
    return entry


def judge_stage(units: list[dict], workers: int, budget: float, max_calls: int, dry: bool) -> bool:
    jobs = [(u, v, d, k) for u in units for v in VARIANTS for d in DRAWS for k in range(VOTES)]
    todo = [j for j in jobs if ballot_key(*j) not in CACHE]
    print(f"judge stage: {len(jobs)} ballots, {len(jobs) - len(todo)} cached, {len(todo)} to call")
    if dry or not todo:
        return not todo
    t0, done, stopped = time.time(), 0, False
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one_ballot, u, v, d, k, budget, max_calls) for u, v, d, k in todo]
        for f in as_completed(futs):
            done += 1
            if f.result() is None:
                stopped = True
            if done % 100 == 0 or done == len(futs):
                print(f"  {done}/{len(futs)} ballots  calls={COST['calls']} retries={COST['retries']} in={COST['in_tokens']:,} out={COST['out_tokens']:,} "
                      f"own ${own_cost():.3f}  {time.time() - t0:.0f}s", flush=True)
    save_cache(force=True)
    if stopped:
        print("STOPPED by budget or call cap; the analysis below covers the cached ballots only")
    return not stopped


# ---- analysis ---------------------------------------------------------------------------------------------------------
def copy_votes(u: dict, copy: str) -> list[tuple[int, int, int]] | None:
    if copy in u["votes"]:
        return u["votes"][copy]
    variant, draw = copy.split(".")
    ballots = [CACHE.get(ballot_key(u, variant, int(draw), k)) for k in range(VOTES)]
    if any(b is None for b in ballots):
        return None
    out = []
    for i in range(len(u["assertions"])):
        ms = [b["met"][i] for b in ballots]
        out.append((sum(m is True for m in ms), sum(m is False for m in ms), sum(m is None for m in ms)))
    return out


def nl_verdicts(votes: list[tuple[int, int, int]]) -> dict[str, int]:
    maj = all(vm > vu for vm, vu, vn in votes)
    unan = all(vm == VOTES for vm, vu, vn in votes)
    anyv = all(vm >= 1 for vm, vu, vn in votes)
    return {"majority": int(maj), "unanimous": int(unan), "any": int(anyv)}


def pct(n: int, d: int) -> str:
    return "n/a" if d == 0 else f"{n}/{d} = {100 * n / d:.1f}%"


def analyse(units: list[dict], retail_gate: dict | None, complete: bool) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    verdict_rows, vote_rows = [], []
    per_unit: dict[tuple, dict] = {}
    for u in units:
        copies = ["R"] + (["L"] if "L" in u["votes"] else []) + COPIES
        res = {}
        for c in copies:
            v = copy_votes(u, c)
            if v is None:
                continue
            nv = nl_verdicts(v)
            rew = {k: u["db"] * u["comm"] * x for k, x in nv.items()}
            res[c] = {"nl": nv, "reward": rew, "votes": v}
            verdict_rows.append({"set": u["set"], "domain": u["domain"], "agent": u["agent"], "task_id": u["task_id"], "trial": u["trial"], "copy": c,
                                 "db": u["db"], "comm": u["comm"], "nl_majority": nv["majority"], "nl_unanimous": nv["unanimous"], "nl_any": nv["any"],
                                 "reward_majority": rew["majority"], "reward_unanimous": rew["unanimous"], "reward_any": rew["any"],
                                 "votes": " ".join(f"{vm}-{vu}-{vn}" for vm, vu, vn in v)})
            if c not in ("R", "L"):
                variant, draw = c.split(".")
                for k in range(VOTES):
                    b = CACHE[ballot_key(u, variant, int(draw), k)]
                    for i, a in enumerate(u["assertions"]):
                        vote_rows.append({"set": u["set"], "task_id": u["task_id"], "trial": u["trial"], "copy": c, "vote": k, "assertion_idx": i,
                                          "met": "" if b["met"][i] is None else int(b["met"][i]), "mode": b["modes"][i], "attempts": b["attempts"]})
        per_unit[(u["set"], u["task_id"], u["trial"])] = {"u": u, "res": res}
    with open(OUT / "T3_verdicts.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(verdict_rows[0]))
        w.writeheader()
        w.writerows(verdict_rows)
    if vote_rows:
        with open(OUT / "T3_votes.csv", "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(vote_rows[0]))
            w.writeheader()
            w.writerows(vote_rows)

    L = ["# T3: how much a copy of the judge moves the recorded verdicts (added 2026-11-01)", "",
         f"Definitions, copies and the prediction written before the run: `T3_PLAN.md`. Generated by `scripts/overnight/t3_judge_copies.py` on "
         f"{datetime.now().strftime('%Y-%m-%d %H:%M')} local time from `judge_cache_T3.json` ({len(CACHE)} ballots). "
         + ("All planned ballots present." if complete else "**Incomplete: the judge stage stopped at the budget or call cap; copies with missing ballots are left out for the affected simulations.**"),
         "", f"Judge: {s2.JUDGE_MODEL}, {VOTES} votes per copy, re-ask once on a missing assertion, undetermined counts as unmet. Reference R: airline = the cached V2 verdicts behind the published tables; "
         "retail = the 3-vote majority of the recorded re-judge (check 2j); L = the live single vote of the retail runs. Copies P0 = V2 prompt, P1 = tau2's stock prompt and list format, P2 = paraphrase; .1/.2 = independent draws.", "",
         "Gates: airline, DB x communicate x NL from the reference ballots reproduces the published V2 reward for every simulation (asserted on load)."
         + (f" Retail: {retail_gate['sims']} simulations loaded, majority-vs-live reward flips {retail_gate['majority_vs_live_flips']} (published check 2j: 1)." if retail_gate else ""), ""]
    summary_numbers = {}
    sets = []
    for s in [*AIRLINE_SETS, *RETAIL_SETS]:
        sid = s[0]
        rows = [pu for key, pu in per_unit.items() if key[0] == sid]
        if rows:
            sets.append((sid, s[1], rows))
    for sid, label, rows in sets:
        n = len(rows)
        R = [pu["res"]["R"]["reward"]["majority"] for pu in rows]
        decisive = [pu["u"]["db"] * pu["u"]["comm"] == 1 for pu in rows]
        passes_R, fails_R = sum(R), n - sum(R)
        dec_fails = sum(1 for r, d in zip(R, decisive) if d and not r)
        L += [f"## {sid}: {label}", "",
              f"{n} simulations; judge-decisive (DB and communicate parts pass): {sum(decisive)}; reference passes {passes_R}, fails {fails_R} (judge-decisive fails {dec_fails}).", "",
              "| copy | passes | passes lost (of reference passes) | fails gained (of all reference fails) | fails gained (of judge-decisive fails) | simulations whose verdict differs from R |",
              "|---|---|---|---|---|---|"]
        copies_here = [c for c in (["L"] if "L" in rows[0]["res"] else []) + COPIES if all(c in pu["res"] for pu in rows)]
        flip_vs_R = {}
        for c in copies_here:
            K = [pu["res"][c]["reward"]["majority"] for pu in rows]
            lost = sum(1 for r, k in zip(R, K) if r and not k)
            gained = sum(1 for r, k in zip(R, K) if not r and k)
            diff = sum(1 for r, k in zip(R, K) if r != k)
            flip_vs_R[c] = diff
            L.append(f"| {c} | {sum(K)} | {pct(lost, passes_R)} | {pct(gained, fails_R)} | {pct(gained, dec_fails)} | {pct(diff, n)} |")
        allc = ["R"] + [c for c in copies_here if c != "L"]
        pair_d, pair_dd, npairs = 0.0, 0.0, 0
        for a, b in combinations(allc, 2):
            npairs += 1
            A = [pu["res"][a]["reward"]["majority"] for pu in rows]
            B = [pu["res"][b]["reward"]["majority"] for pu in rows]
            pair_d += sum(1 for x, y in zip(A, B) if x != y) / n
            pair_dd += (sum(1 for x, y, d in zip(A, B, decisive) if d and x != y) / sum(decisive)) if sum(decisive) else 0
        same_prompt = []
        for v in VARIANTS:
            a, b = f"{v}.1", f"{v}.2"
            if a in copies_here and b in copies_here:
                A = [pu["res"][a]["reward"]["majority"] for pu in rows]
                B = [pu["res"][b]["reward"]["majority"] for pu in rows]
                same_prompt.append((v, sum(1 for x, y in zip(A, B) if x != y)))
        by_task = defaultdict(list)
        for pu in rows:
            by_task[pu["u"]["task_id"]].append(pu["res"]["R"]["reward"]["majority"])
        tp, td = 0, 0
        for t, vals in by_task.items():
            for x, y in combinations(vals, 2):
                tp += 1
                td += x != y
        L += ["", (f"Judge-copy flip rate (pairwise, {npairs} pairs among R and the {len(allc) - 1} judge copies): {100 * pair_d / npairs:.1f}% of simulations per pair"
                   + (f", {100 * pair_dd / npairs:.1f}% of judge-decisive simulations" if sum(decisive) else "") + ". " if npairs else "")
              + ("Same prompt, other draw: " + ", ".join(f"{v} {pct(d, n)}" for v, d in same_prompt) + ". " if same_prompt else "")
              + (f"Run-to-run spread of the agent under R (pairs of trials of the same task): {pct(td, tp)} of trial pairs disagree." if tp else "Run-to-run spread: one trial per task, not defined.")]
        L += ["", "Pass threshold per assertion (same ballots): reference rule = majority of 3.", "",
              "| ballots | majority passes | unanimous passes (lost vs majority) | any-vote passes (gained vs majority) |", "|---|---|---|---|"]
        for c in ["R"] + [c for c in copies_here if c != "L"]:
            M = [pu["res"][c]["reward"]["majority"] for pu in rows]
            U = [pu["res"][c]["reward"]["unanimous"] for pu in rows]
            A = [pu["res"][c]["reward"]["any"] for pu in rows]
            lostU = sum(1 for m, x in zip(M, U) if m and not x)
            gainA = sum(1 for m, x in zip(M, A) if not m and x)
            # a pass lost under the unanimous rule without any unmet vote: an undetermined ballot (the reference carries a few from the old parser gap)
            undet_only = sum(1 for pu, m, x in zip(rows, M, U) if m and not x and all(vu == 0 for vm, vu, vn in pu["res"][c]["votes"]))
            note = f"; {undet_only} of them with no unmet vote, only an undetermined ballot" if undet_only else ""
            L.append(f"| {c} | {sum(M)} | {sum(U)} ({pct(lostU, sum(M))}{note}) | {sum(A)} ({pct(gainA, n - sum(M))}) |")
        if rows[0]["u"]["domain"] == "airline":
            onF = sum(1 for pu in rows if pu["res"]["R"]["reward"]["majority"] and pu["u"]["task_id"] in REFUSAL_FLOOR)
            stock = [pu["u"]["stock_reward"] for pu in rows]
            n_stock = sum(1 for x in stock if x == 1.0)
            onE = sum(1 for pu, sr in zip(rows, stock) if sr == 1.0 and pu["u"]["task_id"] in EMPTY_FLOOR)
            L += ["", f"Floor definition: under V2 the empty conversation passes 0 tasks (nothing excluded); taking the refusal-only agent as the floor ({len(REFUSAL_FLOOR)} tasks) "
                  f"removes {pct(onF, passes_R)} of the reference passes from the credited count. Under the stock scorer the same simulations pass {n_stock} times; "
                  f"with the empty conversation as the floor ({len(EMPTY_FLOOR)} tasks) {pct(onE, n_stock)} of those passes fall on floor tasks."]
        L.append("")
        summary_numbers[sid] = {"n": n, "decisive": sum(decisive), "passes_R": passes_R, "flip_vs_R": flip_vs_R, "pair_flip_pct": round(100 * pair_d / npairs, 2) if npairs else None,
                                "pair_flip_decisive_pct": round(100 * pair_dd / npairs, 2) if npairs and sum(decisive) else None,
                                "same_prompt_flips": same_prompt, "trial_pairs_disagree": [td, tp]}

    def agg(domain: str, kind: str) -> str:
        num = den = 0
        for sid, label, rows in sets:
            if rows[0]["u"]["domain"] != domain:
                continue
            dec = sum(1 for pu in rows if pu["u"]["db"] * pu["u"]["comm"] == 1)
            R = [pu["res"]["R"]["reward"]["majority"] for pu in rows]
            same = SAME_PROMPT[domain]
            cs = [c for c in COPIES if c.startswith(same)] if kind == "redraw" else [c for c in COPIES if not c.startswith(same)]
            cs = [c for c in cs if all(c in pu["res"] for pu in rows)]
            for c in cs:
                K = [pu["res"][c]["reward"]["majority"] for pu in rows]
                num += sum(1 for pu, r, k in zip(rows, R, K) if pu["u"]["db"] * pu["u"]["comm"] == 1 and r != k)
                den += dec
        return pct(num, den)

    def agg_thr(domain: str, which: str) -> str:
        num = den = 0
        for sid, label, rows in sets:
            if rows[0]["u"]["domain"] != domain:
                continue
            M = [pu["res"]["R"]["reward"]["majority"] for pu in rows]
            X = [pu["res"]["R"]["reward"][which] for pu in rows]
            if which == "unanimous":
                num += sum(1 for m, x in zip(M, X) if m and not x)
                den += sum(M)
            else:
                dec_f = [pu["u"]["db"] * pu["u"]["comm"] == 1 and not m for pu, m in zip(rows, M)]
                num += sum(1 for d, x in zip(dec_f, X) if d and x)
                den += sum(dec_f)
        return pct(num, den)

    spread = []
    for sid, label, rows in sets:
        td, tp = summary_numbers[sid]["trial_pairs_disagree"]
        if tp:
            spread.append(f"{sid} {pct(td, tp)}")

    def undet_only_losses(domain: str) -> str:
        num = den = 0
        for sid, label, rows in sets:
            if rows[0]["u"]["domain"] != domain:
                continue
            for pu in rows:
                r = pu["res"]["R"]
                if r["reward"]["majority"] and not r["reward"]["unanimous"]:
                    den += 1
                    num += all(vu == 0 for vm, vu, vn in r["votes"])
        return f"{num} of the {den} lost passes have no unmet vote, only an undetermined ballot in the reference"

    def p1_direction() -> str:
        lost = gained = 0
        for sid, label, rows in sets:
            if rows[0]["u"]["domain"] != "airline":
                continue
            R = [pu["res"]["R"]["reward"]["majority"] for pu in rows]
            for c in ("P1.1", "P1.2"):
                if not all(c in pu["res"] for pu in rows):
                    continue
                K = [pu["res"][c]["reward"]["majority"] for pu in rows]
                lost += sum(1 for r, k in zip(R, K) if r and not k)
                gained += sum(1 for r, k in zip(R, K) if not r and k)
        return f"passes lost {lost}, fails gained {gained} (two P1 copies, five airline sets)"

    # cost of the judge run that produced the cache: kept across offline reruns (--no-judge makes no call)
    prev = json.loads((OUT / "T3_provenance.json").read_text(encoding="utf-8")) if (OUT / "T3_provenance.json").exists() else {}
    judge_run = {"calls": COST["calls"], "new_ballots": COST["new_ballots"], "own_cost_usd": round(own_cost(), 4), "run_finished": datetime.now().isoformat(timespec="minutes")} if COST["calls"] else prev.get("judge_run", {})
    if not judge_run and COST_PATH.exists():  # fall back to the cost ledger row of the judge run
        for line in COST_PATH.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 8 and "t3_judge_copies.py" in cells[2] and cells[4].split(" ")[0].isdigit():
                m = re.search(r"(\d+) new ballots", cells[8])
                judge_run = {"calls": int(cells[4].split(" ")[0]), "new_ballots": int(m.group(1)) if m else "n/a", "own_cost_usd": float(cells[6]), "run_finished": cells[1], "source": "cost_overnight.md"}
    L += ["## Prediction (T3_PLAN.md) next to the result", "",
          "Same-prompt copy: P0 for airline (the reference is the V2 prompt), P1 for retail (the reference re-judge used tau2's stock prompt); the plan's retail lines were written before this distinction was drawn (see the note at the end of T3_PLAN.md).", "",
          "| quantity | predicted | measured (judge-decisive simulations, all sets of the domain pooled) |", "|---|---|---|",
          f"| airline, same prompt new draw (P0) : verdicts changed vs R | 2 to 4% | {agg('airline', 'redraw')} |",
          f"| airline, other wording (P1, P2) vs R | 4 to 8% | {agg('airline', 'wording')} |",
          f"| airline, P1 loses more passes than it gains fails | direction only | {p1_direction()} |",
          f"| airline, unanimous threshold: reference passes lost | 5 to 10% | {agg_thr('airline', 'unanimous')}; {undet_only_losses('airline')} |",
          f"| airline, any-vote threshold: judge-decisive fails gained | 10 to 20% | {agg_thr('airline', 'any')} |",
          f"| run-to-run spread under R (trial pairs that disagree) | 15 to 30% | {'; '.join(spread)} |",
          f"| retail, same prompt new draw (P1) vs R | 1 to 3% | {agg('retail', 'redraw')} |",
          f"| retail, other wording (P0, P2) vs R | 3 to 6% | {agg('retail', 'wording')} |",
          f"| judge calls / own cost | about 9,350 / 9 to 12 USD | {judge_run.get('calls', 'n/a')} calls, {judge_run.get('new_ballots', 'n/a')} ballots, ${judge_run.get('own_cost_usd', 0):.2f} (run finished {judge_run.get('run_finished', 'n/a')}; this analysis made {COST['calls']} calls) |", "",
          "## Scope and what the author must check by hand before using any number", "",
          f"- Scope: one judge model ({s2.JUDGE_MODEL}), three wordings, two draws each, the V2 transcript view for airline and the stock view for retail, the tolerant parser everywhere; the judge model itself was not varied. "
          "Sets A1, A3 and A4 have 1, 0 and 8 judge-decisive fails, so copies there can almost only lose passes.",
          "- The paraphrase prompt (P2) is this script's text; read it once and decide whether it says the same as tau2's prompt.",
          "- P1 reproduces tau2's stock prompt and list format but keeps the V2 transcript view for airline and the tolerant parser everywhere; it is a wording copy, not a replay of the stock evaluator.",
          "- The reference R for retail is the 3-vote majority of check 2j, not the live single vote that produced the published retail numbers; L is that live vote (one ballot, so its unanimous and any-vote columns equal its majority column).",
          "- Nothing here changes a published number: the published tables stay as they are; this file reports how far copies of the judge move the same recorded verdicts.", ""]
    (OUT / "T3_sensitivity.md").write_text("\n".join(L), encoding="utf-8")
    (OUT / "T3_provenance.json").write_text(json.dumps({"generated": datetime.now().isoformat(timespec="minutes"), "judge_model": s2.JUDGE_MODEL, "judge_args": s2.JUDGE_ARGS, "votes": VOTES, "retries": RETRIES,
                                                        "variants": {k: {"prompt_sha256": hashlib.sha256(v[0].encode()).hexdigest()[:16], "format": v[1]} for k, v in VARIANTS.items()},
                                                        "same_prompt_copy": SAME_PROMPT, "airline_view": s2.JUDGE_VIEW, "retail_view": "stock",
                                                        "reference": {"airline": "cached V2 verdicts in results/v2/rescore*.csv (V2_nl_detail)", "retail": "3-vote majority in results/retail/judge_cache_rejudge.json"},
                                                        "overlay_commit": s2.git_state()[0], "judge_run": judge_run, "cost_this_analysis": COST,
                                                        "complete": complete, "summary": summary_numbers}, indent=1, default=str), encoding="utf-8")
    print("\n".join(L[-14:]))


def cost_row(sets: str) -> None:
    if not COST_PATH.exists():
        COST_PATH.write_text("# API cost log — overnight 2026-11-01 (own estimates from token counts, $0.10/$0.50 per MTok for claude-haiku-5-5, cache ignored; the convention of cost.md)\n\n"
                             "| date (local) | run | model | calls | in / out tokens | own estimate (USD) | cumulative own estimate (USD) | note |\n|---|---|---|---|---|---|---|---|\n", encoding="utf-8")
    prev = 0.0
    for line in COST_PATH.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 7 and cells[1][:4].isdigit():
            try:
                prev = float(cells[7])
            except ValueError:
                pass
    cum = prev + own_cost()
    with open(COST_PATH, "a", encoding="utf-8") as fp:
        fp.write(f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | `scripts/overnight/t3_judge_copies.py --sets {sets}` | {s2.JUDGE_MODEL} (judge) | {COST['calls']} ({COST['retries']} re-asks) | "
                 f"{COST['in_tokens']:,} / {COST['out_tokens']:,} | {own_cost():.3f} | {cum:.3f} | {COST['new_ballots']} new ballots, {COST['cached_ballots']} from cache |\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", choices=["airline", "retail", "all"], default="all")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-usd", type=float, default=30.0)
    ap.add_argument("--max-calls", type=int, default=20000)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if CACHE_PATH.exists():
        CACHE.update(json.loads(CACHE_PATH.read_text(encoding="utf-8")))
    units, gate = [], None
    if args.sets in ("airline", "all"):
        units += airline_units()
    if args.sets in ("retail", "all"):
        ru, gate = retail_units()
        units += ru
    print(f"units: {len(units)} ({dict(Counter(u['set'] for u in units))})")
    complete = True
    if not args.no_judge:
        complete = judge_stage(units, args.workers, args.budget_usd, args.max_calls, args.dry)
        if args.dry:
            return 0
    else:
        complete = all(ballot_key(u, v, d, k) in CACHE for u in units for v in VARIANTS for d in DRAWS for k in range(VOTES))
    analyse(units, gate, complete)
    if COST["calls"]:
        cost_row(args.sets)
    print(f"written {OUT.relative_to(ROOT)}/T3_sensitivity.md, T3_verdicts.csv, T3_votes.csv, T3_provenance.json; calls {COST['calls']}, own ${own_cost():.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
