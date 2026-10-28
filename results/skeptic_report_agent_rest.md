# Skeptic check of the rest-task agent-run review (checks 1e, 4f, 5c, 5d)

Date: 2026-10-28. Object: `results/review_agent_rest30.csv` (32 rows, 11 with defect=1) and `results/review_agent_rest30.md`.

Read directly: the 19 failed trajectories listed in `results/agent_triage_rest30.md` and the comparison trials 14 t0, 17 t0/t1, 24 t1/t2, 33 t0, 39 t2, 42 t1/t2; task cards 14, 15, 17, 24, 29, 30, 33, 39, 42; `tau2-bench/data/tau2/domains/airline/policy.md`; `tau2-bench/src/tau2/user/guidelines.py`; `tau2-bench/data/tau2/multilingual/en/pack.yaml`; `tools.py` (`book_reservation`, `cancel_reservation`); `config.py` and `runner/build.py` (stop tools); `db.json` (flight statuses for task 39, origin and destination of round trips); the persona of every simulation (`language_context.persona` in `results/runs/rest30_pass3_haiku.results.json` and `rest30_gt_haiku.results.json`); `results/probe_2h.csv`; and, after the verdicts were formed, the static rows of these tasks in `review_batch_*.csv`, `rereview_blind_rest.csv` and `rereview_rest.csv`. Precedent: `review_agent.md`, `skeptic_report_agent.md`, `skeptic_verdicts_agent.csv`, `review_agent_overrides.csv`. No model calls, no replays, nothing under `tau2-bench/` changed. Row verdicts: `results/skeptic_verdicts_agent_rest.csv`. Corrected row: `results/review_agent_overrides_rest30.csv` (29/1e only). Corrections that leave a verdict unchanged are documented here, not as override rows.

Terms: GT = ground-truth agent `llm_agent_gt` (sees the reference actions); t0/t1/t2 = Haiku trials 0-2; DB = database. Classes: A agent slip, B user-simulator deviation, C defensible alternative reading, D reference or scoring problem.

## 1. Verdicts

| task | check | review | skeptic | decisive evidence |
|---|---|---|---|---|
| 14 | 5c | 1 (borderline) | confirmed, borderline | t2 turns 25/26/32: "beyond the included ones", then "6 total" bags confirmed against "You do not need baggage"; the agent's leading question and unrequested bags share the cause |
| 14 | 5d | 1 | confirmed | GT turn 28 invents that Raj Sanchez and Liam Wilson should not travel; the reference books all three |
| 15 | 5d | 1 (borderline) | confirmed, weak | t2 turn 13 "My original booking was in Economy" (business in the DB); outcome-irrelevant |
| 17 | 5d | 1 (borderline) | confirmed, weak | t2 turns 12/14 contradict the premise and stop early; induced by the agent's turn 11; same standard as block-1 22/5d |
| 24 | 5d | 1 | confirmed | GT turn 10 and t1 turn 7 escalate instead of "accept it and move on"; not decisive alone (t1 still succeeded) |
| 29 | 1e | 1 (high) | **rejected**, set to 0 (unclear) | a compliant route exists; every refusal follows an agent framing or hedging error; t1 turn 18 "Before I say yes, can you confirm that the full $686 comes back" |
| 29 | 5d | 1 (borderline) | confirmed, weak | t2 turn 8 invents a "nonstop" original booking |
| 33 | 5c | 1 | confirmed, other grounds | t2 turns 17/19 hold back the triggered upgrade-and-bags request; the waiver itself was prompted by the agents' "charge or refund" wording |
| 33 | 5d | 1 | confirmed | t2 turns 17/19 and 23-41; t1 turn 15 card choice (weak) |
| 39 | 1e | 1 (high) | confirmed | MSJ4OA: economy, insured, flights "available", no covered reason; the GT refusal is policy-correct; no compliant path to the target hash |
| 42 | 5d | 1 (borderline) | confirmed, outcome-decisive in GT | GT turn 13 "Anything that doesn't fit that is the mistake" against "on those days/dates" in t0, t1, t2 |

Counts: 11 defect=1 rows checked; 10 confirmed, 1 rejected (29/1e); 0 defect=0 rows escalated.

## 2. Cross-cutting: persona and transfers

**Persona.** Every simulation records `language_context.persona`. Tasks 24, 33, 39 and 42 ran with `priya_patil` (all three trials and the GT run); tasks 14, 15, 17, 29 and 30 ran with `mamadou_diallo`. The review never mentions persona, although the block-1 check found that it scripts escalation. The `priya_patil` clauses recur verbatim in these runs:
- the clauses: "asking for a supervisor or a timeline early is characteristic", "No, that doesn't work for me", "Nope, not doing that", "Can I just talk to someone who can actually fix this";
- where they appear: 24 GT turn 10 and t1 turn 7; 33 t1 turn 17; 39 GT turn 21, t0 turn 20, t1 turn 15 and t2 turn 22.

The block-1 rule counts such an escalation only where it replaces an instruction that the scenario gives for that situation:
- **Counts:**
  - 24 GT and t1: the scenario says "If agent says cancellation is not possible, accept it and move on".
  - 33 t2: once the flights are changed, the scenario's next instruction is the upgrade and the two bags.
- **Does not count:**
  - 33 t1: the scenario says "Be persistent", and no change had been made yet.
  - 39: the scenario gives no instruction for this situation, and the GT agent offered the transfer itself (turn 22).
  - 42 GT: the agent offered the transfer (turn 16).

**Transfers.** The agent's `transfer_to_human_agents` call does not end an airline run:
- `config.py` line 34 limits `ELICITATION_DOMAINS` to `intake`, and only those domains get stop tools (`runner/build.py` lines 155-156). The airline tool just returns "Transfer successful".
- The run ends only when the simulator sends a token.

In 24 t1 the simulator kept talking after "YOU ARE BEING TRANSFERRED" (turn 11). The agent kept serving, booked the reference (turn 38), and the trial scored 1. Observation 4 of the review ("Those episodes cannot reach the target") is therefore wrong as stated. After a transfer, the outcome depends on whether the agent keeps serving: it did in 24 t1, and it did not in 24 GT or 33 t2.

The 24 t1 success is accidental in the same sense as block-1 19 t2. It rests on two simulator deviations: the escalation, and the missing ###TRANSFER###.

## 3. Task 29, check 1e (high): rejected

Recomputation of the route the reference needs (line numbers of `policy.md`):
1. **No modification.** VA5SGQ cannot be changed to JFK, because a change cannot alter the destination (line 111).
2. **Cancellation is allowed.** VA5SGQ is economy and was created 2024-05-08T18:28:13, more than 24 h before the clock. It has insurance "yes", and in all four runs the user states the health reason in the first message; health is covered (lines 101, 147).
   - `cancel_reservation` reverses every payment entry. The user gets the full 686 back on credit_card_8003957 (fares 163 + 184 + 174 + 135 = 656, plus 30 insurance).
   - Neither the policy nor the tools define a change fee or a cancellation fee.
3. **New booking.** HAT169 on 2024-05-17 (04:00-06:00, economy 171) and HAT033 on 2024-05-19 (00:00-02:00, economy 111), 282 in total.
   - A regular member gets 1 free economy bag (total 1, nonfree 0).
   - The DOB 1967-03-12 is in `get_user_details` (GT turn 6).
4. **Order does not matter.** Booking before cancelling gives the same hash (`probe_2h.csv`, task 29: 1 permutation, 0 differences), so an agent can lock the fares first.

The user ends 404 ahead with no fee. The scenario never asks for the cancellation, but nothing in it forbids accepting one.

What the four runs show:
- **GT, class A (D contributing).**
  - Turn 7 offers the cancellation as the alternative to the change, with no rebooking: "If you'd rather keep the trip as it is, I can leave it unchanged". The user refuses to "cancel the whole thing" (turn 8).
  - Turn 9 lists "Keep", "Cancel" and "Book a new reservation ... It would not be a change to VA5SGQ" as exclusive options. The user picks the new booking (turn 10).
  - The GT agent had both actions in its reference and never presented them as one route.
  - Turns 15-25: the agent makes the user confirm a DOB it already had. The user does not know it, holds off and ends the chat.
- **t1, class A.**
  - The user asks about "cancelling just the flights and rebooking them to JFK" (turn 8).
  - At turn 18 it says: "Before I say yes, can you confirm that the full $686 comes back with no cancellation fee at all?".
  - The agent answers that it "can't guarantee the refund will be exactly $686" and has no information on cancellation fees (turns 17, 19). In fact line 101 and the tool return the full amount.
  - The user declines and cites exactly this (turn 20).
- **t0, class D (A contributing), unresolved.**
  - This is the cleanest presentation: cancel then book, with a "full refund" (turns 7, 12, 14), plus the fares and the free bag (turn 16).
  - But turns 7, 12 and 16 also say that change fees cannot be waived, which implies that fees exist. The agent never offers to book first.
  - The user's stated reasons are "not sure the new fares would be the same" (turn 15) and being "disappointed the change fees can't be waived" (turn 17).
- **t2, class A.**
  - Turn 7 offers the cancellation as an end in itself ("If you need to cancel because of your health problem"), or a change within LGA. The user declines (turn 8).
  - At turn 22 the agent changes the destination against line 111.

"The simulator refused in 4 of 4 runs" is literally true, but it does not show what the review claims:
- No run presented the reference route plainly: cancel with the full refund, book HAT169 and HAT033, no fee, fares that can be locked first.
- In t1 the simulator made its yes depend on a fact that the agent wrongly withheld.

Under the 1e rule (the cause must trace to the task, not to an agent slip) and the block-1 handling of 32/1e before its probe, the row becomes 0 (unclear).

The DOB argument does not support 1e either. The value is in the profile, the reference uses that value, and the stall came from the agent's demand for confirmation. Tasks 17 and 24 contain a "look it up in my profile" line and task 29 does not, but that is a minor scenario gap.

**What remains.** The scenario lacks the cancellation fallback that other tasks state:
- task 14: "you want the agent to cancel the current one and book a new one";
- task 24: "you want the agent to cancel".

nl assertion 1 also expects "it can be cancelled instead". This is a specification finding for the static rows of task 29 (4a, 4c). Their adversarial review is in progress and was not read. The test in section 11 decides the 1e row.

## 4. Task 39, check 1e (high): confirmed

- **The reservation.** MSJ4OA is economy, one way, created 2024-05-05T14:36:15 (10 days before 2024-05-15 15:00), with insurance "yes" and 3 passengers; it was paid with 984 by gift_card_1647044. In `db.json`, HAT099 and HAT274 on 2024-05-22 are "available", so the airline did not cancel them.
- **Policy lines 143-147.** No condition holds:
  - it was not booked within 24 h;
  - the airline did not cancel it;
  - it is not business;
  - it is insured, but insurance covers only health or weather (line 101), and the scenario's only motive is to "give up your seat for someone else who needs it".
- **The GT run.**
  - The GT agent cancelled 8C8K4E and LU15PA (business).
  - It refused UDMOP1 and XAZ3C0 (basic economy, no insurance) and MSJ4OA (turns 12-22).
  - It offered a transfer and made it at the user's request (turns 22-24).
  - Its end state differs from the target only in MSJ4OA.
- **No compliant conversation reaches the target hash.**
  - A health or weather reason would have to be invented by the simulator.
  - Upgrading MSJ4OA to business and then cancelling it (the block-1 task 7 route) writes a cabin change and extra payment entries that the reference lacks, so the hash still differs.
- **The other runs.** t0 and t1 refuse in the same way. The only success, t2 turn 19, cancels MSJ4OA for "change of plan", which breaks the policy.
- **Other rows for task 39.** 4f, 5c and 5d stay at 0.
  - "Change of plan" is a fair mapping of the stated motive. The scenario gives no reason, and any reason that insurance does not cover leads to the same outcome.
  - The requests for a human follow agent offers or the persona script.

## 5. GT failures with 1e = 0 (tasks 14, 24, 42)

- **14: the simulator.**
  - At turn 27 the GT agent proposes the exact reference.
  - At turn 28 the user removes Raj Sanchez and Liam Wilson from the trip, which the scenario never mentions. A one-passenger booking can never match the three-passenger target.
  - Two agent errors only add to this: the Visa payment at turn 33, and a cancel-and-rebook that could not recover, because the certificate and gift cards were not restored (turns 42-45).
  - Haiku t0 reached the target, so 1e = 0 holds.
- **24: simulator and agent.**
  - The simulator escalates at turn 10 instead of moving on.
  - The GT agent transfers at once (turn 11) on a conditional request ("Can you tell me if there's any other option at all? If not, ..."). It then declines the booking the user describes after the transfer (turns 18-21).
  - In t1 the same simulator behaviour ended in success, because the agent kept serving.
  - Class B (A contributing) is right, and 1e = 0 holds (t1, t2).
- **42: led by the simulator.** This reverses the review's A (B contributing).
  - The GT user's criterion "Anything that doesn't fit that is the mistake" (turn 13) appears only in this run. All three Haiku users say "Everything else booked on those days/dates" (t0 turn 14, t1 turn 13, t2 turn 15).
  - The agent then proposed MFRB94 (turn 14), and the user confirmed it explicitly (turn 17).
  - The GT agent shares the blame, since MFRB94 is not in its reference.
  - 1e = 0 holds (t1, t2).

## 6. Other 5c and 5d rows

- **14/5c: confirmed, borderline.**
  - In t2 the only booking argument that differs from the reference is `total_baggages` 6.
  - The agent asked "Do you need any bags beyond that?" (turn 25). The user answered "I don't need any checked bags beyond the included ones" (turn 26), then said "Yes, that all looks good" to a summary listing "6 total" bags (turn 32). Both replies contradict "You do not need baggage".
  - In t0 the user said "I don't need checked bags or insurance" before the agent asked.
  - The cause is shared. The agent added bags the user never asked for, against "Do not add checked bags that the user does not need".
  - The row stays at 1 because the simulator's own reply supplied the premise, and its confirmation contradicts a fact in the scenario. In 42 t0 (5c = 0), by contrast, accepting the agent's offer was consistent with the scenario.
- **14/5d: confirmed.** GT turn 28 is strong evidence (section 5). t2 turns 26/32 are weak evidence.
- **15/5d, 17/5d and 29/5d: confirmed, weak.** These are inventions that did not decide the outcome, or that the agent induced. The standard is the same as for block-1 7/5d and 32/5d.
  - 15 t2 turn 13: claims the original cabin was economy, and asks for the refund "not to the gift card".
  - 17 t2 turns 12/14: same pattern as block-1 22/5d.
  - 29 t2 turn 8: claims the original booking was "nonstop".
- **24/5d: confirmed** (section 2). The review calls it "outcome-decisive in the GT run". It should read "decisive together with the GT agent's choice to stop acting after its transfer".
- **33/5c and 33/5d: confirmed, but on different grounds than the review gives.**
  - *The waiver was not raised unprompted.* The review says the user raised the waiver "although the agent never asked for a fee"; that is overstated.
    - The t1 agent asked which card to use for "the fare difference or refund" (turns 12, 14).
    - The t2 agent asked for a payment method for "any charge or refund" (turn 10), "before anything is charged or refunded" (turn 12).
    - Neither agent said that the change refunds 186 = 503 - 317. The t0 agent did say so before confirmation (turn 12), and in t0 the waiver never came up.
    - Raising the waiver therefore follows a loose but fair reading of "If the agent asks you to pay a fee".
  - *What decided t2 came later.*
    - At turn 16 the agent says no change fee was charged, and the user acknowledges it (turn 17).
    - The user then asks for a supervisor (turn 19) instead of making the upgrade-and-two-bags request. The scenario triggers that request once the flights are changed.
    - That request would have reached the target: business costs 408 > 200, so the cabin stays economy, and 2 bags are free for a gold member.
    - After the transfer the user sends "<br>", keeps talking through turn 41, and ends with ###OUT-OF-SCOPE###.
  - *t1 is mainly an agent failure, class A (B contributing).*
    - The agent never computes the refund and says "I can't say what the fee would be" (turn 16).
    - It transfers at once, with nothing changed, on a conditional request: "If you can't waive it" (turn 18).
    - The simulator's share is choosing gift_card_1646646 "with the higher balance" (turn 15). That choice alone would fail the hash.
    - It is weak as a 5d item, because the blind static 4c places the original-payment sentence with the upgrade request.
- **42/5d: confirmed, and outcome-decisive in the GT run** (section 5). The t0 turn 16 item should be dropped. Accepting the agent's offer to drop the MIA-DEN leg follows "let the agent figure out", and the policy breach is the agent's.

**Notable defect=0 rows, left at 0:**
- **30/5d.** The user named HAT266 early (t1 turn 8), which breaks "mention only the flight number if the agent shows it to you first". But the scenario itself calls HAT266 the user's "one-stop flight", nothing is invented, and the outcome is not affected. Borderline.
- **24/5c.** The only failure (t0) is an agent slip. The accidental t1 success is noted in section 2.
- **17/5c and 42/5c.** Both flips trace to statements or offers made by the agent.
- **39/5d.** See section 4.

## 7. Check 4f: no class C

- **24 t0** passes `destination: "JFK"` for the JFK-SEA-JFK round trip (turn 32).
  - The review supports a "weak D component" with "34 of 955 round trips have origin == destination".
  - Recomputed from `db.json`: all 34 are four-leg itineraries that return to the origin before the last leg.
  - All 254 two-leg out-and-back round trips use the far end as destination; none uses the origin.
  - So the DB convention is unambiguous for this trip shape, and the agent itself described the trip as "JFK to Seattle and back" (turn 28). This is class A, with no D component.
- **14 t2** (free bag allowance) is not C. The ambiguity came from the simulator's reply, not from the task text ("You do not need baggage"), so it is B or A.
- **42 t0 and 29 t2** (`update_reservation_flights` calls that change the route) are not C. Line 111 forbids changing the origin or destination. In 42, the t1 and t2 agents refused exactly this change; in 29, the t2 agent had itself said twice that it could not be done.
- **33 t1** first read "move back" as 2024-05-21, but the user corrected this before any write.
- **17 t2** is a false statement about the policy.
- 4f = 0 holds for all nine tasks.

## 8. Internal consistency

- **C implies 4f = 1:** holds, since there is no class C.
- **A flip caused by the simulator implies 5c = 1 and 5d = 1:** holds for 14 and 33. Every other flipped task (15, 17, 24, 30, 39, 42) has a flip caused by the agent and 5c = 0.
- **29/4f** says the D cause is recorded under 1e. With 29/1e now 0 (unclear), that pointer is stale; the override note says so explicitly.
- **Classes over the 19 trajectories:** after this check A 10, B 5, D 4, C 0; in the review A 8, B 5, D 6, C 0. The changes:
  - 29 GT: D becomes A (D contributing);
  - 29 t1: D becomes A;
  - 33 t1: B (A contributing) becomes A (B contributing);
  - 42 GT: A (B contributing) becomes B (A contributing).
- **14/5c (shared cause, kept at 1) and 42/5c (agent offer accepted, kept at 0)** are told apart in section 6.

## 9. Anchoring

- **No wholesale copying.** The review disagrees with static 4a = 0 on task 29. It also adds a finding the static rows lack: the round-trip destination field in task 24.
- **Task 39.** 39/1e matches static 4b = 1 (high), but the run evidence and the `db.json` check stand on their own.
- **Anchoring on the review's own hypothesis.** The review labels 29 t0 and t1 as D ("the simulator, without a cancellation instruction, declined"), although at t1 turn 20 the user cites the agent's hedge on the refund as the reason. Block 1 found the same pattern for task 32: class D adopted without checking how the agents had presented the path.
- **Task 33.** In 33/5d the review cites the blind static 4c ("the refund destination is pinned only by the upgrade sentence") as support for an invented payment criterion. That finding describes a gap in the scenario. Under the block-1 rule, a choice inside a gap is not counted, so the finding weakens this 5d item rather than supporting it.

## 10. Effect on the numbers

`airline_full/summary_numbers.md` was built before the rest review was merged, so its rest column is still provisional:
- it counts all five GT failures as mechanical 1e rows (5/5);
- it shows 0 rows for 5c and 5d.

The table below gives the rest counts after the review, and after this check with the override file applied:

| quantity (rest, 30 tasks) | review | after this check |
|---|---|---|
| 1e defect rows | 2 (29, 39) | 1 (39) |
| GT failures traced to the task | 2 of 5 | 1 of 5 |
| 5c defect rows | 2 (14, 33) | 2 (14, 33) |
| 5d defect rows | 7 | 7 (42 no longer borderline) |
| 4f defect rows | 0 | 0 |
| tasks with an agent-run defect | 8 (all reviewed except 30) | 8 (unchanged: 29 keeps 5d) |
| tasks with an agent-run defect other than 5d | 4 (14, 29, 33, 39) | 3 (14, 33, 39) |

Other effects:
- **Category 1 (Solvability), rest:** 1/30 from 1e (task 39), down from 2/30 under the review. This assumes the rest has no other category-1 row.
- **Defective tasks:** the count does not change. Task 39 is already defective through static 4b. Task 29 keeps its static 2h, 2k and 4c rows and its 5d row.
- **Whole domain:** GT failures traced to the task fall to 2 of 10 (tasks 32 and 39).

## 11. One test that would settle 29/1e

A prefix probe of the user simulator, built like `results/probe_32/`:
1. **Prefix.** Keep the 29 GT conversation up to and including turn 6: the user's request, the health and insurance statement, and the reads.
2. **One inserted agent message:** "I can't change VA5SGQ to JFK, because a change cannot alter the destination. Because you have travel insurance and a health reason, I can cancel VA5SGQ for a full refund of $686 to your Visa ending 6521, and book new nonstop flights HAT169 on May 17 (arrives 6:00 AM) and HAT033 on May 19, economy, $282, with your one checked bag free. There is no change fee. I can book the new flights first, so the fares are locked. Shall I go ahead?"
3. **Sampling.** Sample the simulator 10 times, with the run's persona (`mamadou_diallo`) and settings.

Pre-registered cutoffs, as for task 32:
- **8 or more refusals out of 10:** the scenario blocks the reference, so 1e = 1 (high).
- **5 or fewer refusals:** the recorded refusals were driven by the agents, so 1e stays 0.

Cost: about 10 short calls.

## 12. Not verified

- **Counterfactuals that need model calls:**
  - task 29 (section 11);
  - 14 t2 without the "beyond that" question;
  - 33 with the 186 refund stated up front.
- **The full rendered simulator prompt.** The persona clauses come from `pack.yaml` and `language_context.persona`, and the scaffold from `guidelines.py`.
- **Sampling settings.** The runs used provider-default sampling, and no seed reaches the API (checklist 5b). Counts such as "4 of 4" therefore assume independent draws.
- **The static adversarial review of the rest rows.** It is in progress and was not read (`skeptic_*rest_*`, `review_overrides_rest_*`). The design finding on task 29 is therefore not reconciled with those rows.
- **Hash effects of alternative routes.** The routes are 39 upgrade-then-cancel and 29 book-first. Their effects were derived from `tools.py` and `probe_2h.csv`, not replayed in this check.
