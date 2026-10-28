# Retail: how each check of `checklist.md` is read in this domain

Same ids, same methods, same severities as `checklist.md` (airline). This file lists only what differs. Paths are relative to `tau2-bench/`. Domain code: `src/tau2/domains/retail/tools.py` (797 lines), `environment.py`; data: `data/tau2/domains/retail/{tasks.json, db.json, policy.md, split_tasks.json}`.

## What is different about retail scoring

- `reward_basis` is `["DB","NL_ASSERTION"]` in 112 tasks and `["DB"]` in tasks 33 and 34. `COMMUNICATE` is never in the basis, so the 36 non-empty `communicate_info` lists are diagnostics that `tau2 run` never evaluates (`evaluator.py`: `CommEvaluator` runs only when `COMMUNICATE` is in the basis).
- `nl_assertions` exist in 40 tasks (1–4 each, 61 in total) and **gate the reward** there: `NLAssertionsEvaluator.calculate_reward` returns 1.0 when the list is empty, otherwise an LLM judge reads `role: content` lines and the reward is 1.0 only if every assertion is `metExpectation: true`. The default judge is `gpt-5.4-mini-2026-03-17` (`config.py`); this audit substitutes `anthropic/claude-haiku-5-5` (PLAN.md §2).
- The judge maps results to assertions by the text the judge echoes back and iterates over whatever it returns; an assertion the judge omits is silently not counted (`all()` over the returned list). The reply is parsed with a bare `json.loads` (no code fence, no array accepted).
- No clock, no id generation: tools never read time and never create records. Writes are status changes on existing orders and users; `exchange_items`, `return_items` are stored sorted.
- Tasks 24 and 57 have no reference actions; the ground-truth agent skips them. Task 57 also has no `nl_assertions` and empty `communicate_info` (nothing is checked at all; `reward_basis` still lists `NL_ASSERTION`).
- `tasks.json` carries an `issues` field: tasks 4, 5 and 7 have an open upstream-recorded issue each (2026-01-16), with a demonstrating simulation under `task_issues/`. They are compared with the audit rows after the review (PLAN.md P5), not used as input to it.

## Per-check deltas

| check | retail reading |
|---|---|
| 1a | Defect if `evaluation_criteria` is null or `reward_basis` is empty. `["DB"]` on 33/34 is logged in `note`, not a defect on its own (both have no `nl_assertions`, so the reward is the same). |
| 1b–1c | Unchanged (`get_environment()` from `retail/environment.py`; WRITE tools: `cancel_pending_order`, `modify_pending_order_{address,items,payment}`, `modify_user_address`, `return_delivered_order_items`, `exchange_delivered_order_items`). |
| 1d | Reference arguments: user id (via email or name+zip), order ids, item ids (old and new), payment method id, address fields, cancel reason. "Derivable" = reachable by READ tools from what the scenario states (`find_user_id_by_*`, `get_user_details` lists the orders, `get_order_details`, `get_product_details` lists variants). Values only in `unknown_info` do not count as stated. |
| 1e–1f | Unchanged; `haiku_pass` = k/3 with the Haiku judge in the loop (stated with every number). |
| 2a | Positive control = target hash equals the initial hash **and** `nl_assertions` is empty (NL reward 1.0 by construction) — or `NL_ASSERTION` not in the basis. `communicate_info` plays no part. |
| 2b | Empty trajectory through `EnvironmentEvaluator` + `NLAssertionsEvaluator` (judge called only where assertions exist, `scripts/retail/noop_judge_probe.py`). |
| 2c | Transfer-only trajectory (greeting, one user turn, `transfer_to_human_agents`, the policy's transfer sentence); the tool is GENERIC and not replayed, so the DB part equals 2b; the judge decides the rest. Tasks whose reference *is* a transfer (10, 12, 26, 50) are not defects here. |
| 2d | Mechanical: `scripts/retail/probe_2d.py` substitutes one argument of one WRITE action at a time (another payment method of the same user; the other cancel reason; another available variant of the same product; the user's default address vs the order address) and replays. Defect (high) when a substitution that breaks the request or `policy.md` leaves the target hash unchanged. |
| 2e | End-state-only: a wrong write that a later write overwrites is invisible (`modify_pending_order_address` twice; `modify_user_address` twice). Probed by inserting a wrong address write before the reference one. Benchmark-level row plus per-task rows for tasks with address writes. |
| 2f, 2g, 2i | n/a for the reward: `COMMUNICATE` is not in the basis (one `ALL` row each, defect=0, note). The substring-matching risks of the 36 `communicate_info` lists are listed under 2k instead. |
| 2h | WRITE-order permutations (≤ 120 per task), same rule as airline. |
| 2j | The choice of scorer = the NL judge: (a) share of live judge replies the stock strict parser rejects; (b) 3-vote offline re-judge of every fresh simulation with assertions, flips of the live single vote and of the reward (`scripts/retail/rejudge.py`). Defect (medium, benchmark-level) if the parser rejects any reply or if any reward flips under re-judging. |
| 2k | A requirement stated only in `communicate_info` (never scored) and not covered by an enforced `nl_assertion` or by the DB hash. Medium. Also the mirror case: an `nl_assertion` that only restates what the hash already checks is logged in `note` (no defect). |
| 2l | n/a, by construction (as airline). |
| **2m** (new) | A process requirement of `policy.md` with no DB footprint: authenticate before any lookup or action; list the details and get explicit "yes" before each write; one exchange/modify per order (correction 2026-10-27: the tools enforce this only for item changes: `modify_pending_order_items` requires status exactly `pending`, while `modify_pending_order_address` accepts any status containing `pending`, so an address change after an item change is accepted although policy.md l.110 forbids it). Defect (medium) at benchmark level; per task only where an `nl_assertion` names such a requirement and the hash cannot check it. |
| 3a–3b | Grep `src/tau2/domains/retail/tools.py`; `calculate` is the same whitelist + `eval`. |
| 3c–3e, 3g, 3i, 3j | Unchanged. |
| 3d | `communicate_info` values, `nl_assertion` numbers and computed amounts (refund totals, price differences) searched in the user prompt text. |
| 3f | `get_environment()` loads `db.json` per simulation (`retail/environment.py`); `RetailTools` keeps state in `self.db` only. |
| 3h | No user tools for retail. |
| 4a | `reason_for_call` + `task_instructions` vs the WRITE actions and their arguments (which items, which new variants, which payment method, which address, which reason). |
| 4b | Each WRITE vs `policy.md`: status rules (pending / delivered), cancel reasons, refund destination (original method or an existing gift card for returns), gift-card balance for price differences, one modify/exchange per order, same-product variant rule, authentication first. |
| 4c | Choices the scenario leaves open: payment method for a refund or difference (original vs gift card), which variant when several match the stated options, which orders when the user names a set loosely, address fields. |
| 4d | Ids, names, zip, emails, order statuses, item availability and prices in the scenario vs `db.json`. |
| 4e | `nl_assertions` and `description` vs `actions` / `communicate_info` (amounts, counts, product facts). |
| 4f, 5c–5f | Unchanged (trajectories from the retail runs). |
| 5a | Deterministic by construction (no clock, no ids); the scan still replays twice. |
| 5b | Unchanged. |
| 5g | `info.git_commit` == pinned; model ids; the judge model and args are **not** recorded in `results.json` (checked under 6g). |
| 6a–6f, 6h | Unchanged; 6e counts `infrastructure_error` simulations of the retail runs. |
| 6g | Scorer disclosure: `results.json` records `communicate_scoring` but not the NL judge model/args/prompt version although the judge gates the reward. |

## Static pre-screen columns (retail additions)

`results/retail/static_scan.csv` keeps the airline columns where they apply and adds: `nl_in_basis`, `comm_in_basis`, `n_transfer`, `noop_needs_judge` (target == initial and assertions exist: the empty-trajectory verdict depends on the judge), `comm_covered_by_nl` (every `communicate_info` string appears in some `nl_assertion`, string match; the reading decides the rest), `upstream_issues` (count of entries in `tasks.json` → `issues`).
