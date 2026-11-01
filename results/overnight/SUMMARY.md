# Overnight work 2026-10-31 → 2026-11-01: summary for the author

Branch `overnight-2026-11-01` (from main a3fd7e1), merged into main and pushed on 2026-10-31 evening after the two reviews named below. Nothing was filed, posted or sent. No published number was edited; all new results are under `results/overnight/`, new texts under `upstream/ready/`, the new script under `scripts/overnight/`. Running log: `LOG.md`. Paid calls: one judge run, 9,349 calls, own estimate $7.73 (`cost_overnight.md`; cap $40). Two independent read-only reviews of the branch (models claude-fable-5-1 and claude-opus-5-5) recomputed every T3 number and checked T1, T2, T5, T6 and hygiene; both verdicts "mergeable after fixes"; the fixes are applied and listed in `LOG.md`.

| task | status | result in one line | files |
|---|---|---|---|
| T1 reproducibility (fresh clone, fresh environment) | done | REPRODUCES WITH DOC FIXES: demo matches; both offline sequences give the published numbers once a missing copy step is added; five command edits applied to STRUCTURE.md (two run in the clone, three by the same reasoning, not run) | `T1_repro.md`, `DISCREPANCIES.md` (D1), STRUCTURE.md diff |
| T2 upstream issue texts | done | both texts ready to paste, but both problems are already partly in the upstream tracker; texts narrowed to the parts that are not | `upstream/ready/issue_nl_assertion_judge.md`, `upstream/ready/issue_db_hash_order_and_generated_ids.md` |
| T3 judge-copy sensitivity, airline | done | six copies of the judge change the verdict of 7 of 360 recorded airline simulations; per copy 0.7 to 1.4% of judge-decisive simulations; the agent's own run-to-run spread is 23 to 27% (haiku) and 10% (sonnet) | `T3_PLAN.md`, `T3_sensitivity.md`, `T3_verdicts.csv`, `T3_votes.csv`, `judge_cache_T3.json`, `T3_provenance.json` |
| T4 retail | partial (as agreed) | same statistic on the recorded retail runs, no fresh runs, no v2 for retail: 3 of 159 simulations change in some copy; run-to-run spread 16.7% | same files, sets B1 and B2 |
| T5 README reviewer block | done | table of three demo commands, the number each prints and its source file, after the title | README.md diff |
| T6 forum post draft | done | 699 words from ONE_PAGER and README's Limits, every number traced to a source line (line numbers of main a3fd7e1) | `post_draft.md` |

## T1: what a stranger gets

Fresh clone of the public repository (a3fd7e1), tau2-bench at the pinned commit, `uv sync` (Python 3.12.16), separate Python 3.11.2 with today's pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0. `DEMO.md` as printed: 13 s, all four reproductions match the expected output. The two STRUCTURE.md sequences as printed: 19 of 20 commands ran; `build_audit_log.py` failed because `agent_rows.py` looks for the recorded runs in `tau2-bench/data/simulations/`, which a fresh clone does not have, and silently writes empty files. With the copy step added, `audit_log.csv`, `haiku_pass.csv`, the summaries, the task cards and `summary_numbers.md` are byte-identical to the commit; Block 2 differs only in run stamps (0 judge calls, all cached). Every README number checked matches the rebuilt files.

Five edits applied tonight (documentation only, `STRUCTURE.md`): the copy step before `agent_rows.py` in the sample block (run in the clone) and in the rest-30 block (same defect, not run); `$uv` defined in the three blocks that open a new shell (the Block 2 block run in the clone; the retail and strong-vs-weak blocks same defect, not run). Not applied, for the author: pin the analysis package versions; say that `python` in the blocks is the Python 3.11 environment; make `agent_rows.py` stop with an error when it finds no runs instead of writing empty files; re-execute and commit `analysis.ipynb` (its stored output still shows 18/20 and 13/20 from 2026-10-27 while README says 16/20 and 12/20; `DISCREPANCIES.md` D1).

## T2: upstream status (tracker read 2026-10-31, 706 items, #1 to #711; HEAD da0835f6 of 2026-10-29)

- NL-assertion judge: I9 (tool calls invisible) is #553 (fix #584 open, tool calls still hidden); the fenced-reply part of I10 is #555 (fixes #562 and #469 open, neither handles a bare JSON array); I14 (omitted verdict counts as met) is #554 (fix #581 open). New part, kept in the text: the bare top-level JSON array reply. Still reproduces at HEAD by reading the code (every cited file byte-identical to the pinned commit).
- DB hash: #514 covers list order via `payment_history`. New parts, kept in the text: passenger order and the generated reservation ids. Still reproduces at HEAD by reading the code.
- Two choices before pasting: both texts carry the public repository URL (remove if unwanted); the NL file suggests, as optional, a comment on #553 with the task 9 trial 1 evidence (not written).

## T3 and T4: the judge as a source of noise, measured

Definition kept from the kickoff; copies: three prompt wordings (V2 prompt, tau2's stock prompt with its list format, a paraphrase) × two independent draws, three votes each, majority rule; threshold and floor copies offline. "Seed/temperature" could not be re-drawn (Anthropic models reject a non-default temperature, issue I5); independent draws take its place. Prediction written before the run (`T3_PLAN.md`), shown next to the result in `T3_sensitivity.md`.

| set | simulations | judge-decisive | reference passes | passes across the six copies | simulations flipped in at least one copy | run-to-run spread (trial pairs that disagree) |
|---|---|---|---|---|---|---|
| A1 recorded sample 20×3, haiku, V2 | 60 | 45 | 44 | 44 to 44 | 0 | 23.3% |
| A2 recorded rest 30×3, haiku, V2 | 90 | 76 | 68 | 68 to 70 | 3 (tasks 5, 34) | 26.7% |
| A3 fresh v2 sample 20×3, haiku | 60 | 47 | 47 | 46 to 47 | 1 (task 8) | 23.3% |
| A4 fresh v2 rest 30×3, haiku | 90 | 72 | 64 | 64 to 64 | 0 | 26.7% |
| A5 recorded sample 20×3, sonnet, V2 | 60 | 54 | 53 | 52 to 54 | 3 (tasks 8, 28) | 10.0% |
| B1 retail pass^3 run, haiku, stock scoring (the 120 of 342 simulations with assertion-gated reward) | 120 | 107 | 99 | 97 to 98 | 3 (tasks 67, 110) | 16.7% |
| B2 retail ground-truth run (the 39 of 112 simulations with assertion-gated reward) | 39 | 34 | 31 | 31 to 31 | 0 | one trial, undefined |

Pooled over judge-decisive simulations: the same prompt in a new draw changes 1.2% of airline verdicts (P0, the prompt of the airline reference: 7/588) and 0.7% of retail (P1, tau2's stock prompt, which the retail reference used: 2/282); another wording changes 1.0% of airline (P1, P2: 12/1176) and 1.4% of retail (P0, P2: 8/564). Requiring unanimous votes loses 2.5% of airline reference passes (7/276), but 5 of those 7 have no unmet vote, only an undetermined ballot left in the reference by the old parser gap, so the loss from real dissent is 2 of 276; accepting any one vote gains 4 of the 18 judge-decisive airline fails. Every flipped simulation has one assertion whose votes sit at 2-1 or 1-2 in some copy (list in `LOG.md`). Prediction vs result: the redraw and wording effects came in below the predicted 2 to 8%; the unanimous-threshold loss below the predicted 5 to 10%; the any-vote gain above its range (22.2% against 10 to 20%, on 18 fails); the run-to-run spread inside its range for the haiku sets and retail (16.7 to 26.7%) and below it for sonnet (10.0%); cost below the estimate.

Floor definition (airline, offline): taking the refusal-only agent as the floor would remove 28 to 41% of the credited V2 passes (its 14 tasks are where the agents pass most); under the stock scorer 41 to 65% of the same agents' passes fall on the 23 tasks an empty conversation passes.

Reading, for the author to confirm: on these recorded runs the judge is a small part of the noise. A copy of the judge moves one to two simulations in a hundred; running the same agent again on the same task moves one in four (haiku) or one in ten (sonnet). Under the six prompt-and-draw copies with the majority rule, the pass count of a set moves by at most 2 simulations; the threshold copies move it by up to 4 (B1 unanimous 95 against 99). This holds for one judge model (claude-haiku-5-5), three wordings, two draws, the views and the parser used here; the judge model itself was not varied, and sets A1, A3 and A4 have 1, 0 and 8 judge-decisive fails, so copies there can almost only lose passes. This does not speak to the judge's validity (task 9 trial 1 in `block2/judge_handcheck.md` remains the example of a unanimous wrong verdict); it speaks to its stability.

## What the author must check by hand before using any number

1. `T3_sensitivity.md`: read the paraphrase prompt in `scripts/overnight/t3_judge_copies.py` (P2) and decide whether it says the same as tau2's prompt. P1 is tau2's wording and list format but keeps the V2 transcript view for airline and the tolerant parser; it is a wording copy, not a replay of the stock evaluator.
2. Retail reference R is the 3-vote majority of check 2j, not the live single vote that produced the published retail numbers (that vote is copy L: it differs from R on 1 of 159, as published).
3. `DISCREPANCIES.md` D1: decide whether to re-execute and commit `analysis.ipynb` before the next push.
4. `upstream/ready/*.md`: filed on 2026-11-01 at the author's request from the author's account, with the repository URL kept: [#735](https://github.com/sierra-research/tau2-bench/issues/735), [#736](https://github.com/sierra-research/tau2-bench/issues/736). A tracker re-check the same day (39 items updated since 2026-10-30) found no duplicate of the two new parts; it did find #708 (= I12) and #321, #714, #715 (parts of I13/I16), not yet reflected in the counts above.
5. README: the new reviewer block sits above Key results, as the kickoff asked; the file now opens with a table. Move it below the reading paths if that reads better.
6. `post_draft.md`: HAL stays unexpanded to keep the post under 700 words; the repository expands it once, in `null_agent/external_candidates.md` (Holistic Agent Leaderboard), and two words can be swapped in by hand; the three dropped Limits sentences (cost, two-model comparison, Wilson intervals) are listed in `LOG.md`.

## Not done

- T4 in full (fresh retail runs under stock and v2): not attempted, by agreement; v2 exists only for airline.
- Optional T1 clarifications listed above (version pins, `python` note, `agent_rows.py` guard, notebook re-execution): left to the author.
- `T3_run.log` was trimmed to the progress lines; the 9,349 litellm price-lookup errors it contained (the known "LLM Provider NOT provided" cost message, present in every earlier judge run as well) were dropped.
