"""Generate block2/tasks_airline_v2.json from the pinned tasks.json and the edits of block2/task_fixes.md.

Every edit is anchored to the exact pinned wording: if an expected substring is missing the
script stops with an error, so a change of the upstream file cannot silently produce a
different v2. Reference actions are never touched. No tau2 import, no model call.

Usage (repo root):  python -I scripts/v2/make_tasks_v2.py [--check]
  --check   only verify that the existing v2 file equals what the edits produce (exit 1 otherwise)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "tau2-bench" / "data" / "tau2" / "domains" / "airline" / "tasks.json"
OUT = ROOT / "block2" / "tasks_airline_v2.json"
BENCH_COMMIT = "989d3285ae669e49503324bdb9981bf14fccedeb"

# (task_id, kind, locator, old, new)
#   kind "replace": substring replacement inside user_scenario.instructions[locator]
#   kind "append":  append a paragraph to user_scenario.instructions[locator] (old must be None)
#   kind "comm":    set evaluation_criteria.communicate_info (old = expected current list)
#   kind "nl":      replace nl_assertions[locator] (old = expected current text)
EDITS = [
    # task 32 — rows 1e, 4c
    ("32", "replace", "task_instructions",
     "You are willing to pay up to $100 for the change.",
     "You are willing to pay up to $100 net for the change. If one step charges more than that but a later "
     "step in the same conversation refunds it so that the net result is within $100 (or a refund to you), "
     "that is acceptable."),
    ("32", "append", "task_instructions", None,
     "Any charge or refund should go to your Visa credit card ending in 1777."),
    # task 7 — row 4f (I6)
    ("7", "replace", "task_instructions",
     "you also want to check if you have any other upcoming flights and ask for what the total cost of those flights is.",
     "you also want to check if you have any other upcoming flights (other than the two reservations you are "
     "cancelling) and ask what the total cost of those other flights is."),
    ("7", "comm", None, ["1628"], ["708"]),
    ("7", "nl", 3,
     "Agent communicates that total cost of upcoming flights is $1,628.",
     "Agent communicates that the total cost of the other upcoming flights (7WPL39 and 3EMQJ6) is $708."),
    # task 44 — rows 4a, 4c, 2k
    ("44", "replace", "reason_for_call",
     "For the flights that are under or equal to 3 hours (including layovers), ask the agent to upgrade you to "
     "business wherever possible.",
     "For the reservations in which every individual flight segment is 3 hours or shorter (judge each flight on "
     "its own; do not add layover time), ask the agent to upgrade you to business wherever possible."),
    ("44", "append", "task_instructions", None,
     "Pay for the upgrades with your Visa credit card ending in 7238."),
    ("44", "comm", None, [], ["1387"]),
    # task 23 — row 4e
    ("23", "nl", 3,
     "Agent books a round-trip reservation from JFK to SFO in business with outbound flights HAT023 and HAT204 on "
     "2024-05-26 and return flight HAT100 on 2024-05-28 for Mohamed Silva.",
     "Agent books a round-trip reservation from JFK to SFO in business with outbound flight HAT023 on 2024-05-26 "
     "and return flights HAT204 and HAT100 on 2024-05-28 for Mohamed Silva."),
    ("23", "nl", 4,
     "For this reservation Agent charges $500 on certificate_3765853, $198 on gift_card_8020792, $129 on "
     "gift_card_6136092\", and $44 on credit_card_2198526.",
     "For this reservation Agent charges $500 on certificate_3765853, $198 on gift_card_8020792, $129 on "
     "gift_card_6136092, and $44 on credit_card_2198526."),
    # assertion typos that contradict the reference, found by the classification pass (block2/nl_assertion_classes.md);
    # prerequisites of nl_enforce like the task-23 rows above
    ("8", "nl", 2, None, None),   # "Sophia Silvia" -> "Sophia Silva" (resolved at run time, see NL_TYPO)
    ("35", "nl", 2, None, None),  # "credit_card_907483" -> "credit_card_9074831"
]
NL_TYPO = {("8", 2): ("Sophia Silvia", "Sophia Silva"), ("35", 2): ("credit_card_907483", "credit_card_9074831")}


def apply_edits(tasks: list[dict]) -> tuple[list[dict], list[str]]:
    by_id = {t["id"]: t for t in tasks}
    out = copy.deepcopy(tasks)
    out_by_id = {t["id"]: t for t in out}
    log = []
    for tid, kind, loc, old, new in EDITS:
        if tid not in by_id:
            raise SystemExit(f"task {tid} not found")
        t = out_by_id[tid]
        if kind in ("replace", "append"):
            ins = t["user_scenario"]["instructions"]
            cur = ins[loc]
            if kind == "replace":
                if cur.count(old) != 1:
                    raise SystemExit(f"task {tid} {loc}: expected exactly one occurrence of {old!r}, found {cur.count(old)}")
                ins[loc] = cur.replace(old, new)
            else:
                ins[loc] = cur.rstrip() + "\n\n" + new
        elif kind == "comm":
            cur = t["evaluation_criteria"]["communicate_info"]
            if cur != old:
                raise SystemExit(f"task {tid} communicate_info: expected {old!r}, found {cur!r}")
            t["evaluation_criteria"]["communicate_info"] = new
        elif kind == "nl":
            cur = t["evaluation_criteria"]["nl_assertions"][loc]
            if old is None:  # typo substitution anchored to the exact wrong token
                wrong, right = NL_TYPO[(tid, loc)]
                if cur.count(wrong) != 1 or right in cur:
                    raise SystemExit(f"task {tid} nl_assertions[{loc}]: expected exactly one {wrong!r}, got {cur!r}")
                new = cur.replace(wrong, right)
            elif cur != old:
                raise SystemExit(f"task {tid} nl_assertions[{loc}]: expected {old!r}, found {cur!r}")
            t["evaluation_criteria"]["nl_assertions"][loc] = new
        else:
            raise SystemExit(kind)
        log.append(f"{tid}:{kind}:{loc}")
    # invariant: reference actions untouched
    for t in out:
        if t["evaluation_criteria"].get("actions") != by_id[t["id"]]["evaluation_criteria"].get("actions"):
            raise SystemExit(f"task {t['id']}: actions changed — not allowed")
    return out, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = SRC.read_bytes()
    src_sha = hashlib.sha256(raw).hexdigest()
    tasks = json.loads(raw.decode("utf-8"))
    v2, log = apply_edits(tasks)
    changed = sorted({e.split(":")[0] for e in log}, key=int)
    text = json.dumps(v2, indent=2, ensure_ascii=False) + "\n"
    meta = {
        "source": "tau2-bench/data/tau2/domains/airline/tasks.json",
        "bench_commit": BENCH_COMMIT,
        "source_sha256": src_sha,
        "tasks_changed": changed,
        "edits": log,
        "v2_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("tasks_airline_v2.json differs from the edits in make_tasks_v2.py")
            return 1
        print("tasks_airline_v2.json is up to date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    (OUT.with_suffix(".meta.json")).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"written {OUT.relative_to(ROOT)}: {len(v2)} tasks, {len(log)} edits in tasks {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
