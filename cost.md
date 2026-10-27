# API cost log — tau2-bench airline audit

Hard stop: **$30.00** cumulative. LiteLLM may not know prices for new Anthropic models, so every row is reconciled against the Anthropic Console figure; the Console figure is authoritative.

| date (PT) | run | models (agent / user / judge) | tasks x trials | litellm cost (USD) | console cost (USD) | cumulative (console, USD) | note |
|---|---|---|---|---|---|---|---|
| 2026-10-27 | (none yet — `.env` absent, no API calls made) | — | — | 0.00 | 0.00 | 0.00 | static work only |
| 2026-10-27 | `run_pilot.ps1`, attempt 1 (`pilot_5_haiku_FAILED_temperature_2026-10-27`) | haiku-5-5 / haiku-5-5 / — | 5 x 1 | 0.00 | pending | pending | 45 requests rejected with HTTP 400 (`temperature` not accepted by the model); 5/5 `infrastructure_error`, nothing evaluated; rejected requests carry no usage |
| 2026-10-27 | `run_pilot.ps1`, attempt 2 (`pilot_5_haiku`), `--agent-llm-args {} --user-llm-args {}` | haiku-5-5 / haiku-5-5 / — | 5 x 1 | 0.0156 (user only; agent_cost is None in results.json) | pending | pending | own estimate from usage at $0.10/$0.50 per MTok, cache ignored: agent 582,120 in / 14,068 out = $0.065; user 123,391 in / 6,532 out = $0.016; total ≈ $0.08 (upper bound) |
