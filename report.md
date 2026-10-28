# Report: validation audit of tau2-bench airline and the v2 protocol

Target: tau2-bench, tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`, domain airline (50 tasks). All numbers below are copied from the generated files `summary_numbers.md` (block 1) and `block2/summary_v2.md` (block 2); intervals are 95% Wilson. Where this report interprets, it says so.

## 1. Question

An agent benchmark is an examination: a task text, a hidden reference, a scorer. Its headline number, the pass rate, is trusted as a measure of the agent. This project checks the examination itself. For each task it asks whether the task is solvable as written, whether the scorer accepts what it should and rejects what it should not, whether anything leaks, whether the specification is clear, whether the result is repeatable, and whether the reporting matches the code.

## 2. Method

**Checklist.** 52 checks in six categories (`checklist.md`): 1 solvability, 2 scoring validity, 3 isolation and leaks, 4 specification clarity, 5 determinism, 6 reporting. Each check names its method: static reading of code and data, a mechanical probe, or an agent run.

**Sample.** 20 of 50 tasks, drawn with a fixed seed before any run (`sample.json`). Static scans that cost nothing were run on all 50.

**Verdicts.** One row per task and check in `audit_log.csv`, validated against `schema.md`. Every medium or high defect row went through an adversarial review that tried to overturn it; 11 of 15 contested rows survived, 4 were withdrawn. Three tasks were re-labelled blind by a second reader: 27/29 agreement with the original labels, 29/29 with the corrected ones.

**Agent runs.** The audited model, `claude-haiku-5-5`, as agent and as user simulator, 3 trials per task on the 20 sampled tasks; the ground-truth agent (`llm_agent_gt`, which sees the reference actions) on the 16 tasks that have reference actions. The runner settings are recorded in the results files and were reused unchanged in block 2.

**Block 2.** Pre-registered hypotheses and rules (`block2/PLAN.md`), then: a scorer overlay with three independent switches (canonical DB hash; word-boundary communicate check; free-text assertions enforced through a 3-vote judge), text fixes to six tasks (`block2/task_fixes.md`), an offline re-score of the 76 recorded conversations under one switch at a time, and fresh runs under the full v2 protocol. Gates before any v2 number: the stock scorer must reproduce every recorded reward (76/76, then 85/85 on the fresh runs); each switch must flip a perturbed real trajectory (4/4). An adversarial review of the design preceded the paid runs and one of the results followed them; both are in the repository with the changes they forced.

## 3. Block 1: what the audit found

Table 1. Headline shares (sampled tasks).

| quantity | share |
|---|---|
| defective tasks (≥1 confirmed medium/high defect) | 18/20 = 0.90 [0.70, 0.97] |
| defective by static reading and probes only | 13/20 = 0.65 [0.43, 0.82] |
| defective by agent-run checks only | 9/20 = 0.45 |
| defective by agent-run checks, excluding user-simulator deviations | 6/20 = 0.30 |
| defective excluding the documented pass-by-doing-nothing class | 16/20 = 0.80 |
| defective excluding every defect that derives from that design | 11/20 = 0.55 |
| tasks an empty trajectory passes, whole domain | 23/50 = 0.46 [0.33, 0.60] |

Table 2. Sampled tasks with a confirmed defect, by category.

| category | share |
|---|---|
| 1 solvability | 1/20 |
| 2 scoring validity | 12/20 |
| 3 isolation and leaks | 0/20 (rule of three: ≤ 0.15) |
| 4 specification clarity | 4/20 |
| 5 determinism | 8/20 |
| 6 reporting | 0/20 at task level; one benchmark-wide documentation mismatch (I1) |

The main mechanisms, each with a reproduction in the repository:

- **A pass for doing nothing (checks 2a, 2b).** 23 of 50 tasks have a reference that leaves the database unchanged and no required output string. The default scorer compares the end-state hash and the required strings, so an empty conversation scores 1.0. The benchmark's documentation describes the refusal case as the intended outcome of these tasks; the audit records the consequence, not a hidden bug: the exam cannot distinguish an agent that correctly refuses from one that does nothing.
- **An end-state hash that depends on list order (2h, I3).** The DB hash serialises lists in their stored order. Reordering the reference actions, with the same final state, changes the hash in 24 of 78 tested permutations; adding passengers or payment methods in a different but equally valid order fails a correct solution.
- **A substring check that matches by accident (2g, I4).** Required strings such as "1000" or "327" are matched as substrings after commas are stripped, so they are found inside unrelated numbers and identifiers.
- **Requirements that no scorer reads (2k, 6 tasks).** The free-text `nl_assertions` state obligations that the default evaluation never checks; the documentation says the CLI evaluates them by default, the code at this tag does not (I1).
- **A wrong reference answer (I6).** Task 7's required total, 1628, sums four reservations including two in the past; the task asks for the upcoming ones (708). Every agent that answered correctly failed.
- **A scenario that forbids the reference (1e, I8).** Task 32's scenario caps the user at a $100 charge while the reference path charges $396 and refunds $510 in two steps. A counterfactual probe of the user simulator with the exact reference figures produced 10 refusals in 10 samples.
- **A user simulator that leaves its script (5d, 7 tasks).** In 7 of the 20 tasks the simulator volunteered facts, invented constraints or changed its request across trials, which is the largest single source of run-to-run variance.

Table 3. Agent runs (block 1).

| quantity | value |
|---|---|
| tasks passed 3/3 (tau2 pass^3) | 12/20 = 0.60 [0.39, 0.78] |
| passing trials (tau2 pass^1) | 44/60 = 0.73 |
| tasks solved in 0/3 trials | 3/20 (tasks 7, 32, 44) |
| unstable tasks (1 or 2 of 3) | 5/20 |
| ground-truth agent reaches the target state | 11/16 |
| ground-truth agent fails on | tasks 7, 16, 23, 32, 44 |

Note on labels: `summary_numbers.md` reports "pass^1 = 0.80" as the share of tasks whose first trial passes (16/20); tau2's pass^k for k = 1 is 44/60 = 0.73. The two coincide for pass^3.

## 4. Block 2: the v2 protocol and what it changed

### 4.1 What v2 is

Three switches, each on its own, plus six task-text fixes:

| switch | what it changes |
|---|---|
| `hash_canon` | the DB is serialised in a canonical form: order-free collections sorted, new identifiers replaced by content-derived ones, amounts rounded to cents; flight order kept |
| `comm_boundary` | required numbers must appear as whole tokens; words on word boundaries |
| `nl_enforce` | `nl_assertions` enter the reward; a 3-vote judge (`claude-haiku-5-5`) sees the transcript with tool calls, assertions are numbered and matched by index, unparseable replies are re-asked once, an undetermined verdict is reported with bounds instead of guessed; an empty trajectory fails by rule |

Task fixes (`block2/task_fixes.md`): task 7 (reference total 1628 → 708), task 32 (the $100 cap rewritten as a net cap with an explicit confirmation step; a payment-method sentence added), task 44 (per-segment wording, payment method, required total), task 23 (two assertion texts corrected), tasks 8 and 35 (typos in assertions). Reference actions were never edited; the generator asserts that.

### 4.2 Verdicts on the pre-registered hypotheses

| hypothesis | verdict | evidence |
|---|---|---|
| H1 no-op pass | supported for the rule part; the judged part is a protocol choice | empty trajectory 23/50 under the stock scorer → 0/50 under v2; a refusal-only agent, judged, still passes 14/23 of the no-op tasks (17/23 without the process-type assertions), which the benchmark documents as intended |
| H2 order-sensitive hash | supported | permutations with a differing hash 24/78 → 4/78; the remaining 4 change the outcome (refund before upgrade, flight change before cabin change) |
| H3 recorded conversations re-scored | deterministic switches: no observed effect; judge: 1 flip; criteria text: 1 flip | 76 conversations, flips under the full v2: 2 (task 9 trial 0, 1 → 0, by the judge, on an assertion the agent did not meet; task 7 trial 0, 0 → 1, by the corrected total). 0 of 20 DB mismatches were order-only; 0 communicate checks flipped |
| H4 ground-truth agent passes the fixed tasks | task 7 supported (4/4); task 44 supported with caveat (3/4); task 32 **failed** (1/4) | see 4.4 |
| H5 agent pass^3 differs under v2 | no difference detected | tasks passed 3/3: 12/20 in both runs; pass^1 0.73 → 0.78; on the 15 tasks nothing was changed on, 40/45 trials passed in both runs while 6 of the 45 trial slots changed outcome |

### 4.3 Separating the effects on the fresh conversations

The 85 fresh conversations were re-scored under every protocol, so the text effect and the scorer effect can be read on identical trajectories:

| agent | conversations | stock scorer, tasks v1 | stock scorer, tasks v2 | full v2 |
|---|---|---|---|---|
| audited agent, 20 × 3 | 60 | 47 | 47 | 47 |
| ground-truth agent, 16 × 1 | 16 | 12 | 13 | 13 |
| ground-truth agent, 3 × 3 on tasks 7, 32, 44 | 9 | 3 | 6 | 6 |

The three scorer switches changed no fresh reward (last two columns equal on every row). The corrected reference total of task 7 accounts for the four ground-truth gains. Enforcing the *original* assertion texts would have failed one correct ground-truth conversation on task 23; the corrected text passes it, which is what that fix was for.

### 4.4 The task fixes, one by one

- **Task 44** (block 1: 0/3 and ground truth 0/1; v2: 3/3 and 3/4). In block 1 no conversation executed any upgrade: two escalated to a human over cancellation requests, one over a total quoted without one reservation. Under the per-segment wording all six three-trial conversations execute the three upgrades, and then still transfer to a human over the cancellation request the scenario contains; the single-trial ground-truth run transfers first and fails. The fix moves the upgrades ahead of a conflict it does not remove.
- **Task 7** (0/3 → 0/3; ground truth 0/1 → 4/4). The corrected total passes every conversation that answers correctly. The audited agent still fails the task for a different reason: it refuses the upgrade that the reference performs.
- **Task 32** (0/4 → 2/7). The rewritten budget clause no longer blocks the two-step path: a pre-registered probe with the exact reference figures went from 0/10 acceptances to 8/10, and two live conversations completed the path. But in all seven fresh conversations the agent stated that refunds go to the original payment method; the policy's flight-change section lets the customer name the card, and the tool refunds to the payment method passed in the call, so the statement is wrong, and the ground-truth agent made it while holding the reference arguments. The added sentence "any charge or refund should go to your Visa" gave the simulator a preference to defend, so an error that was harmless under the old text now fails the task. The pre-test, whose counterfactual message already named the refund destination, never exercised that branch. H4 is reported as failed for this task; the sentence changed the task's difficulty in a way the pre-registration did not anticipate.
- **Task 23** (3/3 → 1/3). Not a scorer effect: the agent changed the flights on the existing reservation instead of cancelling and rebooking three. The reference needs the simulator to volunteer a three-way split of the booking, which it did in 3/3 block-1 conversations and 1/3 fresh ones (the determinism defect 5d). The task's own edit touched only its assertion texts.

### 4.5 The judge as an instrument

The judge is the agent's own model, which is a self-evaluation risk. What was done about it: three votes per assertion; transcript with tool calls (the stock transcript view hid tool-call arguments and produced a false failure on task 9 trial 1, issue I9); every reward-changing, process-type and communication-type verdict on the recorded conversations hand-checked by two readers, 46/46 agreement with the judge; verdicts reported with the number of determined ballots. The results review found a parser gap: the upstream JSON extractor rejects a reply that is a bare JSON array, which the judge model returned in 53 of 610 replies, and those ballots had been dropped. The parser was fixed; an offline re-parse of the discarded replies recovered 32 ballots and changed no majority verdict, so the cached rewards stand. Six passes rested on one or two ballots and are named in `summary_v2.md`. Fresh-run verdicts were not hand-checked; 35 of the 66 fresh passes contain at least one assertion only the judge decides, and no fresh failure rests on the judge alone.

## 5. Issue candidates

Drafted in `issues_draft.md`, none filed:

| id | summary |
|---|---|
| I1 | documentation says the CLI evaluates `nl_assertions` by default; the code at this tag does not |
| I2 | `calculate` runs `eval` on a character-whitelisted expression |
| I3 | the DB hash depends on list order and on generated identifiers, so equally valid solutions hash differently |
| I4 | short numeric required strings match by accident under the substring scorer |
| I5 | default `llm_args` set a temperature that current Anthropic models reject with HTTP 400 |
| I6 | task 7's required total sums past reservations the task excludes |
| I7 | the user simulator departs from its scenario in 7 of 20 sampled tasks |
| I8 | task 32's scenario forbids the reference path |
| I9 | the assertion judge's transcript view hides tool-call arguments; verdict parsing has no fallback |
| I10 | the assertion evaluator and the JSON extractor fail on a bare top-level JSON array, which the judge model returns in about 9% of replies |

## 6. What the numbers mean

Two facts stand side by side. The examination has reproducible faults: a pass for doing nothing on 23 of 50 tasks, an end-state check that fails valid solutions, a string check that passes by accident, a wrong reference answer, a scenario that forbids its own reference, requirements nobody scores, a simulator that improvises. And the agent's headline number barely moves when the examination is repaired: pass^3 0.60 in both runs, pass^1 within the noise floor. The leaderboard cannot show what is wrong with the exam. Finding it took a checklist applied to the procedure, probes with known answers, and reviews whose job was to overturn the findings.

The repair itself is instructive. The deterministic faults exist (they fire on perturbed trajectories) but did not flip a single recorded conversation, because the recorded agents happened not to hit them. The one fix that failed, task 32, failed because a sentence added to make the scenario consistent with the reference exposed a second agent error that the pre-test could not see. Both say the same thing: an examination has to be validated as an instrument, with pre-registered expectations and adversarial review, before its numbers are read.

## 7. Limits

One domain of one benchmark; 20 sampled tasks; one agent model and one simulator model; a judge from the same model family; the 30 unsampled tasks' assertions unaudited; the refusal pass is documented as intended, so v2 is a stricter alternative protocol rather than a bug fix; dollar figures are own estimates at an assumed price. Single-trial ground-truth runs flipped on 4 of 13 unchanged tasks between the two runs, so ground-truth totals are read against that floor.

## 8. Reproducibility and cost

Every number is rebuilt by the command sequences in `STRUCTURE.md`; the judge stages replay from cached votes without a model call. Provenance stamps on every v2 output record the overlay commit and a dirty-tree flag; the live runs record the runner configuration and its empty diff against block 1. Spend, own estimate from token counts: block 1 about $1.36, block 2 about $2.27 (`cost.md`).

## 9. Open items

Not done, candidates for a next iteration: a counterfactual ground-truth run on task 32 without the payment-method sentence, to isolate its effect; a blind hand-check of about 20 fresh judge-only verdicts; the assertions of the 30 unsampled tasks; the same audit on a second domain.
