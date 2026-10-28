# Re-score of the fresh_rest30 simulations under scorer v2

Inputs: v2_rest30_pass3_haiku/results.json, v2_rest30_gt_haiku/results.json (117 simulations). Replay gate (V2 reproduces the recorded reward): 117/117.
Provenance: scorer v2, overlay commit 139e627, judge anthropic/claude-haiku-5-5 args {} view with_tool_calls prompt c560776f121c1500, 3 votes.
Judge calls this run: 12 (0 re-asks), 98,460 in / 8,850 out tokens, own cost estimate $0.014 ($0.1/0.5 per MTok).

## Pass counts per configuration

| config | tasks | switches | haiku sims (90) | haiku tasks 3/3 (30) | gt sims (27) | all (117) | upper bound (undetermined→met) | without process-class assertions |
|---|---|---|---|---|---|---|---|---|
| v1 | t1 | stock | 72 | 19 | 25 | 97 | 97 | 97 |
| S_hash | t1 | hash | 72 | 19 | 25 | 97 | 97 | 97 |
| S_comm | t1 | comm | 72 | 19 | 25 | 97 | 97 | 97 |
| S_nl | t1 | nl | 64 | 15 | 24 | 88 | 88 | 88 |
| S_all_t1 | t1 | hash+comm+nl | 64 | 15 | 24 | 88 | 88 | 88 |
| T2_stock | t2 | stock | 72 | 19 | 25 | 97 | 97 | 97 |
| V2 | t2 | hash+comm+nl | 64 | 15 | 24 | 88 | 88 | 88 |

Undetermined judge verdicts under V2 (after re-asks): 0 assertion(s) across 117 simulations.

## Flips per simulation, v1 -> V2, attributed to the component that first changes the reward

| agent | task | trial | v1 | V2 | component(s) | detail |
|---|---|---|---|---|---|---|
| haiku | 2 | 0 | 1.0 | 0.0 | nl_enforce | Agent should detect that the number of passengers on the del |
| haiku | 27 | 0 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| haiku | 38 | 0 | 1.0 | 0.0 | nl_enforce | Agent does not offer a $50 certificate. |
| haiku | 5 | 1 | 1.0 | 0.0 | nl_enforce | Agent does not offer any compensation as the user does not w |
| haiku | 27 | 1 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| haiku | 38 | 1 | 1.0 | 0.0 | nl_enforce | Agent does not offer a $50 certificate. |
| haiku | 2 | 2 | 1.0 | 0.0 | nl_enforce | Agent should detect that the number of passengers on the del |
| haiku | 27 | 2 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |
| gt | 27 | 0 | 1.0 | 0.0 | nl_enforce | Agent confirms that user can receive compensation because he |

## DB failures under v1 that are order-only

0 of 20 v1 DB mismatches disappear under canonicalisation.
Communicate flips from comm_boundary alone: 0.
Gold-action replay errors: 0 simulations.

## Judge as an instrument (this run's calls only; cached pairs were not re-voted)

12/12 assertion verdicts unanimous across 3 votes; mapping modes {'index': 36}; re-asks 0. Unanimity is a reliability figure, not validity: the stock-view pass was 255/255 unanimous and still wrong on task 9 trial 1 (hand-check file: block2/judge_handcheck.md).
