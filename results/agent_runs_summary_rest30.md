# Agent runs on the 30 rest tasks (claude-haiku-5-5 agent and user, substring scorer)

pass3 dir: `rest30_pass3_haiku`; gt dir: `rest30_gt_haiku`; infrastructure_error simulations: 0

| task | n_write | pass3 rewards | haiku_pass | terminations | gt_eligible | gt reward | gt termination | gt db_match |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 2 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 4 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 5 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 6 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 12 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 13 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 14 | 2 | 1 0 0 | 1/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 15 | 1 | 1 1 0 | 2/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 17 | 3 | 1 1 0 | 2/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 18 | 5 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 24 | 1 | 0 1 1 | 2/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 25 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 27 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 29 | 2 | 0 0 0 | 0/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 30 | 1 | 1 0 1 | 2/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 31 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 33 | 2 | 1 0 0 | 1/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 34 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 35 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 36 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 38 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 39 | 3 | 0 0 1 | 1/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 40 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 41 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 42 | 2 | 0 1 1 | 2/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 43 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 45 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 47 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 49 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |

- pass^1 = 0.867 (n=30 tasks)
- pass^2 = 0.767 (n=30 tasks)
- pass^3 = 0.700 (n=30 tasks)
- GT agent: 22/27 eligible rest tasks reach the target state
- tokens (all messages, agent+user): in=15,836,869 out=569,418; cost at $0.10/$0.50 per MTok, cache ignored (upper bound): $1.868
- benchmark-wide log hits (replay/mismatch): 0
- infrastructure_error simulations in these runs: 0
