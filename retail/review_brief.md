# Static review brief — retail tasks (one batch of ~10 tasks per reviewer)

You are a static reviewer of tasks in the retail domain of tau2-bench v2.0.0 (commit `989d3285ae669e49503324bdb9981bf14fccedeb`). The benchmark scores an agent by (a) whether the final database state equals the state produced by replaying the task's reference actions and (b) for tasks with `nl_assertions`, whether an LLM judge says each assertion is met. `communicate_info` is never scored in this domain. Your job is to read each assigned task and decide, check by check, whether the task as written has a defect of the kind the checklist defines. Evidence first; no speculation.

## Inputs (read only these)

- `retail/checklist.md` — the retail reading of every check (authoritative for this review), then `checklist.md` — the full check definitions, methods, severities (airline wording; use the retail reading where they differ).
- `retail/PLAN.md` — rules, in particular the dated clarification on 1b/1c (intended negative steps) and on 2m.
- `results/retail/task_cards/task_<id>.md` for your task ids — everything about the task: scenario, reference actions, assertions, the DB records involved (user with payment methods and orders; orders with items, status, payment history; products with all variants, availability and prices), and the static-scan line.
- `tau2-bench/data/tau2/domains/retail/policy.md` — the agent policy (136 lines).
- `results/retail/static_scan.csv` — your tasks' rows (flags for 1b, 1c, 1d, 3d, 4d).
- `results/retail/probe_2h.csv`, `results/retail/probe_2d.csv` — rows for your tasks, if any.
- `tau2-bench/data/tau2/domains/retail/db.json` — only to verify a DB fact the card does not show (grep or a short read-only Python snippet). `tau2-bench/src/tau2/domains/retail/tools.py` — only to verify what a tool checks or stores.

Do not read other files under `results/` (other reviewers' outputs, airline review files), nothing under `tau2-bench/data/tau2/domains/retail/task_issues/`, and do not open `tasks.json` (the cards contain the task; the file carries fields that must stay hidden from reviewers).

## Checks to decide, one row per (task, check)

Always: **1d, 2k, 2m, 4a, 4b, 4c, 4d, 4e**.
Only when the scan or a probe flags the task: **1b** (`replay_errors` > 0), **1c** (`write_noop_ids` non-empty), **2h** (`n_hash_differs` > 0 in probe_2h.csv), **2d** (a row with `check=2d` and `hash_equals_gold=1` in probe_2d.csv), **2e** (rows with `check=2e` in probe_2d.csv).

Readings and severities (from `retail/checklist.md`):
- 1b/1c (high when defect): a reference action that raises, or a WRITE that leaves the DB unchanged, is a defect only when the scenario does **not** set up that failure. A lookup with an e-mail or order id the scenario deliberately gives wrong is an intended negative step → defect=0, note "intended negative step". A WRITE that fails for a reason the scenario does not anticipate (e.g. insufficient gift-card balance), so the scored target state is not the state the author meant → defect=1.
- 1d (high): a value the reference needs is neither stated in the scenario nor reachable by READ tools from what is stated (`find_user_id_by_*`, `get_user_details` → orders, `get_order_details`, `get_product_details` → variants). Values only in `unknown_info` do not count as stated.
- 2k (medium): a requirement stated only in `communicate_info` (never scored) that no reward-gating `nl_assertion` and no DB change covers. Mirror case (an assertion that only restates the DB change) → defect=0, mention in note.
- 2m (medium): the task is *about* a process requirement of the policy that leaves no DB trace (authenticate before acting; explicit "yes" before each write; deny requests for another user; one exchange/modification per order) — e.g. the scenario makes the user refuse authentication, push for an action without confirmation, or ask about another user's order — and no `nl_assertion` names that requirement, so the scorer cannot see whether the agent followed it. Otherwise defect=0 (the benchmark-level row covers the general gap).
- 2h (medium): reorderings that change the hash are *independent* writes the scenario allows in either order (defect) vs dependent writes (same order, same user address written twice → the last wins) → defect=0.
- 2d (high): the substitution that leaves the hash unchanged is a genuinely wrong solution (breaks the request or the policy) → defect; if it is the same value by another route (e.g. the requested address equals the DB address) → defect=0, explain.
- 2e: defect=0 unless a *policy-violating* intermediate write is hidden; always note that the end-state comparison hides an earlier wrong address write.
- 4a (medium): the reference changes something the user did not ask for, omits a permitted change the user asked for, or uses other values (items, variants, payment method, address, reason). Check the variant options against the product list in the card.
- 4b (medium; high if no compliant trajectory reaches the target): each WRITE against policy.md — status rules (pending/delivered), allowed cancel reasons, refund destination for returns (original method or an existing gift card), gift-card balance for price differences, one modify/exchange per order, same-product variants only.
- 4c (medium): a choice the scenario leaves open (payment method for a refund or a difference, which variant when several fit, which orders) that the reference fixes to one of several compliant end states.
- 4d (medium; high if it blocks the reference path): a scenario fact that contradicts the DB (name, zip, e-mail, order id, status, item, price). Deliberate wrong facts that the scenario sets up as the user's mistake are not defects (say so in the note).
- 4e (medium): an `nl_assertion` or `description` that contradicts the reference or the DB (wrong amount, wrong count, wrong product fact). Recompute amounts from the card's prices (refund = sum of returned item prices; exchange difference = new minus old; cancel refund = order total). State the computation in the evidence.

When unsure, defect=0 and a note that starts with "uncertain:" and says what would settle it. Do not inflate; do not pad.

## Output

1. `results/retail/review_batch_<N>.csv` — header exactly `task_id,check,defect,severity,evidence,note`; one row per (task, check) decided; `severity` empty when defect=0, else high/medium/low; `evidence` names the card section or field, the policy line, the probe row or the computed number that reproduces the finding; UTF-8, RFC-4180 quoting (quote fields that contain commas or quotes).
2. `results/retail/review_batch_<N>.md` — a short per-task paragraph: the request in one sentence, the computation if any, each check's verdict with the reason, as compact as possible.

Write in English, impersonally (no first person, no names of people, no mention of which model or tool produced the review). Return in your final message: the list of defect=1 rows (task, check, severity, one line each) and anything you could not decide.
