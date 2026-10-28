"""Adversarial checks of scorer v2 (read-only; every model call is blocked).

Run from inside tau2-bench with the tau2 venv:
  uv run --no-sync python <this file>
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

os.environ["PYTHONUTF8"] = "1"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["LOGURU_LEVEL"] = "ERROR"

ROOT = Path(__file__).resolve().parents[2]  # repository root
sys.path.insert(0, str(ROOT / "scripts" / "v2"))

import scorer_v2 as s2  # noqa: E402


def _blocked(*a, **k):
    raise RuntimeError("MODEL CALL BLOCKED")


# block every path to a model
s2.generate = _blocked
import tau2.utils.llm_utils as lu  # noqa: E402

lu.generate = _blocked
import tau2.evaluator.evaluator_communicate as ecm  # noqa: E402

ecm.generate = _blocked
import tau2.evaluator.evaluator_nl_assertions as enl  # noqa: E402

enl.generate = _blocked
try:
    import litellm  # noqa: E402

    litellm.completion = _blocked
    litellm.acompletion = _blocked
except Exception:  # noqa: BLE001
    pass

from loguru import logger  # noqa: E402

logger.remove()
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation  # noqa: E402
from tau2.orchestrator.modes import CommunicationMode  # noqa: E402
from tau2.registry import registry  # noqa: E402

s2.install()
RUNS = ROOT / "results" / "runs"
gt = Results.load(RUNS / "sample20_gt_haiku.results.json")
hk = Results.load(RUNS / "sample20_pass3_haiku.results.json")
comm_scoring = gt.info.effective_communicate_scoring
print("effective_communicate_scoring:", comm_scoring.model_dump(mode="json"))
T1 = {t.id: t for t in gt.tasks}
T1.update({t.id: t for t in hk.tasks})


def ev(sim, task):
    return evaluate_simulation(
        simulation=sim, task=task, evaluation_type=EvaluationType.ALL, solo_mode=False, domain="airline",
        mode=CommunicationMode.HALF_DUPLEX, env_kwargs=None, strict_replay=False, communicate_scoring=comm_scoring,
    )


def summary(ri):
    comm = None
    if ri.communicate_checks:
        comm = [(c.info, c.met) for c in ri.communicate_checks]
    nl = None
    if ri.nl_assertions:
        nl = [(a.nl_assertion[:40], a.met) for a in ri.nl_assertions]
    return f"reward={ri.reward} db_match={ri.db_check.db_match if ri.db_check else None} comm={comm} nl={nl}"


def find_sim(res, task_id, trial=0):
    return next(s for s in res.simulations if s.task_id == task_id and s.trial == trial)


def run_switches(label, sim, task, configs=((0, 0, 0), (1, 0, 0), (0, 1, 0))):
    for h, c, n in configs:
        s2.SWITCHES.set(bool(h), bool(c), bool(n))
        try:
            ri = ev(sim, task)
            print(f"  [{label}] hash={h} comm={c} nl={n}: {summary(ri)}")
        except Exception as e:  # noqa: BLE001
            print(f"  [{label}] hash={h} comm={c} nl={n}: ERROR {e!r}")
    s2.SWITCHES.set(False, False, False)


print("\n=== E1a: task 8 (GT t0, passing) - passengers reversed inside the recorded book_reservation call ===")
sim = find_sim(gt, "8")
run_switches("orig", sim, T1["8"])
sim2 = sim.model_copy(deep=True)
n_mod = 0
for m in sim2.messages:
    if isinstance(m, AssistantMessage) and m.tool_calls:
        for tc in m.tool_calls:
            if tc.name == "book_reservation":
                tc.arguments["passengers"] = list(reversed(tc.arguments["passengers"]))
                n_mod += 1
print("  modified book_reservation calls:", n_mod)
run_switches("passengers reversed", sim2, T1["8"])

print("\n=== E1b: task 20 (GT t0, passing) - payment_methods reversed ===")
sim = find_sim(gt, "20")
sim2 = sim.model_copy(deep=True)
for m in sim2.messages:
    if isinstance(m, AssistantMessage) and m.tool_calls:
        for tc in m.tool_calls:
            if tc.name == "book_reservation":
                tc.arguments["payment_methods"] = list(reversed(tc.arguments["payment_methods"]))
run_switches("payments reversed", sim2, T1["20"])

print("\n=== E1c: task 23 (haiku t0, passing) - first and last booking arguments swapped (generated ids swap) ===")
sim = find_sim(hk, "23", 0)
sim2 = sim.model_copy(deep=True)
calls = [tc for m in sim2.messages if isinstance(m, AssistantMessage) and m.tool_calls for tc in m.tool_calls if tc.name == "book_reservation"]
print("  bookings in transcript:", len(calls), [c.arguments["passengers"][0]["first_name"] for c in calls])
if len(calls) >= 2:
    calls[0].arguments, calls[-1].arguments = calls[-1].arguments, calls[0].arguments
run_switches("bookings swapped", sim2, T1["23"])

print("\n=== E1d: task 23 (haiku t0) - agent states '$1,327' instead of '$327' everywhere ===")
sim2 = sim.model_copy(deep=True)
n_mod = 0
for m in sim2.messages:
    if isinstance(m, AssistantMessage) and m.has_text_content() and "327" in m.content:
        m.content = m.content.replace("$327", "$1,327").replace(" 327", " 1,327")
        n_mod += 1
print("  modified assistant messages:", n_mod)
run_switches("1,327", sim2, T1["23"], configs=((0, 0, 0), (0, 1, 0)))

print("\n=== E1e: NL path with a stubbed judge (no model call) on task 8 GT t0 ===")
sim = find_sim(gt, "8")
task_nl = s2.with_nl_basis(T1["8"])
A = task_nl.evaluation_criteria.nl_assertions
print("  reward_basis:", [str(x) for x in task_nl.evaluation_criteria.reward_basis], "n_assertions", len(A))


def stub(results):
    def g(*a, **k):
        return AssistantMessage(role="assistant", content=json.dumps({"results": results}))
    return g


for label, results in [
    ("all met", [{"expectedOutcome": a, "reasoning": "r", "metExpectation": True} for a in A]),
    ("first not met", [{"expectedOutcome": a, "reasoning": "r", "metExpectation": i != 0} for i, a in enumerate(A)]),
    ("one omitted", [{"expectedOutcome": a, "reasoning": "r", "metExpectation": True} for a in A[1:]]),
]:
    s2._JUDGE_CACHE.clear()
    s2.generate = stub(results)
    s2.SWITCHES.set(False, False, True)
    ri = ev(sim, task_nl)
    print(f"  [{label}] {summary(ri)}")
s2.SWITCHES.set(False, False, False)
s2.generate = _blocked

print("\n=== C3: judge paraphrases AND reorders (2 assertions) ===")
assertions = ["Agent cancels XEHM4B.", "Agent does not cancel 59XX6W."]
reply = {"results": [
    {"expectedOutcome": "The agent did not cancel reservation 59XX6W", "reasoning": "it did cancel", "metExpectation": False},
    {"expectedOutcome": "Agent cancels XEHM4B.", "reasoning": "yes", "metExpectation": True},
]}
s2.generate = lambda *a, **k: AssistantMessage(role="assistant", content=json.dumps(reply))
v = s2._one_vote("assistant: hi", assertions, 0)
print("  judge said: A1=True (exact text), A2=False (paraphrased, listed first)")
print("  mapped   :", [(assertions[i][:30], x["met"], x["matched"]) for i, x in enumerate(v)])

print("\n=== C4: judge copies the trailing comma of the tau2 example JSON ===")
bad = '{\n "results": [\n  {"expectedOutcome": "Agent cancels XEHM4B.", "reasoning": "r", "metExpectation": true,},\n  {"expectedOutcome": "Agent does not cancel 59XX6W.", "reasoning": "r", "metExpectation": true,}\n ]\n}'
s2.generate = lambda *a, **k: AssistantMessage(role="assistant", content=bad)
v = s2._one_vote("assistant: hi", assertions, 0)
print("  mapped   :", [(x["met"], x["matched"], x["reasoning"][:70]) for x in v])
s2.generate = _blocked

print("\n=== C1: empty-trajectory rule vs the canned greeting ===")
from tau2.orchestrator.orchestrator import DEFAULT_FIRST_AGENT_MESSAGE  # noqa: E402

refusal_bot = [copy.deepcopy(DEFAULT_FIRST_AGENT_MESSAGE),
               UserMessage(role="user", content="I want to cancel reservation 3RK2T9."),
               AssistantMessage(role="assistant", content="I'm sorry, I can't help with that."),
               UserMessage(role="user", content="###STOP###")]
greeting_only = refusal_bot[:2]
print("  has_agent_text(greeting + user msg)        =", s2.has_agent_text(greeting_only))
print("  has_agent_text(greeting + refusal)         =", s2.has_agent_text(refusal_bot))
n_rec = sum(1 for r in (gt, hk) for s in r.simulations)
n_greet = sum(1 for r in (gt, hk) for s in r.simulations if s.messages and isinstance(s.messages[0], AssistantMessage) and s.messages[0].content == DEFAULT_FIRST_AGENT_MESSAGE.content)
print(f"  recorded sims starting with the canned greeting: {n_greet}/{n_rec}")
print("  judge view of a tool-call message:", repr(s2.trajectory_text([m for m in find_sim(gt, '8').messages if isinstance(m, AssistantMessage) and m.tool_calls][:1])[:80]))

print("\n=== C-prompt: system prompt identity with tau2 (whitespace-normalised) ===")
import inspect, re  # noqa: E401,E402

src = inspect.getsource(enl.NLAssertionsEvaluator.evaluate_nl_assertions)
m = re.search(r'system_prompt = """(.*?)"""', src, re.S)
tau2_prompt = m.group(1)
norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
print("  identical after whitespace normalisation:", norm(tau2_prompt) == norm(s2._SYSTEM_PROMPT))
print("  byte-identical:", tau2_prompt == s2._SYSTEM_PROMPT)

print("\nall model calls were blocked; done")
