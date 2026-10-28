# Adversarial review brief — retail agent-run rows (results skeptic, second pass)

Object: the trajectory review of the retail runs, `results/retail/review_agent.csv` (concatenation of `review_agent_A..E.csv`, five independent reviewers, checks 1e, 4f, 5c, 5d, 2j per task) and the five `review_agent_<batch>.md` readings, plus the re-judge output `results/retail/rejudge.csv` / `rejudge_summary.md` (check 2j). Try to kill every `defect=1` row before it counts, catch the rows that should have been defects, and make the five reviewers consistent with each other (they worked in isolation on disjoint task batches).

## Inputs

- `retail/review_agent_brief.md` (what the reviewers were told: cause classes A–E, row rules), `checklist.md`, `retail/checklist.md`, `retail/PLAN.md` (the dated Deviations at the end are binding).
- Transcripts: `results/retail/trajectories/<task>_<haiku|gt>_t<k>.md` (read every trajectory a defect row cites, and the successful trials of flipped tasks); `results/retail/agent_triage.md`; `results/retail/agent_runs_summary.md`; `results/retail/haiku_pass.csv`.
- Task cards `results/retail/task_cards/task_<id>.md`; `tau2-bench/data/tau2/domains/retail/policy.md`; `tau2-bench/src/tau2/domains/retail/tools.py`; `tau2-bench/src/tau2/user/guidelines.py` (simulator instructions); `tau2-bench/src/tau2/evaluator/evaluator_nl_assertions.py` (what the judge sees: `role: content` lines, one vote).
- The static-phase log and its skeptic pass: `retail/audit_log.csv`, `results/retail/skeptic_report.md` (open question 6 there asks you to check 18 4d, the conditional branches of 45/60 and the minimal-change reading of 86/91/100 against the trajectories).
- Do not open `tau2-bench/data/tau2/domains/retail/tasks.json` or `task_issues/`. Do not call any model. Nothing under `tau2-bench/` is edited.

## What to decide

For every `defect=1` row: `skeptic_ok` = 1 (holds: the cited turns say what the row says, the cause class is right, the check id and severity follow the brief) or 0 (does not hold, or belongs under another check or class). For rows with defect=0 whose reading looks wrong (a class B labelled A, a class D labelled C, a judge error missed), escalate with a note starting "should be defect=1 <severity>:". Consistency rules to settle and state: when a simulator request for a human counts as a deviation; when an agent's refusal is class A versus class C; when a judge verdict is class E (the assertion is satisfied "in substance") versus an agent omission; 1e severity (high only when no policy-compliant conversation reaches the reference); 4f versus the static rows (no double counting of a mechanism the static log already carries on the same task).

Cross-check 2j with the re-judge: for every judge-only failure (DB matched, an assertion unmet) the reviewers classified, compare with the 3-vote majority in `rejudge.csv`; a disagreement between the reading and the majority is not decisive either way, but say which you believe and why.

## Output

1. `results/retail/skeptic_verdicts_agent.csv` — header `task_id,check,skeptic_ok,note`; one row per reviewed defect row and per escalation (`skeptic_ok` empty, note "should be defect=1 <severity>: ..." or "stays 0: ...").
2. `results/retail/review_agent_overrides.csv` — header `task_id,check,defect,severity,evidence,note`; the corrected rows, read last by the builder.
3. `results/retail/skeptic_report_agent.md` — verdict table (row, holds / fails / re-filed, one line why), the consistency rules applied, cross-cutting findings (simulator patterns, judge patterns), the cause-class tally per trajectory after your pass, and what you could not verify.

English, impersonal, no names of people, no mention of which model or tool wrote the review. Return in your final message: counts (rows reviewed, confirmed, rejected, re-filed, escalated), the rejected and escalated rows, and open questions.
