# Re-score of the sonnet simulations under scorer v2

Inputs: sample20_sonnet_t3.results.json (60 simulations). Replay gate (v1 reproduces the recorded reward): 60/60.
Provenance: scorer v2, overlay commit c470f5a, judge anthropic/claude-haiku-5-5 args {} view with_tool_calls prompt c560776f121c1500, 3 votes.
Judge calls this run: 209 (2 re-asks), 1,434,593 in / 143,639 out tokens, own cost estimate $0.215 ($0.1/0.5 per MTok).

## Pass counts per configuration

| config | tasks | switches | sonnet sims (60) | sonnet tasks 3/3 (20) | gt sims (0) | all (60) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|---|---|
| v1 | t1 | stock | 51 | 16 | 0 | 51 | 51 | 51 |
| S_hash | t1 | hash | 51 | 16 | 0 | 51 | 51 | 51 |
| S_comm | t1 | comm | 51 | 16 | 0 | 51 | 51 | 51 |
| S_nl | t1 | nl | 51 | 16 | 0 | 51 | 51 | 51 |
| S_all_t1 | t1 | hash+comm+nl | 51 | 16 | 0 | 51 | 51 | 51 |
| T2_stock | t2 | stock | 54 | 17 | 0 | 54 | 54 | 54 |
| V2 | t2 | hash+comm+nl | 53 | 16 | 0 | 53 | 53 | 54 |

Undetermined judge verdicts under V2 (after re-asks): 0 assertion(s) across 60 simulations.

## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward

| agent | task | trial | v1 | V2 | component(s) | detail |
|---|---|---|---|---|---|---|
| sonnet | 7 | 0 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |
| sonnet | 7 | 1 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |
| sonnet | 8 | 2 | 1.0 | 0.0 | interaction | Agent identifies reservation id as WUNA5K. |
| sonnet | 7 | 2 | 0.0 | 1.0 | criteria text (T2_stock) | by construction: communicate_info 1628 -> 708;  |

## DB failures under v1 that are order-only

0 of 6 v1 DB mismatches disappear under canonicalisation.
Communicate flips from comm_boundary alone: 0.
Gold-action replay errors: 0 simulations.

## Judge as an instrument (this run's calls only; cached pairs were not re-voted)

202/207 assertion verdicts unanimous across 3 votes; mapping modes {'index': 621}; re-asks 2. Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md).
