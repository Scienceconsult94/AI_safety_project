"""Build one Markdown "task card" per airline task for static review and blind re-review.

Each card gathers everything a reviewer needs in one place: task description, the
user-simulator instructions (what the simulated customer knows and wants), the
reference trajectory with arguments, communicate_info / nl_assertions, the DB
records the task touches (user, reservations, flights named in the reference
actions or in known_info), and the static-scan numbers. No LLM calls.
Usage (from ==Project):  python -I extract_tasks.py   -> results/task_cards/task_<id>.md
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "tau2-bench" / "data" / "tau2" / "domains" / "airline"
OUT = ROOT / "results" / "task_cards"


def j(obj) -> str:
    return "```json\n" + json.dumps(obj, ensure_ascii=False, indent=1) + "\n```"


def main() -> None:
    tasks = json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))
    db = json.loads((DATA / "db.json").read_text(encoding="utf-8"))
    scan = {r["task_id"]: r for r in csv.DictReader(open(ROOT / "results" / "static_scan.csv", encoding="utf-8"))}
    sample = set(json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))["task_ids"])
    OUT.mkdir(parents=True, exist_ok=True)

    for t in tasks:
        tid = t["id"]
        ec = t.get("evaluation_criteria") or {}
        us = (t.get("user_scenario") or {}).get("instructions") or {}
        actions = ec.get("actions") or []
        text_blob = " ".join(str(us.get(k, "")) for k in ("task_instructions", "reason_for_call", "known_info", "unknown_info"))
        user_ids, res_ids, flight_nos = set(), set(), set()
        for a in actions:
            args = a.get("arguments") or {}
            if "user_id" in args:
                user_ids.add(args["user_id"])
            if "reservation_id" in args:
                res_ids.add(args["reservation_id"])
            for fl in args.get("flights") or []:
                if isinstance(fl, dict) and fl.get("flight_number"):
                    flight_nos.add(fl["flight_number"])
        user_ids |= {m for m in re.findall(r"\b[a-z]+_[a-z]+_\d{4}\b", text_blob) if m in db["users"]}
        res_ids |= {m for m in re.findall(r"\b[A-Z0-9]{6}\b", text_blob) if m in db["reservations"]}
        for uid in list(user_ids):
            res_ids |= set(db["users"].get(uid, {}).get("reservations") or [])

        s = scan.get(tid, {})
        lines = [
            f"# Airline task {tid}" + ("  (in sample20)" if tid in sample else ""),
            "",
            f"bench_commit: `{s.get('bench_commit', '')}` · reward_basis: {ec.get('reward_basis')}",
            f"static scan: n_actions={s.get('n_actions')} (read={s.get('n_read')}, write={s.get('n_write')}, generic={s.get('n_generic')}), "
            f"db_changed={s.get('db_changed')}, comm_len={s.get('comm_len')}, nl_count={s.get('nl_count')}, **noop_pass={s.get('noop_pass')}**",
            "",
            "## Task description (author annotation, not shown to the agent)",
            j(t.get("description")),
            "",
            "## User-simulator instructions",
            f"**persona:** {(t.get('user_scenario') or {}).get('persona')}",
            "",
            f"**reason_for_call:**\n\n{us.get('reason_for_call', '')}",
            "",
            f"**known_info:**\n\n{us.get('known_info', '')}",
            "",
            f"**unknown_info:**\n\n{us.get('unknown_info', '')}",
            "",
            f"**task_instructions:**\n\n{us.get('task_instructions', '')}",
            "",
            "## Reference trajectory (evaluation_criteria.actions)",
            j(actions),
            "",
            "## communicate_info (substring, case-insensitive, commas stripped)",
            j(ec.get("communicate_info")),
            "",
            "## nl_assertions (diagnostic only, do not gate reward)",
            j(ec.get("nl_assertions")),
            "",
            "## DB records referenced",
        ]
        for uid in sorted(user_ids):
            u = db["users"].get(uid)
            if u:
                slim = {k: u[k] for k in ("user_id", "name", "dob", "membership", "payment_methods", "saved_passengers", "reservations") if k in u}
                lines += [f"### user `{uid}`", j(slim)]
        for rid in sorted(res_ids):
            r = db["reservations"].get(rid)
            if r:
                lines += [f"### reservation `{rid}`", j(r)]
                for fl in r.get("flights") or []:
                    if isinstance(fl, dict) and fl.get("flight_number"):
                        flight_nos.add(fl["flight_number"])
        for fn in sorted(flight_nos):
            f = db["flights"].get(fn)
            if f:
                slim = {k: f[k] for k in ("flight_number", "origin", "destination", "scheduled_departure_time_est", "scheduled_arrival_time_est") if k in f}
                lines += [f"### flight `{fn}` (schedule only; per-date status/prices omitted)", j(slim)]
        (OUT / f"task_{tid}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(tasks)} cards to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
