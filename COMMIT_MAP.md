# Commit map after the history rewrite of 2026-10-27

The commit messages of the whole history were rewritten once, to drop a trailing attribution line; no tree changed (verified: identical tree hash for each of the pairs below). Provenance stamps written before the rewrite (`overlay_commit` in `results/v2/provenance*.json`, `results/v2/runs/*/summary.json`, `results/v2/noop_judge_probe.md`, `block2/summary_v2.md`, `results/v2/rescore_summary*.md`) cite the old short hashes; this table maps them to the current ones.

| old | new | subject |
|---|---|---|
| 9758aa7 | 0735e91 | Init audit repo: kickoff prompt and .gitignore |
| d0479d0 | ab18664 | Pin tau2-bench v2.0.0 (989d328); sample.json (seed 42, k=20 of airline base); audit scaffo |
| dfc27fb | f4338f4 | Static no-op scan over all 50 airline tasks: 23/50 pass with an empty trajectory |
| 126dbca | 1d26f4c | Add NL-judge patch (OpenAI default -> anthropic/claude-haiku-5-5) as a recorded deviation; |
| dd048cc | 4b6f8be | Run scripts for the pilot and the 20-task agent runs (no API call without .env); results s |
| 3193945 | 0a3e637 | audit_log.csv schema conventions (schema.md) and stdlib validator; static_scan.csv passed  |
| 2a313a3 | 4a35d70 | Task cards: one Markdown file per airline task (description, user-sim instructions, refere |
| 0eb91d7 | 5be9762 | checklist.md (49 checks, 1a-6h) + fixes: ALL-row convention, NL-judge patch not applied (C |
| 527e63b | 86d1a06 | static_scan.py: pre-screen columns from checklist.md (per-action WRITE no-ops, second repl |
| f588560 | 0988f0a | probe_2h.py: WRITE-order permutation probe (3 sampled tasks change hash: 7, 23, 32); make_ |
| 2d3ecec | 88e10b9 | build_audit_log.py: rebuild audit_log.csv from static_scan/probe/review CSVs and validate; |
| e1e444f | 5e6adfe | audit_log.csv built from all CSV inputs (static, 2h probe, 4 reviewer batches, ALL rows);  |
| d7eb902 | 2b1e77f | issues_draft: I2 (calculate admits ** and the timeout is checked only between steps) |
| 973d8b5 | 69ae99b | make_summary: add share of defective tasks excluding the documented no-op class (9/20); AL |
| 0a306a9 | 9ae20d7 | Reviewer inputs: per-task static review (1d, 2g, 2k, 4a-4e) for the 20 sampled tasks and b |
| 61b45dc | 943e7d6 | Skeptic review applied: 27/27 medium/high rows confirmed; 2k aligned for tasks 26/28; issu |
| ecbd4e6 | 398b5e6 | Skeptic verdicts for the two aligned 2k rows (26, 28); audit_log rebuilt: 29/29 medium/hig |
| 0ec2da9 | 27c5c68 | make_summary: share of defective tasks excluding every no-op-derived defect (6/20); summar |
| 81dd455 | 3820fe7 | agent runs: pilot on Haiku 5.5 passes 5/5 after dropping the default temperature |
| 1c59526 | af0f7e8 | agent runs: 20 sampled tasks x 3 Haiku trials + ground-truth agent on 16 eligible tasks |
| 385a999 | 6402c90 | make_summary: Table 4 with the agent-run numbers (pass^k, stability, ground-truth solve ra |
| 6ace537 | f4b6ab7 | trajectory review of the 21 failed/flipped runs (provisional, skeptic pass pending) |
| 96c0c58 | 44db1bf | make_summary: headline shares split by method (static/probe vs agent_run, with and without |
| 20043b5 | 071fc57 | agent phase closed: skeptic verdicts applied, final numbers, issue candidates I6/I7 |
| bf4722c | bc26e9d | task 32: pre-registered counterfactual simulator probe settles 1e as a defect (class D) |
| a6382a6 | d7552c0 | blind re-review of 3 sampled tasks (23, 10, 37): 27/29 label agreement, kappa 0.76; two di |
| 5283bd6 | 3cd6778 | repo layout for publication: scripts/ and scripts/runs/, STRUCTURE.md map; pipeline re-ver |
| 7396e04 | aab6068 | block 2: pre-registered plan, task fixes v2 (tasks 7, 23, 32, 44) generated from anchored  |
| b0fc614 | d5a6b65 | block 2: scorer v2 overlay (hash_canon, comm_boundary, nl_enforce) with selftest; tasks_v2 |
| 55a35c0 | d8e08eb | block 2: deterministic v2 results (no-op 23/50 -> 0/50; permutation probe 24 -> 4 of 78),  |
| 5f4d92a | f252d91 | block 2: design-review changes — indexed one-to-one judge mapping with re-ask and undeterm |
| bafdbdc | cdfc825 | block 2: task-32 probe on v2 text (two_step 10/10 accept; step1_only 8/10 accept -> wordin |
| 3d84550 | d9c4b3c | block 2: judge pass 2 on the 76 recorded simulations (one true flip: task 9 t0; task 9 t1  |
| d55bd49 | 90fe423 | block 2: hand-check of 46 judge verdicts (reward-changing, process, communication classes) |
| a4f86e7 | 3b1af0c | block 2: live v2 runs, fresh re-score, results review and summary |
| 55909c2 | 1545a15 | block 2: refusal-bot probe re-run on a clean overlay (0 judge calls, cached ballots replay |
| e2211e0 | de73c07 | untrack the internal kickoff notes (not part of the publication) |
| 55369f3 | d814c42 | publication hygiene: drop the kickoff entry from the map, keep the design-review check scr |
| b27af93 | 2a5e5d0 | publication hygiene: no session temp paths in the review files |
