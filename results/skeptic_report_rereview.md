# Skeptic check of the blind re-review disagreements on task 23 (2g; 4c vs 2h)

Inputs: checklist.md rows 2g, 2h, 4c; results/review_overrides.csv (last row), review_batch_3.csv, rereview.csv; `tau2-bench/src/tau2/evaluator/evaluator_communicate.py`; recorded runs `sample20_gt_haiku` and `sample20_pass3_haiku` (`results.json`). GT = ground-truth agent run, DB = database. Method: tau2's own code without LLM calls (`evaluate_simulation` with `EvaluationType.ALL` on in-memory copies; reference replay through the registry). Nothing under tau2-bench/ was written (checked by file timestamps). Scripts: session scratchpad, folder `skeptic_rereview/` (scan23.py, cf23.py, order23.py).

## 1. 23/2g = 1, medium (override row): holds, skeptic_ok = 1

- **(a) Text.** GT trial 0, message index 26 (assistant), the same as "[26]" in results/trajectories/23_gt_t0.md: "Your Mastercard would be charged **$1,286** in total, based on the $2,613 trip cost less $1,327 in certificates and gift cards."
- **(b) Scorer.** `evaluator_communicate.py:173-175` holds the substring branch; both runs record `{"scorer": "substring"}`. The test is `info_str.lower() in message.content.lower().replace(",", "")`, so "$1,327" becomes "$1327", which contains "327". Commas are stripped from the agent text only.
- **(c) Position.** `communicate_info` is ["327", "1000", "1286"], and "327" is the gift-card total (nl_assertions[0]).
  - 1,327 = certificates 1,000 + gift cards 327, a third quantity: the amount subtracted in the Mastercard calculation, not the answer.
  - The digits collide only because the certificate total is a round 1,000.
  - So this is a non-answer position.
- **Second hit the row omits.** Haiku trial 1, message 22: "All $1,327 in certificates and gift cards would be used, leaving $1,286 of the $2,613 total for the card." 2 of the 4 recorded trajectories produce the colliding sentence unprompted. "1000" and "1286" have no non-answer hits in any of the 4, and the 2b greeting has none.
- **Recorded verdicts did not depend on it.** In all 4 runs the scorer's first hit for "327" is an explicit "$327" answer (GT message 11), so the row's "no observed bypass" is correct.
- **Counterfactual rescoring.** On in-memory copies, every standalone "327" in agent text was replaced by a wrong value; nothing else changed.
  - GT t0 and Haiku t1: the "327" check stays met through the $1,327 sentence, and Haiku t1 keeps full reward 1.0 (DB 1.0).
  - Haiku t0 and t2: reward drops to 0.
  - The unedited copies reproduce the stored rewards (0, 1, 1, 1).
  - So a stated-wrong gift-card total can earn full reward.
- **(d) 1 is right under the rule as written** ("a match occurs in a non-answer position ... in the GT and Haiku trajectories").
  - The original 0 (review_batch_3.csv) had already seen "327" inside "1327".
  - It then applied a test the rule does not contain ("not clearly accidental in a normal wrong answer") and deferred the required search ("check 2b/GT text"). No runs existed at that time (skeptic_report.md, systemic issue 5).
  - That search is now positive, and the counterfactual answers the "normal wrong answer" doubt.
- **(e) Severity: medium, as the checklist lists for 2g.** Same as 3/2g (issues_draft.md I4). Nothing argues for a change:
  - Not high: the bypass needs the full four-write DB target, the combined-total sentence, and a missing or wrong gift-card total. No recorded run was affected.
  - Not low: the exposure is narrower than task 3's "4", which any "2024" date satisfies on a no-write task, but the evidence is stronger: observed text in real runs plus a rescoring result, against a constructed reply for task 3.
- **Amend the evidence string.** Cite GT t0 message 26, Haiku t1 message 22, "2 of 4 trajectories" and the rescoring result.
- **Effects.**
  - Task-level count unchanged: 23 is already defective via 2h, 4e and 5d.
  - Table 2b, row 2g: 1 → 2 rows (2/20). Category 2 unchanged.
  - Task 23 leaves the static-phase "list-order-only" tier (8, 20, 23): it now has a reward-affecting, task-specific defect.
  - I4 should name task 23 too.

## 2. 23/4c vs 23/2h: the blind labelling (2h = 1, 4c = 0) is correct

- **The two rule texts.**
  - 2h's title is "rejected because the DB hash depends on order or on free choices". Its how names this exact case: "Permute independent WRITE calls (e.g. several `book_reservation`)". It also names list order inside one call ("passenger order").
  - 4c is about "choices the scenario leaves open". Its how lists only content choices ("payment method, flight among equal options, cabin, insurance, bag count") and asks whether "the scenario or the policy pins each one". Its defect_if needs "≥2 compliant end states".
- **Order-only variants are not two end states in the 4c sense.**
  - Reservations, passengers, flights, payments and amounts are identical. Only the system-assigned ids (HATHAT/HATHAU/HATHAV, given out in call order) or the stored list order differ.
  - No scenario text can sensibly pin which id a passenger receives. The fix belongs in the hash, which is 2h's subject.
- **When one fact sets both checks.** Only for a genuine content choice; the checklist names "payment method" in both rows (32/4c, 44/4c).
- **Payment-list order does not keep 4c = 1.** The second item in the original 4c row, payment-list order inside one booking, is list order: the analogue of 2h's "passenger order", not a choice of payment method.
- **Every content choice in task 23 is pinned.** Flights are the unique cheapest (364 + 248 + 259 = 871). The certificate-per-passenger split, gift cards and Mastercard are stated in the scenario. No bags, no insurance.
- **Facts re-verified with tau2's replay.** The reference hash is b46d1bed. All of these differ, with 0 replay errors:
  - bookings in the order Raj, Mohamed, Liam: 69e28ff1;
  - Mohamed's payment list reversed: 33a4921e;
  - his two gift cards swapped: a34f1709;
  - Raj's card listed before his certificate: 46ba213b.
- **The blind note is wrong on one fact.** It calls payment-list order "not probed (unclear)", but the effect is real; it belongs in the 23/2h evidence.
- **Earlier support for this reading.** The first skeptic already marked 23/4c "order-only; double-counts 23/2h". issues_draft.md I3 files the whole order property under category 2.
- **Consistency condition.** 8/4c (passenger order, named in 2h's how) and 20/4c (payment-list order) are the same order-only kind. Relabelling 23 alone would make the audit inconsistent. Either move all three to 2h, or keep all three under 4c and mark 23/4c as a double count.
- **Effect of moving all three** (23/4c → 0; tasks 8 and 20 from 4c to 2h, with the existing variant hashes as evidence):
  - Headline 18/20 and static 13/20 unchanged.
  - Category 4: 6/20 → 4/20 (tasks 7, 23, 32, 44 remain).
  - Category 2: 10/20 → 12/20.
  - Table 2b: 2h 1 → 3, 4c 5 → 2.
- No file was changed for this part.
