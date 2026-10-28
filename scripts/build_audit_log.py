"""Rebuild audit_log.csv from the CSV inputs (one command, no LLM calls).

Inputs (all under results/ unless noted):
  static_scan.csv        mechanical static checks and the empty-trajectory probe (all 50 tasks)
  probe_2h.csv           WRITE-order permutation probe (hash differences only; verdicts in review_2h.csv)
  review_2h.csv          per-task verdicts for check 2h           (task_id,check,defect,severity,evidence,note)
  review_2j.csv          per-task rows for check 2j (substring vs semantic communicate scorer; probe_2j.py)
  review_batch_*.csv     per-task reviewer verdicts for 1d,2g,2k,4a-4e (same columns)
  review_ALL.csv         benchmark-level static rows, task_id = ALL   (same columns)
  review_overrides.csv   rows that replace reviewer rows after skeptic review (same columns)
  haiku_pass.csv         optional: task_id,check,haiku_pass,defect,severity,evidence,note from agent runs (agent_rows.py)
  review_agent.csv       optional: reviewer verdicts on failed/flipped trajectories (4f, 5c, 5d, 1e triage); read last
  skeptic_verdicts.csv   optional: task_id,check,skeptic_ok,note  (results-skeptic review of medium/high rows)
Rest tasks (airline_full/PLAN.md): review_overrides_rest_*.csv (adversarial review of the rest static rows),
  haiku_pass_rest30.csv, review_agent_rest30.csv, review_agent_overrides_rest30.csv; skeptic_verdicts_*rest*.csv.
  Inputs are filtered by task id, so the same file list serves both logs.
Output: audit_log.csv (schema.md), then validate_audit_log.py is run.
  --ids population: all 50 tasks -> airline_full/audit_log.csv (or --out PATH).
  A row identical (all columns but date) to the row already in the output file keeps its date; in population mode the
  root audit_log.csv is a second date source, so the sampled rows keep their block-1 dates.
Usage (from ==Project):  python -I scripts/build_audit_log.py [--ids sample|population] [--out PATH]
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
RES = ROOT / "results"
COLS = ["task_id", "bench_commit", "category", "check", "method", "defect",
        "severity", "evidence", "haiku_pass", "skeptic_ok", "date", "note"]
# method per check id (checklist.md); anything not listed defaults to "static"
METHOD = {"2b": "probe", "2c": "probe", "2d": "probe", "2e": "probe", "2f": "probe", "2h": "probe", "2j": "probe",
          "1e": "agent_run", "1f": "agent_run", "4f": "agent_run",
          "5c": "agent_run", "5d": "agent_run", "5e": "agent_run", "5f": "agent_run"}
TODAY = date.today().isoformat()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def row(task_id, check, defect, severity, evidence, note="", haiku_pass="", commit=""):
    defect = str(int(defect))
    return {
        "task_id": task_id, "bench_commit": commit, "category": check[0], "check": check,
        "method": METHOD.get(check, "static"), "defect": defect,
        "severity": severity.strip().lower() if defect == "1" else "",
        "evidence": evidence.strip().replace("\n", " "), "haiku_pass": haiku_pass,
        "skeptic_ok": "", "date": TODAY, "note": note.strip().replace("\n", " "),
    }


def static_rows(scan: list[dict], sample: set[str], commit: str) -> list[dict]:
    out = []
    for r in scan:
        tid = r["task_id"]
        if tid not in sample:
            continue
        ev = "results/static_scan.csv"
        out.append(row(tid, "1a", r["reward_basis"] != "DB|COMMUNICATE", "high",
                       f"{ev}: reward_basis={r['reward_basis']}", commit=commit))
        out.append(row(tid, "1b", int(r["replay_errors"]) > 0, "high",
                       f"{ev}: replay_errors={r['replay_errors']} {r['replay_error_msgs']}".strip(), commit=commit))
        c1 = bool(r["write_noop_ids"]) or (int(r["n_write"]) > 0 and r["db_changed"] == "0")
        out.append(row(tid, "1c", c1, "high",
                       f"{ev}: n_write={r['n_write']}, db_changed={r['db_changed']}, write_noop_ids={r['write_noop_ids'] or '-'}", commit=commit))
        out.append(row(tid, "2a", r["positive_control"] == "1", "high",
                       f"{ev}: gold_db_hash==init_db_hash is {r['db_changed'] == '0'}, comm_len={r['comm_len']}",
                       note="documented as intended τ-bench scoring (docs/evaluation.md); positive control" if r["positive_control"] == "1" else "",
                       commit=commit))
        out.append(row(tid, "2b", r["noop_pass"] == "1", "high",
                       f"{ev}: EnvironmentEvaluator+CommunicateEvaluator(substring) on an empty trajectory -> reward {r['noop_reward']}",
                       note="in-process probe, same evaluator classes as tau2 run", commit=commit))
        out.append(row(tid, "2i", r["ci_has_comma"] == "1", "medium",
                       f"{ev}: ci_has_comma={r['ci_has_comma']}, comm_len={r['comm_len']}", commit=commit))
        out.append(row(tid, "3d", r["ci_in_user_scenario"] == "1", "medium",
                       f"{ev}: ci_in_user_scenario={r['ci_in_user_scenario']}", commit=commit))
        out.append(row(tid, "3f", r["init_hash_stable"] != "1", "high",
                       f"{ev}: init_hash_stable={r['init_hash_stable']}", commit=commit))
        out.append(row(tid, "5a", r["replay_stable"] != "1", "high",
                       f"{ev}: replay_stable={r['replay_stable']}", commit=commit))
    return out


def reviewer_rows(paths: list[Path], sample: set[str], commit: str) -> list[dict]:
    out = []
    for p in paths:
        for r in read(p):
            tid = r["task_id"].strip()
            if tid != "ALL" and tid not in sample:
                continue
            hp = r.get("haiku_pass", "")
            out.append(row(tid, r["check"].strip(), r["defect"].strip() == "1", r.get("severity", ""),
                           r.get("evidence", ""), r.get("note", ""), haiku_pass=hp, commit=commit))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", choices=("sample", "population"), default="sample")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    pop = a.ids == "population"
    out = Path(a.out) if a.out else ROOT / ("airline_full/audit_log.csv" if pop else "audit_log.csv")
    out = out if out.is_absolute() else ROOT / out
    sample_json = json.loads((ROOT / "sample.json").read_text(encoding="utf-8"))
    sample, commit = set(sample_json["population_ids" if pop else "task_ids"]), sample_json["bench_commit"]
    rows = static_rows(read(RES / "static_scan.csv"), sample, commit)
    rows += reviewer_rows([RES / "review_2h.csv"] + sorted(RES.glob("review_batch_*.csv"))
                          + [RES / "review_2j.csv", RES / "review_ALL.csv", RES / "review_overrides.csv"]
                          + sorted(RES.glob("review_overrides_rest_*.csv"))
                          + [RES / "haiku_pass.csv", RES / "haiku_pass_rest30.csv",
                             RES / "review_agent.csv", RES / "review_agent_overrides.csv",
                             RES / "review_agent_rest30.csv", RES / "review_agent_overrides_rest30.csv",
                             # the consistency pass across parts and blocks is read last, so it settles any row it names
                             RES / "review_overrides_consistency.csv"], sample, commit)
    # skeptic verdicts
    verdicts = {}
    for p in sorted(RES.glob("skeptic_verdicts*.csv")):  # skeptic_verdicts.csv (static phase), skeptic_verdicts_agent.csv (agent runs)
        verdicts.update({(r["task_id"], r["check"]): r for r in read(p)})
    for r in rows:
        v = verdicts.get((r["task_id"], r["check"]))
        if v and r["defect"] == "1":
            ok = v["skeptic_ok"].strip()
            # a skeptic row "should be defect=1" (or, for a blind re-review disagreement, "re-review prevails") on a row
            # that has since been set to defect=1 counts as confirmation; block 1 wrote such rows with skeptic_ok 0,
            # the rest briefs with skeptic_ok empty
            if ok in ("", "0") and v.get("note", "").strip().lower().startswith(("should be defect=1", "re-review prevails")):
                ok = "1"
            r["skeptic_ok"] = ok
            if v.get("note"):
                r["note"] = (r["note"] + "; skeptic: " + v["note"].strip()).strip("; ")
    # duplicates: keep the last occurrence (later files override earlier ones)
    dedup = {}
    for r in rows:
        dedup[(r["task_id"], r["check"])] = r
    # every agent_run row carries the task's haiku_pass (k/n from the 1f row, agent_rows.py)
    hp = {t: r["haiku_pass"] for (t, c), r in dedup.items() if c == "1f" and r["haiku_pass"]}
    for (t, c), r in dedup.items():
        if r["method"] == "agent_run" and not r["haiku_pass"]:
            r["haiku_pass"] = hp.get(t, "")
    rows = sorted(dedup.values(), key=lambda r: (r["task_id"] == "ALL", int(r["task_id"]) if r["task_id"].isdigit() else 0, r["check"]))
    # an unchanged row keeps the date it was first logged with
    prev = {}
    for p in ([ROOT / "audit_log.csv"] if pop else []) + [out]:
        prev.update({(r["task_id"], r["check"]): r for r in read(p)})
    for r in rows:
        o = prev.get((r["task_id"], r["check"]))
        if o and all(o.get(c, "") == r[c] for c in COLS if c != "date"):
            r["date"] = o["date"]
    with open(out, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    n_def = sum(r["defect"] == "1" for r in rows)
    by_sev = {s: sum(1 for r in rows if r["defect"] == "1" and r["severity"] == s) for s in ("high", "medium", "low")}
    tasks_def = sorted({r["task_id"] for r in rows if r["defect"] == "1" and r["severity"] in ("high", "medium") and r["task_id"] != "ALL"}, key=int)
    tasks_head = [t for t in tasks_def if any(r["task_id"] == t and r["defect"] == "1" and r["severity"] in ("high", "medium") and r["check"] not in ("2a", "2b") for r in rows)]  # headline: the no-op class is reported separately
    print(f"{out.relative_to(ROOT).as_posix()}: {len(rows)} rows; defect=1 rows: {n_def} {by_sev}; "
          f"defective tasks without the no-op class (2a, 2b): {len(tasks_head)}/{len(sample)}; counting it: {len(tasks_def)}/{len(sample)} -> {tasks_def}")
    return subprocess.call([sys.executable, "-I", str(Path(__file__).resolve().parent / "validate_audit_log.py"), str(out)])


if __name__ == "__main__":
    sys.exit(main())
