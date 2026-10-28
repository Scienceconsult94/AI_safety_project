"""Airline (block 1, 20 sampled tasks of 50) beside retail (all 114 tasks): one table and one figure from the two audit logs.

Both columns are computed by the same functions (scripts/make_summary.py) from audit_log.csv / retail/audit_log.csv, the
two static scans and the recorded runs. Nothing is copied from the written summaries.
Output: retail/comparison.md, retail/fig_comparison.png.
Run:  python -I -X utf8 scripts/retail/comparison.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "retail"))
from make_summary import AGENT_RUN, CATEGORIES, agent_run_stats, defective_tasks, fmt_share, per_category, wilson  # noqa: E402
from make_summary import load_inputs as load_airline, load_runs as load_airline_runs  # noqa: E402
import make_summary as retail_ms  # noqa: E402  (scripts/retail/make_summary.py, found first on sys.path? no: imported below by path)


def load_retail():
    import importlib.util
    spec = importlib.util.spec_from_file_location("retail_make_summary", ROOT / "scripts" / "retail" / "make_summary.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    audit, scan, sample = mod.load_inputs()
    return audit, scan, sample, mod.load_runs(), mod


def main() -> int:
    a_audit, a_scan, a_sample = load_airline(ROOT)
    a_runs = load_airline_runs(ROOT)
    r_audit, r_scan, r_sample, r_runs, rmod = load_retail()
    a_ids, r_ids = a_sample["task_ids"], r_sample["task_ids"]
    na, nr = len(a_ids), len(r_ids)
    rows = []

    def add(label, ka, nna, kr, nnr):
        rows.append((label, fmt_share(ka, nna) if nna else "n/a", fmt_share(kr, nnr) if nnr else "n/a", (ka, nna, kr, nnr)))

    add("tasks with ≥1 confirmed medium/high defect (all checks)", defective_tasks(a_audit, a_ids), na, defective_tasks(r_audit, r_ids), nr)
    add("… static and probe checks only", defective_tasks(a_audit, a_ids, exclude_methods=(AGENT_RUN,)), na, defective_tasks(r_audit, r_ids, exclude_methods=(AGENT_RUN,)), nr)
    add("… agent_run checks only", defective_tasks(a_audit, a_ids, methods=(AGENT_RUN,)), na, defective_tasks(r_audit, r_ids, methods=(AGENT_RUN,)), nr)
    add("… excluding the no-op class (2a, 2b[, 2c])", defective_tasks(a_audit, a_ids, ("2a", "2b")), na, defective_tasks(r_audit, r_ids, ("2a", "2b", "2c")), nr)
    ca, cr = per_category(a_audit, a_ids), per_category(r_audit, r_ids)
    for c, name in CATEGORIES.items():
        add(f"category {c} {name}", ca[c], na, cr[c], nr)
    add("empty answer gets full reward (whole domain)", int(a_scan["noop_pass"].sum()), len(a_scan), int(r_scan["noop_pass"].sum()), len(r_scan))
    sa = agent_run_stats(a_runs, a_ids) if a_runs else None
    sr = agent_run_stats(r_runs, r_ids) if r_runs else None
    for k in (1, 3):
        add(f"agent pass^{k} (claude-haiku-5-5)", *(sa[f"pass{k}"] if sa else (0, 0)), *(sr[f"pass{k}"] if sr else (0, 0)))
    add("ground-truth agent reaches reward 1.0", *(sa["gt"] if sa else (0, 0)), *(sr["gt"] if sr else (0, 0)))
    jo_r = rmod.judge_only(r_runs["haiku"]) if r_runs else (0, 0)
    L = ["# Airline beside retail", "",
         f"Same pinned benchmark (`{a_sample['bench_commit']}`), same checklist, same models and run settings. Airline: {na} tasks sampled before any run out of 50; "
         f"retail: all {nr} tasks. Airline reward = DB hash × substring check of `communicate_info`; retail reward = DB hash × LLM-judged `nl_assertions` "
         "(judge model substituted by claude-haiku-5-5; the stock default is an OpenAI model). Retail adds checks 2c, 2d, 2e (probed), 2j and 2m; airline logged none of these "
         "per task, so the retail defective share is computed with and without them below. Intervals: 95% Wilson.", "",
         f"| quantity | airline (20 of 50, sampled) | retail (all 114) |", "|---|---|---|"]
    L += [f"| {lab} | {x} | {y} |" for lab, x, y, _ in rows]
    extra = ("2c", "2d", "2e", "2m", "2j")
    L.append(f"| tasks with ≥1 confirmed defect, retail without the checks airline did not log per task ({', '.join(extra)}) | — | {fmt_share(defective_tasks(r_audit, r_ids, extra), nr)} |")
    L.append(f"| Haiku trials failed by the judge alone (DB matched) | — (no judge in airline scoring) | {fmt_share(*jo_r) if jo_r[1] else 'n/a'} |")
    L += ["", "Reading notes", "",
          "- Airline's share is a sample estimate with a wide interval; retail's is the population value of the domain. The two are not the same quantity, and the retail figure carries no sampling error.",
          "- Airline's no-op class (23/50 tasks passable by an empty answer) is the domain's largest defect class; retail's scorer enforces assertions on 40 tasks, which shrinks that class to the 6 tasks that have neither a write nor an assertion.",
          "- Retail moves the weight onto the judge: whether a trial passes depends on one LLM vote whose reply the stock parser would often reject (Table 6 of retail/summary_numbers.md).",
          "- Agent numbers are not comparable across domains (different tasks, different scorer); they are listed to show the noise floor each domain carries."]
    (ROOT / "retail" / "comparison.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    sel = [r for r in rows if r[0].startswith("category") or r[0].startswith("tasks with") or r[0].startswith("empty")]
    fig, ax = plt.subplots(figsize=(9.5, 0.5 * len(sel) + 1.4), dpi=150)
    y = list(range(len(sel)))[::-1]
    for off, col, idx, label in ((0.18, "#c0504d", 0, f"airline ({na} sampled of 50)"), (-0.18, "#4a6fa5", 2, f"retail (all {nr})")):
        vals = [r[3][idx] / r[3][idx + 1] if r[3][idx + 1] else 0 for r in sel]
        err = [[v - wilson(r[3][idx], r[3][idx + 1])[0] if r[3][idx + 1] else 0 for v, r in zip(vals, sel)],
               [wilson(r[3][idx], r[3][idx + 1])[1] - v if r[3][idx + 1] else 0 for v, r in zip(vals, sel)]]
        ax.barh([yy + off for yy in y], vals, height=0.34, xerr=err, color=col, ecolor="#333", capsize=2, label=label)
        for yy, v, r in zip(y, vals, sel):
            ax.text(min(v + 0.01, 0.92), yy + off, f"{r[3][idx]}/{r[3][idx + 1]}", va="center", fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in sel], fontsize=8)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("share of tasks (95% Wilson interval)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("tau2-bench v2.0.0: the same checklist on two domains", fontsize=10)
    fig.tight_layout()
    fig.savefig(ROOT / "retail" / "fig_comparison.png", dpi=150, facecolor="white")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
