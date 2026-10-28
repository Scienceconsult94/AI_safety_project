"""Rebuild retail/audit_log.csv from the CSV inputs (one command, no LLM calls) — the retail reading of scripts/build_audit_log.py.

Inputs (results/retail/ unless noted):
  static_scan.csv          mechanical static checks over all 114 tasks (1a, 1b*, 1c*, 2a, 3d, 3f, 5a; * = provisional, the reviewer decides)
  noop_judge_probe.csv     2b (empty answer) and 2c (transfer only) through the real evaluators, judge where needed
  probe_2h.csv             WRITE-order permutations (2h); probe_2d.csv  argument perturbations (2d), hidden writes and forbidden write order (2e)
  probe_1g.csv, probe_1g_pair_order.csv   the modify_pending_order_items tool bug (1g) and the pair-order dependence it causes (2h)
  review_batch_*.csv       reviewer verdicts for 1b, 1c, 1d, 2k, 2m, 4a-4e (+ 2h, 2d, 2e where flagged)
  review_ALL.csv           benchmark-level static rows, task_id = ALL
  review_overrides.csv     rows that replace earlier rows after the skeptic review
  haiku_pass.csv           agent-run rows (agent_rows.py); review_agent.csv, review_agent_overrides*.csv (one per review part): readings of failed trajectories
  review_2j.csv            benchmark-level 2j row written after rejudge.py
  skeptic_verdicts*.csv    task_id,check,skeptic_ok,note
Output: retail/audit_log.csv (schema.md), then scripts/retail/validate_audit_log.py runs.
Usage (from ==Project):  python -I scripts/retail/build_audit_log.py
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "retail"
OUT = ROOT / "retail" / "audit_log.csv"
COLS = ["task_id", "bench_commit", "category", "check", "method", "defect", "severity", "evidence", "haiku_pass", "skeptic_ok", "date", "note"]
METHOD = {"2b": "probe", "2c": "probe", "2d": "probe", "2e": "probe", "2f": "probe", "2h": "probe", "2j": "probe",
          "1e": "agent_run", "1f": "agent_run", "4f": "agent_run", "5c": "agent_run", "5d": "agent_run", "5e": "agent_run", "5f": "agent_run"}
TODAY = date.today().isoformat()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def row(task_id, check, defect, severity, evidence, note="", haiku_pass="", commit=""):
    defect = str(int(bool(int(defect)))) if str(defect).strip() in {"0", "1"} else str(int(bool(defect)))
    return {"task_id": task_id, "bench_commit": commit, "category": check[0], "check": check, "method": METHOD.get(check, "static"),
            "defect": defect, "severity": severity.strip().lower() if defect == "1" else "",
            "evidence": evidence.strip().replace("\n", " "), "haiku_pass": haiku_pass, "skeptic_ok": "", "date": TODAY,
            "note": note.strip().replace("\n", " ")}


def static_rows(scan, probe, p2h, p2d, commit) -> list[dict]:
    out = []
    probe_by = {(r["task_id"], r["probe"]): r for r in probe}
    h_by = {r["task_id"]: r for r in p2h}
    d_by, e_by = defaultdict(list), defaultdict(list)
    for r in p2d:
        (d_by if r["check"] == "2d" else e_by)[r["task_id"]].append(r)
    for r in scan:
        tid, ev = r["task_id"], "results/retail/static_scan.csv"
        out.append(row(tid, "1a", r["reward_basis"] == "", "high", f"{ev}: reward_basis={r['reward_basis']}",
                       note="DB-only basis; no nl_assertions, so the reward is the same as DB+NL" if r["reward_basis"] == "DB" else "", commit=commit))
        flagged = int(r["replay_errors"]) > 0
        out.append(row(tid, "1b", flagged, "high", f"{ev}: replay_errors={r['replay_errors']} {r['replay_error_msgs']}".strip(),
                       note="PROVISIONAL (mechanical flag): reviewer decides intended negative step vs defect (PLAN.md deviation)" if flagged else "", commit=commit))
        c1 = bool(r["write_noop_ids"]) or (int(r["n_write"]) > 0 and r["db_changed"] == "0")
        out.append(row(tid, "1c", c1, "high", f"{ev}: n_write={r['n_write']}, db_changed={r['db_changed']}, write_noop_ids={r['write_noop_ids'] or '-'}",
                       note="PROVISIONAL (mechanical flag): reviewer decides" if c1 else "", commit=commit))
        out.append(row(tid, "2a", r["positive_control"] == "1", "high",
                       f"{ev}: gold_db_hash==init_db_hash is {r['db_changed'] == '0'}, nl_count={r['nl_count']}, nl_in_basis={r['nl_in_basis']}",
                       note="an empty answer is full reward by construction (DB unchanged, nothing else gates the reward); documented as intended τ-bench scoring (docs/evaluation.md)" if r["positive_control"] == "1" else "", commit=commit))
        for probe_id, label in (("2b", "greeting + one user turn, no tool call"), ("2c", "transfer only")):
            pr = probe_by.get((tid, probe_id))
            if pr is None:
                continue
            passes = pr["passes"] == "1"
            is_transfer_ref = probe_id == "2c" and int(r["n_transfer"]) > 0
            ev_p = (f"results/retail/noop_judge_probe.csv: {label} -> db_reward={pr['db_reward']} nl_gates={pr['nl_gates']} judged={pr['judged']} "
                    f"nl_reward={pr['nl_reward']} reward={pr['reward']}")
            if probe_id == "2c" and is_transfer_ref:
                out.append(row(tid, "2c", 0, "", ev_p, note="the reference itself is a transfer; a transfer-only answer is the intended solution", commit=commit))
            else:
                out.append(row(tid, probe_id, passes, "high", ev_p,
                               note=("in-process probe, real EnvironmentEvaluator + NLAssertionsEvaluator with the substituted judge" + ("; the judge accepted the assertions" if passes and pr["judged"] == "1" else "")) if passes else "", commit=commit))
        ci_leak = r["ci_in_user_scenario"] == "1" and r["comm_covered_by_nl"] == "1"
        nl_leak = bool(r["nl_numbers_in_user_scenario"])
        out.append(row(tid, "3d", 0, "", f"{ev}: ci_in_user_scenario={r['ci_in_user_scenario']}, comm_covered_by_nl={r['comm_covered_by_nl']}, nl_numbers_in_user_scenario={r['nl_numbers_in_user_scenario'] or '-'}",
                       note="mechanical flag: a reward-gating value may appear in the user prompt; decided in review_overrides.csv" if (ci_leak or nl_leak) else "", commit=commit))
        out.append(row(tid, "3f", r["init_hash_stable"] != "1", "high", f"{ev}: init_hash_stable={r['init_hash_stable']}", commit=commit))
        out.append(row(tid, "5a", r["replay_stable"] != "1", "high", f"{ev}: replay_stable={r['replay_stable']}", commit=commit))
        # 2h
        h = h_by.get(tid)
        if h is None:
            out.append(row(tid, "2h", 0, "", f"results/retail/probe_2h.csv: n/a, fewer than 2 WRITE actions (n_write={r['n_write']})", commit=commit))
        elif int(h["n_hash_differs"]) == 0:
            out.append(row(tid, "2h", 0, "", f"results/retail/probe_2h.csv: {h['n_permutations']} reorderings of {h['n_write']} WRITE actions [{h['write_names']}], hash unchanged in all (replay errors in {h['n_with_replay_error']})", commit=commit))
        else:
            out.append(row(tid, "2h", 0, "", f"results/retail/probe_2h.csv: {h['n_hash_differs']}/{h['n_permutations']} reorderings change the hash [{h['write_names']}]",
                           note="REVIEW: reviewer decides independent vs dependent writes", commit=commit))
        # 2d / 2e
        d = d_by.get(tid)
        if int(r["n_write"]) == 0:
            out.append(row(tid, "2d", 0, "", "results/retail/probe_2d.csv: n/a, no WRITE action in the reference", commit=commit))
        elif d:
            blind = [x for x in d if x["hash_equals_gold"] == "1"]
            rej = sum(1 for x in d if x["replay_error"])
            if blind:
                out.append(row(tid, "2d", 0, "", f"results/retail/probe_2d.csv: {len(blind)}/{len(d)} perturbations leave the hash unchanged: " + "; ".join(f"{x['tool']} {x['field']} {x['original']}->{x['alternative']} ({x['kind']})" for x in blind),
                               note="REVIEW: reviewer decides whether the substitution is a genuinely wrong solution", commit=commit))
            else:
                out.append(row(tid, "2d", 0, "", f"results/retail/probe_2d.csv: {len(d)} single-argument perturbations of the WRITE actions; {rej} rejected by the tool, the rest change the hash (none leaves it unchanged)", commit=commit))
        e = [x for x in e_by.get(tid, []) if x["field"] == "address"]
        if e:
            hidden = sum(1 for x in e if x["hash_equals_gold"] == "1")
            out.append(row(tid, "2e", 0, "", f"results/retail/probe_2d.csv: a wrong address written before the reference address write leaves the final hash equal to gold in {hidden}/{len(e)} probes",
                           note="end-state-only comparison hides the earlier wrong write; not a policy violation by itself (benchmark-level row 2e)", commit=commit))
    return out


def mechanical_overrides(p2d, p1g, p1g_pairs, commit) -> list[dict]:
    """Rows decided by probes after the reviewers (PLAN.md deviations of 2026-10-27): the forbidden write order (2e), the
    modify_pending_order_items tool bug (1g) and the pair-order dependence it causes (2h). They supersede reviewer rows of the
    same (task, check); review_overrides.csv and the skeptic verdicts still come after them."""
    out = []
    forbidden = defaultdict(list)
    for r in p2d:
        if r["check"] == "2e" and r["field"] == "write_order":
            forbidden[r["task_id"]].append(r)
    for tid, rs in forbidden.items():
        if any(x["hash_equals_gold"] == "1" for x in rs):
            out.append(row(tid, "2e", 1, "medium", "results/retail/probe_2d.csv (write_order): the reference modifies the order's address and then its items; the reversed sequence (items first, then address) replays without error to the gold hash. policy.md l.110 forbids any modification after the items change; modify_pending_order_address accepts the status 'pending (item modified)' (_is_pending_order substring test, tools.py)",
                           note="mechanical (probe), supersedes the reviewer's 2e row; the end-state comparison also hides an earlier wrong address write (same probe)", commit=commit))
    bad = defaultdict(list)
    for r in p1g:
        if r["matches"] == "0":
            bad[r["task_id"]].append(r)
    multi = {r["task_id"]: r for r in p1g_pairs}
    for tid, r in multi.items():
        wrong = bad.get(tid, [])
        out.append(row(tid, "1g", 1, "medium", f"results/retail/probe_1g.csv: the reference modifies {r['n_pairs']} items in one modify_pending_order_items call; {len(wrong)} of them are stored with the price/options of the last new variant (tools.py 'Modify the order' loop reuses `variant` from the validation loop); the scored target state is this corrupted order",
                       note="tool bug found during the review (PLAN.md deviation); the agent is scored against the corrupted state, so the reward is unaffected when the agent makes the same single call", commit=commit))
        if int(r["n_hash_differs"]) > 0:
            out.append(row(tid, "2h", 1, "medium", f"results/retail/probe_1g_pair_order.csv: the same (old item, new item) pairs listed in another order inside the one call give a different target hash in {r['n_hash_differs']}/{r['n_pair_orders_tried']} orders (consequence of the 1g bug: every item takes the last pair's price and options); the scenario does not fix the order",
                           note="mechanical (probe); a policy-compliant agent that lists the same swaps in another order is scored 0", commit=commit))
    out.append(row("ALL", "1g", 1, "medium", "tau2-bench/src/tau2/domains/retail/tools.py, modify_pending_order_items: the loop 'Modify the order' assigns item.price = variant.price and item.options = variant.options with `variant` left over from the validation loop (the last new variant); verified by replay in results/retail/probe_1g.csv (tasks 20, 21, 36, 37, 100: 7 items stored with another variant's price/options; target hash depends on pair order in 5/5 tasks)",
                   note="check 1g added 2026-10-27 during the review (PLAN.md deviations): a WRITE tool stores a state other than the one its documentation describes; issue candidate for the upstream repository", commit=commit))
    return out


def reviewer_rows(paths: list[Path], ids: set[str], commit: str) -> list[dict]:
    out = []
    for p in paths:
        for r in read(p):
            tid = r["task_id"].strip()
            if tid != "ALL" and tid not in ids:
                continue
            out.append(row(tid, r["check"].strip(), r["defect"].strip() == "1", r.get("severity", ""), r.get("evidence", ""), r.get("note", ""),
                           haiku_pass=r.get("haiku_pass", ""), commit=commit))
    return out


def main() -> int:
    sample = json.loads((ROOT / "retail" / "sample.json").read_text(encoding="utf-8"))
    ids, commit = set(sample["task_ids"]), sample["bench_commit"]
    rows = static_rows(read(RES / "static_scan.csv"), read(RES / "noop_judge_probe.csv"), read(RES / "probe_2h.csv"), read(RES / "probe_2d.csv"), commit)
    rows += reviewer_rows(sorted(RES.glob("review_batch_*.csv"), key=lambda p: int(p.stem.split("_")[-1]))
                          + [RES / "review_ALL.csv", RES / "review_2j.csv", RES / "haiku_pass.csv", RES / "review_agent.csv"], ids, commit)
    rows += mechanical_overrides(read(RES / "probe_2d.csv"), read(RES / "probe_1g.csv"), read(RES / "probe_1g_pair_order.csv"), commit)
    rows += reviewer_rows([RES / "review_overrides.csv"] + sorted(RES.glob("review_agent_overrides*.csv")), ids, commit)  # the skeptic's corrections come last
    verdicts = {}
    for p in sorted(RES.glob("skeptic_verdicts*.csv")):
        verdicts.update({(r["task_id"].strip(), r["check"].strip()): r for r in read(p)})
    dedup = {}
    for r in rows:  # later files override earlier ones
        dedup[(r["task_id"], r["check"])] = r
    for (t, c), r in dedup.items():
        v = verdicts.get((t, c))
        if v and r["defect"] == "1":
            ok = v["skeptic_ok"].strip()
            if ok in ("0", "") and v.get("note", "").strip().lower().startswith("should be defect=1"):
                ok = "1"  # an escalation: the skeptic filed the row itself, so it counts as skeptic-confirmed
            r["skeptic_ok"] = ok
            if v.get("note"):
                r["note"] = (r["note"] + "; skeptic: " + v["note"].strip()).strip("; ")
    hp = {t: r["haiku_pass"] for (t, c), r in dedup.items() if c == "1f" and r["haiku_pass"]}
    for (t, c), r in dedup.items():
        if r["method"] == "agent_run" and not r["haiku_pass"]:
            r["haiku_pass"] = hp.get(t, "")
    rows = sorted(dedup.values(), key=lambda r: (r["task_id"] == "ALL", int(r["task_id"]) if r["task_id"].isdigit() else 0, r["check"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    n_def = sum(r["defect"] == "1" for r in rows)
    by_sev = {s: sum(1 for r in rows if r["defect"] == "1" and r["severity"] == s) for s in ("high", "medium", "low")}
    tasks_def = sorted({r["task_id"] for r in rows if r["defect"] == "1" and r["severity"] in ("high", "medium") and r["task_id"] != "ALL"}, key=int)
    tasks_head = [t for t in tasks_def if any(r["task_id"] == t and r["defect"] == "1" and r["severity"] in ("high", "medium") and r["check"] not in ("2a", "2b", "2c") for r in rows)]  # headline: the no-op class is reported separately
    prov = sum(1 for r in rows if r["defect"] == "1" and "PROVISIONAL" in r["note"])
    print(f"retail/audit_log.csv: {len(rows)} rows; defect=1 rows: {n_def} {by_sev}; provisional defect rows still unreviewed: {prov}; "
          f"defective tasks without the no-op class (2a, 2b, 2c): {len(tasks_head)}/{len(ids)}; counting it: {len(tasks_def)}/{len(ids)}")
    return subprocess.call([sys.executable, "-I", str(Path(__file__).resolve().parent / "validate_audit_log.py")])


if __name__ == "__main__":
    sys.exit(main())
