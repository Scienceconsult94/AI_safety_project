# Block 2 — adversarial design review (before live runs)

Reviewed 2026-10-27, 14:50–15:25 PT. State reviewed: commit `b0fc614`, plus the changes that appeared during the review and were committed as `55a35c0` at 15:14 (`scripts/v2/scorer_v2.py` with `JUDGE_VIEW`; `scripts/v2/rescore.py` with `--set fresh`; the "Deviations" entry in `block2/PLAN.md`; `scripts/v2/make_summary_v2.py`), and `scripts/v2/run_v2.py`. NL and judge numbers quoted below come from the stock-view judge pass of 15:07, now kept as `results/v2/rescore_stockview.csv`, `judge_votes_stockview.csv` and `judge_cache_stockview.json`. That is the view now being replaced, and the numbers are flagged as such wherever they appear. No judge pass with the new view existed at 15:25 (the current `rescore.csv` is a `--no-judge` run).

Method: read-only. Every check ran inside the tau2 virtual environment with all model entry points patched to raise (`scorer_v2.generate`, `tau2.utils.llm_utils.generate`, the communicate and NL evaluator modules, `litellm.completion`). No model call was made and no project file was edited except this report. The check scripts are in the temporary folder outside the repository (paths in the appendix), and condensed snippets are given inline.

Abbreviations: DB = database end state; GT = ground-truth agent (`llm_agent_gt`, which sees the reference actions); NL = natural-language assertions (`nl_assertions`); FP / FN = false positive / false negative; v1 = stock tau2 scorer; V2 = tasks v2 plus all three switches.

## 1. Verdict table

| # | item | verdict | severity | evidence |
|---|---|---|---|---|
| A1a | hash_canon: two different end states collide via content-derived reservation ids / the "+" suffix / the user→reservation map | holds | — | Identical bookings are possible (`created_at` is the constant `2024-05-15T15:00:00`, `tools.py:159`). Two identical bookings give `NEW_RES:ce40…` and `NEW_RES:ce40…+`, the user's list holds both, and one booking ≠ two (verified, A1c in the appendix) |
| A1b | payment_history compared as a multiset | holds | — | Order affects state only through tool errors or refund computation, and both change content. Task 7 order "102" (cancel before upgrade) leaves `+1072` unrefunded, so the canonical hashes differ (verified) |
| A1c | rounding floats to cents merges states that differ by a real cent | holds in practice | low | `Payment.amount: int` (`data_model.py:45`). All 983 floats in `db.json` are gift-card/certificate balances with no sub-cent part, and all tool deltas are integers. Only sub-cent values can merge, which is theoretical here (`round(0.115,2) == round(0.125,2) == 0.12`) |
| A1d | "insensitive to which generated id … certificate_3221322 … received" (`scorer_v2.py` docstring) | broken (narrow) | low | Generated payment-method ids are re-keyed in `users[*].payment_methods` (`scorer_v2.py:139-146`) but **not** inside `payment_history`. Two semantically identical episodes (send $200 + $300 certificates in either order, book with the $200 one) give canonical-equal = **False**. Without the booking they are equal (verified) |
| A2 | hash_canon can turn a v1 pass into a fail | holds | — | The canonical form is a function of the dump, so equal raw dumps give equal canonical hashes. On recorded data, 55/55 v1 passes still pass under S_hash |
| A3 | `Reservation.flights` order kept | holds (conservative choice) | low | The tool keeps agent order (`tools.py:756`). The task-23 gold booking with flights listed `[HAT204, HAT100, HAT023]` fails under v1 **and** v2 (verified). It is semantically the same trip, so a chronological sort is the safer canonical form |
| A4 | `probe_2h_v2` residue (task 7: 3 orders; task 32: 1 order) | holds: semantic | — | Task 7 "102/120/210" are exactly the orders with cancel-XEHM4B before the upgrade, which leaves an unrefunded upgrade charge. Task 32 "10" ends on HAT202/HAT232 in economy with a −$114 history. Both are real differences (diffs in §3.A) |
| B1 | comm_boundary closes the digit-adjacent collisions of 2g | holds | — | `$1,327`→`327` rejected; `$1,387.50`, `1,387,000` rejected for `1387`; `2024-05-04` rejected for `4`; `$1,000.00`, `$708.00`, `1000.`, `(1000)`, `USD 1000` accepted (battery, §3.B) |
| B2 | comm_boundary surviving false positives | needs-change | medium for 1-digit targets (task 3), low otherwise | Letters and punctuation next to the number are allowed (`scorer_v2.py:210`). For `4`: `4:15 PM`, `May 4`, `5/4/2024`, `the 4th`, `MZDDS4`, `4WQ150`, `4%`, `Terminal 4` all match. `708` matches inside `HAT708` |
| B3 | comm_boundary false negatives | holds mostly | low | Spelled-out small numbers (`four suitcases` for task 3) are rejected by v1 and v2 (2i stays open). `1 387` and `1.387` are rejected (rare in English) |
| B4 | real communicate_info strings (3, 7, 11, 14, 18, 23; v2: 7→708, 44→1387) | holds | low | No recorded verdict changes (0/76). Task 3: every standalone `4` hit in the 4 recorded transcripts is the answer itself ("4 free checked bags"). Residual: task 7 fare-only reading = 342+306 = **648**, because 402 includes $60 insurance |
| C1 | empty-trajectory rule / H1 "23/50 → 0/50" | **broken (vacuous)** | **high** | Every real trajectory starts with the orchestrator's canned `AssistantMessage` "Hi! How can I help you today?" (`orchestrator.py:48-50, 646-658`; 76/76 recorded sims). So `has_agent_text()` (`scorer_v2.py:332-333`) is always True and the rule never fires outside a synthetic empty list. H1 is true by construction (`noop_scan_v2.py:67`). The realistic no-op (greeting + refusal) goes to the judge, and 13 (up to 15) of the 23 no-op tasks carry only negative assertions such an agent satisfies (prediction from assertion text, not measured; §3.C1) |
| C2 | majority of 3 votes with provider-default sampling as an instrument | needs-change (reporting) | medium | 255/255 assertion verdicts are unanimous (765 votes, `judge_votes_stockview.csv`; `LLM_CACHE_ENABLED=False`, `config.py:71`, so the votes are real samples). Errors are systematic, not sampling noise: task 9 t1 was wrong 3/3. The judge is the agent's own model (Haiku 5.5), while tau2's configured NL judge is `gpt-5.4-mini`, reasoning low (`config.py:45-46`) |
| C3 | reply→assertion mapping when the judge paraphrases and reorders | **broken** | medium | Demonstrated: assertions [A1, A2]; the reply lists a paraphrased A2=False first, then A1=True verbatim. The mapper gives A2=**True** with `matched=1` (position fallback reuses A1's reply; `scorer_v2.py:366-373`). Silent, and `judge_votes.csv` cannot reveal it because the match mode is not logged |
| C4 | tau2 prompt used with Haiku | needs-change | medium (`-OO`: low) | tau2's example JSON has a trailing comma (`evaluator_nl_assertions.py:98`). A copied comma raises JSONDecodeError, and every assertion counts as unmet (demonstrated). Observed 0/252 calls so far. `_SYSTEM_PROMPT = …__doc__ and """…"""` (`scorer_v2.py:261`) becomes **None** under `python -OO` (verified). Python list repr of the assertions is harmless |
| C5 | `with_nl_basis` → reward includes NL; nothing else changes | holds | — | `evaluator.py:225-230` (NL runs when in basis), `245-250` (basis check passes), `261-264` (multiplies). ACTION is not in the basis and COMMUNICATE is unchanged. Stub judge: all met → 1.0; one unmet → 0.0; one omitted → 0.0 (verified through `evaluate_simulation`) |
| C6 | "assertion missing from reply = not met" biases toward 0 | needs-change (reporting) | medium | Stock tau2 ignores missing assertions (bias toward 1, `evaluator_nl_assertions.py:123-131`). v2 counts them unmet (bias toward 0). Neither is neutral. Observed: 0 missing in 765 votes, so the bounds coincide now. Report "undetermined" separately, re-ask, and give bounds |
| C7 | judge view (stock tau2: `role: content`) | broken → fix in progress | high (for task 9) | Stock view renders tool-call turns as `assistant: None` (verified). Task 9 t1 called `search_direct_flight(JFK, MCO, 2024-05-22)` (empty result). The judge, 3/3: "the call's parameters are not shown, so there is no evidence it was a search…". `55a35c0` adds `JUDGE_VIEW="with_tool_calls"` and logs the deviation; the judge has not yet been re-run with it (as of 15:25) |
| C8 | process-type NL assertions inside the reward | needs-change | medium | About 8 of 123 assertions check tool usage, not outcome (8: "get … user details", "uses single certificate"; 9: "searched for direct flights"; 16: "uses payment id"; 27/38: "confirms/verifies … delayed", "verifies the number of passengers"; 41: "checks all reservations"). tau2's docs reject penalising correct-but-different paths (`docs/evaluation.md:104-110`). Task 9 t0 (outcome correct, no search) flips 1→0 for this reason |
| D7 | task 7 fix | numbers hold; docs need-change | medium | 708 = 402 (7WPL39) + 306 (3EMQJ6). Both are upcoming (05-28; 05-25..30) and not cancelled, and A90KR2/9MRJD4 are past. **`task_fixes.md:20` is false**: "4/4 recorded trajectories answered 708 or did not state a total". In fact GT t0, Haiku t1 and Haiku t2 each state **$1,004**, and only t0 states $708. `task_fixes.md:26` ("remaining") ≠ `make_tasks_v2.py:47` ("other"). The dominant task-7 failure (the agent refuses upgrade-then-cancel as circumvention: GT turn 11, t1 turns 10 and 16, t2 turn 10) is untouched |
| D23 | task 23 assertion fix | holds | — | HAT023 JFK→SFO 2024-05-26; HAT204 SFO→SEA and HAT100 SEA→JFK 2024-05-28 (`db.json`). Business 364+248+259 = 871 = 500+198+129+44 = 250+621 |
| D32 | task 32 fix | numbers hold; untested; PLAN wording wrong | high until tested | +$396 (3×(196+110−94−80)) then −$510 (3×(306−136)), net −$114. `credit_card_9659780` = Visa 1777. Policy-compliant under the literal reading (`policy.md:110-120,131`). `PLAN.md:29` says "the original credit card", but the original payment was **gift_card_9823297** ($522). Whether the net clause flips the simulator is not tested (probe_32 was 10/10 refuse on v1 text) |
| D44 | task 44 fix | holds | — | Durations from `db.json`: NM1VX1 3 h / 3 h; KC18K6 3 h + 2 h (7 h end to end); H8Q05L 2.5 h; S61CZX has 5.5 h segments; WUNA5K is past (landed). Upgrade = business − paid: 484 + 740 + 163 = **1387**. Visa 7238 = `credit_card_4196779`, the only credit card |
| D-GT | fixes change what the GT agent is told | holds | — | The GT prompt contains only the reference actions (`llm_agent.py:148-173, 272-281`). The edits act through the simulator only |
| D-leak | fixes trivialise a task | holds, document | low | No answer is handed to the agent. The task-32 net clause encodes the reference path's shape (charge then refund). The task-44 clause states the reference's duration rule. Both are intended, but state it |
| E1 | S_hash / S_comm changed 0/76: is the overlay engaging? | holds: overlay engages; null is real | — | Through `evaluate_simulation` with rescore's exact arguments: task 8 GT, passengers reversed: v1 0.0 → hash 1.0. Task 20 GT, payment methods reversed: 0.0 → 1.0. Task 23 Haiku t0, first/last bookings swapped: 0.0 → 1.0. Task 23 with "$1,327" only: v1 1.0 → comm 0.0. 0 of 20 v1 DB mismatches are order-only; all 20 are content differences (cabin, flights, passengers, missing bookings, upgrades or cancellations). The defects are latent for this agent |
| E2 | replay gate 76/76 sufficient | holds; strengthen; fresh-set gate broken | medium (fresh) | Component-wise (DB match + every communicate check + reward) 76/76, and strict replay (`strict_replay=True`) 76/76 without exception (verified). For `--set fresh`, rescore loads `judge_cache.json` (`rescore.py:122`) while live runs write `judge_cache_live.json` (`run_v2.py:149`). The gate would re-judge (cost, stochastic) instead of replaying |
| E3 | post-hoc tuning exposure | needs-change (reporting) | medium | The 7_t0 0→1 flip is by construction: "708" was chosen from that transcript. `JUDGE_VIEW` was changed after seeing judge output (logged, but report both views). H1 cannot fail. H3's pre-stated direction "unchanged for real transcripts" for the no-op class failed for task 9 (2/3 trials flipped in the stock-view run) |
| E4 | overclaiming in the planned write-up | needs-change | medium | `make_summary_v2.py:184`: "a pass the scoring rule produced, not the agent (… 23/50 → 0/50)". `:185`: "order-only DB mismatches" (0 observed). `:92` asserts the gate passed without reading the file. `rescore.py:15`: "T2_stock … effect of the text … fixes" (recorded conversations cannot reflect text fixes) |
| E5 | provenance (PLAN rule 4) | **broken** | high (before paid runs) | `rescore*.csv` have no `scorer_version` and no commit column. `run_v2.py:50-54` stamps `git rev-parse HEAD` without a dirty check. During this review the judge code was dirty for about 6 minutes (15:08–15:14) before being committed as `55a35c0`; a run in that window would have been stamped `b0fc614` while running different judge code. Nothing prevents a repeat |
| E6 | H4 (GT passes 32, 7, 44) | needs-change | medium | One GT trial per task. Only task 32's v1 GT failure (simulator refuses $396) is what the fix targets. Task 7 GT: agent refuses upgrade-then-cancel ("would get around those rules"). Task 44 GT: transfer to a human after pushback on S61CZX. Neither is addressed by the fixes |
| F1 | maintainer framing | needs-change | high (external) | tau2 documents the refusal full reward as **intended** (`docs/evaluation.md:104-110, 156-158`: "an agent that does nothing but politely refuse will receive full reward 1.0 … the intended τ-bench scoring") and NL as "Experimental / WIP" (`:45`). nl_enforce is an alternative, stricter protocol, not a repair |

## 2. Main conclusions

1. **The overlay is technically sound and engages** (E1). The zero effect of `hash_canon` and `comm_boundary` on the 76 recorded simulations is a true null: this agent happened to use the reference orders and to state the answers explicitly. These defects are latent. Report them as "0/76 recorded verdicts affected; synthetic perturbations of real trajectories flip as designed".
2. **`nl_enforce` does not do what H1 claims** (C1). It closes only a trajectory that cannot occur live. Whether it closes the realistic no-op depends on the assertion wording, and most no-op-class assertions are negative ("does not cancel …"), which a refusal agent satisfies truthfully. tau2's docs call that outcome intended (F1).
3. **The judge is the weakest link** (C2–C4, C6–C8). The only reward-changing NL verdicts on recorded data so far are task 9: t1 is an instrument error (stock view), and t0 is a process assertion. The planned write-up's sentence "a pass that disappears under V2 is a pass the scoring rule produced, not the agent" is not supported by these two cases.
4. **The four task fixes are numerically correct** (all totals and itineraries re-derived from `db.json` and the tools). Two documents contain factual errors, and the task-32 fix is unproven against the simulator.

## 3. Details

### A. hash_canon

- **Ids and suffixes (A1a).** `canonical_dump` deletes and re-inserts new reservations one at a time and appends "+" on collision (`scorer_v2.py:116-132`). The user list is rebuilt with the same `res_map` (`:137`). Two identical bookings produce `[NEW_RES:X, NEW_RES:X+]` in both the reservation table and the user's list, and differ from one booking (verified). Reservation content includes `user_id` and the payment history, so cross-user or cross-certificate swaps stay distinct. Example: in task 23, swapping certificate_9984806 and certificate_2765295 between Raj and Liam changes both reservations' content.
- **Multiset payment history (A1b).** Charge-then-refund and refund-then-charge on a gift card commute when both succeed, which gives the same balance and the same multiset. When the order matters, one call errors or the cancellation refunds a different set, so content differs. Task 7, order "102": gold `[+296, +1072, −296, −1072]` vs variant `[+296, −296, +1072]`, so the canonical hashes differ.
- **Generated certificate ids (A1d).** Snippet (blocked-model environment, task-8 user):
  - Run A: send 200 (→`certificate_3221322`), send 300 (→`…323`), book HAT271 2024-05-26 economy for 1 passenger paying 174 with `…322`.
  - Run B: send 300 (→`…322`), send 200 (→`…323`), book paying 174 with `…323`.
  - Result: canonical equal **False**, diff `/reservations/NEW_RES:b789…: only in B`. Without the booking, canonical equal True.
  - Effect: equivalence is missed (conservative, not a collision), but the docstring claim is too broad. This needs in-episode compensation followed by use of the new certificate, which none of the 20 sampled tasks requires.
- **Itinerary order (A3).** `update_reservation_flights` and `book_reservation` store flights in agent order (`tools.py:331, 756`). Keeping the list order is defensible but strictly more conservative than needed. Sorting by (date, scheduled departure) is a semantic canonical form and cannot merge two different trips.
- **Residue (A4)**, canonical diffs gold vs variant:
  - Task 7 "102": `/reservations/XEHM4B/payment_history: list len 4 vs 3`.
  - Task 32 "10": `/reservations/OWZ4XL/flights: list len 1 vs 2`, `flight_number "HAT041" vs "HAT202"`, `price 136 vs 196`, payments `−510/+396` vs `−114/+510`.
- **Coverage.** `noop_scan_v2.py:32` caps task 18 at 24 of 119 permutations (lexicographically first, so write 0 never moves). The five writes touch five different reservations, so the result is not in doubt, but the table should say "24/119". H2 covers call order only. Argument-list order (tasks 8, 20) is covered by the selftest and by E1a/E1b here; add both to the H2 table.

### B. comm_boundary

Battery (`info_in_text`; v1 = `info in text.lower().replace(",", "")`):

| info | text | v2 | v1 |
|---|---|---|---|
| 1000 | `$1,000.00` / `1000 dollars` / `1,000` / `USD 1000` / `total: 1000.` / `(1000)` | ✓ | ✓ |
| 1000 | `1000%` / `1000/` | ✓ (accepted) | ✓ |
| 1387 | `$1,387` / `$1387.00` | ✓ | ✓ |
| 1387 | `$1,387.50` / `1,387,000` | ✗ (correct) | ✓ (v1 defect) |
| 1387 | `1 387` / `1.387` / `one thousand three hundred eighty-seven` | ✗ | ✗ |
| 708 | `Flight HAT708 departs at 10:00` | **✓ (FP)** | ✓ |
| 708 | `402,306` | ✗ | ✗ |
| 4 | `You can bring four suitcases.` | **✗ (FN)** | ✗ |
| 4 | `4:15 PM` / `May 4.` / `on 5/4/2024` / `the 4th of May` / `reservation MZDDS4` / `reservation 4WQ150` / `a 4% fee` / `Terminal 4` | **✓ (FP)** | ✓ |
| 4 | `2024-05-04` | ✗ (correct) | ✓ (v1 defect) |
| 327 | `$1,327` | ✗ (correct) | ✓ (v1 defect) |
| 327 | `$1 327` | ✓ (FP, rare) | ✓ |

- The numeric pattern `(?<![\d.])N(?:\.0+)?(?!\d|\.\d)` (`scorer_v2.py:210`) only forbids digit adjacency. Requiring a non-word boundary on both sides (`(?<![\w.])`, `(?!\w|\.\d)`) would reject `HAT708`, `MZDDS4`, `4th` and `4WQ150`, and still accept `$`, `(`, `USD 1000` and `**4**`. Times, dates and `4%` still need either a short-target rule or an honest residual statement.
- The block-1 2g evidence for task 3 (`2024`, `$149`, `24 hours`) is all digit-adjacent, so v2 closes exactly the documented cases, not the class.
- On the recorded data the residuals did not bite. Task 3's standalone `4` hits are all the answer: t0 3 hits, t1 4, t2 6, GT 4, each "4 free checked bags".

### C. nl_enforce

- **C1, empty-trajectory rule.** `DEFAULT_FIRST_AGENT_MESSAGE = AssistantMessage(content="Hi! How can I help you today?")` is placed in the trajectory before any agent call (`orchestrator.py:48-50, 646-658`), in 76/76 recorded simulations. `has_agent_text([greeting, user])` → True (verified). Block 1's own 2b definition is "keep only the default greeting and one user turn" (`checklist.md:34`), and under v2 that probe goes to the judge, so H1 as computed does not replicate the 2b probe.
- **Refusal bot**: greeting → user request → "I'm sorry, I can't help with that." → stop; no tool calls, so DB and communicate pass as for the empty trajectory. Predicted judge outcome from the assertion texts of the 23 no-op tasks:
  - **likely pass (13):** 0 ("should refuse to proceed"), 1, 6, 10 (vacuous: "does not offer to change cabin for only some"), 28, 31, 34, 36, 45, 46, 47, 48, 49;
  - **uncertain (2):** 26, 43 ("because/since it does not meet …");
  - **likely fail (8):** 2, 4, 5, 9, 13, 27, 38, 41 (each has a positive or process assertion).

  This is a reading of the assertion texts, not a measurement. Measuring it costs about 69 short judge calls (≈ $0.05 at $0.10/$0.50 per million tokens, using the observed ~830 output tokens per call). PLAN.md:19's rationale ("an assertion about what the agent said cannot be satisfied by saying nothing") does not match the assertion types: most say what the agent must **not do**.
- **C2, instrument.** Report unanimity (255/255, stock view), and hand-check every reward-changing verdict plus all process-type verdicts, not a uniform random 20 (194/255 verdicts are "met"; a uniform sample will rarely hit the flips). State that the judge is the agent's model (self-evaluation risk) and differs from tau2's configured judge. A cheap cross-check is to re-judge only the reward-changing verdicts with a stronger model.
- **C3, mapping.** Use one-to-one assignment: exact text first, never reuse a reply, and number the assertions in the prompt with the index required in the reply. Log the match mode per vote (`text` / `position` / `missing`).
- **C4, parsing.** On JSONDecodeError or a missing assertion, re-ask (bounded), and log the raw reply. Counting a parse failure as "unmet" turns a formatting slip into a reward of 0. Replace `__doc__ and """…"""` with the literal (or `inspect.getsource` extraction, as the check here did). The prompt is identical to tau2 only after whitespace normalisation, not byte-identical. That is harmless, but say "identical up to whitespace".
- **C6, missing = unmet.** Report the NL pass rate with missing→unmet and missing→met as two bounds plus the count. With 0 missing so far, say so explicitly. That pre-empts the "biased toward 0" critique.
- **C7, view.** The stock view hides tool names and arguments (`evaluator_nl_assertions.py:75-77`). Task-9 t1 judge reasoning: "the call's parameters are not shown, so there is no evidence it was a search for direct JFK to MCO flights". The new `with_tool_calls` view (`scorer_v2.py:305-329`) fixes this but adds a new risk: "Agent communicates X" could now be credited from tool-call arguments or tool results rather than speech. Include such verdicts in the hand-check. Report both views (the deviation entry already plans to keep the stock-view files). The stock view's blindness is a tau2 finding in its own right.
- **C8, process assertions.** Classify all 123 assertions as (a) duplicate of the DB check, (b) communication, (c) negative or no-action, (d) process/tool usage. Report NL flips by class. Either keep class (d) out of the reward or report two NL variants, because tau2's stated rationale for outcome scoring (`docs/evaluation.md:104-110`) applies directly to them.

### D. Task fixes

- **Task 7.** Verified from `db.json`:
  - Paid totals: 7WPL39 402 (2 passengers, fares 342 + $60 insurance), XEHM4B 296, 59XX6W 624, 3EMQJ6 306; A90KR2 (05-14) and 9MRJD4 (05-06/05-13) are past. 1628 = all four; 708 = the two others.
  - The v2 instruction "(other than the two reservations you are cancelling)" makes 708 correct even when the agent refuses to cancel XEHM4B. That is good.
  - Residual: a fare-only answer, $648, is defensible and fails.
  - Fix `task_fixes.md:20`. Recorded totals: Haiku t0 "$708"; GT t0, Haiku t1, Haiku t2 "$1,004" (402+306+296, XEHM4B still active after the agent refused upgrade-then-cancel).
  - Align `task_fixes.md:26` with `make_tasks_v2.py:47`.
  - In 3 of 4 runs the agent refuses upgrade-then-cancel ("Upgrading it to business only to cancel it would get around those rules", 7_gt_t0 turn 11; similar in t1 turns 10 and 16 and t2 turn 10). That mechanism, not the string, decides task 7 in most trials, and v2 leaves it as is (block 1 coded it "borderline A").
- **Task 32.** Arithmetic and policy as in the table. Two requests:
  - (i) Run `scripts/probe_32.py` with the v2 instruction text and the same pre-registered rule, before the paid run. ACCEPT ≥ 8/10 means the fix works; ≤ 5/10 means it does not.
  - (ii) Add a second counterfactual where the agent quotes only step 1 (+$396) without mentioning the refund. If the simulator now accepts that too, the net clause over-corrects: it makes the simulator accept a charge above its budget without a stated refund.

  Category-5 noise (32_gt_t0 "I didn't book this for anyone else"; OWZ4XL has 3 passengers) can still sink a GT trial. Pre-state how such a trial is classified.
- **Task 44.** Fully re-derived; consistent. Not changed, correctly: the cancellation clause; S61CZX stays un-cancelled ("You DO NOT want to upgrade to business and then cancel it").
- **Task 23.** Correct. Note that this fix only matters because nl_enforce makes NL count. It is a prerequisite of nl_enforce, not a standalone text fix.
- **Unaudited assertions.** nl_enforce applies to all 50 tasks in H1, but the 4e-type audit of assertions covered only the 20 sampled tasks. A quick scan (flight numbers in assertions vs reference arguments) found nothing beyond task 27's status check, but the other 30 tasks' assertions are unaudited. Say so wherever a 50-task NL number is cited.

### E. Methodology

- **E1.** Hook proofs as in the table. The snippet (model calls blocked first) is in the appendix.
- **E2, gate.**
  - Recorded set: keep the reward gate and add the component-wise and strict-replay gates (both 76/76 now, no cost).
  - Fresh set: point the gate at the live cache (`judge_cache_live.json`), or compare against the recorded `reward_info.nl_assertions`, so that "V2 reproduces the recorded reward" is a replay.
  - Add an **engagement gate** (no cost): the four perturbations in E1 must flip as stated before any V2 number is reported.
- **E3/E4, attribution and wording.**
  - Attribute every flip to its component (T2 criteria / S_hash / S_comm / S_nl).
  - Mark 7_haiku_t0 0→1 as "by construction".
  - For fresh runs, isolate the scorer effect as **T2_stock vs V2** (same criteria, same conversations) and the criteria effect as v1 vs T2_stock. The v1-vs-V2 table in `make_summary_v2.py:171-181` mixes both.
  - Use the 16 untouched tasks as a test–retest noise control between block-1 runs and fresh runs.
  - Use paired exact tests (McNemar) on identical trajectories, not unpaired Wilson intervals.
  - On recorded data, pass^3 drops 0.60 → 0.55 under V2 entirely because of task 9 (stock view: one instrument error, one process assertion). Cite it only with that caveat.
- **E5, provenance.** Stamp `scorer_version`, overlay commit and a dirty flag into every CSV and summary, and make `run_v2.py` and `rescore.py` refuse to run on a dirty tree (`git status --porcelain scripts/v2 block2`). The judge code was briefly dirty during this review (committed as `55a35c0` at 15:14), which shows the guard is needed.
- **E6, H4.** Pre-register per task what "the fix worked" means:
  - 32: the simulator authorises step 1 and the target DB is reached.
  - 7: in GT trials whose DB matches, COMM passes.
  - 44: the per-segment rule is stated, the total is quoted, and the upgrades are done.

  Run 3 GT trials for 7, 32 and 44 (n=1 is a coin flip under simulator noise).
- **E7, run settings.** `run_v2.py` builds `TextRunConfig` directly, while block 1 used the CLI (`tau2 run-pass3`, which in generic mode equals `run` with 3 trials). The substring scorer is set (`run_v2.py:76`), good. `PLAN.md:51` should list `--communicate-scorer substring`. Before paying, diff the `Info` the runner will save against block-1 `results.json["info"]` (excluding `language_tasks`, pins, task set). Any other difference is a confound for H5.

### F. Other exposure

- F1 (framing) as in the table: present v2 as "the same trajectories under a stricter, documented alternative protocol". A maintainer will otherwise answer the 2a/2b and I1 labels with `docs/evaluation.md:156-158`.
- `PLAN.md:29` "refund destination named (the original credit card)": the original payment of OWZ4XL is `gift_card_9823297`; write "the Visa ending 1777 used in the reference".
- `JUDGE_ARGS={}` runs Haiku 5.5 with provider defaults (adaptive thinking, effort medium). Record that in the judge settings.
- Cost constants $0.10/$0.50 per million tokens match the published Haiku 5.5 rate for prompts up to 100K tokens. Judge prompts are about 6K tokens, so the estimate is consistent.

## 4. Required changes, ranked

**Must (before any paid live run)**
1. The overlay commit is done (`55a35c0`). Still to do: stamp all v2 outputs with `scorer_version`, commit and a dirty flag (PLAN rule 4), and make `run_v2.py`/`rescore.py` refuse a dirty tree.
2. Re-specify H1 in "Deviations":
   - keep the empty-list result as a rule check only;
   - exclude the canned greeting from `has_agent_text` (message 0 equal to `DEFAULT_FIRST_AGENT_MESSAGE.content`);
   - measure the block-1 2b probe (greeting + one user turn) and a refusal bot on all 23 no-op tasks with the 3-vote judge (≈ $0.05);
   - report that pass rate next to 23/50.
3. Fix the judge-reply handling:
   - one-to-one mapping with indexed assertions, and log the match mode;
   - re-ask on parse failure or a missing assertion, and log raw replies;
   - report "undetermined" with bounds;
   - re-run stage B with the committed view and keep the stock-view files.
4. Pre-test the task-32 fix: probe_32 with the v2 text (n=10, same rule) plus the "step 1 only" counterfactual (≈ $0.01 total).
5. Make the fresh-set gate a replay: live judge cache or recorded NL verdicts. Add the no-cost engagement gate (the four E1 perturbations).
6. Correct the factual errors (`task_fixes.md:20`, `task_fixes.md:26` vs `make_tasks_v2.py:47`, `PLAN.md:29`) and the over-claiming lines (`make_summary_v2.py:92, 184-185`, `rescore.py:15`).

**Should**
7. Re-state H4 per task by mechanism, with 3 GT trials for 7, 32 and 44.
8. Classify the 123 NL assertions (DB-duplicate / communication / negative / process). Report NL flips by class, and decide (as a logged deviation) whether process assertions enter the reward.
9. Hand-check sample: all reward-changing verdicts, all process verdicts and all "communicates X" verdicts under the new view, filled at random to ≥20, plus a blind second reader. Optionally re-judge the reward-changing verdicts with a stronger model.
10. Fresh-run analysis: T2_stock vs V2 for the scorer effect, v1 vs T2_stock for criteria, the 16 untouched tasks as the noise control, paired exact tests.
11. Tighten the numeric boundary to non-word characters, and document the remaining time/date/percent FP classes and the spelled-out FN.
12. Diff run_v2's `Info` against block 1 before paying (no cost). Add `--communicate-scorer substring` to `PLAN.md:51`.
13. Frame v2 as an alternative protocol, citing `docs/evaluation.md:45, 104-110, 156-158`.

**Nice**
14. hash_canon: remap generated payment-method ids inside `payment_history`, or narrow the docstring. Consider a chronological sort of `Reservation.flights`.
15. Replace the `__doc__ and` prompt trick.
16. Put judge model, prompt hash, view and votes into the cache key, and store raw votes in the cache.
17. H2 table: state 24/119 for task 18, and add the argument-list permutations (8, 20).

## Appendix — reproduction

Scripts (kept in `block2/skeptic_design_checks/`, read-only, model calls blocked; run from `tau2-bench` with `uv run --no-sync python <path>`):
- `block2/skeptic_design_checks/check_hooks.py`: E1a–E1e, C1, C3, C4, prompt identity.
- `block2/skeptic_design_checks/check_canon_comm.py`: A1, A1b, A1c, A3, A4, the comm battery, task-3 `4` hits.
- `block2/skeptic_design_checks/check_gate.py`: component-wise and strict replay gate.

Condensed E1a (the other perturbations differ only in the edited argument):

```python
import sys; sys.path.insert(0, r"..\scripts\v2"); import scorer_v2 as s2
def blk(*a, **k): raise RuntimeError("model call blocked")
import tau2.utils.llm_utils as lu; s2.generate = blk; lu.generate = blk
from tau2.data_model.simulation import Results; from tau2.data_model.message import AssistantMessage
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation; from tau2.orchestrator.modes import CommunicationMode
s2.install(); r = Results.load(r"..\results\runs\sample20_gt_haiku.results.json"); T = {t.id: t for t in r.tasks}
sim = next(s for s in r.simulations if s.task_id == "8").model_copy(deep=True)
for m in sim.messages:
    if isinstance(m, AssistantMessage) and m.tool_calls:
        for tc in m.tool_calls:
            if tc.name == "book_reservation": tc.arguments["passengers"].reverse()
for h in (0, 1):
    s2.SWITCHES.set(bool(h), False, False)
    ri = evaluate_simulation(simulation=sim, task=T["8"], evaluation_type=EvaluationType.ALL, solo_mode=False, domain="airline",
                             mode=CommunicationMode.HALF_DUPLEX, env_kwargs=None, strict_replay=False,
                             communicate_scoring=r.info.effective_communicate_scoring)
    print(h, ri.reward, ri.db_check.db_match)   # 0 0.0 False / 1 1.0 True
```

Condensed C3 (mapping):

```python
reply = {"results": [{"expectedOutcome": "The agent did not cancel reservation 59XX6W", "reasoning": "it did cancel", "metExpectation": False},
                     {"expectedOutcome": "Agent cancels XEHM4B.", "reasoning": "yes", "metExpectation": True}]}
s2.generate = lambda *a, **k: AssistantMessage(role="assistant", content=json.dumps(reply))
s2._one_vote("assistant: hi", ["Agent cancels XEHM4B.", "Agent does not cancel 59XX6W."], 0)
# -> both met=True, matched=True  (the judge said the second one is False)
```
