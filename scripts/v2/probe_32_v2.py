"""Does the task-32 text fix work? Counterfactual simulator probe with the v2 scenario (block2/PLAN.md H4; design review D).

Same construction as scripts/probe_32.py (block 1): the user simulator is rebuilt with tau2's builder
from the recorded run settings and the recorded language context of task 32; the conversation prefix
is 32_haiku_t0 up to the user's two-step request (turn 16); ONE counterfactual assistant message
replaces the agent's next turn; N independent samples of the simulator's reply are saved verbatim and
classified afterwards (REFUSE / ACCEPT / UNCLEAR, same definitions as results/probe_32/protocol.md).

Two arms, pre-registered here before any call:
  A  "two_step"   the block-1 counterfactual (+$396 now, -$510 refund in step 2, net $114 back) with the v2 task text.
                  Rule: ACCEPT >= 8/10 -> the fix works (the reference path is scenario-compatible);
                        ACCEPT <= 5/10 -> it does not; 6-7 inconclusive.
  B  "step1_only" the agent quotes only step 1 (+$396) and asks for authorisation, with NO mention of a refund.
                  Rule: ACCEPT >= 8/10 -> the "net $100" clause over-corrects (the simulator accepts a charge above
                        its budget without a stated refund) and the wording must be tightened;
                        REFUSE >= 8/10 -> the clause behaves as intended; otherwise inconclusive.
The task used is the v2 task (block2/tasks_airline_v2.json); the prefix is the recorded one, whose user turns were
produced under the v1 text (the simulator's system prompt, which carries the scenario, is the v2 one).

Usage (inside tau2-bench, .env present):  uv run --no-sync python ../scripts/v2/probe_32_v2.py [--n 10] [--arm two_step|step1_only|both] [--dry]
Outputs: results/v2/probe_32_v2/<arm>_setup.json, <arm>_samples.json, <arm>_samples.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
OUT = ROOT / "results" / "v2" / "probe_32_v2"
TASK_ID = "32"
RUN_FILE = ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json"
PREFIX_LAST_TURN = 16

TWO_STEP = (
    "Here are the exact figures for the two-step change, confirmed from the system.\n\n"
    "Step 1: upgrade reservation OWZ4XL from basic economy to economy on the same flights "
    "(HAT202 and HAT232 on 2024-05-21). New price 3 x $306 = $918; you already paid $522; "
    "the difference of $396 is charged now to your Visa ending in 1777.\n\n"
    "Step 2: right after that, change the flights to the nonstop HAT041 in economy, 3 x $136 = $408. "
    "The reservation total drops from $918 to $408, and the $510 difference is refunded to the same "
    "Visa ending in 1777.\n\n"
    "Net result of both steps together: you receive $114 back, so overall nothing comes out of your pocket. "
    "The $396 charge happens first and the $510 refund follows in step 2.\n\n"
    "Do you want me to go ahead with step 1 now, the $396 upgrade on the Visa ending in 1777? Please reply yes or no."
)
STEP1_ONLY = (
    "Here are the exact figures for step 1, confirmed from the system.\n\n"
    "Step 1: upgrade reservation OWZ4XL from basic economy to economy on the same flights "
    "(HAT202 and HAT232 on 2024-05-21). New price 3 x $306 = $918; you already paid $522; "
    "the difference of $396 is charged now to your Visa ending in 1777.\n\n"
    "Do you want me to go ahead with step 1 now, the $396 upgrade on the Visa ending in 1777? Please reply yes or no."
)
ARMS = {"two_step": TWO_STEP, "step1_only": STEP1_ONLY}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--arm", choices=["two_step", "step1_only", "both"], default="both")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--tag", default="", help="suffix for the output files, e.g. v21 for the tightened wording")
    a = ap.parse_args()

    import scorer_v2 as s2
    import tasks_v2
    from tau2.config import LLM_CACHE_ENABLED
    from tau2.data_model.message import AssistantMessage
    from tau2.data_model.simulation import Results, TextRunConfig
    from tau2.runner.build import build_text_orchestrator
    from tau2.user.user_simulator_base import is_valid_user_history_message

    assert not LLM_CACHE_ENABLED
    if not a.dry:
        s2.require_clean("probe_32_v2")
    tasks_v2.register()
    results = Results.model_validate_json(RUN_FILE.read_text(encoding="utf-8"))
    sim = next(s for s in results.simulations if str(s.task_id) == TASK_ID and s.trial == 0)
    task_v1 = next(t for t in results.tasks if str(t.id) == TASK_ID)
    task = next(t for t in tasks_v2.get_tasks_v2(None) if t.id == TASK_ID)
    assert task.user_scenario.instructions.task_instructions != task_v1.user_scenario.instructions.task_instructions
    recorded_ctx = results.info.language_tasks[TASK_ID] if results.info.language_tasks else sim.language_context
    recorded_persona = getattr(getattr(recorded_ctx, "persona", None), "persona_id", None)

    config = TextRunConfig(
        domain="airline", task_set_name=tasks_v2.TASK_SET_NAME, task_split_name="base", task_ids=[TASK_ID], num_trials=1,
        agent="llm_agent", llm_agent="anthropic/claude-haiku-5-5", llm_args_agent={},
        user="user_simulator", llm_user="anthropic/claude-haiku-5-5", llm_args_user={}, seed=300, timeout=900,
    )
    # the recorded language context pins the v1 task digest, so the context is resolved afresh for the v2 task;
    # persona assignment is keyed by (seed, task id) and must come out identical to the recorded run
    orch = build_text_orchestrator(config, task, seed=sim.seed, language_context=None)
    user = orch.user
    persona = getattr(getattr(orch.language_context, "persona", None), "persona_id", None) if hasattr(orch, "language_context") else None
    if persona is None:
        from tau2.multilingual.runtime import task_context

        persona = getattr(task_context(config, task).persona, "persona_id", None)
    assert persona == recorded_persona, f"persona differs from the recorded run: {persona} vs {recorded_persona}"
    assert "$100 net" in user.system_prompt, "v2 scenario text not in the simulator prompt"
    history = [m for m in sim.messages if m.turn_idx is not None and m.turn_idx <= PREFIX_LAST_TURN and is_valid_user_history_message(m)]
    assert history[-1].role == "user" and "two separate steps" in (history[-1].content or "")

    OUT.mkdir(parents=True, exist_ok=True)
    arms = list(ARMS) if a.arm == "both" else [a.arm]
    for arm in arms:
        stem = f"{arm}_{a.tag}" if a.tag else arm
        cf = AssistantMessage(role="assistant", content=ARMS[arm], turn_idx=PREFIX_LAST_TURN + 1)
        meta = {"created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "arm": arm, "task_text": "v2.1" if a.tag else "v2", "task_instructions": task.user_scenario.instructions.task_instructions,
                "bench_commit": results.info.git_commit, "provenance": s2.provenance(), "user_llm": config.llm_user, "persona": persona,
                "prefix_source": f"32_haiku_t0, user-visible messages with turn_idx <= {PREFIX_LAST_TURN}", "counterfactual": ARMS[arm], "n": a.n}
        print(f"[{arm}] persona={persona} prefix={len(history)} msgs; system prompt chars={len(user.system_prompt)}")
        if a.dry:
            continue
        (OUT / f"{stem}_setup.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        samples, tin, tout = [], 0, 0
        for i in range(a.n):
            state = user.get_init_state(deepcopy(history))
            msg, _ = user.generate_next_message(deepcopy(cf), state)
            u = msg.usage or {}
            tin += int(u.get("prompt_tokens") or 0)
            tout += int(u.get("completion_tokens") or 0)
            samples.append({"i": i, "content": msg.content, "usage": u})
            print(f"  [{i}] {len(msg.content or '')} chars")
        cost = tin * 0.10 / 1e6 + tout * 0.50 / 1e6
        (OUT / f"{stem}_samples.json").write_text(json.dumps({"setup": meta, "samples": samples, "tokens_in": tin, "tokens_out": tout, "cost_estimate_usd": round(cost, 4)}, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        md = [f"# Task 32 v2 probe, arm {arm}: simulator replies", "", f"n={a.n}; persona {persona}; tokens in/out {tin}/{tout}; cost estimate ${cost:.4f}", "",
              "## Counterfactual assistant message", "", ARMS[arm], "", "## Replies (verbatim)", ""]
        for s in samples:
            md += [f"### sample {s['i']}", "", s["content"] or "", ""]
        (OUT / f"{stem}_samples.md").write_text("\n".join(md), encoding="utf-8")
        print(f"  tokens in/out {tin}/{tout}; cost estimate ${cost:.4f} -> results/v2/probe_32_v2/{stem}_samples.md")
    if a.dry:
        print(user.system_prompt[user.system_prompt.find("$100 net") - 300: user.system_prompt.find("$100 net") + 300])
        print("[dry] no model call")
    return 0


if __name__ == "__main__":
    sys.exit(main())
