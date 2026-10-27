# Offline re-score of the recorded block-1 simulations (scorer v2)

Inputs: sample20_pass3_haiku.results.json, sample20_gt_haiku.results.json (76 simulations). Replay gate: 76/76.
Judge: anthropic/claude-haiku-5-5, 3 votes per assertion, 252 calls this run, 1,470,129 in / 209,147 out tokens, own cost estimate $0.252 ($0.1/0.5 per MTok). Cached verdicts reused from judge_cache.json cost nothing.

## Pass counts per configuration

| config | tasks | switches | haiku (60 sims) | haiku tasks 3/3 | gt (16 sims) | all 76 |
|---|---|---|---|---|---|---|
| v1 | t1 | stock | 44/60 | 12/20 | 11/16 | 55/76 |
| S_hash | t1 | hash | 44/60 | 12/20 | 11/16 | 55/76 |
| S_comm | t1 | comm | 44/60 | 12/20 | 11/16 | 55/76 |
| S_nl | t1 | nl | 42/60 | 11/20 | 11/16 | 53/76 |
| S_all_t1 | t1 | hash+comm+nl | 42/60 | 11/20 | 11/16 | 53/76 |
| T2_stock | t2 | stock | 45/60 | 12/20 | 11/16 | 56/76 |
| V2 | t2 | hash+comm+nl | 43/60 | 11/20 | 11/16 | 54/76 |

## Flips per simulation, v1 -> V2

| agent | task | direction | sims |
|---|---|---|---|
| haiku | 7 | 0->1 | 1 |
| haiku | 9 | 1->0 | 2 |

## DB failures under v1 that are order-only

0 of 20 v1 DB mismatches disappear under canonicalisation: 

Gold-action replay errors: 0 simulations

## Judge agreement

255/255 assertion verdicts unanimous across 3 votes (this run's calls only; cached pairs not re-voted).
