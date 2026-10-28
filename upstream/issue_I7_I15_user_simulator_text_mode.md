# user simulator: the text-mode guidelines lack three scenario-adherence rules that the voice guidelines carry; simulator deviations decide many failures and flips

| field | value |
|---|---|
| audit ids | I7, I15 |
| type | simulator |
| domain | all text-mode runs (measured in airline and retail) |
| severity | medium |
| status | draft, not filed |

## Summary

The text-mode scaffolds `_TEXT_PLAIN` and `_TEXT_TOOLS` in `src/tau2/user/guidelines.py` lack three rules that both voice scaffolds carry: do not end the conversation prematurely (agreeing to an action is not the same as the action being completed), verify that all scenario items were addressed before ending, and answer "no preference" when asked for a preference that the scenario does not give. In the audit's runs with `claude-haiku-5-5` as the user simulator, deviations of exactly these kinds (stopping or accepting a transfer with the instructed request undone, withholding an instruction at its trigger, inventing a preference or a constraint) account for a large share of task failures and of run-to-run flips, so the pass rate measures the agent and the simulator together.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/user/guidelines.py`: `_VOICE_PLAIN` lines 72-78 and `_VOICE_TOOLS` lines 144-150 ("Scenario Adherence"); `_TEXT_PLAIN` lines 203-224 and `_TEXT_TOOLS` lines 226-259 ("Core Principles", "Task Completion"); `render_simulation_guidelines` lines 283-297 selects the scaffold by mode.

The voice scaffolds contain (lines 75-78 of `_VOICE_PLAIN`; the same in `_VOICE_TOOLS`, lines 147-150, with "or don't know" added to the preference rule):

```text
- **You only know what is explicitly stated in the scenario instructions.** If a piece of information is not provided, you do not know it — even if it is something a real person would typically know about themselves (e.g., zip code, address, order ID, size/color preferences, past order details). When asked, say you don't know or don't remember.
- Never fabricate, guess, or infer information not explicitly provided in the scenario instructions. If asked for a preference (e.g., color, size, payment method) that is not in your instructions, say you have no preference.
- **Do not end the conversation prematurely.** Agreeing to an action is not the same as the action being completed. If the agent offers to do something (e.g., cancel an order, process a refund), wait for the agent to confirm it is done before ending the conversation.
- **Before ending the conversation, verify that ALL items in your scenario instructions have been addressed.** If your instructions include multiple requests, questions, or tasks, make sure every single one has been completed — do not stop after only some of them are resolved.
```

The text scaffolds have only (lines 209-211 of `_TEXT_PLAIN`):

```text
- Strictly follow the scenario instructions you have received.
- When providing addresses or other multi-part entity values from the task, preserve the order of their components exactly as given; do not rearrange them to match local conventions unless the task explicitly instructs a different order.
- Never make up or hallucinate information not provided in the scenario instructions. Information that is not provided in the scenario instructions should be considered unknown or unavailable.
```

and, under "Task Completion", "If the instruction goal is satisified, generate the '###STOP###' token to end the conversation." (the typo "satisified" is in both text scaffolds).

## Reproduction

The template difference, without a model call (`uv run --no-sync python repro_I15.py` from the repository root):

```python
"""I15: the text-mode user-simulator guidelines lack three scenario-adherence rules that both voice
templates carry (src/tau2/user/guidelines.py).

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I15.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.user.guidelines import default_persona, render_simulation_guidelines  # noqa: E402

RULES = {
    "do not end prematurely": "Do not end the conversation prematurely.",
    "verify ALL items before ending": "Before ending the conversation, verify that ALL items",
    "no stated preference -> say so": "that is not in your instructions, say you have no preference",
}
rendered = {}
for mode in ("text", "voice"):
    persona = default_persona(mode)
    for use_tools in (False, True):
        rendered[f"{mode}, tools={use_tools}"] = render_simulation_guidelines(persona, use_tools=use_tools)

width = max(len(k) for k in RULES)
print(" " * (width + 2) + " | ".join(rendered))
for name, text in RULES.items():
    print(f"{name:<{width}}  " + " | ".join(f"{str(text in g):<{len(k)}}" for k, g in rendered.items()))
```

Output:

```text
                                text, tools=False | text, tools=True | voice, tools=False | voice, tools=True
do not end prematurely          False             | False            | True               | True
verify ALL items before ending  False             | False            | True               | True
no stated preference -> say so  False             | False            | True               | True
```

The behavioural findings below come from agent runs and need model calls; they are not reproduced by a snippet. Per-task evidence is in the trajectory files listed at the end.

## Observed vs expected

Observed in the audit's runs (`claude-haiku-5-5` as agent and as user simulator, provider-default sampling, 3 trials per task plus one ground-truth-agent run, i.e. an agent that sees the reference actions):

- Airline, 20 sampled tasks: the simulator departs from its scenario in 7 of 20 tasks (tasks 7, 11, 16, 19, 22, 23, 32; every row confirmed by an adversarial review). Examples: it invents a "change of plan" against "You are sick" (task 7); it reads "original payment method" as "not the gift card" when the reservation was paid by gift card (tasks 11 and 16); it asks the agent to rebook against "You will book the flight again yourself later" (task 19); it withholds the instructed three-reservation idea at its trigger and raises it turns later (task 23); it invents "I didn't book this for anyone else" (task 32). Flips between trials trace to the simulator in 3 tasks (8, 11, 19).
- Retail, all 114 tasks: the trajectory review attributes 12 of the 23 ground-truth-agent failures, and the flip of 23 of the 32 unstable tasks (1 or 2 of 3 trials passed), to the simulator; simulator deviations were filed on 36 of the 45 reviewed tasks. These retail run rows were not adversarially reviewed, and the threshold for a deviation differs between reviewer batches.

Expected: the simulator follows its scenario; it does not end or accept a transfer while an instructed request is pending, and it does not invent preferences or facts.

A related design point, not a deviation: in the English pack the persona is assigned by caller gender (`assign_persona`, `src/tau2/multilingual/runtime.py` lines 568-581). The persona `priya_patil` (`data/tau2/multilingual/en/pack.yaml` lines 83-102) scripts early escalation ("When you're not getting somewhere fast, asking for a supervisor or a timeline early is characteristic", "Can I just talk to someone who can actually fix this"). These phrases appear verbatim in airline tasks 8, 19 and 44, where the scenario gives no instruction for a predictable refusal, and the conversations end with in-scope work pending.

## Impact on scores

In retail, the simulator explains more ground-truth failures (12 of 23) than the task and scoring defects do (8 of 23), under the caveat above. A change to the simulator model or to its scaffold moves the pass rate without any change in the agent; text and voice runs use different rules for the same task.

## Suggested fix

- Port the three rules into `_TEXT_PLAIN` and `_TEXT_TOOLS` (and fix "satisified"). This changes the simulator prompt, so results before and after are not comparable; a version bump of `GUIDELINE_TEMPLATE_VERSION` (line 15) would record it.
- Report simulator-attributed failures separately, or validate simulator fidelity per task (for example, replay a fixed agent and check the simulator's turns against the scenario).
- For scenarios that predictably meet a refusal, state the fallback in the scenario, so that persona scripts do not decide the outcome.

## Evidence (audit repository)

- Airline: `results/review_agent.csv` (rows 5c, 5d), `results/review_agent_overrides.csv`, `results/skeptic_report_agent.md` (sections 1, 2 and 6), `results/trajectories/*.md`, `audit_log.csv` rows 5c and 5d.
- Retail: `results/retail/review_agent_A.md` to `review_agent_E.md` and the matching `.csv` files, `retail/audit_log.csv` rows 5c, 5d, 1e, `retail/PLAN.md` (deviation of 2026-10-28, reviewer consistency), `report.md` section 5.3.
- `upstream/repro/I15.py`.
