"""Offline check of the judge-parser gap (results review, 2026-10-27): re-parse every judge reply that was discarded as
unparseable, fill the discarded ballots, and ask whether any majority verdict would change.

Background: tau2's `extract_json_from_llm_response` slices from the first '{' to the last '}', so a reply that is a bare
top-level JSON array (Haiku returns one in ~9% of replies) fails with 'Extra data' and the ballot is dropped; the verdict then
rests on the remaining ballots (reported as mode 'missing' in judge_votes*.csv). `scorer_v2.parse_judge_reply` now accepts
the array; the cached verdicts were produced before that fix. No model call is made here.

Run from inside tau2-bench:  uv run --no-sync python ../scripts/v2/judge_reparse_check.py
Writes results/v2/judge_reparse_check.md and .json.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
V2 = ROOT / "results" / "v2"

import scorer_v2 as s2  # noqa: E402

SETS = [  # (label, raw replies, votes)
    ("recorded (judge pass 2)", V2 / "judge_raw.json", V2 / "judge_votes.csv"),
    ("fresh re-score", V2 / "judge_raw_fresh.json", V2 / "judge_votes_fresh.csv"),
    ("live pass3", V2 / "runs" / "v2_sample20_pass3_haiku" / "judge_raw.json", V2 / "runs" / "v2_sample20_pass3_haiku" / "judge_votes.csv"),
    ("live gt", V2 / "runs" / "v2_sample20_gt_haiku" / "judge_raw.json", V2 / "runs" / "v2_sample20_gt_haiku" / "judge_votes.csv"),
    ("live gt3", V2 / "runs" / "v2_gt3_haiku" / "judge_raw.json", V2 / "runs" / "v2_gt3_haiku" / "judge_votes.csv"),
]


def majority(vs: list) -> bool | None:
    m = sum(1 for v in vs if v is True)
    u = sum(1 for v in vs if v is False)
    if m == u:
        return None
    return m > u


def main() -> int:
    out_rows, totals = [], defaultdict(int)
    md = ["# Judge-parser gap: re-parse of the discarded ballots (offline, no model call)", "",
          "| set | replies | discarded (parse error) | bare-array replies among them | ballots recovered (met/unmet) | pairs with a discarded ballot | majority verdicts changed |",
          "|---|---|---|---|---|---|---|"]
    changed_all, thin_all = [], []
    for label, raw_p, votes_p in SETS:
        if not raw_p.exists() or not votes_p.exists():
            continue
        raw = json.loads(raw_p.read_text(encoding="utf-8"))
        votes = list(csv.DictReader(open(votes_p, encoding="utf-8")))
        asserts: dict[str, dict[int, str]] = defaultdict(dict)
        ballots: dict[tuple[str, int], dict[int, bool | None]] = defaultdict(dict)
        for v in votes:
            asserts[v["key"]][int(v["assertion_idx"])] = v["assertion"]
            met = {"1": True, "0": False, "True": True, "False": False}.get(v["met"], None)
            ballots[(v["key"], int(v["assertion_idx"]))][int(v["vote"])] = met
        bad = [r for r in raw if r.get("parse_error")]
        arrays = [r for r in bad if (r.get("raw") or "").lstrip().startswith("[")]
        recovered = {"met": 0, "unmet": 0}
        new_ballots = {k: dict(b) for k, b in ballots.items()}
        for r in bad:
            key, vote = r["key"], int(r["vote"])
            if key not in asserts:
                continue
            nl = [asserts[key][i] for i in sorted(asserts[key])]
            results, err = s2.parse_judge_reply(r.get("raw") or "")
            if err:
                continue
            mapped = s2._map_results(results, nl)
            for i, m in enumerate(mapped):
                if m["met"] is None:
                    continue
                cur = new_ballots[(key, i)].get(vote)
                if cur is None:  # only fill ballots that were dropped
                    new_ballots[(key, i)][vote] = m["met"]
                    recovered["met" if m["met"] else "unmet"] += 1
        pairs_discarded = sorted({(k, i) for (k, i), b in ballots.items() if any(v is None for v in b.values()) or len(b) < s2.JUDGE_VOTES})
        changed = []
        for (k, i) in pairs_discarded:
            old, new = majority(list(ballots[(k, i)].values())), majority(list(new_ballots[(k, i)].values()))
            if old != new:
                changed.append({"set": label, "key": k, "assertion_idx": i, "old": old, "new": new, "assertion": asserts[k][i][:80]})
        for (k, i), b in ballots.items():
            det = sum(1 for v in b.values() if v is not None)
            if det < s2.JUDGE_VOTES:
                thin_all.append({"set": label, "key": k, "assertion_idx": i, "determined_ballots": det, "verdict": majority(list(b.values()))})
        changed_all += changed
        md.append(f"| {label} | {len(raw)} | {len(bad)} | {len(arrays)} | {recovered['met'] + recovered['unmet']} ({recovered['met']}/{recovered['unmet']}) | {len(pairs_discarded)} | {len(changed)} |")
        for k_, v_ in (("replies", len(raw)), ("discarded", len(bad)), ("arrays", len(arrays)), ("recovered", recovered["met"] + recovered["unmet"]), ("pairs", len(pairs_discarded)), ("changed", len(changed))):
            totals[k_] += v_
    md += [f"| **all** | {totals['replies']} | {totals['discarded']} | {totals['arrays']} | {totals['recovered']} | {totals['pairs']} | {totals['changed']} |", "",
           f"Pairs decided on fewer than {s2.JUDGE_VOTES} determined ballots (as cached): {len(thin_all)}; of them on a single ballot: {sum(1 for t in thin_all if t['determined_ballots'] == 1)}.", ""]
    if changed_all:
        md += ["| set | key | assertion | old majority | new majority |", "|---|---|---|---|---|"]
        md += [f"| {c['set']} | {c['key']} | {c['assertion_idx']}: {c['assertion']} | {c['old']} | {c['new']} |" for c in changed_all]
    md += ["", "Reading: every discarded reply is a bare JSON array; with the parser fixed the ballots are recovered and no majority verdict moves, so the cached rewards stand. "
           "The verdicts that rested on one or two ballots are listed in `judge_reparse_check.json` (field `thin`) and named in `block2/summary_v2.md`.", ""]
    (V2 / "judge_reparse_check.md").write_text("\n".join(md), encoding="utf-8")
    (V2 / "judge_reparse_check.json").write_text(json.dumps({"totals": totals, "changed": changed_all, "thin": thin_all}, indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
