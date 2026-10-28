# Task 32 — pre-test of the text fix (counterfactual simulator probe), result

Design and rules: `scripts/v2/probe_32_v2.py` docstring (fixed before any call). Two independent classifications per arm: `*_classification_a.csv` (first model reader) and `*_classification_b.csv` (blind second reader, Opus, saw only the samples). Simulator: claude-haiku-5-5, persona as in the recorded run, prefix = 32_haiku_t0 up to the user's two-step request.

| task text | arm | ACCEPT | REFUSE | UNCLEAR | agreement a/b | rule | verdict |
|---|---|---|---|---|---|---|---|
| v1 (block 1, `results/probe_32/`) | two_step | 0 | 10 | 0 | 10/10 | REFUSE ≥ 8 → scenario blocks the reference | blocked (1e defect) |
| v2 | two_step | 10 | 0 | 0 | 10/10 | ACCEPT ≥ 8 → fix works | works |
| v2 | step1_only | 8 | 1 | 1 | 10/10 | ACCEPT ≥ 8 → clause over-corrects | over-corrects: the simulator accepts +$396 with no refund stated, reasoning from its own knowledge of step 2 |
| v2.1 (tightened) | two_step | 8 | 0 | 2 | 10/10 | ACCEPT ≥ 8 → fix works | works (at the threshold: 2 replies defer until the agent "confirms" the net the agent had already stated) |
| v2.1 | step1_only | 0 | 10 | 0 | 10/10 | REFUSE ≥ 8 → clause behaves as intended | behaves |

Decision: `block2/tasks_airline_v2.json` carries the v2.1 wording for task 32. Cost of the four arms ≈ $0.022 (own estimate).

Limits: one prefix, one wording per arm, Haiku simulator only; the v2.1 two-step result sits exactly on the pre-set threshold, so a fresh GT run may still see the simulator ask for a restatement before authorising (counted under H4 as a mechanism outcome, not as a text defect).
