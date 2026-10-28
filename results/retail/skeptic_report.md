# Adversarial review of the retail static phase (results skeptic)

Scope: every `defect=1` row of severity high or medium in `retail/audit_log.csv` (80 rows: 23 high, 57 medium), every row whose note starts with "uncertain:" (17 rows) and the borderline rows named in the reviewer `.md` files and in `retail/skeptic_brief.md`. The four low rows (`ALL` 5b, 6d, 6f, 6g) are outside the mandate and were not re-verified. Run-dependent rows (1e, 1f, 2j, 4f, 5c-5f) do not exist yet.

Method: primary sources first. Every amount a defect row depends on was recomputed from the card prices. Hash claims that the probes could not decide (replay stopped at an intended failing lookup: tasks 37, 38, 54, 55, 64) were replayed in the tau2 venv, environment construction and `make_tool_call` only, with the reference actions parsed from the task cards (`tasks.json` was not opened). Policy line numbers were read in `data/tau2/domains/retail/policy.md`, tool behaviour in `src/tau2/domains/retail/tools.py`, the scoring path in `src/tau2/evaluator/evaluator_env.py` and `evaluator_nl_assertions.py`. The 61 `nl_assertions` of all 114 cards were searched for process words (authenticate, confirm, verify, another user, once): none names such a requirement.

Outputs: `results/retail/skeptic_verdicts.csv` (103 rows: 80 verdicts on reviewed defect rows, 4 escalations, 19 "stays 0" decisions) and `results/retail/review_overrides.csv` (17 rows: 3 severity changes, 8 rows set to 0, 2 evidence corrections, 4 new rows).

Conventions in the verdict file: `skeptic_ok = 1` means the row holds as it stands after the override file (so the three 1b rows re-filed from high to low carry 1 with "re-filed" in the note); `skeptic_ok = 0` means the row is set to 0 by an override row (rejected, or re-filed under another check id that already carries the finding); escalations and "stays 0" rows have an empty `skeptic_ok` as the brief asks. Note for the builder: the four escalated rows become `defect=1` through the override file and will show an empty `skeptic_ok` in the merged log unless "should be defect=1" with an empty `skeptic_ok` is treated as confirmed.

## Counts

| | rows |
|---|---|
| reviewed (medium/high defect rows) | 80 |
| confirmed as logged | 69 |
| re-filed, still a defect at another severity (1b high -> low: tasks 2, 3, 4) | 3 |
| re-filed under another check that already carries the finding (20 4c, 21 4c -> 2h; 66 1d -> 4c; 111 2m, 112 2m -> 2e) | 5 |
| rejected as a duplicate of another row of the same task (25 2c, 50 2m, 105 1c) | 3 |
| escalated from 0 to defect (18 4d medium; 26 4a low; 25 4a low; 64 1b low) | 4 |
| evidence corrected, verdict unchanged (37 1g, ALL 1g) | 2 |
| "uncertain" or borderline rows that stay 0 | 19 |

## Verdict table

Severity shown as logged before this pass.

| task | check | sev | verdict | why |
|---|---|---|---|---|
| 2 | 1b | high | re-filed -> low | READ with the tools.py docstring example id 6086499569 (0 hits in db.json); evaluator continues; target unchanged (PLAN deviation 4) |
| 3 | 1b | high | re-filed -> low | same artifact |
| 4 | 1b | high | re-filed -> low | same artifact |
| 4 | 4d | medium | holds | 3799046073 is crew neck, 'same v-neck' false for one shirt; target unique (only purple/S is 9647292434); not blocking |
| 10 | 2a | high | holds | positive_control=1, no assertions |
| 10 | 2b | high | holds | probe reward 1.0 |
| 12 | 2a | high | holds | as 10 |
| 12 | 2b | high | holds | probe reward 1.0 |
| 16 | 4c | medium | holds | no refund method named; PayPal or gift card 1675628 both allowed (l.124); gift-card replay changes the hash; 8276.23 recomputed |
| 20 | 1g | medium | holds | replay: three items stored at 261.11 with Makeup Kit options; 71.96 <= 86.0 recomputed |
| 20 | 2h | medium | holds | 18/23 pair orders change the hash |
| 20 | 4c | medium | re-filed -> 0 | same consequence as 2h/1g (PLAN deviation 1); variants and gift card pinned |
| 21 | 1g | medium | holds | replay: 4107812777 stored at 268.77 with keyboard options; 44.08 recomputed |
| 21 | 2h | medium | holds | 1/1 other pair order changes the hash |
| 21 | 4c | medium | re-filed -> 0 | as 20 |
| 25 | 2a | high | holds | positive_control=1 |
| 25 | 2b | high | holds | probe reward 1.0 |
| 25 | 2c | high | rejected -> 0 | the scenario's fallback is a transfer; treated as 10, 12, 50 (2c = 0 where a transfer is the intended ending); the do-nothing pass is counted under 2a/2b |
| 30 | 2k | medium | holds | tracking id only in communicate_info, no assertions |
| 31 | 2k | medium | holds | same |
| 32 | 2k | medium | holds | same |
| 32 | 4c | medium | holds | no reason stated; 'ordered by mistake' changes the hash (replay) |
| 36 | 1g | medium | holds | replay: camera and lamp slots stored at 46.66 with T-shirt options; 36.13 recomputed |
| 36 | 2h | medium | holds | 4/5 pair orders change the hash |
| 37 | 1g | medium | holds, evidence corrected | probe row blank (intended e-mail failure); replay shows 2 of 3 items corrupted, as in 36 |
| 37 | 2h | medium | holds | 4/5 pair orders change the hash |
| 38 | 4c | medium | holds | 'cancel so that you can order again' pins no reason; replay with the e-mail failure caught: the other reason changes the hash; 1130.85 > 950 recomputed |
| 41 | 2e | medium | holds | write_order probe: items-then-address on #W4082615 reaches the gold hash |
| 41 | 2m | medium | holds | 'in the same order' (jigsaw first) makes the task about policy l.110; no assertion |
| 41 | 4c | medium | holds | no payment word; visa or PayPal; -7.98 recomputed; visa changes the hash; task 42 pins PayPal |
| 42 | 2e | medium | holds | write_order probe reaches the gold hash |
| 45 | 4c | medium | holds | bagless only if several options are offered; replay: the two bagged canister variants change the hash; 9.89 recomputed |
| 50 | 2a | high | holds | positive_control=1 |
| 50 | 2b | high | holds | probe reward 1.0 |
| 50 | 2m | medium | rejected -> 0 | duplicate of the positive control; tasks 10 and 12 (same situation) carry 0 |
| 52 | 4a | medium | holds | no 24MP variant with more zoom keeps SD card; reference changes the resolution the user asked to keep |
| 57 | 2a | high | holds | empty reference, no assertions |
| 57 | 2b | high | holds | probe reward 1.0 |
| 57 | 2c | high | holds | intended ending is a denial, not a transfer |
| 60 | 4c | medium | holds | no payment word (13.75 refund); conditional 'if several options' leaves the one-option branch open; 13.75 recomputed |
| 61 | 4c | medium | holds | no payment word (30.18); gift card changes the hash |
| 63 | 4c | medium | holds | no payment word (30.78); 1288.65 recomputed |
| 64 | 4c | medium | holds | two 4K waterproof variants <= 502.28 (black 466.75, silver 481.50); replay: silver changes the hash; colour unnamed, original silver, reference black |
| 65 | 2a | high | holds | positive_control=1 |
| 65 | 2b | high | holds | probe reward 1.0 |
| 65 | 2c | high | holds | intended ending is a denial |
| 66 | 1d | high | re-filed -> 0 | unstated cancel reason is 4c (PLAN deviation 4) |
| 66 | 4c | medium | holds | no reason stated; other reason changes the hash; 1464.00 recomputed |
| 67 | 1d | high | holds | no date field on orders; three candidate orders; list-position statistics reproduced (pending 131 vs 132, delivered 114 vs 114) |
| 67 | 2m | medium | holds | task built around the zip-code script with the user id handed over; nothing else scored |
| 68 | 1d | high | holds | as 67 |
| 68 | 2m | medium | holds | as 67 |
| 71 | 2e | medium | holds | write_order probe reaches the gold hash; 10.84 recomputed |
| 72 | 2e | medium | holds | same |
| 72 | 2m | medium | holds | 'first mention the modification then the address' |
| 78 | 2e | medium | holds | write_order probe reaches the gold hash |
| 96 | 2e | medium | holds | same (action ids 97_*) |
| 97 | 2e | medium | holds | same |
| 97 | 2m | medium | holds | 'mention the exchange first' |
| 98 | 4c | medium | holds | 'the other card' is defined by what the agent proposes; mastercard paid both orders; visa changes the hash |
| 100 | 1g | medium | holds | replay: luggage slot stored at 217.06 with skateboard options; 68.92 recomputed |
| 100 | 2h | medium | holds | 1/1 other pair order changes the hash |
| 101 | 2e | medium | holds | write_order probe reaches the gold hash |
| 102 | 2e | medium | holds | same |
| 103 | 2e | medium | holds | same |
| 104 | 2e | medium | holds | same |
| 104 | 4e | medium | holds | description.purpose contradicts the DB (cancelled order holds no bookshelf) and the reference (three returns in two orders); reward unaffected; see open questions |
| 105 | 1b | high | holds | 21.10 > 17.00, only payment method, gold hash = initial hash (replay); not a set-up |
| 105 | 1c | high | rejected -> 0 | the unchanged hash is the 1b raise itself; one event, one row |
| 105 | 4b | medium | holds | reference breaks l.134; a compliant denial reaches the target, so medium |
| 105 | 4e | medium | holds | assertion demands an impossible exchange; no trajectory satisfies hash and assertion |
| 109 | 2e | medium | holds | write_order probe reaches the gold hash; -114.73 recomputed |
| 110 | 4d | medium | holds | default address already equals the 'new home' (760 Elm Avenue); 111_1 is a no-op (replay); assertion rests on the false premise |
| 111 | 2e | medium | holds | write_order probe reaches the gold hash; -77.15 and -181.37 recomputed |
| 111 | 2m | medium | re-filed -> 0 | address listed first, no ordering instruction; mechanism carried by 2e (PLAN deviation 2) |
| 112 | 2e | medium | holds | same; -242.15 recomputed |
| 112 | 2m | medium | re-filed -> 0 | as 111 |
| ALL | 1g | medium | holds, evidence corrected | 9 corrupted items (20: 3, 21: 1, 36: 2, 37: 2, 100: 1), not 7 |
| ALL | 2e | medium | holds | 35 address probes over 24 tasks, 34 at the gold hash, 1 undecided (39), reproduced from the probe file |
| ALL | 2m | medium | holds | policy l.10, 14, 16, 84; tool checks verified; 0 of 61 assertions name a process rule |

## Escalations (new defect rows, in the override file)

| task | check | severity | why |
|---|---|---|---|
| 18 | 4d | medium | the fallback trigger presupposes that chair 8069050545 is unavailable; db.json has available=true; the compliant refusal comes from policy l.132 (different option), not from availability; the reference target (1071497737) is reached only through that fallback. Item availability is named in the retail reading of 4d. Not blocking by construction, so medium; the realised effect belongs to 4f/5d. |
| 26 | 4a | low | 26_7 transfer_to_human_agents carries the amex summary of task 25's scenario; task 26's user asks for neither; GENERIC, not replayed (`toolkit.py`: mutates_state defaults to WRITE only), reward unaffected; enters the GT prompt and the action-match diagnostic. |
| 25 | 4a | low | mirror of 26: the scenario asks for a transfer when the amex refund is refused and the reference has none. |
| 64 | 1b | low | 64_6 exchanges on a pending order (policy l.130) two steps after reading its status, raises, and is not a user-side set-up; nil effect on the target (replay with and without it gives the same hash); same mechanism and severity as the raising READs of 2, 3, 4. |

## "Uncertain" and borderline rows that stay 0

17 2e, 22 2e, 34 2e, 59 2e (policy l.84 read conservatively, PLAN deviation 3); 32 1d, 38 1d, 38 4a (carried by 4c); 35 2m, 39 2m (authentication incidental to a scored write); 35 4d (deliberate decoy e-mail); 40 4d (the amex is a candidate in a question, no reference value depends on it); 64 4b (counted once under 1b low); 74 1d (unknown_info is rendered into the user prompt, `data_model/tasks.py:41-42`); 86 4c, 91 4c, 100 4c (minimal-change reading); 98 4a (carried by 4c); 104 2m (no ordering instruction); 70 4a (truncated sentence, see below).

## Consistency rules applied

1. Reference action that raises (1b). User-side set-ups (wrong e-mail, zip or order id given by the scenario) are 0. Otherwise the severity follows the effect on the scored target (PLAN deviation 4): nil effect -> low (2, 3, 4: READ with a docstring id; 64: a forbidden exchange attempt before the real write); target not the intended state -> high (105). A WRITE that raises is logged once, under 1b; 1c is kept for a WRITE that returns without error and changes nothing (none left: 110's 111_1 is a no-op by the DB state and is logged under 4d). The count under the literal rule is reported below.
2. Unstated cancellation reason. 4c medium when the motive pins neither allowed value (32: 'also cancel the boot and kettle'; 38: 'cancel so that you can order again'; 66: 'if there are any issues'); 0 when the motive pins one (30, 31: the charger goes with the returned or lost tablet; 54, 55: financial issue; 59: wait time; 69: better deal; 16, 74, 76, 78, 81, 88, 90, 98, 113: stated). Never 1d.
3. Unstated payment method for a refund or difference. Policy l.114/122/134 makes the user name one; where the scenario names none and the user has two compliant methods, two end states fit -> 4c medium. Swept mechanically over the 19 tasks where probe_2d found a tool-accepted alternative: exactly 16, 41, 60, 61, 63 name no method, and exactly these five carry 4c; 98 ('the other card', relative to the agent's proposal) also 4c; 74 names the card in unknown_info (0, open question).
4. Variant left open by the scenario. Where the scenario names only the options that change and the reference keeps all other options (minimal change), the end state is pinned -> 0 (86, 91, 100, and the variant part of 61). Where a conditional tie-breaker depends on how many options the agent lists (45, 60), or the reference itself departs from the minimal-change reading without the scenario pinning the choice (64), -> 4c medium.
5. Forbidden write order (items before address on the same order). 2e medium per task by probe (14 tasks). 2m per task only where the scenario instructs the user to request the item change first (41 'in the same order', 72 'first mention the modification then the address', 97 'mention the exchange first'); removed from 111 and 112 (address listed first, 'say things together/piecewise'); 104 names the item change first without an instruction and stays 0 (borderline).
6. Authentication as a 2m topic. Per task only where the scenario is built around the authentication procedure itself (67, 68: task_instructions are a zip-code script, the user id is handed over, nothing else is scored); an incidental wrong e-mail or zip next to a scored DB change is not 'about' the rule (35, 39).
7. Transfer tasks. Where a transfer is the intended ending (reference = transfer in 10, 12, 50; scenario fallback in 25), the pass of a do-nothing answer is the 2a/2b positive control and is counted once; 2c and 2m are 0 there. 57 and 65 (intended ending = denial) keep 2c.
8. Pair-order dependence of multi-item modify calls (20, 21, 36, 37, 100) is logged as 1g (corrupted target) and 2h (order sensitivity) per the PLAN decision; the reviewers' 4c rows for 20 and 21 are 0.
9. Description-only contradictions (104 4e) are kept at the checklist severity (medium) because the checklist names `description` in 4e; the reward is unaffected and the task is defective through 2e anyway (open question on severity-by-effect).

## Numbers before and after

| | defect rows (high / medium / low) | defective tasks, PLAN reading | defective tasks, literal 1b rule |
|---|---|---|---|
| before this pass | 84 (23 / 57 / 4) | 45/114 | 45/114 |
| after this pass | 80 (17 / 53 / 10) | 44/114 | 46/114 |

Tasks leaving the defective set: 2, 3 (1b re-filed to low, no other medium/high row). Task entering: 18 (4d escalated). Under the literal 1b rule ("any reference action raises -> high") tasks 2 and 3 re-enter; 64 is defective through 4c under both readings. The 44 defective tasks under the PLAN reading: 4, 10, 12, 16, 18, 20, 21, 25, 30, 31, 32, 36, 37, 38, 41, 42, 45, 50, 52, 57, 60, 61, 63, 64, 65, 66, 67, 68, 71, 72, 78, 96, 97, 98, 100, 101, 102, 103, 104, 105, 109, 110, 111, 112.

Medium/high rows by check after the pass: 1b 1, 1d 2, 1g 6, 2a 6, 2b 6, 2c 2, 2e 15, 2h 5, 2k 3, 2m 6, 4a 1, 4b 1, 4c 11, 4d 3, 4e 2 (70 rows); low rows: 1b 4 (2, 3, 4, 64), 4a 2 (25, 26), ALL 5b, 6d, 6f, 6g.

## Blind re-review (results/retail/rereview_blind.csv, not binding)

Twelve tasks (3, 7, 12, 15, 21, 24, 31, 43, 77, 83, 84, 98). Its defect rows coincide with the originals on 3 1b (kept high there; the low severity here follows PLAN deviation 4, which the blind pass did not apply), 21 1g, 21 2h, 31 2k and 98 4c, and it reports no defect where the originals report none. It adds two "uncertain" 1d rows (7 and 43: the user's name appears only inside the user id token, so the simulator must derive it); these stay 0 here: the simulated user is the person named in the id and can state its own name, and name + zip resolves uniquely in both tasks.

## Could not verify, and open questions

- The realised effect of the conditional branches (18 4d, 45 4c, 60 4c) and of the minimal-change reading (86, 91, 100) depends on the user simulator; the 4f/5d trajectory readings can confirm or overturn them.
- 70: `reason_for_call` is cut mid-sentence ('You do not want the  You prefer original payment'); the lost clause cannot be audited; the visible constraints pin the reference (219.88 - 197.33 = 22.55 matches the assertion). Kept at 0, listed for the issue text.
- 74: the payment instruction sits in `unknown_info`, which the user prompt renders verbatim; functionally stated, formally a misuse of the field. Kept at 0; whether scenario-field misuse is a defect class is a coordinator question.
- 104 4e: a description-only contradiction with no reward effect is medium under the checklist as written; under the severity-by-effect principle of PLAN deviation 4 it would be low. No effect on the task count.
- 104 2m: the only task where the item change is named before the address change without an ordering instruction; kept 0 by the explicit-instruction criterion; a stricter reading adds one 2m row, no change to the task count.
- 25 2c: set to 0 on the ground that the scenario's fallback is a transfer; under the literal check text (the reference as recorded has no transfer) it would stand as high; no change to the task count (2a/2b keep 25 defective).
- The four escalated rows will carry an empty `skeptic_ok` in the merged log unless the builder treats "should be defect=1" with an empty `skeptic_ok` as confirmed.
- The low `ALL` rows (5b, 6d, 6f, 6g) were not re-verified (outside the mandate).
- Not touched: run-dependent rows (1e, 1f, 2j, 4f, 5c-5f); the upstream `issues` field (compared by script afterwards).
