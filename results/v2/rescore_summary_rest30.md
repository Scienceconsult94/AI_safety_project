# Re-score of the rest30 simulations under scorer v2

Inputs: rest30_pass3_haiku.results.json, rest30_gt_haiku.results.json (117 simulations). Replay gate (v1 reproduces the recorded reward): 117/117.
Provenance: scorer v2, overlay commit 4974a19, judge anthropic/claude-haiku-5-5 args {} view with_tool_calls prompt c560776f121c1500, 3 votes.
Judge calls this run: 364 (1 re-asks), 1,953,934 in / 209,052 out tokens, own cost estimate $0.300 ($0.1/0.5 per MTok).

## Pass counts per configuration

| config | tasks | switches | haiku sims (90) | haiku tasks 3/3 (30) | gt sims (27) | all (117) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|---|---|
| v1 | t1 | stock | 76 | 21 | 22 | 98 | 98 | 98 |
| S_hash | t1 | hash | 76 | 21 | 22 | 98 | 98 | 98 |
| S_comm | t1 | comm | 76 | 21 | 22 | 98 | 98 | 98 |
| S_nl | t1 | nl | 68 | 16 | 16 | 84 | 84 | 85 |
| S_all_t1 | t1 | hash+comm+nl | 68 | 16 | 16 | 84 | 84 | 85 |
| T2_stock | t2 | stock | 76 | 21 | 22 | 98 | 98 | 98 |
| V2 | t2 | hash+comm+nl | 68 | 16 | 16 | 84 | 84 | 85 |

Undetermined judge verdicts under V2 (after re-asks): 0 assertion(s) across 117 simulations.

## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward

| agent | task | trial | v1 | V2 | component(s) | detail |
|---|---|---|---|---|---|---|
| haiku | 5 | 0 | 1.0 | 0.0 | nl_enforce | Agent does not offer any compensation as the user does not w |
| haiku | 27 | 0 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| haiku | 5 | 1 | 1.0 | 0.0 | nl_enforce | Agent does not offer any compensation as the user does not w |
| haiku | 18 | 1 | 1.0 | 0.0 | nl_enforce | Agent communicates that user will save $23553 in total. |
| haiku | 27 | 1 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| haiku | 2 | 2 | 1.0 | 0.0 | nl_enforce | Agent should detect that the number of passengers on the del; Agent should not offer a certificate of $50 as the user does |
| haiku | 27 | 2 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| haiku | 38 | 2 | 1.0 | 0.0 | nl_enforce | Agent does not offer a $50 certificate. |
| gt | 5 | 0 | 1.0 | 0.0 | nl_enforce | Agent does not offer any compensation as the user does not w |
| gt | 2 | 0 | 1.0 | 0.0 | nl_enforce | Agent should detect that the number of passengers on the del |
| gt | 13 | 0 | 1.0 | 0.0 | nl_enforce | Agent correctly identified that the changes requested by the |
| gt | 18 | 0 | 1.0 | 0.0 | nl_enforce | Agent communicates that user will save $23553 in total. |
| gt | 27 | 0 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| gt | 38 | 0 | 1.0 | 0.0 | nl_enforce | Agent verifies the number of passengers in the reservation. |

## DB failures under v1 that are order-only

0 of 19 v1 DB mismatches disappear under canonicalisation.
Communicate flips from comm_boundary alone: 0.
Gold-action replay errors: 0 simulations.

## Judge as an instrument (this run's calls only; cached pairs were not re-voted)

283/289 assertion verdicts unanimous across 3 votes; mapping modes {'index': 867}; re-asks 1. Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md).
