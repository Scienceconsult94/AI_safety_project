"""H1 under the judge: what does v2 give an agent that does nothing on the 23 no-op tasks? (design review C1)

The empty-trajectory rule never fires in a live run, because the orchestrator opens every conversation
with the canned greeting and the user then speaks. So two synthetic trajectories are scored per no-op
task (the 23 tasks whose reference leaves the DB unchanged and whose communicate_info is empty):

  2b_probe      [greeting, one user turn]                      -> rule (greeting excluded), no judge call
  refusal_bot   [greeting, user turn, "I'm sorry, I can't help with that.", user turn, same refusal]
                                                               -> judged (3 votes) against the task's nl_assertions

The user turn is the task's reason_for_call rewritten to the first person (mechanical substitution,
recorded verbatim in the output). The DB and communicate parts pass for both by construction (no tool
calls, no required strings), so the NL verdict alone decides. Pre-stated reading (skeptic_design.md C1):
~13 of 23 refusal-bot runs were predicted to pass because their assertions are of the "does not do X"
kind. Cost: 23 x 3 short judge calls.

Run from inside tau2-bench:  uv run --no-sync python ../scripts/v2/noop_judge_probe.py [--dry]
Outputs: results/v2/noop_judge_probe.csv, noop_judge_probe.md, judge votes appended to judge_cache_noop.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
OUT = ROOT / "results" / "v2"

import scorer_v2 as s2  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.registry import registry  # noqa: E402

REFUSAL = "I'm sorry, I can't help with that."


def first_person(text: str) -> str:
    t = text.strip()
    subs = [(r"\bYou are\b", "I am"), (r"\byou are\b", "I am"), (r"\bYou were\b", "I was"), (r"\bYou have\b", "I have"), (r"\byou have\b", "I have"),
            (r"\bYou want\b", "I want"), (r"\byou want\b", "I want"), (r"\bYou\b", "I"), (r"\byou\b", "me"), (r"\bYour\b", "My"), (r"\byour\b", "my"),
            (r"\byourself\b", "myself")]
    for a, b in subs:
        t = re.sub(a, b, t)
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if not args.dry:
        s2.require_clean("noop_judge_probe")
    s2.install()
    s2.set_judge_cache(OUT / "judge_cache_noop.json")
    s2.SWITCHES.set(True, True, True)
    tasks = {t.id: t for t in registry.get_tasks_loader("airline")("base")}
    noop_ids = [r["task_id"] for r in csv.DictReader(open(OUT / "noop_scan_v2.csv", encoding="utf-8")) if r["noop_pass_v1"] == "1"]
    classes = {}
    p = ROOT / "block2" / "nl_assertion_classes.csv"
    if p.exists():
        classes = {(r["task_id"], int(r["idx"])): r["class"] for r in csv.DictReader(open(p, encoding="utf-8"))}
    rows = []
    for tid in noop_ids:
        t = tasks[tid]
        user_turn = first_person(t.user_scenario.instructions.reason_for_call or "")
        asserts = t.evaluation_criteria.nl_assertions or []
        greeting = AssistantMessage(role="assistant", content=s2.GREETING)
        probe = [greeting, UserMessage(role="user", content=user_turn)]
        bot = probe + [AssistantMessage(role="assistant", content=REFUSAL), UserMessage(role="user", content="Please, I really need this done."), AssistantMessage(role="assistant", content=REFUSAL)]
        r2b = s2.judge_nl_assertions(probe, asserts)  # rule only, no call
        row = {"task_id": tid, "n_assertions": len(asserts), "user_turn": user_turn[:200], "probe_2b_pass": int(all(d["met"] is True for d in r2b)), "probe_2b_rule": r2b[0]["rule"] if r2b else ""}
        if not args.dry:
            det = s2.judge_nl_assertions(bot, asserts)
            row["refusal_bot_pass"] = int(all(d["met"] is True for d in det))
            row["refusal_bot_pass_noproc"] = int(all(d["met"] is True for i, d in enumerate(det) if classes.get((tid, i)) != "process")) if classes else ""
            row["refusal_bot_unmet"] = "; ".join(a[:70] for a, d in zip(asserts, det) if d["met"] is not True)[:300]
            row["refusal_bot_undetermined"] = sum(1 for d in det if d["met"] is None)
            row["votes"] = "/".join(f"{d['votes_met']}-{d['votes_unmet']}-{d['votes_undetermined']}" for d in det)
        rows.append(row)
        print(f"task {tid:>2}: 2b_probe pass={row['probe_2b_pass']}" + (f"  refusal_bot pass={row['refusal_bot_pass']} unmet={row['refusal_bot_unmet'][:80]}" if not args.dry else ""))
    with open(OUT / "noop_judge_probe.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=sorted({k for r in rows for k in r}, key=lambda k: (k != "task_id", k)))
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    cost = s2.JUDGE_COST["in_tokens"] / 1e6 * 0.10 + s2.JUDGE_COST["out_tokens"] / 1e6 * 0.50
    md = ["# No-op tasks under v2: the 2b probe and a refusal bot", "",
          f"{n} tasks whose empty trajectory passes under v1 (noop_scan_v2.csv). Provenance: {json.dumps({k: s2.provenance()[k] for k in ('overlay_commit', 'overlay_dirty', 'judge_model', 'judge_view')})}.", "",
          "| trajectory | passes under v2 | of |", "|---|---|---|",
          f"| greeting + one user turn (block-1 2b probe) | {sum(r['probe_2b_pass'] for r in rows)} | {n} |"]
    if not args.dry:
        md += [f"| refusal bot (no tool calls, two refusals) | {sum(r['refusal_bot_pass'] for r in rows)} | {n} |",
               f"| refusal bot, process-class assertions excluded | {sum(1 for r in rows if r.get('refusal_bot_pass_noproc') == 1)} | {n} |", "",
               f"Judge calls {s2.JUDGE_COST['calls']} (re-asks {s2.JUDGE_COST['retries']}), tokens in/out {s2.JUDGE_COST['in_tokens']:,}/{s2.JUDGE_COST['out_tokens']:,}, own cost estimate ${cost:.3f}. "
               f"Undetermined verdicts: {sum(int(r['refusal_bot_undetermined']) for r in rows)}.", "",
               "| task | refusal bot | unmet assertions |", "|---|---|---|"]
        md += [f"| {r['task_id']} | {r['refusal_bot_pass']} | {r['refusal_bot_unmet']} |" for r in rows]
    md += ["", "Reading: under v1 all of these tasks score 1.0 for any agent that changes nothing. Under v2 the 2b probe fails by rule; the refusal bot "
           "passes exactly where every assertion is of the 'does not do X' kind, which tau2's documentation calls the intended τ-bench outcome "
           "(docs/evaluation.md). v2 is therefore a stricter alternative protocol for those tasks, not a repair of a bug.", ""]
    (OUT / "noop_judge_probe.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
