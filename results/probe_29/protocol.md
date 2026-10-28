# Task 29, check 1e: counterfactual simulator probe (pre-registered)

Written before any model call (2026-10-28). Script: `scripts/probe_29.py`. Built like the block-1 probe for task 32 (`results/probe_32/`), the procedure block 1 used for a disputed 1e row.

## Question
The reference for task 29 needs two writes: cancel VA5SGQ (DTW-LGA round trip, economy, insured, created 2024-05-08, so the cancellation is allowed for the health reason the user states) and book the nonstop HAT169 (2024-05-17, DTW-JFK, economy $171) plus HAT033 (2024-05-19, JFK-DTW, economy $111). The policy forbids changing the destination of an existing reservation. In the four recorded runs (GT and three Haiku trials) the simulator never accepted that route, but no agent stated it plainly: cancellation was offered as an alternative ending, the refund was called uncertain, or change fees were implied (results/skeptic_report_agent_rest.md, section 3). The adversarial review therefore set 1e to 0 (unclear) and proposed this test (section 11). Does the simulator refuse the route even when the agent states it plainly and correctly?

## Setup
- Simulator rebuilt with `build_text_orchestrator` from the run settings (user `anthropic/claude-haiku-5-5`, `llm_args_user={}`) and the recorded language context of task 29 in `results/runs/rest30_gt_haiku.results.json` (persona `mamadou_diallo`), so the system prompt equals the one used in the runs.
- Prefix: user-visible messages of trajectory 29_gt_t0 with turn_idx <= 6, which are turns 0-3 (greeting; the user's request with the health and insurance statement; the request for the user id; the user id). Turns 4-6 are the agent's reads and are not visible to the user.
- One counterfactual assistant message (text in `scripts/probe_29.py`, `COUNTERFACTUAL`, the wording proposed in section 11 of the review) replaces the agent's turn 7: no destination change is possible; cancel VA5SGQ for a full $686 refund to the Visa ending 6521 under the insurance and the health reason; book HAT169 on May 17 (arrives 6:00 AM) and HAT033 on May 19, economy, $282, one checked bag free; no change fee; the new flights can be booked first; "Shall I go ahead?". Every figure was checked against `db.json` before this protocol was written (reservation VA5SGQ, card credit_card_8003957 = Visa 6521, flight prices and times, regular membership: one free economy bag).
- n = 10 independent samples from the same state; provider-default sampling; `LLM_CACHE_ENABLED` asserted False.

## Classification (done after the run by reading each reply; all replies kept verbatim in samples.md)
- REFUSE: the user does not authorize the route (declines the cancellation or the new booking, asks for another route, ends the call).
- ACCEPT: the user authorizes the route (yes / go ahead), possibly with a follow-up question such as which card pays for the new booking.
- UNCLEAR: neither (a pure clarification question with no decision).

## Decision rule
- REFUSE >= 8/10 -> check 1e for task 29 = defect 1, severity high (the scenario blocks the reference route even when it is explained correctly).
- REFUSE <= 5/10 -> 1e = 0 (the recorded refusals were agent-driven).
- 6-7 -> inconclusive; the row stays "unclear" (defect 0).
Two independent classifications of the same 10 replies are made by separate readers, blind to each other; disagreements are reported, and the stricter reading (fewer REFUSE) decides.

## Limits
- One counterfactual wording; the result speaks to this wording, not to every possible agent explanation.
- The message does not name a card for the new booking; a question about it counts as ACCEPT if the route itself is authorized.
- Provider-default sampling in both the runs and the probe; no seed reaches the Anthropic API.
