# Check 2j, retail: the judge inside the official score

(a) Stock strict parser over the live judge replies: 103/169 replies would have been rejected (files: results/retail/runs/retail_pass3_haiku/judge_calls.json, results/retail/runs/retail_gt_haiku/judge_calls.json, results/retail/judge_calls_noop.json); replies with fewer results than assertions: 0.

(b) Re-judge with 3 votes (same prompt, same model): 159 simulations, 243 assertion verdicts; replies without any JSON (retried, counted as a missing vote after 3 attempts): 1; live vote != majority on 1 assertions; live verdict omitted an assertion 0 times; reward flips: 1 (pass->fail 0, fail->pass 1).

- retail_pass3_haiku task 110 trial 1: live reward 0.0 -> majority 1.0 (db_match=True)

judge calls this run: 385; tokens in/out 2220267/163355; own estimate $0.304
