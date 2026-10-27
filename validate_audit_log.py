"""Validate audit_log.csv against schema.md. Pure stdlib; exit 0 when every rule holds."""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COLS = ["task_id", "bench_commit", "category", "check", "method", "defect",
        "severity", "evidence", "haiku_pass", "skeptic_ok", "date", "note"]


def main() -> int:
    sample = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))
    ids = set(sample["population_ids"]) | {"*"}
    commit = sample["bench_commit"]
    created = date.fromisoformat(sample["created"])
    with open(ROOT / "audit_log.csv", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        header = reader.fieldnames or []
        rows = list(reader)
    errs: list[str] = []
    if header != COLS:
        errs.append(f"header mismatch: {header}")
    seen = set()
    for i, r in enumerate(rows, start=2):
        key = (r["task_id"], r["check"])
        if key in seen:
            errs.append(f"line {i}: duplicate (task_id, check) {key}")
        seen.add(key)
        if r["task_id"] not in ids:
            errs.append(f"line {i}: unknown task_id {r['task_id']!r}")
        if r["bench_commit"] != commit:
            errs.append(f"line {i}: bench_commit != sample.json ({r['bench_commit']!r})")
        if r["category"] not in {"1", "2", "3", "4", "5", "6"}:
            errs.append(f"line {i}: category {r['category']!r}")
        if not re.fullmatch(r"[1-6][a-z]\d?", r["check"]):
            errs.append(f"line {i}: check id {r['check']!r} (expected like '2a')")
        if r["check"][:1] != r["category"]:
            errs.append(f"line {i}: check {r['check']!r} not in category {r['category']}")
        if r["method"] not in {"static", "probe", "agent_run"}:
            errs.append(f"line {i}: method {r['method']!r}")
        if r["defect"] not in {"0", "1"}:
            errs.append(f"line {i}: defect {r['defect']!r}")
        if r["defect"] == "1" and r["severity"] not in {"high", "medium", "low"}:
            errs.append(f"line {i}: defect=1 needs severity, got {r['severity']!r}")
        if r["defect"] == "0" and r["severity"] != "":
            errs.append(f"line {i}: defect=0 must have empty severity")
        if r["defect"] == "1" and not r["evidence"].strip():
            errs.append(f"line {i}: defect=1 needs evidence")
        if r["method"] == "agent_run":
            m = re.fullmatch(r"(\d+)/(\d+)", r["haiku_pass"])
            if not m or int(m.group(2)) < 1 or int(m.group(1)) > int(m.group(2)):
                errs.append(f"line {i}: haiku_pass {r['haiku_pass']!r} must be k/n for agent_run")
        elif r["haiku_pass"] != "":
            errs.append(f"line {i}: haiku_pass must be empty unless method=agent_run")
        if r["skeptic_ok"] not in {"", "0", "1"} or (r["skeptic_ok"] and r["defect"] != "1"):
            errs.append(f"line {i}: skeptic_ok {r['skeptic_ok']!r} (only on defect=1 rows)")
        try:
            d = date.fromisoformat(r["date"])
            if not (created <= d <= date.today()):
                errs.append(f"line {i}: date {r['date']} out of range")
        except ValueError:
            errs.append(f"line {i}: bad date {r['date']!r}")
    for e in errs:
        print("ERR", e)
    print(f"audit_log.csv: {len(rows)} rows, {len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
