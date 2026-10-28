# Agent exams need validating: the results on one page

**Question.** Agent benchmarks, exams for AI agents, rank models by pass rate (share of tasks completed) and support deployment decisions. Do they measure the agent? This work audits tau2-bench v2.0.0, a widely used customer-service exam (airline: all 50 tasks, 20 sampled first and the other 30 audited afterwards with the same method; retail: all 114 tasks). It also measures a do-nothing agent's score on tau2 and four external benchmarks.

**Method.** Every task goes through 52 fixed checks: reading the task and its scoring, tests with known outcomes, paid agent runs. Hypotheses and predictions were recorded before reading results. Every finding from reading and testing went through adversarial review (an attempt to overturn it); a blind second review (sampled tasks, earlier labels hidden) agreed with the corrected labels on every row. Scripts rebuild every number from recorded files. Spend on paid model calls (API, application programming interface): about $33, own estimate from token counts.

**Findings.**

| what was measured | result |
|---|---|
| airline tasks with a confirmed medium- or high-severity defect | 18 of 20 sampled (17 without the one finding that depends on the non-default scorer setting the runs selected) |
| airline, whole domain: tasks with a confirmed medium- or high-severity defect | 44 of 50 (18 of 20 sampled, 26 of 30 others) |
| airline tasks passed by an empty conversation | 23 of 50 |
| retail tasks with an adversarially reviewed defect | 44 of 114 (67 counting the unreviewed rows from the agent runs) |
| retail tasks accepting a policy-forbidden order of changes | 14 |
| retail tasks hit by a tool that stores the wrong item | 5 |
| retail failures of an agent given the answer key, explained by the model playing the customer | 12 of 23 |
| repaired exam ("v2"): tasks passed by an empty conversation | 23 of 50 → 0 of 50 |
| the agent's share of tasks passed in all 3 trials, unmodified exam → v2 | 0.60 → 0.60 on the 20 sampled airline tasks; 0.70 → 0.50 on the other 30 |
| stronger vs weaker agent model, unmodified exam (20 tasks × 3 trials) | mean pass rate (trials passed, averaged over tasks) 0.850 vs 0.733; ahead on 6 tasks, behind on 1; p = 0.125 (p value: the chance of a split at least this lopsided if the two models were equally good) |
| the same comparison under v2 | gap +0.150, p = 0.039 before correcting for three comparisons |
| floor (score of a do-nothing or refuse-only agent) on external benchmarks | BFCL V4: 10 of 100 points; original tau-bench airline: 38%; OSWorld-Verified: 8.1% or 7.0%, by version of the task files (task definitions); WebArena: 4.4% (original), 3.0% (Verified) |
| published scores below that floor (HAL leaderboard, TAU-bench Airline: same 50 tasks, same scoring code) | 4 runs, one per model: 28%, 36%, 36% and 36%, against 38% for doing nothing |

**What it means** (interpretation).

- **The headline number hides the exam's faults.** Repairing the airline exam cut do-nothing passes from 23 to 0, yet the agent's score on the 20 sampled tasks stayed at 0.60. On the other 30 tasks it fell from 0.70 to 0.50, because v2 also reads the requirements written only in free text. A leaderboard (public model ranking) cannot show its exam's faults.
- **A pass rate measures three things at once.** In retail the simulated customer, not the agent, explains about half the failures of an agent that knows the answer: the score mixes agent, simulated customer and exam.
- **Exam faults shrink the difference between models.** Nine of the 20 airline tasks give strong and weak models the same result by construction: 7 pass for doing nothing, 2 cannot be passed. On the unmodified exam the gap is not significant; fixing one wrong reference answer (the official expected outcome) moves it across the usual significance threshold, though not after correcting for the three comparisons.
- **The floor has to be measured, not assumed.** A do-nothing agent scores 0 to 46% across tau2 domains and 0 to 38% across external benchmarks. On a public leaderboard, four published airline scores (one run each) sit below the 38% that doing nothing earns on the same tasks, and the page shows no floor to compare with. On OSWorld-Verified the floor changed between two task-file versions. Defects also carry over: original tau-bench retail task 106 passes for doing nothing; tau2 kept it as task 105 and added a requirement making it impossible.

**What would help** (proposal). Publish next to every agent leaderboard: do-nothing and refuse-only floors; a replay of each task's reference solution (official correct actions) as a control; the task-file version behind each score; and, with a simulated customer, the share of failures it causes. Scripts here produce the do-nothing floor and the reference replay for five of the six tau2 task sets without paid model calls.

**What is in the repository.** Full report (`report.md`), audit logs, an offline demo (about 12 seconds, no model call; `scripts/demo/demo.py`, script in `DEMO.md`), and 16 issue drafts for the maintainers with reproduction scripts and patches (`issues_draft.md`, `upstream/`; nothing filed).

**Limits.** One benchmark audited in depth; retail rows from agent runs not adversarially reviewed; reviewers and adversarial reviewers are language models, not people; one run per model in the strong-vs-weak comparison; three of nine external rows counted from task files rather than measured.
