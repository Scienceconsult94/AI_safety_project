# Retail agent runs (claude-haiku-5-5 agent and user; stock scorer, NL judge claude-haiku-5-5 in the loop)

pass3 dir: `retail_pass3_haiku`; gt dir: `retail_gt_haiku`; infrastructure_error simulations: 0

| task | n_write | nl | pass3 rewards | haiku_pass | judge-only fails | terminations | gt_eligible | gt reward | gt db_match | gt nl unmet |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 0 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 1 | 1 | 0 | 0 0 1 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 2 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 3 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 4 | 2 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 6 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 7 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 8 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 10 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 11 | 2 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 13 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 14 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 15 | 1 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 16 | 3 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 19 | 1 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | True | 1 |
| 20 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 21 | 1 | 1 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 22 | 3 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 23 | 3 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 24 | 0 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 25 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 28 | 3 | 1 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 29 | 2 | 1 | 0 0 1 | 1/3 | 2 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 30 | 3 | 0 | 1 0 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 31 | 2 | 0 | 0 0 1 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 34 | 1 | 0 | 1 0 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 35 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 37 | 1 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 41 | 4 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 43 | 1 | 3 | 1 0 0 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 44 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 46 | 1 | 2 | 0 1 0 | 1/3 | 2 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 1 |
| 47 | 1 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 48 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 50 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 52 | 1 | 0 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 54 | 3 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 57 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 58 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 59 | 2 | 2 | 1 0 0 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 63 | 1 | 3 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 66 | 1 | 0 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 67 | 0 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 69 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 72 | 2 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 73 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 75 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 76 | 2 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 78 | 3 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 80 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 81 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 82 | 1 | 0 | 0 1 0 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 83 | 1 | 0 | 0 0 1 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 84 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 85 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 87 | 4 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 88 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 89 | 1 | 4 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 91 | 2 | 0 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 92 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 93 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 95 | 2 | 3 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 96 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 98 | 3 | 0 | 1 0 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 99 | 2 | 0 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 103 | 4 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | True | 1 |
| 104 | 5 | 1 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 105 | 1 | 1 | 0 0 0 | 0/3 | 3 | user_stop, user_stop, user_stop | 1 | 0.0 | True | 1 |
| 106 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 107 | 2 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 109 | 3 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 110 | 3 | 3 | 1 0 0 | 1/3 | 2 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 112 | 3 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 113 | 2 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 5 | 1 | 0 | 1 0 0 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 9 | 1 | 0 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 12 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 17 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 18 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 26 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 27 | 1 | 0 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 32 | 3 | 0 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 33 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 36 | 1 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 38 | 1 | 2 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 39 | 1 | 1 | 0 0 1 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 40 | 1 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 42 | 4 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 45 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 49 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 51 | 1 | 0 | 1 0 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 53 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 55 | 4 | 0 | 1 1 0 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 56 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 60 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 61 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 62 | 0 | 2 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 64 | 2 | 0 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 65 | 0 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 68 | 0 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 70 | 1 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 71 | 2 | 0 | 0 0 1 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 74 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 77 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 79 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 86 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 90 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 94 | 1 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 97 | 2 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 100 | 2 | 0 | 0 0 0 | 0/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 101 | 3 | 0 | 1 0 0 | 1/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 0 |
| 102 | 3 | 0 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |
| 108 | 1 | 1 | 0 1 1 | 2/3 | 0 | user_stop, user_stop, user_stop | 1 | 0.0 | False | 1 |
| 111 | 3 | 1 | 1 1 1 | 3/3 | 0 | user_stop, user_stop, user_stop | 1 | 1.0 | True | 0 |

- pass^1 = 0.807 (n=114 tasks)
- pass^2 = 0.713 (n=114 tasks)
- pass^3 = 0.658 (n=114 tasks)
- GT agent: 89/112 eligible tasks reach reward 1.0; GT failures with db_match=True (judge alone): 3
- Haiku trials: 342; failed: 66; of which the DB matched and only the judge failed: 9
- tokens (agent+user messages): in=59,277,812 out=1,603,481; cost at $0.10/$0.50 per MTok, cache ignored (upper bound): $6.730 (judge tokens separate: summary.json)
- benchmark-wide log hits (replay/mismatch): 0
