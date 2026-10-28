"""Build the hand-check sample of judge verdicts (design review C2/9) and score the readers' labels.

Selection from results/v2/rescore.csv (V2 configuration, tasks v2) and block2/nl_assertion_classes.csv:
  * every verdict that changes a reward: assertions judged unmet in a simulation whose DB and communicate
    parts pass (the NL part alone decides), and every assertion of the simulations that flip v1 -> V2;
  * every process-class and every communication-class verdict in the sampled tasks;
  * random fill (seed 20261027) up to at least 20 items.
Each item gets the judge-visible transcript (the with_tool_calls view) and the assertion; the judge's verdict
is written to a separate answer key so that readers label blind.

  --build   -> block2/handcheck/items.md (transcripts), items.csv (blank labels), key.csv (judge verdicts)
  --score   -> reads labels_a.csv (first model reader) and labels_b.csv (blind second model reader), writes block2/judge_handcheck.md
Run --build from inside tau2-bench; --score needs only Python 3.11.
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
HC = ROOT / "block2" / "handcheck"
SAMPLE = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"]


def build() -> int:
    import scorer_v2 as s2
    import tasks_v2
    from tau2.data_model.simulation import Results

    classes = {(r["task_id"], int(r["idx"])): r["class"] for r in csv.DictReader(open(ROOT / "block2" / "nl_assertion_classes.csv", encoding="utf-8"))}
    rs = list(csv.DictReader(open(V2 / "rescore.csv", encoding="utf-8")))
    t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}
    sims = {}
    for agent, fn in (("haiku", "sample20_pass3_haiku.results.json"), ("gt", "sample20_gt_haiku.results.json")):
        for sim in Results.load(ROOT / "results" / "runs" / fn).simulations:
            sims[(agent, sim.task_id, str(sim.trial))] = sim
    items, reasons = {}, {}

    def add(key, why):
        items.setdefault(key, set()).add(why)

    for r in rs:
        det = json.loads(r["V2_nl_detail"]) if r.get("V2_nl_detail") else []
        base_pass = r.get("V2_db") == "1" and r.get("V2_comm") in ("1", "", None)
        flip = r["v1_reward"] != r.get("V2_reward")
        for d in det:
            k = (r["agent"], r["task_id"], r["trial"], d["i"])
            cls = classes.get((r["task_id"], d["i"]), "")
            if flip:
                add(k, "flip")
            if base_pass and d["met"] is not True:
                add(k, "reward-changing")
            if cls == "process":
                add(k, "process")
            if cls == "communication":
                add(k, "communication")
    pool = [(r["agent"], r["task_id"], r["trial"], d["i"]) for r in rs for d in (json.loads(r["V2_nl_detail"]) if r.get("V2_nl_detail") else []) if (r["agent"], r["task_id"], r["trial"], d["i"]) not in items]
    rng = random.Random(20261027)
    while len(items) < 24 and pool:
        k = pool.pop(rng.randrange(len(pool)))
        add(k, "random")
    HC.mkdir(parents=True, exist_ok=True)
    keyed = sorted(items, key=lambda k: (k[0], int(k[1]), int(k[2]), k[3]))
    md = ["# Hand-check items: judge verdicts under V2 (blind labelling)", "",
          "For each item: the transcript exactly as the judge saw it, then ONE assertion. Label `met` / `unmet` / `cannot_tell` in labels_*.csv. "
          "The judge's verdicts are in key.csv — do not open it before labelling.", ""]
    rows, key = [], []
    per_sim: dict[tuple, list] = {}
    for n, (agent, tid, trial, i) in enumerate(keyed, 1):
        sim = sims[(agent, tid, trial)]
        asserts = t2[tid].evaluation_criteria.nl_assertions
        det = {d["i"]: d for d in json.loads(next(r for r in rs if (r["agent"], r["task_id"], r["trial"]) == (agent, tid, trial))["V2_nl_detail"])}
        per_sim.setdefault((agent, tid, trial), []).append((n, i, asserts[i]))
        rows.append({"item": n, "agent": agent, "task_id": tid, "trial": trial, "assertion_idx": i, "class": classes.get((tid, i), ""), "why": "+".join(sorted(items[(agent, tid, trial, i)])), "label": "", "note": ""})
        key.append({"item": n, "judge_met": det[i]["met"], "votes_met": det[i]["vm"], "votes_unmet": det[i]["vu"], "rule": det[i]["rule"]})
    # one file per simulation: the judge-visible transcript (tool results shortened to 300 chars) and that simulation's items
    (HC / "sims").mkdir(exist_ok=True)
    for (agent, tid, trial), its in per_sim.items():
        full = s2.trajectory_text(sims[(agent, tid, trial)].messages)
        compact = [(ln[:300] + " …[truncated]") if ln.startswith("tool result:") and len(ln) > 300 else ln for ln in full.split("\n")]
        body = [f"# {agent} task {tid} trial {trial}", "", "Transcript as the judge saw it (tool results shortened to 300 characters):", "", "```", "\n".join(compact), "```", "", "## Items to label", ""]
        body += [f"- item {n}: (assertion {i + 1}) {a}" for n, i, a in its]
        (HC / "sims" / f"{agent}_{tid}_t{trial}.md").write_text("\n".join(body), encoding="utf-8")
        md.append(f"- {agent} task {tid} trial {trial}: items {', '.join(str(n) for n, _, _ in its)} -> sims/{agent}_{tid}_t{trial}.md")
    (HC / "items.md").write_text("\n".join(md), encoding="utf-8")
    for name, data in (("items.csv", rows), ("key.csv", key)):
        with open(HC / name, "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f"{len(rows)} items -> {HC.relative_to(ROOT)}/items.md, items.csv, key.csv; reasons {Counter(w for r in rows for w in r['why'].split('+'))}")
    return 0


def score() -> int:
    items = {r["item"]: r for r in csv.DictReader(open(HC / "items.csv", encoding="utf-8"))}
    key = {r["item"]: r for r in csv.DictReader(open(HC / "key.csv", encoding="utf-8"))}
    la = {r["item"]: r for r in csv.DictReader(open(HC / "labels_a.csv", encoding="utf-8"))}
    lb = {r["item"]: r for r in csv.DictReader(open(HC / "labels_b.csv", encoding="utf-8"))}
    n = len(items)
    jm = lambda k: "met" if key[k]["judge_met"] == "True" else "unmet"
    agree_ab = sum(1 for k in items if la[k]["label"] == lb[k]["label"])
    agree_aj = sum(1 for k in items if la[k]["label"] == jm(k))
    agree_bj = sum(1 for k in items if lb[k]["label"] == jm(k))
    both_vs_j = sum(1 for k in items if la[k]["label"] == lb[k]["label"] == jm(k))
    L = ["# Hand-check of judge verdicts (V2, recorded simulations)", "",
         f"{n} items selected by `scripts/v2/judge_handcheck.py` (reasons: {dict(Counter(w for r in items.values() for w in r['why'].split('+')))}). "
         "Reader A = the first model reader; reader B = a blind second model reader (Opus), both labelled from the judge-visible transcript without seeing the judge's verdict.", "",
         "| comparison | agreement |", "|---|---|", f"| A vs B | {agree_ab}/{n} |", f"| A vs judge | {agree_aj}/{n} |", f"| B vs judge | {agree_bj}/{n} |", f"| A = B = judge | {both_vs_j}/{n} |", "",
         "| item | agent | task | trial | assertion | class | why | judge | A | B | notes |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in items.items():
        L.append(f"| {k} | {r['agent']} | {r['task_id']} | {r['trial']} | {r['assertion_idx']} | {r['class']} | {r['why']} | {jm(k)} ({key[k]['votes_met']}-{key[k]['votes_unmet']}) | {la[k]['label']} | {lb[k]['label']} | {(la[k].get('note') or '')[:80]} {('/ B: ' + lb[k]['note'][:80]) if lb[k].get('note') else ''} |")
    dis = [k for k in items if la[k]["label"] == lb[k]["label"] and la[k]["label"] != jm(k)]
    L += ["", f"Items where both readers disagree with the judge: {', '.join(dis) or 'none'}.", ""]
    (ROOT / "block2" / "judge_handcheck.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    sys.exit(build() if a.build else score() if a.score else 1)
