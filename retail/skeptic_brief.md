# Adversarial review brief — retail static phase (results skeptic)

You are the adversarial reviewer of the retail audit of tau2-bench v2.0.0 (commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Twelve independent reviewers filed verdicts on all 114 tasks; probes and the static scan filed mechanical rows. Your job is to try to **kill every defect=1 row of severity medium or high** before it counts, and to catch the rows that should have been defects. Evidence beats opinion; primary sources beat reviewer notes.

## Inputs

- `retail/audit_log.csv` — the merged log (one row per task × check; `method`, `defect`, `severity`, `evidence`, `note`); built by `scripts/retail/build_audit_log.py` from the inputs below. Review every row with `defect=1` and `severity` in {high, medium}, and every row whose `note` starts with "uncertain:" or contains "REVIEW" or "PROVISIONAL".
- Definitions: `checklist.md` (ids, methods, severities), `retail/checklist.md` (retail readings; the correction on the once-per-order rule), `retail/PLAN.md` (pre-registration; the dated Deviations at the end are binding, in particular the four coordinator decisions: 1g, forbidden write order under 2e, policy line 84 read conservatively, 1b severity by effect on the target; unstated cancel reason = 4c not 1d; 2m per task only where the scenario itself is about the process rule), `retail/review_brief.md` (what the reviewers were told), `schema.md`.
- Primary sources: `results/retail/task_cards/task_<id>.md`; `tau2-bench/data/tau2/domains/retail/policy.md`; `tau2-bench/src/tau2/domains/retail/tools.py`; `tau2-bench/data/tau2/domains/retail/db.json` (read-only queries); `tau2-bench/src/tau2/evaluator/*.py`.
- Probe outputs: `results/retail/static_scan.csv`, `probe_2h.csv`, `probe_2d.csv`, `probe_1g.csv`, `probe_1g_pair_order.csv`, `noop_judge_probe.csv/.md`.
- Reviewer files: `results/retail/review_batch_1..12.csv/.md`, `results/retail/review_ALL.csv/.md`.
- Do not open `tau2-bench/data/tau2/domains/retail/tasks.json` or `task_issues/` (the upstream `issues` field is compared with the audit afterwards, by script). Do not run anything that calls a model. You may run read-only Python inside the tau2 venv for replays: from `tau2-bench/`, `uv run --no-sync python -c "..."` (environment construction and `make_tool_call` only; never edit the clone, never `pip`/`uv sync`).

## What to decide, per row

For each defect=1 (medium/high) row: `skeptic_ok` = 1 (holds: the evidence reproduces, the severity matches the checklist, the check id is the right one) or 0 (does not hold, or belongs under another check, or severity wrong) with a note that says what you verified and what should change. For "uncertain:" rows and rows the reviewers flagged as borderline in their .md files: say whether they should become defect=1 (note starting "should be defect=1 <severity>: ...") or stay 0.

Consistency is part of the job: the same mechanism must carry the same check id and severity on every task (reviewers worked in isolation). Known tensions to settle with the PLAN rules: 2e vs 2m for the forbidden write order (2e per task is mechanical; 2m only where the scenario puts the item change first); 4c vs 1d for unstated cancel reasons; 2m for tasks 5–9 (confirmation scenarios), 35/39 (authentication with the user id given), 50/10/12 (transfer tasks; overlap with 2b); 1b for READ raises (low) vs WRITE raises (high); 110 1c vs 4d; 26 4a (a transfer whose summary belongs to another task); 86/91/100 4c (variant pinned by a minimal-change reading); 74 1d/4c (payment method only in `unknown_info`); 105 (four rows from one failing reference write: which stay); 104 4e (description.purpose wrong, reward unaffected); 20/21 4c re-filed under 2h.

Recompute every amount that a defect row depends on from the card prices. Replay when a hash claim matters and the probe did not cover it (e.g. tasks 54, 55, 64 where probes stopped at an intended failing lookup).

## Output

1. `results/retail/skeptic_verdicts.csv` — header `task_id,check,skeptic_ok,note`; one row per reviewed defect row (and per "uncertain"/borderline row you escalate, with `skeptic_ok` empty and the note starting "should be defect=1 <severity>:" or "stays 0:").
2. `results/retail/review_overrides.csv` — header `task_id,check,defect,severity,evidence,note`; the corrected rows (re-filed check ids, severities, escalations, consistency fixes), ready to be read last by the builder. Include the 4c→0 rows for tasks 20 and 21 ("re-filed under 2h") and whatever your consistency pass requires.
3. `results/retail/skeptic_report.md` — a verdict table (row, holds / fails / re-filed, one line why), the consistency rules you applied, the rows you escalated, the numbers before and after your pass (defective tasks under the literal 1b rule and under the PLAN reading), and anything you could not verify.

English, impersonal, no names of people, no mention of which model or tool wrote it. Return in your final message: counts (rows reviewed, confirmed, rejected, re-filed, escalated), the list of rejected and escalated rows, and open questions.
