# Adversarial review brief: airline rest tasks, static phase

This brief covers the audit of tau2-bench v2.0.0 (commit `989d3285ae669e49503324bdb9981bf14fccedeb`), airline domain. Block 1 audited a seed-drawn sample of 20 tasks. This phase covers the 30 remaining tasks: 0 2 4 5 6 12 13 14 15 17 18 24 25 27 29 30 31 33 34 35 36 38 39 40 41 42 43 45 47 49.

What already exists:
- Six independent reviewer batches (5-10) filed static verdicts for checks 1d, 2g, 2k and 4a-4e on these tasks, plus 2h for the tasks in `probe_2h.csv`.
- A blind re-review re-labelled tasks 33, 35 and 39.
- The static scan filed the mechanical rows.

Your job has three parts:
- Try to **kill every defect=1 row of severity medium or high** before it counts.
- Settle the rows the reviewers left undecided.
- Catch rows that should have been defects.

Evidence beats opinion, and primary sources beat reviewer notes.

The review is split **by check family** across three independent skeptics, so that one mechanism is judged the same way on every task:

| part | checks | scope |
|---|---|---|
| `2k` | 2k (unenforced assertions) | every 2k row on the 30 tasks |
| `order` | 2h and 4c (order effects and open choices) | every 2h and 4c row on the 30 tasks |
| `other` | 1d, 2g, 4a, 4b, 4d, 4e and the mechanical rows | every row of these checks on the 30 tasks |

Each part also settles the blind re-review disagreements for its own checks.

## Inputs

**Rows under review:**
- `results/review_batch_5.csv` ... `review_batch_10.csv`, with the reviewers' reasoning in the matching `.md` files.
- `results/rereview_blind_rest.csv`: the blind re-review of tasks 33, 35 and 39.
- `results/static_scan.csv`: the mechanical flags per task (`noop_pass`, `positive_control`, `db_changed`, `comm_len`, ...).
- `results/probe_2h.csv`: the WRITE-order permutations.

**Definitions:**
- `checklist.md` is the authority (`defect_if` rules, methods, severities).
- `schema.md` defines the row format.
- `airline_full/review_brief.md` is what the reviewers were told.

**Precedent from block 1** (binding conventions, summarised below):
- `results/skeptic_report.md`
- `results/skeptic_report_rereview.md`
- `results/review_overrides.csv`
- `results/skeptic_verdicts_relabel.csv`
- the block-1 reviewer files `results/review_batch_1.csv` ... `_4.csv`

**Primary sources:**
- `results/task_cards/task_<id>.md`
- `tau2-bench/data/tau2/domains/airline/tasks.json`, `db.json`, `policy.md`
- `tau2-bench/src/tau2/domains/airline/tools.py`
- `tau2-bench/src/tau2/utils/pydantic_utils.py` (`get_pydantic_hash`)
- `tau2-bench/src/tau2/evaluator/*.py`
- The clock is 2024-05-15 15:00:00 EST.

**Do not read:**
- `airline_full/PLAN.md`: it holds the pre-registered predictions.
- Anything that comes from live runs: `results/runs/`, `results/v2/`, `results/review_agent*`, `results/haiku_pass*`, `results/probe_2j*`, `results/review_2j.csv`. Agent-run rows are reviewed separately, later.
- `audit_log.csv` and `airline_full/audit_log.csv`.
- The other two parts' output files.

## Tools and limits

- **Read-only Python.** Use the system interpreter `<system python> -I` for JSON, CSV and arithmetic.
- **Replays inside the pinned benchmark.** From `tau2-bench/`, run `uv run --no-sync python <script>`, where the script lives in your own temporary folder. Allowed: environment construction through the registry, `make_tool_call` and `get_db_hash`.
- **Prohibited:**
  - editing the clone;
  - `uv sync`, `pip` or any install;
  - model or API calls;
  - network;
  - git.
- **Temporary folder:** `<temporary folder>\skeptic_rest_<part>\`.
- **Files you may create:** only the three output files below. Do not modify any existing file.

## Scoring facts

- **Airline reward** = DB-hash equality × COMMUNICATE.
  - **DB hash:** the agent's final DB is compared with the DB after replaying the reference actions on a fresh environment.
  - **COMMUNICATE:** each `communicate_info` string must occur in some assistant message. The audit's runs use the substring scorer: case-insensitive, with commas stripped from the agent text. An empty list passes automatically.
- `nl_assertions` are not evaluated for airline at this version: `reward_basis` is `DB|COMMUNICATE` on all 50 tasks.
- Any trajectory that reaches the same end state passes.
- `get_pydantic_hash` serialises with sorted dict keys and **keeps list order**.
- New reservation ids come from a fixed sequence (`_get_new_reservation_id`).

## Conventions from block 1

Apply these. A departure needs a stated reason.

1. **Order versus content.**
   - **2h (order only).** An effect that exists only because of order is filed under 2h, never under 4c. Order means the order of WRITE calls, or the order of entries in a list argument (passengers, `payment_methods`). Block 1 relabelled 8/4c and 20/4c to 2h, and set 23/4c to 0 as a double count of 23/2h.
   - **2h (content that follows from order).** A content difference that arises only from the execution order of WRITEs is still an order effect, so it is 2h. Example: a bag fee that depends on whether a cabin change came first.
   - **4c (open content choice).** A content choice the scenario leaves open is 4c. Examples: which payment method, how an amount is split, insurance yes or no, which of two equal flights, which date a phrase means. Block-1 precedents: 32/4c and 44/4c.
   - **Chronological flight-list order** inside a call is not counted (block-1 filter).
   - **One root cause is counted once.** When a reviewer filed one root cause under both 2h and 4c, keep the right check. Set the other to 0 with the note "double count of <task>/<check>".
   - **Two independent root causes** on one task are counted separately: for example, an open amount split (4c) and an unpinned list order (2h).
2. **2k.**
   - **Unenforced** means a plausible agent behaviour that breaks the assertion still reaches the target hash and every required string.
   - **A refusal of a WRITE is enforced by the hash**, because doing the write changes the DB. So it is not 2k.
   - **These are 2k = 1 (medium)** when `communicate_info` does not cover them: a requirement to inform, to state a reason, or not to make a verbal offer (an offer with no write). This applies also on empty-answer tasks. Block 1 aligned tasks 26 and 28 with task 46 on the verbal-offer pattern.
3. **4b** is high if no policy-compliant trajectory reaches the target hash. Otherwise it is medium.
4. **4e.**
   - A typo is 0. Precedent: 8/4e, "Sophia Silvia" against the reference "Silva".
   - A contradiction is 1. Precedent: 23/4e, where an assertion names a flight and date the reference does not book.
5. **4d.** One reading of a scenario phrase must be applied to every task that uses it. Mark the reading as an assumption in the note.
6. **Severity** follows `checklist.md`. Do not invent likelihood levels. If an issue is real but improbable, keep the checklist severity and say so in the note.
7. **Evidence must let a stranger reproduce the verdict:** the file and field, the ids, the quote and the computation.
   - Recompute every amount a defect depends on.
   - For a claim that two end states hash differently, replay both and quote the 8-hex prefixes, unless the difference is evident from one stored field.

## Per part

### Part `2k`

- **Defect rows to verify:**
  - batch 5: 2/2k, 4/2k, 5/2k;
  - batch 6: 12/2k, 13/2k;
  - batch 7: 27/2k, 29/2k;
  - batch 9: 38/2k, 41/2k.
- **Re-review disagreement:** 33/2k is 1 in the re-review and 0 in batch 8. Decide which holds.
- **False negatives:** check every 2k = 0 row on the 30 tasks against the same rule. Pay particular attention to the empty-answer tasks whose 2k is 0: 0, 6, 31, 34, 36, 43, 45, 47, 49.

### Part `order`

- **Defect rows to verify:**
  - batch 6: 14/2h, 14/4c, 17/2h, 17/4c;
  - batch 7: 25/4c, 29/2h, 29/4c.
- **Re-review disagreements:** 33/2h and 33/4c are 1 in the re-review and 0 in batch 8. Decide which holds.
- **Undecided zeros:**
  - 24/4c: gift-card order; nl 3 names the larger card first.
  - 31/4c: an upgrade-first route with a net cost of 81, under the user's $100 limit.
  - 33/4c: "move back" read as 2024-05-21 or as 2024-05-23. The reference's own READ searches 05-21; its WRITE books 05-23.
  - 43/4c and 47/4c: an upgrade-then-cancel route (batch 10).
  - 39/2h: kept at 0 by batch 9, because the cause is counted under 4b.
- **Specific points:**
  - 17/2h depends on the free-bag allowance following the cabin at the moment the bags are added. Verify this against `policy.md` and against what `update_reservation_baggages` stores, given what the agent passes.
  - Apply convention 1 to every double count (14, 17, 29).
  - For false negatives, check list order in every rest-task `book_reservation` (passengers, `payment_methods`) against the block-1 filter.

### Part `other`

- **Defect rows to verify:**
  - 2/4d (batch 5);
  - 39/4b, high (batch 9; the re-review agrees).
- **Mechanical rows:** 2a and 2b of the 16 empty-answer tasks (0, 2, 4, 5, 6, 13, 27, 31, 34, 36, 38, 41, 43, 45, 47, 49).
  - Verify in bulk from `tasks.json` and `static_scan.csv` that the reference leaves the DB unchanged (or is READ-only) and that `communicate_info` is empty.
  - The evaluator path of the scan was verified in block 1 (`results/skeptic_report.md`). Re-check the data, not the method.
  - Confirm that no other mechanical check (1a, 1b, 1c, 2i, 3d, 3f, 5a) fires on a rest task.
- **Undecided:**
  - **2/4d = 1 against 38/4d = 0.** These are the same reservation family, read two ways. In task 2 "the last reservation you made", and in task 38 "most recent reservation". By `created_at`, SDZQKO is newer, but the delayed flight is in 4OG6T3. Settle one reading and apply it to both tasks.
  - **27/4e.** nl 2 ("user can receive compensation") against the policy and the reference, which give none.
  - **39/4e.** The purpose says "only cancel flights that are eligible for refunds", but the reference cancels MSJ4OA. Decide whether this is a separate contradiction or the same cause as 39/4b.
  - **35/4e.** The typo `credit_card_907483` (convention 4).
  - **25/1d.** The static scan flags reference arguments that appear only in `unknown_info` (`Ivan|Smith`); batch 7 kept 1d = 0.
- **Re-review rows for 35 and 39** (the checks of this part): confirm agreement or settle the difference.
- **2g:** only tasks 14 and 18 have `communicate_info` among the rest tasks. Confirm that 2g = 0 holds for them under the substring rule.

## Output (part `<X>` = `2k`, `order` or `other`)

1. **`results/skeptic_verdicts_rest_<X>.csv`**, with the header `task_id,check,skeptic_ok,note`:
   - one row per defect=1 row you verified: `skeptic_ok` = 1 if it holds, 0 if it does not;
   - one row per undecided or false-negative row you escalate or keep, with `skeptic_ok` empty and a note starting "should be defect=1 <severity>: ..." or "stays 0: ...";
   - one row per re-review disagreement, with a note starting "re-review prevails: ..." or "batch prevails: ...".
2. **`results/review_overrides_rest_<X>.csv`**, with the header `task_id,check,defect,severity,evidence,note`:
   - the corrected final rows: rejected rows set to 0 or re-filed, severity changes, escalations, double-count zeroes, and adjudicated re-review rows;
   - one row per (task, check) you change, none for rows you leave as they are;
   - the audit-log builder reads these rows last.
3. **`results/skeptic_report_rest_<X>.md`**:
   - a verdict table: row; holds, fails, re-filed or escalated; one line why;
   - the conventions you applied and the recomputations;
   - the defective rest tasks according to your family's rows, before and after your pass;
   - what you could not verify.

Write in English and impersonally: no names of people, and no mention of which model or tool wrote the files. Use ASCII and quote CSV fields that contain commas.

In your final message, return:
- the counts: reviewed, confirmed, rejected, re-filed, escalated;
- the list of rejected and escalated rows;
- open questions.
