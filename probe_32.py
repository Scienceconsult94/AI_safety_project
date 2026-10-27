"""Counterfactual user-simulator probe for task 32 (check 1e triage).

Question: does the scenario clause "willing to pay up to $100 for the change" make the user simulator refuse
step 1 of the reference path (+$396 upgrade, then -$510 refund in step 2, net -$114) even when the agent
states the two steps and the net result plainly? In the recorded runs no agent ever did, so 1e stayed "unclear".

Design (pre-registered before any call, see results/probe_32/protocol.md):
- Simulator rebuilt with tau2's own builder (build_text_orchestrator) from the recorded run settings and the
  recorded language context of task 32 (persona mamadou_diallo), so the system prompt is the one used in the runs.
- Conversation prefix: the user-visible messages of 32_haiku_t0 up to and including the user's two-step request
  (turn 16). Then ONE counterfactual assistant message (COUNTERFACTUAL below) replaces the agent's turn 20.
- N independent samples of the simulator's reply from the same state (provider-default sampling, no seed,
  LLM cache off). Replies are saved verbatim; classification is done afterwards by reading them.
- Classes: REFUSE = does not authorize step 1 (declines / says it exceeds the $100 limit / asks for another route);
  ACCEPT = authorizes step 1 (yes / go ahead, possibly with a request to confirm the refund);
  UNCLEAR = neither (pure clarification, no decision).
- Cutoffs: REFUSE >= 8/10 -> 1e = 1 (class D, scenario clause blocks the reference); REFUSE <= 5/10 -> 1e = 0;
  6-7 -> inconclusive, row stays "unclear".
Usage (from inside tau2-bench, .env present):  uv run --no-sync python ../probe_32.py [--n 10] [--dry]
--dry builds everything and prints the prompt/prefix without calling the model.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "probe_32"
TASK_ID = "32"
RUN_FILE = ROOT / "results" / "runs" / "sample20_pass3_haiku.results.json"
PREFIX_LAST_TURN = 16  # user's two-step request in 32_haiku_t0

COUNTERFACTUAL = (
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    from tau2.config import LLM_CACHE_ENABLED
    from tau2.data_model.message import AssistantMessage
    from tau2.data_model.simulation import Results, TextRunConfig
    from tau2.user.user_simulator_base import is_valid_user_history_message
    from tau2.registry import registry
    from tau2.runner.build import build_text_orchestrator

    assert not LLM_CACHE_ENABLED, "LLM cache must be off for independent samples"

    results = Results.model_validate_json(RUN_FILE.read_text(encoding="utf-8"))
    sim = next(s for s in results.simulations if str(s.task_id) == TASK_ID and s.trial == 0)
    task = next(t for t in results.tasks if str(t.id) == TASK_ID)
    language_context = results.info.language_tasks[TASK_ID] if results.info.language_tasks else sim.language_context

    config = TextRunConfig(
        domain="airline", task_split_name="base", task_ids=[TASK_ID], num_trials=1,
        agent="llm_agent", llm_agent="anthropic/claude-haiku-5-5", llm_args_agent={},
        user="user_simulator", llm_user="anthropic/claude-haiku-5-5", llm_args_user={},
        seed=300, timeout=900,
    )
    orch = build_text_orchestrator(config, task, seed=sim.seed, language_context=language_context)
    user = orch.user
    persona = getattr(getattr(language_context, "persona", None), "persona_id", None)

    history = [m for m in sim.messages if m.turn_idx is not None and m.turn_idx <= PREFIX_LAST_TURN
               and is_valid_user_history_message(m)]
    assert history[-1].role == "user" and "two separate steps" in (history[-1].content or ""), history[-1]
    cf = AssistantMessage(role="assistant", content=COUNTERFACTUAL, turn_idx=PREFIX_LAST_TURN + 1)

    OUT.mkdir(parents=True, exist_ok=True)
    meta = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bench_commit": results.info.git_commit if hasattr(results.info, "git_commit") else None,
        "user_llm": config.llm_user, "llm_args_user": config.llm_args_user, "persona": persona,
        "prefix_source": "32_haiku_t0 (sample20_pass3_haiku), user-visible messages with turn_idx <= %d" % PREFIX_LAST_TURN,
        "prefix_turns": [(m.turn_idx, m.role) for m in history],
        "counterfactual": COUNTERFACTUAL, "n": a.n,
    }
    (OUT / "setup.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"persona={persona} prefix={len(history)} msgs (turns {[m.turn_idx for m in history]})")
    print("system prompt chars:", len(user.system_prompt))
    if a.dry:
        print(user.system_prompt[:1200])
        print("...\n[dry] no model call")
        return 0

    samples = []
    tin = tout = 0
    for i in range(a.n):
        state = user.get_init_state(deepcopy(history))
        msg, _ = user.generate_next_message(deepcopy(cf), state)
        u = msg.usage or {}
        tin += int(u.get("prompt_tokens") or 0)
        tout += int(u.get("completion_tokens") or 0)
        samples.append({"i": i, "content": msg.content, "usage": u, "cost": msg.cost})
        print(f"[{i}] {len(msg.content or '')} chars")
    cost = tin * 0.10 / 1e6 + tout * 0.50 / 1e6
    out = {"setup": meta, "samples": samples, "tokens_in": tin, "tokens_out": tout, "cost_estimate_usd": round(cost, 4)}
    (OUT / "samples.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    md = ["# Task 32 counterfactual probe: simulator replies", "",
          f"n={a.n}; user model {config.llm_user}; persona {persona}; tokens in/out {tin}/{tout}; cost estimate ${cost:.4f}", "",
          "## Counterfactual assistant message", "", COUNTERFACTUAL, "", "## Replies (verbatim)", ""]
    for s in samples:
        md += [f"### sample {s['i']}", "", s["content"] or "", ""]
    (OUT / "samples.md").write_text("\n".join(md), encoding="utf-8")
    print(f"tokens in/out {tin}/{tout}; cost estimate ${cost:.4f}; -> results/probe_32/samples.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
