# Retail static review, batch 9 (tasks 80–89)

Checks decided per task: 1d, 2k, 2m, 4a, 4b, 4c, 4d, 4e; plus 2e for 86 and 87 (probe_2d rows with `check=2e`). No task in the batch has a 1b/1c flag (`replay_errors` = 0, `write_noop_ids` empty), no 2h flag (`n_hash_differs` = 0 for 81, 86, 87) and no 2d row with `hash_equals_gold` = 1. Result: 82 rows, 0 defects; one row (86 / 4c) carries an "uncertain" note.

**80.** Exchange the blue/S/polyester/v-neck T-Shirt in #W7209932 for the red/XXL/cotton/crew neck one, paid with the gift card. Difference 46.85 − 54.84 = −7.99 (refund to the gift card). Only one variant matches (9354168549, available); the gift card is the user's only payment method; order delivered. 1d, 2k, 2m, 4a–4e: 0. No `communicate_info`, no assertions.

**81.** No longer needs boots, watch, keyboard, charger, jacket, running shoes; cancel whole orders if partial cancel is impossible. The first three are all of #W3289292; the other three are in #W9722559 with an unnamed Luggage Set, which the whole-order fallback covers. Both orders pending, reason "no longer needed" stated. Refunds: 2468.70 and 943.83, the same as the order payments. All checks 0.

**82.** Two tablets in two delivered orders; return the dearer one (6065192424, 989.70, #W9571698) to credit card, otherwise return the whole order to the gift card. #W9571698 was paid by gift card, so a credit-card refund breaks policy l.124 (probe_2d: ValueError). The reference takes the fallback and returns all 4 items, 2850.32 + 260.19 + 193.22 + 989.70 = 4293.43, the same as the order payment. All checks 0.

**83.** Same set-up as 82, but the fallback only switches the refund to the gift card. The reference returns 6065192424 (989.70) to gift_card_7250692. All checks 0.

**84.** The user first asks to return the cheaper tablet (8551474201, 938.92, #W3069600, credit-card refund allowed), then at confirmation switches to the dearer one with a gift-card refund. The reference follows the final request (same target hash as 83). 2m: 0. The task tests the confirmation step, but a write made before confirmation would mark #W3069600 as returned and change the hash, so the DB records it. Other checks 0.

**85.** "Exchange" the Fleece Jacket for large/red/half zipper. #W2466703 is pending, so the policy route is item modification (l.96, l.112). The reference changes 9385662952 to 8733974883; difference 153.18 − 159.92 = −6.74, refunded to PayPal, the only payment method. One variant matches. All checks 0.

**86.** Jacket to red + half zipper, and default address to the Washington DC address from one of the orders (#W1994898, the only DC address). Same jacket write as 85 plus modify_user_address. 4c: 0, uncertain. No size is stated, and two available variants are red + half zipper: L 8733974883 (reference) and S 5992316252 (probe_2d: different hash). Keeping L is the reading that changes only what was asked, but the user simulator is not told its current size. The user turns in the task-86 runs would settle it. 2e: 0. An earlier wrong default-address write is hidden by the end-state comparison (probe 86_1, hash equal to gold), but such a write is not a policy violation in itself. Other checks 0.

**87.** Move all pending orders (#W2166301, #W2466703, #W6832752) and the default address to the DC address from #W1994898 (processed). The reference matches with 3 order-address writes plus 1 user-address write, all to orders that are pending. 2e: 0. Probe rows 87_0–87_3 all keep the gold hash after a wrong address is written first, so the end-state comparison hides those writes, but none is a policy-violating write in itself. Other checks 0.

**88.** Change the glass/white Bookshelf to 4 ft; if that is unavailable, cancel the whole order ("ordered by mistake"). In db.json, glass/white/4 ft (7373893106) has available = false; the card does not list the Bookshelf variants. So the cancel of pending #W8835847 is correct. Refund 46.85 + 138.47 + 504.65 = 689.97, the same as the order payment. All checks 0.

**89.** Ask for the cheapest available mechanical keyboard; exchange if it costs under $200, otherwise return the current one. The cheapest of the 13 available variants is 3616838507 at 226.11 (tactile, white, full size), so the return branch applies. The reference returns 9690244451 to PayPal, the original and only payment method. 4e: 0. All 4 assertions ($226.11, tactile, white, full) match the variant. 2k: 0. Every `communicate_info` string is covered by an assertion. Other checks 0.
