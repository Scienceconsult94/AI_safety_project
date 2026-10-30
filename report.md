# Report: validation audit of tau2-bench (airline, retail) and the v2 protocol

Target: tau2-bench, tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`, domains airline (all 50 tasks; 20 sampled first, the other 30 afterwards) and retail (all 114 tasks). Most numbers below are copied from the generated files `summary_numbers.md` (block 1), `block2/summary_v2.md` (block 2), `retail/summary_numbers.md` and `retail/comparison.md` (retail) and `results/null_agent/tau2_null_agent.md` (null agent). Sections 6, 7, 11 and 13 also use `results/null_agent/external.md`, `results/null_agent/hal_check.md`, `strong_vs_weak/summary.md`, `cost.md` and `airline_full/summary_numbers.md`, and some counts come from the review reports in `results/`. Intervals are 95% Wilson. Where this report interprets, it says so.

**Who did what.** The audit is the author's work, carried out with Claude Code (language-model assistants). The author chose the question and the benchmark, set the scope (every airline and retail task), wrote the rules the assistants worked under (the checklist, the severity definitions, the headline rule that counts the pass for doing nothing on its own line, the review and adversarial-review procedures), took the definitional decisions and settled the disputed points, and read, checked and corrected every file in this repository. The assistants worked under the author's direction. The author commissioned each step (the drafts of the texts and scripts, the audit-log entries, the reviews, re-reviews and paid agent runs), decided what was run and when, and accepted, corrected or sent back what came back. Wherever this repository says that a reviewer, adversarial reviewer or reader was a language model, that is what it means.

## 1. Question

An agent benchmark is an examination: a task text, a hidden reference, a scorer. Its headline number, the pass rate, is trusted as a measure of the agent. This project checks the examination itself. For each task it asks whether the task is solvable as written, whether the scorer accepts what it should and rejects what it should not, whether anything leaks, whether the specification is clear, whether the result is repeatable, and whether the reporting matches the code.

## 2. Method

**Checklist.** 49 checks in six categories (`checklist.md`): 1 solvability, 2 scoring validity, 3 isolation and leaks, 4 specification clarity, 5 determinism, 6 reporting. Each check names its method: static reading of code and data, a mechanical probe, or an agent run. The retail audit added two checks (`retail/PLAN.md`): 2m, written into the plan before the audit began, and 1g, added after the first review pass, when four reviewers had independently found the same fault in a tool.

**Sample.** 20 of 50 tasks, drawn with a fixed seed before any run (`sample.json`). Static scans that cost nothing were run on all 50. Section 13 audits the other 30 tasks with the same pipeline.

**Verdicts.** One row per task and check in `audit_log.csv`, validated against `schema.md`. Every medium or high defect row went through an adversarial review that tried to overturn it: the 27 rows from reading and probes all held; of the 15 rows from the agent runs, 11 held and 4 were withdrawn, and one of the four (task 32, check 1e) was restored by a later probe (`results/skeptic_report.md`, `results/skeptic_report_agent.md`, `results/probe_32/`). One sampled row was added later, when the audit was extended to all 50 tasks: task 22, check 2h, set by the consistency pass for the same reason as task 17 (Section 13). A separate adversarial review then confirmed it, under the same reading of the free-bag allowance as task 17. Three tasks were re-labelled blind by a second model reader: 27/29 agreement with the original labels; the adversarial review settled the 2 differences, each in favour of the blind reader.

**Counting rule.** A pass for doing nothing (checks 2a and 2b; in retail also 2c) is a design the benchmark documents, not a hidden bug. The defect counts therefore leave it out and report it on its own line; the counts that include it are given beside them.

**Agent runs.** The audited model, `claude-haiku-5-5`, as agent and as user simulator, 3 trials per task on the 20 sampled tasks; the ground-truth agent (`llm_agent_gt`, which sees the reference actions) on the 16 tasks that have reference actions. The runner settings are recorded in the results files and were reused unchanged in block 2. Two of them depart from the v2.0.0 defaults: required information is checked by the substring scorer (`--communicate-scorer substring`) instead of the default semantic judge, which keeps the check deterministic, and no sampling parameters are sent (`llm_args {}`), because the default `temperature: 0.0` is rejected by the model (I5). Among the findings from reading and probes, only check 2g depends on the first choice (Section 3); the rewards behind the run-based rows were computed with it. The null-agent floor does not: the 23 tasks have no required information, which both scorers pass without a check.

**Block 2.** Pre-registered hypotheses and rules (`block2/PLAN.md`), then: a scorer overlay with three independent switches (canonical DB hash; word-boundary communicate check; free-text assertions enforced through a 3-vote judge), text fixes to six tasks (`block2/task_fixes.md`), an offline re-score of the 76 recorded conversations under one switch at a time, and fresh runs under the full v2 protocol. Gates before any v2 number: the stock scorer must reproduce every recorded reward (76/76), and the v2 scorer every reward recorded in the fresh v2 runs (85/85); each switch must flip a perturbed real trajectory (4/4). An adversarial review of the design preceded the paid runs and one of the results followed them; both are in the repository with the changes they forced.

## 3. Block 1: what the audit found

Table 1. Headline shares (sampled tasks).

| quantity | share |
|---|---|
| defective tasks (≥1 confirmed medium/high defect; the pass for doing nothing is counted on its own line) | 16/20 = 0.80 [0.58, 0.92] |
| defective by static reading and probes only | 12/20 = 0.60 [0.39, 0.78] |
| defective by agent-run checks only | 9/20 = 0.45 |
| defective by agent-run checks, excluding user-simulator deviations | 6/20 = 0.30 |
| defective, counting the pass for doing nothing (checks 2a, 2b) | 18/20 = 0.90 [0.70, 0.97]; 14/20 by static reading and probes |
| defective excluding every defect that derives from that design | 11/20 = 0.55 |
| defective also excluding the substring-scorer check (2g), which applies only to the substring scorer, the non-default setting the runs selected | 15/20 = 0.75 |
| tasks that pass for doing nothing (counted on its own line) | 7/20 sampled; 23/50 = 0.46 [0.33, 0.60] whole domain |

Table 2. Sampled tasks with a confirmed defect, by category (the pass for doing nothing is counted on its own line).

| category | share |
|---|---|
| 1 solvability | 1/20 |
| 2 scoring validity | 11/20 |
| 3 isolation and leaks | 0/20 (rule of three: ≤ 0.15) |
| 4 specification clarity | 4/20 |
| 5 determinism | 8/20 |
| 6 reporting | 0/20 at task level; one benchmark-wide documentation mismatch (I1) |

The main mechanisms, each with a reproduction in the repository:

- **A pass for doing nothing (checks 2a, 2b).** 23 of 50 tasks have a reference that leaves the database unchanged and no required output string. The default scorer compares the end-state hash and the required strings, so an empty conversation scores 1.0. The benchmark's documentation describes the refusal case as the intended outcome of these tasks; the audit records the consequence, not a hidden bug: the exam cannot distinguish an agent that correctly refuses from one that does nothing. For this reason the defect counts report it on its own line.
- **An end-state hash that depends on list order (2h, I3).** The DB hash serialises lists in their stored order. Reordering the reference actions changes the hash in 24 of 78 tested orders (the 13 tasks of the domain with two or more writes; all 24 fall in the sampled tasks 7, 23 and 32). In 20 of the 24, all in task 23, the final state is the same and only the identifiers the system gives new bookings move, so an equally valid order fails a correct solution. Adding passengers or payment methods in a different but equally valid order inside one call fails a correct solution as well. A second probe, added when the audit was extended to the whole domain, lets an earlier write change the arguments of a later one: in task 22, adding the three bags before the upgrade from basic economy makes one bag non-free, and the extra $50 charge fails an equally valid order (Section 13).
- **A substring check that matches by accident (2g, I4).** Short required strings are matched as substrings after commas are stripped, so they are found inside unrelated numbers: "4" in task 3 matches dates and a fare, and "327" in task 23 matches "$1,327". This concerns the substring scorer, which every run here selected; the v2.0.0 default is a semantic judge. Task 3 has no other confirmed defect, so without this check the headline is 15/20.
- **Requirements that no scorer reads (2k, 6 tasks).** The free-text `nl_assertions` state obligations that the default evaluation never checks; the documentation says the CLI evaluates them by default, the code at this tag does not (I1).
- **A wrong reference answer (I6).** Task 7's required total, 1628, sums all four upcoming reservations, including the two the user cancels in the same conversation; the task asks for the total of the other upcoming flights (708). In block 1 one of the four trials answered 708 and scored 0, and the other three answered 1004; all three Sonnet trials (Section 7) answered 708 and scored 0.
- **A scenario that forbids the reference (1e, I8).** Task 32's scenario caps the user at a $100 charge while the reference path charges $396 and refunds $510 in two steps. A counterfactual probe of the user simulator with the exact reference figures produced 10 refusals in 10 samples.
- **A user simulator that leaves its script (5d, 7 tasks).** In 7 of the 20 tasks the simulator volunteered facts, invented constraints or changed its request across trials; in 3 of the 5 tasks whose outcome changed between trials, the change came through the simulator.

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
- **Task 32** (0/4 → 2/7). The rewritten budget clause no longer blocks the two-step path: a pre-registered probe with the exact reference figures went from 0/10 acceptances to 8/10, and two live conversations completed the path. But in all seven fresh conversations the agent stated that refunds go to the original payment method; the policy's flight-change section lets the customer name the card, and the tool refunds to the payment method passed in the call, so the statement is wrong, and the ground-truth agent made it while holding the reference arguments. The first reading after the run blamed the sentence added to the scenario ("any charge or refund should go to your Visa") for turning that error into a failure. A later pre-registered test did not support this reading: the ground-truth agent passed 2 of 10 trials with the sentence and 2 of 10 without it (Section 13, Q3). H4 is reported as failed for this task.
- **Task 23** (3/3 → 1/3). Not a scorer effect: the agent changed the flights on the existing reservation instead of cancelling and rebooking three. The reference needs the simulator to volunteer a three-way split of the booking, which it did in 3/3 block-1 conversations and 1/3 fresh ones (the determinism defect 5d). The task's own edit touched only its assertion texts.

### 4.5 The judge as an instrument

The judge is the agent's own model, which is a self-evaluation risk. What was done about it: three votes per assertion; transcript with tool calls (the stock transcript view hid tool-call arguments and produced a false failure on task 9 trial 1, issue I9); every reward-changing, process-type and communication-type verdict on the recorded conversations checked by two model readers, 46/46 agreement with the judge; verdicts reported with the number of determined ballots. The results review found a parser gap: the upstream JSON extractor rejects a reply that is a bare JSON array, which the judge model returned in 53 of 610 replies, and those ballots had been dropped. The parser was fixed; an offline re-parse of the discarded replies recovered 32 ballots and changed no majority verdict, so the cached rewards stand. Six passes rested on one or two ballots and are named in `summary_v2.md`. Fresh-run verdicts were not checked in block 2 (Section 13 adds a blind check of 20 of them); 35 of the 66 fresh passes contain at least one assertion only the judge decides, and no fresh failure rests on the judge alone.

## 5. Retail: the same checklist on a whole domain

### 5.1 Design

The retail audit was pre-registered in `retail/PLAN.md` before any paid run: the question, the protocol, predictions P1–P7 and a budget ceiling of $15. Deviations were appended there with dates as the work went. It covers all 114 tasks of the split `base` without sampling, so the shares below are values for the whole domain, not estimates.

Retail is scored differently from airline. The reward is the database hash times a judge's verdict on the free-text `nl_assertions`; 40 tasks carry such assertions. `communicate_info` is never scored (`retail/checklist.md`). The stock judge is an OpenAI model. It was replaced by `claude-haiku-5-5` with the stock prompt and evaluator, and every judge reply is logged.

The steps:

1. A static scan and mechanical probes on all 114 tasks: WRITE-order permutations, argument perturbations, hidden and forbidden write orders, and a probe of a tool bug the reviewers found.
2. Twelve independent model reviewers on the task cards.
3. An adversarial review of every medium or high row: 80 rows, 69 confirmed, 8 re-filed, 3 rejected as duplicates, 4 added.
4. A blind second pass on 12 tasks.
5. Paid runs: Pass^3 on 114 tasks and the ground-truth agent on 112.
6. Five model reviewers read every failed trajectory (89) and the successful trials of every flipped task.
7. A 3-vote re-judge of every simulation whose reward depends on assertions.

The adversarial pass over the rows from the runs first stopped on a usage limit. It was later run again in four parts (Section 5.3, `results/retail/skeptic_report_agent.md`).

### 5.2 What the audit found

Table 4. Retail headline shares (all 114 tasks).

| quantity | share |
|---|---|
| tasks with ≥1 medium/high defect, static reading and probes (every row adversarially reviewed) | 38/114 = 0.33 [0.25, 0.42] |
| tasks with ≥1 medium/high defect, all checks (the run rows also adversarially reviewed) | 61/114 = 0.54 [0.44, 0.62] |
| the same, without the rows that attribute the failure to the user simulator (5c, 5d) | 40/114 = 0.35 [0.27, 0.44] |
| tasks that pass for doing nothing (no database write, no assertion; counted on its own line) | 6/114 = 0.05 [0.02, 0.11] |
| the three defect counts above, counting the pass for doing nothing (2a, 2b, 2c) | 44/114, 67/114 and 46/114 |
| blind second pass by another model reader, against the first reviewers' labels | 97/98, Cohen's kappa (agreement corrected for chance) 0.85; the adversarial review settled the one difference in favour of the blind reader |

The mechanisms, each reproduced by a script or a replay:

- **A forbidden write order passes (2e, 14 tasks; I12).** The policy forbids any change to an order after its items were modified. `modify_pending_order_address` still accepts the status `pending (item modified)`, because it tests the status by substring. The reversed sequence reaches the gold hash in all 14 tasks whose reference changes an address and then items, and several of these scenarios are written to test exactly this rule.
- **A tool stores the wrong item (1g, 5 tasks; I11).** `modify_pending_order_items` writes the price and options of the last new variant into every modified item. In the scored target, 9 items in 5 tasks carry another variant's data. The target hash then depends on the order of the (old, new) pairs inside the call (2h, 5 tasks), so a correct agent that lists the same swaps in another order scores 0. This falsified prediction P3.
- **The reference fixes a choice the scenario leaves open (4c, 11 tasks).** The open choice is a payment method, a cancellation reason or a product variant; only the reference's choice matches the hash.
- **A reference that cannot be reached (1b, 4b, 4e: task 105; I13).** The only reference action pays a 21.10 difference with a gift card that holds 17.00, so it raises. The scored target is the unchanged database, while the assertion demands the exchange, and no conversation can satisfy both.
- **Requirements without a scorer (2k, 2m).** In 3 tasks a required fact sits only in `communicate_info`, which nothing scores. Authentication and explicit confirmation leave no trace in the database, and none of the 61 assertions names them; this matters in 5 scenarios built around such a rule.
- **The no-op class is small (2a, 2b: 6 tasks).** Retail's assertions close most of airline's pass for doing nothing. Six tasks have neither a write nor an assertion. In 5 more, the verdict on an empty answer is left to the judge, which failed all 5 in the probe.

### 5.3 Agent runs and what the failed conversations show

Table 5. Retail runs (`claude-haiku-5-5` as agent and as user simulator; stock scorer with the substituted judge).

| quantity | value |
|---|---|
| tau2 pass^1 (average reward) | 0.807 |
| tasks passed 3/3 (pass^3) | 75/114 = 0.66 [0.57, 0.74] |
| tasks solved in 0/3; unstable tasks (1 or 2 of 3) | 7/114; 32/114 |
| ground-truth agent reaches reward 1.0 | 89/112 = 0.79 [0.71, 0.86] |
| failures caused by the judge alone (database matched) | 9 of 342 trials; 3 of 112 ground-truth runs |

The reviewers read the full record of every failed conversation and named its cause. A second, adversarial review then checked every finding from the runs in four parts, with rules fixed in advance (`results/retail/skeptic_report_agent.md`). It kept 66 of the 74 findings that report a defect as filed, set 7 to 0 (no defect), moved one from high to medium severity and raised two from 0.

- **Ground-truth failures.** Of the 23 ground-truth failures, 8 trace to the task or its scoring (1e). In task 105 (high severity) no conversation that follows the policy reaches the reference; tasks 1, 16, 38, 52, 64, 98 and 100 are medium severity. Another 12 trace to the user simulator and 3 to agent errors.
- **Unstable tasks.** In 24 of the 32 unstable tasks the flip runs through the simulator (5c): in 21 it departs from its scenario, and in 3 it makes a choice the scenario leaves open. Seven flips run through the agent and one through the judge (the model that grades the conversation). Departures from the scenario appear on 32 of the 45 reviewed tasks (5d). The text-mode simulator instructions lack three rules that the voice-mode instructions carry: do not end the conversation prematurely, check that every scenario item was addressed before ending, and answer "no preference" when the scenario gives none (I15).
- **New task-level findings.** The runs added four findings the reading of the task texts alone missed (4f: tasks 0, 1, 31 and 100; tasks 0, 1 and 100 are in I16). Tasks 0 and 1, for example, require "Google Home" compatibility, which appears nowhere in the catalogue.

A few rows rest on a reading that could go the other way. In tasks 15, 39, 59 and 91 a loosely worded scenario sentence was read as having one plain meaning, so the simulator's reading counts as a departure. Task 80's only defect is a refusal the scenario never gives, which a stricter reading of the character description the simulator is given would excuse. In task 28 a request for a human was read as the simulator filling a gap; read as a departure, it adds one defective task. Together these readings move the number of tasks with a defect under all checks to between 60 and 62 of 114, and the count without the user-simulator findings to at most 44. The figure from reading the tasks and from probes (38/114) does not depend on them.

### 5.4 The judge inside the score

Table 6. The judge as part of the reward (check 2j).

| quantity | value |
|---|---|
| live judge replies the stock strict parser would reject | 103/169 = 0.61 |
| assertion verdicts where the live single vote differs from a 3-vote majority | 1/243 |
| rewards that flip under the majority | 1 of 159 (task 110, fail → pass) |

With the substituted judge, the stock code would have rejected most replies, because they came in a code fence (103 of 169 replies). In a live run such a simulation is retried and then dropped from the denominator as an infrastructure error. The overlay's tolerant parser kept these replies and marked each one.

The single vote is stable on these transcripts: 1 disagreement in 243 verdicts. The one flip is on task 110, whose reference writes the address the user already has while the assertion asks the agent to change it (I13). The judge passes the same agent behaviour in one trial and fails it in two.

### 5.5 Predictions and upstream issues

Table 7. Pre-registered predictions against the measurements.

| id | prediction | outcome |
|---|---|---|
| P1 | no-op pass on 6/114 | held: 6/114 |
| P2 | 2k only where no assertion covers the fact; certain for 30, 31, 32 | held: exactly 30, 31, 32 |
| P3 | no task flips on WRITE order | **failed**: 5 tasks, through the tool bug of I11 |
| P4 | process requirements unscored | held: the benchmark-level 2m row, and 5 tasks |
| P5 | the three upstream-recorded issues (tasks 4, 5, 7) re-found | **not met** at task level (see below) |
| P6 | some replies fail the strict parser, and re-judging flips some verdicts | held: 103/169 rejected; 1 flip |
| P7 | defective share | no numeric prediction; 38/114 static, 61/114 all checks (44/114 and 67/114 counting the pass for doing nothing) |

P5 in detail:

- **Task 4:** the issue does not reproduce at the pinned commit. The scenario asks for the exact count, and all four runs pass.
- **Task 5:** the missing authentication check appears only as the benchmark-level 2m row.
- **Task 7:** the issue was not found.

The rows that sit on tasks 4 and 5 describe other mechanisms (`results/retail/upstream_issue_match.csv`).

### 5.6 Airline beside retail

Table 8. The same checklist on two domains (`retail/comparison.md`; airline is a sample of 20, retail the whole domain).

| quantity | airline | retail |
|---|---|---|
| tasks with ≥1 medium/high defect, static and probe checks | 12/20 = 0.60 | 38/114 = 0.33 |
| tasks with ≥1 medium/high defect, all checks | 16/20 = 0.80 | 61/114 = 0.54 |
| the same, counting the pass for doing nothing | 18/20 = 0.90 | 67/114 = 0.59 |
| empty answer gets full reward (whole domain) | 23/50 = 0.46 | 6/114 = 0.05 |
| agent pass^3 | 12/20 = 0.60 | 75/114 = 0.66 |
| ground-truth agent reaches reward 1.0 | 11/16 | 89/112 |

Reading (interpretation): the two domains fail in different places. Airline's largest hole is the pass for doing nothing. Retail closes most of it with judged assertions and moves the weight onto the judge and the tools: an order rule the tools do not enforce, and a tool that stores the wrong item. The agent's pass^3 is similar in both domains while the defects underneath differ in kind. This repeats the block-1 observation: the headline number does not show the state of the exam.

## 6. What an agent that does nothing scores, across tau2

Table 9. Null agent: an empty trajectory pushed through the stock evaluators of every task set (banking_knowledge could not be built, so 5 of 6 are measured), with no model call (`results/null_agent/tau2_null_agent.md`).

| task set | tasks | reward basis | passes by doing nothing | 95% CI |
|---|---|---|---|---|
| airline base | 50 | DB × COMMUNICATE | 23 (46.0%) | 33.0–59.6% |
| retail base | 114 | DB (× NL judge) | 6 (5.3%); 5 more depend on the judge, which failed them | 2.4–11.0% |
| telecom base | 114 | ENV_ASSERTION (× ACTION) | 0 | 0.0–3.3% |
| telecom full | 2,285 | ENV_ASSERTION (× ACTION) | 0 | 0.0–0.2% |
| intake base | 200 | DB | 0 | 0.0–1.9% |
| banking_knowledge | 97 | DB / ACTION / NL | not measured: the environment needs a package the pinned environment lacks | — |

The floor differs by an order of magnitude across domains of the same benchmark. Telecom asserts on the device state, so an empty answer fails everywhere; airline's hash design passes it on almost half the tasks.

The same script also runs a positive control: it replays every reference and checks the task's own assertions.

- **Telecom:** the control passes once the agent and user state are synchronised after every action, as the orchestrator does.
- **Retail:** 15 references contain a raising action. Most are intended negative steps; task 105 is the one that matters.

Four external agent benchmarks, chosen from a desk survey of nine (`null_agent/external_candidates.md`), were then examined the same way, with no model call (`results/null_agent/external.md`): BFCL V4, the original tau-bench and WebArena-Verified with their own scoring code, installed in their own folders outside the repository; OSWorld-Verified and the original WebArena task file by counting from the task files and the quoted scoring code. Next to the null agent, the table reports a refusal agent, which does nothing except give the benchmark's "cannot be done" answer.

Table 9b. Null-agent and refusal-agent floors on four external benchmarks (Wilson 95% intervals over tasks).

| benchmark, version | tasks | null agent | refusal agent | how the number was obtained |
|---|---|---|---|---|
| BFCL V4, bfcl-eval 2026.3.23 | 5,106 entries | 10.00 of 100 overall points | 10.00 of 100 | evaluator run on all 22 scoring categories |
| tau-bench (original) `59a200c6`, airline test | 50 | 19 (38.0%, 25.9–51.8%) | 19 | reward code; the reference replay passes 50/50 |
| the same, retail test | 115 | 7 (6.1%, 3.0–12.0%) | 7 | reward code; 115/115 |
| the same, retail train | 500 | 5 (1.0%, 0.4–2.3%) | 5 | reward code; 500/500 |
| the same, retail dev | 20 | 1 (5.0%, 0.9–23.6%) | 1 | reward code; 20/20 |
| OSWorld-Verified, task files as released (`00804f81`) | 369 | not measured (needs the virtual machine) | 30 (8.1%, 5.8–11.4%) | counted from the task files and the quoted scoring code |
| OSWorld-Verified, current task files (`044bc339`) | 369 | not measured | 26 (7.0%, 4.9–10.1%) | counted |
| WebArena-Verified v1.2.3 | 812 | 0 (0.0–0.5%) | 24 (3.0%, 2.0–4.4%) for the best fixed refusal; 31 (3.8%) with the right refusal chosen per task | evaluator, with a synthetic start-page network trace |
| WebArena, original task file | 812 | not measured (needs the live sites) | at least 36 (4.4%, 3.2–6.1%) for the answer "N/A"; the other tasks were not computed | counted from the task file and the quoted scoring code |

- **BFCL V4.** All 10 points come from the two irrelevance subsets (240 and 884 entries), where making no function call is the correct answer; every other category scores 0. A refusal sentence scores the same. The live relevance subset, which would penalise never calling a function, carries no weight in the overall score.
- **tau-bench (original).** An agent that does nothing passes 19 of the 50 airline test tasks, and a hand-over to a human at step 0 passes the same 19, because it ends the episode with the database untouched. The figure was reported before: Zhu et al. (2025), *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (arXiv:2507.02825) give 38% of the airline subset and 6% of the retail subset as tasks that an agent that does nothing passes; the counts here come from running the benchmark's own reward code, and the paragraph on the HAL leaderboard below compares the airline floor with published scores. The tau2 airline tasks were rewritten and reordered, so 19 against tau2's 23 compares counts only. In retail, six tasks pass for doing nothing because their single reference write is rejected on replay (test 106; train 161, 214, 229, 288, 349), so the scored target is the starting state. Test task 106 is tau2 retail task 105: same order, items and gift card, and the tau2 action id still reads `106_0`. The original benchmark gives this task to an agent that does nothing; tau2 added an assertion that demands the exchange, which turned the free pass into a task no conversation can pass (Section 5).
- **OSWorld-Verified.** The environment returns success for a `FAIL` action on every task marked infeasible, so an agent that gives up at step 0 scores the infeasible share. That share depends on the task-file version: 30 of 369 as released and 26 of 369 at the current head, after five tasks received real checkers and one became infeasible. A published score therefore carries a refusal floor of 8.1% or 7.0%, depending on the version it was scored on.
- **WebArena.** In the original task file 36 tasks expect the answer "N/A" and score it by exact match, so that one answer passes all 36. WebArena-Verified closes most of this: the best single fixed refusal passes 24 tasks. Its evaluator has defects of its own: task 319 cannot be passed by any response tried, including the expected one; tasks 699, 700 and 811 end in an evaluator error on every response; and 10 map tasks pass for reporting success at step 0, because their only network check is met by loading the start page.

Outside tau2 the floor runs from 0 (WebArena-Verified, null agent) to 38% of tasks (original tau-bench airline), plus 10 of 100 points on BFCL V4.

**Published scores below the floor.** HAL's TAU-bench Airline leaderboard (accessed 2026-10-28) lists four single runs of the "TAU-bench Tool Calling" scaffold below 38%: Gemini 2.0 Flash High at 28% (14 of 50 tasks), and o4-mini Low, GPT-4.1 and DeepSeek R1 at 36% (18 of 50). HAL scores the same 50 airline test tasks with tau-bench's own reward code. It installs the code from a modified copy (fork) whose airline tasks differ from the original in tasks 2, 8, 9, 10 and 23 only. None of these five is among the 19 that doing nothing passes, so the floor on HAL's version is also 19 of 50; this follows from reading the fork's task file, as the fork itself was not run (`results/null_agent/hal_check.md`). The 28% run therefore failed at least 5 of the 19 tasks that doing nothing passes. This does not show that these models do worse than doing nothing: each row is one run, the 36% rows are one task below the floor, both margins of error (Wilson intervals) contain 38%, and HAL counts errors and timeouts as failures. It shows that a reader of the page cannot tell, because the page prints no floor. HAL's Generalist rows (10% to 32%) cannot be compared: HAL marks them as a lower bound, because that scaffold rarely ends the conversation, and a conversation that does not end scores 0.

## 7. Strong vs weak: does the exam separate a stronger agent?

The predictions were written in `strong_vs_weak/PLAN.md` after the paid run had finished and before any of its results were read, and committed before the analysis. The check uses the same 20 sampled airline tasks with three trials each. The agent is `claude-sonnet-5-5`; everything else is unchanged: the user simulator `claude-haiku-5-5`, the seed, the scorer and the settings. Results are in `strong_vs_weak/summary.md`.

Table 10. Sonnet and Haiku on the same exam (20 sampled airline tasks × 3 trials).

| quantity | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| tau2 pass^1, stock scorer | 0.733 | 0.850 |
| tasks passed 3/3, stock scorer | 12/20 = 0.60 [0.39, 0.78] | 16/20 = 0.80 [0.58, 0.92] |
| tau2 pass^1, full v2 | 0.733 | 0.883 |
| tasks passed 3/3, full v2 | 11/20 | 16/20 |

- **Stock scorer.** Paired per task, Sonnet is ahead on 6 tasks, behind on 1 and equal on 13; the exact sign test gives p = 0.125. By the rule set in the plan, the exam does not separate the two models on this sample.
- **Tasks that carry no information.** Nine of the 20 tasks say nothing about the difference. The 7 tasks that an empty conversation passes give both models 3/3. Tasks 7 and 44, whose references are defective, give both models 0/3.
- **Full v2.** The gap widens to +0.150: 8 tasks ahead, 1 behind, 11 equal, p = 0.039. Most of the change in the gap comes from task 7, whose corrected reference total Sonnet reaches in 3 of 3 trials and Haiku in 1; the eighth task ahead is task 9, where the judge lowers Haiku from 3 to 2 passes. With the corrected task texts alone, under the stock scorer, Sonnet is ahead on 7 tasks and p = 0.070. This p value comes from one of three configurations compared on the same conversations, so it does not survive a Bonferroni correction (threshold 0.017).

All five predictions held. The check cost about $17.20: the run $16.85, the smoke simulation and the re-score about $0.35 together.

Reading (interpretation): the defects found in block 1 compress the measured difference between models. Free passes and tasks with defective references tie both models, so a real gap has fewer tasks in which to show. Correcting one wrong reference answer lowered p from 0.125 to 0.070; the full v2 protocol, whose judge also lowers Haiku on one more task, brings it to 0.039, which does not survive the correction for three comparisons. With 20 tasks and one run per model, the check cannot say how large the true gap is. It shows that the measurable gap depends on the exam's defects.

## 8. Issue candidates

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
| I10 | the assertion evaluator and the JSON extractor fail on a bare top-level JSON array, which the judge model returned in 53 of 610 replies (about 9%) to the audit's own prompt and in none of 169 replies to the stock prompt |
| I11 | retail: `modify_pending_order_items` stores the last variant's price and options in every modified item; the target hash depends on the pair order |
| I12 | retail: an address change after an item change is accepted although the policy forbids it (a payment change is rejected, by an unrelated check); 14 references reach the same hash in the forbidden order |
| I13 | retail reference defects: a product id that exists nowhere (2, 3, 4), an unreachable exchange (105), a transfer summary from another task (26), a no-op address write (110) |
| I14 | retail scoring path: an assertion the judge omits counts as met; the strict parser rejects most replies of the substituted judge |
| I15 | the text-mode user simulator lacks three rules of the voice mode, among them "do not end prematurely"; the simulator is the largest cause of retail failures and flips |
| I16 | retail task texts a faithful simulator cannot follow to the reference (0, 1, 52, 100) |

**Already reported upstream.** A check of the benchmark's issue tracker on 2026-10-28 found three of these drafts reported by others: I6 as [sierra-research/tau2-bench#495](https://github.com/sierra-research/tau2-bench/issues/495); I11 as [#318](https://github.com/sierra-research/tau2-bench/issues/318), [#317](https://github.com/sierra-research/tau2-bench/issues/317) and [#325](https://github.com/sierra-research/tau2-bench/issues/325), with a fix in [pull request #322](https://github.com/sierra-research/tau2-bench/pull/322) (open, not merged); and the payment-order part of I3 as [#514](https://github.com/sierra-research/tau2-bench/issues/514). Not found there: the passenger order and generated identifiers of I3, the unrounded price difference of I11, I4 and I8. The other drafts were not compared with the tracker in detail, although some issue titles there point to related findings (for example [#384](https://github.com/sierra-research/tau2-bench/issues/384) on passes without any action, [#499](https://github.com/sierra-research/tau2-bench/issues/499) on reference actions that raise errors, and [#555](https://github.com/sierra-research/tau2-bench/issues/555) on the judge's reply parser). On the main branch at commit `122e2432` (2026-10-28), none of the files behind I3, I4, I6, I8 and I11 has changed since `v2.0.0`. The tracker and the main branch were read on GitHub on that date; no copy of those pages is kept in this repository. Nothing from this audit is filed upstream.

## 9. What the numbers mean

Two facts stand side by side. The examination has reproducible faults and one documented design that hurts the measurement: a pass for doing nothing on 23 of 50 tasks, an end-state check that fails valid solutions, a string check that passes by accident, a wrong reference answer, a scenario that forbids its own reference, requirements nobody scores, a simulator that improvises. And on the 20 sampled tasks the agent's headline number barely moves when the examination is repaired: pass^3 0.60 in both runs, pass^1 within the noise floor. On the other 30 tasks (Section 13) the same repair moves it from 0.70 to 0.50, mostly because v2 reads the requirements written only in free text. Whether the number moves depends on the tasks, and the stock number gives no sign of it. The leaderboard cannot show what is wrong with the exam. Finding it took a checklist applied to the procedure, probes with known answers, and reviews whose job was to overturn the findings.

The repair itself is instructive. The deterministic faults exist (they fire on perturbed trajectories) but did not flip a single recorded conversation, because the recorded agents happened not to hit them. The one fix that failed, task 32, still fails, and its first explanation did not survive a test: a sentence added to make the scenario consistent with the reference was blamed, but in a later pre-registered test the ground-truth agent passed 2 of 10 trials with that sentence and 2 of 10 without it. Both say the same thing: an examination has to be validated as an instrument, with pre-registered expectations and adversarial review, before its numbers are read.

Retail tests the claim on a whole domain (interpretation). Its scorer closes airline's largest hole, yet 38 of 114 tasks still carry a defect found by reading and probes alone, and 61 counting the runs, all adversarially reviewed (the 6 tasks that pass for doing nothing are counted on their own line). The new holes sit in places a leaderboard never shows: a tool that stores the wrong item, an order rule only the policy text enforces, and a judge that would crash the stock parser on most replies. The conversations add a second lesson. In retail, the user simulator decides more outcomes than the reference does: it explains 12 of 23 ground-truth failures, and 24 of 32 flips run through it. A pass rate on this benchmark therefore measures the agent and the simulator together. The null-agent table puts the same point in one line: the score of an agent that does nothing ranges from 0% to 46% across domains of one benchmark, depending only on how each domain's exam is built. Four external benchmarks show a similar spread, from 0 to 38% of tasks, and on OSWorld-Verified the refusal floor changed between two versions of the same task files. The strong-vs-weak check adds the consequence for model comparison. On the stock exam a stronger model is ahead on 6 of the 7 tasks where the two differ, yet the difference is not significant, because 9 of the 20 tasks tie both models by construction.

## 10. Limits

- **Scope.** Two domains of one benchmark: airline with all 50 tasks (20 sampled in block 1, the other 30 in Section 13) and retail with all 114 tasks.
- **Models.** One agent model (`claude-haiku-5-5`; `claude-sonnet-5-5` only in the strong-vs-weak check), one simulator model (`claude-haiku-5-5`) and a judge from the same family. In retail that judge replaces the stock OpenAI judge, so the parser figures describe the substitution.
- **Run-row readings.** The retail findings from the runs went through their own adversarial review, in four parts with rules fixed in advance. A few rows rest on readings that could go the other way; together they move the all-checks count to between 60 and 62 of 114.
- **Reading of the bag allowance.** Rows 17/2h and 22/2h hold only if the free-bag allowance follows the cabin the reservation has when the bags are added. If the final cabin governed, both would be 0, and the counts from reading and probes would be 11/20 (sample), 14/30 (rest) and 25/50 (all); the headline counts would not change.
- **Reviewers.** Every reviewer, adversarial reviewer and reader in this audit was a language model, not a person, so agreement figures measure agreement between model reviewers. Deviations during the airline review are listed in Section 13.6.
- **One reading for the whole audit.** An upgrade the user never asked for, which would make a refused cancellation or change possible, is read as an unrequested write in both blocks. The opposite reading would add seven rows on the other 30 tasks and raise the whole-domain count to at least 39/50: five of those seven tasks have no other defect once the pass for doing nothing is counted on its own line.
- **What v2 is.** The refusal pass is documented as intended, so v2 is a stricter alternative protocol rather than a bug fix.
- **Run-to-run noise.** Single-trial ground-truth runs flipped on 4 of 13 unchanged airline tasks between two runs, so ground-truth totals are read against that floor.
- **Strong vs weak.** One run per model and 20 tasks. The two runs are a day apart and the user simulator samples, so each run is one draw.
- **External floors.** Three of the nine external rows are counted from task files and quoted scoring code rather than measured by running the evaluator (OSWorld-Verified twice, original WebArena). The WebArena-Verified agents were scored with a synthetic start-page network trace, because its evaluator rejects an empty one.
- **Scorer setting.** The airline runs check required information with the substring scorer, not the v2.0.0 default semantic judge. Check 2j compared the two on every recorded airline run: 0 of 58 verdicts differ. Task 3 is defective only through check 2g, which depends on the substring choice; the run rewards were computed under it.
- **Cost figures.** Dollar figures are own estimates from token counts at the published per-token prices. They were not reconciled with billing row by row; the account's billing was about $11 when the own estimate was $10.79.

## 11. Reproducibility and cost

Every number from the recorded files is rebuilt by the command sequences in `STRUCTURE.md`, except a few counts taken from review reports and the HAL leaderboard figures, read from its web page (`results/null_agent/hal_check.md`); the judge stages replay from cached votes without a model call. Provenance stamps on every v2 output record the overlay commit and a dirty-tree flag; the live runs record the runner configuration and its empty diff against block 1. Spend, own estimate from token counts: block 1 about $1.36, block 2 about $2.27, retail about $7.16 (runs $6.86, re-judge $0.30, probe below one cent); the strong-vs-weak check about $17.20; the whole-domain airline work (Section 13: runs, probes and re-scores) about $5.05; about $33.04 in total (`cost.md`). The null-agent tables and the demo make no model call; the external benchmarks are installed in their own folders outside the repository, with the commands in `results/null_agent/external.md`.

## 12. Open items

Not done, candidates for a next iteration:

- **Strong vs weak, more power.** Repeat the comparison on all 50 airline tasks or with a second run per model, so that a gap of the observed size can reach significance.
- **External null agent, remaining runs.** Run the do-nothing agent on OSWorld-Verified (needs its virtual machine) and on the original WebArena (needs the live sites).
- **External defects.** The problems found in tau-bench (six retail tasks whose single reference write is rejected; whether the task authors intended this was not reviewed) and in WebArena-Verified (tasks 319, 699, 700, 811 and the 10 map tasks) are recorded in `results/null_agent/external.md`; no issue text is drafted for them.
- **Upstream issues.** Texts for I1 and I3–I16 are ready in `upstream/` (nine issues, five patches, fourteen reproductions, each patch checked against the pinned clone). None is filed; three are already reported by others (Section 8).

## 13. The whole airline domain: the other 30 tasks

Block 1 audited 20 of the 50 airline tasks. This section runs the same pipeline on the other 30 tasks and closes the block-1 items that were still open. The questions, the predictions and the decision rules were written down before any run or review (`airline_full/PLAN.md`). Departures from that plan are recorded, with dates, at its end.

Most numbers below come from `airline_full/summary_numbers.md`; the rest come from the probe, re-score and review files in `results/` and `airline_full/`. The script `scripts/airline_full_summary.py` builds that file from `airline_full/audit_log.csv`, which has one row per task and check (1,219 rows). The format validator finds 0 errors in it.

### 13.1 What was done

On the 30 tasks outside the sample:
- **Reading and probes.** Reviewers read the tasks in batches of five (`results/review_batch_5.md` to `review_batch_10.md`). They used the same mechanical probes and static scan as in block 1.
- **Agent runs.** The settings were those of block 1: Haiku 5.5 as the agent and as the user simulator, the substring scorer, 3 trials per task. The ground-truth agent ran on the 27 tasks that have reference actions (`scripts/runs/run_rest30.ps1`). A reviewer read every conversation that failed, and every task whose trials gave different results (`results/review_agent_rest30.md`).
- **Adversarial review.** Every medium or high row went through a review that tried to overturn it (`results/skeptic_report_rest_*.md`, `results/skeptic_report_agent_rest.md`). The review had four parts:
  - check 2k;
  - the order checks 2h and 4c;
  - all other static checks (checks that need no agent runs);
  - the checks based on runs.
- **Blind re-review.** A second model reader labelled three tasks (33, 35, 39) without seeing the first labels: 23 of 26 labels agreed (Cohen's kappa 0.36). The adversarial review, which saw both sets, settled the 3 differences, each in favour of the blind reader.
- **Consistency pass.** One mechanism gets one reading and one check, across the four parts and across both blocks (`results/consistency_pass.md`).

On all 50 tasks:
- **Scorer choice (check 2j).** On every recorded run, the substring scorer was compared with a semantic judge that votes three times (`results/probe_2j.md`). There are 58 recorded verdicts on required information, in 36 trials; 0 differ.
- **Task 32 (open item from block 1).** The ground-truth agent ran 10 times with the payment sentence and 10 times without it (`airline_full/cf32.md`).
- **The v2 judge, second blind check.** Two model readers labelled 20 judge verdicts and 10 decoys from the v2 runs on the 20 sampled tasks, each working on a copy without the answer key (`airline_full/judge_handcheck_fresh_r2.md`).
  - Decoys are verdicts the judge had marked unmet, mixed in so that a reader who marks everything as met is caught.
  - A first round was only partially blind, which is recorded in the plan, so this second round was run.
- **Block 2 on the 30 tasks.** The recorded conversations on the other 30 tasks were scored again under every block-2 configuration. A fresh run used the full v2 protocol.

### 13.2 What the audit found

Table 13.1. Defective tasks (at least one confirmed medium or high defect; the pass for doing nothing is counted on its own line), with 95% Wilson intervals.

| quantity | sample (20) | rest (30) | all 50 |
|---|---|---|---|
| defective tasks, all checks | 16/20 = 0.80 [0.58, 0.92] | 18/30 = 0.60 [0.42, 0.75] | 34/50 = 0.68 [0.54, 0.79] |
| from reading and probes only (no agent runs) | 12/20 = 0.60 [0.39, 0.78] | 15/30 = 0.50 [0.33, 0.67] | 27/50 = 0.54 [0.40, 0.67] |
| also without check 2g (substring scorer only) | 15/20 = 0.75 | 18/30 = 0.60 | 33/50 = 0.66 |
| without every defect that follows from the do-nothing design | 11/20 = 0.55 | 13/30 = 0.43 | 24/50 = 0.48 |
| counting the pass for doing nothing (2a, 2b), all checks | 18/20 = 0.90 [0.70, 0.97] | 26/30 = 0.87 [0.70, 0.95] | 44/50 = 0.88 [0.76, 0.94] |
| counting it, from reading and probes only | 14/20 = 0.70 | 23/30 = 0.77 | 37/50 = 0.74 |
| tasks that pass for doing nothing (counted on its own line) | 7/20 | 16/30 | 23/50 = 0.46 |

Table 13.2. Defective tasks per category (the pass for doing nothing is counted on its own line).

| category | sample | rest | all 50 |
|---|---|---|---|
| 1 solvability | 1/20 | 1/30 | 2/50 |
| 2 scoring validity | 11/20 | 14/30 | 25/50 |
| 3 isolation and leaks | 0/20 | 0/30 | 0/50 |
| 4 specification clarity | 4/20 | 7/30 | 11/50 |
| 5 determinism | 8/20 | 7/30 | 15/50 |
| 6 reporting | 0/20 | 0/30 | 0/50 |

The other 30 tasks show the same mechanisms as block 1, in different proportions:
- **A pass for doing nothing.** This is more common in the other 30 tasks: 16 of 30, against 7 of 20 in the sample.
- **Requirements no scorer reads (2k).** These are in 11 of the other 30 tasks. In task 6, no tool can break the requirement.
- **Order that changes the hash (2h).** This is in 4 of the other 30 tasks. In task 33 the user asks for two flight changes separately, and they can be done in two calls. That gives the same flights and the same balance, but a different payment record.
- **Open choices the hash punishes (4c).** These are in 3 of the other 30 tasks.
- **A reference that breaks the policy (4b, task 39).** The reference cancels a reservation that the policy does not allow to be cancelled. No conversation that follows the policy reaches the target, and the ground-truth agent failed on this task.
- **Text left over from an earlier version (4e, task 27).** The purpose and one requirement of task 27 still describe a certificate that the current task text no longer contains. Result files in the benchmark's own repository show that earlier text.
- **"Your most recent reservation" (4d, tasks 2 and 38).** The phrase can point to more than one reservation. The review read it the same way in both tasks: the reservation with the latest booking time.
- **A required number found inside another number (2g, task 14).** In a recorded run, the answer "$1,327" (certificates 1,000 plus gift cards 327) contains the required "327".

Table 13.3. Agent runs (Haiku 5.5 as agent and user, substring scorer, three trials per task).

| quantity | sample | rest | all 50 |
|---|---|---|---|
| tasks passed 3/3 (tau2 pass^3) | 12/20 = 0.60 | 21/30 = 0.70 | 33/50 = 0.66 [0.52, 0.78] |
| passing trials (tau2 pass^1, mean over all trials) | 44/60 = 0.73 | 76/90 = 0.84 | 120/150 = 0.80 |
| tasks solved in 1 or 2 of 3 trials | 5/20 | 8/30 | 13/50 |
| ground-truth agent reaches the target | 11/16 | 22/27 | 33/43 = 0.77 |

The block-1 summaries also report a pass^1 that counts only the first trial of each task: 0.80 on the sample and 0.87 on the rest. Pass^3 is the same under both ways of counting.

The ground-truth agent failed on 5 of the other 30 tasks (14, 24, 29, 39, 42).
- After the adversarial review and one probe (Section 13.3), one of the five traces to the task itself: task 39, whose reference breaks the policy.
- Across all 50 tasks, the ground-truth agent failed on 10 tasks, and 2 of them trace to the task (32 and 39). The other failures trace to the agent or to the user simulator.
- The user simulator stepped outside its script in 7 of the other 30 tasks (check 5d). In block 1 the count was also 7.

### 13.3 What the adversarial review and the consistency pass changed

- **Check 2k.** All 9 defect rows held. One row was raised: task 6, a requirement that no tool can break. For task 33, the label from the blind re-review was kept. As in block 1, a clause such as "because …" inside a requirement was read as a justification, not as a demand to state a reason.
- **Order checks (2h, 4c).** Four of seven rows held.
  - Three were withdrawn, because each counted a cause that another row already counted.
  - Task 25 got two rows for two causes: the split of the amount, which the task leaves open, and the order of the payment list.
  - Two rows on task 33 were raised, keeping the labels of the blind re-review. The first is the two-call path described above. The second is "move back your return by one day", which gives a size but no direction.
  - Every claim that two end states give different hashes was replayed in the pinned version of the benchmark.
- **All other static checks.** All 34 rows held. Three were raised: 38/4d, 27/4e and 14/2g.
- **Run-based checks.** Ten of 11 rows held. 29/1e was rejected, because every recorded refusal came after an agent error. Block 1 had settled the same kind of dispute on task 32 with a probe of the user simulator, and the same procedure was used here (`results/probe_29/`):
  - the protocol was committed before the call;
  - 10 replies were sampled;
  - two model readers classified them blind.

  In the probe, the agent message states the reference route plainly: cancel for the full refund under the insurance, then book the two nonstop flights. The user simulator refused it in 1 reply of 10. By the pre-set rule (at most 5 refusals of 10 means 0), 1e stays 0.
- **Blind re-review (tasks 33, 35, 39).** It agreed with the original labels on 23 of 26 rows, and with the corrected labels on 26 of 26. All three disagreements were settled in favour of the blind reader, so the second figure does not confirm the corrections independently.
- **Consistency across the blocks.** A second order probe (`scripts/probe_2h_paths.py`) covers two paths the first one could not: an earlier write that changes the arguments of a later one, and one change split into two calls. It found one block-1 row to change.
  - Task 22 has the same reservation and the same reference writes as task 17 from the other 30.
  - The reference upgrades the reservation from basic economy first and adds the bags afterwards. An agent that adds the bags first, while the reservation is still basic economy, must charge for one of them. That extra $50 changes the end state, so this equally valid order fails.
  - 22/2h went from 0 to 1, and a separate adversarial review then confirmed it (`results/skeptic_report_consistency.md`). This moves the block-1 count from reading and probes from 11/20 to 12/20 (13/20 to 14/20 counting the pass for doing nothing); the block-1 headline stays 16/20.
  - Rows 17/2h and 22/2h hold only if the free-bag allowance follows the cabin the reservation has when the bags are added. If the final cabin governed, both would be 0, and the counts from reading and probes would be 11/20 (sample), 14/30 (rest) and 25/50 (all); the headline counts would not change.
- **One reading of "upgrade routes".** These are upgrades the user never asked for that would make a refused cancellation or change possible. Both blocks read them as unrequested writes (4c = 0). The opposite reading would raise the whole-domain count to at least 39/50 (45/50 counting the pass for doing nothing).

### 13.4 Block 2 on the 30 tasks

| configuration | Haiku trials passing (90) | Haiku tasks 3/3 (30) | ground-truth runs passing (27) |
|---|---|---|---|
| stock scorer (v1) | 76 | 21 | 22 |
| canonical hash only, or word-boundary check only | 76 | 21 | 22 |
| requirements enforced by the judge (S_nl), or full V2 | 68 | 16 | 16 |

- **The new scoring of recorded runs matches the original.** The stock (unchanged) scorer reproduces all 117 recorded rewards. The two mechanical switches (canonical hash, word-boundary check) change none of them (prediction P9).
- **The whole difference comes from the judge reading the requirements.** On the same conversations, tasks passed 3/3 drop from 21 to 16, and ground-truth passes drop from 22 to 16.
- **The fresh run under the full v2 protocol** passes 15 of 30 tasks 3/3 (0.50), against 21 (0.70) under the stock protocol. On the same fresh conversations, the stock scorer passes 19. So 4 of the 6 lost tasks are due to the stricter scoring, and the other 2 to different conversations (new task texts and random sampling). Prediction P10 (a difference of at most 0.10) does not hold.
- **Task 32 (Q3).** The ground-truth agent passes 2 of 10 trials with the payment sentence and 2 of 10 without it. The pre-set rule asked for at least 3 more passes without the sentence, so the sentence does not cause the failures; prediction P7 does not hold. With and without the sentence, most failed trials miss one or both of the same two requirements (7 of 8 with the sentence, 6 of 8 without; the others fail on the database only): the cabin change is missed in 4 trials with the sentence and in 5 without it, the flight change in 7 and 6.
- **The v2 judge.** Both blind readers agreed with it on 20 of 20 verdicts and on 10 of 10 decoys (P8).

Table 13.4. Pre-registered predictions (`airline_full/PLAN.md`, section 3).

| id | prediction | measured | verdict |
|---|---|---|---|
| P1 | whole-domain defective share, counting the pass for doing nothing as registered, in [0.70, 0.97] | 44/50 = 0.88 | holds |
| P2 | the same without the pass for doing nothing (2a, 2b; the headline definition) in [0.58, 0.92] | 34/50 = 0.68 | holds |
| P3 | the same from reading and probes, counting the pass for doing nothing as registered, in [0.43, 0.82] | 37/50 = 0.74 | holds |
| P4 | rest pass^3 above the sample's 0.60 | 21/30 = 0.70 | holds |
| P5 | semantic scorer: the empty conversation passes the same 23 tasks | none of the 6 tasks with required information | holds |
| P6 | recorded runs: semantic and substring verdicts differ on at most 2 trials | 0 of 36 | holds |
| P7 | task 32: at least 3 more passes of 10 without the payment sentence | 2 vs 2 | does not hold |
| P8 | each blind reader agrees with the judge on at least 18 of 20 | 20/20 and 20/20 | holds |
| P9 | the mechanical v2 switches change no rest reward | 0 changed | holds |
| P10 | rest pass^3 under v2 within 0.10 of the stock protocol | 0.70 vs 0.50 | does not hold |

### 13.5 What else the conversations show

- **A plan that cannot be flown still scores 1.0.** In task 10, two fresh v2 conversations (trials 0 and 1) quote the same cheapest business option: HAT131, arriving in Las Vegas at 21:00, connecting to HAT047, which leaves Las Vegas at 13:00 the same day.
  - Nothing was booked, because the user declined on price. Both conversations scored 1.0.
  - Task 10 is one of the tasks an empty conversation passes: its reference changes nothing and requires no output. So the score cannot tell this conversation from a correct one.
- **A transfer does not end an airline conversation.** In airline runs the transfer call does not stop the conversation. Task 24 from the other 30 succeeded after a transfer.
- **The two blocks agree on the registered measure.** Counting the pass for doing nothing, as P1 was registered, the other 30 tasks are defective at about the sample's rate (0.87 against 0.90), and the block-1 estimate holds for the whole domain (P1). Without it the rest is lower (0.60 against 0.80; the intervals overlap): 8 of its 26 defective tasks are defective only through that design, against 2 of 18 in the sample. The agent's pass^3 on the rest is a little higher (0.70 against 0.60).

### 13.6 How the review was carried out

- All reviewers, adversarial reviewers and readers were language models, not people. Agreement figures measure agreement between model reviewers.
- One adversarial reviewer opened the pre-registration file once, before it read the list of files it must not open. Three ran read-only git commands inside the pinned copy of the benchmark; no file changed. Neither event changed a verdict.
- Row 22/2h, set by the consistency pass, got its own adversarial review afterwards and held. That reviewer read four more benchmark source files than its brief named, and listed file names in the clone's folder of recorded simulations without opening any of them.
