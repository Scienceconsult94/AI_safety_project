"""Turn the agent runs (run-pass3 with Haiku, llm_agent_gt) into audit rows and review material.

Inputs:
  sample.json                                   sampled task ids, bench_commit
  results/static_scan.csv                       gt_eligible, n_write per task
  tau2-bench/data/simulations/<pass3_dir>/**/results.json   three Haiku trials per task
  tau2-bench/data/simulations/<gt_dir>/results.json         one ground-truth-agent trial per eligible task
  optional: one or more run logs (stderr of tau2) scanned for replay mismatches
Outputs (results/):
  haiku_pass.csv            mechanical rows for checks 1e, 1f, 5c, 5e, 5f (per task) and 6e (ALL);
                            columns task_id,check,haiku_pass,defect,severity,evidence,note
  agent_runs_summary.md     per-task table, pass^k, terminations, token-based cost estimate
  agent_triage.md           every failed or flipped trajectory, with pointers for the manual review (4f, 5c, 5d)
  trajectories/<task>_<src>_t<trial>.md   readable transcripts of those trajectories
Rows that need a human/LLM reading (4f, 5d, and 1e/5c triage) are written as defect=0 with note
"REVIEW" here; the reviewer's verdicts go to results/review_agent.csv, which build_audit_log.py reads last.
Usage (from ==Project):  python -I agent_rows.py [--pass3 sample20_pass3_haiku] [--gt sample20_gt_haiku] [--log path ...]
No LLM calls, no file under tau2-bench/ is modified.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
SIMS = ROOT / "tau2-bench" / "data" / "simulations"
NORMAL = {"agent_stop", "user_stop"}
ABNORMAL = {"timeout", "max_steps", "too_many_errors"}
PRICE_IN, PRICE_OUT = 0.10 / 1e6, 0.50 / 1e6  # claude-haiku-5-5, prompts <= 100K tokens; cache ignored (upper bound)
COLS = ["task_id", "check", "haiku_pass", "defect", "severity", "evidence", "note"]


def load_results(pattern_root: Path) -> list[dict]:
    files = sorted(pattern_root.rglob("results.json")) if pattern_root.is_dir() else []
    out = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        tasks = {str(t["id"]): t for t in data.get("tasks", [])}
        for s in data.get("simulations", []):
            s["_file"] = str(f.relative_to(ROOT)).replace("\\", "/")
            s["_task"] = tasks.get(str(s.get("task_id")))
            out.append(s)
    return out


def sim_facts(s: dict) -> dict:
    ri = s.get("reward_info") or {}
    db = ri.get("db_check") or {}
    comm = ri.get("communicate_checks")
    comm_fail = [c.get("info") for c in (comm or []) if c.get("met") is False]
    usage_in = usage_out = 0
    n_tool_calls = 0
    for m in s.get("messages", []):
        u = m.get("usage") or {}
        usage_in += int(u.get("prompt_tokens") or 0)
        usage_out += int(u.get("completion_tokens") or 0)
        n_tool_calls += len(m.get("tool_calls") or [])
    return {
        "task_id": str(s.get("task_id")),
        "trial": s.get("trial"),
        "reward": ri.get("reward"),
        "has_reward_info": bool(s.get("reward_info")),
        "db_match": db.get("db_match"),
        "comm_fail": comm_fail,
        "termination": str(s.get("termination_reason")),
        "n_msgs": len(s.get("messages", [])),
        "n_tool_calls": n_tool_calls,
        "duration": round(float(s.get("duration") or 0), 1),
        "usage_in": usage_in,
        "usage_out": usage_out,
        "file": s["_file"],
        "sim_id": s.get("id"),
    }


def render_transcript(s: dict, path: Path) -> None:
    t = s.get("_task") or {}
    f = sim_facts(s)
    lines = [f"# task {f['task_id']} trial {f['trial']} ({f['file']}, sim {f['sim_id']})",
             "",
             f"reward={f['reward']} termination={f['termination']} db_match={f['db_match']} "
             f"communicate_failed={f['comm_fail'] or '-'} messages={f['n_msgs']} tool_calls={f['n_tool_calls']}",
             ""]
    us = t.get("user_scenario") or {}
    if us:
        lines += ["## user_scenario", "```json", json.dumps(us, ensure_ascii=False, indent=1), "```", ""]
    ec = t.get("evaluation_criteria") or {}
    if ec:
        lines += ["## evaluation_criteria", "```json", json.dumps(ec, ensure_ascii=False, indent=1), "```", ""]
    lines += ["## transcript", ""]
    for m in s.get("messages", []):
        role = m.get("role")
        turn = m.get("turn_idx")
        content = (m.get("content") or "").strip()
        if role == "tool":
            lines.append(f"**[{turn}] tool -> {m.get('requestor', '')}** (id {m.get('id', '')}):")
            lines.append("```")
            lines.append(content[:3000] + ("…[truncated]" if len(content) > 3000 else ""))
            lines.append("```")
        else:
            lines.append(f"**[{turn}] {role}:** {content}")
            for tc in m.get("tool_calls") or []:
                lines.append(f"  - tool_call `{tc.get('name')}` {json.dumps(tc.get('arguments'), ensure_ascii=False)} (id {tc.get('id')})")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass3", default="sample20_pass3_haiku")
    ap.add_argument("--gt", default="sample20_gt_haiku")
    ap.add_argument("--log", nargs="*", default=[])
    a = ap.parse_args()

    sample = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))
    ids = [str(i) for i in sample["task_ids"]]
    with open(RES / "static_scan.csv", encoding="utf-8", newline="") as fp:
        scan = {r["task_id"]: r for r in csv.DictReader(fp)}

    p3 = [sim_facts(s) for s in load_results(SIMS / a.pass3)]
    gt_sims = load_results(SIMS / a.gt)
    gt = {sim_facts(s)["task_id"]: sim_facts(s) for s in gt_sims}
    p3_sims = load_results(SIMS / a.pass3)
    by_task: dict[str, list[dict]] = defaultdict(list)
    for f in p3:
        by_task[f["task_id"]].append(f)
    for v in by_task.values():
        v.sort(key=lambda x: (x["trial"] is None, x["trial"]))

    # replay / scoring anomalies in logs (benchmark-wide; attributed per task when the line names one)
    log_hits: dict[str, list[str]] = defaultdict(list)
    pat = re.compile(r"replay|mismatch|strict|set_state", re.I)
    for lp in a.log:
        p = Path(lp)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if pat.search(line) and "ERROR" in line or "mismatch" in line.lower():
                m = re.search(r"[Tt]ask (\d+)", line)
                log_hits[m.group(1) if m else "ALL"].append(line.strip()[:200])

    rows: list[dict] = []
    triage: list[str] = []
    traj_dir = RES / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    infra = sum(1 for f in p3 if f["termination"] == "infrastructure_error") + \
        sum(1 for f in gt.values() if f["termination"] == "infrastructure_error")

    def add(task_id, check, defect, severity, evidence, note="", hp=""):
        rows.append({"task_id": task_id, "check": check, "haiku_pass": hp, "defect": int(defect),
                     "severity": severity if defect else "", "evidence": evidence, "note": note})

    summary = ["# Agent runs on the 20 sampled tasks (claude-haiku-5-5 agent and user, substring scorer)", "",
               f"pass3 dir: `{a.pass3}`; gt dir: `{a.gt}`; infrastructure_error simulations: {infra}", "",
               "| task | n_write | pass3 rewards | haiku_pass | terminations | gt_eligible | gt reward | gt termination | gt db_match |",
               "|---|---|---|---|---|---|---|---|---|"]
    for tid in ids:
        trials = [f for f in by_task.get(tid, []) if f["termination"] != "infrastructure_error"]
        rewards = [f["reward"] for f in trials]
        k = sum(1 for r in rewards if r == 1.0)
        n = len(trials)
        hp = f"{k}/{n}" if n else ""
        terms = [f["termination"] for f in by_task.get(tid, [])]
        sc = scan.get(tid, {})
        elig = sc.get("gt_eligible") == "1"
        g = gt.get(tid)
        summary.append(f"| {tid} | {sc.get('n_write', '?')} | {' '.join('1' if r == 1.0 else '0' if r == 0.0 else '?' for r in rewards) or '-'} | {hp or '-'} | {', '.join(terms) or '-'} | {int(elig)} | {g['reward'] if g else '-'} | {g['termination'] if g else '-'} | {g['db_match'] if g else '-'} |")

        ev_p3 = f"{a.pass3}: rewards={rewards} terminations={terms} msgs={[f['n_msgs'] for f in by_task.get(tid, [])]}"
        # 1f baseline solve rate (never a defect on its own)
        add(tid, "1f", 0, "", ev_p3, note="haiku_pass = successes/evaluated trials" if n else "no evaluated trial", hp=hp)
        # 1e GT agent reaches the target state
        if not elig:
            add(tid, "1e", 0, "", "static_scan gt_eligible=0 (no reference actions); llm_agent_gt skips the task (registry task_filter)", note="n/a")
        elif g is None:
            add(tid, "1e", 0, "", f"{a.gt}: no simulation for this task", note="REVIEW: missing GT run")
        else:
            ev = f"{a.gt}: reward={g['reward']} db_match={g['db_match']} communicate_failed={g['comm_fail'] or '-'} termination={g['termination']} msgs={g['n_msgs']} tool_calls={g['n_tool_calls']}"
            if g["reward"] == 1.0:
                add(tid, "1e", 0, "", ev)
            else:
                add(tid, "1e", 1, "high", ev, note="PROVISIONAL (mechanical): GT agent did not reach the target; REVIEW whether the cause is the task or an agent slip")
                triage.append(f"- task {tid}, GT run: {ev} -> `results/trajectories/{tid}_gt_t{g['trial']}.md`")
                for s in gt_sims:
                    if str(s.get("task_id")) == tid:
                        render_transcript(s, traj_dir / f"{tid}_gt_t{s.get('trial')}.md")
        # 5c stability across trials
        if n and 0 < k < n:
            add(tid, "5c", 0, "", ev_p3, note=f"REVIEW: flip {k}/{n}; decide whether it traces to the user simulator (then defect=1 medium) or to the agent", hp=hp)
        else:
            add(tid, "5c", 0, "", ev_p3, note="stable" if n else "no evaluated trial", hp=hp)
        failed = [f for f in trials if f["reward"] != 1.0]
        if failed or (n and 0 < k < n):
            for f in failed:
                triage.append(f"- task {tid}, Haiku trial {f['trial']}: reward={f['reward']} db_match={f['db_match']} communicate_failed={f['comm_fail'] or '-'} termination={f['termination']} msgs={f['n_msgs']} -> `results/trajectories/{tid}_haiku_t{f['trial']}.md`")
            for s in p3_sims:
                if str(s.get("task_id")) == tid:
                    render_transcript(s, traj_dir / f"{tid}_haiku_t{s.get('trial')}.md")
        # 5e limits deciding the result
        abn = [t for t in terms + ([g["termination"]] if g else []) if t in ABNORMAL]
        if len(abn) >= 2:
            add(tid, "5e", 1, "medium", f"terminations={terms} gt={g['termination'] if g else '-'}", note="≥2 abnormal terminations")
        else:
            add(tid, "5e", 0, "", f"terminations={terms} gt={g['termination'] if g else '-'}", note="single abnormal termination: note only" if abn else "")
        # 5f replay consistency: reward_info present for normal stops; log anomalies
        missing = [f["trial"] for f in by_task.get(tid, []) + ([g] if g else []) if f["termination"] in NORMAL and not f["has_reward_info"]]
        hits = log_hits.get(tid, [])
        if missing or hits:
            add(tid, "5f", 1, "medium", f"reward_info missing for trials {missing}; log hits: {hits[:3]}")
        else:
            add(tid, "5f", 0, "", f"reward_info present for every normal-stop simulation ({len(by_task.get(tid, [])) + (1 if g else 0)}); no replay/mismatch line in the run log names this task")

    # pass^k over the sample
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
    summary.append(f"- GT agent: {sum(1 for g in gt_e if g['reward'] == 1.0)}/{len(gt_e)} eligible sampled tasks reach the target state")
    tin = sum(f["usage_in"] for f in p3) + sum(g["usage_in"] for g in gt.values())
    tout = sum(f["usage_out"] for f in p3) + sum(g["usage_out"] for g in gt.values())
    summary.append(f"- tokens (all messages, agent+user): in={tin:,} out={tout:,}; cost at $0.10/$0.50 per MTok, cache ignored (upper bound): ${tin * PRICE_IN + tout * PRICE_OUT:.3f}")
    summary.append(f"- benchmark-wide log hits (replay/mismatch): {len(log_hits.get('ALL', []))}")

    add("ALL", "6e", 0, "", f"infrastructure_error simulations in these runs: {infra}; tau2 prints 'Infra Errors N (excluded from metrics below)' above Average Reward (display.py)",
        note="disclosed next to the score in tau2 view/CLI; the audit report must repeat the count" if infra else "no exclusion in these runs")

    with open(RES / "haiku_pass.csv", "w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    (RES / "agent_runs_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (RES / "agent_triage.md").write_text(
        "# Trajectories for manual review (checks 4f, 5c, 5d; 1e triage)\n\n"
        "Each line: one failed Haiku trial or failed GT run; flipped tasks (1 or 2 of 3) have all their trials rendered.\n\n"
        + ("\n".join(triage) if triage else "- none: every evaluated trajectory succeeded") + "\n", encoding="utf-8")
    print("\n".join(summary))
    print(f"rows written: {len(rows)} -> results/haiku_pass.csv; triage items: {len(triage)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
