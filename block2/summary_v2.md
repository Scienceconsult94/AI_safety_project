# Block 2 — results: scorer v2 and tasks v2 against the pinned benchmark

All numbers are rebuilt from `results/v2/*` by `scripts/v2/make_summary_v2.py`. Intervals are Wilson 95%; paired comparisons on identical trajectories are given as discordant counts with an exact McNemar p. Block-1 numbers are never recomputed here; the v1 columns come from the recorded block-1 files. v2 is a stricter, documented alternative scoring protocol laid over the pinned benchmark, not a claim that the benchmark's own protocol is 'wrong' where its documentation states a choice (the refusal pass, `docs/evaluation.md`).

Provenance of the re-score: scorer v2, overlay commit 5f4d92a, judge anthropic/claude-haiku-5-5 (provider-default sampling, args {}), view with_tool_calls, prompt c560776f121c1500, 3 votes.

## H1 — tasks an agent passes by doing nothing

| trajectory | scorer | all 50 tasks | 20 sampled |
|---|---|---|---|
| empty trajectory (static scan) | v1 | 23/50 = 0.46 [0.33, 0.60] | 7/20 = 0.35 [0.18, 0.57] |
| empty trajectory | v2 (rule) | 0/50 = 0.00 [0.00, 0.07] | 0/20 = 0.00 [0.00, 0.16] |
| greeting + one user turn (block-1 2b probe) | v2 (rule) | 0/23 of the no-op tasks | 0/7 |
| refusal bot, no tool calls (judged) | v2 | 14/23 = 0.61 [0.41, 0.78] of the no-op tasks | 5/7 |
| refusal bot, process-class assertions excluded | v2 | 17/23 | |

Provenance of the refusal-bot probe: overlay commit a4f86e7, dirty flag False (re-run on a clean overlay; the cached ballots of the first run were replayed).

Under v1 every one of the 23 no-op tasks is passed by an agent that changes nothing and says nothing required. Under v2 the empty trajectory and the 2b probe fail by rule; a refusal bot still passes the tasks whose assertions are all of the 'does not do X' kind, which tau2 documents as the intended outcome. The design review predicted about 13 of 23 such passes before the measurement. The 30 tasks outside the sample carry assertions that were not audited in block 1.

## H2 — WRITE-order permutation probe (reference actions reordered)

| hash | permutations whose DB hash differs from the reference | tasks affected |
|---|---|---|
| v1 raw | 24/78 | 7, 23, 32 |
| v2 canonical | 4/78 | 7, 32 |

The permutation count per task is capped at 24 (task 18 has 5 writes = 119 other orders, 24 tested). Remaining canonical differences are orders that change the outcome (task 7: cancelling before upgrading changes the refund; task 32: changing flights before the cabin upgrade changes the payments). Argument-list order (passengers in task 8, payment methods in task 20) is covered by the selftest and the engagement gate, not by this probe.

Engagement gate (perturbed real trajectories; must flip before any v2 number is reported): passengers_reversed task 8: 0.0→1.0 ok; payments_reversed task 20: 0.0→1.0 ok; bookings_swapped task 23: 0.0→1.0 ok; comm_1327_only task 23: 1→0 ok.

## H3 — the 76 recorded block-1 simulations re-scored

Replay gate: the stock scorer reproduces the recorded reward of all 76 (`replay_check.csv`). One switch at a time on tasks v1, all three together, tasks v2 with the stock scorer, and V2 (tasks v2 + all switches).

| config | haiku sims passing (60) | haiku tasks 3/3 (20) | haiku pass^1 (mean over tasks) | GT sims passing (16) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|
| v1 | 44/60 | 12/20 = 0.60 [0.39, 0.78] | 0.73 | 11/16 = 0.69 [0.44, 0.86] | 55/76 | 55/76 |
| S_hash | 44/60 | 12/20 = 0.60 [0.39, 0.78] | 0.73 | 11/16 = 0.69 [0.44, 0.86] | 55/76 | 55/76 |
| S_comm | 44/60 | 12/20 = 0.60 [0.39, 0.78] | 0.73 | 11/16 = 0.69 [0.44, 0.86] | 55/76 | 55/76 |
| S_nl | 43/60 | 11/20 = 0.55 [0.34, 0.74] | 0.72 | 11/16 = 0.69 [0.44, 0.86] | 54/76 | 55/76 |
| S_all_t1 | 43/60 | 11/20 = 0.55 [0.34, 0.74] | 0.72 | 11/16 = 0.69 [0.44, 0.86] | 54/76 | 55/76 |
| T2_stock | 45/60 | 12/20 = 0.60 [0.39, 0.78] | 0.75 | 11/16 = 0.69 [0.44, 0.86] | 56/76 | 56/76 |
| V2 | 44/60 | 11/20 = 0.55 [0.34, 0.74] | 0.73 | 11/16 = 0.69 [0.44, 0.86] | 55/76 | 56/76 |

Flips v1 → V2 on identical trajectories: 2 of 76 (b=1, c=1, exact p=1.000).

| agent | task | trial | v1 | V2 | first component that changes it | what failed / why |
|---|---|---|---|---|---|---|
| haiku | 9 | 0 | 1.0 | 0.0 | nl_enforce | Check that Agent searched for direct flights between JFK and |
| haiku | 7 | 0 | 0.0 | 1.0 | criteria text | by construction: communicate_info 1628 → 708 and the transcript states $708;  |

DB mismatches under v1: 20; order-only among them (closed by canonicalisation): 0. Communicate flips from `comm_boundary` alone: 0. Gold-action replay errors: 0. So on these 76 conversations the two deterministic switches have no observed effect; the block-1 2g/2h mechanisms are shown by construction (selftest and engagement gate on perturbed trajectories), not by a flip in a recorded conversation.

Passes under v1 that fail once `nl_assertions` count (S_nl): 1 of 55 v1 passes (tasks 9). Undetermined judge verdicts after re-asks: 0.

First judge pass with tau2's stock transcript view (kept as `rescore_stockview.csv`): 3 flips (haiku/9/t0, haiku/7/t0, haiku/9/t1); task 9 trial 1 was a judge error caused by the view hiding tool-call arguments (issue I9).

## The judge as an instrument

claude-haiku-5-5 (the agent's own model: self-evaluation risk), 3 votes per assertion, provider-default sampling. Recorded conversations: 271 (trajectory, assertion) pairs in `judge_votes.csv`; real disagreements (both met and unmet among the determined ballots) 1/271; pairs with at least one discarded ballot 8 (8 ballots). Live runs and fresh re-score: 316 pairs; real disagreements 2; pairs with a discarded ballot 19 (24 ballots).

Parser gap (found in the results review): tau2's `extract_json_from_llm_response` slices from the first `{` to the last `}`, so a reply that is a bare JSON array is rejected and its ballot dropped; 53 of 610 judge replies were such arrays. `scorer_v2.parse_judge_reply` now accepts the array (selftest). Offline re-parse of the discarded replies (`results/v2/judge_reparse_check.md`): 32 ballots recovered, 0 majority verdicts changed, so the cached rewards stand. Passes whose NL part rests on fewer than 3 determined ballots: recorded haiku/3/t0 (2 ballots), recorded haiku/20/t1 (2 ballots), fresh haiku/21/t0 (2 ballots), fresh haiku/37/t1 (2 ballots), fresh haiku/44/t2 (1 ballot), fresh gt3/7/t2 (2 ballots).

Check of judge verdicts by two model readers (`block2/judge_handcheck.md`): 46 items = all reward-changing, process-class and communication-class verdicts of the recorded conversations (classes: communication 28, db_dup 6, process 12; negative-class verdicts 0; the mandatory classes exceeded the fill target, so no random item was drawn); the first model reader and the blind second model reader agree with the judge 46/46. Fresh-run verdicts were not checked by the model readers: 35 of 66 fresh passes contain at least one assertion that only the judge decides (not duplicated by the DB check); fresh failures decided by the judge alone: 0. Unanimity measures repeatability, not validity (the stock-view pass was 255/255 unanimous and wrong on task 9 t1).

## Task 32 — does the text fix work? (counterfactual simulator probe)

| task text | arm | ACCEPT | REFUSE | UNCLEAR | a/b agreement | cost |
|---|---|---|---|---|---|---|
| v1 (block 1, `results/probe_32/`) | two_step | 0 | 10 | 0 | 10/10 | — |
| v2 | two_step | 10 | 0 | 0 | 10/10 | ≈ $0.0041 |
| v2 | step1_only | 8 | 1 | 1 | 10/10 | ≈ $0.0055 |
| v2.1 | two_step | 8 | 0 | 2 | 10/10 | ≈ $0.0064 |
| v2.1 | step1_only | 0 | 10 | 0 | 10/10 | ≈ $0.0043 |

Rules fixed beforehand (`scripts/v2/probe_32_v2.py`): two_step ACCEPT ≥ 8/10 = the fix works; step1_only ACCEPT ≥ 8/10 = the net clause over-corrects, REFUSE ≥ 8/10 = it behaves. The v2 wording over-corrected (step1_only 8 ACCEPT), so the wording was tightened to v2.1, which `block2/tasks_airline_v2.json` carries; details and the post-run observation on the refund destination in `block2/task_fixes.md`.

## H4, H5 — fresh runs on the v2 benchmark

Two effects are mixed in a fresh run (changed task text and changed scoring) plus simulator noise. The per-trajectory re-score below separates them: scorer effect = T2_stock vs V2 on the same fresh conversations; criteria effect = v1 vs T2_stock. Noise control: the 15 sampled tasks nothing was changed on, and the 17 tasks whose change is invisible to agent and simulator (tasks 8 and 23 changed only in `nl_assertions`, which only the evaluator reads).

### Haiku agent, 20 tasks × 3 trials

| metric | block-1 run (v1 benchmark) | fresh run (v2 benchmark) |
|---|---|---|
| pass^1 (mean over tasks) | 0.73 | 0.78 |
| tasks passed 3/3 | 12/20 = 0.60 [0.39, 0.78] | 12/20 = 0.60 [0.39, 0.78] |
| trials passed on the 15 untouched tasks (noise control) | 40/45 | 40/45 |
| trials passed on the 17 agent-invisible tasks (noise control) | 44/51 | 43/51 |
| trials passed on the 3 agent-visible fixed tasks (7, 32, 44) | 0/9 | 4/9 |

Run-to-run noise: the untouched-task totals agree, but 6 of 45 trial slots changed outcome on the 15 untouched tasks and 9 of 51 on the 17 agent-invisible ones (same seeds per trial in both runs; the simulator and agent are sampled at provider defaults). Any per-task difference below that floor is noise.

| task | changed in v2 | block-1 trials | block-1 pass | v2 trials | v2 pass |
|---|---|---|---|---|---|
| 1 |  | 111 | 3/3 | 111 | 3/3 |
| 3 |  | 111 | 3/3 | 111 | 3/3 |
| 7 | yes | 000 | 0/3 | 000 | 0/3 |
| 8 | yes | 100 | 1/3 | 110 | 2/3 |
| 9 |  | 111 | 3/3 | 111 | 3/3 |
| 10 |  | 111 | 3/3 | 111 | 3/3 |
| 11 |  | 110 | 2/3 | 111 | 3/3 |
| 16 |  | 101 | 2/3 | 110 | 2/3 |
| 19 |  | 001 | 1/3 | 101 | 2/3 |
| 20 |  | 111 | 3/3 | 111 | 3/3 |
| 21 |  | 111 | 3/3 | 110 | 2/3 |
| 22 |  | 101 | 2/3 | 001 | 1/3 |
| 23 | yes | 111 | 3/3 | 100 | 1/3 |
| 26 |  | 111 | 3/3 | 111 | 3/3 |
| 28 |  | 111 | 3/3 | 111 | 3/3 |
| 32 | yes | 000 | 0/3 | 010 | 1/3 |
| 37 |  | 111 | 3/3 | 111 | 3/3 |
| 44 | yes | 000 | 0/3 | 111 | 3/3 |
| 46 |  | 111 | 3/3 | 111 | 3/3 |
| 48 |  | 111 | 3/3 | 111 | 3/3 |

GT run-to-run noise: on the 13 GT tasks whose scenario did not change, the single-trial outcome flipped on 4 (16, 19, 21, 23); the GT total is read against that floor.

### Ground-truth agent, 1 trial (16 tasks with reference actions)

| task | block-1 GT | v2 GT trials |
|---|---|---|
| 1 | 1 | 1 |
| 3 | 1 | 1 |
| 7 | 0 | 1 |
| 8 | 1 | 1 |
| 9 | 1 | 1 |
| 11 | 1 | 1 |
| 16 | 0 | 1 |
| 19 | 1 | 0 |
| 20 | 1 | 1 |
| 21 | 1 | 0 |
| 22 | 1 | 1 |
| 23 | 0 | 1 |
| 32 | 0 | 1 |
| 37 | 1 | 1 |
| 44 | 0 | 0 |
| 48 | 1 | 1 |

v2 GT passes: 13/16 trials; block-1 GT 11/16 = 0.69 [0.44, 0.86].

### Ground-truth agent, 3 trials on the text-fixed tasks 7, 32, 44

| task | block-1 GT | v2 GT trials |
|---|---|---|
| 7 | 0 | 111 |
| 32 | 0 | 000 |
| 44 | 0 | 111 |

v2 GT passes: 6/9 trials.

- `v2_sample20_pass3_haiku`: 60 sims, infra errors 0, 1064 s; agent+user tokens in/out 7,944,134/336,795 ≈ $0.963; judge calls 197 ≈ $0.173; overlay commit bafdbdc; own estimate at $0.10/$0.50 per MTok, cache ignored, not reconciled with the Console; Info diff vs block 1: {}.
- `v2_sample20_gt_haiku`: 16 sims, infra errors 0, 304 s; agent+user tokens in/out 2,072,217/88,254 ≈ $0.251; judge calls 51 ≈ $0.045; overlay commit d55bd49; own estimate at $0.10/$0.50 per MTok, cache ignored, not reconciled with the Console; Info diff vs block 1: {}.
- `v2_gt3_haiku`: 9 sims, infra errors 0, 268 s; agent+user tokens in/out 1,827,754/90,096 ≈ $0.228; judge calls 32 ≈ $0.040; overlay commit d55bd49; own estimate at $0.10/$0.50 per MTok, cache ignored, not reconciled with the Console; Info diff vs block 1: {}.

### The fresh v2 conversations scored under each protocol

| agent | sims | v1 (tasks v1, stock) | T2_stock (tasks v2, stock) | V2 | criteria effect v1→T2_stock (1→0, 0→1) | scorer effect T2_stock→V2 (1→0, 0→1) |
|---|---|---|---|---|---|---|
| gt | 16 | 12 | 13 | 13 | 0, 1 (b=0, c=1, exact p=1.000) | 0, 0 (no discordant pairs) |
| gt3 | 9 | 3 | 6 | 6 | 0, 3 (b=0, c=3, exact p=0.250) | 0, 0 (no discordant pairs) |
| haiku | 60 | 47 | 47 | 47 | 0, 0 (no discordant pairs) | 0, 0 (no discordant pairs) |

Fresh conversations that would fail if the *v1* assertions were enforced but pass under V2 (an assertion-text fix preventing a false failure): gt/23/t0 — Agent books a round-trip reservation from JFK to SFO in busi.

Haiku on the text-fixed tasks in the sample (7, 8, 23, 32, 44), trials passing under V2: 7/15; block-1 trials on the same tasks: 4/15. Restricted to the three tasks whose scenario the agent and simulator actually see (7, 32, 44): 4/9 vs 0/9 in block 1; tasks 8 (+1) and 23 (−2) moved without any agent-visible change.

## Verdicts on the pre-registered hypotheses

| hypothesis | verdict | evidence |
|---|---|---|
| H1 no-op pass | supported for the rule part; the judged part is a protocol choice | empty trajectory 23/50 under v1 -> 0/50 under v2; refusal bot still passes 14/23 no-op tasks, which tau2 documents as intended |
| H2 order-sensitive hash | supported | reference-action permutations with a differing hash 24/78 -> 4/78; the 4 are outcome-changing orders |
| H3 recorded conversations | deterministic switches: no observed effect (0 flips in 76); nl_enforce: 1 flip (task 9 t0); criteria text: 1 flip (task 7 t0) | H3 table and flip table above |
| H4 GT passes the fixed tasks | task 7: supported (4/4); task 44: supported with caveat (3/4, the single-trial GT run fails); task 32: **failed** (1/4) | GT tables; task-32 reading note |
| H5 Haiku pass^3 differs under v2 | no difference detected | tasks passed 3/3: 12/20 vs 12/20 (pass^3 0.60 = 0.60); pass^1 0.73 -> 0.78 within the noise floor above |

## Reading the result

- A pass that disappears under V2 on the *same* conversation is a pass the scoring protocol produced, not the agent; a failure that disappears is a failure the protocol produced. Each flip is attributed to the component that first changes it.
- The task-7 trials that gain a pass under tasks v2 do so by construction of the fix (the reference arithmetic was wrong). On the fresh conversations the three scorer switches change no reward (T2_stock = V2); every fresh difference from block 1 is task text or run-to-run noise, and the noise-control rows above give the floor.
- Task 44 (block 1: no upgrade executed in any of the 4 conversations — two escalated over cancellation requests, one over a total quoted without KC18K6; fresh: all 3 Haiku and all 3 GT-3 trials execute the three upgrades, and then still transfer to a human over the S61CZX cancellation; the single GT trial transfers before upgrading). The per-segment wording moves the upgrades ahead of the S61CZX conflict, which the fix does not touch; the pass depends on that order.
- Task 32 (fresh 2/7: Haiku 1/3, GT 1/1 and 0/3; block 1: 0/4). The budget clause no longer blocks the two-step path. In all 7 fresh conversations the agent states that refunds go to the original payment method (the gift card); policy.md line 131 lets the user name the card for a flight change and the tool refunds to the `payment_id` passed, so the statement is wrong — and the GT agent makes it while holding the gold `payment_id`. The post-run reading blamed the appended sentence 'any charge or refund should go to your Visa' for turning this error into a failure (`block2/task_fixes.md`, post-run observation); a later pre-registered test did not support it: the GT agent passed 2 of 10 trials with the sentence and 2 of 10 without it (`airline_full/cf32.md`). In 2 of the 3 GT-3 trials the simulator also invented that two passengers were not travelling. Both passes are untidy: the GT pass ends with two transfer calls after the target DB is reached. H4 fails for task 32.
- Task 23 (3/3 → 1/3): a DB mismatch, the agent changes the flights on K1NW8N instead of cancelling and rebooking three reservations; the reference needs the simulator to volunteer the three-way split (block-1 row 5d), which it did 3/3 in block 1 and 1/3 here. Task 23's own edit touched only `nl_assertions`.
- pass^1 here is tau2's pass^k with k=1: the mean over tasks of passing trials / 3 (block 1: 44/60 = 0.73; fresh: 47/60 = 0.78). Block 1's headline 'pass^1 = 0.80' in `results/agent_runs_summary.md` is a non-standard label for a different quantity, the share of tasks whose first trial passes (16/20); the two definitions coincide for pass^3 (0.60 in both runs).
- The judge is a model, run on the agent's own model family; its repeatability (unanimity) is not its validity, so reward-changing verdicts are checked by two model readers and reported with bounds.
- Limits: 20 tasks of one domain; the user simulator is unchanged (category-5 noise persists); assertions of the 30 unsampled tasks were not audited; the pinned benchmark documents the refusal pass as intended, so v2 is an alternative protocol.
