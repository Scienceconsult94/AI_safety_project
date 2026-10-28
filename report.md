# Report: validation audit of tau2-bench (airline, retail) and the v2 protocol

Target: tau2-bench, tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`, domains airline (50 tasks, 20 sampled) and retail (all 114 tasks). All numbers below are copied from the generated files `summary_numbers.md` (block 1), `block2/summary_v2.md` (block 2), `retail/summary_numbers.md` and `retail/comparison.md` (retail) and `results/null_agent/tau2_null_agent.md` (null agent); intervals are 95% Wilson. Where this report interprets, it says so.

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

## 5. Retail: the same checklist on a whole domain

### 5.1 Design

The retail audit was pre-registered in `retail/PLAN.md` before any paid run: the question, the protocol, predictions P1–P7 and a budget ceiling of $15. Deviations were appended there with dates as the work went. It covers all 114 tasks of the split `base` without sampling, so the shares below are values for the whole domain, not estimates.

Retail is scored differently from airline. The reward is the database hash times a judge's verdict on the free-text `nl_assertions`; 40 tasks carry such assertions. `communicate_info` is never scored (`retail/checklist.md`). The stock judge is an OpenAI model. It was replaced by `claude-haiku-5-5` with the stock prompt and evaluator, and every judge reply is logged.

The steps:

1. A static scan and mechanical probes on all 114 tasks: WRITE-order permutations, argument perturbations, hidden and forbidden write orders, and a probe of a tool bug the reviewers found.
2. Twelve independent reviewers on the task cards.
3. An adversarial review of every medium or high row: 80 rows, 69 confirmed, 8 re-filed, 3 rejected as duplicates, 4 added.
4. A blind second pass on 12 tasks.
5. Paid runs: Pass^3 on 114 tasks and the ground-truth agent on 112.
6. Five reviewers read every failed trajectory (89) and the successful trials of every flipped task.
7. A 3-vote re-judge of every simulation whose reward depends on assertions.

The adversarial pass over the rows from the runs stopped on a usage limit and was not rerun. Those rows are reported separately below.

### 5.2 What the audit found

Table 4. Retail headline shares (all 114 tasks).

| quantity | share |
|---|---|
| tasks with ≥1 medium/high defect, static reading and probes (every row adversarially reviewed) | 44/114 = 0.39 [0.30, 0.48] |
| tasks with ≥1 medium/high defect, all checks (the run rows not adversarially reviewed) | 67/114 = 0.59 [0.50, 0.67] |
| the same, without the rows that attribute the failure to the user simulator (5c, 5d) | 48/114 = 0.42 [0.33, 0.51] |
| tasks an empty trajectory passes (no write and no assertion) | 6/114 = 0.05 [0.02, 0.11] |
| blind second pass against the corrected labels | 98/98, kappa 1.00 (97/98, kappa 0.85, against the first reviewers) |

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

The reviewers read every failed trajectory and named its cause.

- **Ground-truth failures.** Of the 23 ground-truth failures, 8 trace to the task or its scoring (1e). In tasks 52 and 105 (high) no compliant conversation reaches the reference; tasks 1, 16, 38, 64, 98 and 100 are medium. Another 12 trace to the user simulator and 3 to agent errors.
- **Unstable tasks.** The flip traces to the simulator in 23 of the 32 unstable tasks (5c). Deviations from the scenario appear on 36 of the 45 reviewed tasks (5d). The text-mode simulator instructions lack the "do not end the conversation prematurely" rule that the voice-mode instructions carry (I15).
- **New task-level findings.** The runs added six findings the static reading missed (4f: tasks 0, 1, 15, 31, 34 and 100; I16). Tasks 0 and 1, for example, require "Google Home" compatibility, which appears nowhere in the catalogue.

These run rows were not adversarially reviewed. The threshold for 5d differs between reviewer batches, and the rule for "the simulator makes a choice the scenario leaves open" was applied differently (tasks 0, 1 and 98 against 15 and 100). The static-and-probe figure (44/114) carries no such caveat.

### 5.4 The judge inside the score

Table 6. The judge as part of the reward (check 2j).

| quantity | value |
|---|---|
| live judge replies the stock strict parser would reject | 103/169 = 0.61 |
| assertion verdicts where the live single vote differs from a 3-vote majority | 1/243 |
| rewards that flip under the majority | 1 of 159 (task 110, fail → pass) |

With the substituted judge, the stock code would have rejected most replies, because they came in a code fence or as a bare array. In a live run such a simulation is retried and then dropped from the denominator as an infrastructure error. The overlay's tolerant parser kept these replies and marked each one.

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
| P7 | defective share | no numeric prediction; 44/114 static, 67/114 all checks |

P5 in detail:

- **Task 4:** the issue does not reproduce at the pinned commit. The scenario asks for the exact count, and all four runs pass.
- **Task 5:** the missing authentication check appears only as the benchmark-level 2m row.
- **Task 7:** the issue was not found.

The rows that sit on tasks 4 and 5 describe other mechanisms (`results/retail/upstream_issue_match.csv`).

### 5.6 Airline beside retail

Table 8. The same checklist on two domains (`retail/comparison.md`; airline is a sample of 20, retail the whole domain).

| quantity | airline | retail |
|---|---|---|
| tasks with ≥1 medium/high defect, static and probe checks | 13/20 = 0.65 | 44/114 = 0.39 |
| tasks with ≥1 medium/high defect, all checks | 18/20 = 0.90 | 67/114 = 0.59 |
| empty answer gets full reward (whole domain) | 23/50 = 0.46 | 6/114 = 0.05 |
| agent pass^3 | 12/20 = 0.60 | 75/114 = 0.66 |
| ground-truth agent reaches reward 1.0 | 11/16 | 89/112 |

Reading (interpretation): the two domains fail in different places. Airline's largest hole is the pass for doing nothing. Retail closes most of it with judged assertions and moves the weight onto the judge and the tools: an order rule the tools do not enforce, and a tool that stores the wrong item. The agent's pass^3 is similar in both domains while the defects underneath differ in kind. This repeats the block-1 observation: the headline number does not show the state of the exam.

## 6. What an agent that does nothing scores, across tau2

Table 9. Null agent: an empty trajectory pushed through the stock evaluators of every task set, with no model call (`results/null_agent/tau2_null_agent.md`).

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

Four external agent benchmarks, chosen from a desk survey of nine (`null_agent/external_candidates.md`), were then measured the same way: each with its own scoring code, installed in its own folder outside the repository, with no model call (`results/null_agent/external.md`). Next to the null agent, the table reports a refusal agent, which does nothing except give the benchmark's "cannot be done" answer.

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
| WebArena, original task file | 812 | not measured (needs the live sites) | 36 (4.4%, 3.2–6.1%) for the answer "N/A" | counted from the task file and the quoted scoring code |

- **BFCL V4.** All 10 points come from the two irrelevance subsets (240 and 884 entries), where making no function call is the correct answer; every other category scores 0. A refusal sentence scores the same. The live relevance subset, which would penalise never calling a function, carries no weight in the overall score.
- **tau-bench (original).** An agent that does nothing passes 19 of the 50 airline test tasks, and a hand-over to a human at step 0 passes the same 19, because it ends the episode with the database untouched. The tau2 airline tasks were rewritten and reordered, so 19 against tau2's 23 compares counts only. In retail, six tasks pass for doing nothing because their single reference write is rejected on replay (test 106; train 161, 214, 229, 288, 349), so the scored target is the starting state. Test task 106 is tau2 retail task 105: same order, items and gift card, and the tau2 action id still reads `106_0`. The original benchmark gives this task to an agent that does nothing; tau2 added an assertion that demands the exchange, which turned the free pass into a task no conversation can pass (Section 5).
- **OSWorld-Verified.** The environment returns success for a `FAIL` action on every task marked infeasible, so an agent that gives up at step 0 scores the infeasible share. That share depends on the task-file version: 30 of 369 as released and 26 of 369 at the current head, after five tasks received real checkers and one became infeasible. A published score therefore carries a refusal floor of 8.1% or 7.0%, depending on the version it was scored on.
- **WebArena.** In the original task file 36 tasks expect the answer "N/A" and score it by exact match, so that one answer passes all 36. WebArena-Verified closes most of this: the best single fixed refusal passes 24 tasks. Its evaluator has defects of its own: task 319 cannot be passed by any response tried, including the expected one; tasks 699, 700 and 811 end in an evaluator error on every response; and 10 map tasks pass for reporting success at step 0, because their only network check is met by loading the start page.

Outside tau2 the floor runs from 0 (WebArena-Verified, null agent) to 38% of tasks (original tau-bench airline), plus 10 of 100 points on BFCL V4.

## 7. Strong vs weak: does the exam separate a stronger agent?

The check was pre-registered in `strong_vs_weak/PLAN.md` and committed before any result of the run was read. It uses the same 20 sampled airline tasks with three trials each. The agent is `claude-sonnet-5-5`; everything else is unchanged: the user simulator `claude-haiku-5-5`, the seed, the scorer and the settings. Results are in `strong_vs_weak/summary.md`.

Table 10. Sonnet and Haiku on the same exam (20 sampled airline tasks × 3 trials).

| quantity | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| tau2 pass^1, stock scorer | 0.733 | 0.850 |
| tasks passed 3/3, stock scorer | 12/20 = 0.60 [0.39, 0.78] | 16/20 = 0.80 [0.58, 0.92] |
| tau2 pass^1, full v2 | 0.733 | 0.883 |
| tasks passed 3/3, full v2 | 11/20 | 16/20 |

- **Stock scorer.** Paired per task, Sonnet is ahead on 6 tasks, behind on 1 and equal on 13; the exact sign test gives p = 0.125. By the pre-registered rule, the exam does not separate the two models on this sample.
- **Tasks that carry no information.** Nine of the 20 tasks say nothing about the difference. The 7 tasks that an empty conversation passes give both models 3/3. Tasks 7 and 44, whose references are defective, give both models 0/3.
- **Full v2.** The gap widens to +0.150: 8 tasks ahead, 1 behind, 11 equal, p = 0.039. Most of the change comes from task 7, whose corrected reference total Sonnet reaches in 3 of 3 trials and Haiku in 1. This p value comes from one of three configurations compared on the same conversations, so it does not survive a Bonferroni correction (threshold 0.017).

All five predictions held. The check cost about $17.21: the run $16.85, the smoke simulation $0.14 and the re-score $0.22.

Reading (interpretation): the defects found in block 1 compress the measured difference between models. Free passes and impossible tasks tie both models, so a real gap has fewer tasks in which to show. Repairing one wrong reference answer moved the comparison across the conventional threshold. With 20 tasks and one run per model, the check cannot say how large the true gap is. It shows that the measurable gap depends on the exam's defects.

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
| I10 | the assertion evaluator and the JSON extractor fail on a bare top-level JSON array, which the judge model returns in about 9% of replies |
| I11 | retail: `modify_pending_order_items` stores the last variant's price and options in every modified item; the target hash depends on the pair order |
| I12 | retail: an address or payment change after an item change is accepted although the policy forbids it; 14 references reach the same hash in the forbidden order |
| I13 | retail reference defects: a product id that exists nowhere (2, 3, 4), an unreachable exchange (105), a transfer summary from another task (26), a no-op address write (110) |
| I14 | retail scoring path: an assertion the judge omits counts as met; the strict parser rejects most replies of the substituted judge |
| I15 | the text-mode user simulator lacks the "do not end prematurely" rule of the voice mode; the simulator is the largest cause of retail failures and flips |
| I16 | retail task texts a faithful simulator cannot follow to the reference (0, 1, 15, 34, 52, 100) |

## 9. What the numbers mean

Two facts stand side by side. The examination has reproducible faults: a pass for doing nothing on 23 of 50 tasks, an end-state check that fails valid solutions, a string check that passes by accident, a wrong reference answer, a scenario that forbids its own reference, requirements nobody scores, a simulator that improvises. And the agent's headline number barely moves when the examination is repaired: pass^3 0.60 in both runs, pass^1 within the noise floor. The leaderboard cannot show what is wrong with the exam. Finding it took a checklist applied to the procedure, probes with known answers, and reviews whose job was to overturn the findings.

The repair itself is instructive. The deterministic faults exist (they fire on perturbed trajectories) but did not flip a single recorded conversation, because the recorded agents happened not to hit them. The one fix that failed, task 32, failed because a sentence added to make the scenario consistent with the reference exposed a second agent error that the pre-test could not see. Both say the same thing: an examination has to be validated as an instrument, with pre-registered expectations and adversarial review, before its numbers are read.

Retail tests the claim on a whole domain (interpretation). Its scorer closes airline's largest hole, yet 44 of 114 tasks still carry an adversarially reviewed defect. The new holes sit in places a leaderboard never shows: a tool that stores the wrong item, an order rule only the policy text enforces, and a judge that would crash the stock parser on most replies. The conversations add a second lesson. In retail, the user simulator decides more outcomes than the reference does: it explains 12 of 23 ground-truth failures and 23 of 32 flips. A pass rate on this benchmark therefore measures the agent and the simulator together. The null-agent table puts the same point in one line: the score of an agent that does nothing ranges from 0% to 46% across domains of one benchmark, depending only on how each domain's exam is built. Four external benchmarks show the same spread, from 0 to 38% of tasks, and on OSWorld-Verified the refusal floor changed between two versions of the same task files. The strong-vs-weak check adds the consequence for model comparison. On the stock exam a stronger model is ahead on 6 of the 7 tasks where the two differ, yet the difference is not significant, because 9 of the 20 tasks tie both models by construction.

## 10. Limits

- **Scope.** Two domains of one benchmark: airline with 20 of 50 tasks sampled (its 30 unsampled tasks' assertions unaudited), retail with all 114 tasks.
- **Models.** One agent model and one simulator model, and a judge from the same family. In retail that judge replaces the stock OpenAI judge, so the parser figures describe the substitution.
- **Unreviewed rows.** The retail rows from the runs (1e, 4f, 5c, 5d) were not adversarially reviewed, and their 5d threshold differs between reviewer batches.
- **What v2 is.** The refusal pass is documented as intended, so v2 is a stricter alternative protocol rather than a bug fix.
- **Run-to-run noise.** Single-trial ground-truth runs flipped on 4 of 13 unchanged airline tasks between two runs, so ground-truth totals are read against that floor.
- **Strong vs weak.** One run per model and 20 tasks. The two runs are a day apart and the user simulator samples, so each run is one draw.
- **External floors.** Three of the nine external rows are counted from task files and quoted scoring code rather than measured by running the evaluator (OSWorld-Verified twice, original WebArena). The WebArena-Verified agents were scored with a synthetic start-page network trace, because its evaluator rejects an empty one.
- **Cost figures.** Dollar figures are own estimates from token counts at the published per-token prices. They were not reconciled with billing row by row; the account's billing was about $11 when the own estimate was $10.79.

## 11. Reproducibility and cost

Every number is rebuilt by the command sequences in `STRUCTURE.md`; the judge stages replay from cached votes without a model call. Provenance stamps on every v2 output record the overlay commit and a dirty-tree flag; the live runs record the runner configuration and its empty diff against block 1. Spend, own estimate from token counts: block 1 about $1.36, block 2 about $2.27, retail about $7.16 (runs $6.86, re-judge $0.30, probe below one cent); the strong-vs-weak check about $17.21; about $27.99 in total (`cost.md`). The null-agent tables and the demo make no model call; the external benchmarks are installed in their own folders outside the repository, with the commands in `results/null_agent/external.md`.

## 12. Open items

Not done, candidates for a next iteration:

- **Strong vs weak, more power.** Repeat the comparison on all 50 airline tasks or with a second run per model, so that a gap of the observed size can reach significance.
- **External null agent, remaining runs.** Run the do-nothing agent on OSWorld-Verified (needs its virtual machine) and on the original WebArena (needs the live sites). Check whether published tau-bench airline scores use the 50 original test tasks and this reward code: the HAL leaderboard lists 28.00% for a cheap model, which would then sit 10 points below the do-nothing floor of 38.0%.
- **External defects.** The defects found in tau-bench (six retail tasks whose single reference write is rejected) and in WebArena-Verified (tasks 319, 699, 700, 811 and the 10 map tasks) are recorded in `results/null_agent/external.md`; no issue text is drafted for them.
- **Retail run rows.** Give the retail run rows an adversarial pass.
- **Task 32.** Run a counterfactual ground-truth conversation on airline task 32 without the payment-method sentence, to isolate its effect.
- **Judge hand-check.** Hand-check about 20 fresh judge-only verdicts blind.
- **Airline coverage.** Audit the assertions of the 30 unsampled airline tasks.
- **Upstream issues.** Decide which of the issue drafts I1–I16 to file.
