"""Blind re-review agreement: compare the original reviewer labels with a blind second pass.

Inputs (results/):
  rereview_blind.csv       blind second-pass labels (task_id,check,defect,severity,evidence,note), produced without
                           access to the original review files
  review_batch_*.csv, review_2h.csv, review_agent.csv, review_agent_overrides.csv, review_overrides.csv
                           original labels; later files override earlier ones for the same (task_id, check),
                           mirroring build_audit_log.py. The comparison uses the ORIGINAL reviewer label, i.e.
                           before skeptic corrections, for the agent checks (review_agent.csv); the skeptic-corrected
                           label is reported in a separate column for information.
Output: results/rereview.csv (one row per (task_id, check) in the blind file: original, corrected, blind, agree flags)
        and the agreement numbers printed and written to results/rereview_summary.md.
Sampling of the three tasks: random.Random(20261027).sample(sample.json["task_ids"], 3) -> 23, 10, 37.
--set rest: the blind re-review of three of the 30 rest tasks (airline_full/PLAN.md: random.Random(20261028) -> 33, 35, 39):
  rereview_blind_rest.csv against the rest reviewer batches; the skeptic-corrected labels add review_overrides_rest_*.csv.
  Output: results/rereview_rest.csv and results/rereview_summary_rest.md.
Usage (from ==Project):  python -I scripts/rereview_agreement.py [--set rest]
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
RES = ROOT / "results"


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


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    pa1 = sum(a == "1" for a, _ in pairs) / n
    pb1 = sum(b == "1" for _, b in pairs) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return float("nan") if math.isclose(pe, 1.0) else (po - pe) / (1 - pe)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=("sample", "rest"), default="sample")
    rest = ap.parse_args().set == "rest"
    sfx = "_rest" if rest else ""
    blind = labels([RES / f"rereview_blind{sfx}.csv"])
    original = labels(sorted(RES.glob("review_batch_*.csv")) + [RES / "review_2h.csv", RES / "review_agent.csv"])
    corrected = labels(sorted(RES.glob("review_batch_*.csv")) + [RES / "review_2h.csv", RES / "review_overrides.csv"]
                       + sorted(RES.glob("review_overrides_rest_*.csv"))
                       + [RES / "review_agent.csv", RES / "review_agent_overrides.csv"])
    rows, pairs_orig, pairs_corr, missing = [], [], [], []
    for key in sorted(blind, key=lambda k: (int(k[0]), k[1])):
        b = blind[key]
        o = original.get(key)
        c = corrected.get(key)
        if o is None:
            missing.append(key)
        bd = b["defect"].strip()
        od = o["defect"].strip() if o else ""
        cd = c["defect"].strip() if c else ""
        rows.append({
            "task_id": key[0], "check": key[1],
            "original_defect": od, "original_severity": (o or {}).get("severity", ""),
            "corrected_defect": cd, "corrected_severity": (c or {}).get("severity", ""),
            "blind_defect": bd, "blind_severity": b.get("severity", ""),
            "agree_original": "" if o is None else str(int(od == bd)),
            "agree_corrected": "" if c is None else str(int(cd == bd)),
            "agree_severity_corrected": "" if c is None else str(int((c.get("severity", "") or "") == (b.get("severity", "") or ""))),
            "blind_note": b.get("note", "").replace("\n", " "),
            "original_note": (o or {}).get("note", "").replace("\n", " "),
        })
        if o is not None:
            pairs_orig.append((od, bd))
        if c is not None:
            pairs_corr.append((cd, bd))
    with open(RES / f"rereview{sfx}.csv", "w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def share(pairs):
        k = sum(a == b for a, b in pairs)
        return k, len(pairs), (k / len(pairs) if pairs else float("nan"))

    ko, no, so = share(pairs_orig)
    kc, nc, sc = share(pairs_corr)
    dis = [r for r in rows if r["agree_corrected"] == "0"]
    head = (["# Blind re-review of 3 rest tasks (33, 35, 39; random.Random(20261028))", "",
             "Labels compared on `defect` (0/1) per (task, check). The blind pass saw task cards, the static scan and probe outputs,",
             "the policy and tool code, checklist.md and the review brief (with the block-1 defect rows of batches 2-4 as style",
             "examples); none of batches 8 and 9, the audit log, skeptic or summary files. Corrected labels = after the adversarial",
             "review of the rest rows (review_overrides_rest_*.csv; equal to the original labels where none exists).", ""]
            if rest else
            ["# Blind re-review of 3 sampled tasks (23, 10, 37; random.Random(20261027))", "",
             "Labels compared on `defect` (0/1) per (task, check). The blind pass saw task cards, mechanical scan/probe outputs,",
             "the task-23 GT trajectory, the policy and tool code, and checklist.md; none of the review, skeptic or summary files.", ""])
    lines = head + [
             "| comparison | agreement | Cohen's kappa |", "|---|---|---|",
             f"| blind vs original reviewer labels | {ko}/{no} = {so:.3f} | {kappa(pairs_orig):.3f} |",
             f"| blind vs skeptic-corrected labels | {kc}/{nc} = {sc:.3f} | {kappa(pairs_corr):.3f} |", "",
             f"Disagreements vs corrected labels ({len(dis)}):"] + \
            [f"- task {r['task_id']} check {r['check']}: corrected={r['corrected_defect']} blind={r['blind_defect']} — blind note: {r['blind_note'][:220]}" for r in dis] + \
            ([""] + [f"- no original label for task {t} check {c} (blind row kept, not counted)" for t, c in missing] if missing else [])
    (RES / f"rereview_summary{sfx}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
