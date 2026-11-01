# Discrepancies found overnight (added 2026-11-01)

Rule of the night: a published number is never edited; a result that contradicts one is written here and the task stops at that point.

## D1. `analysis.ipynb`: the committed cell output is older than the published numbers (T1)

Found by the fresh-clone check (`T1_repro.md`): the stored output of cell 3 in `analysis.ipynb` was executed on 2026-10-27 under the earlier headline definition. Re-running the notebook, as STRUCTURE.md says to, gives output equal to `summary_numbers.md` and README.

| row | committed notebook output shows | rebuild gives (= README, summary_numbers.md) |
|---|---|---|
| headline row | 18/20 = 0.900 | 16/20 = 0.800 |
| static and probe checks only | 13/20 = 0.650 | 12/20 = 0.600 |
| defects only from agent runs | 5/20 = 0.250 | 4/20 = 0.200 |
| Table 2, scoring validity | 12/20 = 0.600 | 11/20 = 0.550 |
| Table 2b, check 2h | 3 rows | 4 rows |

Two rows of the current output (14/20 and 15/20) are missing from the committed output. The published numbers are not in question: the rebuild reproduces them; the notebook's stored output is stale. Not touched tonight (a result file). Fix for the author: re-execute `analysis.ipynb` in the Python 3.11 environment and commit it, so a reader opening the notebook on GitHub sees 16/20 and 12/20, not 18/20 and 13/20.

## Not a discrepancy, recorded for completeness

- Rebuild run 1 of T1 corrupted `audit_log.csv` in the clone because the printed command sequence skipped a copy step; that was a documentation defect, fixed in STRUCTURE.md tonight (see LOG.md), not a difference in any number.
- `fig_defects.png` and the notebook figures differ only in font rendering under matplotlib 3.11 (the analysis packages are unpinned).
