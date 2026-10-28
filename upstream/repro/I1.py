"""I1: docs/evaluation.md says the CLI runner uses EvaluationType.ALL_WITH_NL_ASSERTIONS by default;
the runner functions default to EvaluationType.ALL, which calls the NL-assertion judge only for tasks
whose reward_basis contains NL_ASSERTION.

No model call: the judge call (`generate`) is replaced by a counting stub.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I1.py
"""

import inspect
import json
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.data_model.semantic_communication import CommunicateScorer, CommunicateScoring  # noqa: E402
from tau2.data_model.simulation import SimulationRun, TerminationReason  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation  # noqa: E402
from tau2.registry import registry  # noqa: E402
from tau2.runner.batch import run_domain, run_single_task, run_tasks  # noqa: E402
from tau2.runner.simulation import run_simulation  # noqa: E402

for line in Path("docs/evaluation.md").read_text(encoding="utf-8").splitlines():
    if "by default" in line and "ALL_WITH_NL_ASSERTIONS" in line:
        print("docs/evaluation.md:", line.strip())
for fn in (run_tasks, run_single_task, run_simulation):
    print(f"{fn.__module__}.{fn.__name__}: evaluation_type default = {inspect.signature(fn).parameters['evaluation_type'].default}")
print("run_domain (used by `tau2 run`) passes an evaluation_type:", "evaluation_type" in inspect.getsource(run_domain))

judge_calls = []


def fake_generate(**kwargs):
    judge_calls.append(kwargs.get("call_name"))
    return SimpleNamespace(content=json.dumps({"results": []}))


nl_module.generate = fake_generate
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="###STOP###"),
]
for domain, task_id in (("airline", "1"), ("retail", "62")):
    task = {t.id: t for t in registry.get_tasks_loader(domain)("base")}[task_id]
    for evaluation_type in (EvaluationType.ALL, EvaluationType.ALL_WITH_NL_ASSERTIONS):
        judge_calls.clear()
        simulation = SimulationRun(id="probe", task_id=task.id, start_time="", end_time="", duration=0.0,
                                   termination_reason=TerminationReason.USER_STOP, messages=trajectory)
        evaluate_simulation(simulation, task, evaluation_type, solo_mode=False, domain=domain,
                            communicate_scoring=CommunicateScoring(scorer=CommunicateScorer.SUBSTRING))
        basis = [r.value for r in task.evaluation_criteria.reward_basis]
        print(f"{domain} task {task_id} (reward_basis {basis}, {len(task.evaluation_criteria.nl_assertions or [])} nl_assertions), "
              f"{evaluation_type.name}: NL judge calls = {len(judge_calls)}")
