# Skeptic verification of the medium/high defect rows (τ²-bench airline audit)

Scope: the 27 rows of `audit_log.csv` with defect=1 and severity high or medium (`ALL` rows are low and out of scope). Checkout `tau2-bench` at tag v2.0.0, commit `989d3285ae669e49503324bdb9981bf14fccedeb` (clean working tree). Verdicts: `results/skeptic_verdicts.csv`.

## How the rows were checked

- **Scoring code read.** `evaluator_env.py` replays the agent’s mutating calls through `Environment.set_state` and the reference actions through `make_tool_call` on a fresh environment, then compares `get_db_hash()`. `evaluator_communicate.py` (substring) lower-cases each assistant message, strips commas from the agent text only, and returns 1.0 for an empty `communicate_info` before it reads the trajectory. `evaluator.py` under `EvaluationType.ALL` multiplies only the components in `reward_basis`, so `nl_assertions` (natural-language assertions) never affect airline reward. `batch.py:367` defaults to `ALL`. `toolkit.py:242-244` hashes `get_dict_hash(db.model_dump())`, and `utils.py:36-43` computes `sha256(json.dumps(obj, sort_keys=True, default=str))`. That sorts dict keys but **keeps list order**.
- **Audit scripts.** `scripts/static_scan.py` and `scripts/probe_2h.py` use the registry’s airline constructor (`get_environment`), `make_tool_call`, `get_db_hash`, and tau2’s own `EnvironmentEvaluator` / `CommunicateEvaluator`. The 2b probe calls these two classes on an empty trajectory instead of rescoring "greeting + one user turn" with `tau2 evaluate-trajs`. The checklist’s route needs a recorded run, and none exists (`cost.md`: no API calls). From the code the outcome is the same: those turns contain no tool calls, an empty `communicate_info` short-circuits to 1.0, and ACTION is not in the basis.
- **Independent recomputation without tau2.** The hash was re-implemented in the standard library, with the `model_dump` defaults: `Reservation.status=None`, float balances, int prices. The six airline WRITE tools (`book_reservation`, `cancel_reservation`, `update_reservation_flights/_baggages/_passengers`, `send_certificate`) were re-implemented the same way. Together they reproduce:
  - the initial hash `124e39a6…`;
  - **all 50** target hashes in `static_scan.csv`;
  - **all 13** rows of `probe_2h.csv`, including the exact strings of differing orders.

  Every variant hash quoted below comes from this re-implementation (8-hex prefixes). The scripts are temporary and live outside the project, in the session scratchpad folder `skeptic/` (`emu_hash.py`, `emu_tools.py`, `check_gold.py`, `variants.py`, `probe2h_emu.py`).
- Prices, balances and times come from `db.json`; policy line numbers refer to `policy.md`.

## Per-row verdicts

### 2a: target hash = initial hash and `communicate_info` empty (high). 7 rows, all confirmed

- **1/2a.** Actions are `get_user_details` and `get_reservation_details`, both READ. `communicate_info=[]`, basis [DB, COMMUNICATE]. Target = initial = `124e39a6`, reproduced. Confirmed. This is the documented "intended τ-bench scoring" example (`docs/evaluation.md`, the worked example for task 1).
- **9/2a.** The only action is `search_direct_flight` (READ). `communicate_info=[]`, target = initial. Confirmed.
- **10/2a.** `actions=[]`, `communicate_info=[]`, target = initial. Confirmed.
- **26/2a.** `actions=[]`, `communicate_info=[]`, target = initial. Confirmed.
- **28/2a.** `actions=[]`, `communicate_info=[]`, target = initial. Confirmed.
- **46/2a.** `actions=[]`, `communicate_info=[]`, target = initial. Confirmed.
- **48/2a.** The only action is `get_reservation_details` (READ). `communicate_info=[]`, target = initial. Confirmed.

### 2b: an empty answer scores 1.0 (high). 7 rows, all confirmed

- **1, 9, 10, 26, 28, 46, 48 / 2b**, one row each.
  - Claim: an empty trajectory scores 1.0.
  - Checked in `static_scan.csv`: `noop_db_reward=1.0`, `noop_comm_reward=1.0`, `noop_pass=1`.
  - Code path: the predicted DB stays initial, which equals the target. The user-DB hash is None on both sides because airline has no user tools. COMMUNICATE returns 1.0 on an empty list.
  - Verdict: confirmed for all seven.
  - 2a and 2b agree on every one of the 7 tasks, and on all 50 tasks (`positive_control == noop_pass`). They are one phenomenon measured two ways: a hash rule and an evaluator call.
  - Caveat: this is the substitute in-process procedure described above, not the checklist’s `evaluate-trajs` path.

### 2g: short expected string matches by accident (medium)

- **3/2g.**
  - Claim: `communicate_info=["4"]` can be met by accident.
  - Checked: the scorer looks for "4" in **every** assistant turn of the conversation. The reservation the agent must read (JMO1MG) has date `2024-05-16`, fare `149` and `created_at` `2024-05-13`. All 30 flight dates in the DB contain "2024".
  - Computation: the constructed wrong reply "As a Gold member … 6 in total … May 16, 2024" passes; the greeting "Hi! How can I help you today?" does not.
  - Verdict: **confirmed**. The task has no writes, so DB reward is automatically 1.0. A one-character string therefore carries the whole score, and echoing the flight date with its year is a natural move in a wrong "Gold → 6" answer.
  - Weaknesses in the evidence:
    - The checklist’s own search (the 2b probe plus GT, i.e. ground-truth, and Haiku trajectories) was not possible. The 2b branch is negative and no runs exist.
    - "Near-certain" is unsupported.
    - "24 hours" is irrelevant to a baggage question.

### 2h: correct variant rejected because of order or free choices (medium)

- **23/2h.**
  - Claim: reordering the three bookings changes the hash.
  - Checked: re-running the probe reproduces `probe_2h.csv` exactly. 20 of 23 orders differ. The only hash-neutral orders are `1023`, `1203` and `1230`, which move the cancel and nothing else. So all 5 non-identity booking orders × 4 cancel positions change the hash.
  - Cause: `_get_new_reservation_id` hands out HATHAT, HATHAU and HATHAV in call order.
  - The scenario lists "for you … for Raj … for Liam" but does not fix the booking order, and the policy is silent.
  - Verdict: confirmed.

### 2k: requirement stated only in `nl_assertions` (medium). 4 rows, all confirmed

- **9/2k.**
  - Assertion: "Check that Agent searched for direct flights between JFK and MCO on May 22 2024."
  - The DB has no JFK→MCO flight at all. An agent that skips the search, or states "no nonstop" without checking, ends at DB = initial with no required strings and scores 1.0.
  - Verdict: confirmed.
  - Low information: the row follows from the 2a/2b no-op pass, and the docs make READ steps non-required by design.
- **10/2k.**
  - Assertion: "…does not offer to change cabin for only some of the flights in a reservation."
  - Computation: the cheapest May-24 business IAH→SEA is HAT190+HAT047 = 464+202 = 666. A partial (outbound-only) offer costs (666−(126+139))×3 = **1203** ≥ 1000, so the user declines, nothing is written, and the score is 1.0.
  - An executed upgrade would be a write and would be caught: the full upgrade costs 2010 and changes the hash.
  - Verdict: confirmed (verbal violation, unscored by design).
- **44/2k.**
  - Assertion: "The total cost that the agent mentions is between $1380 and $1390."
  - Computation: the reference upgrades cost 484+163+740 = **1387**.
  - `communicate_info=[]` and the user has no budget limit. Three correct upgrades with a wrong or missing total therefore reach the target `0c788749` and score 1.0.
  - Verdict: confirmed. This is the only 2k row that is a real authoring gap: "1387" could have been put in `communicate_info`.
- **46/2k.**
  - Assertion: "Agent does not cancel insurance or offer a refund."
  - No tool edits insurance. A verbal refund offer, or a false "done" with no write, keeps DB = initial and scores 1.0.
  - Verdict: confirmed.
  - Inconsistency: batch 3 judged the same pattern 0 for tasks 26 ("does not offer the refund") and 28 ("does not offer any refund").

### 4a: request vs reference (medium)

- **44/4a.**
  - Exact words: `reason_for_call` says "For the flights that are under or equal to 3 hours (including layovers), ask the agent to upgrade you to business wherever possible."
  - The reference action 44_19 upgrades KC18K6, which is HAT300 06:00–09:00 plus HAT215 11:00–13:00: **7 h end to end** including the 2 h layover. The nl assertions "Agent updates KC18K6 to business" and the $1380–1390 total show the author used a per-segment reading, which turns "(including layovers)" into a dead clause.
  - Computation: the layover reading (NM1VX1 + H8Q05L, $647) hashes `cae93edd`, not the target `0c788749`.
  - Verdict: confirmed (at minimum a two-reading ambiguity, and the reference takes the weaker reading).

### 4c: open choice fixed by the reference (medium). 5 rows, all confirmed

- **8/4c.**
  - Passenger order is open in both the policy and the scenario.
  - Computation: [Kevin, Sophia] hashes `c6e939a7`, the target is `00766aa3`.
  - The rest is pinned: HAT271 economy is 174×2 = 348, and only `certificate_8045380` (500) covers it, since `certificate_3887113` has 150.
  - Verdict: confirmed. This is an order-only finding (the 2h class, filed as 4c) with low likelihood: putting the booking user first is natural.
- **20/4c.**
  - `payment_history = deepcopy(payment_methods)` stores the payments in call order.
  - Computation: [card 5, certificate 250] hashes `5332159e`, the target is `a561da60`. Amounts are pinned: 152+103 = 255 = 250 + 5, and gold economy gives 3 free bags.
  - Verdict: confirmed (order-only). It is plausible because the profile lists `credit_card_4421486` first.
- **23/4c.**
  - Two open orders:
    - booking order, the same finding as 23/2h;
    - payment-list order: reordering the first booking’s list hashes `5f24be24`, the target is `b46d1bed`.
  - Amounts are pinned: 364+248+259 = 871 per passenger, and the Mastercard total is 44+621+621 = 1286.
  - Verdict: confirmed (order-only; double-counts 23/2h).
- **32/4c.**
  - Computation: step 1 is (196+110−94−80)×3 = **+396**, and both gift cards (183 and 224) raise "balance is not enough", so step 1 must go on the card. Step 2 is (136−306)×3 = **−510**.
  - The tool accepts either gift card for the refund, and policy line 131 allows "a single gift card or credit card for payment or refund method". The resulting hashes are `c40c29e3` and `e874ca80`, against the target `caea5724`.
  - Verdict: confirmed (a genuine payment choice).
- **44/4c.**
  - The H8Q05L upgrade (+163) fits within `gift_card_5094406` (balance 274), and the tool accepts it. The result hashes `3af7f243`, not `0c788749`.
  - NM1VX1 (484) and KC18K6 (740) raise on that card, and certificates are rejected for updates.
  - Verdict: confirmed (a genuine payment choice).

### 4e: nl assertion contradicts the reference (medium)

- **23/4e.**
  - Exact words: nl assertion 4 says "…with outbound flights HAT023 and HAT204 on 2024-05-26 and return flight HAT100 on 2024-05-28…".
  - The reference action 23_1 books HAT204 (SFO→SEA, 08:00–10:00) on **2024-05-28** as the first return leg.
  - The assertion is wrong on both date and direction. A literal reading also gives an impossible itinerary: HAT204 leaves SFO on 05-26 at 08:00, before HAT023 arrives at 20:00.
  - Verdict: confirmed. It has no reward effect at this commit because nl assertions are unscored.

## Summary

| check | rows | confirmed | rejected |
|---|---|---|---|
| 2a | 7 | 7 | 0 |
| 2b | 7 | 7 | 0 |
| 2g | 1 | 1 | 0 |
| 2h | 1 | 1 | 0 |
| 2k | 4 | 4 | 0 |
| 4a | 1 | 1 | 0 |
| 4c | 5 | 5 | 0 |
| 4e | 1 | 1 | 0 |
| **total** | **27** | **27** | **0** |

- **Rejected rows: none.** Every defect_if rule holds, every evidence string is factually correct (prices, balances, times and hashes re-derived), and every severity matches the checklist. No "severity should be X" flag applies.
- **Reproducibility flags:**
  - 3/2g rests on a constructed reply; no agent trajectory exists.
  - The seven 2b rows come from an in-process substitute for the checklist’s `evaluate-trajs` probe. They are reproducible with `scripts/static_scan.py`, which needs the uv environment.
  - 23/2h: `probe_2h.csv` stores raw order strings, so "all 5 reorderings" has to be decoded from them.
- **Confirmed does not mean material.** The 27 rows fall into four groups:
  - **reward-affecting and task-specific:** 3/2g, 32/4c, 44/2k, 44/4a, 44/4c;
  - **hash-order artifacts:** 8/4c, 20/4c, 23/2h, 23/4c;
  - **no reward effect at this commit:** 23/4e;
  - **documented design class:** 2a/2b ×7, plus 2k on the no-op tasks 9, 10 and 46.

## Systematic issues in the audit method

1. **2a/2b flag a documented design choice as "high".** `docs/evaluation.md` calls the no-op pass the intended scoring. `issues_draft.md` agrees it is not an issue, yet these rows drive the 13/20 headline. The 13 tasks split into three groups:
   - 7 no-op-class tasks: 1, 9, 10, 26, 28, 46, 48;
   - 3 order-only tasks: 8, 20, 23 (23 also has the unscored 4e row);
   - 3 substantive tasks: 3, 32, 44.

   The audit’s "excluding no-op" figure, 9/20 [0.258, 0.658], still includes 9, 10 and 46, whose remaining rows are 2k findings that follow from the same no-op design. Excluding them as well gives 6/20 = 0.30 [0.145, 0.519]. Excluding order-only and unscored-field rows too gives 3/20 = 0.15 [0.052, 0.360]. All intervals are 95% Wilson.
2. **2k cannot separate a task defect from outcome-only scoring, and it was applied inconsistently.** On a no-op task, every non-write assertion is unenforced by construction. The verbal "offer" pattern was scored 1 in batch 2 (task 10) and batch 4 (task 46), but 0 in batch 3 (tasks 26 and 28), citing a "convention in the brief" that is not on disk. Under the literal rule, 26 and 28 (and arguably task 1, "should not approve") are false negatives. The task-level count does not change.
3. **The order findings are one benchmark-wide hash property split across 2h and 4c.** The 2h probe permutes only whole WRITE calls, so list order inside a call fell to the 4c checks on tasks 8, 20 and 23. Read literally, 4c also fires on flight-list order: reversing the `flights` list changes the hash in 11 of the 13 sampled write tasks. The exception is task 32, where the second update overwrites the first. The audit did not count those, which is a reasonable "chronological order" filter, but it shows that order-only rows measure how many free-order lists a task has, not how clear its specification is.
4. **Severity has no likelihood or reward-impact axis.** A typo in an unscored field (23/4e) and a near-zero-probability passenger order (8/4c) carry the same "medium" as the genuine payment choices (32, 44) and the layover conflict (44/4a).
5. **No agent runs exist**, so several checks ran on substitutes or constructed examples rather than the checklist’s procedure:
   - 2g’s trajectory search did not run;
   - 2b’s `evaluate-trajs` probe was replaced by an in-process call;
   - the violating behaviours in 2k were constructed, not observed.
6. **Provenance gaps.**
   - Review batches 2–4 report `static_scan.csv` columns as missing that exist in the current file, so the reviews were done against an earlier version.
   - `scripts/probe_2h.py` caps the sweep at 24 permutations ("max 3-4 writes"), but task 18 has 5 writes (119 orders). A full emulated sweep finds 0 differences, so there is no effect on any result.
