"""Blind re-review agreement for retail (the retail reading of scripts/rereview_agreement.py).

Inputs (results/retail/):
  rereview_blind.csv       blind second-pass labels (task_id,check,defect,severity,evidence,note), produced without access
                           to the original review files
  review_batch_*.csv, review_overrides.csv   original labels (later files override earlier ones for the same (task_id, check));
                           the comparison uses the ORIGINAL reviewer label (batches), the skeptic-corrected label (overrides) is
                           reported in a separate column
  retail/audit_log.csv     the final label (reviewers + mechanical probe rows + skeptic), third column
Rows the blind reviewer disclosed as not strictly blind (an excerpt of retail/PLAN.md's deviations was seen while looking for
dates; the rows it could have influenced) are flagged `not_blind=1` and every agreement figure is also given without them.
Output: results/retail/rereview.csv and rereview_summary.md.
Sampling of the twelve tasks: random.Random(20261027).sample(retail/sample.json["task_ids"], 12) -> 24, 7, 77, 21, 31, 12, 83, 15, 43, 3, 98, 84.
Usage (from ==Project):  python -I scripts/retail/rereview_agreement.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "retail"


def read(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def labels(paths: list[Path]) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for p in paths:
        for r in read(p):
            out[(r["task_id"].strip(), r["check"].strip())] = r
    return out


def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = (a.count("1") / n) * (b.count("1") / n) + (a.count("0") / n) * (b.count("0") / n)
    return float("nan") if pe >= 1.0 else (po - pe) / (1 - pe)


NOT_BLIND = {("3", "1b"), ("43", "2e")}  # disclosed by the blind reviewer: PLAN.md deviation excerpt seen (1b severity rule, hidden address write)


def main() -> int:
    blind = read(RES / "rereview_blind.csv")
    batches = sorted(RES.glob("review_batch_*.csv"), key=lambda p: int(p.stem.split("_")[-1]))
    original = labels(batches)
    corrected = labels(batches + [RES / "review_overrides.csv"])
    final = labels([ROOT / "retail" / "audit_log.csv"])
    rows = []
    for r in blind:
        key = (r["task_id"].strip(), r["check"].strip())
        o, c, f = original.get(key), corrected.get(key), final.get(key)
        rows.append({"task_id": key[0], "check": key[1], "original_defect": o["defect"].strip() if o else "", "corrected_defect": c["defect"].strip() if c else "",
                     "final_defect": f["defect"].strip() if f else "",
                     "blind_defect": r["defect"].strip(), "agree_original": int(bool(o) and o["defect"].strip() == r["defect"].strip()),
                     "agree_corrected": int(bool(c) and c["defect"].strip() == r["defect"].strip()),
                     "agree_final": int(bool(f) and f["defect"].strip() == r["defect"].strip()),
                     "not_blind": int(key in NOT_BLIND), "blind_note": r.get("note", "")[:200],
                     "original_note": (o or {}).get("note", "")[:200], "final_note": (f or {}).get("note", "")[:200]})
    with open(RES / "rereview.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    L = ["# Blind re-review, retail", "", f"tasks: {', '.join(sorted({r['task_id'] for r in rows}, key=int))}; rows compared: {len(rows)}", ""]
    nb = sorted(f"{t}/{c}" for t, c in NOT_BLIND)
    L.append(f"rows flagged not strictly blind (excluded in the second figure of each line): {', '.join(nb)}")
    L.append("")
    for col, label in (("original_defect", "blind vs original reviewer labels"), ("corrected_defect", "blind vs skeptic-corrected labels"),
                       ("final_defect", "blind vs final audit log (reviewers + probes + skeptic)")):
        parts = []
        for excl in (False, True):
            sub = [r for r in rows if r[col] != "" and not (excl and r["not_blind"])]
            if not sub:
                parts.append("n/a")
                continue
            a, b = [r[col] for r in sub], [r["blind_defect"] for r in sub]
            agree = sum(x == y for x, y in zip(a, b))
            parts.append(f"{agree}/{len(sub)} = {agree / len(sub):.3f}, kappa {kappa(a, b):.3f}")
        L.append(f"- {label}: {parts[0]}; without the flagged rows: {parts[1]}")
    L += ["", "Rows with no original reviewer label (mechanical or newly added checks): "
          + ", ".join(f"{r['task_id']}/{r['check']}" for r in rows if r["original_defect"] == "")]
    L += ["", "Disagreements (blind vs original):"]
    for r in rows:
        if r["original_defect"] != "" and not r["agree_original"]:
            L.append(f"- task {r['task_id']} {r['check']}: original={r['original_defect']} blind={r['blind_defect']}; blind note: {r['blind_note'][:160]}")
    L += ["", "Disagreements (blind vs final audit log):"]
    for r in rows:
        if r["final_defect"] != "" and not r["agree_final"]:
            L.append(f"- task {r['task_id']} {r['check']}: final={r['final_defect']} blind={r['blind_defect']}; blind note: {r['blind_note'][:160]}; final note: {r['final_note'][:120]}")
    (RES / "rereview_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
