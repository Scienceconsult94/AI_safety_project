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

# Commit map after the author e-mail change of 2026-10-29

The author and committer e-mail of every commit was changed to the address of the publishing account; names, dates, messages and trees are unchanged (verified: identical tree hash and message for each of the 122 pairs). Hashes quoted in notes written before this date refer to the old column.

| old | new | subject |
|---|---|---|
| 0735e91 | 6285ae2 | Init audit repo: kickoff prompt and .gitignore |
| ab18664 | b0d010f | Pin tau2-bench v2.0.0 (989d328); sample.json (seed 42, k=20 of airline base); audit scaffo |
| f4338f4 | 9453632 | Static no-op scan over all 50 airline tasks: 23/50 pass with an empty trajectory |
| 1d26f4c | 5cd0b12 | Add NL-judge patch (OpenAI default -> anthropic/claude-haiku-5-5) as a recorded deviation; |
| 4b6f8be | ded3581 | Run scripts for the pilot and the 20-task agent runs (no API call without .env); results s |
| 0a3e637 | 3efd2be | audit_log.csv schema conventions (schema.md) and stdlib validator; static_scan.csv passed  |
| 4a35d70 | 26b531e | Task cards: one Markdown file per airline task (description, user-sim instructions, refere |
| 5be9762 | 0b95d3c | checklist.md (49 checks, 1a-6h) + fixes: ALL-row convention, NL-judge patch not applied (C |
| 86d1a06 | ea2093d | static_scan.py: pre-screen columns from checklist.md (per-action WRITE no-ops, second repl |
| 0988f0a | be63100 | probe_2h.py: WRITE-order permutation probe (3 sampled tasks change hash: 7, 23, 32); make_ |
| 88e10b9 | 4ef4c21 | build_audit_log.py: rebuild audit_log.csv from static_scan/probe/review CSVs and validate; |
| 5e6adfe | a55c88a | audit_log.csv built from all CSV inputs (static, 2h probe, 4 reviewer batches, ALL rows);  |
| 2b1e77f | 5cbee15 | issues_draft: I2 (calculate admits ** and the timeout is checked only between steps) |
| 69ae99b | 7f856e9 | make_summary: add share of defective tasks excluding the documented no-op class (9/20); AL |
| 9ae20d7 | b425ffd | Reviewer inputs: per-task static review (1d, 2g, 2k, 4a-4e) for the 20 sampled tasks and b |
| 943e7d6 | f07aec1 | Skeptic review applied: 27/27 medium/high rows confirmed; 2k aligned for tasks 26/28; issu |
| 398b5e6 | 5a4a0be | Skeptic verdicts for the two aligned 2k rows (26, 28); audit_log rebuilt: 29/29 medium/hig |
| 27c5c68 | d75fa50 | make_summary: share of defective tasks excluding every no-op-derived defect (6/20); summar |
| 3820fe7 | bbb0267 | agent runs: pilot on Haiku 5.5 passes 5/5 after dropping the default temperature |
| af0f7e8 | 0a80781 | agent runs: 20 sampled tasks x 3 Haiku trials + ground-truth agent on 16 eligible tasks |
| 6402c90 | 7949125 | make_summary: Table 4 with the agent-run numbers (pass^k, stability, ground-truth solve ra |
| f4b6ab7 | 048c9e9 | trajectory review of the 21 failed/flipped runs (provisional, skeptic pass pending) |
| 44db1bf | dca5ce3 | make_summary: headline shares split by method (static/probe vs agent_run, with and without |
| 071fc57 | 383e3e6 | agent phase closed: skeptic verdicts applied, final numbers, issue candidates I6/I7 |
| bc26e9d | 8dda7b6 | task 32: pre-registered counterfactual simulator probe settles 1e as a defect (class D) |
| d7552c0 | f6f54a6 | blind re-review of 3 sampled tasks (23, 10, 37): 27/29 label agreement, kappa 0.76; two di |
| 3cd6778 | 1f57b02 | repo layout for publication: scripts/ and scripts/runs/, STRUCTURE.md map; pipeline re-ver |
| aab6068 | 0ee8ed6 | block 2: pre-registered plan, task fixes v2 (tasks 7, 23, 32, 44) generated from anchored  |
| d5a6b65 | 93af71c | block 2: scorer v2 overlay (hash_canon, comm_boundary, nl_enforce) with selftest; tasks_v2 |
| d8e08eb | c682ba4 | block 2: deterministic v2 results (no-op 23/50 -> 0/50; permutation probe 24 -> 4 of 78),  |
| f252d91 | ec15ffb | block 2: design-review changes — indexed one-to-one judge mapping with re-ask and undeterm |
| cdfc825 | cba1e7d | block 2: task-32 probe on v2 text (two_step 10/10 accept; step1_only 8/10 accept -> wordin |
| d9c4b3c | 0248abf | block 2: judge pass 2 on the 76 recorded simulations (one true flip: task 9 t0; task 9 t1  |
| 90fe423 | 58a5447 | block 2: hand-check of 46 judge verdicts (reward-changing, process, communication classes) |
| 3b1af0c | 4bbbc93 | block 2: live v2 runs, fresh re-score, results review and summary |
| 1545a15 | 7d29c3f | block 2: refusal-bot probe re-run on a clean overlay (0 judge calls, cached ballots replay |
| de73c07 | d85ed9b | untrack the internal kickoff notes (not part of the publication) |
| d814c42 | 8075ded | publication hygiene: drop the kickoff entry from the map, keep the design-review check scr |
| 2a5e5d0 | 4b0d9cf | publication hygiene: no session temp paths in the review files |
| 37c8d9a | a145300 | commit map for the provenance stamps after the message rewrite |
| c809aa7 | 8e01abb | README and report for blocks 1 and 2 |
| 817933c | 39c03ce | retail audit: pre-registration, per-check readings, all 114 task ids |
| c3a1f4a | f4162d5 | retail audit: static scan, WRITE-order and argument probes, empty/transfer probes with the |
| 75ef614 | c0bcd80 | retail audit: twelve static review batches, tool-bug probe (1g), forbidden-write-order pro |
| 398521b | 261b6cd | retail audit: benchmark-level rows (ALL), audit log before the adversarial review |
| b1b053f | b859c32 | retail audit: blind re-review of 12 tasks and provisional agreement figures; null-agent ta |
| c72beb7 | 9d5d0f3 | retail audit: paid runs (Pass^3 on 114 tasks, ground-truth agent on 112), adversarial revi |
| 00164e7 | a5d638a | retail audit: trajectory review of the agent runs (five batches, 45 tasks, 89 trajectories |
| 6f70eba | 37bf8ec | retail audit: 3-vote re-judge (check 2j: 103/169 strict-parser rejections, 1 reward flip i |
| c139a97 | 4dfa4e6 | null-agent table: desk research on nine external agent benchmarks (scoring mechanism, null |
| e375d4c | 50f54d9 | retail audit: final audit log with the trajectory-review rows (not adversarially reviewed, |
| c9d9b7a | 362d68d | README and report: retail audit (all 114 tasks) and the null-agent table across tau2; issu |
| 7681c8a | 28c2f58 | Sonnet strong-vs-weak script: cost estimate from the airline Haiku token counts at Sonnet  |
| c143c90 | 989a2f4 | cost ledger: billing reported at about $11 (consistent with the own estimate); the $30 har |
| 64f5cff | 7293169 | strong vs weak: pre-registration of the Sonnet-vs-Haiku analysis, committed before any res |
| c470f5a | 8151d81 | strong vs weak: Sonnet run results (20 airline tasks x 3) and smoke run kept as recorded;  |
| 0151474 | b6d855b | demo: four offline reproductions for a five-minute demo (empty airline conversation, forbi |
| 2c67dd9 | 73d4d1c | strong vs weak: Sonnet vs Haiku on the 20 sampled airline tasks (stock scorer: pass^1 0.85 |
| a7137a8 | b08de84 | README and report: strong-vs-weak section (report section 7; later sections renumbered); D |
| 6f6cc14 | dedfa90 | null agent on four external benchmarks, scored offline with each benchmark's own code (BFC |
| a2aaf96 | b04623d | README and report: external null-agent results (report Table 9b, sections 9-12; README ext |
| 75ea07a | 43f00c1 | upstream: issue and pull-request texts ready to file for I1 and I3-I16 (nine issues, fourt |
| a499dce | 5045362 | corrections found while drafting the upstream texts, each checked against code, data or re |
| 725730b | ea700f3 | ONE_PAGER.md: the results on one page; STRUCTURE map: one-pager, demo, upstream texts, str |
| fa059c4 | 17097cd | DEMO.md: the adversarial review covered the findings from reading and probes, not the run  |
| b9f8821 | 71aeb37 | airline whole domain and the open items of blocks 1-2: pre-registration (questions Q1-Q5,  |
| 1d97d89 | 3092452 | run_rest30.ps1: block-1 runs (Pass^3 and ground-truth agent, same settings) on the 30 airl |
| df49d4c | 7b08302 | run_v2.py: parts for the 30 rest tasks (pass3_rest30, gt_rest30) and the task-32 counterfa |
| f0e5fcd | 5bfe9dc | probe_2j.py: check 2j (substring vs semantic communicate scorer, judge claude-haiku-5-5, 3 |
| 37e2648 | bc87dc3 | handcheck_fresh.py: blind hand-check sample of judge-only verdicts (negative and communica |
| b44c930 | 95b7b7d | fresh-pass hand-check: 20 judge-only items drawn (10 negative, 10 communication) with thei |
| 3702329 | 8afd836 | airline_full: deviations (adversarial review approved for the rest rows; hand-check round  |
| a8f3fa3 | 87d4bb7 | airline_full/PLAN.md: restore two file names in the hand-check deviation |
| cb07ec0 | e0e24aa | airline rest tasks: reviewer batches 5, 9, 10 (static checks, before the adversarial revie |
| 5e91c2f | 35b223e | check 2j on the recorded sample runs (Haiku, ground truth, Sonnet): 0 of 42 fact verdicts  |
| 6a159de | 8c3f482 | handcheck_fresh.py --round 2: the same 20 items with 10 judge-unmet decoys, shuffled, with |
| a4e3109 | 7e23d84 | airline_full/handcheck_fresh_r2: round-2 hand-check items (the 20 round-1 items mixed with |
| 5e5e91f | 7363c9d | static_scan.py: the six-character reservation-id pattern also matched flight numbers (hat2 |
| 1179e3e | 3ac443b | airline rest tasks: reviewer batches 6, 7, 8 (static checks, before the adversarial review |
| c55c680 | 889b1d4 | blind re-review of rest tasks 33, 35, 39 (seed-drawn; made without access to batches 8 and |
| 6d4bab1 | 90f89db | judge hand-check round 2 (blind, with decoys): readers C and D, each working on a copy wit |
| 9850ab8 | 5dc9344 | airline_full/skeptic_brief.md: adversarial review brief for the rest static rows (three pa |
| d037b04 | c989ba2 | airline rest tasks: stock agent runs (Haiku agent and user, substring scorer, block-1 sett |
| 13aaa98 | cdf2031 | check 2j on the rest runs: 0 of 58 recorded fact verdicts differ between the substring and |
| c8a833d | 673faab | rereview_agreement.py --set rest: blind re-review of rest tasks 33, 35, 39 against the rev |
| 8bea554 | bc9a78d | build_audit_log.py --ids population (all 50 tasks -> airline_full/audit_log.csv) with the  |
| 6a5824b | 2525485 | rescore.py: sets rest30 (stock rest runs, replay gate v1, embedded tasks asserted equal to |
| 4974a19 | dae9f53 | airline_full/PLAN.md deviations: task-32 arms implemented as run_v2.py parts (before eithe |
| 079d355 | 028cc07 | scripts/airline_full_summary.py: sample, rest and whole-domain tables with the pre-registe |
| 139e627 | 8ce0b88 | v2 runs on the 30 rest tasks (Haiku pass^3 15/30 under the full v2 protocol; ground-truth  |
| 5dcd398 | 9fdfcd6 | task-32 counterfactual (Q3): ground-truth agent, full v2 protocol, 10 trials per arm: A 2/ |
| e7122c1 | 83ad9a8 | airline rest tasks: trajectory review of the 19 failed or unstable rest trajectories (1e 2 |
| bf32ec7 | 4d2de63 | build_audit_log.py: an escalation with an empty skeptic_ok (rest briefs) or a re-review ad |
| 023eb6a | b9b3e72 | adversarial review of the rest 2k rows: 9 of 9 defect rows confirmed, 6/2k escalated (an a |
| 492dfd6 | 9f75afc | block 2 on the rest (Q5, H3): the 117 recorded stock rest conversations re-scored under ev |
| efc9595 | eac10ad | adversarial review of the rest rows, part other (1d, 2g, 4a-4e, mechanical): 34 of 34 defe |
| 68d91a1 | cd983cb | adversarial review, part other: 14/2g escalated to 1 medium on observed run evidence ('1,3 |
| d94f165 | 36e7442 | block 2 on the rest (Q5): the 117 fresh v2 rest conversations re-scored under every config |
| 249a634 | af2753e | adversarial review of the rest rows, part order (2h, 4c): 4 of 7 defect rows confirmed; 14 |
| b807dc3 | f53290c | adversarial review of the rest agent-run rows (1e, 4f, 5c, 5d): 10 of 11 defect rows confi |
| dc1fefd | 7013575 | consistency pass, part 1: second-pass 2h probe (scripts/probe_2h_paths.py) for write paths |
| 27b780a | 609f486 | task 29, check 1e: pre-registered counterfactual simulator probe (protocol and script, no  |
| 7208cc7 | 2ea6e56 | blind re-review of the rest rows, recomputed with all skeptic corrections: blind vs origin |
| 3edf5cd | 2e1c313 | task 29, check 1e: pre-registered probe run (10 simulator samples, about half a cent): the |
| 4757edd | 031220a | whole airline domain: audit log of all 50 tasks (1219 rows, validator 0 errors) and its su |
| 0ef1eb8 | e569ecb | docs for the whole airline domain: report section 13 (what was done on the other 30 tasks  |
| 8b4b275 | 4d53efd | STRUCTURE.md: offline rebuild check of the whole-domain pipeline: every output reproduced  |
| d648ba5 | a9a4dec | adversarial review of row 22/2h (approved by the account owner): holds as filed, defect 1  |
| be7de22 | 2c80471 | retail: brief for the adversarial review of the agent-run rows (1e, 4f, 5c, 5d, 2j) in fou |
| 4e6d25c | 3a2d864 | HAL check: four TAU-bench Tool Calling rows on the HAL airline leaderboard (28%, 36%, 36%, |
| e51fd24 | 46e0634 | retail builder reads the override file of every part of the run-row adversarial review (re |
| 619329e | bc07424 | retail run rows: adversarial review in four parts (approved by the account owner): 66 of 7 |
| 848951b | 16deea9 | plain-language pass over the new HAL and retail passages (report sections 5, 6 and 10, REA |
| 65d26c5 | ca8efd5 | nothing is filed upstream (decision of 2026-10-28): report section 8 cites the upstream is |
| 112e265 | f01dbe0 | headline defect counts leave out the documented pass for doing nothing (checks 2a, 2b; ret |
| de9222f | a67b05f | checklist count corrected to 49 (checklist.md lists ids 1a to 6h; the figure 52 had no sou |
| 6aec581 | f79f8fc | consistency sweep of the documents against their source files (2026-10-28): five read-only |
| 79d6aa1 | dedc032 | eight wording fixes from a cold read of the entry documents (2026-10-29): README states th |
| d708313 | 1637b99 | authorship stated (decision of 2026-10-29): README, report and ONE_PAGER say who did what. |
| 3ecca9c | 242ca99 | authorship paragraph names the tool (decision of 2026-10-29): the audit was carried out wi |
| fbe1a07 | aa9e3d3 | local absolute paths replaced by placeholders before publication (user folder, session tem |
| 92db2c4 | af8cfc3 | internal reviewer name replaced by 'the adversarial reviewer' in schema.md and the audit-l |
