# Re-score of the fresh simulations under scorer v2

Inputs: v2_sample20_pass3_haiku/results.json, v2_sample20_gt_haiku/results.json, v2_gt3_haiku/results.json (85 simulations). Replay gate (V2 reproduces the recorded reward): 85/85.
Provenance: scorer v2, overlay commit d55bd49, judge anthropic/claude-haiku-5-5 args {} view with_tool_calls prompt c560776f121c1500, 3 votes.
Judge calls this run: 49 (5 re-asks), 372,008 in / 57,019 out tokens, own cost estimate $0.066 ($0.1/0.5 per MTok).

## Pass counts per configuration

| config | tasks | switches | haiku sims (60) | haiku tasks 3/3 (20) | gt sims (25) | all (85) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|---|---|
| v1 | t1 | stock | 47 | 12 | 15 | 62 | 62 | 62 |
| S_hash | t1 | hash | 47 | 12 | 15 | 62 | 62 | 62 |
| S_comm | t1 | comm | 47 | 12 | 15 | 62 | 62 | 62 |
| S_nl | t1 | nl | 47 | 12 | 14 | 61 | 61 | 61 |
| S_all_t1 | t1 | hash+comm+nl | 47 | 12 | 14 | 61 | 61 | 61 |
| T2_stock | t2 | stock | 47 | 12 | 19 | 66 | 66 | 66 |
| V2 | t2 | hash+comm+nl | 47 | 12 | 19 | 66 | 66 | 66 |

Undetermined judge verdicts under V2 (after re-asks): 0 assertion(s) across 85 simulations.

## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward

| agent | task | trial | v1 | V2 | component(s) | detail |
|---|---|---|---|---|---|---|
| gt | 7 | 0 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |
| gt3 | 7 | 0 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |
| gt3 | 7 | 1 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |
| gt3 | 7 | 2 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |

## DB failures under v1 that are order-only

0 of 19 v1 DB mismatches disappear under canonicalisation.
Communicate flips from comm_boundary alone: 0.
Gold-action replay errors: 0 simulations.

## Judge as an instrument (this run's calls only; cached pairs were not re-voted)

70/76 assertion verdicts unanimous across 3 votes; mapping modes {'index': 224, 'missing': 4}; re-asks 5. Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md).
