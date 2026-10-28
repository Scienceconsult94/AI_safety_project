"""Check 2j (checklist.md): does the choice of communicate scorer change the verdict?

Every recorded simulation on the stock airline tasks whose task has non-empty `communicate_info` is scored twice on
its communicate part: with the substring scorer the runs used, and with tau2's semantic scorer, judge
anthropic/claude-haiku-5-5 with model_args {} (the checklist's 2j method; the stock default judge, gpt-5.5, is an
OpenAI model and is not used). The semantic scorer runs in `--passes` independent passes; its verdict per fact is
the majority. The same is done for the empty trajectory of every such task (null agent): it tests that the
null-agent floor does not depend on the scorer. Tasks without `communicate_info` pass under both scorers without a
check (evaluator_communicate.py), so their 2j row is decided by construction.

Note: the semantic judge reads assistant AND user text; the substring scorer reads assistant text only.

Inputs  results/runs/*.results.json listed in RUNS (missing files are skipped)
Outputs results/probe_2j.csv     one row per simulation x fact (substring, every semantic pass, majority)
        results/probe_2j.md      per-task summary, the null agent, the 2j verdicts
        results/review_2j.csv    one 2j row per airline task for build_audit_log.py (task_id,check,defect,...)
        results/judge_cache_2j.json  judge verdicts; a re-run replays them without calls
Run from inside tau2-bench (tau2 venv; .env is read by tau2 for the judge):
    uv run --no-sync python ../scripts/probe_2j.py [--passes 3] [--no-judge] [--workers 4]
SPENDS MONEY (judge calls; well below $0.5 for all runs).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
RES = ROOT / "results"
CACHE = RES / "judge_cache_2j.json"
RUNS = {  # label -> recorded run on the stock airline tasks (substring scorer)
    "haiku_sample20": "sample20_pass3_haiku.results.json",
    "gt_sample20": "sample20_gt_haiku.results.json",
    "sonnet_sample20": "sample20_sonnet_t3.results.json",
    "haiku_rest30": "rest30_pass3_haiku.results.json",
    "gt_rest30": "rest30_gt_haiku.results.json",
}
JUDGE = {"model": "anthropic/claude-haiku-5-5", "model_args": {}}

from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

SUBSTRING = CommunicateScoring(scorer=CommunicateScorer.SUBSTRING)
SEMANTIC = CommunicateScoring.model_validate({"scorer": "semantic", "judge": JUDGE})
_lock = threading.Lock()


def load_cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def semantic_vote(cache: dict, key: str, messages, fact: str, no_judge: bool):
    """One semantic verdict for one fact, cached by key; None when not available (no judge, or a failed reply)."""
    with _lock:
        if key in cache:
            return cache[key]["met"]
    if no_judge:
        return None
    try:
        check = CommunicateEvaluator.evaluate_communicate_info(messages, [fact], scoring=SEMANTIC)[0]
        rec = {"met": bool(check.met), "justification": check.justification}
    except Exception as exc:  # a reply that fails validation counts as undetermined, as in block 2
        rec = {"met": None, "justification": f"error: {type(exc).__name__}: {exc}"[:500]}
    with _lock:
        cache[key] = rec
    return rec["met"]


def majority(votes: list) -> bool | None:
    det = [v for v in votes if v is not None]
    if not det:
        return None
    met = sum(det)
    if met * 2 == len(det):
        return None
    return met * 2 > len(det)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    tasks = {t.id: t for t in registry.get_tasks_loader("airline")(None)}
    info = {tid: list((t.evaluation_criteria.communicate_info or []) if t.evaluation_criteria else []) for tid, t in tasks.items()}
    cache = load_cache()

    # (label, agent, task_id, trial, sim_id, messages, recorded_reward)
    sims = []
    for label, fn in RUNS.items():
        p = RES / "runs" / fn
        if not p.exists():
            print(f"missing {p.name} - skipped")
            continue
        res = Results.load(p)
        assert res.info.effective_communicate_scoring.scorer == CommunicateScorer.SUBSTRING, f"{fn}: not a substring run"
        for s in res.simulations:
            if info.get(s.task_id):
                rr = s.reward_info.reward if s.reward_info else None
                sims.append((label, label.split("_")[0], s.task_id, s.trial, s.id, list(s.messages or []), rr))
    for tid in sorted((t for t in info if info[t]), key=int):  # the null agent: empty trajectory
        sims.append(("null", "null", tid, 0, f"null_{tid}", [], None))

    jobs = []
    for label, agent, tid, trial, sid, msgs, rr in sims:
        for fact in info[tid]:
            for k in range(args.passes):
                jobs.append((f"{label}|{sid}|{fact}|{k}", msgs, fact))
    todo = [j for j in jobs if j[0] not in cache]
    print(f"simulations {len(sims)}, judge verdicts {len(jobs)}, cached {len(jobs) - len(todo)}, to call {0 if args.no_judge else len(todo)}")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(semantic_vote, cache, key, msgs, fact, args.no_judge) for key, msgs, fact in todo]
        for i, f in enumerate(as_completed(futs), 1):
            f.result()
            if i % 25 == 0:
                print(f"  {i}/{len(futs)}")
            if i % 25 == 0 and not args.no_judge:
                with _lock:
                    CACHE.write_text(json.dumps(cache, indent=0, ensure_ascii=False), encoding="utf-8")
    if not args.no_judge:
        CACHE.write_text(json.dumps(cache, indent=0, ensure_ascii=False), encoding="utf-8")

    rows = []
    for label, agent, tid, trial, sid, msgs, rr in sims:
        sub = {c.info: c.met for c in CommunicateEvaluator.evaluate_communicate_info(msgs, info[tid], scoring=SUBSTRING)}
        for fact in info[tid]:
            votes = [cache.get(f"{label}|{sid}|{fact}|{k}", {}).get("met") for k in range(args.passes)]
            maj = majority(votes)
            rows.append({"run": label, "agent": agent, "task_id": tid, "trial": trial, "sim_id": sid, "fact": fact,
                         "recorded_reward": "" if rr is None else rr, "substring_met": int(sub[fact]),
                         **{f"semantic_{k + 1}": "" if v is None else int(v) for k, v in enumerate(votes)},
                         "semantic_majority": "" if maj is None else int(maj),
                         "unanimous": int(len(set(votes)) == 1 and votes[0] is not None),
                         "differs": "" if maj is None else int(maj != sub[fact])})
    with open(RES / "probe_2j.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # per task: the recorded runs and the null agent
    by = defaultdict(list)
    for r in rows:
        by[r["task_id"]].append(r)
    L = ["# Check 2j: substring vs semantic communicate scorer (airline, stock tasks)", "",
         f"Judge `{JUDGE['model']}`, model_args {{}}, {args.passes} passes per fact, verdict = majority (a tie or no "
         "determined vote is undetermined). The semantic judge reads assistant and user text; the substring scorer reads "
         "assistant text only. Runs: " + ", ".join(f"`{RUNS[k]}`" for k in RUNS if (RES / 'runs' / RUNS[k]).exists()) + ".", "",
         "| task | communicate_info | facts judged (recorded runs) | substring met | semantic met | differ | undetermined | not unanimous | null agent: substring / semantic |",
         "|---|---|---|---|---|---|---|---|---|"]
    review = []
    for tid in sorted(tasks, key=int):
        if not info[tid]:
            review.append({"task_id": tid, "check": "2j", "defect": 0, "severity": "",
                           "evidence": "communicate_info = []: both scorers return COMMUNICATE 1.0 without a check (evaluator_communicate.py)",
                           "note": "by construction"})
            continue
        rec = [r for r in by[tid] if r["run"] != "null"]
        nul = [r for r in by[tid] if r["run"] == "null"]
        diff = [r for r in rec if r["differs"] == 1]
        und = [r for r in rec if r["semantic_majority"] == ""]
        nonu = [r for r in rec if r["unanimous"] == 0]
        null_sub = all(r["substring_met"] == 1 for r in nul)
        null_sem = all(r["semantic_majority"] == 1 for r in nul)
        L.append(f"| {tid} | {info[tid]} | {len(rec)} | {sum(r['substring_met'] for r in rec)} | "
                 f"{sum(r['semantic_majority'] == 1 for r in rec)} | {len(diff)} | {len(und)} | {len(nonu)} | "
                 f"{'pass' if null_sub else 'fail'} / {'pass' if null_sem else 'fail' if all(r['semantic_majority'] == 0 for r in nul) else 'undetermined'} |")
        ev = (f"results/probe_2j.csv: {len(rec)} recorded fact verdicts, {len(diff)} differ "
              + ("(" + "; ".join(f"{r['run']} t{r['trial']} '{r['fact']}': substring {r['substring_met']}, semantic {r['semantic_majority']}" for r in diff[:6]) + ")" if diff else "")
              + f"; {len(und)} undetermined; null agent substring {int(null_sub)}, semantic {int(null_sem)}")
        review.append({"task_id": tid, "check": "2j", "defect": int(bool(diff)), "severity": "medium" if diff else "",
                       "evidence": ev, "note": f"semantic judge {JUDGE['model']} (substitute for the stock gpt-5.5), {args.passes} passes, majority"})
    nd = sum(r["differs"] == 1 for r in rows if r["run"] != "null")
    L += ["", f"Recorded fact verdicts that differ between the scorers: {nd} of {sum(r['run'] != 'null' for r in rows)}.",
          f"Tasks with a 2j defect (any differing trial): {[r['task_id'] for r in review if r['defect'] == 1]}.", ""]
    (RES / "probe_2j.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(RES / "review_2j.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=["task_id", "check", "defect", "severity", "evidence", "note"])
        w.writeheader()
        w.writerows(review)
    print("\n".join(L[-3:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
