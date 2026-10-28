"""Recompute the audit summary numbers and the defect chart from the CSV files.

Inputs (next to this script): audit_log.csv, results/static_scan.csv, sample.json.
Outputs: summary_numbers.md (numbers only) and fig_defects.png.
Defect rule (schema.md): a task is defective iff it has >=1 row with defect=1
and severity in {high, medium}. Headline counts leave out the documented no-op class (checks 2a, 2b), which is
reported separately as the no-op pass; the counts that include it are listed as their own rows. All intervals: 95% Wilson.
Run:  python -I scripts/make_summary.py            (write outputs)
      python -I scripts/make_summary.py --selftest (check the counting rules on fake data)
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

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
CATEGORIES = {1: "Solvability", 2: "Scoring validity", 3: "Isolation and leaks",
              4: "Specification clarity", 5: "Determinism", 6: "Reporting"}
CONFIRMED = {"high", "medium"}
NOOP_CHECKS = ("2a", "2b")  # documented no-op class: reported separately from the headline defect counts
AGENT_RUN = "agent_run"  # method of rows from live runs; static and probe come from the static phase
USER_SIM_CHECKS = ("5d",)  # user-simulator deviations
SUBSTRING_CHECKS = ("2g",)  # apply only to the substring communicate scorer the runs selected


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
    a["method"] = a["method"].astype(str).str.strip().str.lower() if "method" in a else ""
    return a


def defect_rows(audit: pd.DataFrame, ids, severities) -> pd.DataFrame:
    """Rows with defect=1 and severity in `severities`, restricted to task ids `ids`."""
    a = normalize(audit)
    return a[(a["defect"] == 1) & a["severity"].isin(severities) & a["task_id"].isin(set(ids))]


def defective_task_ids(audit, ids, exclude_checks=(), methods=None, exclude_methods=()) -> set:
    """Distinct defective task ids in `ids`, ignoring rows whose check is excluded;
    `methods` keeps only rows of those methods, `exclude_methods` drops rows of those methods."""
    rows = defect_rows(audit, ids, CONFIRMED)
    m = ~rows["check"].isin(exclude_checks) & ~rows["method"].isin(exclude_methods)
    if methods is not None:
        m &= rows["method"].isin(methods)
    return set(rows.loc[m, "task_id"])


def defective_tasks(audit, ids, exclude_checks=(), methods=None, exclude_methods=()) -> int:
    """Distinct defective tasks in `ids` (each counted once), ignoring rows whose check is excluded."""
    return len(defective_task_ids(audit, ids, exclude_checks, methods, exclude_methods))


def agent_run_only_tasks(audit, ids) -> int:
    """Tasks defective over all methods but not over static/probe rows: their only confirmed defects are agent_run."""
    return len(defective_task_ids(audit, ids) - defective_task_ids(audit, ids, exclude_methods=(AGENT_RUN,)))


def rows_per_check(audit, ids) -> list:
    """[(check, confirmed defect rows, distinct sampled tasks)] sorted by check id, checks with >=1 row only."""
    rows = defect_rows(audit, ids, CONFIRMED)
    g = rows.groupby("check")["task_id"].agg(["size", "nunique"])
    return [(c, int(g.at[c, "size"]), int(g.at[c, "nunique"])) for c in sorted(g.index, key=_check_key)]


def _check_key(c: str):
    head = c.rstrip("abcdefghijklmnopqrstuvwxyz")
    return (int(head), c) if head.isdigit() else (10**9, c)


def defective_tasks_noop_free(audit, ids, noop_ids) -> int:
    """Defective tasks after dropping no-op-derived rows: check 2a/2b, or 2k on a task with noop_pass=1."""
    rows = defect_rows(audit, ids, CONFIRMED)
    derived = rows["check"].isin(NOOP_CHECKS) | ((rows["check"] == "2k") & rows["task_id"].isin(set(noop_ids)))
    return rows.loc[~derived, "task_id"].nunique()


def per_category(audit, ids, severities=CONFIRMED, exclude_checks=()) -> dict:
    """Category -> number of distinct tasks in `ids` with >=1 matching defect row, ignoring rows whose check is excluded."""
    rows = defect_rows(audit, ids, severities)
    rows = rows[~rows["check"].isin(exclude_checks)]
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


RUN_FILES = {"haiku": "sample20_pass3_haiku.results.json", "gt": "sample20_gt_haiku.results.json"}


def load_runs(root: Path = ROOT):
    """Return {"haiku": simulations, "gt": simulations} from results/runs, or None if a file is missing."""
    paths = {k: root / "results" / "runs" / f for k, f in RUN_FILES.items()}
    if not all(p.exists() for p in paths.values()):
        return None
    return {k: json.loads(p.read_text(encoding="utf-8"))["simulations"] for k, p in paths.items()}


def _id_key(t: str):
    return (0, int(t), t) if t.isdigit() else (1, 0, t)


def agent_run_stats(runs: dict, ids) -> dict:
    """Per-task trial outcomes on sampled ids, infrastructure_error simulations excluded."""
    ids = set(map(str, ids))
    out, n_infra = {}, 0
    for key, sims in runs.items():
        per = {}
        for s in sims:
            t = str(s["task_id"])
            if t not in ids:
                continue
            if s.get("termination_reason") == "infrastructure_error":
                n_infra += 1
                continue
            r = (s.get("reward_info") or {}).get("reward")
            per.setdefault(t, []).append((int(s["trial"]), r is not None and float(r) == 1.0))
        out[key] = {t: [ok for _, ok in sorted(v)] for t, v in per.items()}
    h, g = out["haiku"], out["gt"]
    st = {"infra": n_infra}
    for k in (1, 2, 3):
        elig = [t for t, v in h.items() if len(v) >= k]
        st[f"pass{k}"] = (sum(all(h[t][:k]) for t in elig), len(elig))
    h3 = {t: sum(v[:3]) for t, v in h.items() if len(v) >= 3}
    st["n3"] = len(h3)
    st["s0"] = sum(x == 0 for x in h3.values())
    st["s12"] = sum(x in (1, 2) for x in h3.values())
    st["s3"] = sum(x == 3 for x in h3.values())
    gt_ok = {t: v[0] for t, v in g.items()}
    st["gt"] = (sum(gt_ok.values()), len(gt_ok))
    st["gt_fail"] = sorted((t for t, ok in gt_ok.items() if not ok), key=_id_key)
    st["h_not_gt"] = sorted((t for t, ok in gt_ok.items() if not ok and any(h.get(t, []))), key=_id_key)
    st["gt_not_h"] = sorted((t for t, ok in gt_ok.items() if ok and t in h3 and h3[t] == 0), key=_id_key)
    return st


def _share(k: int, n: int) -> str:
    return fmt_share(k, n) if n else f"{k}/0 (no tasks)"


def agent_runs_table(runs, ids) -> list:
    title = "Table 4. Agent runs (claude-haiku-5-5 agent and user, substring scorer)"
    if runs is None:
        return ["", title, "", "agent runs: not available"]
    st = agent_run_stats(runs, ids)
    n3, ids_ = st["n3"], lambda xs: ", ".join(xs) if xs else "none"
    L = ["", title, "", "| quantity | value |", "|---|---|"]
    L += [f"| pass^{k}, sampled tasks (first {k} trial(s) all reward 1.0) | {_share(*st[f'pass{k}'])} |"
          for k in (1, 2, 3)]
    L.append(f"| tasks solved in 0/3 trials | {_share(st['s0'], n3)} |")
    L.append(f"| tasks solved in 1/3 or 2/3 trials (unstable) | {_share(st['s12'], n3)} |")
    L.append(f"| tasks solved in 3/3 trials | {_share(st['s3'], n3)} |")
    L.append(f"| ground-truth agent reaches the target state (reward 1.0) | {_share(*st['gt'])} |")
    L.append(f"| Haiku passes ≥1 trial, ground-truth agent fails | {len(st['h_not_gt'])} |")
    L.append(f"| ground-truth agent passes, Haiku 0/3 | {len(st['gt_not_h'])} |")
    L.append(f"| infrastructure_error simulations excluded | {st['infra']} |")
    L += ["", f"- ground-truth agent fails on tasks: {ids_(st['gt_fail'])}",
          f"- Haiku passes ≥1 trial, ground-truth agent fails: {ids_(st['h_not_gt'])}",
          f"- ground-truth agent passes, Haiku 0/3: {ids_(st['gt_not_h'])}"]
    return L


def rereview_table(path: Path) -> list:
    """Table 5: blind re-review agreement from results/rereview.csv (rereview_agreement.py)."""
    if not path.exists():
        return ["", "Table 5. Blind re-review", "", "blind re-review: not available"]
    df = pd.read_csv(path, dtype=str).fillna("")
    out = ["", "Table 5. Blind re-review of 3 sampled tasks (labels compared on defect 0/1 per task x check)", "",
           "| comparison | agreement | Cohen's kappa |", "|---|---|---|"]
    for col, label in (("original_defect", "blind vs original reviewer labels"),
                       ("corrected_defect", "blind vs skeptic-corrected labels")):
        sub = df[df[col] != ""]
        a, b = sub[col].astype(str), sub["blind_defect"].astype(str)
        n = len(sub)
        if n == 0:
            out.append(f"| {label} | n/a | n/a |")
            continue
        po = float((a == b).mean())
        pe = float((a == "1").mean() * (b == "1").mean() + (a == "0").mean() * (b == "0").mean())
        kappa = float("nan") if pe >= 1.0 else (po - pe) / (1 - pe)
        out.append(f"| {label} | {int((a == b).sum())}/{n} = {po:.3f} | {kappa:.3f} |")
    tasks = sorted(df["task_id"].unique(), key=lambda x: int(x) if str(x).isdigit() else 0)
    out.append(f"\n- tasks: {', '.join(tasks)}; rows: {len(df)}; disagreements listed in results/rereview_summary.md")
    return out


def build_markdown(audit, scan, sample, runs=None) -> str:
    ids = sample["task_ids"]
    n = len(ids)
    k_s, n_s, k_all, n_all = noop_counts(scan, ids)
    L = [f"# Summary numbers", "", f"bench_commit: `{sample['bench_commit']}`", "",
         "Intervals: 95% Wilson.", "", "Table 1. Headline shares", "",
         "| quantity | share |", "|---|---|"]
    empty = len(audit) == 0
    L.append("| defective tasks, sampled tasks (headline; the documented no-op class, checks 2a and 2b, is reported "
             "separately as the no-op pass below) | "
             + ("no rows yet" if empty else fmt_share(defective_tasks(audit, ids, NOOP_CHECKS), n)) + " |")
    split = [] if empty else [
        ("static and probe checks only (method ≠ agent_run)",
         defective_tasks(audit, ids, NOOP_CHECKS, exclude_methods=(AGENT_RUN,))),
        ("agent_run checks only (1e, 4f, 5c, 5d, 5e, 5f)", defective_tasks(audit, ids, methods=(AGENT_RUN,))),
        ("agent_run checks excluding 5d (user-simulator deviations)",
         defective_tasks(audit, ids, USER_SIM_CHECKS, methods=(AGENT_RUN,)))]
    for label, k in split:
        L.append(f"| defective tasks, sampled tasks, {label} | {fmt_share(k, n)} |")
    k_new = None if empty else agent_run_only_tasks(audit, ids)
    L.append("| tasks whose only confirmed defects come from agent_run checks (new versus the static phase) | "
             + ("no rows yet" if empty else fmt_share(k_new, n)) + " |")
    k_ex = None if empty else defective_tasks(audit, ids)
    L.append("| defective tasks, sampled tasks, counting the documented no-op class (checks 2a, 2b), all checks | "
             + ("no rows yet" if empty else fmt_share(k_ex, n)) + " |")
    L.append("| defective tasks, sampled tasks, counting the documented no-op class, static and probe checks only | "
             + ("no rows yet" if empty else fmt_share(defective_tasks(audit, ids, exclude_methods=(AGENT_RUN,)), n)) + " |")
    k_sub = None if empty else defective_tasks(audit, ids, NOOP_CHECKS + SUBSTRING_CHECKS)
    L.append("| defective tasks, sampled tasks, also excluding check 2g (it applies only to the substring communicate "
             "scorer the runs selected; the v2.0.0 default is a semantic judge) | "
             + ("no rows yet" if empty else fmt_share(k_sub, n)) + " |")
    noop_ids = scan.loc[scan["noop_pass"] == 1, "task_id"]
    k_nf = None if empty else defective_tasks_noop_free(audit, ids, noop_ids)
    L.append("| defective tasks, sampled tasks, excluding every defect that derives from the no-op design "
             "(checks 2a, 2b, and 2k rows on tasks with noop_pass = 1 in results/static_scan.csv) | "
             + ("no rows yet" if empty else fmt_share(k_nf, n)) + " |")
    L.append(f"| no-op pass, all airline tasks | {fmt_share(k_all, n_all)} |")
    L.append(f"| no-op pass, sampled tasks | {fmt_share(k_s, n_s)} |")
    L.append(f"| medium/high defect rows with skeptic_ok empty (whole file, incl. task_id ALL) | {unverified_rows(audit)} |")
    notes = rule_of_three(k_all, n_all, "no-op pass, all") + rule_of_three(k_s, n_s, "no-op pass, sampled")
    if empty:
        L += ["", "Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category", "",
              "no rows yet", "", "Table 3. Low-severity defects, by category (informational)", "",
              "no rows yet"]
    else:
        k_def = defective_tasks(audit, ids, NOOP_CHECKS)
        notes += rule_of_three(k_def, n, "defective tasks")
        notes += rule_of_three(k_ex, n, "defective tasks counting checks 2a, 2b")
        notes += rule_of_three(k_nf, n, "defective tasks excluding no-op-derived defects")
        conf = per_category(audit, ids, exclude_checks=NOOP_CHECKS)
        L += ["", "Table 2. Sampled tasks with ≥1 confirmed defect (high/medium), by category "
              "(the no-op class, checks 2a and 2b, is reported separately)", "",
              "| category | share of sampled tasks |", "|---|---|"]
        for c, name in CATEGORIES.items():
            L.append(f"| {c} {name} | {fmt_share(conf[c], n)} |")
            notes += rule_of_three(conf[c], n, f"category {c} {name}")
        L += ["", "Table 2b. Confirmed defect rows by check (all methods)", "",
              "| check | defect rows (high/medium) | sampled tasks |", "|---|---|---|"]
        L += [f"| {c} | {r} | {t}/{n} |" for c, r, t in rows_per_check(audit, ids)]
        low_t, low_r = per_category(audit, ids, {"low"}), rows_per_category(audit, ids, {"low"})
        L += ["", "Table 3. Low-severity defects, by category (informational)", "",
              "| category | rows | sampled tasks |", "|---|---|---|"]
        L += [f"| {c} {name} | {low_r[c]} | {low_t[c]}/{n} |" for c, name in CATEGORIES.items()]
    L += agent_runs_table(runs, ids)
    L += rereview_table(ROOT / "results" / "rereview.csv")
    if notes:
        L += ["", "Rule of three (k = 0)", ""] + notes
    return "\n".join(L) + "\n"


def make_figure(audit, scan, sample, out: Path):
    ids, n = sample["task_ids"], len(sample["task_ids"])
    _, _, k_all, n_all = noop_counts(scan, ids)
    bars = [(f"No-op pass: empty answer gets full score\n(all {n_all} tasks; reported separately)", k_all, n_all)]
    if len(audit):
        conf = per_category(audit, ids, exclude_checks=NOOP_CHECKS)
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
    md = build_markdown(audit, scan, sample, load_runs(root))
    (root / "summary_numbers.md").write_text(md, encoding="utf-8")
    make_figure(audit, scan, sample, root / "fig_defects.png")
    return md


def selftest():
    ids = [str(i) for i in range(1, 21)]
    cols = ["task_id", "category", "check", "defect", "severity", "skeptic_ok"]
    static = pd.DataFrame([
        ["1", "2", "2b", "1", "high", "1"],     # task 1: two cat-2 rows -> counted once
        ["1", "2", "2c", "1", "medium", ""],
        ["1", "4", "4a", "1", "medium", "1"],
        ["10", "2", "2d", "1", "medium", ""],   # task 10: defective
        ["11", "2", "2a", "1", "high", "1"],    # task 11: only a 2a row -> excluded from no-op-free share
        ["12", "2", "2k", "1", "high", "1"],    # task 12: 2k on a no-op task -> no-op-derived
        ["14", "2", "2k", "1", "medium", "1"],  # task 14: 2k on a non-no-op task -> still counts
        ["3", "1", "1a", "1", "low", ""],       # task 3: low only -> not defective
        ["3", "5", "5a", "0", "", ""],
        ["0", "1", "1a", "1", "high", "1"],     # task 0: outside sample -> ignored
        ["ALL", "6", "6a", "1", "high", "1"],   # benchmark-wide row -> not a sampled task
    ], columns=cols).astype(str)
    static["method"] = "static"
    agent = pd.DataFrame([
        ["5", "5", "5d", "1", "medium", "1"],   # task 5: only a 5d row -> new versus static, dropped without 5d
        ["10", "1", "1e", "1", "high", ""],     # task 10: already defective statically -> not new
        ["7", "5", "5c", "0", "", ""],          # task 7: agent_run non-defect -> ignored
    ], columns=cols).astype(str)
    agent["method"] = AGENT_RUN
    fake = pd.concat([static, agent], ignore_index=True)
    assert defective_tasks(static, ids) == 5
    assert defective_tasks(fake, ids) == 6
    assert defective_tasks(fake, ids, NOOP_CHECKS) == 5
    assert defective_tasks_noop_free(fake, ids, ["11", "12"]) == 4  # tasks 1, 5, 10, 14
    assert defective_tasks(fake, ids, exclude_methods=(AGENT_RUN,)) == 5
    assert defective_tasks(fake, ids, methods=(AGENT_RUN,)) == 2       # tasks 5, 10
    assert defective_tasks(fake, ids, USER_SIM_CHECKS, methods=(AGENT_RUN,)) == 1  # task 10
    assert agent_run_only_tasks(fake, ids) == 1                        # task 5
    assert rows_per_check(fake, ids) == [("1e", 1, 1), ("2a", 1, 1), ("2b", 1, 1), ("2c", 1, 1), ("2d", 1, 1),
                                         ("2k", 2, 2), ("4a", 1, 1), ("5d", 1, 1)], rows_per_check(fake, ids)
    conf = per_category(fake, ids)
    assert conf == {1: 1, 2: 5, 3: 0, 4: 1, 5: 1, 6: 0}, conf
    assert per_category(fake, ids, {"low"})[1] == 1
    assert rows_per_category(fake, ids, {"low"}) == {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    assert unverified_rows(fake) == 3
    assert fmt_share(23, 50) == "23/50 = 0.460 [0.330, 0.596]"
    assert fmt_share(7, 20) == "7/20 = 0.350 [0.181, 0.567]"
    assert rule_of_three(0, 20, "x")[0].endswith("3/20 = 0.150")
    # Table 4 on two tiny synthetic results.json files
    import tempfile

    def sim(t, trial, r, term="user_stop"):
        return {"task_id": t, "trial": trial, "reward_info": {"reward": r}, "termination_reason": term}
    haiku = [sim(t, i, r) for t, rs in {"1": [1.0] * 3, "2": [1.0, 0.0, 1.0], "3": [0.0] * 3}.items()
             for i, r in enumerate(rs)]
    haiku += [sim("3", 3, 1.0, "infrastructure_error"), sim("99", 0, 1.0)]  # excluded / outside sample
    gt = [sim("1", 0, 1.0), sim("2", 0, 0.0), sim("3", 0, 1.0)]
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td) / "results" / "runs"
        rd.mkdir(parents=True)
        assert load_runs(Path(td)) is None
        for key, sims in (("haiku", haiku), ("gt", gt)):
            (rd / RUN_FILES[key]).write_text(json.dumps({"simulations": sims}), encoding="utf-8")
        st = agent_run_stats(load_runs(Path(td)), ids)
    assert st["pass1"] == (2, 3) and st["pass3"] == (1, 3), st
    assert st["gt"] == (2, 3) and st["gt_fail"] == ["2"], st
    assert st["h_not_gt"] == ["2"] and st["gt_not_h"] == ["3"] and st["infra"] == 1, st
    assert "agent runs: not available" in "\n".join(agent_runs_table(None, ids))
    print("selftest passed")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    selftest() if "--selftest" in sys.argv else print(run())
