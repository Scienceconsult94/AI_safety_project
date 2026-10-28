"""Counterfactual user-simulator probe for task 29 (check 1e triage), built like scripts/probe_32.py.

Question: does the task-29 scenario make the user simulator refuse the reference route (cancel VA5SGQ for a full
refund under the travel insurance, then book the nonstop HAT169 + HAT033 to and from JFK) even when the agent states
that route plainly and correctly? In the recorded runs no agent did, so 1e was set to 0 (unclear) by the adversarial
review of the rest agent-run rows (results/skeptic_report_agent_rest.md, sections 3 and 11).

Design (pre-registered before any call, see results/probe_29/protocol.md):
- Simulator rebuilt with tau2's own builder (build_text_orchestrator) from the recorded run settings and the
  recorded language context of task 29, so the system prompt is the one used in the runs.
- Conversation prefix: the user-visible messages of 29_gt_t0 (rest30_gt_haiku) up to and including turn 6. Then ONE
  counterfactual assistant message (COUNTERFACTUAL below, the wording proposed in section 11 of that report) replaces
  the agent's turn 7.
- N independent samples of the simulator's reply from the same state (provider-default sampling, no seed,
  LLM cache off). Replies are saved verbatim; classification is done afterwards by reading them.
- Classes: REFUSE = does not authorize the route (declines the cancellation or the new booking, asks for another
  route, ends the call); ACCEPT = authorizes it (yes / go ahead, possibly with a question such as which card pays);
  UNCLEAR = neither (a pure clarification question with no decision).
- Cutoffs: REFUSE >= 8/10 -> 1e = 1 (the scenario blocks the reference); REFUSE <= 5/10 -> 1e = 0;
  6-7 -> inconclusive, the row stays "unclear" (defect 0).
Usage (from inside tau2-bench, .env present):  uv run --no-sync python ../scripts/probe_29.py [--n 10] [--dry]
--dry builds everything and prints the prompt/prefix without calling the model.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (this file lives in scripts/)
OUT = ROOT / "results" / "probe_29"
TASK_ID = "29"
RUN_FILE = ROOT / "results" / "runs" / "rest30_gt_haiku.results.json"
PREFIX_LAST_TURN = 6  # the user's request, the health and insurance statement and the reads of 29_gt_t0

COUNTERFACTUAL = (
    "I can't change VA5SGQ to JFK, because a change cannot alter the destination. Because you have travel "
    "insurance and a health reason, I can cancel VA5SGQ for a full refund of $686 to your Visa ending 6521, and "
    "book new nonstop flights HAT169 on May 17 (arrives 6:00 AM) and HAT033 on May 19, economy, $282, with your "
    "one checked bag free. There is no change fee. I can book the new flights first, so the fares are locked. "
    "Shall I go ahead?"
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
    from tau2.runner.build import build_text_orchestrator

    assert not LLM_CACHE_ENABLED, "LLM cache must be off for independent samples"

    results = Results.model_validate_json(RUN_FILE.read_text(encoding="utf-8"))
    sim = next(s for s in results.simulations if str(s.task_id) == TASK_ID and s.trial == 0)
    task = next(t for t in results.tasks if str(t.id) == TASK_ID)
    language_context = results.info.language_tasks[TASK_ID] if results.info.language_tasks else sim.language_context

    config = TextRunConfig(
        domain="airline", task_split_name="base", task_ids=[TASK_ID], num_trials=1,
        agent="llm_agent_gt", llm_agent="anthropic/claude-haiku-5-5", llm_args_agent={},
        user="user_simulator", llm_user="anthropic/claude-haiku-5-5", llm_args_user={},
        seed=300, timeout=900,
    )
    orch = build_text_orchestrator(config, task, seed=sim.seed, language_context=language_context)
    user = orch.user
    persona = getattr(getattr(language_context, "persona", None), "persona_id", None)

    history = [m for m in sim.messages if m.turn_idx is not None and m.turn_idx <= PREFIX_LAST_TURN
               and is_valid_user_history_message(m)]
    assert history[-1].role == "user", history[-1]
    cf = AssistantMessage(role="assistant", content=COUNTERFACTUAL, turn_idx=PREFIX_LAST_TURN + 1)

    OUT.mkdir(parents=True, exist_ok=True)
    meta = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bench_commit": results.info.git_commit if hasattr(results.info, "git_commit") else None,
        "user_llm": config.llm_user, "llm_args_user": config.llm_args_user, "persona": persona,
        "prefix_source": "29_gt_t0 (rest30_gt_haiku), user-visible messages with turn_idx <= %d" % PREFIX_LAST_TURN,
        "prefix_turns": [(m.turn_idx, m.role) for m in history],
        "counterfactual": COUNTERFACTUAL, "n": a.n,
    }
    print(f"persona={persona} prefix={len(history)} msgs (turns {[m.turn_idx for m in history]})")
    print("system prompt chars:", len(user.system_prompt))
    if a.dry:
        for m in history:
            print(f"--- turn {m.turn_idx} {m.role}: {(m.content or '')[:400]}")
        print("...\n[dry] no model call, nothing written")
        return 0
    (OUT / "setup.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

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
    md = ["# Task 29 counterfactual probe: simulator replies", "",
          f"n={a.n}; user model {config.llm_user}; persona {persona}; tokens in/out {tin}/{tout}; cost estimate ${cost:.4f}", "",
          "## Counterfactual assistant message", "", COUNTERFACTUAL, "", "## Replies (verbatim)", ""]
    for s in samples:
        md += [f"### sample {s['i']}", "", s["content"] or "", ""]
    (OUT / "samples.md").write_text("\n".join(md), encoding="utf-8")
    print(f"tokens in/out {tin}/{tout}; cost estimate ${cost:.4f}; -> results/probe_29/samples.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
