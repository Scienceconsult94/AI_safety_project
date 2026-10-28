# Adversarial review, consistency pass: row 22/2h

Scope: one row of `results/review_overrides_consistency.csv`, task 22, check 2h (defect 1, severity medium), tau2-bench v2.0.0, commit 989d3285ae669e49503324bdb9981bf14fccedeb, airline domain. Conventions: sections "Tools and limits", "Scoring facts" and "Conventions from block 1" of `airline_full/skeptic_brief.md`.

Output: `results/skeptic_verdicts_consistency.csv` (1 row) and this file.

## Verdict

**Holds as filed: defect 1, medium (skeptic_ok = 1).**

- The row rests on the write-time reading of the free-bag allowance: the allowance follows the cabin the reservation has when the bags are added.
- 17/2h was confirmed under the same assumption.
- Under the other defensible reading (the final cabin governs), 22/2h and 17/2h would both be 0. The two rows must move together.
- No difference between the two tasks changes the label. The differences change only how likely the failing path is.

## The seven tests

1. **Replays and recomputation.** The two end states hash differently.
   - Reference: 37ea6df3. Bags first: edc62003. Initial DB: 124e39a6.
   - The data, from `db.json`:
     - omar_rossi_1241 is a gold member;
     - FQ8APE is basic_economy, with 1 passenger (Ivan Garcia) and bags 0/0;
     - the fares paid are HAT056 71 and HAT138 60;
     - the economy fares on 2024-05-25 are 155 and 185;
     - gift_card_8190333 holds 280.
   - The allowance, from `policy.md` 91-95: a gold member gets 2 free bags per basic-economy passenger and 3 per economy passenger. Each extra bag costs 50.
   - Bags first:
     - free bags: 2 x 1 = 2;
     - nonfree: 3 - 2 = 1;
     - fee: 50 x max(0, 1 - 0) = 50 (`tools.py` 649-651).
   - The upgrade costs (155 + 185) - (71 + 60) = 340 - 131 = 209.
   - Gift card: bags first 280 -> 230 -> 21; reference 280 -> 71.
   - End states:
     - reference: bags 3/0, `payment_history` [161, 209];
     - bags first: bags 3/1, `payment_history` [161, 50, 209].
2. **Policy compliance of the bags-first path.** It is compliant under the write-time reading. No rule forbids it or changes its arguments.
   - Policy 7 asks only for listed details and an explicit yes before each update.
   - Policy 97 ("Do not add checked bags that the user does not need") is not touched: the user asks for 3 bags.
   - Policy 115-120 prices a cabin change by the fares only, and nothing re-prices bags afterwards.
   - Policy 122-124 forbids only removing bags or adding insurance.
   - Policy 130-131 needs one gift card or credit card from the profile.
   - Payment: gift_card_8190333 covers 50 and then 209. The replays raise no errors.
   - No rule tells the agent to put the upgrade first to save the fee. Policy 9 rules out unrequested recommendations.
3. **Does the scenario pin the order? No.**
   - `reason_for_call` in task 22: "change the passenger to yourself, upgrade it to economy class, and have 3 checked bags".
   - `task_instructions`: gift card preferred; birthday in the profile; reactive user; end the call if a change is impossible. Nothing fixes a sequence.
   - Task 17 lists the bags first and tells the user to "Mention all three things at once and in this order". That fixes the order in which the user mentions the changes, not the order in which the agent makes them.
   - In 22 the mention order (passenger, upgrade, bags) agrees with the reference on upgrade before bags. So the failing path needs the agent to make the bag change before the upgrade, against the mention order. The scenario still allows this.
4. **Is the write-time reading the only defensible one? No.**
   - An agent that adds the bags first can still compute nonfree from the final cabin (economy: 3 free, so nonfree 0). That path replays to the target, 37ea6df3 (variant V4).
   - So the row is conditional on the write-time reading, exactly like 17/2h.
   - The write-time reading is the more literal one:
     - the allowance attaches to each passenger by cabin (policy 91-94);
     - `update_reservation_baggages` computes no allowance: it stores the count the agent passes (`tools.py` 659-660) and charges only the increase in nonfree bags;
     - `update_reservation_flights` leaves the bag fields untouched;
     - `data_model.py` 242 defines `nonfree_baggages` as "Number of paid bags in reservation".
   - The final-cabin path passes through one state that the current cabin does not allow: 3 bags with 0 paid on a gold basic-economy reservation, whose allowance is 2.
   - A compliant variant that scores 0 therefore exists under a defensible reading, which is what `defect_if` asks for. The row holds, with the assumption stated.
5. **Double count: none found.**
   - In `results/review_batch_3.csv`, 22/4c is 0. Its note records this path and files it under 2h.
   - Convention 1 also puts it under 2h, as content that follows from WRITE order.
   - The other task-22 rows in batch 3 (1d, 2g, 2k, 4a, 4b, 4d, 4e) are all 0.
   - The agent-run rows of task 22 could not be checked within the limits.
6. **Severity: medium**, as `checklist.md` sets for 2h (convention 6). The path is real but less likely in 22 than in 17, for two reasons:
   - the mention order puts the upgrade before the bags;
   - the user discloses information only when asked.

   This is stated as a remark, not graded.
7. **Differences between 17 and 22: none justifies different labels.**
   - What is identical:
     - the user;
     - the reservation;
     - the reference WRITE list, with identical names and arguments;
     - the reference hash, 37ea6df3;
     - the variant hash, edc62003.
   - What differs:
     - the mention order: bags first in 17, last in 22;
     - "add 3" in 17 against "have 3" checked bags in 22;
     - a reactive user in 22, with an exit rule;
     - nl_assertion 3: "3 free baggages" in 22, "updated to 3" in 17.
   - These differences change only the likelihood of the path.
   - The 22 assertion shows that the author expected the bags to be free. Neither participant sees it, so it cannot fix the order for the agent.

## Replays

The script is `replay_22.py`, in a temporary folder outside the repository (subfolder `skeptic_consistency_22`).

- It runs from `tau2-bench/` as `uv run --no-sync python <script>`, with `PYTHONDONTWRITEBYTECODE=1`.
- Each replay builds a fresh environment through `registry.get_env_constructor('airline')`, then calls `set_state` with an empty history, `make_tool_call` with requestor `assistant`, and `get_db_hash`.
- The reference lists come from the registry task loader.
- The script writes no files.

Output, with the state lines shortened:

```
initial hash 124e39a6  | cabin=basic_economy bags=0/0 payments=[('gift_card_8190333', 161)] ... gift_card_8190333=280.0 gift_card_6490722=127.0
reference WRITE lists of 22 and 17 identical (names and arguments): True
R22  reference task 22 (flights, passengers, bags 3/0)          hash 37ea6df3 (TARGET)  bags=3/0 payments=[161, 209] gift_card_8190333=71.0
R17  reference task 17                                           hash 37ea6df3 (TARGET)
    at the bag call: membership=gold cabin=basic_economy passengers=1 free allowance=2 -> write-time nonfree for 3 bags = 1
V1  bags 3/1 (write-time) -> flights -> passengers               hash edc62003 (differs) bags=3/1 payments=[161, 50, 209] gift_card_8190333=21.0
V2  passengers -> bags 3/1 -> flights                            hash edc62003 (differs)
V3  bags 3/1 -> passengers -> flights  [task-17 mention order]   hash edc62003 (differs)
V4  bags 3/0 (final-cabin) -> flights -> passengers              hash 37ea6df3 (TARGET)
V5  passengers -> flights -> bags 3/0  [task-22 mention order]   hash 37ea6df3 (TARGET)
V6  bags 3/1 on gift_card_6490722 -> flights -> passengers       hash 7b890f40 (differs) gift_card_6490722=77.0
V7  bags 3/1 -> flights -> passengers -> bags 3/0 (repair)       hash c0f2ed4b (differs) bags=3/0 payments=[161, 50, 209]
V8  flights -> bags 3/1 -> passengers (fee after the upgrade)    hash 8a619964 (differs)
upgrade difference (340) - (131) = 209
```

None of the replays raised an error.

- The prefixes agree with `results/probe_2h_paths.csv` (row 22: edc62003 against 37ea6df3).
- They also agree with the 17/2h verdict in `results/skeptic_verdicts_rest_order.csv` (37ea6df3, edc62003, 7b890f40, c0f2ed4b).
- V8 is not a compliant path, because economy already gives 3 free bags. It is listed only to show that the hash also catches a fee charged after the upgrade.

## Inputs and deviations

- **Read:**
  - `airline_full/skeptic_brief.md`, `checklist.md`, `schema.md`;
  - the task-22 and task-17 entries of `tasks.json`; `db.json` (FQ8APE, omar_rossi_1241, HAT056/HAT138); `policy.md`;
  - `tools.py`;
  - the two probe scripts and their CSV files;
  - `results/review_batch_3.csv/.md` and `results/review_batch_6.csv/.md` (task 17 section);
  - `results/skeptic_verdicts_rest_order.csv` and `results/skeptic_report_rest_order.md`;
  - `results/review_overrides_consistency.csv`.
- **Not opened:** no file from the prohibited list.
- **Possible deviation 1, source files beyond `tools.py`.** Four more source files under `tau2-bench/` were read, all as primary sources:
  - `src/tau2/evaluator/evaluator_env.py`: the hash comparison;
  - `src/tau2/domains/airline/data_model.py`: the field descriptions;
  - `src/tau2/user/guidelines.py`: progressive disclosure;
  - `src/tau2/data_model/tasks.py`: what the user simulator receives.
- **Possible deviation 2, file names listed.** A read-only `find` for files modified today, run before the replay, listed file names under `tau2-bench/data/simulations/`. None of them was opened.
- **Integrity of the clone.** After the replay, `find -newer <script>` over `tau2-bench/` (excluding `.git`) listed no file, and `uv.lock` keeps its 2026-10-27 07:23 timestamp.
- No git command, install, network access, or model or API call was made. No existing file was modified.
