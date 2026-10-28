"""Check 2j for retail: how much of the official score is the judge?

(a) Parser: over every live judge reply recorded by the runs (results/retail/runs/*/judge_calls.json) and by the probes,
    the share the stock strict `json.loads` would have rejected (`strict_ok` = 0).
(b) Re-judge: every fresh simulation that ended normally and whose task has reward-gating `nl_assertions` is judged
    again 3 times with the stock evaluator (same prompt, same model via the overlay). Per assertion: the live single
    vote vs the majority of the 3 new votes; per simulation: the live NL reward vs the majority NL reward and the
    resulting reward flip (DB part unchanged). Votes are cached in results/retail/judge_cache_rejudge.json.
Outputs: results/retail/rejudge.csv (per simulation x assertion), rejudge_summary.md / .json.
SPENDS MONEY (own estimate: a few tenths of a dollar). Run from inside tau2-bench:
    uv run --no-sync python ../scripts/retail/rejudge.py [--votes 3] [--dry]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
RES = ROOT / "results" / "retail"
CACHE = RES / "judge_cache_rejudge.json"

import judge_overlay as jo  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402

RUNS = ["retail_pass3_haiku", "retail_gt_haiku"]


def strict_share() -> dict:
    files = [RES / "runs" / r / "judge_calls.json" for r in RUNS] + [RES / "judge_calls_noop.json"]
    tot = {"calls": 0, "strict_rejected": 0, "results_short": 0, "files": []}
    for f in files:
        if not f.exists():
            continue
        calls = json.loads(f.read_text(encoding="utf-8"))
        tot["files"].append(str(f.relative_to(ROOT)).replace("\\", "/"))
        tot["calls"] += len(calls)
        tot["strict_rejected"] += sum(1 for c in calls if not c.get("strict_ok"))
        tot["results_short"] += sum(1 for c in calls if c.get("n_results", 0) < c.get("n_assertions", 0))
    return tot


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--votes", type=int, default=3)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    jo.install()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    rows, per_sim = [], []
    for run in RUNS:
        p = RES / "runs" / run / "results.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        tasks = {str(t["id"]): t for t in data["tasks"]}
        for s in data["simulations"]:
            if str(s.get("termination_reason")) not in {"agent_stop", "user_stop"}:
                continue
            t = tasks[str(s["task_id"])]
            ec = t["evaluation_criteria"]
            nl = ec.get("nl_assertions") or []
            if not nl or "NL_ASSERTION" not in (ec.get("reward_basis") or []):
                continue
            ri = s.get("reward_info") or {}
            live = {c["nl_assertion"]: c["met"] for c in (ri.get("nl_assertions") or [])}
            traj = [SimpleNamespace(role=m["role"], content=m.get("content")) for m in s["messages"]]
            key = hashlib.sha256(("\n".join(f"{m.role}: {m.content}" for m in traj) + json.dumps(nl)).encode("utf-8")).hexdigest()
            ballots = cache.get(key)
            if ballots is None and not args.dry:
                ballots = []
                for _ in range(args.votes):
                    checks = NLAssertionsEvaluator.evaluate_nl_assertions(traj, nl)
                    jo.drain()
                    ballots.append({c.nl_assertion: c.met for c in checks})
                cache[key] = ballots
                CACHE.write_text(json.dumps(cache), encoding="utf-8")
            if ballots is None:
                continue
            live_nl = 1.0 if all(live.get(a) is True for a in nl) and len(live) >= len(nl) else 0.0
            maj_all = True
            for i, a in enumerate(nl):
                votes = [b.get(a) for b in ballots]
                # fall back to position when the judge paraphrased the assertion text
                if all(v is None for v in votes):
                    votes = [list(b.values())[i] if i < len(b) else None for b in ballots]
                vm, vu = sum(v is True for v in votes), sum(v is False for v in votes)
                maj = True if vm > vu else False if vu > vm else None
                live_met = live.get(a)
                if live_met is None and i < len(ri.get("nl_assertions") or []):
                    live_met = (ri["nl_assertions"][i] or {}).get("met")
                maj_all = maj_all and maj is True
                rows.append({"run": run, "task_id": t["id"], "trial": s.get("trial"), "sim_id": s.get("id"), "assertion_idx": i, "assertion": a[:80],
                             "live_met": live_met, "votes_met": vm, "votes_unmet": vu, "votes_missing": len(votes) - vm - vu,
                             "majority_met": maj, "flip": int(maj is not None and live_met is not None and maj != live_met),
                             "live_omitted": int(live_met is None)})
            db_ok = bool((ri.get("db_check") or {}).get("db_match"))
            maj_nl = 1.0 if maj_all else 0.0
            per_sim.append({"run": run, "task_id": t["id"], "trial": s.get("trial"), "db_match": db_ok, "live_reward": ri.get("reward"),
                            "live_nl": live_nl, "majority_nl": maj_nl,
                            "majority_reward": (1.0 if db_ok else 0.0) * maj_nl, "live_omitted_any": int(any(live.get(a) is None for a in nl))})
    with open(RES / "rejudge.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()) if rows else ["run"])
        w.writeheader()
        w.writerows(rows)
    tot = jo.totals()
    strict = strict_share()
    flips = sum(r["flip"] for r in rows)
    rf = [p for p in per_sim if p["live_reward"] is not None and float(p["live_reward"]) != p["majority_reward"]]
    summ = {"strict_parser": strict, "rejudge": {"simulations": len(per_sim), "assertion_verdicts": len(rows), "assertion_flips": flips,
                                                "live_omitted_assertions": sum(r["live_omitted"] for r in rows),
                                                "reward_flips": len(rf), "pass_to_fail": sum(1 for p in rf if float(p["live_reward"]) == 1.0),
                                                "fail_to_pass": sum(1 for p in rf if float(p["live_reward"]) != 1.0),
                                                "flipped": [{k: p[k] for k in ("run", "task_id", "trial", "live_reward", "majority_reward")} for p in rf],
                                                "votes": args.votes, "judge_calls": tot["calls"], "in_tokens": tot["in_tokens"], "out_tokens": tot["out_tokens"],
                                                "own_estimate_usd": round(tot["own_estimate_usd"], 4)}}
    (RES / "rejudge_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    L = ["# Check 2j, retail: the judge inside the official score", "",
         f"(a) Stock strict parser over the live judge replies: {strict['strict_rejected']}/{strict['calls']} replies would have been rejected "
         f"(files: {', '.join(strict['files'])}); replies with fewer results than assertions: {strict['results_short']}.", "",
         f"(b) Re-judge with {args.votes} votes (same prompt, same model): {len(per_sim)} simulations, {len(rows)} assertion verdicts; "
         f"live vote != majority on {flips} assertions; live verdict omitted an assertion {sum(r['live_omitted'] for r in rows)} times; "
         f"reward flips: {len(rf)} (pass->fail {summ['rejudge']['pass_to_fail']}, fail->pass {summ['rejudge']['fail_to_pass']}).", ""]
    for p in rf:
        L.append(f"- {p['run']} task {p['task_id']} trial {p['trial']}: live reward {p['live_reward']} -> majority {p['majority_reward']} (db_match={p['db_match']})")
    L += ["", f"judge calls this run: {tot['calls']}; tokens in/out {tot['in_tokens']}/{tot['out_tokens']}; own estimate ${tot['own_estimate_usd']:.3f}"]
    (RES / "rejudge_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
