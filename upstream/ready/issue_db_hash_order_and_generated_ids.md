Filed 2026-11-01 as [#736](https://github.com/sierra-research/tau2-bench/issues/736) (the paste-ready text below, title = its first heading).

Status: partly covered by #514, so do not file the payment-method-order part: #514 shows that `get_dict_hash` keeps list order, using airline `payment_history`. The passenger-order and generated-reservation-id parts still reproduce at da0835f6c67baef58bdda18f2a3b037dfb3a1754 (by reading the code; not run)

Source draft: `upstream/issue_I3_db_hash_order_and_generated_ids.md`. Upstream `main` read at `da0835f6c67baef58bdda18f2a3b037dfb3a1754` (2026-10-29 22:37 -0700, merge of #692), shallow clone in `<fresh-folder>\upstream_main`.

Tracker checked on 2026-10-31: `https://api.github.com/repos/sierra-research/tau2-bench/issues?state=all&per_page=100`, pages 1-8 (page 9 empty). 706 items, numbers #1-#711 (#133, #134, #146, #324, #561 not returned), 202 issues and 504 pull requests. Every title read; bodies read where the title was close.

Items on the same or a nearby problem:

- #514 (issue, open): same mechanism. Lists keep their order under `sort_keys=True`, shown with `payment_history` in airline task 14 (task 23 is named as a second failure "modulo list order", without the list). Nothing on `passengers` or on generated reservation ids. Its scoped fix (sort `payment_history` by `payment_id`, or a per-domain allowlist of order-free fields) does not touch ids.
- #518 (PR, open): a leaderboard submission that points to #514. Nothing new.
- #325 (issue, open): retail `modify_pending_order_items`, order of the (old, new) pairs. Same family, different tool (audit id I11).
- #557 (issue) and #570 (PR), both open: order sensitivity of the ACTION check on list arguments. A different check (action match, not the DB hash).
- #148 (PR, open): telecom bill ids made deterministic instead of random UUIDs. These are generated ids too, but in telecom and caused by randomness, not by call order.
- #711 (issue, open): telecom DB match is broken by float formatting and a stale gold user DB. Different fields.
- #397 (PR, merged), #633 (issue) and #634 (PR): banking_knowledge canonicalization of int vs float and of timestamps. Different domain and fields.
- #609 (PR, open): grades the DB check against the live environment instead of the replay. A different mechanism.
- Not the same: #15, #384, #646 (airline or retail reward validity, not list order); #654 (caching the gold DB); #671 (Windows line endings and frozen subset hashes).

Code check at HEAD. Every file below is byte-identical to `v2.0.0`; `src/tau2/domains/airline/` and `data/tau2/domains/airline/` are identical too.

- Hash: `src/tau2/utils/utils.py` lines 36-42 (`get_dict_hash`: `json.dumps(obj, sort_keys=True, default=str)`, then SHA-256). Still exists.
- Call chain: `src/tau2/evaluator/evaluator_env.py` lines 117-129, then `src/tau2/environment/environment.py` lines 275-282, then `src/tau2/environment/toolkit.py` lines 242-244 (`get_dict_hash(self.db.model_dump())`). The draft's `DB.get_hash` path (`src/tau2/environment/db.py` lines 28-30, `src/tau2/utils/pydantic_utils.py` lines 15-21) is unchanged and ends in the same function.
- Generated ids: `src/tau2/domains/airline/tools.py` lines 131-144 (`_get_new_reservation_id`, the fixed sequence `HATHAT`, `HATHAU`, `HATHAV`), called at line 292. Still exists.
- List order: same file, lines 302-303 (`passengers` and `payment_history` stored with `deepcopy` in call order). Still exists.
- Docs: `docs/evaluation.md` lines 18-20 ("any sequence of tool calls that produces an equivalent DB end state passes the DB check"). Unchanged.

---

## DB check: passenger order and generated reservation ids also change the DB hash (follow-up to #514)

**Versions.** Reproduced at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Checked by reading the code at `main` `da0835f6c67baef58bdda18f2a3b037dfb3a1754`: the files below and the airline data are unchanged.

**What happens.** #514 shows, with `payment_history`, that `get_dict_hash` (`src/tau2/utils/utils.py` lines 36-42) keeps list order in the DB hash. The fix scoped there misses two more airline cases:

1. `book_reservation` stores `passengers` in call order (`src/tau2/domains/airline/tools.py` line 302). Task 8 with the two passengers of action `8_3` swapped gets DB reward 0.0. Neither the scenario nor the policy orders them.
2. `_get_new_reservation_id` (same file, lines 131-144) hands out `HATHAT`, `HATHAU`, `HATHAV` in call order. Task 23 with its three bookings in another order gets 0.0, because the ids follow the order. Neither the scenario nor the policy fixes that order.

`docs/evaluation.md` (lines 18-20) says any sequence of tool calls that reaches an equivalent DB end state passes. On the 13 airline tasks with two or more WRITE calls, reordering those calls changed the hash in 24 of 78 orders. In 20 of the 24 (all task 23), only the generated ids differed. In 76 recorded conversations, no DB mismatch was due to order alone.

**Reproduction** (no model call), from a tau2-bench root:

```text
PYTHONUTF8=1 uv run --no-sync python <audit repo>/upstream/repro/I3.py
```

Script: `upstream/repro/I3.py` in https://github.com/Scienceconsult94/AI_safety_project. Output at `v2.0.0`, tasks 8 and 23 only (task 20 shows the payment-method order that #514 already covers; #514's own example is task 14):

```text
task 8 reference: db_reward = 1.0
task 8, the two passengers of 8_3 in the other order: db_reward = 0.0
task 23 reference (cancel, then book Mohamed, Raj, Liam): ids {'Mohamed': 'HATHAT', 'Raj': 'HATHAU', 'Liam': 'HATHAV'}; db_reward = 1.0
task 23, same three bookings in the order Liam, Raj, Mohamed: ids {'Liam': 'HATHAT', 'Raj': 'HATHAU', 'Mohamed': 'HATHAV'}; db_reward = 0.0
```

**Expected vs actual.** Expected: 1.0 whenever the scenario and the policy leave the order open. Actual: 0.0.

**Fix.** No patch. Suggested, for the DB check only: hash a canonical form. It sorts order-free lists by content (`passengers`, the user's `saved_passengers` and `reservations`, airline `payment_history`). It replaces ids created during the episode with content-derived ids and remaps the references. It rounds amounts to cents and keeps the `flights` order. The audit's overlay (`canonical_dump` in `scripts/v2/scorer_v2.py`) changed no reward on the 76 recorded conversations. It cut the order-dependent reorderings from 24/78 to 4, all real outcome changes.
