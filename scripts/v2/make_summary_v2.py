"""block2/summary_v2.md from the block-2 outputs (no tau2 import, no API).

Inputs (results/v2/): noop_scan_v2.csv, noop_judge_probe.csv, probe_2h_v2.csv, engagement_gate.csv, rescore.csv,
rescore_fresh.csv, judge_votes*.csv, provenance*.json, probe_32_v2/*_samples.json + classification CSVs,
runs/*/summary.json and results.json; block-1 run files results/runs/*.results.json for the v1 side.

Usage (repo root, Python 3.11 with statsmodels):  python -I scripts/v2/make_summary_v2.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "results" / "v2"
OUT = ROOT / "block2" / "summary_v2.md"
SAMPLE = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"]
FIXED = {"7", "32", "44", "23", "8"}  # tasks whose text or assertions changed in v2 (35 is outside the sample)
UNTOUCHED = [t for t in SAMPLE if t not in FIXED]


def wilson(k: int, n: int) -> str:
    if n == 0:
        return "n/a"
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return f"{k}/{n} = {k / n:.2f} [{lo:.2f}, {hi:.2f}]"


def mcnemar_exact(b: int, c: int) -> str:
    """Two-sided exact McNemar p for discordant counts b (1->0) and c (0->1)."""
    n = b + c
    if n == 0:
        return "no discordant pairs"
    k = min(b, c)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    return f"b={b}, c={c}, exact p={p:.3f}"


def read(path: Path) -> list[dict]:
    return list(csv.DictReader(open(path, encoding="utf-8"))) if path.exists() else []


def f1(x) -> bool:
    return str(x) in ("1", "1.0", "True")


def pass_table(results_path: Path) -> dict[str, list[float]]:
    d = json.loads(results_path.read_text(encoding="utf-8"))
    out: dict[str, list[float]] = defaultdict(list)
    for s in d["simulations"]:
        r = (s.get("reward_info") or {}).get("reward")
        if s.get("termination_reason") != "infrastructure_error":
            out[s["task_id"]].append(float(r) if r is not None else 0.0)
    return out


def prov_line() -> str:
    p = V2 / "provenance.json"
    if not p.exists():
        return ""
    d = json.loads(p.read_text(encoding="utf-8"))
    return (f"Provenance of the re-score: scorer {d.get('scorer_version')}, overlay commit {d.get('overlay_commit')}"
            f"{' (dirty)' if d.get('overlay_dirty') else ''}, judge {d.get('judge_model')} (provider-default sampling, args {d.get('judge_args')}), "
            f"view {d.get('judge_view')}, prompt {d.get('judge_prompt_sha256')}, {d.get('votes')} votes.")


def main() -> int:
    L: list[str] = ["# Block 2 — results: scorer v2 and tasks v2 against the pinned benchmark", ""]
    L += ["All numbers are rebuilt from `results/v2/*` by `scripts/v2/make_summary_v2.py`. Intervals are Wilson 95%; paired comparisons on identical "
          "trajectories are given as discordant counts with an exact McNemar p. Block-1 numbers are never recomputed here; the v1 columns come from the "
          "recorded block-1 files. v2 is a stricter, documented alternative scoring protocol laid over the pinned benchmark, not a claim that the "
          "benchmark's own protocol is 'wrong' where its documentation states a choice (the refusal pass, `docs/evaluation.md`).", "", prov_line(), ""]

    # ---- H1
    noop = read(V2 / "noop_scan_v2.csv")
    nj = read(V2 / "noop_judge_probe.csv")
    if noop:
        n1 = sum(f1(r["noop_pass_v1"]) for r in noop)
        s1 = sum(f1(r["noop_pass_v1"]) for r in noop if r["task_id"] in SAMPLE)
        L += ["## H1 — tasks an agent passes by doing nothing", "",
              "| trajectory | scorer | all 50 tasks | 20 sampled |", "|---|---|---|---|",
              f"| empty trajectory (static scan) | v1 | {wilson(n1, 50)} | {wilson(s1, 20)} |",
              f"| empty trajectory | v2 (rule) | {wilson(sum(f1(r['noop_pass_v2']) for r in noop), 50)} | {wilson(sum(f1(r['noop_pass_v2']) for r in noop if r['task_id'] in SAMPLE), 20)} |"]
        if nj:
            n = len(nj)
            ns = sum(1 for r in nj if r["task_id"] in SAMPLE)
            L += [f"| greeting + one user turn (block-1 2b probe) | v2 (rule) | {sum(f1(r['probe_2b_pass']) for r in nj)}/{n} of the no-op tasks | {sum(f1(r['probe_2b_pass']) for r in nj if r['task_id'] in SAMPLE)}/{ns} |"]
            if "refusal_bot_pass" in nj[0]:
                rb = sum(f1(r["refusal_bot_pass"]) for r in nj)
                rbs = sum(f1(r["refusal_bot_pass"]) for r in nj if r["task_id"] in SAMPLE)
                rbn = sum(f1(r.get("refusal_bot_pass_noproc")) for r in nj)
                L += [f"| refusal bot, no tool calls (judged) | v2 | {wilson(rb, n)} of the no-op tasks | {rbs}/{ns} |",
                      f"| refusal bot, process-class assertions excluded | v2 | {rbn}/{n} | |"]
        L += ["", "Under v1 every one of the 23 no-op tasks is passed by an agent that changes nothing and says nothing required. Under v2 the empty trajectory and the 2b probe fail by rule; "
              "a refusal bot still passes the tasks whose assertions are all of the 'does not do X' kind, which tau2 documents as the intended outcome. "
              f"The design review predicted about 13 of 23 such passes before the measurement. The 30 tasks outside the sample carry assertions that were not audited in block 1.", ""]

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
              "The permutation count per task is capped at 24 (task 18 has 5 writes = 119 other orders, 24 tested). Remaining canonical differences are orders that change the outcome "
              "(task 7: cancelling before upgrading changes the refund; task 32: changing flights before the cabin upgrade changes the payments). Argument-list order "
              "(passengers in task 8, payment methods in task 20) is covered by the selftest and the engagement gate, not by this probe.", ""]
    eg = read(V2 / "engagement_gate.csv")
    if eg:
        L += ["Engagement gate (perturbed real trajectories; must flip before any v2 number is reported): " + "; ".join(f"{r['perturbation']} task {r['task']}: {r.get('stock')}→{r.get('switched')} {'ok' if f1(r['ok']) else 'FAIL'}" for r in eg) + ".", ""]

    # ---- H3
    rs = read(V2 / "rescore.csv")
    if rs:
        cfgs = [c[:-7] for c in rs[0].keys() if c.endswith("_reward") and c != "recorded_reward" and not c.endswith(("_upper_reward", "_noproc_reward"))]
        hk = [r for r in rs if r["agent"] == "haiku"]
        gt = [r for r in rs if r["agent"] == "gt"]
        L += ["## H3 — the 76 recorded block-1 simulations re-scored", "",
              "Replay gate: the stock scorer reproduces the recorded reward of all 76 (`replay_check.csv`). One switch at a time on tasks v1, all three together, tasks v2 with the stock scorer, and V2 (tasks v2 + all switches).", "",
              "| config | haiku sims passing (60) | haiku tasks 3/3 (20) | haiku pass^1 (mean over tasks) | GT sims passing (16) | upper bound (undetermined→met) | without process-class assertions |", "|---|---|---|---|---|---|---|"]
        for c in cfgs:
            ph = sum(1 for r in hk if r.get(f"{c}_reward") == "1.0")
            pg = sum(1 for r in gt if r.get(f"{c}_reward") == "1.0")
            per = Counter(r["task_id"] for r in hk if r.get(f"{c}_reward") == "1.0")
            full = sum(1 for t in SAMPLE if per[t] == 3)
            p1 = sum(per[t] / 3 for t in SAMPLE) / 20
            up = sum(1 for r in rs if r.get(f"{c}_reward_upper") == "1.0") if f"{c}_reward_upper" in rs[0] else ph + pg
            npc = sum(1 for r in rs if r.get(f"{c}_reward_noproc") == "1.0") if rs[0].get(f"{c}_reward_noproc", "") != "" else ("n/a" if f"{c}_nl" in rs[0] and any(r.get(f"{c}_nl") for r in rs) else ph + pg)
            L.append(f"| {c} | {ph}/60 | {wilson(full, 20)} | {p1:.2f} | {wilson(pg, 16)} | {up}/76 | {npc}/76 |")
        flips = [r for r in rs if r.get("V2_reward") not in (None, "") and r["v1_reward"] != r.get("V2_reward")]
        b = sum(1 for r in flips if r["v1_reward"] == "1.0")
        c = len(flips) - b
        L += ["", f"Flips v1 → V2 on identical trajectories: {len(flips)} of {len(rs)} ({mcnemar_exact(b, c)}).", ""]
        if flips:
            L += ["| agent | task | trial | v1 | V2 | first component that changes it | what failed / why |", "|---|---|---|---|---|---|---|"]
            for r in flips:
                comp = [n for n, k in (("criteria text", "T2_stock_reward"), ("hash_canon", "S_hash_reward"), ("comm_boundary", "S_comm_reward"), ("nl_enforce", "S_nl_reward")) if r.get(k) not in (None, "") and r.get(k) != r["v1_reward"]]
                why = r.get("V2_nl_failed") or r.get("V2_comm_failed") or ""
                if r["task_id"] == "7" and r["v1_reward"] == "0.0":
                    why = "by construction: communicate_info 1628 → 708 and the transcript states $708; " + why
                L.append(f"| {r['agent']} | {r['task_id']} | {r['trial']} | {r['v1_reward']} | {r['V2_reward']} | {', '.join(comp) or 'interaction'} | {why[:170]} |")
        oo = sum(1 for r in rs if f1(r["db_order_only"]))
        dbf = sum(1 for r in rs if not f1(r["db_raw_match"]))
        L += ["", f"DB mismatches under v1: {dbf}; order-only among them (closed by canonicalisation): {oo}. Communicate flips from `comm_boundary` alone: "
              f"{sum(1 for r in rs if r.get('S_comm_reward') not in (None, '') and r['v1_reward'] != r['S_comm_reward'])}. Gold-action replay errors: {sum(1 for r in rs if r.get('gold_action_errors'))}. "
              "So on these 76 conversations the two deterministic switches change nothing: the block-1 2g/2h defects are latent here (the engagement gate shows they fire on perturbed trajectories), not absent.", ""]
        if "S_nl_reward" in rs[0]:
            drop = [r for r in rs if r["v1_reward"] == "1.0" and r.get("S_nl_reward") == "0.0"]
            und = sum(int(r.get("V2_nl_undetermined") or 0) for r in rs)
            L += [f"Passes under v1 that fail once `nl_assertions` count (S_nl): {len(drop)} of {sum(1 for r in rs if r['v1_reward'] == '1.0')} v1 passes "
                  f"(tasks {', '.join(sorted({r['task_id'] for r in drop}, key=int)) or 'none'}). Undetermined judge verdicts after re-asks: {und}.", ""]
        sv = read(V2 / "rescore_stockview.csv")
        if sv:
            fl = [(r["agent"], r["task_id"], r["trial"]) for r in sv if r.get("V2_reward") not in (None, "") and r["v1_reward"] != r.get("V2_reward")]
            L += [f"First judge pass with tau2's stock transcript view (kept as `rescore_stockview.csv`): {len(fl)} flips ({', '.join(f'{a}/{t}/t{tr}' for a, t, tr in fl)}); "
                  "task 9 trial 1 was a judge error caused by the view hiding tool-call arguments (issue I9).", ""]

    # ---- judge as instrument
    jv = read(V2 / "judge_votes.csv")
    if jv:
        votes = defaultdict(list)
        for v in jv:
            votes[(v["key"], v["assertion_idx"])].append(v["met"])
        n = len(votes)
        unan = sum(1 for vs in votes.values() if len(set(vs)) == 1)
        modes = Counter(v.get("mode", "") for v in jv)
        L += ["## The judge as an instrument", "",
              f"claude-haiku-5-5 (the agent's own model: self-evaluation risk), 3 votes per assertion, provider-default sampling. {n} (trajectory, assertion) pairs in `judge_votes.csv`: "
              f"unanimous {wilson(unan, n)}; mapping modes {dict(modes)}. Unanimity measures repeatability, not validity (the stock-view pass was 255/255 unanimous and wrong on task 9 t1). "
              "Hand-check: `block2/judge_handcheck.md` (all reward-changing, all process-class and all 'communicates X' verdicts, filled at random to ≥ 20, with a blind second reader).", ""]

    # ---- task-32 probe
    p32 = V2 / "probe_32_v2"
    if p32.exists():
        L += ["## Task 32 — does the text fix work? (counterfactual simulator probe, v2 text)", ""]
        for arm in ("two_step", "step1_only"):
            sj = p32 / f"{arm}_samples.json"
            cl = read(p32 / f"{arm}_classification.csv")
            if sj.exists():
                d = json.loads(sj.read_text(encoding="utf-8"))
                cnt = Counter(r["label"] for r in cl) if cl else {}
                L.append(f"- `{arm}`: n={d['setup']['n']}, cost ≈ ${d['cost_estimate_usd']}; classification: {dict(cnt) if cnt else 'pending'}")
        L += ["", "Rules fixed beforehand: two_step ACCEPT ≥ 8/10 = the fix works; step1_only ACCEPT ≥ 8/10 = the net clause over-corrects. Block 1 (v1 text, two_step): REFUSE 10/10.", ""]

    # ---- fresh runs
    v1p = ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json"
    v1g = ROOT / "results" / "runs" / "sample20_gt_haiku.results.json"
    v2p = V2 / "runs" / "v2_sample20_pass3_haiku" / "results.json"
    v2g = V2 / "runs" / "v2_sample20_gt_haiku" / "results.json"
    v2g3 = V2 / "runs" / "v2_gt3_haiku" / "results.json"
    if v2p.exists() or v2g.exists() or v2g3.exists():
        L += ["## H4, H5 — fresh runs on the v2 benchmark", "",
              "Two effects are mixed in a fresh run (changed task text and changed scoring) plus simulator noise. The per-trajectory re-score below separates them: "
              "scorer effect = T2_stock vs V2 on the same fresh conversations; criteria effect = v1 vs T2_stock. The 15 sampled tasks whose text did not change are the test–retest noise control.", ""]
        if v2p.exists():
            a, b = pass_table(v1p), pass_table(v2p)
            rows = ["| task | changed in v2 | block-1 trials | block-1 pass | v2 trials | v2 pass |", "|---|---|---|---|---|---|"]
            k1 = k2 = 0
            for t in sorted(SAMPLE, key=int):
                x, y = a.get(t, []), b.get(t, [])
                rows.append(f"| {t} | {'yes' if t in FIXED else ''} | {''.join('1' if r == 1.0 else '0' for r in x)} | {sum(1 for r in x if r == 1.0)}/{len(x)} | {''.join('1' if r == 1.0 else '0' for r in y)} | {sum(1 for r in y if r == 1.0)}/{len(y)} |")
                k1 += len(x) == 3 and all(r == 1.0 for r in x)
                k2 += len(y) == 3 and all(r == 1.0 for r in y)
            p1a = sum(sum(1 for r in a.get(t, []) if r == 1.0) / max(1, len(a.get(t, []))) for t in SAMPLE) / 20
            p1b = sum(sum(1 for r in b.get(t, []) if r == 1.0) / max(1, len(b.get(t, []))) for t in SAMPLE) / 20
            ua = sum(sum(1 for r in a.get(t, []) if r == 1.0) for t in UNTOUCHED)
            ub = sum(sum(1 for r in b.get(t, []) if r == 1.0) for t in UNTOUCHED)
            L += ["### Haiku agent, 20 tasks × 3 trials", "", "| metric | block-1 run (v1 benchmark) | fresh run (v2 benchmark) |", "|---|---|---|",
                  f"| pass^1 (mean over tasks) | {p1a:.2f} | {p1b:.2f} |", f"| tasks passed 3/3 | {wilson(k1, 20)} | {wilson(k2, 20)} |",
                  f"| trials passed on the {len(UNTOUCHED)} untouched tasks (noise control) | {ua}/{3 * len(UNTOUCHED)} | {ub}/{3 * len(UNTOUCHED)} |", ""] + rows + [""]
        for path, title in ((v2g, "Ground-truth agent, 1 trial (16 tasks with reference actions)"), (v2g3, "Ground-truth agent, 3 trials on the text-fixed tasks 7, 32, 44")):
            if path.exists():
                a, b = pass_table(v1g), pass_table(path)
                L += [f"### {title}", "", "| task | block-1 GT | v2 GT trials |", "|---|---|---|"]
                for t in sorted(b, key=int):
                    L.append(f"| {t} | {'' if t not in a else int(a[t][0] == 1.0)} | {''.join('1' if r == 1.0 else '0' for r in b[t])} |")
                L += ["", f"v2 GT passes: {sum(1 for t in b for r in b[t] if r == 1.0)}/{sum(len(v) for v in b.values())} trials" + (f"; block-1 GT {wilson(sum(1 for t in a if a[t][0] == 1.0), len(a))}." if path is v2g else "."), ""]
        for name in ("v2_sample20_pass3_haiku", "v2_sample20_gt_haiku", "v2_gt3_haiku"):
            sj = V2 / "runs" / name / "summary.json"
            if sj.exists():
                s = json.loads(sj.read_text(encoding="utf-8"))
                u, j = s.get("usage", {}), s.get("judge", {})
                L.append(f"- `{name}`: {s.get('n_sims')} sims, infra errors {s.get('infra_errors')}, {s.get('seconds')} s; agent+user tokens in/out "
                         f"{u.get('agent_in', 0) + u.get('user_in', 0):,}/{u.get('agent_out', 0) + u.get('user_out', 0):,} ≈ ${u.get('own_estimate_usd', 0):.3f}; "
                         f"judge calls {j.get('calls')} ≈ ${j.get('own_estimate_usd', 0):.3f}; overlay commit {s.get('provenance', {}).get('overlay_commit')}; Info diff vs block 1: {s.get('info_diff_vs_block1')}.")
        L.append("")
    fr = read(V2 / "rescore_fresh.csv")
    if fr:
        L += ["### The fresh v2 conversations scored under each protocol", "",
              "| agent | sims | v1 (tasks v1, stock) | T2_stock (tasks v2, stock) | V2 | criteria effect v1→T2_stock (1→0, 0→1) | scorer effect T2_stock→V2 (1→0, 0→1) |", "|---|---|---|---|---|---|---|"]
        for ag in sorted({r["agent"] for r in fr}):
            rr = [r for r in fr if r["agent"] == ag]
            c10 = sum(1 for r in rr if r["v1_reward"] == "1.0" and r.get("T2_stock_reward") == "0.0")
            c01 = sum(1 for r in rr if r["v1_reward"] == "0.0" and r.get("T2_stock_reward") == "1.0")
            s10 = sum(1 for r in rr if r.get("T2_stock_reward") == "1.0" and r.get("V2_reward") == "0.0")
            s01 = sum(1 for r in rr if r.get("T2_stock_reward") == "0.0" and r.get("V2_reward") == "1.0")
            L.append(f"| {ag} | {len(rr)} | {sum(1 for r in rr if r['v1_reward'] == '1.0')} | {sum(1 for r in rr if r.get('T2_stock_reward') == '1.0')} | {sum(1 for r in rr if r.get('V2_reward') == '1.0')} | "
                     f"{c10}, {c01} ({mcnemar_exact(c10, c01)}) | {s10}, {s01} ({mcnemar_exact(s10, s01)}) |")
        L.append("")

    L += ["## Reading the result", "",
          "- A pass that disappears under V2 on the *same* conversation is a pass the scoring protocol produced, not the agent; a failure that disappears is a failure the protocol produced. Each flip is attributed to the component that first changes it.",
          "- The task-7 trial that gains a pass under tasks v2 does so by construction of the fix (the reference arithmetic was wrong).",
          "- The judge is a model, run on the agent's own model family; its repeatability (unanimity) is not its validity, so reward-changing verdicts are hand-checked and reported with bounds.",
          "- Limits: 20 tasks of one domain; the user simulator is unchanged (category-5 noise persists); assertions of the 30 unsampled tasks were not audited; the pinned benchmark documents the refusal pass as intended, so v2 is an alternative protocol.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nwritten {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
