"""Probe 2h, second pass: compliant write paths that the first probe (scripts/probe_2h.py) cannot see.

probe_2h.py permutes the reference WRITE calls with their arguments held fixed. Two kinds of path change the arguments
or the number of calls, so they get their own replay here:
  bags_vs_cabin  the task adds checked bags and changes the cabin of the same reservation. The policy sets the free
                 allowance by membership and cabin, so an agent that adds the bags while the old cabin is still in place
                 computes another number of non-free bags (and another charge) than one that adds them after the change.
                 The variant moves the baggage call to the other side of the flights call and recomputes the non-free
                 bags as max(0, total - free allowance x passengers) for the cabin in place at that moment.
  split_call     a reference update_reservation_flights call changes more than one part of the reservation (cabin,
                 outbound flights, return flights). The variant reaches the same flights and cabin in two calls, through
                 every intermediate state that has some of those parts changed and the others not yet.
A differing hash means that path is scored 0. Whether the scenario and the policy allow the path is judged per task
(checklist.md, 2h). No LLM calls. Output: results/probe_2h_paths.csv.
Run from inside tau2-bench:  uv run --no-sync python ../scripts/probe_2h_paths.py
"""

from __future__ import annotations

import copy
import csv
import itertools
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.registry import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
OUT = ROOT / "results" / "probe_2h_paths.csv"
# free checked bags per passenger (policy.md, checked bag allowance)
FREE = {"regular": {"basic_economy": 0, "economy": 1, "business": 2},
        "silver": {"basic_economy": 1, "economy": 2, "business": 3},
        "gold": {"basic_economy": 2, "economy": 3, "business": 4}}


def fresh(env_ctor):
    env = env_ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    return env


def replay(env_ctor, calls):
    """Replay (name, arguments, requestor) calls on a fresh environment; return the environment, its DB hash, errors."""
    env = fresh(env_ctor)
    errors = []
    for name, args, requestor in calls:
        try:
            env.make_tool_call(tool_name=name, requestor=requestor, **copy.deepcopy(args))
        except Exception as e:  # a failed call leaves the DB as it was, as in the evaluator
            errors.append(f"{name}: {e}")
    return env, env.get_db_hash(), errors


def legs(segments, destination):
    """Split (flight_number, date, origin, destination) segments into outbound (up to the arrival at the reservation
    destination) and return."""
    for i, s in enumerate(segments):
        if s[3] == destination:
            return segments[: i + 1], segments[i + 1:]
    return segments, []


def main() -> int:
    env_ctor = registry.get_env_constructor("airline")
    tasks = registry.get_tasks_loader("airline")("base")
    sample = {str(i) for i in json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"]}
    rows = []
    for task in tasks:
        acts = [(a.name, dict(a.arguments), a.requestor)
                for a in ((task.evaluation_criteria.actions or []) if task.evaluation_criteria else [])]
        _, gold, gold_err = replay(env_ctor, acts)
        base = {"task_id": task.id, "set": "sample" if str(task.id) in sample else "rest", "ref_hash": gold[:8]}

        def record(mechanism, variant, calls, detail=""):
            _, h, err = replay(env_ctor, calls)
            rows.append({**base, "mechanism": mechanism, "variant": variant, "variant_hash": h[:8],
                         "hash_differs": int(h != gold), "replay_errors": " | ".join(err)[:300],
                         "reference_replay_errors": len(gold_err), "detail": detail})

        flights_idx = [i for i, a in enumerate(acts) if a[0] == "update_reservation_flights"]
        bags_idx = [i for i, a in enumerate(acts) if a[0] == "update_reservation_baggages"]
        for f in flights_idx:
            rid = acts[f][1]["reservation_id"]
            env_f, _, _ = replay(env_ctor, acts[:f])  # state just before the reference flights call
            db = env_f.tools.db
            res = db.reservations[rid]
            cabin_old, cabin_new = str(res.cabin), str(acts[f][1]["cabin"])
            # bags_vs_cabin
            for b in bags_idx:
                if acts[b][1]["reservation_id"] != rid or cabin_old == cabin_new:
                    continue
                membership, n = str(db.users[res.user_id].membership), len(res.passengers)
                total, nf_ref = acts[b][1]["total_baggages"], acts[b][1]["nonfree_baggages"]
                cab_ref, cab_alt = (cabin_new, cabin_old) if f < b else (cabin_old, cabin_new)
                nf_formula = max(0, total - FREE[membership][cab_ref] * n)
                nf_alt = max(0, total - FREE[membership][cab_alt] * n)
                variant = [x for k, x in enumerate(acts) if k != b]
                args = dict(acts[b][1], nonfree_baggages=nf_alt)
                variant.insert(f, (acts[b][0], args, acts[b][2]))  # before the flights call if f < b, after it if not
                side = "before" if f < b else "after"
                record("bags_vs_cabin", f"bags {side} the cabin change {cabin_old}->{cabin_new}", variant,
                       f"{membership}, {n} passenger(s), {total} bags: non-free {nf_alt} in the variant, "
                       f"{nf_ref} in the reference (policy formula for the reference order: {nf_formula})")
            # split_call
            old = [(x.flight_number, x.date, x.origin, x.destination) for x in res.flights]
            new = [(x["flight_number"], x["date"], str(db.flights[x["flight_number"]].origin),
                    str(db.flights[x["flight_number"]].destination)) for x in acts[f][1]["flights"]]
            out_old, ret_old = legs(old, res.destination)
            out_new, ret_new = legs(new, res.destination)
            parts = {"cabin": (cabin_old, cabin_new), "outbound": (out_old, out_new), "return": (ret_old, ret_new)}
            changed = [p for p, (o, nw) in parts.items()
                       if (o != nw if p == "cabin" else [s[:2] for s in o] != [s[:2] for s in nw])]
            if len(changed) < 2:
                continue
            final = acts[f]
            for r in range(1, len(changed)):
                for first in itertools.combinations(changed, r):
                    pick = {p: parts[p][1] if p in first else parts[p][0] for p in parts}
                    step1 = dict(final[1], cabin=pick["cabin"],
                                 flights=[{"flight_number": s[0], "date": s[1]} for s in pick["outbound"] + pick["return"]])
                    variant = acts[:f] + [(final[0], step1, final[2]), final] + acts[f + 1:]
                    record("split_call", "first call changes " + " + ".join(first) + ", second call the rest", variant,
                           "changed parts: " + ", ".join(changed))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"variants: {len(rows)} on {len({r['task_id'] for r in rows})} tasks; hash differs: "
          f"{sum(r['hash_differs'] for r in rows)}")
    for r in rows:
        err = "y" if r["replay_errors"] else "n"
        print(f"  {r['set']:6} task {r['task_id']:>2} {r['mechanism']:13} differs={r['hash_differs']} err={err} "
              f"| {r['variant']} | {r['detail'][:110]}")
    print(f"written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
