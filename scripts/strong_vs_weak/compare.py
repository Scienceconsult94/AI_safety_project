"""Strong vs weak (strong_vs_weak/PLAN.md): claude-sonnet-5-5 vs claude-haiku-5-5 as the agent on the 20 sampled airline tasks.

Inputs (repository root):
  sample.json                                        the 20 sampled task ids
  results/static_scan.csv                            noop_pass per task (the empty trajectory passes the stock scorer)
  results/runs/sample20_pass3_haiku.results.json     weak agent, 20 tasks x 3 (block 1)
  results/runs/sample20_sonnet_t3.results.json       strong agent, 20 tasks x 3 (scripts/runs/run_sonnet20.ps1 -Trials 3)
  results/v2/rescore.csv, results/v2/rescore_sonnet.csv   the same conversations re-scored under every block-2 configuration
Outputs: strong_vs_weak/summary.md, strong_vs_weak/per_task.csv, strong_vs_weak/fig_per_task.png
Metrics are the ones fixed in strong_vs_weak/PLAN.md before the run's results were read.
Usage (from the repository root):  python -I -X utf8 scripts/strong_vs_weak/compare.py      (Python 3.11 with pandas, scipy, statsmodels, matplotlib)
No model call.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import binomtest  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "strong_vs_weak"
RUNS = {"haiku": ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json",
        "sonnet": ROOT / "results" / "runs" / "sample20_sonnet_t3.results.json"}
RESCORE = {"haiku": ROOT / "results" / "v2" / "rescore.csv", "sonnet": ROOT / "results" / "v2" / "rescore_sonnet.csv"}
PRICES = {"haiku": (0.10, 0.50), "sonnet": (2.00, 10.00)}  # USD per MTok, claude-api reference (Haiku: prompts up to 100K tokens)
USER_PRICE = (0.10, 0.50)  # the user simulator is claude-haiku-5-5 in both runs
DEFECT_TASKS = ("7", "32", "44")  # block-1 task defects (wrong total; scenario forbids the reference; ambiguous layover reading)


def wilson(k: int, n: int) -> tuple[float, float]:
    return proportion_confint(k, n, alpha=0.05, method="wilson") if n else (float("nan"), float("nan"))


def share(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]" if n else "n/a"


def load_run(path: Path, ids: set[str]) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    per = defaultdict(list)
    term = Counter()
    tok = {"agent_in": 0, "agent_out": 0, "user_in": 0, "user_out": 0, "n_sims": 0, "infra": 0}
    for s in data["simulations"]:
        t = str(s["task_id"])
        if t not in ids:
            continue
        tr = str(s.get("termination_reason"))
        term[tr] += 1
        tok["n_sims"] += 1
        if tr == "infrastructure_error":
            tok["infra"] += 1
            continue
        r = (s.get("reward_info") or {}).get("reward")
        per[t].append((int(s.get("trial") or 0), r is not None and float(r) == 1.0))
        for m in s.get("messages") or []:
            u = m.get("usage") or {}
            pi = u.get("prompt_tokens") or u.get("input_tokens") or 0
            po = u.get("completion_tokens") or u.get("output_tokens") or 0
            if m.get("role") == "assistant":
                tok["agent_in"] += pi
                tok["agent_out"] += po
            elif m.get("role") == "user":
                tok["user_in"] += pi
                tok["user_out"] += po
    return {"per": {t: [ok for _, ok in sorted(v)] for t, v in per.items()}, "term": term, "tok": tok}


def tau2_pass(per: dict, tasks: list[str], k: int) -> float:
    el = [per[t] for t in tasks if t in per and len(per[t]) >= k]
    return sum(comb(sum(v), k) / comb(len(v), k) for v in el) / len(el) if el else float("nan")


def full(per: dict, tasks: list[str]) -> tuple[int, int]:
    el = [t for t in tasks if t in per and len(per[t]) >= 3]
    return sum(1 for t in el if sum(per[t][:3]) == 3), len(el)


def paired(a: dict, b: dict, tasks: list[str]) -> dict:
    """b relative to a: tasks where b has more / fewer / equal successes; exact sign test; exact McNemar on 3/3."""
    ahead = behind = equal = 0
    b_only = a_only = 0
    for t in tasks:
        ca, cb = sum(a.get(t, [])), sum(b.get(t, []))
        ahead += cb > ca
        behind += cb < ca
        equal += cb == ca
        fa, fb = len(a.get(t, [])) >= 3 and ca == 3, len(b.get(t, [])) >= 3 and cb == 3
        b_only += fb and not fa
        a_only += fa and not fb
    n = ahead + behind
    p_sign = binomtest(ahead, n, 0.5).pvalue if n else 1.0
    nd = a_only + b_only
    p_mc = binomtest(b_only, nd, 0.5).pvalue if nd else 1.0
    return {"ahead": ahead, "behind": behind, "equal": equal, "p_sign": p_sign, "b_only_3of3": b_only, "a_only_3of3": a_only, "p_mcnemar": p_mc}


def rescore_per(path: Path, agent: str, cfg: str, ids: set[str]) -> dict | None:
    if not path.exists():
        return None
    per = defaultdict(list)
    with open(path, encoding="utf-8", newline="") as fp:
        for r in csv.DictReader(fp):
            if r["agent"] != agent or str(r["task_id"]) not in ids:
                continue
            v = r.get(f"{cfg}_reward", "")
            per[str(r["task_id"])].append((int(r["trial"] or 0), v not in ("", "None") and float(v) == 1.0))
    return {t: [ok for _, ok in sorted(v)] for t, v in per.items()} if per else None


def main() -> int:
    sample = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))
    tasks = [str(t) for t in sample["task_ids"]]
    ids = set(tasks)
    noop = set()
    with open(ROOT / "results" / "static_scan.csv", encoding="utf-8", newline="") as fp:
        for r in csv.DictReader(fp):
            if r["task_id"] in ids and r["noop_pass"] == "1":
                noop.add(r["task_id"])
    others = [t for t in tasks if t not in noop]
    noop_l = [t for t in tasks if t in noop]
    run = {m: load_run(p, ids) for m, p in RUNS.items()}
    H, S = run["haiku"]["per"], run["sonnet"]["per"]

    L = ["# Strong vs weak: Sonnet and Haiku as the agent on the 20 sampled airline tasks", "",
         "Pre-registration: `strong_vs_weak/PLAN.md`, committed before any result of the Sonnet run was read. tau2-bench v2.0.0, "
         "same user simulator (claude-haiku-5-5), seed, scorer (stock, substring communicate check) and run settings; one run per model, "
         "a day apart. Intervals: 95% Wilson; tests: exact two-sided.", ""]

    # ---- 1. pass rates
    L += ["Table 1. Pass rates (stock scorer, as recorded)", "", "| quantity | claude-haiku-5-5 | claude-sonnet-5-5 |", "|---|---|---|"]
    for k in (1, 2, 3):
        L.append(f"| tau2 pass^{k} (mean over tasks of C(c,{k})/C(n,{k})) | {tau2_pass(H, tasks, k):.3f} | {tau2_pass(S, tasks, k):.3f} |")
    fh, fs = full(H, tasks), full(S, tasks)
    L.append(f"| tasks passed 3 of 3 | {share(*fh)} | {share(*fs)} |")
    th = sum(sum(v) for v in H.values()), sum(len(v) for v in H.values())
    ts = sum(sum(v) for v in S.values()), sum(len(v) for v in S.values())
    L.append(f"| passing trials (trials are not independent; interval for orientation only) | {share(*th)} | {share(*ts)} |")
    L.append(f"| tasks solved in 0 of 3 | {sum(1 for t in tasks if sum(H.get(t, [])) == 0)} | {sum(1 for t in tasks if sum(S.get(t, [])) == 0)} |")
    L.append(f"| infrastructure errors (excluded) | {run['haiku']['tok']['infra']} | {run['sonnet']['tok']['infra']} |")
    L.append(f"| terminations | {dict(run['haiku']['term'])} | {dict(run['sonnet']['term'])} |")

    # ---- 2 and 3. paired comparison, overall and by the no-op split
    L += ["", "Table 2. Paired per-task comparison (Sonnet relative to Haiku; successes out of 3 per task)", "",
          "| tasks | n | Sonnet ahead | behind | equal | sign test p | 3/3 only Sonnet | 3/3 only Haiku | McNemar p | tau2 pass^1 Haiku → Sonnet | tasks 3/3 Haiku → Sonnet |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    parts = (("all 20 sampled tasks", tasks), (f"the {len(noop_l)} no-op tasks (empty trajectory passes)", noop_l), (f"the {len(others)} other tasks", others))
    pair_all = None
    for label, ts_ in parts:
        pr = paired(H, S, ts_)
        if pair_all is None:
            pair_all = pr
        L.append(f"| {label} | {len(ts_)} | {pr['ahead']} | {pr['behind']} | {pr['equal']} | {pr['p_sign']:.3f} | {pr['b_only_3of3']} | {pr['a_only_3of3']} | {pr['p_mcnemar']:.3f} | "
                 f"{tau2_pass(H, ts_, 1):.3f} → {tau2_pass(S, ts_, 1):.3f} | {full(H, ts_)[0]} → {full(S, ts_)[0]} |")
    L.append("")
    L.append(f"No-op tasks of the sample: {', '.join(sorted(noop_l, key=int))}.")

    # ---- per-task table and csv
    rows = []
    for t in sorted(tasks, key=int):
        rows.append({"task_id": t, "noop_pass": int(t in noop), "haiku": "".join("1" if x else "0" for x in H.get(t, [])),
                     "sonnet": "".join("1" if x else "0" for x in S.get(t, [])), "haiku_c": sum(H.get(t, [])), "sonnet_c": sum(S.get(t, [])),
                     "block1_task_defect": int(t in DEFECT_TASKS)})
    with open(OUT / "per_task.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L += ["", "Table 3. Per task (1 = trial passed, in trial order)", "", "| task | no-op | Haiku | Sonnet | block-1 task defect |", "|---|---|---|---|---|"]
    L += [f"| {r['task_id']} | {'yes' if r['noop_pass'] else ''} | {r['haiku']} | {r['sonnet']} | {'yes' if r['block1_task_defect'] else ''} |" for r in rows]

    # ---- 4. v2 re-score
    L += ["", "Table 4. The same conversations re-scored (block-2 configurations; `results/v2/rescore.csv`, `rescore_sonnet.csv`)", ""]
    v2 = {}
    for cfg in ("v1", "T2_stock", "V2"):
        h = rescore_per(RESCORE["haiku"], "haiku", cfg, ids)
        s = rescore_per(RESCORE["sonnet"], "sonnet", cfg, ids)
        v2[cfg] = (h, s)
    if all(h is not None and s is not None for h, s in v2.values()):
        L += ["| configuration | tau2 pass^1 Haiku | tau2 pass^1 Sonnet | gap | tasks 3/3 Haiku | tasks 3/3 Sonnet | sign test p (Sonnet vs Haiku) |", "|---|---|---|---|---|---|---|"]
        names = {"v1": "stock scorer, tasks v1 (as recorded)", "T2_stock": "stock scorer, tasks v2 (corrected criteria)", "V2": "full v2 (canonical hash, word-boundary check, 3-vote judge on assertions)"}
        for cfg, (h, s) in v2.items():
            pr = paired(h, s, tasks)
            g = tau2_pass(s, tasks, 1) - tau2_pass(h, tasks, 1)
            L.append(f"| {names[cfg]} | {tau2_pass(h, tasks, 1):.3f} | {tau2_pass(s, tasks, 1):.3f} | {g:+.3f} | {full(h, tasks)[0]} | {full(s, tasks)[0]} | {pr['p_sign']:.3f} |")
        hv1 = v2["v1"][1]
        rec_ok = all(hv1.get(t) == S.get(t) for t in tasks)
        L.append("")
        L.append(f"Replay check: the v1 re-score of the Sonnet run reproduces the recorded rewards on every task: {'yes' if rec_ok else 'NO'}.")
    else:
        L.append("not available yet: run `scripts/v2/rescore.py --set sonnet` from inside tau2-bench")

    # ---- 5. cost and tokens
    L += ["", "Table 5. Tokens and cost (own estimate from the recorded usage; claude-api reference prices)", "",
          "| quantity | claude-haiku-5-5 run | claude-sonnet-5-5 run |", "|---|---|---|"]
    cost = {}
    for m in ("haiku", "sonnet"):
        tk = run[m]["tok"]
        pa, pb = PRICES[m]
        cost[m] = (tk["agent_in"] * pa + tk["agent_out"] * pb + tk["user_in"] * USER_PRICE[0] + tk["user_out"] * USER_PRICE[1]) / 1e6
    th_, ts_ = run["haiku"]["tok"], run["sonnet"]["tok"]
    L.append(f"| agent input / output tokens | {th_['agent_in']:,} / {th_['agent_out']:,} | {ts_['agent_in']:,} / {ts_['agent_out']:,} |")
    L.append(f"| agent output tokens per simulation | {th_['agent_out'] / max(th_['n_sims'], 1):,.0f} | {ts_['agent_out'] / max(ts_['n_sims'], 1):,.0f} |")
    L.append(f"| user-simulator input / output tokens | {th_['user_in']:,} / {th_['user_out']:,} | {ts_['user_in']:,} / {ts_['user_out']:,} |")
    L.append(f"| cost of the run, agent and user simulator | ${cost['haiku']:.2f} | ${cost['sonnet']:.2f} |")

    # ---- predictions
    p1h, p1s = tau2_pass(H, tasks, 1), tau2_pass(S, tasks, 1)
    d1 = p1s - p1h
    noop_pr = paired(H, S, noop_l)
    oth_pr = paired(H, S, others)
    defect_zero = sum(1 for t in DEFECT_TASKS if sum(S.get(t, [])) == 0)
    L += ["", "Table 6. Pre-registered predictions against the measurements", "", "| id | prediction | measured | verdict |", "|---|---|---|---|"]
    L.append(f"| P1 | Sonnet's tau2 pass^1 above Haiku's 0.733, likely by +0.05 to +0.15 | {p1h:.3f} → {p1s:.3f} ({d1:+.3f}) | {'held' if d1 > 0 else 'failed'}{'' if 0.05 <= d1 <= 0.15 else ' (outside the expected range)'} |")
    L.append(f"| P2 | the paired sign test does not reach p < 0.05 | p = {pair_all['p_sign']:.3f} ({pair_all['ahead']} ahead, {pair_all['behind']} behind, {pair_all['equal']} equal) | {'held' if pair_all['p_sign'] >= 0.05 else 'failed'} |")
    hn, sn = tau2_pass(H, noop_l, 1), tau2_pass(S, noop_l, 1)
    L.append(f"| P3 | both close to 3/3 on the {len(noop_l)} no-op tasks; the gap sits in the {len(others)} others | no-op tasks pass^1 {hn:.3f} / {sn:.3f}; others {tau2_pass(H, others, 1):.3f} / {tau2_pass(S, others, 1):.3f}; tasks with a different count: no-op {noop_pr['ahead'] + noop_pr['behind']}, others {oth_pr['ahead'] + oth_pr['behind']} | see the numbers |")
    L.append(f"| P4 | at least 2 of tasks 7, 32, 44 stay at 0/3 for Sonnet | " + ", ".join(f"{t}: {sum(S.get(t, []))}/3" for t in DEFECT_TASKS) + f" | {'held' if defect_zero >= 2 else 'failed'} |")
    if all(h is not None and s is not None for h, s in v2.values()):
        g1 = tau2_pass(v2['v1'][1], tasks, 1) - tau2_pass(v2['v1'][0], tasks, 1)
        g2 = tau2_pass(v2['V2'][1], tasks, 1) - tau2_pass(v2['V2'][0], tasks, 1)
        L.append(f"| P5 | the gap does not shrink under v2 | gap {g1:+.3f} (v1) → {g2:+.3f} (V2) | {'held' if g2 >= g1 - 1e-9 else 'failed'} |")
    else:
        L.append("| P5 | the gap does not shrink under v2 | re-score not available | open |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- figure: successes per task, both models; no-op tasks shaded
    order = sorted(tasks, key=lambda t: (t in noop, int(t)))
    fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=150)
    y = list(range(len(order)))[::-1]
    for yy, t in zip(y, order):
        if t in noop:
            ax.axhspan(yy - 0.5, yy + 0.5, color="#eeeeee", zorder=0)
        ch, cs = sum(H.get(t, [])), sum(S.get(t, []))
        ax.plot([ch, cs], [yy, yy], color="#999999", lw=1, zorder=1)
    ax.scatter([sum(H.get(t, [])) for t in order], y, s=60, color="#c0504d", label="claude-haiku-5-5", zorder=2)
    ax.scatter([sum(S.get(t, [])) for t in order], y, s=60, marker="D", facecolors="none", edgecolors="#4a6fa5", linewidths=1.6, label="claude-sonnet-5-5", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"task {t}" + (" (passes empty)" if t in noop else "") + (" *" if t in DEFECT_TASKS else "") for t in order], fontsize=7.5)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xlim(-0.3, 3.3)
    ax.set_xlabel("trials passed out of 3 (stock scorer)")
    ax.set_title("Same exam, two agent models: trials passed per task (20 sampled airline tasks)", fontsize=9.5)
    ax.legend(loc="lower right", fontsize=8)
    fig.text(0.01, 0.005, "Grey rows: tasks an empty conversation passes. * task with a defect found in block 1 (7, 32, 44).", fontsize=7)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "fig_per_task.png", dpi=150, facecolor="white")
    plt.close(fig)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
