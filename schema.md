# audit_log.csv — schema and conventions

One row per `(task_id, check)`. Columns, in this order:
`task_id, bench_commit, category, check, method, defect, severity, evidence, haiku_pass, skeptic_ok, date, note`.

| column | rule |
|---|---|
| task_id | an airline `base` task id (`sample.json` → `population_ids`), or `ALL` for a benchmark-wide check (checklist convention) |
| bench_commit | 40-hex SHA of the pinned checkout; one value for the whole file, equal to `sample.json` → `bench_commit` |
| category | 1–6, the checklist numbering of the audit plan (1 solvability, 2 scoring validity, 3 isolation/leaks, 4 specification clarity, 5 determinism, 6 reporting) |
| check | check id from `checklist.md` (e.g. `2a`); free text never |
| method | `static` = code/data inspection, no model call; `probe` = scripted evaluator call (e.g. empty trajectory); `agent_run` = real model run |
| defect | `1` only when confirmed; otherwise `0` |
| severity | required when defect=1 (`high` = the result is uninformative (the task passes for doing nothing or for a dump of everything, or the reference does not pass it); `medium` = the outcome depends on interpretation or chance (the scenario contradicts the reference, a change of scorer changes the outcome); `low` = no effect on the reward); empty when defect=0 |
| evidence | file path, line reference, rule or short quote that reproduces the finding; required when defect=1 |
| haiku_pass | `k/n` only when method=agent_run; otherwise empty |
| skeptic_ok | `1` confirmed by the adversarial reviewer, `0` rejected, empty = not yet reviewed; only defect=1 rows carry a value |
| date | ISO `yyyy-mm-dd`, the day the row was written |
| note | optional free text; `patched=nl_judge_haiku` whenever the row's run used the recorded patch |

Derived rule: a task is **defective** iff it has ≥1 row with defect=1 and severity ∈ {high, medium}. Headline counts leave out the documented no-op class (checks 2a, 2b; in retail also 2c) and report it on its own line; the counts that include it are listed beside them (report Section 2, counting rule).
Validation: `python -I scripts/validate_audit_log.py` (exit code 0 = all rules hold).
