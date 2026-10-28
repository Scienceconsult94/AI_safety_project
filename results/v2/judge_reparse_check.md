# Judge-parser gap: re-parse of the discarded ballots (offline, no model call)

| set | replies | discarded (parse error) | bare-array replies among them | ballots recovered (met/unmet) | pairs with a discarded ballot | majority verdicts changed |
|---|---|---|---|---|---|---|
| recorded (judge pass 2) | 281 | 18 | 18 | 8 (7/1) | 8 | 0 |
| fresh re-score | 49 | 5 | 5 | 4 (1/3) | 4 | 0 |
| live pass3 | 197 | 21 | 21 | 16 (16/0) | 11 | 0 |
| live gt | 51 | 3 | 3 | 0 (0/0) | 0 | 0 |
| live gt3 | 32 | 6 | 6 | 4 (4/0) | 4 | 0 |
| **all** | 610 | 53 | 53 | 32 | 27 | 0 |

Pairs decided on fewer than 3 determined ballots (as cached): 27; of them on a single ballot: 5.


Reading: every discarded reply is a bare JSON array; with the parser fixed the ballots are recovered and no majority verdict moves, so the cached rewards stand. The verdicts that rested on one or two ballots are listed in `judge_reparse_check.json` (field `thin`) and named in `block2/summary_v2.md`.
