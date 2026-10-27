# Re-score of the recorded simulations under scorer v2

Inputs: sample20_pass3_haiku.results.json, sample20_gt_haiku.results.json (76 simulations). Replay gate (v1 reproduces the recorded reward): 76/76.
Provenance: scorer v2, overlay commit 5f4d92a, judge anthropic/claude-haiku-5-5 args {} view with_tool_calls prompt c560776f121c1500, 3 votes.
Judge calls this run: 281 (20 re-asks), 1,810,883 in / 191,762 out tokens, own cost estimate $0.277 ($0.1/0.5 per MTok).

## Pass counts per configuration

| config | tasks | switches | haiku sims (60) | haiku tasks 3/3 (20) | gt sims (16) | all (76) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|---|---|
| v1 | t1 | stock | 44 | 12 | 11 | 55 | 55 | 55 |
| S_hash | t1 | hash | 44 | 12 | 11 | 55 | 55 | 55 |
| S_comm | t1 | comm | 44 | 12 | 11 | 55 | 55 | 55 |
| S_nl | t1 | nl | 43 | 11 | 11 | 54 | 54 | 55 |
| S_all_t1 | t1 | hash+comm+nl | 43 | 11 | 11 | 54 | 54 | 55 |
| T2_stock | t2 | stock | 45 | 12 | 11 | 56 | 56 | 56 |
| V2 | t2 | hash+comm+nl | 44 | 11 | 11 | 55 | 55 | 56 |

Undetermined judge verdicts under V2 (after re-asks): 0 assertion(s) across 76 simulations.

## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward

| agent | task | trial | v1 | V2 | component(s) | detail |
|---|---|---|---|---|---|---|
| haiku | 9 | 0 | 1.0 | 0.0 | nl_enforce | Check that Agent searched for direct flights between JFK and |
| haiku | 7 | 0 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |

## DB failures under v1 that are order-only

0 of 20 v1 DB mismatches disappear under canonicalisation.
Communicate flips from comm_boundary alone: 0.
Gold-action replay errors: 0 simulations.

## Judge as an instrument (this run's calls only; cached pairs were not re-voted)

262/271 assertion verdicts unanimous across 3 votes; mapping modes {'index': 805, 'missing': 8}; re-asks 20. Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md).
