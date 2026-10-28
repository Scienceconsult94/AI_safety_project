# Consistency pass across the review parts and the two blocks (airline, all 50 tasks)

Done after the four parts of the adversarial review of the 30 rest tasks (2k, order, other, agent rows). The rule is that one mechanism gets one reading and one check across block 1 (the 20 sampled tasks) and the rest. Changes are recorded in `results/review_overrides_consistency.csv`, which `scripts/build_audit_log.py` reads last.

## 1. Write paths the first order probe could not see

`scripts/probe_2h.py` permutes the reference writes with their arguments held fixed. Two compliant paths change the arguments or the number of calls, so the order part of the review found them by hand on rest tasks 17 and 33. `scripts/probe_2h_paths.py` replays both on all 50 tasks (`results/probe_2h_paths.csv`, no model call):

| mechanism | tasks where the hash changes | label |
|---|---|---|
| bags added before a cabin change: the free allowance follows the cabin at the moment of the write, so one bag becomes non-free (+$50) | 17 (rest), 22 (sample): hash edc62003 against 37ea6df3 | 17/2h = 1 medium (order part). **22/2h: 0 -> 1 medium** (this pass) |
| one flight change split into two calls: same flights and cabin, a different payment ledger | 15, 16 (cabin and outbound), 33 (outbound and return) | 33/2h = 1 medium (order part). 15 and 16 stay 0 |

- **Task 22** has the same reservation (FQ8APE), the same three reference writes and the same mechanism as task 17.
  - The block-1 probe could not see the path. Batch 3 had flagged it as "uncertain" in its 22/4c note.
  - In 22 the user lists the upgrade before the bags; in 17 the bags come first and "in this order". So in 22 the failing path needs the agent to take the bags first. Severity is medium, as on every 2h row.
  - The row has no adversarial verdict of its own (`skeptic_ok` empty). The order part stated that 22 "would be 1" under its reading of 17 (`results/skeptic_report_rest_order.md`, open question 2).
  - Effect on block 1: the sample headline stays 18/20, because 22 was already defective through 5d. The static-only count goes from 13/20 to 14/20, and sample 2h rows from 3 to 4.
- **Tasks 15 and 16** (the same reservation and reference) state one change. Splitting it would put in an intermediate state that the user never asked for: first a downgrade on the old flights, then the flight change. Both stay 0. Block 1 has no 2h row for 16, a single-write task, and the order part reached the same reading for 15.

## 2. Upgrade routes

An upgrade route is an upgrade the user never asked for, which would make a refused cancellation or change possible. Both blocks read it as an unrequested write that does not fit the scenario, so 4c = 0:
- block 1: 19/4c;
- rest: 0, 31, 35, 39, 41, 43, 47 (`results/skeptic_verdicts_rest_order.csv`).

The opposite reading would add seven rest 4c rows. Of those seven tasks, only 35 is not defective already, so the whole-domain count would rise from 44/50 to at least 45/50. The block-1 tasks on the same route (19, 46, 48) were not re-reviewed under that reading.

## 3. One root cause, several checks

- **Static double counts removed** by the order part:
  - 14/4c, 17/4c and 29/2h are counted under 14/2h, 17/2h and 29/4c.
  - Task 25 keeps two rows for two root causes: the open amount split (4c) and the unpinned payment-list order (2h).
- **Task 39 has 4b (static) and 1e (agent run).** Both describe one cause: no compliant path reaches the reference. The rows stay because the two checks use different methods, one reading the reference against the policy and one observing the ground-truth agent. The per-check table lists 39 under both checks; the defective-task count counts it once. Block 1 has no case of one cause under a static check and 1e: task 32 carries 4c for the refund method and 1e for the $100 clause.

## 4. A disputed 1e row settled the block-1 way

The agent-row part rejected 29/1e (0, unclear), because every recorded refusal followed an agent error. Block 1 settled the same kind of dispute on 32/1e with a pre-registered simulator probe, so the same procedure was used here (`results/probe_29/`):
- protocol committed before the call;
- 10 samples;
- two blind classifications.

When the route is stated plainly, the simulator refuses it in 1 of 10 samples. 29/1e = 0 (cutoff: REFUSE <= 5).

## 5. Corrections that change no value (agent-row part)

- **Transfers.** In airline runs a transfer call does not end the episode; only the `intake` domain has stop tools. 24 t1 succeeded after a transfer, so observation 4 of `results/review_agent_rest30.md` ("those episodes cannot reach the target") does not hold.
- **Trajectory classes on the rest:** A 10, B 5, D 4, C 0 (the review had 8/5/6/0). Check 4f stays 0 on every rest task.
- **Persona.** The block-1 persona rule was applied to 24, 33, 39 and 42, which ran with `priya_patil`.

## 6. Disclosures from the review parts

- The part "other" opened `airline_full/PLAN.md` once, before it read the list of files it must not open.
- The parts 2k, other and order each ran read-only git commands inside the pinned clone. The index timestamp is unchanged, no lock file remains, and no file changed.
- The agent-row part made no model call, ran no git command and changed nothing under `tau2-bench/`.
- None of these changes a verdict. All reviewers, adversarial reviewers and readers in this audit are language-model reviewers, not people.
