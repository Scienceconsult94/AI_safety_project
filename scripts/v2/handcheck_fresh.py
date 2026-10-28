"""Blind hand-check of judge-only verdicts in the fresh v2 passes (airline_full/PLAN.md, Q4).

Selection from results/v2/rescore_fresh.csv (V2 configuration) and block2/nl_assertion_classes.csv: every assertion
of class negative or communication, in a simulation whose V2 reward is 1.0, that the judge marked met (the classes
whose only check is the judge). Twenty are drawn with random.Random(20261028): negative first (all of them if fewer
than 10, else 10), communication for the rest. Each item gets the judge-visible transcript (the with_tool_calls view,
as in scripts/v2/judge_handcheck.py) and the assertion; the judge's verdict goes to a separate key so that two
readers label blind.

  --build   -> airline_full/handcheck_fresh/items.md, sims/*.md, items.csv (blank labels), key.csv (judge verdicts)
  --score   -> reads labels_a.csv and labels_b.csv (two blind readers), writes airline_full/judge_handcheck_fresh.md
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
    a = ap.parse_args()
    sys.exit(build() if a.build else score() if a.score else 1)
