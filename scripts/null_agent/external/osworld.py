"""Refusal-agent floor of OSWorld-Verified, counted from the task definitions (no VM, nothing executed).

DesktopEnv.evaluate() (desktop_env/desktop_env.py) returns 1 on a task whose evaluator func is "infeasible" when the last
action is FAIL, and 0 on every other task when the last action is FAIL. An agent that emits FAIL at step 0 therefore
scores (number of infeasible tasks) / (number of tasks) by construction. This script counts those tasks per index file
(test_all.json = 369-task Verified set, test_nogdrive.json = the set without Google Drive tasks, test_infeasible.json)
for one or more checkouts of evaluation_examples/, and lists tasks whose infeasible status differs between checkouts.

Usage (any Python 3.10+, isolated mode; reads JSON only):
  python -I osworld.py --checkout HEAD=<repo>/evaluation_examples --checkout 2025-07-29=<old>/evaluation_examples
"""

from __future__ import annotations

import argparse
import json
import math
import os


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def funcs(ev: dict) -> list:
    f = ev.get("func")
    return f if isinstance(f, list) else [f]


def scan(base: str) -> dict:
    out = {"index": {}, "infeasible": set(), "func": {}}
    for idx in ["test_all", "test_nogdrive", "test_infeasible"]:
        p = os.path.join(base, idx + ".json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        out["index"][idx] = [(dom, t) for dom, ts in d.items() for t in ts]
    for dom, t in out["index"]["test_all"]:
        with open(os.path.join(base, "examples", dom, t + ".json"), encoding="utf-8") as f:
            e = json.load(f)
        fl = funcs(e["evaluator"])
        out["func"][(dom, t)] = fl
        if "infeasible" in fl:
            out["infeasible"].add((dom, t))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", action="append", required=True, help="label=path to evaluation_examples")
    a = ap.parse_args()
    res = {}
    for spec in a.checkout:
        label, path = spec.split("=", 1)
        r = scan(path)
        res[label] = r
        print(f"== {label}: {path}")
        for idx, items in r["index"].items():
            n = len(items)
            k = sum(1 for x in items if x in r["infeasible"]) if idx != "test_infeasible" else None
            if idx == "test_infeasible":
                inf_eval = sum(1 for x in items if x in r["infeasible"])
                print(f"  {idx}: {n} listed, of which {inf_eval} have evaluator func 'infeasible' in test_all")
            else:
                lo, hi = wilson(k, n)
                by = {}
                for dom, t in items:
                    if (dom, t) in r["infeasible"]:
                        by[dom] = by.get(dom, 0) + 1
                print(f"  {idx}: {k}/{n} = {100 * k / n:.1f}% [Wilson 95% {100 * lo:.1f}-{100 * hi:.1f}] by domain {by}")
        if "test_infeasible" in r["index"]:
            listed = set(r["index"]["test_infeasible"])
            print(f"  infeasible in test_all but not in test_infeasible.json: {sorted(r['infeasible'] - listed)}")
    labels = list(res)
    for i in range(len(labels) - 1):
        a_, b_ = res[labels[i]], res[labels[i + 1]]
        print(f"== infeasible in {labels[i]} only: {sorted(a_['infeasible'] - b_['infeasible'])}")
        for x in sorted(a_["infeasible"] - b_["infeasible"]):
            print(f"     {x}: {labels[i + 1]} func = {b_['func'].get(x)}")
        print(f"== infeasible in {labels[i + 1]} only: {sorted(b_['infeasible'] - a_['infeasible'])}")
        for x in sorted(b_["infeasible"] - a_["infeasible"]):
            print(f"     {x}: {labels[i]} func = {a_['func'].get(x)}")


if __name__ == "__main__":
    main()
