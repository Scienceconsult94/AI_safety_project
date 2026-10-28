# Check 2j: substring vs semantic communicate scorer (airline, stock tasks)

Judge `anthropic/claude-haiku-5-5`, model_args {}, 3 passes per fact, verdict = majority (a tie or no determined vote is undetermined). The semantic judge reads assistant and user text; the substring scorer reads assistant text only. Runs: `sample20_pass3_haiku.results.json`, `sample20_gt_haiku.results.json`, `sample20_sonnet_t3.results.json`, `rest30_pass3_haiku.results.json`, `rest30_gt_haiku.results.json`.

| task | communicate_info | facts judged (recorded runs) | substring met | semantic met | differ | undetermined | not unanimous | null agent: substring / semantic |
|---|---|---|---|---|---|---|---|---|
| 3 | ['4'] | 7 | 7 | 7 | 0 | 0 | 0 | fail / fail |
| 7 | ['1628'] | 7 | 0 | 0 | 0 | 0 | 0 | fail / fail |
| 11 | ['5244'] | 7 | 7 | 7 | 0 | 0 | 0 | fail / fail |
| 14 | ['327', '1000', '1786'] | 12 | 11 | 11 | 0 | 0 | 1 | fail / fail |
| 18 | ['23553'] | 4 | 4 | 4 | 0 | 0 | 0 | fail / fail |
| 23 | ['327', '1000', '1286'] | 21 | 21 | 21 | 0 | 0 | 0 | fail / fail |

Recorded fact verdicts that differ between the scorers: 0 of 58.
Tasks with a 2j defect (any differing trial): [].

