"""Retail summary numbers (retail/summary_numbers.md) and figure (retail/fig_defects_retail.png) from the CSV files.

Reuses the counting functions of scripts/make_summary.py (block 1) unchanged; only the inputs, the labels and the
retail-specific tables (judge, upstream issues, predictions) differ. Defect rule (schema.md): a task is defective iff it
has >= 1 row with defect=1 and severity in {high, medium}. Intervals: 95% Wilson.
Run (Python 3.11 with pandas, matplotlib, statsmodels):  python -I -X utf8 scripts/retail/make_summary.py
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from make_summary import (AGENT_RUN, CATEGORIES, CONFIRMED, USER_SIM_CHECKS, agent_run_only_tasks, agent_run_stats,  # noqa: E402
                          defect_rows, defective_task_ids, defective_tasks, fmt_share, normalize, per_category, rows_per_category,
                          rows_per_check, rule_of_three, unverified_rows, wilson)

RES = ROOT / "results" / "retail"
NOOP_CHECKS = ("2a", "2b", "2c")
RUN_FILES = {"haiku": RES / "runs" / "retail_pass3_haiku" / "results.json", "gt": RES / "runs" / "retail_gt_haiku" / "results.json"}


def load_inputs():
    audit = pd.read_csv(ROOT / "retail" / "audit_log.csv", dtype=str, keep_default_na=False)
    scan = pd.read_csv(RES / "static_scan.csv", dtype={"task_id": str})
    sample = json.loads((ROOT / "retail" / "sample.json").read_text(encoding="utf-8"))
    return audit, scan, sample


def load_runs():
    if not all(p.exists() for p in RUN_FILES.values()):
        return None
    return {k: json.loads(p.read_text(encoding="utf-8"))["simulations"] for k, p in RUN_FILES.items()}


def judge_only(sims) -> tuple[int, int]:
    """(trials failed with db_match True and an unmet assertion, evaluated trials)."""
    n = jo = 0
    for s in sims:
        if s.get("termination_reason") == "infrastructure_error":
            continue
        n += 1
        ri = s.get("reward_info") or {}
        if (ri.get("db_check") or {}).get("db_match") and float(ri.get("reward") or 0) != 1.0 and any(c.get("met") is False for c in (ri.get("nl_assertions") or [])):
            jo += 1
    return jo, n


def _share(k, n):
    return fmt_share(k, n) if n else f"{k}/0"


def tau2_pass_k(sims, ids, k: int) -> tuple[float, int]:
    """tau2's pass^k: per task C(c, k) / C(n, k) over the n evaluated trials with c successes, averaged over tasks
    (k = 1 is the average reward that `tau2 run` prints); infrastructure_error simulations excluded."""
    ids = set(map(str, ids))
    per: dict[str, list[bool]] = {}
    for s in sims:
        t = str(s["task_id"])
        if t not in ids or s.get("termination_reason") == "infrastructure_error":
            continue
        r = (s.get("reward_info") or {}).get("reward")
        per.setdefault(t, []).append(r is not None and float(r) == 1.0)
    el = [v for v in per.values() if len(v) >= k]
    return (sum(comb(sum(v), k) / comb(len(v), k) for v in el) / len(el), len(el)) if el else (float("nan"), 0)


def agent_table(runs, ids) -> list:
    title = "Table 4. Agent runs (claude-haiku-5-5 agent and user; stock scorer; NL judge claude-haiku-5-5, one vote, in the loop)"
    if runs is None:
        return ["", title, "", "agent runs: not available"]
    st = agent_run_stats(runs, ids)
    n3 = st["n3"]
    L = ["", title, "", "| quantity | value |", "|---|---|"]
    L += [f"| pass^{k}, all tasks (first {k} trial(s) all reward 1.0) | {_share(*st[f'pass{k}'])} |" for k in (1, 2, 3)]
    L += [f"| pass^{k}, tau2 estimator (mean over tasks of C(c,k)/C(n,k); k = 1 is the average reward tau2 prints) | {tau2_pass_k(runs['haiku'], ids, k)[0]:.3f} (n = {tau2_pass_k(runs['haiku'], ids, k)[1]} tasks) |" for k in (1, 2, 3)]
    L.append(f"| tasks solved in 0/3 trials | {_share(st['s0'], n3)} |")
    L.append(f"| tasks solved in 1/3 or 2/3 trials (unstable) | {_share(st['s12'], n3)} |")
    L.append(f"| tasks solved in 3/3 trials | {_share(st['s3'], n3)} |")
    jo_h, n_h = judge_only(runs["haiku"])
    jo_g, n_g = judge_only(runs["gt"])
    L.append(f"| Haiku trials failed by the judge alone (DB matched, an assertion unmet) | {_share(jo_h, n_h)} of evaluated trials |")
    L.append(f"| ground-truth agent reaches reward 1.0 | {_share(*st['gt'])} |")
    L.append(f"| ground-truth runs failed by the judge alone (DB matched) | {_share(jo_g, n_g)} |")
    L.append(f"| Haiku passes ≥1 trial, ground-truth agent fails | {len(st['h_not_gt'])} |")
    L.append(f"| ground-truth agent passes, Haiku 0/3 | {len(st['gt_not_h'])} |")
    L.append(f"| infrastructure_error simulations excluded | {st['infra']} |")
    ids_ = lambda xs: ", ".join(xs) if xs else "none"  # noqa: E731
    L += ["", f"- ground-truth agent fails on tasks: {ids_(st['gt_fail'])}", f"- Haiku passes ≥1 trial, ground-truth agent fails: {ids_(st['h_not_gt'])}",
          f"- ground-truth agent passes, Haiku 0/3: {ids_(st['gt_not_h'])}"]
    return L


def rereview_table() -> list:
    p = RES / "rereview.csv"
    if not p.exists():
        return ["", "Table 5. Blind re-review", "", "blind re-review: not available"]
    df = pd.read_csv(p, dtype=str).fillna("")
    out = ["", "Table 5. Blind re-review of 12 tasks (labels compared on defect 0/1 per task x check)", "", "| comparison | agreement | Cohen's kappa |", "|---|---|---|"]
    for col, label in (("original_defect", "blind vs original reviewer labels"), ("corrected_defect", "blind vs skeptic-corrected labels")):
        sub = df[df[col] != ""]
        if len(sub) == 0:
            out.append(f"| {label} | n/a | n/a |")
            continue
        a, b = sub[col].astype(str), sub["blind_defect"].astype(str)
        po = float((a == b).mean())
        pe = float((a == "1").mean() * (b == "1").mean() + (a == "0").mean() * (b == "0").mean())
        kappa = float("nan") if pe >= 1.0 else (po - pe) / (1 - pe)
        out.append(f"| {label} | {int((a == b).sum())}/{len(sub)} = {po:.3f} | {kappa:.3f} |")
    tasks = sorted(df["task_id"].unique(), key=lambda x: int(x) if str(x).isdigit() else 0)
    out.append(f"\n- tasks: {', '.join(tasks)}; rows: {len(df)}; disagreements listed in results/retail/rereview_summary.md")
    return out


def judge_table() -> list:
    p = RES / "rejudge_summary.json"
    out = ["", "Table 6. The judge inside the score (check 2j)", ""]
    if not p.exists():
        return out + ["re-judge: not available"]
    s = json.loads(p.read_text(encoding="utf-8"))
    sp, rj = s["strict_parser"], s["rejudge"]
    out += ["| quantity | value |", "|---|---|",
            f"| live judge replies the stock strict parser would reject | {_share(sp['strict_rejected'], sp['calls'])} |",
            f"| live replies with fewer results than assertions (silently uncounted by the stock code) | {sp['results_short']}/{sp['calls']} |",
            f"| simulations re-judged with {rj['votes']} votes | {rj['simulations']} |",
            f"| assertion verdicts where the live vote differs from the majority | {_share(rj['assertion_flips'], rj['assertion_verdicts'])} |",
            f"| rewards that flip under the majority (pass→fail / fail→pass) | {rj['reward_flips']} ({rj['pass_to_fail']} / {rj['fail_to_pass']}) of {rj['simulations']} |"]
    return out


def issues_table(audit, ids) -> list:
    tasks = json.loads((ROOT / "tau2-bench" / "data" / "tau2" / "domains" / "retail" / "tasks.json").read_text(encoding="utf-8"))
    rows = defect_rows(audit, ids, CONFIRMED)
    match = {r["task_id"]: r for r in pd.read_csv(RES / "upstream_issue_match.csv", dtype=str).to_dict("records")} if (RES / "upstream_issue_match.csv").exists() else {}
    out = ["", "Table 7. Upstream-recorded open issues (tasks.json → issues) against the audit rows", "",
           "| task | upstream issue (title) | audit: defect rows on the task (any mechanism) | same mechanism found by the audit (results/retail/upstream_issue_match.csv) |",
           "|---|---|---|---|"]
    for t in tasks:
        for iss in t.get("issues") or []:
            found = sorted(set(rows.loc[rows["task_id"] == str(t["id"]), "check"]))
            m = match.get(str(t["id"]), {}).get("match", "not read")
            out.append(f"| {t['id']} | {iss.get('title', '')[:110]} | {', '.join(found) or 'none'} | {m} |")
    return out


def predictions_table(audit, scan, ids, runs) -> list:
    n = len(ids)
    probe = pd.read_csv(RES / "noop_judge_probe.csv", dtype=str) if (RES / "noop_judge_probe.csv").exists() else None
    rows = defect_rows(audit, ids, CONFIRMED)
    k2k = rows.loc[rows["check"] == "2k", "task_id"].nunique()
    k2h = rows.loc[rows["check"] == "2h", "task_id"].nunique()
    k2m_all = int(((normalize(audit)["task_id"] == "ALL") & (normalize(audit)["check"] == "2m") & (normalize(audit)["defect"] == 1)).sum())
    noop = int(scan["noop_pass"].sum())
    b = c = "n/a"
    if probe is not None:
        b = f"{int((probe[probe['probe'] == '2b']['passes'] == '1').sum())}/{n}"
        c = f"{int((probe[probe['probe'] == '2c']['passes'] == '1').sum())}/{n}"
    issues = [ln for ln in issues_table(audit, ids) if ln.startswith("| ") and not ln.startswith("| task")]
    j = judge_table()
    out = ["", "Table 8. Pre-registered predictions (retail/PLAN.md §3) against the measurements", "", "| id | prediction | measured |", "|---|---|---|",
           f"| P1 | no-op pass 6/114 by construction; refusal/transfer passes only where the judge accepts | static {noop}/{n}; probe 2b {b}; probe 2c {c} (judge accepted the assertions of an empty answer in {int((probe[(probe['probe'] == '2b') & (probe['judged'] == '1')]['passes'] == '1').sum()) if probe is not None else 'n/a'} tasks) |",
           f"| P2 | 2k only where no enforced assertion covers the communicate_info fact; certain for 30, 31, 32 | 2k confirmed on {k2k} tasks: {', '.join(sorted(rows.loc[rows['check'] == '2k', 'task_id'].unique(), key=int))} |",
           f"| P3 | 0 tasks flip on WRITE order (except shared payment_history) | 2h confirmed on {k2h} tasks |",
           f"| P4 | process requirements unscored (benchmark-level 2m) | 2m benchmark-level defect rows: {k2m_all}; per-task 2m: {rows.loc[rows['check'] == '2m', 'task_id'].nunique()} |",
           f"| P5 | upstream issues on 4, 5, 7 re-found | {' / '.join(ln.strip('| ').split(' | ')[0] + ': ' + ln.strip('| ').split(' | ')[3] for ln in issues)} (Table 7; the rows on tasks 4 and 5 describe other mechanisms) |",
           f"| P6 | some judge replies fail the strict parser; re-judge flips some verdicts | {j[5].strip('| ').split(' | ')[1] if len(j) > 5 else 'n/a'} rejected; reward flips {j[-1].strip('| ').split(' | ')[1] if len(j) > 5 else 'n/a'} |",
           f"| P7 | defective share, no numeric prediction | {fmt_share(defective_tasks(audit, ids), n)} (airline sample: 18/20) |"]
    return out


def build_markdown(audit, scan, sample, runs) -> str:
    ids = sample["task_ids"]
    n = len(ids)
    noop = int(scan["noop_pass"].sum())
    needs = int(scan["noop_needs_judge"].sum())
    L = ["# Summary numbers — retail", "", f"bench_commit: `{sample['bench_commit']}`; all {n} tasks of the base split (no sampling).", "", "Intervals: 95% Wilson.", "",
         "Table 1. Headline shares", "", "| quantity | share |", "|---|---|"]
    k_def = defective_tasks(audit, ids)
    L.append(f"| defective tasks (≥1 medium/high defect row, all checks) | {fmt_share(k_def, n)} |")
    for label, k in (("static and probe checks only (method ≠ agent_run; every row passed the adversarial review)", defective_tasks(audit, ids, exclude_methods=(AGENT_RUN,))),
                     ("all checks without the simulator-attributed rows (5c, 5d)", defective_tasks(audit, ids, ("5c", "5d"))),
                     ("agent_run checks only (1e, 4f, 5c, 5d, 5e, 5f)", defective_tasks(audit, ids, methods=(AGENT_RUN,))),
                     ("agent_run checks excluding 5d (user-simulator deviations)", defective_tasks(audit, ids, USER_SIM_CHECKS, methods=(AGENT_RUN,))),
                     ("agent_run checks excluding 5c and 5d (simulator-attributed rows)", defective_tasks(audit, ids, ("5c", "5d"), methods=(AGENT_RUN,)))):
        L.append(f"| defective tasks, {label} | {fmt_share(k, n)} |")
    L.append(f"| tasks whose only defects come from agent_run checks | {fmt_share(agent_run_only_tasks(audit, ids), n)} |")
    noop_checks = NOOP_CHECKS + ("2c",)  # retail adds the transfer-only probe to the no-op class
    k_ex = defective_tasks(audit, ids, noop_checks)
    L.append(f"| defective tasks, excluding the no-op class (checks 2a, 2b, 2c) | {fmt_share(k_ex, n)} |")
    rows = defect_rows(audit, ids, CONFIRMED)
    noop_ids = set(scan.loc[scan["noop_pass"] == 1, "task_id"].astype(str))
    derived = rows["check"].isin(noop_checks) | ((rows["check"] == "2k") & rows["task_id"].isin(noop_ids))
    k_nf = rows.loc[~derived, "task_id"].nunique()
    L.append(f"| defective tasks, excluding every defect that derives from the no-op design (2a, 2b, 2c, and 2k on no-op tasks) | {fmt_share(k_nf, n)} |")
    L.append(f"| no-op pass by construction (empty answer = full reward), all tasks | {fmt_share(noop, n)} |")
    L.append(f"| no-op verdict left to the judge (DB unchanged, assertions exist) | {needs}/{n}; the judge failed all of them in the probe |")
    L.append(f"| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | {unverified_rows(audit)} |")
    L += ["", "Verification status: the static and probe rows passed the adversarial review (results/retail/skeptic_report.md). "
          "The agent-run rows (1e, 4f, 5c, 5d per task) are as filed by five trajectory reviewers and were not adversarially reviewed "
          "(retail/PLAN.md, deviation of 2026-10-28); every share that includes them carries that caveat."]
    notes = rule_of_three(noop, n, "no-op pass") + rule_of_three(k_def, n, "defective tasks") + rule_of_three(k_ex, n, "defective tasks excluding the no-op class")
    conf = per_category(audit, ids)
    L += ["", "Table 2. Tasks with ≥1 defect (high/medium, all checks; agent-run rows not adversarially reviewed), by category", "", "| category | share of all tasks |", "|---|---|"]
    for c, name in CATEGORIES.items():
        L.append(f"| {c} {name} | {fmt_share(conf[c], n)} |")
        notes += rule_of_three(conf[c], n, f"category {c} {name}")
    L += ["", "Table 2b. Defect rows by check (high/medium, all methods; 1e, 4f, 5c, 5d come from the runs and were not adversarially reviewed)", "", "| check | defect rows (high/medium) | tasks |", "|---|---|---|"]
    L += [f"| {c} | {r} | {t}/{n} |" for c, r, t in rows_per_check(audit, ids)]
    a = normalize(audit)
    all_rows = a[(a["task_id"] == "ALL") & (a["defect"] == 1)]
    L += ["", "Benchmark-level defect rows (task_id = ALL): " + (", ".join(f"{r.check} ({r.severity})" for r in all_rows.itertuples()) or "none")]
    low_t, low_r = per_category(audit, ids, {"low"}), rows_per_category(audit, ids, {"low"})
    L += ["", "Table 3. Low-severity defects, by category (informational)", "", "| category | rows | tasks |", "|---|---|---|"]
    L += [f"| {c} {name} | {low_r[c]} | {low_t[c]}/{n} |" for c, name in CATEGORIES.items()]
    L += agent_table(runs, ids)
    L += rereview_table()
    L += judge_table()
    L += issues_table(audit, ids)
    L += predictions_table(audit, scan, ids, runs)
    if notes:
        L += ["", "Rule of three (k = 0)", ""] + notes
    return "\n".join(L) + "\n"


def make_figure(audit, scan, sample, runs, out: Path):
    ids, n = sample["task_ids"], len(sample["task_ids"])
    bars = [("Empty answer gets full score\n(no-op pass, by construction)", int(scan["noop_pass"].sum()), n),
            ("≥1 defect (all checks;\nrun rows not adversarially reviewed)", defective_tasks(audit, ids), n),
            ("≥1 defect without the\nsimulator rows (5c, 5d)", defective_tasks(audit, ids, ("5c", "5d")), n),
            ("≥1 confirmed defect\n(static and probe checks, reviewed)", defective_tasks(audit, ids, exclude_methods=(AGENT_RUN,)), n)]
    conf = per_category(audit, ids)
    bars += [(f"category {c}: {name}", conf[c], n) for c, name in CATEGORIES.items()]
    if runs is not None:
        st = agent_run_stats(runs, ids)
        bars += [("agent pass^3 (judge in the loop)", *st["pass3"]), ("ground-truth agent reaches reward 1.0", *st["gt"])]
    labels = [b[0] for b in bars][::-1]
    vals = [b[1] / b[2] for b in bars][::-1]
    err = [(v - wilson(b[1], b[2])[0], wilson(b[1], b[2])[1] - v) for v, b in zip(vals, bars[::-1])]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(bars) + 1.2), dpi=150)
    ax.barh(range(len(bars)), vals, xerr=list(zip(*err)), color="#4a6fa5", ecolor="#333", capsize=3)
    ax.set_yticks(range(len(bars)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of the 114 retail tasks (95% Wilson interval)")
    for i, (v, b) in enumerate(zip(vals, bars[::-1])):
        ax.text(min(wilson(b[1], b[2])[1] + 0.01, 0.9), i, f"{b[1]}/{b[2]}", va="center", fontsize=8)  # right of the interval
    ax.set_title("tau2-bench retail (v2.0.0): what the checklist found on all 114 tasks", fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)


def main() -> int:
    audit, scan, sample = load_inputs()
    runs = load_runs()
    md = build_markdown(audit, scan, sample, runs)
    (ROOT / "retail" / "summary_numbers.md").write_text(md, encoding="utf-8")
    make_figure(audit, scan, sample, runs, ROOT / "retail" / "fig_defects_retail.png")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
