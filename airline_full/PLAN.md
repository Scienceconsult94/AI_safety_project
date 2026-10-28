# Airline, whole domain, and the open items of blocks 1 and 2: pre-registration

Written and committed on 2026-10-28, before any result of the work below was produced or read. The pinned benchmark, models, run settings and checklist are those of block 1 (`checklist.md`, `schema.md`, `sample.json`) and block 2 (`block2/PLAN.md`); only the differences are written here. Deviations are appended at the end with a date.

## 1. Questions

- **Q1.** Do the block-1 estimates, made on 20 sampled tasks, hold on the whole domain? The 30 unsampled tasks go through the same checklist, the same reviewers' brief, the same probes and the same agent runs.
- **Q2 (check 2j).** Does the choice of communicate scorer change verdicts? Every run here used the substring scorer; the v2.0.0 default is a semantic judge.
- **Q3 (task 32).** Did the payment sentence added in v2 ("Any charge or refund should go to your Visa credit card ending in 1777.") cause the ground-truth failures of task 32 under the v2.1 text?
- **Q4 (judge).** Are the judge's "met" verdicts on judge-only assertions in the fresh v2 passes correct? Block 2 hand-checked only the recorded conversations; 35 of 66 fresh passes contain at least one judge-only assertion that nobody checked.
- **Q5 (block 2 on the whole domain).** Do the block-2 results H3 (re-scoring recorded conversations) and H5 (pass^3 under v1 and v2) hold on the 30 unsampled tasks?

## 2. Protocol

**Task sets.** Sample: the 20 ids of `sample.json` → `task_ids` (unchanged; every block-1 number stays as published). Rest: the other 30 ids of `population_ids`: 0, 2, 4, 5, 6, 12, 13, 14, 15, 17, 18, 24, 25, 27, 29, 30, 31, 33, 34, 35, 36, 38, 39, 40, 41, 42, 43, 45, 47, 49. Whole domain: all 50.

**Q1, static and probe rows.** `results/static_scan.csv` already covers all 50 tasks; its mechanical rows (1a, 1b, 1c, 2a, 2b, 2i, 3d, 3f, 5a) are generated for the rest exactly as for the sample. Reviewer rows (1d, 2g, 2k, 4a, 4b, 4c, 4d, 4e, and 2h for the seven rest tasks in `results/probe_2h.csv`) come from six reviewer batches of five tasks each, written to `results/review_batch_5.csv` … `review_batch_10.csv` with notes in `.md`, under the brief `airline_full/review_brief.md`, which restates the conventions of batches 1–4:

| batch | tasks |
|---|---|
| 5 | 0, 2, 4, 5, 6 |
| 6 | 12, 13, 14, 15, 17 |
| 7 | 18, 24, 25, 27, 29 |
| 8 | 30, 31, 33, 34, 35 |
| 9 | 36, 38, 39, 40, 41 |
| 10 | 42, 43, 45, 47, 49 |

**Q1, agent runs.** `scripts/runs/run_rest30.ps1` with the block-1 settings (Haiku 5.5 as agent and user, `llm_args {}`, substring scorer, seed 300, max concurrency 3, timeout 900): Pass^3 on the 30 tasks and the ground-truth agent on the 27 of them with reference actions. `scripts/agent_rows.py --ids rest` turns them into rows (1e, 1f, 5c, 5e, 5f); every failed or flipped trajectory is read by a trajectory reviewer for 4f and 5d (`results/review_agent_rest30.csv`), as in block 1.

**Q1, review stages.** A blind second reviewer re-labels three rest tasks drawn now with `random.Random(20261028).sample(rest, 3)`: tasks **33, 35, 39**; agreement is computed as in block 1. The adversarial review of every medium or high row, which block 1 applied, runs only if the account owner approves it; otherwise the rest rows are reported as not adversarially reviewed, separately from the sample rows, and this plan records the decision as a deviation.

**Q1, outputs.** `airline_full/audit_log.csv` holds all 50 tasks (same schema; the sample rows are the published ones). `airline_full/summary_numbers.md` reports the sample, the rest and the whole domain side by side; the root `audit_log.csv` and `summary_numbers.md` stay the pre-registered block-1 record.

**Q2.** `scripts/probe_2j.py` re-scores the communicate part of every recorded simulation on the stock airline tasks with non-empty `communicate_info` (block-1 Pass^3 and ground-truth runs, the Sonnet run, the rest runs) under the semantic scorer with judge `anthropic/claude-haiku-5-5` (the checklist's 2j method; the stock default judge is an OpenAI model and is not used). Three independent judge passes per fact; the semantic verdict is the majority. The same scorer is applied to the empty trajectory of every task with non-empty `communicate_info`. A task gets a 2j defect (medium) when the semantic and substring verdicts differ on any trial.

**Q3.** `scripts/v2/run_32_cf.py`: the ground-truth agent on task 32 of the v2 task set, under the full v2 protocol, 10 trials per arm. Arm A: the v2.1 text as published. Arm B: the same text without the sentence "Any charge or refund should go to your Visa credit card ending in 1777." Everything else is identical. Rule: the sentence is taken to cause the failures if the pass count of B exceeds that of A by at least 3 of 10.

**Q4.** From the fresh v2 runs of block 2 (`results/v2/rescore_fresh.csv`), take every assertion of class negative or communication (`block2/nl_assertion_classes.csv`) in a simulation with V2 reward 1.0 that the judge marked met. Draw 20 with `random.Random(20261028)`, negative first (all of them if fewer than 10), communication for the rest. Two blind readers label each item from the judge-visible transcript without the judge's verdict. Agreement with the judge is reported per reader and for both together.

**Q5.** `scripts/v2/rescore.py --set rest30` re-scores the rest Pass^3 and ground-truth runs under every block-2 configuration, with the replay gate. `scripts/v2/run_v2.py --part pass3_rest30` and `--part gt_rest30` run the 30 tasks under the full v2 protocol (tasks v2; the only text fix among the rest is the assertion typo of task 35).

**Statistics.** Wilson 95% intervals; exact binomial tests where a comparison is paired; no new significance claims beyond the rules above.

**Budget.** Own estimate about $6: rest runs about $2, v2 rest runs with the judge about $2.5, task-32 arms about $1, check 2j and the re-score judge below $0.5. The readers make no API call.

## 3. Predictions

| id | prediction | measured by |
|---|---|---|
| P1 | The whole-domain share of defective tasks lies inside the sample's 95% interval [0.70, 0.97]. | `airline_full/summary_numbers.md` |
| P2 | The whole-domain share without the documented no-op class (2a, 2b) lies inside the sample's interval [0.58, 0.92]. | same |
| P3 | The whole-domain share from static and probe rows alone lies inside the sample's interval [0.43, 0.82]. | same |
| P4 | Haiku passes more of the rest tasks 3/3 than the sample's 0.60, because 16 of the 30 rest tasks are no-op tasks (7 of 20 in the sample). | rest Pass^3 |
| P5 | Under the semantic scorer the empty trajectory passes exactly the same 23 tasks; no task with required information passes. | Q2 |
| P6 | On the recorded runs the semantic and substring verdicts differ on at most 2 trials in all, because the recorded answers state the numbers explicitly. | Q2 |
| P7 | Arm B passes at least 3 more of 10 than arm A. | Q3 |
| P8 | Each blind reader agrees with the judge on at least 18 of 20 items. | Q4 |
| P9 | On the rest runs the deterministic v2 switches (canonical hash, word-boundary communicate check) change no reward. | Q5 |
| P10 | On the rest tasks, Haiku's pass^3 under v2 differs from v1 by at most 0.10. | Q5 |

## Deviations

- 2026-10-28, before any rest row was written: the account owner approved the adversarial review for the rest rows, as block 1 applied it (static-phase rows after batches 5-10; agent-run rows after the trajectory review).
- 2026-10-28, Q4: the first labelling round was only partially blind. `handcheck_fresh/items.md` stated that the pool consisted of judge-met assertions, and `items.csv` carried the class, so a reader could infer the judge's verdict (reader A flagged it). Both round-1 readers labelled all 20 items met. Round 2 re-labels the same 20 items mixed with 10 judge-unmet decoys from the same fresh runs, in a random order, without the pool statement and without the class, by two new readers. Round 2 is the result that decides P8; round 1 is reported as partially blind.
- 2026-10-28, Q3, before the result of either arm was read: the two task-32 arms run as parts `cf32_A` and `cf32_B` of `scripts/v2/run_v2.py` (commit df49d4c) instead of a separate `scripts/v2/run_32_cf.py`. The arms, the protocol (ground-truth agent, tasks v2, full v2 protocol), the 10 trials per arm and the rule are unchanged.
- 2026-10-28, Q1, review stages: the approved adversarial review of the rest static rows is split by check family (2k; 2h and 4c; the remaining checks and the mechanical rows) rather than by task, so that one mechanism is judged the same way on every task (`airline_full/skeptic_brief.md`, committed before any verdict).
- 2026-10-28, after all review parts: a consistency pass across the parts and the two blocks was added (`results/consistency_pass.md`). It changed one block-1 row. 22/2h went from 0 to 1 medium: it has the same reservation, reference writes and mechanism as rest 17/2h. A second order probe (`scripts/probe_2h_paths.py`), in which an earlier write can change the arguments of a later one, found it. The block-1 headline stays 18/20; its count from static and probe rows moves from 13/20 to 14/20. The row has no adversarial verdict of its own.
- 2026-10-28, Q1, agent-run rows: the adversarial review rejected 29/1e as unclear. The dispute was settled with a pre-registered user-simulator probe (`results/probe_29/protocol.md`, committed before the model call), the procedure block 1 used for 32/1e. Result: REFUSE 1 of 10, so 1e = 0.
