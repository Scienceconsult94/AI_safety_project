"""Blind re-review agreement for retail (the retail reading of scripts/rereview_agreement.py).

Inputs (results/retail/):
  rereview_blind.csv       blind second-pass labels (task_id,check,defect,severity,evidence,note), produced without access
                           to the original review files
  review_batch_*.csv, review_overrides.csv   original labels (later files override earlier ones for the same (task_id, check));
                           the comparison uses the ORIGINAL reviewer label (batches), the skeptic-corrected label (overrides) is
                           reported in a separate column
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


def main() -> int:
    blind = read(RES / "rereview_blind.csv")
    batches = sorted(RES.glob("review_batch_*.csv"), key=lambda p: int(p.stem.split("_")[-1]))
    original = labels(batches)
    corrected = labels(batches + [RES / "review_overrides.csv"])
    rows = []
    for r in blind:
        key = (r["task_id"].strip(), r["check"].strip())
        o, c = original.get(key), corrected.get(key)
        rows.append({"task_id": key[0], "check": key[1], "original_defect": o["defect"].strip() if o else "", "corrected_defect": c["defect"].strip() if c else "",
                     "blind_defect": r["defect"].strip(), "agree_original": int(bool(o) and o["defect"].strip() == r["defect"].strip()),
                     "agree_corrected": int(bool(c) and c["defect"].strip() == r["defect"].strip()), "blind_note": r.get("note", "")[:200],
                     "original_note": (o or {}).get("note", "")[:200]})
    with open(RES / "rereview.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    L = ["# Blind re-review, retail", "", f"tasks: {', '.join(sorted({r['task_id'] for r in rows}, key=int))}; rows compared: {len(rows)}", ""]
    for col, label in (("original_defect", "blind vs original reviewer labels"), ("corrected_defect", "blind vs skeptic-corrected labels")):
        sub = [r for r in rows if r[col] != ""]
        if not sub:
            L.append(f"- {label}: n/a")
            continue
        a, b = [r[col] for r in sub], [r["blind_defect"] for r in sub]
        agree = sum(x == y for x, y in zip(a, b))
        L.append(f"- {label}: {agree}/{len(sub)} = {agree / len(sub):.3f}, Cohen's kappa {kappa(a, b):.3f}")
    L += ["", "Disagreements (blind vs original):"]
    for r in rows:
        if r["original_defect"] != "" and not r["agree_original"]:
            L.append(f"- task {r['task_id']} {r['check']}: original={r['original_defect']} blind={r['blind_defect']}; blind note: {r['blind_note'][:160]}")
    (RES / "rereview_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
