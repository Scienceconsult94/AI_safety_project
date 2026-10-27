"""Recompute the audit summary numbers and the defect chart from the CSV files.

Inputs (next to this script): audit_log.csv, results/static_scan.csv, sample.json.
Outputs: summary_numbers.md (numbers only) and fig_defects.png.
Defect rule (schema.md): a task is defective iff it has >=1 row with defect=1
and severity in {high, medium}. All intervals: 95% Wilson.
Run:  python -I make_summary.py            (write outputs)
      python -I make_summary.py --selftest (check the counting rules on fake data)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

ROOT = Path(__file__).resolve().parent
CATEGORIES = {1: "Solvability", 2: "Scoring validity", 3: "Isolation and leaks",
              4: "Specification clarity", 5: "Determinism", 6: "Reporting"}
CONFIRMED = {"high", "medium"}
NOOP_CHECKS = ("2a", "2b")  # documented no-op class


def load_inputs(root: Path = ROOT):
    """Return (audit rows, static scan, sample.json dict); ids kept as strings."""
    audit = pd.read_csv(root / "audit_log.csv", dtype=str, keep_default_na=False)
    scan = pd.read_csv(root / "results" / "static_scan.csv", dtype={"task_id": str})
    sample = json.loads((root / "sample.json").read_text(encoding="utf-8"))
    return audit, scan, sample


def normalize(audit: pd.DataFrame) -> pd.DataFrame:
    a = audit.copy()
    a["task_id"] = a["task_id"].astype(str).str.strip()
    a["defect"] = pd.to_numeric(a["defect"], errors="coerce").fillna(0).astype(int)
    a["category"] = pd.to_numeric(a["category"], errors="coerce")
    a["severity"] = a["severity"].astype(str).str.strip().str.lower()
    a["skeptic_ok"] = a["skeptic_ok"].astype(str).str.strip()
    a["check"] = a["check"].astype(str).str.strip().str.lower()
    return a


def defect_rows(audit: pd.DataFrame, ids, severities) -> pd.DataFrame:
    """Rows with defect=1 and severity in `severities`, restricted to task ids `ids`."""
    a = normalize(audit)
    return a[(a["defect"] == 1) & a["severity"].isin(severities) & a["task_id"].isin(set(ids))]


def defective_tasks(audit, ids, exclude_checks=()) -> int:
    """Distinct defective tasks in `ids` (each counted once), ignoring rows whose check is excluded."""
    rows = defect_rows(audit, ids, CONFIRMED)
    return rows.loc[~rows["check"].isin(exclude_checks), "task_id"].nunique()


def per_category(audit, ids, severities=CONFIRMED) -> dict:
    """Category -> number of distinct tasks in `ids` with >=1 matching defect row."""
    rows = defect_rows(audit, ids, severities)
    return {c: rows.loc[rows["category"] == c, "task_id"].nunique() for c in CATEGORIES}


def rows_per_category(audit, ids, severities) -> dict:
    rows = defect_rows(audit, ids, severities)
    return {c: int((rows["category"] == c).sum()) for c in CATEGORIES}


def unverified_rows(audit) -> int:
    """defect=1 rows with severity medium/high (whole file, incl. task_id ALL) whose skeptic_ok is empty."""
    a = normalize(audit)
    m = (a["defect"] == 1) & a["severity"].isin(CONFIRMED)
    return int((m & (a["skeptic_ok"] == "")).sum())


def wilson(k: int, n: int):
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return float(lo), float(hi)


def fmt_share(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]"


def rule_of_three(k: int, n: int, label: str) -> list:
    if k != 0:
        return []
    return [f"- {label}: 0/{n} → upper bound by the rule of three ≈ 3/{n} = {3 / n:.3f}"]


def noop_counts(scan: pd.DataFrame, ids):
    s = scan[scan["task_id"].isin(set(ids))]
    return int(s["noop_pass"].sum()), len(s), int(scan["noop_pass"].sum()), len(scan)


def build_markdown(audit, scan, sample) -> str:
    ids = sample["task_ids"]
    n = len(ids)
    k_s, n_s, k_all, n_all = noop_counts(scan, ids)
    L = [f"# Summary numbers", "", f"bench_commit: `{sample['bench_commit']}`", "",
         "Intervals: 95% Wilson.", "", "Table 1. Headline shares", "",
         "| quantity | share |", "|---|---|"]
    empty = len(audit) == 0
    L.append("| defective tasks, sampled tasks | "
             + ("no rows yet" if empty else fmt_share(defective_tasks(audit, ids), n)) + " |")
    k_ex = None if empty else defective_tasks(audit, ids, NOOP_CHECKS)
    L.append("| defective tasks, sampled tasks, excluding the documented no-op class (checks 2a, 2b) | "
             + ("no rows yet" if empty else fmt_share(k_ex, n)) + " |")
    L.append(f"| no-op pass, all airline tasks | {fmt_share(k_all, n_all)} |")
    L.append(f"| no-op pass, sampled tasks | {fmt_share(k_s, n_s)} |")
    L.append(f"| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | {unverified_rows(audit)} |")
    notes = rule_of_three(k_all, n_all, "no-op pass, all") + rule_of_three(k_s, n_s, "no-op pass, sampled")
    if empty:
        L += ["", "Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category", "",
              "no rows yet", "", "Table 3. Low-severity defects, by category (informational)", "",
              "no rows yet"]
    else:
        k_def = defective_tasks(audit, ids)
        notes += rule_of_three(k_def, n, "defective tasks")
        notes += rule_of_three(k_ex, n, "defective tasks excluding checks 2a, 2b")
        conf = per_category(audit, ids)
        L += ["", "Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category", "",
              "| category | share of sampled tasks |", "|---|---|"]
        for c, name in CATEGORIES.items():
            L.append(f"| {c} {name} | {fmt_share(conf[c], n)} |")
            notes += rule_of_three(conf[c], n, f"category {c} {name}")
        low_t, low_r = per_category(audit, ids, {"low"}), rows_per_category(audit, ids, {"low"})
        L += ["", "Table 3. Low-severity defects, by category (informational)", "",
              "| category | rows | sampled tasks |", "|---|---|---|"]
        L += [f"| {c} {name} | {low_r[c]} | {low_t[c]}/{n} |" for c, name in CATEGORIES.items()]
    if notes:
        L += ["", "Rule of three (k = 0)", ""] + notes
    return "\n".join(L) + "\n"


def make_figure(audit, scan, sample, out: Path):
    ids, n = sample["task_ids"], len(sample["task_ids"])
    _, _, k_all, n_all = noop_counts(scan, ids)
    bars = [(f"No-op pass: empty answer gets full score\n(all {n_all} tasks)", k_all, n_all)]
    if len(audit):
        conf = per_category(audit, ids)
        bars = [(f"{c}. {name}", conf[c], n) for c, name in CATEGORIES.items()] + bars
    labels = [b[0] for b in bars][::-1]
    p = [b[1] / b[2] for b in bars][::-1]
    ci = [wilson(b[1], b[2]) for b in bars][::-1]
    err = [[pi - lo for pi, (lo, _) in zip(p, ci)], [hi - pi for pi, (_, hi) in zip(p, ci)]]
    height = 2.2 + 0.55 * len(bars)
    fig, ax = plt.subplots(figsize=(8.5, height), dpi=150)
    fig.patch.set_facecolor("white")
    y = range(len(bars))
    ax.barh(y, p, color="#5b7aa6", height=0.6)
    ax.errorbar(p, y, xerr=err, fmt="none", ecolor="#9a9a9a", capsize=4, lw=1.2)
    for yi, pi, (_, hi), b in zip(y, p, ci, bars[::-1]):
        ax.text(hi + 0.015, yi, f"{b[1]}/{b[2]}", va="center", fontsize=9, color="#333333")
    ax.set_yticks(list(y), labels, fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of tasks with a confirmed defect")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(False)
    title = f"Benchmark audit: confirmed defects in {n} sampled airline tasks"
    if not len(audit):
        title = "Benchmark audit of airline tasks"
        ax.set_ylim(-1.2, 1.2)
        ax.text(0.5, 0.8, "no audit rows yet", fontsize=11, color="#666666", style="italic")
    ax.set_title(title, fontsize=11, loc="left")
    fig.text(0.01, 0.01, "Each bar is the share of tasks with that problem (the number next to it is the count);\n"
             "the grey whisker shows the range where the true share lies with 95% confidence (Wilson interval).",
             fontsize=8, color="#444444")
    fig.tight_layout(rect=(0, 0.45 / height, 1, 1))
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)


def run(root: Path = ROOT) -> str:
    audit, scan, sample = load_inputs(root)
    if len(audit) == 0:
        print("no rows yet")
    md = build_markdown(audit, scan, sample)
    (root / "summary_numbers.md").write_text(md, encoding="utf-8")
    make_figure(audit, scan, sample, root / "fig_defects.png")
    return md


def selftest():
    ids = [str(i) for i in range(1, 21)]
    cols = ["task_id", "category", "check", "defect", "severity", "skeptic_ok"]
    fake = pd.DataFrame([
        ["1", "2", "2b", "1", "high", "1"],     # task 1: two cat-2 rows -> counted once
        ["1", "2", "2c", "1", "medium", ""],
        ["1", "4", "4a", "1", "medium", "1"],
        ["10", "2", "2d", "1", "medium", ""],   # task 10: defective
        ["11", "2", "2a", "1", "high", "1"],    # task 11: only a 2a row -> excluded from no-op-free share
        ["3", "1", "1a", "1", "low", ""],       # task 3: low only -> not defective
        ["3", "5", "5a", "0", "", ""],
        ["0", "1", "1a", "1", "high", "1"],     # task 0: outside sample -> ignored
        ["ALL", "6", "6a", "1", "high", "1"],   # benchmark-wide row -> not a sampled task
    ], columns=cols).astype(str)
    assert defective_tasks(fake, ids) == 3
    assert defective_tasks(fake, ids, NOOP_CHECKS) == 2
    conf = per_category(fake, ids)
    assert conf == {1: 0, 2: 3, 3: 0, 4: 1, 5: 0, 6: 0}, conf
    assert per_category(fake, ids, {"low"})[1] == 1
    assert rows_per_category(fake, ids, {"low"}) == {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    assert unverified_rows(fake) == 2
    assert fmt_share(23, 50) == "23/50 = 0.460 [0.330, 0.596]"
    assert fmt_share(7, 20) == "7/20 = 0.350 [0.181, 0.567]"
    assert rule_of_three(0, 20, "x")[0].endswith("3/20 = 0.150")
    print("selftest passed")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    selftest() if "--selftest" in sys.argv else print(run())
