# Block 2 — fix the scoring, fix the tasks, measure the difference

Pre-registered on 2026-10-27, before any v2 code was written. Block 1 (`audit_log.csv`, `summary_numbers.md`) found that 18 of 20 sampled airline tasks of tau2-bench v2.0.0 (commit `989d3285ae669e49503324bdb9981bf14fccedeb`) carry at least one medium/high defect. Block 2 asks one question:

> How much of the measured agent performance is an artefact of *how the exam is scored*, and how much survives when the scoring and the task statements are repaired?

The pinned benchmark is **never edited**. Everything of block 2 is an overlay that lives in this repository and imports the pinned clone; `git -C tau2-bench status` must stay clean at every commit.

## 1. What changes (v2) and why

Each change answers specific rows of `audit_log.csv`. Nothing is changed "by taste": a change without a block-1 defect row is out of scope.

### 1.1 Scorer v2 (`scripts/v2/scorer_v2.py`), three independent switches

| switch | change | answers checks | mechanism |
|---|---|---|---|
| `hash_canon` | DB hash becomes insensitive to the order of order-free lists (passengers, `payment_methods`, user `reservations`) and to *which* generated reservation id (HATHAT/HATHAU/HATHAV) a new booking received; itinerary (`flights`) order is kept because it is semantic | 2h (tasks 8, 20, 23), I3 | canonical form of the DB before hashing: sort order-free lists by content; newly created reservation ids mapped to a content-derived key |
| `comm_boundary` | every `communicate_info` string must appear as a whole token: digit strings are matched only when not adjacent to other digits, `,`-thousands are normalised on both sides (`1,327` = `1327`), words on word boundaries; a target that is itself a strict substring of another number in the text does not count | 2g (tasks 3, 23), I4 | replaces the bare case-insensitive substring test of `evaluator_communicate.py` |
| `nl_enforce` | `nl_assertions` are part of the reward (`reward = DB ∧ COMMUNICATE ∧ NL`), judged by an LLM judge on `anthropic/claude-haiku-5-5`; an **empty or tool-only trajectory fails every assertion without a judge call** (an assertion about what the agent said cannot be satisfied by saying nothing) | 2a/2b (no-op pass, 7 sampled / 23 of 50 tasks), 2k (6 rows), I1 | tau2's own `NLAssertionsEvaluator`, routed to the Anthropic judge; majority of 3 judge votes per assertion, votes recorded |

All 50 airline tasks carry `nl_assertions` (checked 2026-10-27), so `nl_enforce` applies to every task.

### 1.2 Task statements v2 (`block2/tasks_airline_v2.json`, diff in `block2/task_fixes.md`)

Only tasks with a block-1 defect that the scorer cannot repair are touched. Planned (final wording in `task_fixes.md`):

| task | rows | fix |
|---|---|---|
| 32 | 1e high, 4c | scenario cap "up to $100 for the change" → "up to $100 **net**; an intermediate charge refunded in the same conversation is acceptable"; refund destination named (the original credit card) |
| 7 | 4f | `communicate_info` "1628" → "708" (the two reservations that remain after the cancellations: 402 + 306); scenario says explicitly "total of the reservations that remain after these cancellations" |
| 44 | 4a, 4c, 2k | scenario duration rule rewritten to the per-segment reading the reference and the `$1380–1390` assertion imply; payment method named (credit card); `communicate_info` gets the total "1387" |
| 23 | 4e | `nl_assertion` 4 corrected (HAT204 is the return leg on 2024-05-28); stray quote in assertion 5 removed |

Not touched: tasks whose only defects are scoring-level (3, 8, 20, the seven no-op tasks), and every row of category 5 (user-simulator behaviour) — the simulator is a separate variable and stays identical in block 2.

## 2. Hypotheses (fixed before measurement)

| id | statement | test | decided by |
|---|---|---|---|
| H1 | Under v2 the no-op pass rate falls from 23/50 to 0/50 | static scan with an empty trajectory, v2 scorer | deterministic (rule for empty trajectories) |
| H2 | `hash_canon` alone makes the recorded reorderings of `probe_2h.csv` score 1 where only list order / new-id assignment differed | re-run the WRITE-order permutation probe with v2 hash | deterministic |
| H3 | Some recorded trajectories that scored 1.0 under v1 score 0 under `comm_boundary` and/or `nl_enforce` (passes that were artefacts); some that scored 0 score 1 under `hash_canon` (failures that were artefacts). The *direction* per task is pre-stated in `task_fixes.md` where known; the counts are the result | offline re-score of the 76 recorded simulations, each switch alone and all together | ablation table |
| H4 | On tasks v2 the ground-truth agent (`llm_agent_gt`) passes 32, 7 and 44 (fails under v1) | fresh GT run on the 20 sampled tasks | per-task |
| H5 | The Haiku agent's pass^3 under v2 differs from v1 (0.60); direction not predicted | fresh pass^3 run, 20 tasks × 3 trials, same CLI settings as block 1 | Wilson 95% CIs, per-task flip counts |

A hypothesis that fails is reported as failed; the plan is not edited after the fact (changes go into a dated "Deviations" section at the end of this file).

## 3. Rules of block 2

1. **Clone stays pinned.** No file inside `tau2-bench/` changes; `patches/` stays unapplied. v2 is `scripts/v2/` + `block2/` only.
2. **One variable at a time.** Switches are reported alone and combined. The user simulator, models, seeds and CLI flags are those of block 1: `anthropic/claude-haiku-5-5` for agent and user, `--agent-llm-args {} --user-llm-args {}`, `--max-concurrency 3`, `--timeout 900`, no `--workers`.
3. **Replay gate.** Before any v2 number is reported, the offline harness must reproduce the v1 reward of all 76 recorded simulations exactly (`results/v2/replay_check.csv`, 76/76). If it does not, the harness is wrong, not the benchmark.
4. **Block-1 files are read-only.** `audit_log.csv`, `summary_numbers.md`, `results/*.csv` of block 1 are never rebuilt with v2 logic. v2 outputs live in `results/v2/` and carry `scorer_version=v2` and the overlay commit hash.
5. **Judge validity.** The NL judge is an instrument, not an oracle: 3 votes per assertion, agreement reported; a random sample of 20 judge verdicts is checked by hand and independently by a blind second reader (same protocol as the block-1 re-review).
6. **Skeptic before spending.** A max-effort adversarial review of scorer v2 and of `task_fixes.md` runs before the live re-run; a second one over the results before they are written up.
7. **Budget.** Block-2 ceiling $5 (block-1 hard stop of $30 overall unchanged). Estimate: judge over recorded trajectories ≈ $0.3; fresh pass^3 + GT ≈ $1.3; judge over fresh runs ≈ $0.3.
8. **Nothing leaves the machine.** No push, no issues, no PRs without explicit confirmation; upstream gets the defect reports first when the time comes.

## 4. Deliverables

| path | content |
|---|---|
| `scripts/v2/scorer_v2.py` | the three switches; `python -I scripts/v2/scorer_v2.py --selftest` (permutation invariance, boundary cases, empty-trajectory rule) |
| `scripts/v2/rescore.py` | offline re-score of recorded `results.json` files → `results/v2/replay_check.csv`, `results/v2/rescore.csv` (per simulation: v1 reward, DB/COMM/NL under each switch, v2 reward), `results/v2/judge_votes.csv` |
| `scripts/v2/noop_scan_v2.py` | H1 and H2 (empty trajectory and permutation probe under v2) → `results/v2/noop_scan_v2.csv`, `results/v2/probe_2h_v2.csv` |
| `scripts/v2/run_v2.py` | live runs with the v2 evaluator and tasks v2 through tau2's own runner → `results/v2/runs/*.results.json` |
| `block2/tasks_airline_v2.json`, `block2/task_fixes.md` | the task data and a per-task diff with the defect rows each change answers |
| `block2/summary_v2.md` | before/after tables: no-op pass, per-task pass^k v1 vs v2 (same trajectories; fresh runs), GT solvability, ablation per switch, judge agreement, cost |
| `block2/skeptic_*.md` | the two adversarial reviews |

## 5. What the result will and will not show

It will show, on 20 tasks of one domain, how many "passes" and "failures" of a fixed agent were produced by the scoring rule rather than by the agent, and whether the reference solutions become reachable once the task text says what the reference assumes. It will not show that the repaired benchmark is a *good* exam — the user simulator (category 5, 8/20 tasks) stays unfixed in this block, and 20 tasks give wide intervals. Both limits are stated wherever the numbers are.

## Deviations
(none yet)
