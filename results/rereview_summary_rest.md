# Blind re-review of 3 rest tasks (33, 35, 39; random.Random(20261028))

Labels compared on `defect` (0/1) per (task, check). The blind pass saw task cards, the static scan and probe outputs,
the policy and tool code, checklist.md and the review brief (with the block-1 defect rows of batches 2-4 as style
examples); none of batches 8 and 9, the audit log, skeptic or summary files. Corrected labels = after the adversarial
review of the rest rows (review_overrides_rest_*.csv; equal to the original labels where none exists).

| comparison | agreement | Cohen's kappa |
|---|---|---|
| blind vs original reviewer labels | 23/26 = 0.885 | 0.361 |
| blind vs skeptic-corrected labels | 26/26 = 1.000 | 1.000 |

Disagreements vs corrected labels (0):
