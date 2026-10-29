# retail: reject address and payment changes once an order's items were modified

Status: draft, not opened. Patch: `patches/I12.patch` (paths relative to the repository root; base tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Issue text: `issue_I12_modify_after_item_change.md`.

## Description

`policy.md` (line 110) says that after the items of a pending order are modified, "The agent will not be able to modify or cancel the order anymore", and line 96 allows modifications only in status `pending`. `modify_pending_order_items` sets the status to `pending (item modified)`, and `cancel_pending_order` and `modify_pending_order_items` already require the exact status `pending`. `modify_pending_order_address` and `modify_pending_order_payment` used `_is_pending_order`, a substring test, so they accepted `pending (item modified)`: an address change after an item change succeeded, and a payment change was rejected only by the unrelated one-payment check.

Changes:

- `src/tau2/domains/retail/tools.py`: `_is_pending_order` returns `order.status == "pending"`; its docstring says why. Only the address and the payment tool call it. Both now reject such an order with their existing message, "Non-pending order cannot be modified".
- `tests/test_domains/test_retail/test_modify_after_item_change.py` (new): an address change before the item change is accepted; an address change and a payment change after it are rejected and leave the DB hash unchanged.

The old docstring said the substring test was deliberate ("This is not a strict check"). If the tool behaviour is the intended one, the alternative fix is to change `policy.md` instead; this patch follows the policy, which is what the agent is told and what several scenarios test.

## Testing done

- `git apply --check` against `v2.0.0`: clean.
- On a copy of `v2.0.0` with the patch applied (pytest 9.0.2, CPython 3.12.16):
  - `tests/test_domains/test_retail/`: 22 passed (19 existing, 3 new). On unpatched `v2.0.0`, 2 of the 3 new tests fail (the two post-item-change cases); the "before" case passes on both.
  - Together with the other four patches of this audit: 160 passed, 6 skipped (see `pr_I11.md` for the file list).
- Reproduction script of the issue (`repro/I12.py`) on the patched copy:

```text
task 41, reference order ['41_0', '41_1', '41_2', '41_3', '41_4', '41_5', '41_6', '41_7', '41_8', '41_9']: db_reward = 1.0
task 41, address moved after the item change ['41_0', '41_1', '41_2', '41_3', '41_4', '41_6', '41_7', '41_8', '41_9', '41_5']: order status before the address call = 'pending (item modified)'; address call error = True; db_reward = 0.0
after the item change, modify_pending_order_payment: Error: Non-pending order cannot be modified
after the item change, cancel_pending_order: Error: Non-pending order cannot be cancelled
```

- All 14 retail tasks whose reference changes an order's address and later its items (41, 42, 71, 72, 78, 96, 97, 101, 102, 103, 104, 109, 111, 112): with the address change moved after the item change, the replay reached the target hash without error in 14 of 14 before the patch; after it, the moved call is rejected in 14 of 14 (after-patch output not saved in this repository).
- Gold (target) hashes of all 114 retail tasks before and after: 0 changed (output not saved in this repository). No reference in `tasks.json`, `multilingual/en/retail_tasks_en.json` or the five regional retail files modifies, pays for or cancels an order after modifying its items.

## Risk

- Agents that change an address or payment method after an item change now get a tool error. That is the policy's intent; trajectories that did so and passed before now fail the DB check, so published retail numbers can move slightly where agents broke this rule.
- No target hash changes, so references and correct trajectories are unaffected.
- The policy text names the status `pending (items modifed)` while the tool stores `pending (item modified)`; this patch does not touch `policy.md`, because the policy is part of the agent prompt.
