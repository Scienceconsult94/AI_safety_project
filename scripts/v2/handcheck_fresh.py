"""Blind hand-check of judge-only verdicts in the fresh v2 passes (airline_full/PLAN.md, Q4).

Selection from results/v2/rescore_fresh.csv (V2 configuration) and block2/nl_assertion_classes.csv: every assertion
of class negative or communication, in a simulation whose V2 reward is 1.0, that the judge marked met (the classes
whose only check is the judge). Twenty are drawn with random.Random(20261028): negative first (all of them if fewer
than 10, else 10), communication for the rest. Each item gets the judge-visible transcript (the with_tool_calls view,
as in scripts/v2/judge_handcheck.py) and the assertion; the judge's verdict goes to a separate key so that two
readers label blind.

  --build   -> airline_full/handcheck_fresh/items.md, sims/*.md, items.csv (blank labels), key.csv (judge verdicts)
  --score   -> reads labels_a.csv and labels_b.csv (two blind readers), writes airline_full/judge_handcheck_fresh.md
Round 2 (airline_full/PLAN.md, deviation of 2026-10-28): round 1 was only partially blind, because items.md stated
that the pool was judge-met and items.csv carried the class. `--round 2` re-labels the same 20 items mixed with 10
judge-unmet decoys from the same fresh runs (the 3 communication ones and 7 db_dup ones drawn with the same seed),
shuffled, with no pool statement and no class column; the key records which items are decoys.
  --round 2 --build -> airline_full/handcheck_fresh_r2/ (same layout);  --round 2 --score -> labels_c.csv, labels_d.csv
  -> airline_full/judge_handcheck_fresh_r2.md
Run --build from inside tau2-bench; --score needs only Python 3.11. No model call.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
V2 = ROOT / "results" / "v2"
HC = ROOT / "airline_full" / "handcheck_fresh"
HC2 = ROOT / "airline_full" / "handcheck_fresh_r2"
N_DECOYS = 10
CLASSES = ("negative", "communication")
N_ITEMS, N_NEGATIVE, SEED = 20, 10, 20261028


def build() -> int:
    import scorer_v2 as s2
    import tasks_v2
    from tau2.data_model.simulation import Results

    classes = {(r["task_id"], int(r["idx"])): r["class"] for r in csv.DictReader(open(ROOT / "block2" / "nl_assertion_classes.csv", encoding="utf-8"))}
    rs = list(csv.DictReader(open(V2 / "rescore_fresh.csv", encoding="utf-8")))
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}
    sims, rows_by_sim = {}, {}
    for fn in sorted({r["file"] for r in rs}):
        for sim in Results.load(V2 / "runs" / fn).simulations:
            sims[(fn, sim.task_id, str(sim.trial))] = sim
    pool = {c: [] for c in CLASSES}
    passes = 0
    for r in rs:
        if r.get("V2_reward") not in ("1.0", "1"):
            continue
        passes += 1
        rows_by_sim[(r["file"], r["task_id"], r["trial"])] = r
        for d in json.loads(r["V2_nl_detail"]) if r.get("V2_nl_detail") else []:
            cls = classes.get((r["task_id"], d["i"]), "")
            if cls in CLASSES and d["met"] is True:
                pool[cls].append((r["file"], r["agent"], r["task_id"], r["trial"], d["i"]))
    rng = random.Random(SEED)
    neg = sorted(pool["negative"])
    chosen = neg if len(neg) <= N_NEGATIVE else rng.sample(neg, N_NEGATIVE)
    com = sorted(pool["communication"])
    chosen += rng.sample(com, min(N_ITEMS - len(chosen), len(com)))
    HC.mkdir(parents=True, exist_ok=True)
    (HC / "sims").mkdir(exist_ok=True)
    keyed = sorted(chosen, key=lambda k: (k[1], int(k[2]), int(k[3]), k[4]))
    md = ["# Hand-check items: judge-only verdicts in the fresh v2 passes (blind labelling)", "",
          "For each item: the transcript exactly as the judge saw it, then ONE assertion. Label `met` / `unmet` / `cannot_tell` "
          "in your labels file. The judge's verdicts are in key.csv: do not open it.", "",
          f"Pool: {passes} fresh simulations with V2 reward 1.0; judge-met assertions of class negative {len(pool['negative'])}, "
          f"communication {len(pool['communication'])}; drawn {len(keyed)} with random.Random({SEED}).", ""]
    items, key, per_sim = [], [], {}
    for n, (fn, agent, tid, trial, i) in enumerate(keyed, 1):
        r = rows_by_sim[(fn, tid, trial)]
        det = {d["i"]: d for d in json.loads(r["V2_nl_detail"])}
        asserts = t2[tid].evaluation_criteria.nl_assertions
        per_sim.setdefault((fn, agent, tid, trial), []).append((n, i, asserts[i]))
        items.append({"item": n, "run": fn.split("/")[0], "agent": agent, "task_id": tid, "trial": trial, "assertion_idx": i,
                      "class": classes[(tid, i)], "label": "", "note": ""})
        key.append({"item": n, "judge_met": det[i]["met"], "votes_met": det[i]["vm"], "votes_unmet": det[i]["vu"], "rule": det[i]["rule"]})
    for (fn, agent, tid, trial), its in per_sim.items():
        run = fn.split("/")[0]
        full = s2.trajectory_text(sims[(fn, tid, trial)].messages)
        compact = [(ln[:300] + " …[truncated]") if ln.startswith("tool result:") and len(ln) > 300 else ln for ln in full.split("\n")]
        body = [f"# {run} task {tid} trial {trial}", "", "Transcript as the judge saw it (tool results shortened to 300 characters):", "", "```", "\n".join(compact), "```", "", "## Items to label", ""]
        body += [f"- item {n}: (assertion {i + 1}) {a}" for n, i, a in its]
        (HC / "sims" / f"{run}_{tid}_t{trial}.md").write_text("\n".join(body), encoding="utf-8")
        md.append(f"- {run} task {tid} trial {trial}: items {', '.join(str(n) for n, _, _ in its)} -> sims/{run}_{tid}_t{trial}.md")
    (HC / "items.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for name, data in (("items.csv", items), ("key.csv", key)):
        with open(HC / name, "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f"{len(items)} items ({Counter(r['class'] for r in items)}) from {passes} fresh passes -> {HC.relative_to(ROOT)}")
    return 0


def build_round2() -> int:
    """The 20 round-1 items plus 10 judge-unmet decoys, shuffled; readers see neither the pool nor the class."""
    import scorer_v2 as s2
    import tasks_v2
    from tau2.data_model.simulation import Results

    classes = {(r["task_id"], int(r["idx"])): r["class"] for r in csv.DictReader(open(ROOT / "block2" / "nl_assertion_classes.csv", encoding="utf-8"))}
    rs = list(csv.DictReader(open(V2 / "rescore_fresh.csv", encoding="utf-8")))
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}
    by_sim = {(r["file"].split("/")[0], r["task_id"], r["trial"]): r for r in rs}
    r1 = list(csv.DictReader(open(HC / "items.csv", encoding="utf-8")))
    targets = [(r["run"], r["task_id"], r["trial"], int(r["assertion_idx"])) for r in r1]
    unmet = {"communication": [], "db_dup": []}
    for r in rs:
        for d in json.loads(r["V2_nl_detail"]) if r.get("V2_nl_detail") else []:
            cls = classes.get((r["task_id"], d["i"]), "")
            if d["met"] is False and cls in unmet:
                unmet[cls].append((r["file"].split("/")[0], r["task_id"], r["trial"], d["i"]))
    rng = random.Random(SEED)
    com = sorted(unmet["communication"])
    decoys = com + rng.sample(sorted(unmet["db_dup"]), N_DECOYS - len(com))
    allk = [(k, 1) for k in targets] + [(k, 0) for k in decoys]
    random.Random(SEED + 2).shuffle(allk)
    HC2.mkdir(parents=True, exist_ok=True)
    (HC2 / "sims").mkdir(exist_ok=True)
    sims = {}
    for run in sorted({k[0] for k, _ in allk}):
        for sim in Results.load(V2 / "runs" / run / "results.json").simulations:
            sims[(run, sim.task_id, str(sim.trial))] = sim
    md = ["# Hand-check items (blind labelling)", "",
          "For each item: the transcript exactly as the judge saw it, then ONE assertion about the agent's behaviour. "
          "Label `met` / `unmet` / `cannot_tell` in your labels file. Do not open key.csv.", ""]
    items, key, per_sim = [], [], {}
    for n, ((run, tid, trial, i), is_target) in enumerate(allk, 1):
        det = {d["i"]: d for d in json.loads(by_sim[(run, tid, trial)]["V2_nl_detail"])}
        a = t2[tid].evaluation_criteria.nl_assertions[i]
        per_sim.setdefault((run, tid, trial), []).append((n, i, a))
        items.append({"item": n, "run": run, "task_id": tid, "trial": trial, "assertion_idx": i, "label": "", "note": ""})
        key.append({"item": n, "target": is_target, "class": classes.get((tid, i), ""), "judge_met": det[i]["met"],
                    "votes_met": det[i]["vm"], "votes_unmet": det[i]["vu"], "rule": det[i]["rule"]})
    for (run, tid, trial), its in sorted(per_sim.items(), key=lambda kv: min(n for n, _, _ in kv[1])):
        full = s2.trajectory_text(sims[(run, tid, trial)].messages)
        compact = [(ln[:300] + " …[truncated]") if ln.startswith("tool result:") and len(ln) > 300 else ln for ln in full.split("\n")]
        body = [f"# {run} task {tid} trial {trial}", "", "Transcript as the judge saw it (tool results shortened to 300 characters):", "", "```", "\n".join(compact), "```", "", "## Items to label", ""]
        body += [f"- item {n}: (assertion {i + 1}) {a}" for n, i, a in sorted(its)]
        (HC2 / "sims" / f"{run}_{tid}_t{trial}.md").write_text("\n".join(body), encoding="utf-8")
        md.append(f"- {run} task {tid} trial {trial}: items {', '.join(str(n) for n, _, _ in sorted(its))} -> sims/{run}_{tid}_t{trial}.md")
    (HC2 / "items.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for name, data in (("items.csv", items), ("key.csv", key)):
        with open(HC2 / name, "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f"{len(items)} items ({sum(k['target'] for k in key)} targets, {len(key) - sum(k['target'] for k in key)} decoys) -> {HC2.relative_to(ROOT)}")
    return 0


def score_round2() -> int:
    items = {r["item"]: r for r in csv.DictReader(open(HC2 / "items.csv", encoding="utf-8"))}
    key = {r["item"]: r for r in csv.DictReader(open(HC2 / "key.csv", encoding="utf-8"))}
    lc = {r["item"]: r for r in csv.DictReader(open(HC2 / "labels_c.csv", encoding="utf-8"))}
    ld = {r["item"]: r for r in csv.DictReader(open(HC2 / "labels_d.csv", encoding="utf-8"))}
    jm = lambda k: "met" if key[k]["judge_met"] == "True" else "unmet"  # noqa: E731
    L = ["# Hand-check of judge-only verdicts in the fresh v2 passes, round 2 (blind, with decoys)", "",
         "The 20 round-1 items mixed with 10 judge-unmet decoys from the same fresh runs, shuffled; the readers saw neither "
         "the pool nor the class (`scripts/v2/handcheck_fresh.py --round 2`; airline_full/PLAN.md, Q4 and its deviation). "
         "Readers C and D labelled blind and independently.", "",
         "| items | n | C vs judge | D vs judge | C vs D | C = D = judge |", "|---|---|---|---|---|---|"]
    for name, sel in (("targets (judge-only, judge met)", "1"), ("decoys (judge unmet)", "0")):
        ks = [k for k in items if key[k]["target"] == sel]
        L.append(f"| {name} | {len(ks)} | {sum(lc[k]['label'] == jm(k) for k in ks)}/{len(ks)} | "
                 f"{sum(ld[k]['label'] == jm(k) for k in ks)}/{len(ks)} | {sum(lc[k]['label'] == ld[k]['label'] for k in ks)}/{len(ks)} | "
                 f"{sum(lc[k]['label'] == ld[k]['label'] == jm(k) for k in ks)}/{len(ks)} |")
    L += ["", "| item | target | run | task | trial | assertion | class | judge | C | D | notes |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in items.items():
        L.append(f"| {k} | {key[k]['target']} | {r['run']} | {r['task_id']} | {r['trial']} | {int(r['assertion_idx']) + 1} | {key[k]['class']} | "
                 f"{jm(k)} ({key[k]['votes_met']}-{key[k]['votes_unmet']}) | {lc[k]['label']} | {ld[k]['label']} | "
                 f"C: {(lc[k].get('note') or '')[:90]} / D: {(ld[k].get('note') or '')[:90]} |")
    dis = [k for k in items if lc[k]["label"] == ld[k]["label"] and lc[k]["label"] != jm(k)]
    L += ["", f"Items where both readers disagree with the judge: {', '.join(dis) or 'none'}.", ""]
    (ROOT / "airline_full" / "judge_handcheck_fresh_r2.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:9]))
    return 0


def score() -> int:
    items = {r["item"]: r for r in csv.DictReader(open(HC / "items.csv", encoding="utf-8"))}
    key = {r["item"]: r for r in csv.DictReader(open(HC / "key.csv", encoding="utf-8"))}
    la = {r["item"]: r for r in csv.DictReader(open(HC / "labels_a.csv", encoding="utf-8"))}
    lb = {r["item"]: r for r in csv.DictReader(open(HC / "labels_b.csv", encoding="utf-8"))}
    n = len(items)
    jm = lambda k: "met" if key[k]["judge_met"] == "True" else "unmet"  # noqa: E731
    agree_ab = sum(la[k]["label"] == lb[k]["label"] for k in items)
    agree_aj = sum(la[k]["label"] == jm(k) for k in items)
    agree_bj = sum(lb[k]["label"] == jm(k) for k in items)
    both_j = sum(la[k]["label"] == lb[k]["label"] == jm(k) for k in items)
    L = ["# Hand-check of judge-only verdicts in the fresh v2 passes", "",
         f"{n} items selected by `scripts/v2/handcheck_fresh.py` ({dict(Counter(r['class'] for r in items.values()))}; "
         "airline_full/PLAN.md, Q4). Readers A and B labelled blind and independently from the judge-visible transcript, "
         "without the judge's verdict.", "",
         "| comparison | agreement |", "|---|---|", f"| A vs B | {agree_ab}/{n} |", f"| A vs judge | {agree_aj}/{n} |",
         f"| B vs judge | {agree_bj}/{n} |", f"| A = B = judge | {both_j}/{n} |", "",
         "| item | run | task | trial | assertion | class | judge | A | B | notes |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in items.items():
        L.append(f"| {k} | {r['run']} | {r['task_id']} | {r['trial']} | {int(r['assertion_idx']) + 1} | {r['class']} | {jm(k)} "
                 f"({key[k]['votes_met']}-{key[k]['votes_unmet']}) | {la[k]['label']} | {lb[k]['label']} | "
                 f"A: {(la[k].get('note') or '')[:90]} / B: {(lb[k].get('note') or '')[:90]} |")
    dis = [k for k in items if la[k]["label"] == lb[k]["label"] and la[k]["label"] != jm(k)]
    L += ["", f"Items where both readers disagree with the judge: {', '.join(dis) or 'none'}.", ""]
    (ROOT / "airline_full" / "judge_handcheck_fresh.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--round", type=int, choices=(1, 2), default=1)
    a = ap.parse_args()
    if a.round == 2:
        sys.exit(build_round2() if a.build else score_round2() if a.score else 1)
    sys.exit(build() if a.build else score() if a.score else 1)
