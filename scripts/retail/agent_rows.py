"""Retail agent runs -> audit rows and review material (the retail reading of scripts/agent_rows.py).

Inputs:
  retail/sample.json                                   task ids, bench_commit
  results/retail/static_scan.csv                       gt_eligible, n_write, nl_count per task
  results/retail/runs/retail_pass3_haiku/results.json  three Haiku trials per task (stock scorer, judge substituted)
  results/retail/runs/retail_gt_haiku/results.json     one ground-truth-agent trial per eligible task
  results/retail/run_retail_all.log                    console log, scanned for replay mismatches
Outputs (results/retail/):
  haiku_pass.csv            rows for 1e, 1f, 5c, 5e, 5f (per task) and 6e (ALL); columns task_id,check,haiku_pass,defect,severity,evidence,note
  agent_runs_summary.md     per-task table, pass^k, judge-only failures, terminations, token-based cost estimate
  agent_triage.md           every failed or flipped trajectory with pointers for the manual review (4f, 5c, 5d, 1e triage)
  trajectories/<task>_<src>_t<trial>.md   readable transcripts of those trajectories
Rows that need a reading (4f, 5d, 1e/5c triage) are written as defect=0 with the note "REVIEW"; the reviewer's verdicts go
to results/retail/review_agent.csv, which build_audit_log.py reads last.
Usage (from ==Project):  python -I scripts/retail/agent_rows.py
No LLM calls, nothing under tau2-bench/ is modified.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "retail"
RUNS = RES / "runs"
sys.path.insert(0, str(ROOT / "scripts"))
from agent_rows import render_transcript  # noqa: E402  (block-1 transcript renderer, domain-neutral)

NORMAL = {"agent_stop", "user_stop"}
ABNORMAL = {"timeout", "max_steps", "too_many_errors"}
PRICE_IN, PRICE_OUT = 0.10 / 1e6, 0.50 / 1e6
COLS = ["task_id", "check", "haiku_pass", "defect", "severity", "evidence", "note"]
P3, GT = "retail_pass3_haiku", "retail_gt_haiku"


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = {str(t["id"]): t for t in data.get("tasks", [])}
    out = []
    for s in data.get("simulations", []):
        s["_file"] = str(path.relative_to(ROOT)).replace("\\", "/")
        s["_task"] = tasks.get(str(s.get("task_id")))
        out.append(s)
    return out


def facts(s: dict) -> dict:
    ri = s.get("reward_info") or {}
    db = ri.get("db_check") or {}
    nl = ri.get("nl_assertions")
    nl_fail = [c.get("nl_assertion", "")[:70] for c in (nl or []) if c.get("met") is False]
    usage_in = usage_out = n_tool_calls = 0
    for m in s.get("messages", []):
        u = m.get("usage") or {}
        usage_in += int(u.get("prompt_tokens") or 0)
        usage_out += int(u.get("completion_tokens") or 0)
        n_tool_calls += len(m.get("tool_calls") or [])
    reward = ri.get("reward")
    return {"task_id": str(s.get("task_id")), "trial": s.get("trial"), "reward": reward, "has_reward_info": bool(s.get("reward_info")),
            "db_match": db.get("db_match"), "nl_checked": len(nl or []), "nl_fail": nl_fail,
            "judge_only_fail": bool(db.get("db_match")) and reward is not None and float(reward) != 1.0 and bool(nl_fail),
            "termination": str(s.get("termination_reason")), "n_msgs": len(s.get("messages", [])), "n_tool_calls": n_tool_calls,
            "usage_in": usage_in, "usage_out": usage_out, "file": s["_file"], "sim_id": s.get("id")}


def main() -> int:
    sample = json.loads((ROOT / "retail" / "sample.json").read_text(encoding="utf-8"))
    ids = [str(i) for i in sample["task_ids"]]
    with open(RES / "static_scan.csv", encoding="utf-8", newline="") as fp:
        scan = {r["task_id"]: r for r in csv.DictReader(fp)}
    p3_sims = load_results(RUNS / P3 / "results.json")
    gt_sims = load_results(RUNS / GT / "results.json")
    p3 = [facts(s) for s in p3_sims]
    gt = {facts(s)["task_id"]: facts(s) for s in gt_sims}
    by_task: dict[str, list[dict]] = defaultdict(list)
    for f in p3:
        by_task[f["task_id"]].append(f)
    for v in by_task.values():
        v.sort(key=lambda x: (x["trial"] is None, x["trial"]))

    log_hits: dict[str, list[str]] = defaultdict(list)
    lp = RES / "run_retail_all.log"
    if lp.exists():
        pat = re.compile(r"replay|mismatch|strict|set_state", re.I)
        for line in lp.read_text(encoding="utf-8", errors="replace").replace("\r", "\n").splitlines():
            if (pat.search(line) and "ERROR" in line) or "mismatch" in line.lower():
                m = re.search(r"[Tt]ask (\d+)", line)
                log_hits[m.group(1) if m else "ALL"].append(line.strip()[:200])

    rows, triage = [], []
    traj_dir = RES / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    infra = sum(1 for f in p3 if f["termination"] == "infrastructure_error") + sum(1 for f in gt.values() if f["termination"] == "infrastructure_error")

    def add(task_id, check, defect, severity, evidence, note="", hp=""):
        rows.append({"task_id": task_id, "check": check, "haiku_pass": hp, "defect": int(defect), "severity": severity if defect else "",
                     "evidence": evidence, "note": note})

    summary = ["# Retail agent runs (claude-haiku-5-5 agent and user; stock scorer, NL judge claude-haiku-5-5 in the loop)", "",
               f"pass3 dir: `{P3}`; gt dir: `{GT}`; infrastructure_error simulations: {infra}", "",
               "| task | n_write | nl | pass3 rewards | haiku_pass | judge-only fails | terminations | gt_eligible | gt reward | gt db_match | gt nl unmet |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
    judge_only_trials = 0
    for tid in ids:
        trials = [f for f in by_task.get(tid, []) if f["termination"] != "infrastructure_error"]
        rewards = [f["reward"] for f in trials]
        k = sum(1 for r in rewards if r == 1.0)
        n = len(trials)
        hp = f"{k}/{n}" if n else ""
        terms = [f["termination"] for f in by_task.get(tid, [])]
        jo = sum(1 for f in trials if f["judge_only_fail"])
        judge_only_trials += jo
        sc = scan.get(tid, {})
        elig = sc.get("gt_eligible") == "1"
        g = gt.get(tid)
        summary.append(f"| {tid} | {sc.get('n_write', '?')} | {sc.get('nl_count', '?')} | {' '.join('1' if r == 1.0 else '0' if r == 0.0 else '?' for r in rewards) or '-'} | {hp or '-'} | {jo} | "
                       f"{', '.join(terms) or '-'} | {int(elig)} | {g['reward'] if g else '-'} | {g['db_match'] if g else '-'} | {len(g['nl_fail']) if g else '-'} |")
        ev_p3 = f"{P3}: rewards={rewards} terminations={terms} msgs={[f['n_msgs'] for f in by_task.get(tid, [])]} judge_only_fails={jo}"
        add(tid, "1f", 0, "", ev_p3, note="haiku_pass = successes/evaluated trials; NL judge claude-haiku-5-5 in the loop" if n else "no evaluated trial", hp=hp)
        if not elig:
            add(tid, "1e", 0, "", "static_scan gt_eligible=0 (no reference actions); llm_agent_gt skips the task (registry task_filter)", note="n/a")
        elif g is None:
            add(tid, "1e", 0, "", f"{GT}: no simulation for this task", note="REVIEW: missing GT run")
        else:
            ev = (f"{GT}: reward={g['reward']} db_match={g['db_match']} nl_unmet={g['nl_fail'] or '-'} termination={g['termination']} "
                  f"msgs={g['n_msgs']} tool_calls={g['n_tool_calls']}")
            if g["reward"] == 1.0:
                add(tid, "1e", 0, "", ev)
            else:
                cause = "judge failed an assertion while the DB matched" if g["judge_only_fail"] else "DB did not match"
                add(tid, "1e", 1, "high", ev, note=f"PROVISIONAL (mechanical, {cause}): REVIEW whether the cause is the task, the judge, or an agent slip")
                triage.append(f"- task {tid}, GT run: {ev} -> `results/retail/trajectories/{tid}_gt_t{g['trial']}.md`")
                for s in gt_sims:
                    if str(s.get("task_id")) == tid:
                        render_transcript(s, traj_dir / f"{tid}_gt_t{s.get('trial')}.md")
        if n and 0 < k < n:
            add(tid, "5c", 0, "", ev_p3, note=f"REVIEW: flip {k}/{n}; decide whether it traces to the user simulator (defect=1 medium), to the judge (note under 2j) or to the agent", hp=hp)
        else:
            add(tid, "5c", 0, "", ev_p3, note="stable" if n else "no evaluated trial", hp=hp)
        failed = [f for f in trials if f["reward"] != 1.0]
        if failed or (n and 0 < k < n):
            for f in failed:
                triage.append(f"- task {tid}, Haiku trial {f['trial']}: reward={f['reward']} db_match={f['db_match']} nl_unmet={f['nl_fail'] or '-'} "
                              f"termination={f['termination']} msgs={f['n_msgs']} -> `results/retail/trajectories/{tid}_haiku_t{f['trial']}.md`")
            for s in p3_sims:
                if str(s.get("task_id")) == tid:
                    render_transcript(s, traj_dir / f"{tid}_haiku_t{s.get('trial')}.md")
        abn = [t for t in terms + ([g["termination"]] if g else []) if t in ABNORMAL]
        if len(abn) >= 2:
            add(tid, "5e", 1, "medium", f"terminations={terms} gt={g['termination'] if g else '-'}", note="≥2 abnormal terminations")
        else:
            add(tid, "5e", 0, "", f"terminations={terms} gt={g['termination'] if g else '-'}", note="single abnormal termination: note only" if abn else "")
        missing = [f["trial"] for f in by_task.get(tid, []) + ([g] if g else []) if f["termination"] in NORMAL and not f["has_reward_info"]]
        hits = log_hits.get(tid, [])
        if missing or hits:
            add(tid, "5f", 1, "medium", f"reward_info missing for trials {missing}; log hits: {hits[:3]}")
        else:
            add(tid, "5f", 0, "", f"reward_info present for every normal-stop simulation ({len(by_task.get(tid, [])) + (1 if g else 0)}); no replay/mismatch line in the run log names this task")

    evald = [v for v in (by_task.get(t, []) for t in ids) if v]

    def pk(k):
        el = [[f["reward"] for f in v if f["termination"] != "infrastructure_error"] for v in evald]
        el = [v for v in el if len(v) >= k]
        return (sum(all(r == 1.0 for r in v[:k]) for v in el) / len(el), len(el)) if el else (float("nan"), 0)

    summary += [""]
    for k in (1, 2, 3):
        p, nn = pk(k)
        summary.append(f"- pass^{k} = {p:.3f} (n={nn} tasks)")
    gt_e = [g for t, g in gt.items() if t in ids and g["termination"] != "infrastructure_error"]
    summary.append(f"- GT agent: {sum(1 for g in gt_e if g['reward'] == 1.0)}/{len(gt_e)} eligible tasks reach reward 1.0; "
                   f"GT failures with db_match=True (judge alone): {sum(1 for g in gt_e if g['judge_only_fail'])}")
    all_trials = [f for f in p3 if f["termination"] != "infrastructure_error"]
    summary.append(f"- Haiku trials: {len(all_trials)}; failed: {sum(1 for f in all_trials if f['reward'] != 1.0)}; "
                   f"of which the DB matched and only the judge failed: {judge_only_trials}")
    tin = sum(f["usage_in"] for f in p3) + sum(g["usage_in"] for g in gt.values())
    tout = sum(f["usage_out"] for f in p3) + sum(g["usage_out"] for g in gt.values())
    summary.append(f"- tokens (agent+user messages): in={tin:,} out={tout:,}; cost at $0.10/$0.50 per MTok, cache ignored (upper bound): ${tin * PRICE_IN + tout * PRICE_OUT:.3f} (judge tokens separate: summary.json)")
    summary.append(f"- benchmark-wide log hits (replay/mismatch): {len(log_hits.get('ALL', []))}")
    add("ALL", "6e", 0, "", f"infrastructure_error simulations in these runs: {infra}; tau2 discloses 'Infra Errors N (excluded from metrics below)' above Average Reward (display.py)",
        note="disclosed next to the score; the audit report repeats the count" if infra else "no exclusion in these runs")

    with open(RES / "haiku_pass.csv", "w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    (RES / "agent_runs_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (RES / "agent_triage.md").write_text("# Trajectories for manual review (checks 4f, 5c, 5d; 1e triage)\n\n"
                                         "Each line: one failed Haiku trial or failed GT run; flipped tasks (1 or 2 of 3) have all their trials rendered.\n\n"
                                         + ("\n".join(triage) if triage else "- none") + "\n", encoding="utf-8")
    print("\n".join(summary[-8:]))
    print(f"rows written: {len(rows)} -> results/retail/haiku_pass.csv; triage items: {len(triage)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
