# Reviewer brief: static checks on the 30 unsampled airline tasks

This brief restates, for reviewer batches 5–10, the conventions that batches 1–4 followed (`results/review_batch_1.md` … `_4.md` show the expected depth and style). One batch = five tasks. Work from the pinned benchmark only.

## Sources

- `checklist.md`: the definition, method, `defect_if` rule and severity of every check. It is the authority; this brief only summarises.
- `schema.md`: the row format.
- `results/task_cards/task_<id>.md`: one card per task (user-simulator instructions, reference actions, `communicate_info`, `nl_assertions`, static-scan flags).
- `tau2-bench/data/tau2/domains/airline/tasks.json`, `db.json`, `policy.md`, and `tau2-bench/src/tau2/domains/airline/tools.py` (the tool semantics, read-only).
- `results/static_scan.csv` (mechanical flags per task) and `results/probe_2h.csv` (write-order permutations).
- Clock: 2024-05-15 15:00:00 EST (policy line 3; `_get_datetime` in `tools.py`).

Do not read `audit_log.csv`, `results/skeptic_*`, `results/review_agent*`, `results/rereview*` or other batches' files: the batches are independent. Do not edit any existing file, and do not touch `tau2-bench/`.

## Checks per task

Write exactly one row per task for each of: **1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e**. Write a **2h** row only for the tasks listed in `results/probe_2h.csv` (in these batches: 14, 17, 18, 29, 33, 39, 42).

| check | what to decide (see `checklist.md` for the full method) | defect_if | severity |
|---|---|---|---|
| 1d | Every value the reference needs is stated in `user_scenario.instructions` or reachable through READ tools from user-given ids. Values listed in `unknown_info` do not count as stated. | a required value is neither stated nor derivable | high |
| 2g | List `communicate_info` strings of ≤3 characters or bare integers; search for them in non-answer positions (dates, ids, prices, the default greeting). | a match occurs in a non-answer position, or in the greeting | medium |
| 2h | Read the permutation result; also vary choices the scenario leaves open. | a policy-compliant variant that the scenario allows scores 0 | medium |
| 2k | Compare `nl_assertions` with `actions` and `communicate_info`; `tau2 run` does not evaluate `nl_assertions` for airline. | an assertion demands a behaviour (inform X, refuse Y) that neither the DB hash nor `communicate_info` checks, and breaking it still yields 1.0 | medium |
| 4a | `reason_for_call` + `task_instructions` against the reference WRITE actions and their arguments. | the reference makes a change the user did not ask for, omits a permitted change the user asked for, or uses different values | medium |
| 4b | Each WRITE against `policy.md` (cancellation eligibility, basic-economy rules, baggage, payment and certificate rules, the clock). | the reference violates the policy; high if no compliant trajectory reaches the target hash | medium |
| 4c | List the choices the reference fixes (payment method, flight among equal options, cabin, insurance, bags) and whether the scenario or the policy pins each. | ≥2 compliant end states fit the scenario and only one hash passes | medium |
| 4d | Ids, names, dates and amounts in the instructions against `db.json`. | a mismatch; high if it blocks the reference path | medium |
| 4e | `nl_assertions`, `description.purpose`, `description.notes` against `actions` / `communicate_info`. | a contradiction (an assertion forbids a write the reference makes, or similar) | medium |

Conventions from batches 1–4:
- Recompute every amount yourself (fares × passengers, bag fees, refunds, certificate remainders) and show the arithmetic in `evidence`.
- A task whose reference leaves the DB unchanged and whose `communicate_info` is empty passes for an empty answer; that is checks 2a/2b (not yours). On such a task, 2k is still judged on its own rule: a refusal or information requirement that only an assertion states is a 2k defect.
- `defect` is 1 only when the rule holds; when the evidence is suggestive but the rule does not hold, write 0 and say so in `note`. Observations that belong to another check go into `note` with that check's id; they are not counted.
- Evidence must let a reader reproduce the verdict: file and field, ids, the quote, the computation.

## Output

For batch N, write two new files:
- `results/review_batch_N.csv` with the header `task_id,check,defect,severity,evidence,note` (UTF-8, comma-separated, fields quoted where needed; `severity` empty when `defect` = 0).
- `results/review_batch_N.md`: a heading `# Review batch N: airline tasks a, b, c, d, e`, the line `Checks applied: …`, then one section per task in the style of `results/review_batch_1.md` (request, computation, the verdicts that need words).

Return a short report: the rows with `defect` = 1 (task, check, severity, one line each) and anything you could not decide.
