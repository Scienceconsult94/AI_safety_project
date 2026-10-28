# No-op tasks under v2: the 2b probe and a refusal bot

23 tasks whose empty trajectory passes under v1 (noop_scan_v2.csv). Provenance: {"overlay_commit": "a4f86e7", "overlay_dirty": false, "judge_model": "anthropic/claude-haiku-5-5", "judge_view": "with_tool_calls"}.

| trajectory | passes under v2 | of |
|---|---|---|
| greeting + one user turn (block-1 2b probe) | 0 | 23 |
| refusal bot (no tool calls, two refusals) | 14 | 23 |
| refusal bot, process-class assertions excluded | 17 | 23 |

Judge calls 0 (re-asks 0), tokens in/out 0/0, own cost estimate $0.000. Undetermined verdicts: 0.

| task | refusal bot | unmet assertions |
|---|---|---|
| 0 | 1 |  |
| 1 | 1 |  |
| 2 | 0 | Agent should check that the flight was indeed delayed.; Agent should detect that the number of passengers on the delayed fligh |
| 4 | 0 | Agent should realize that flight was not cancel and not in business cl |
| 5 | 0 | Agent identifies that user is not a Gold member but a Regular member. |
| 6 | 1 |  |
| 9 | 0 | Check that Agent searched for direct flights between JFK and MCO on Ma |
| 10 | 1 |  |
| 13 | 0 | Agent correctly identified that the changes requested by the user cann |
| 26 | 0 | Agent does not offer the refund because reservation doesn't meet polic |
| 27 | 0 | Agent confirms that flight HAT039 from ATL to SEA on 2024-05-15 has be; Agent confirms that user can receive compensation because he has Silve |
| 28 | 1 |  |
| 31 | 1 |  |
| 34 | 1 |  |
| 36 | 1 |  |
| 38 | 0 | Agent verifies that the flight was delayed.; Agent verifies the number of passengers in the reservation. |
| 41 | 0 | Agent checks all reservations. |
| 43 | 1 |  |
| 45 | 1 |  |
| 46 | 1 |  |
| 47 | 1 |  |
| 48 | 1 |  |
| 49 | 1 |  |

Reading: under v1 all of these tasks score 1.0 for any agent that changes nothing. Under v2 the 2b probe fails by rule; the refusal bot passes exactly where every assertion is of the 'does not do X' kind, which tau2's documentation calls the intended τ-bench outcome (docs/evaluation.md). v2 is therefore a stricter alternative protocol for those tasks, not a repair of a bug.
