# Retail static review, batch 8 (tasks 70–79)

Checks decided: 1d, 2k, 2m, 4a–4e for all ten tasks; 2e for 71, 72, 78 (rows with `check=2e` in `probe_2d.csv`). No task is flagged for 1b/1c (`replay_errors`=0, `write_noop_ids` empty), 2h (`n_hash_differs`=0 in every `probe_2h.csv` row) or 2d (no `check=2d` row with `hash_equals_gold=1`). All name+zip and e-mail lookups below resolve to exactly one user in `db.json`.

**Shared finding (71, 72, 78).** `modify_pending_order_address` checks `_is_pending_order` ("pending" in status, `tools.py:164-170`, used at `:485`), so it accepts an order already set to `pending (item modified)` by `modify_pending_order_items` (`:585`). `policy.md:96` and `:110` forbid any further modification after an item modification. `probe_2h.csv` shows that the items-then-address order replays without error and gives the gold hash. So a trajectory that breaks the policy still scores 1.0 → 2e defect (medium). The end-state comparison also hides an earlier wrong address write (`probe_2d.csv` 2e rows, `hash_equals_gold=1`). Whether two address writes on one order break `policy.md:84` is uncertain, so that part is not counted.

## 70
The user exchanges a cycling helmet (S/red/low) for M + high ventilation, blue if more than one color fits, pays with the original method, and asks what the difference is. Available M/high variants are red 8573379326 and blue 9013366374, so blue gives exactly one. 219.88 − 197.33 = 22.55, which matches the assertion (4e=0). 1d=0: name+zip leads to the only helmet order, and there is one payment method. 2k=0: "22.55" is covered by the assertion. 2m=0. 4a=0, but `reason_for_call` contains a cut sentence ("You do not want the" followed by a double space). The visible text still fixes the reference; the missing constraint cannot be checked. 4b, 4c, 4d=0.

## 71
The user moves pending order #W5270061 from the son's DC address to the default Charlotte address, wants the backpack in medium/polyester (grey preferred) and the desk lamp in black, then at confirmation switches to PayPal and keeps only the backpack change. Only 5917587651 is medium/polyester and available; 212.79 − 201.95 = +10.84 on PayPal. 1d, 2k, 4a–4e=0. The four available black lamp variants do not matter, because the lamp is dropped. 2m=0: skipping confirmation would produce a gift-card, two-item write with a different hash, so the confirmation step leaves a trace. **2e=1 (medium)**: see the shared finding.

## 72
Near duplicate of 71: same user, same reference arguments, same gold hash. The only addition is "first mention the modification then the address". 1d, 2k, 4a–4e=0. **2m=1 (medium)**: the scenario sets up the policy's ordering requirement (the address must come before the items, because modify items locks the order). Yet both orders give the same DB state (`probe_2h` 72) and `nl_assertions` is null, so the scorer cannot see whether the agent followed it. **2e=1 (medium)**: shared finding. Both rows have the same root cause.

## 73
The user returns everything in the only order except the "coffee machine", which is the Espresso Machine 7441167885. The reference returns the other four items to the original credit card, the only payment method. All checks 0. 4d note: "coffee machine" is an informal name for the only coffee appliance in the order, not a contradiction.

## 74
Two requests: change the pending laptop order to an i9 (256GB SSD preferred, silver preferred), and cancel the pending five-item order as no longer needed. The available i9 variants are 2913673670 (512GB/black) and 3265035808 (256GB/silver), so 3265035808. 2530.72 − 2749.56 = −218.84, refunded to the credit card. The only pending five-item order is #W3189752. 4a=0: the user says "exchange", but the order is pending, so a modification is correct. 4b, 4d, 4e, 2k, 2m=0. 1d=0, uncertain: the payment choice ("use your credit card") appears only in `unknown_info`. The literal rule does not count that field as stated, but the user prompt includes it as an instruction. The recorded user turns would settle this. 4c=0 under the same reading; without that instruction, three payment methods would fit the refund.

## 75
The user exchanges earbuds blue/8 hours/IPX4 for black/4 hours/not resistant (4063058357, available) in delivered order #W6908222. 243.34 − 226.49 = +16.85 on the only payment method (PayPal). All checks 0.

## 76
The fleece jacket cannot be removed on its own, so the reference cancels #W8367380 as "ordered by mistake". The skateboard variant maple/34 inch/graphic (2343503231) is unavailable in `db.json`, so the reference cancels #W1242543 as "no longer needed". The user also asks for the total of all grills: 985.66 + 953.39 = 1939.05 (#W8668939), which matches the assertion (4e=0). 2k=0: "1939.05" is covered by the assertion; the scan's `comm_covered_by_nl=0` comes only from the thousands separator. 1d, 2m, 4a–4d=0.

## 77
The user wants the largest available size of the delivered perfume (woody/30ml/men), by exchange. Woody/100ml/men 3399869890 is available, and the oriental 100ml is a different scent, not "it". 312.04 − 322.52 = −10.48, refunded to PayPal, the only payment method. All checks 0.

## 78
Three requests: set the address of #W5056519 to the address of #W8277957 (380 Maple Drive, Suite 960, San Diego, CA 92101), change the Makeup Kit to dark/Brand A, and cancel #W5995614 as ordered by mistake. Only one dark/Brand A variant is available, 1573035764 (professional). 253.98 − 243.62 = +10.36 on the only credit card. 1d, 2k, 2m, 4a–4e=0. The default-address substitution changes the hash (`probe_2d` 78_0). **2e=1 (medium)**: shared finding.

## 79
The user changes the 500ml bottle in pending #W8661412 to a 1000ml bottle. The exact other bottle (1000ml/glass/red) is unavailable, so the same color with any material gives 2439754078 (stainless steel/red), the only match. 49.51 − 52.79 = −3.28, refunded to the only credit card. All checks 0.
