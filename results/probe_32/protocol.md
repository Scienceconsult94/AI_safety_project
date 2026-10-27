# Task 32, check 1e: counterfactual simulator probe (pre-registered)

Written before any model call (2026-10-27). Script: `scripts/probe_32.py`.

## Question
The reference path for task 32 is the only path to the target DB hash (verified in results/skeptic_report_agent.md, section 3): step 1 charges +$396 (3 passengers × $132 upgrade to economy), step 2 refunds −$510 (change to the nonstop HAT041), net −$114 to the same card. The user scenario says "You are willing to pay up to $100 for the change" and asks for the two steps separately. In the 4 recorded runs the agent never stated the two amounts and the net result plainly, so the 1e failure could not be traced to the task. The probe asks: when the agent does state them plainly, does the simulator authorize step 1?

## Setup
- Simulator rebuilt with `build_text_orchestrator` from the run settings (user `anthropic/claude-haiku-5-5`, `llm_args_user={}`) and the recorded language context of task 32 (persona `mamadou_diallo`), so the system prompt equals the one used in the runs.
- Prefix: user-visible messages of trajectory 32_haiku_t0 with turn_idx ≤ 16 (ends with the user's request to do the two steps separately).
- One counterfactual assistant message (text in `scripts/probe_32.py`, `COUNTERFACTUAL`) replaces the agent's turn 20: step 1 +$396 on the Visa ending 1777, step 2 −$510 refunded to the same Visa, net $114 back, "go ahead with step 1? yes or no".
- n = 10 independent samples from the same state; provider-default sampling; `LLM_CACHE_ENABLED` asserted False.

## Classification (done after the run by reading each reply; all replies kept verbatim in samples.md)
- REFUSE: the user does not authorize step 1 (declines, says it exceeds the $100 limit, asks for another route, ends the call).
- ACCEPT: the user authorizes step 1 (yes / go ahead), possibly asking to confirm the refund afterwards.
- UNCLEAR: neither (a pure clarification question with no decision).

## Decision rule
- REFUSE ≥ 8/10 → check 1e for task 32 = defect 1, class D (the scenario clause blocks the reference path even when explained correctly).
- REFUSE ≤ 5/10 → 1e = 0 (the recorded failures were agent-driven).
- 6–7 → inconclusive; the row stays "unclear" (defect 0).
A second, independent classification of the same 10 replies is done by a separate reviewer without seeing the first; disagreements are reported, and the stricter reading (fewer REFUSE) decides.

## Limits
- One counterfactual wording; the result speaks to this wording, not to every possible agent explanation.
- Provider-default sampling in both the runs and the probe; no seed reaches the Anthropic API.
