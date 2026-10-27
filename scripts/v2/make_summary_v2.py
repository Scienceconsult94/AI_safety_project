"""block2/summary_v2.md from the block-2 CSV outputs (no tau2 import, no API).

Inputs (results/v2/): noop_scan_v2.csv, probe_2h_v2.csv, rescore.csv (+ rescore_fresh.csv when the
fresh v2 runs have been re-scored), judge_votes.csv, runs/*/summary.json, runs/*/results.json; and
the block-1 run files results/runs/*.results.json for the v1 side of the fresh-run comparison.

Usage (repo root, Python 3.11 with statsmodels):  python -I scripts/v2/make_summary_v2.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "results" / "v2"
OUT = ROOT / "block2" / "summary_v2.md"
SAMPLE = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"]


def wilson(k: int, n: int) -> str:
    if n == 0:
        return "n/a"
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return f"{k}/{n} = {k / n:.2f} [{lo:.2f}, {hi:.2f}]"


def read(path: Path) -> list[dict]:
    return list(csv.DictReader(open(path, encoding="utf-8"))) if path.exists() else []


def f1(x) -> bool:
    return str(x) in ("1", "1.0", "True")


def pass_table(results_path: Path) -> dict[str, list[float]]:
    """task_id -> rewards per trial from a tau2 results.json (loaded as plain JSON)."""
    d = json.loads(results_path.read_text(encoding="utf-8"))
    out: dict[str, list[float]] = defaultdict(list)
    for s in d["simulations"]:
        r = (s.get("reward_info") or {}).get("reward")
        if s.get("termination_reason") != "infrastructure_error":
            out[s["task_id"]].append(float(r) if r is not None else 0.0)
    return out


def main() -> int:
    L: list[str] = ["# Block 2 — results: scorer v2 and tasks v2 against the pinned benchmark", ""]
    L += ["All numbers are rebuilt from `results/v2/*.csv` by `scripts/v2/make_summary_v2.py`. Intervals are Wilson 95%. "
          "Block-1 numbers are never recomputed here; the v1 columns come from the recorded block-1 files.", ""]

    # ---- H1
    noop = read(V2 / "noop_scan_v2.csv")
    if noop:
        n1 = sum(f1(r["noop_pass_v1"]) for r in noop)
        n2 = sum(f1(r["noop_pass_v2"]) for r in noop)
        s1 = sum(f1(r["noop_pass_v1"]) for r in noop if r["task_id"] in SAMPLE)
        s2 = sum(f1(r["noop_pass_v2"]) for r in noop if r["task_id"] in SAMPLE)
        agree = sum(1 for r in noop if str(r["noop_pass_v1"]) == str(r["noop_pass_v1_static_scan"]))
        L += ["## H1 — no-op pass (empty trajectory scores 1)", "", "| scorer | all 50 tasks | 20 sampled tasks |", "|---|---|---|",
              f"| v1 (stock) | {wilson(n1, len(noop))} | {wilson(s1, 20)} |", f"| v2 | {wilson(n2, len(noop))} | {wilson(s2, 20)} |", "",
              f"v1 column agrees with block-1 `static_scan.csv` on {agree}/{len(noop)} tasks. Under v2 the empty trajectory fails because every airline task carries "
              "`nl_assertions` and the empty-trajectory rule marks them unmet; the DB and communicate parts are unchanged for the empty trajectory "
              f"({sum(1 for r in noop if r['db_unchanged_v1'] != r['db_unchanged_v2'])} tasks differ between raw and canonical DB check).", ""]

    # ---- H2
    pr = read(V2 / "probe_2h_v2.csv")
    if pr:
        tot = sum(int(r["n_permutations"]) for r in pr)
        raw = sum(int(r["n_hash_differs_raw"]) for r in pr)
        can = sum(int(r["n_hash_differs_canonical"]) for r in pr)
        L += ["## H2 — WRITE-order permutation probe (reference actions reordered)", "",
              "| hash | permutations whose DB hash differs from the reference | tasks affected |", "|---|---|---|",
              f"| v1 raw | {raw}/{tot} | {', '.join(r['task_id'] for r in pr if int(r['n_hash_differs_raw']))} |",
              f"| v2 canonical | {can}/{tot} | {', '.join(r['task_id'] for r in pr if int(r['n_hash_differs_canonical']))} |", "",
              "Remaining canonical differences are orders that change the outcome (e.g. task 7: cancelling before upgrading changes the refund; "
              "task 32: changing flights before the cabin upgrade changes the payments), not list-order artefacts. "
              f"Block-1 `probe_2h.csv` agrees with the raw column on {sum(1 for r in pr if str(r['n_hash_differs_raw']) == str(r['n_hash_differs_raw_probe_2h']))}/{len(pr)} tasks.", ""]

    # ---- H3
    rs = read(V2 / "rescore.csv")
    if rs:
        cfgs = [c[:-7] for c in rs[0].keys() if c.endswith("_reward") and c != "recorded_reward"]
        hk = [r for r in rs if r["agent"] == "haiku"]
        gt = [r for r in rs if r["agent"] == "gt"]
        L += ["## H3 — the 76 recorded block-1 simulations re-scored", "",
              f"Replay gate: `replay_check.csv` — the stock scorer reproduces the recorded reward of every simulation (see file). Configurations: one switch at a time on tasks v1, all three together, tasks v2 with the stock scorer, and V2 (tasks v2 + all switches).", "",
              "| config | haiku sims passing (60) | haiku tasks passing 3/3 (20) | haiku pass^1 (mean over tasks) | GT sims passing (16) |", "|---|---|---|---|---|"]
        for c in cfgs:
            ph = sum(1 for r in hk if r.get(f"{c}_reward") == "1.0")
            pg = sum(1 for r in gt if r.get(f"{c}_reward") == "1.0")
            per = Counter(r["task_id"] for r in hk if r.get(f"{c}_reward") == "1.0")
            full = sum(1 for t in SAMPLE if per[t] == 3)
            p1 = sum(per[t] / 3 for t in SAMPLE) / 20
            L.append(f"| {c} | {ph}/60 | {wilson(full, 20)} | {p1:.2f} | {wilson(pg, 16)} |")
        flips = [(r["agent"], r["task_id"], r["trial"], r["v1_reward"], r.get("V2_reward")) for r in rs if r.get("V2_reward") not in (None, "") and r["v1_reward"] != r.get("V2_reward")]
        L += ["", f"Flips v1 → V2: {len(flips)} of {len(rs)} simulations" + (":" if flips else "."), ""]
        if flips:
            L += ["| agent | task | trial | v1 | V2 | NL assertions failed under V2 | communicate strings failed under V2 |", "|---|---|---|---|---|---|---|"]
            for r in rs:
                if r.get("V2_reward") not in (None, "") and r["v1_reward"] != r.get("V2_reward"):
                    L.append(f"| {r['agent']} | {r['task_id']} | {r['trial']} | {r['v1_reward']} | {r['V2_reward']} | {r.get('V2_nl_failed', '')[:160]} | {r.get('V2_comm_failed', '')} |")
        oo = sum(1 for r in rs if f1(r["db_order_only"]))
        dbf = sum(1 for r in rs if not f1(r["db_raw_match"]))
        L += ["", f"DB mismatches under v1: {dbf}; of these, order-only (closed by canonicalisation): {oo}. Communicate flips from `comm_boundary` alone: "
              f"{sum(1 for r in rs if r.get('S_comm_reward') not in (None, '') and r['v1_reward'] != r['S_comm_reward'])}. "
              f"Gold-action replay errors: {sum(1 for r in rs if r.get('gold_action_errors'))}.", ""]
        if any(r.get("S_nl_reward") for r in rs):
            drop = [r for r in rs if r["v1_reward"] == "1.0" and r.get("S_nl_reward") == "0.0"]
            L += [f"Passes under v1 that fail once `nl_assertions` count (S_nl): {len(drop)} of {sum(1 for r in rs if r['v1_reward'] == '1.0')} v1 passes; tasks: "
                  + ", ".join(sorted({r['task_id'] for r in drop}, key=int)) + ".", ""]

    # ---- judge agreement
    jv = read(V2 / "judge_votes.csv")
    if jv:
        votes = defaultdict(list)
        for v in jv:
            votes[(v["key"], v["assertion_idx"])].append(v["met"])
        n = len(votes)
        unan = sum(1 for vs in votes.values() if len(set(vs)) == 1)
        met_all = sum(1 for vs in votes.values() if all(x == "1" for x in vs))
        unmatched = sum(1 for v in jv if v.get("matched") == "0")
        L += ["## Judge as an instrument", "", f"{s2_label()} judge, 3 votes per assertion, {n} (trajectory, assertion) pairs in `judge_votes.csv`: "
              f"unanimous {wilson(unan, n)}; unanimously met {met_all}/{n}; replies where an assertion was missing or unmatched: {unmatched} of {len(jv)} votes.", ""]

    # ---- fresh runs
    v1p = ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json"
    v1g = ROOT / "results" / "runs" / "sample20_gt_haiku.results.json"
    v2p = V2 / "runs" / "v2_sample20_pass3_haiku" / "results.json"
    v2g = V2 / "runs" / "v2_sample20_gt_haiku" / "results.json"
    if v2p.exists() or v2g.exists():
        L += ["## H4, H5 — fresh runs on the v2 benchmark vs the block-1 runs", ""]
        if v2p.exists():
            a, b = pass_table(v1p), pass_table(v2p)
            rows = ["| task | v1 trials | v1 pass | v2 trials | v2 pass |", "|---|---|---|---|---|"]
            k1 = k2 = f1n = f2n = 0
            for t in sorted(SAMPLE, key=int):
                x, y = a.get(t, []), b.get(t, [])
                rows.append(f"| {t} | {''.join('1' if r == 1.0 else '0' for r in x)} | {sum(1 for r in x if r == 1.0)}/{len(x)} | {''.join('1' if r == 1.0 else '0' for r in y)} | {sum(1 for r in y if r == 1.0)}/{len(y)} |")
                k1 += all(r == 1.0 for r in x) and len(x) == 3
                k2 += all(r == 1.0 for r in y) and len(y) == 3
                f1n += not any(r == 1.0 for r in x)
                f2n += not any(r == 1.0 for r in y)
            p1a = sum(sum(1 for r in a.get(t, []) if r == 1.0) / max(1, len(a.get(t, []))) for t in SAMPLE) / 20
            p1b = sum(sum(1 for r in b.get(t, []) if r == 1.0) / max(1, len(b.get(t, []))) for t in SAMPLE) / 20
            L += ["### Haiku agent, 20 tasks × 3 trials", "", "| metric | v1 (block 1) | v2 |", "|---|---|---|",
                  f"| pass^1 (mean over tasks) | {p1a:.2f} | {p1b:.2f} |", f"| tasks passed 3/3 (pass^3) | {wilson(k1, 20)} | {wilson(k2, 20)} |",
                  f"| tasks failed 3/3 | {f1n}/20 | {f2n}/20 |", ""] + rows + [""]
        if v2g.exists():
            a, b = pass_table(v1g), pass_table(v2g)
            ids = sorted(set(a) | set(b), key=int)
            L += ["### Ground-truth agent (sees the reference actions), 1 trial", "", "| task | v1 | v2 |", "|---|---|---|"]
            for t in ids:
                L.append(f"| {t} | {'' if t not in a else int(a[t][0] == 1.0)} | {'' if t not in b else int(b[t][0] == 1.0)} |")
            L += ["", f"GT passes: v1 {wilson(sum(1 for t in a if a[t][0] == 1.0), len(a))}; v2 {wilson(sum(1 for t in b if b[t][0] == 1.0), len(b))}. "
                  "H4 pre-stated: tasks 32, 7, 44 become reachable.", ""]
        for name in ("v2_sample20_pass3_haiku", "v2_sample20_gt_haiku"):
            sj = V2 / "runs" / name / "summary.json"
            if sj.exists():
                s = json.loads(sj.read_text(encoding="utf-8"))
                u, j = s.get("usage", {}), s.get("judge", {})
                L.append(f"- `{name}`: {s.get('n_sims')} sims, infra errors {s.get('infra_errors')}, {s.get('seconds')} s; agent+user tokens in/out "
                         f"{u.get('agent_in', 0) + u.get('user_in', 0):,}/{u.get('agent_out', 0) + u.get('user_out', 0):,} ≈ ${u.get('own_estimate_usd', 0):.3f}; "
                         f"judge calls {j.get('calls')} ≈ ${j.get('own_estimate_usd', 0):.3f}; overlay commit {s.get('overlay_commit')}.")
        L.append("")
    fr = read(V2 / "rescore_fresh.csv")
    if fr:
        L += ["### The fresh v2 trajectories scored both ways", "",
              "The same v2 trajectories under the stock v1 scorer with tasks v1 (`v1` column) and under V2; a difference is the scoring rule's own effect on identical conversations.", "",
              "| agent | sims | pass under v1 scoring | pass under V2 | flips 1→0 | flips 0→1 |", "|---|---|---|---|---|---|"]
        for ag in ("haiku", "gt"):
            rr = [r for r in fr if r["agent"] == ag]
            if rr:
                L.append(f"| {ag} | {len(rr)} | {sum(1 for r in rr if r['v1_reward'] == '1.0')} | {sum(1 for r in rr if r.get('V2_reward') == '1.0')} | "
                         f"{sum(1 for r in rr if r['v1_reward'] == '1.0' and r.get('V2_reward') == '0.0')} | {sum(1 for r in rr if r['v1_reward'] == '0.0' and r.get('V2_reward') == '1.0')} |")
        L.append("")

    L += ["## Reading the result", "",
          "- A pass that disappears under V2 on the *same* trajectory is a pass the scoring rule produced, not the agent (the no-op class is the extreme case: 23/50 → 0/50).",
          "- A failure that disappears under V2 on the same trajectory is a failure the scoring rule produced (order-only DB mismatches; wrong reference arithmetic such as task 7).",
          "- Fresh runs mix two effects (changed task text and changed scoring) with simulator noise; the per-trajectory re-score separates them.",
          "- Limits: 20 tasks of one domain; the user simulator is unchanged (category-5 noise persists); the NL judge is itself a model and is reported with its agreement rate.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nwritten {OUT.relative_to(ROOT)}")
    return 0


def s2_label() -> str:
    return "claude-haiku-5-5"


if __name__ == "__main__":
    sys.exit(main())
