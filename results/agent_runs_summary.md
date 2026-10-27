# Agent runs on the 20 sampled tasks (claude-haiku-5-5 agent and user, substring scorer)

pass3 dir: `sample20_pass3_haiku`; gt dir: `sample20_gt_haiku`; infrastructure_error simulations: 0

| task | n_write | pass3 rewards | haiku_pass | terminations | gt_eligible | gt reward | gt termination | gt db_match |
|---|---|---|---|---|---|---|---|---|
| 26 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 10 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 1 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 28 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 23 | 4 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 21 | 2 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 11 | 1 | 1 1 0 | 2/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 9 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 16 | 1 | 1 0 1 | 2/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 7 | 3 | 0 0 0 | 0/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 22 | 3 | 1 0 1 | 2/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 46 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 0 | - | - | - |
| 3 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 44 | 3 | 0 0 0 | 0/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 48 | 0 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 20 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 32 | 2 | 0 0 0 | 0/3 | user_stop, user_stop, user_stop | 1 | 0.0 | user_stop | False |
| 8 | 1 | 1 0 0 | 1/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 19 | 1 | 0 0 1 | 1/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |
| 37 | 1 | 1 1 1 | 3/3 | user_stop, user_stop, user_stop | 1 | 1.0 | user_stop | True |

- pass^1 = 0.800 (n=20 tasks)
- pass^2 = 0.650 (n=20 tasks)
- pass^3 = 0.600 (n=20 tasks)
- GT agent: 11/16 eligible sampled tasks reach the target state
- tokens (all messages, agent+user): in=10,354,758 out=459,891; cost at $0.10/$0.50 per MTok, cache ignored (upper bound): $1.265
- benchmark-wide log hits (replay/mismatch): 0
