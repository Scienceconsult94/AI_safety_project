# Blind re-review of 3 rest tasks (33, 35, 39; random.Random(20261028))

Labels compared on `defect` (0/1) per (task, check). The blind pass saw task cards, the static scan and probe outputs,
the policy and tool code, checklist.md and the review brief (with the block-1 defect rows of batches 2-4 as style
examples); none of batches 8 and 9, the audit log, skeptic or summary files. Corrected labels = after the adversarial
review of the rest rows (review_overrides_rest_*.csv; equal to the original labels where none exists).

| comparison | agreement | Cohen's kappa |
|---|---|---|
| blind vs original reviewer labels | 23/26 = 0.885 | 0.361 |
| blind vs skeptic-corrected labels | 23/26 = 0.885 | 0.361 |

Disagreements vs corrected labels (3):
- task 33 check 2h: corrected=0 blind=1 — blind note: each call is compliant (round trip IAH-SFO kept, economy, one gift card from the profile) and reason_for_call states the two changes as separate wants. Hash-neutral variants: write order (probe), bag payment method (cost
- task 33 check 2k: corrected=0 blind=1 — blind note: nl 1 (HAT072 2024-05-19, HAT278 2024-05-23) and nl 3 (2 free bags) are enforced by the hash; only the refusal in nl 2 is unchecked. A business write that drops a leg would succeed but changes the hash
- task 33 check 4c: corrected=0 blind=1 — blind note: the postpone reading is the dominant one and matches nl 1. Pinned: HAT072 (HAT180 departs 07:00), cabin economy, bags 2/0, bag payment (cost 0). The -186 refund destination is pinned only by 'original form of payment', a
