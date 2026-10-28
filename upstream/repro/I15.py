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
