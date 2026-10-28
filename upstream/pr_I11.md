# retail: store each item's own new variant in `modify_pending_order_items`; round the price difference to cents

Status: draft, not opened. Patch: `patches/I11.patch` (paths relative to the repository root; base tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Issue text: `issue_I11_modify_items_last_variant.md`.

## Description

`modify_pending_order_items` validates each (old, new) pair in one loop and rewrites the items in a second loop, but the second loop reads the variable `variant` left over from the first, i.e. the last new variant. With two or more pairs, every modified item was stored with the last variant's price and options, and the target hash of tasks that modify several items in one call depended on the order of the pairs. The price difference was also stored unrounded, unlike in `exchange_delivered_order_items`.

Changes:

- `src/tau2/domains/retail/tools.py`: the validation loop keeps the variant looked up for each pair (`new_variants`), and the rewrite loop uses it; `diff_price` is rounded to cents after the validation loop, before the gift-card check and the payment record, as in `exchange_delivered_order_items`.
- `tests/test_domains/test_retail/test_modify_pending_order_items_variants.py` (new): each item stores its own variant; the stored difference is in cents; the order of the pairs does not change the DB hash.

## Testing done

- `git apply --check` against `v2.0.0`: clean.
- On a copy of `v2.0.0` with the patch applied (pytest 9.0.2, CPython 3.12.16):
  - `tests/test_domains/test_retail/`: 22 passed (19 existing, 3 new). The 3 new tests fail on unpatched `v2.0.0`.
  - Together with the other four patches of this audit applied to one copy: `tests/test_domains/test_retail/`, `tests/test_evaluator/`, `tests/test_runner/test_elicitation_integration.py`, `tests/test_orchestrator.py`, `tests/test_evaluate_trajectories.py` and the new tests: 160 passed, 6 skipped; the same existing files on unpatched `v2.0.0`: 141 passed, 6 skipped.
- Reproduction script of the issue (`repro/I11.py`) on the patched copy:

```text
task 20, reference call 20_8: 4 (old, new) pairs
  item 4579334072 (Water Bottle): stored price 54.85, variant price 54.85; stored options == variant options: True
  item 1151293680 (Mechanical Keyboard): stored price 272.33, variant price 272.33; stored options == variant options: True
  item 4107812777 (Running Shoes): stored price 155.33, variant price 155.33; stored options == variant options: True
  item 2882812427 (Makeup Kit): stored price 261.11, variant price 261.11; stored options == variant options: True
  payment_history[-1]: payment 71.96
task 20, reference trajectory: db_reward = 1.0
task 20, same pairs in reverse order inside the call: db_reward = 1.0
task 15, payment_history[-1]: refund 0.35
```

- All 114 retail references replayed before and after: reference actions that raise, 18 before and 18 after; items stored with another variant's data, 9 before and 0 after; pair orders that change the target hash, 18/23, 1/1, 4/5, 4/5, 1/1 (tasks 20, 21, 36, 37, 100) before and 0 in every task after.

## Risk

- The target hash changes for 35 of the 114 retail tasks: 5 through the variant fix (20, 21, 36, 37, 100) and the others because stored differences are now rounded. Within one code version the gold and the predicted state are produced by the same tool, so a trajectory's pass or fail changes only where the order of the pairs mattered (a correct solution that used another order now passes). Published retail numbers stay comparable except on those 5 tasks.
- Re-grading old `results.json` files with strict replay (`strict=True`) would raise on recorded tool outputs that contain the old prices or unrounded amounts; `tau2 evaluate-trajs` uses `strict_replay=False`, which only logs a warning.
- The multilingual retail task sets use the same tool; their references with multi-item calls (tasks 21 and 36 in each set) change in the same way.
- The two hunks (variant, rounding) are independent and can be split if the maintainers prefer to land only the variant fix.
