# Skeptic check of the agent-run review (checks 1e, 4f, 5c, 5d)

Date: 2026-10-27. Object: `results/review_agent.csv` (33 rows, 15 with defect=1) and `results/review_agent.md`.
Read directly: all 29 trajectories in `results/trajectories/`; task cards 7, 8, 11, 16, 19, 22, 23, 32, 44; `tau2-bench/data/tau2/domains/airline/policy.md`; `tau2-bench/src/tau2/user/guidelines.py` (text scaffolds); `tau2-bench/src/tau2/domains/airline/tools.py` (`update_reservation_flights`, `_payment_for_update`, `cancel_reservation`, `_get_new_reservation_id`); the per-simulation persona recorded in `results/runs/sample20_pass3_haiku.results.json` and `sample20_gt_haiku.results.json` (`language_context.persona`); `tau2-bench/data/tau2/multilingual/en/pack.yaml`. No model calls, no replays, nothing under `tau2-bench/` changed. Row-level verdicts: `results/skeptic_verdicts_agent.csv`.

Terms: GT = ground-truth agent `llm_agent_gt` (sees the reference actions); t0/t1/t2 = Haiku trials 0-2; DB = database. Classes: A agent slip, B user-simulator deviation, C defensible alternative reading, D reference or scoring problem.

## 1. Verdicts

| task | check | review | skeptic | decisive evidence |
|---|---|---|---|---|
| 7 | 4f | 1 | confirmed | 1628 = 402+296+624+306 includes both reservations being cancelled; t0 asked after both cancellations (708); t2 asked for flights "besides those two" |
| 8 | 5c | 1 | confirmed | t1 agent offered the exact reference booking; the simulator refused (simulator-side flip, root cause a scenario gap) |
| 8 | 5d | 1 | rejected | refusal wording is the assigned persona's script; the seat wish is in the scenario; no fact invented |
| 11 | 5c | 1 | confirmed | agent turns match t0/t1; simulator invents "not a gift card" |
| 11 | 5d | 1 | confirmed | contradicts the DB fact the agent stated and the scenario goal |
| 16 | 5d | 1 | confirmed | GT: "not my original card" after the agent said the gift card is the original payment |
| 19 | 5c | 1 | confirmed | t1 asks the agent to rebook, against "You will book the flight again yourself later" |
| 19 | 5d | 1 | confirmed | t1/t2 rebooking; t0 withholds the instructed insurance cancellation |
| 22 | 5c | 1 | rejected | agent turn 13 differs materially between t0 and t1; t1 agent falsely says the reservation cannot be modified, and the scenario tells the simulator to end in that case |
| 22 | 5d | 1 | confirmed (weak) | turn 14 contradicts the scenario premise; induced by the agent's framing |
| 23 | 5d | 1 | confirmed | instructed three-reservation split withheld at its trigger (turns 16-19), raised at turn 25 |
| 32 | 1e | 1 (high) | rejected | arithmetic holds, but no run presented the net refund correctly; the GT failure traces to agent misstatements |
| 32 | 5d | 1 | confirmed | "I didn't book this for anyone else" / "only supposed to be on this reservation myself" are fabricated |
| 44 | 4f | 1 | confirmed | KC18K6 is 7 h end to end incl. a 2 h layover; t0/t2 exclude it from the upgrades |
| 44 | 5d | 1 | rejected | supervisor demands are the persona's script; t2 reacts to the agent's shifting totals; the residual linkage is gap-filling |
| 7 | 5d | 0 | should be 1 | "change of plan" invented in 3 of 4 runs against "You are sick"; t0 "I never used a 2135 card" after three corrections |

Counts: 15 defect=1 rows checked, 11 confirmed, 4 rejected; 1 defect=0 row should be 1.

## 2. Cross-cutting finding: the "asks for a human" pattern comes from the assigned persona

The English pack defines one male and one female simulator persona (`pack.yaml`). `assign_persona` (`src/tau2/multilingual/runtime.py`) chooses by `caller_gender` from `airline_metadata_en.json`. As recorded in every simulation, tasks 8, 19 and 44 ran with `priya_patil`, and tasks 7, 11, 16, 22, 23 and 32 ran with `mamadou_diallo`. The `priya_patil` clauses in the simulator prompt include:
- "When you're not getting somewhere fast, asking for a supervisor or a timeline early is characteristic"
- "No, that doesn't work for me"
- "Can I just talk to someone who can actually fix this"

These phrases appear verbatim in 8 t1 turn 17, 19 t0 turn 13, 44 GT turn 23, 44 t0 turns 27/35 and 44 t1 turns 23/25. The text scaffold in `guidelines.py` has no rule against asking for a human. It only says to follow the scenario strictly, not to invent information, and to emit ###TRANSFER### when transferred. Consequences:
- Asking for a human is allowed, and for female-caller tasks it is scripted. It counts as a deviation only where it replaces an instruction the scenario gives for that situation (19 t0: "If basic economy cannot be modified, you are willing to cancel ...").
- In 8 and 44 the scenario has no instruction for a predictable denial: seat selection does not exist, and the S61CZX cancellation has no covered reason. The escalation there is persona behaviour inside a scenario gap, which is a task-design finding, not simulator infidelity.
- Pass rates do not differ by persona overall (21/30 vs 23/30 trials), and persona is confounded with task. No claim is made beyond these three tasks.
- 7 t0 is a different case: the agent itself offered the transfer (turn 36).

## 3. Task 32, check 1e (high): rejected

Recomputation. In `tools.py`, a kept flight keeps its old price only if the cabin is unchanged, and fare differences are multiplied by the number of passengers.
- Step 32_3 (economy on HAT202+HAT232): (196 + 110) x 3 - (94 + 80) x 3 = 918 - 522 = +396 to credit_card_9659780.
- Step 32_4 (HAT041 economy): 136 x 3 - 918 = -510 to the same card. Net -114.
- A one-step change from basic economy to HAT041 economy gives 408 - 522, a single -114 payment entry and therefore a different hash. Reversing the steps is not possible, because basic economy flights cannot be changed. Gift cards (183, 224) cannot cover step 1. The reference path is therefore the only path to the target hash, and it requires the user to confirm a +396 charge first. This part of the review holds.

The claim that "a literal simulator refuses it in all 4 runs" does not hold. In none of the 4 runs did the agent state plainly that step 1 charges 396, step 2 refunds 510 to the same card, and the user ends up 114 ahead.
- GT: quotes 132 (the per-passenger figure). At turns 17/19 it says the nonstop is impossible within the 100 limit and never mentions the step-2 refund. The user asked twice for any option under 100 (turns 16, 18). The GT agent had 32_4 in its reference and had seen the HAT041 price at turn 9.
- t1: turn 28 says step 2 "would add more to the cost"; in fact it refunds 510. The simulator also fabricates that it is the only passenger (turns 23/27).
- t2: the user frames the cap as a total ("keep the total under $100", turns 12, 21, 23). The agent replies "I don't see any option that keeps the total under $100" (turn 24), which is false under the total reading.
- t0: the only run that states the net (turn 24). Before that, the agent called step 1 "not under $100" (turn 20). It said the refund would go to the gift card within 5-7 days, although for a flight change the policy lets the user choose the refund method and the reference uses the same card. It offered an off-reference one-step change (turn 22). At turn 24 it closed the two-step path itself ("Since you don't want to pay $396 at any point, I can't do the upgrade by itself"). Only after that did the simulator decline to pay that much "up front" (turn 25).
- The simulator's own wording in t0 and t2 ("under $100 total for the change") supports the total reading, under which the reference is acceptable.

Classes: GT A (D contributing); t0 A (B/D contributing); t1 A + B; t2 A. The 1e rule excludes failures that trace to an agent slip, so 1e=1 is not supported. Correct value: 0 (unclear), and the "high" severity is not earned. The static 4a "uncertain" note stays uncertain: these runs neither confirm nor refute it. 32/4f=0 stays, but its justification ("all failures class D") is wrong, because the failures are A-dominant and not C.

## 4. Task 7, check 4f: confirmed

Upcoming reservations at 2024-05-15 15:00, with the amount paid: 7WPL39 402, XEHM4B 296, 59XX6W 624, 3EMQJ6 306. A90KR2 (May 14) and 9MRJD4 (May 6/13) are in the past.
- 402 + 296 + 624 + 306 = 1628, the expected string. It counts all four reservations, including the two that the same reference cancels.
- 402 + 296 + 306 = 1004 (GT turn 23, t1 turn 25, t2 turn 25): the reservations still active after 59XX6W was cancelled.
- 402 + 306 = 708 (t0 turn 30): the reservations active after both cancellations.

Neither "1628" nor "1,628" appears in any transcript. t0 asked at turn 24, after both cancellations. In t2 the simulator asked for flights "besides those two" (turn 19), and the literal answer to that is 708. 1628 is correct only if the question is answered before any cancellation and "other" is read as "all". The agents' answers are defensible (C, arguably D). The review's rationale repeats the static 4a note and misses the t2 wording, which is the strongest evidence in the transcripts.
7/1e = 0 (unclear) is right. The GT agent refused a reference path that the policy permits ("would get around those rules", turn 11) on its own judgment, and t0 reached db_match=True.

## 5. Task 44, check 4f: confirmed

KC18K6 is HAT300 06:00-09:00 EST, a 2 h layover, then HAT215 11:00-13:00: 7 h end to end. "Under or equal to 3 hours (including layovers)" excludes it, yet the reference 44_19 upgrades it. t0 (turn 24) and t2 (turn 20) apply this literal reading. GT figures recomputed from its own search results: HAT300 business 460 + HAT215 business 386 = 846 (GT said 805), and upgrade total (637 + 846 + 237) - 333 = 1387 (GT said 1346). t1 gives 1387 correctly.
44/1e = 0 (unclear) is right, but because the causes are mixed. The GT run has agent slips: the false "no layovers", wrong totals, and a transfer while three in-scope upgrades were pending. It also has task-side pressure: the layover clause conflicts with the reference, and the scenario gives no instruction for the denied cancellation, which combines with persona escalation. The review's stated reason ("reference policy-consistent, every value available") does not address the conflict between scenario and reference. The same standard would have given 0 for task 32 too.

## 6. Other 5c and 5d rows

- 8/5c confirmed. The task passed 1/3. In t1 the agent proposes exactly 8_3 at turn 16. The t2 flip is the agent's ("only one economy seat" against 3 in the search). The t1 refusal is the persona acting inside a scenario gap: the instability is real, but its root is scenario design.
- 8/5d rejected (see section 2). The scenario states the seat want and gives no fallback, and t0 resolved the same gap the other way. No fact is invented, withheld or contradicted.
- 11/5c and 11/5d confirmed. The agent's turns 12/19/21 match t0 (accepted at turn 17) and t1 (accepted at turn 18). The simulator says "original payment method, not a gift card" at turn 13, then declines and stops at turns 20/22.
- 16/5d confirmed. GT turns 15/17/21 insist on "my original card" after the agent stated at turn 16 that the original payment was gift_card_8887175. This contradicts "You are happy with original payment for refund".
- 19/5c and 19/5d confirmed on t1. The simulator invents "today" (turn 13) and asks for a new booking (turn 21), against "You will book the flight again yourself later". t2 does the same and succeeds only because it withholds a date of birth that the scenario does not give (turns 33-37). Withholding it is guideline-compliant; the wording at turn 37 leaks the scenario. t0 is weaker: the persona line plus an immediate agent transfer without offering the cancellation (A contributing).
- 22/5c rejected. The review's "near-identical agent summary" is wrong. In t0, turn 13 offers "other changes that are allowed" and asks what change is wanted. In t1, turn 13 says "not you" and "cannot be modified" and asks for the date or passenger names, and turns 15/17 repeat "can't be modified". Under the policy that is false: cabin, passengers and bags can all change. The scenario makes the user reactive and says "If agent mentions that any of those changes are not possible, move on and end the conversation", and the t1 ending follows that instruction. The flip traces to the agent.
- 22/5d confirmed, weak. Only turn 14 ("should be under my name, Omar Rossi") counts. It contradicts the scenario premise and is induced by the agent's framing.
- 23/5d confirmed. The trigger fires at turns 16-18. The simulator confirms a one-certificate booking at turns 17/19 and proposes the split only at turn 25. A co-cause: at turn 22 the GT agent made a non-reference three-passenger booking, although its reference lists three single-passenger bookings. 23/1e = 0 is right, since Haiku 3/3 shows the target is reachable.
- 32/5d confirmed: fabricated passenger facts (GT turn 24, t1 turns 23/27).
- 44/5d rejected as evidenced (see section 2). Residual evidence: in t0 turn 27 and t1 turn 25 the simulator makes the upgrades conditional on an impossible cancellation. That is gap-filling and borderline. t2 turn 27 ("firm total in writing") follows the agent's correction from 874 to 647 and its statement that it "can't confirm that nothing else will be added".
- 7/5d should be 1. The simulator invents "change of plan" in GT turn 3, t1 turn 9 and t2 turn 3, while the scenario says "You are sick". In t0 turns 33/37 it asserts "I never used a 2135 card for it" after the agent's corrections at turns 25/32/36. The review scored an agent-induced invention (22) and outcome-irrelevant inventions (32) as 1, so 7 must be 1 under the same standard.

Rule applied to 5d: fabricated facts, contradictions of the scenario, and withheld instructed actions count. Persona-scripted escalation and choices made inside a scenario gap do not count; they are recorded as design findings.

## 7. Internal consistency

- C implies 4f=1: holds (tasks 7, 44). Task 32 is not C.
- A simulator-caused flip implies 5c=1 and 5d=1: this holds in the review. After this check, task 8 has 5c=1 and 5d=0. That is deliberate: the flip runs through the simulator but comes from a scenario gap and the persona, not from infidelity. If the audit keeps the rule strictly, re-file task 8's instability as a task-design defect rather than forcing 5d=1.
- The review applies inconsistent standards: (a) 32/1e=1 but 44/1e=0, although both GT runs combine agent slips with a conflict between scenario and reference; (b) 7/5d=0, but 22/5d=1 and 32/5d=1 for the same kind of invention; (c) the note on task 22 admits the agent contributed but still scores 5c=1.
- Minor misstatements:
  - The 32 t0 summary ("user refuses because the scenario requires separate steps") mixes the refusal of the one-step change (turn 23) with the refusal of the two-step change (turns 21/25).
  - Observation 5 lists 7 t0 as a human request started by the simulator; the agent offered it (turn 36).
  - The 32 t0 simulator leak "My instructions are to do this in two separate steps" (turn 23) is not recorded.

## 8. Anchoring

There is no sign of wholesale copying: turn citations are specific and, apart from the items above, accurate. Two verdicts follow the static notes rather than the transcripts:
- 32: the D class adopts the static 4a hypothesis ("a literal user simulator may refuse step 1") and calls it confirmed in every run, without controlling for the fact that no agent presented the net refund.
- 7: the 4f rationale restates the static 4a note ("other upcoming flights" read literally) and misses both the timing (t0) and the "besides those two" wording (t2).

A separate problem, not anchoring: the simulator prompt (persona) was not checked, so persona-scripted behaviour was scored as simulator deviation.

## 9. Effect on the headline numbers (`summary_numbers.md`)

| quantity | review | after this check |
|---|---|---|
| 1e defect rows / category 1 Solvability | 1 (task 32) / 1/20 | 0 / 0/20 = 0.000 [0.000, 0.161] |
| 5c defect rows | 4 (8, 11, 19, 22) | 3 (8, 11, 19) |
| 5d defect rows | 8 (8, 11, 16, 19, 22, 23, 32, 44) | 7 (7, 11, 16, 19, 22, 23, 32) |
| 4f defect rows | 2 (7, 44) | 2 (7, 44) |
| tasks with agent_run defects | 9/20 | 9/20 (unchanged; every affected task keeps another row) |
| agent_run defects excluding 5d | 7/20 | 5/20 = 0.250 [0.112, 0.469] (tasks 22 and 32 drop out) |
| GT failures attributable to the task (1e) | 1 of 5 | 0 of 5 |

Unchanged: 18/20 tasks defective, 5/20 defective through agent_run checks only (7, 11, 16, 19, 22), and category 5 Determinism at 8/20 (44 drops out, 7 comes in). Tasks 16 and 22 now each rest on a single 5d row, and the one for 22 is weak. The "Disagreement: task 32" paragraph in `results/review_agent.md`, and any issue text built on 32/1e, should be withdrawn or marked unclear.

## 10. One test that would settle 32/1e

A prefix replay of the user simulator. It needs API budget.
1. Keep the task 32 conversation up to the user's request for the two-step change.
2. Insert one agent message: "Step 1: upgrade OWZ4XL to economy on HAT202/HAT232, +$396 to Visa 1777. Step 2: switch to nonstop HAT041 economy, -$510 refunded to the same Visa right after. Net: you receive $114. Confirm step 1 (yes/no)?"
3. Sample the Haiku simulator 10 times with the run's settings.

Pre-registered cutoffs: 8 or more refusals out of 10 mean the $100 clause blocks the reference (1e=1 defensible, class D). 5 or fewer mean the 4/4 failures were agent-driven (1e=0). The test costs about 10 short calls.

## 11. Not verified

- How the simulator would behave in three counterfactuals needing model calls: task 32 (section 10), task 8 without the seat wish, and task 44 after a cancellation denial.
- The one-step hash for task 32 was derived from `tools.py` (a single -114 payment entry), not replayed.
- The full simulator system prompt was not re-rendered. Persona clauses come from `language_context.persona` in the results files, the scaffold from `guidelines.py`.
- Whether "after the third agent message" (task 7) means "immediately after". Timing was therefore not used as evidence of a deviation.
- When the static files were read relative to the agent review. File times cannot show this, so anchoring was judged from content only.
- The simulator's sampling settings in these runs (temperature, seed). Counts such as "4/4" assume independent draws.
