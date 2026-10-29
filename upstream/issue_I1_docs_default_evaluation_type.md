# docs: `evaluation.md` says the CLI runner defaults to `ALL_WITH_NL_ASSERTIONS`; the code defaults to `ALL`

| field | value |
|---|---|
| audit id | I1 |
| type | docs |
| domain | all (visible in airline) |
| severity | low |
| status | draft, not filed |

## Summary

`docs/evaluation.md` (section "How to inspect action correctness anyway") says that the CLI runner uses `EvaluationType.ALL_WITH_NL_ASSERTIONS` by default, and `docs/running_simulations.md` says the same of `run_tasks`. At v2.0.0 every runner entry point defaults to `EvaluationType.ALL`, and `run_domain` (the function behind `tau2 run`) passes no evaluation type. Under `ALL` the natural-language (NL) assertion judge runs only for tasks whose `reward_basis` contains `NL_ASSERTION`, so `tau2 run` never judges the `nl_assertions` of airline tasks, and the worked example's sentence that the assertion "runs as a diagnostic only" does not hold at the default.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- Docs: `docs/evaluation.md` lines 152-154 (worked example) and 171-172; `docs/running_simulations.md` line 264.
- Code: `src/tau2/runner/batch.py` line 367 (`run_single_task`), line 850 (`prepare_batch`), line 1011 (`run_tasks`), lines 1248-1254 (`run_domain` calls `run_tasks` without `evaluation_type`); `src/tau2/runner/simulation.py` line 23 (`run_simulation`); `src/tau2/evaluator/evaluator.py` lines 224-230 (the NL evaluator runs under `ALL` only when `NL_ASSERTION` is in the task's basis).

## Reproduction

No model call: the judge call is replaced by a counting stub. Run from the tau2-bench root with `PYTHONUTF8=1 uv run --no-sync python <path to repro>/I1.py` (the script is `upstream/repro/I1.py` in the audit repository).

```python
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
```

Output:

```text
docs/evaluation.md: - The CLI runner uses `EvaluationType.ALL_WITH_NL_ASSERTIONS` by default,
tau2.runner.batch.run_tasks: evaluation_type default = EvaluationType.ALL
tau2.runner.batch.run_single_task: evaluation_type default = EvaluationType.ALL
tau2.runner.simulation.run_simulation: evaluation_type default = EvaluationType.ALL
run_domain (used by `tau2 run`) passes an evaluation_type: False
airline task 1 (reward_basis ['DB', 'COMMUNICATE'], 1 nl_assertions), ALL: NL judge calls = 0
airline task 1 (reward_basis ['DB', 'COMMUNICATE'], 1 nl_assertions), ALL_WITH_NL_ASSERTIONS: NL judge calls = 1
retail task 62 (reward_basis ['DB', 'NL_ASSERTION'], 2 nl_assertions), ALL: NL judge calls = 1
retail task 62 (reward_basis ['DB', 'NL_ASSERTION'], 2 nl_assertions), ALL_WITH_NL_ASSERTIONS: NL judge calls = 1
```

## Observed vs expected

- Observed: the default is `ALL`. Airline task 1 (`reward_basis` `[DB, COMMUNICATE]`, one assertion) gets no judge call under `ALL` and one under `ALL_WITH_NL_ASSERTIONS`. Retail task 62 (`reward_basis` `[DB, NL_ASSERTION]`) is judged under both.
- Expected from the docs: `ALL_WITH_NL_ASSERTIONS` by default, so that `nl_assertions` are judged as a diagnostic on every task.

The code behaviour looks intended (the leaderboard score follows `reward_basis`), so the docs should change.

## Impact on scores

None on the reward, because an assertion outside `reward_basis` never gates it. The impact is on reading the results: all 50 airline tasks carry `nl_assertions` and none has `NL_ASSERTION` in its basis, so a user who follows the docs expects assertion verdicts in `results.json` and gets none. In an audit sample of 20 airline tasks, 6 state a requirement that only an `nl_assertion` expresses (for example "Agent searched for direct flights between JFK and MCO on May 22 2024", task 9); with the default runner those requirements are neither scored nor reported.

## Suggested fix

Correct the three passages: the CLI runner uses `EvaluationType.ALL`; under `ALL`, `nl_assertions` are judged only for tasks whose `reward_basis` contains `NL_ASSERTION`; `ALL_WITH_NL_ASSERTIONS` is available through `run_tasks(..., evaluation_type=...)`, and `tau2 run` has no option for it. A docs-only patch is in `pr_I1.md` / `patches/I1.patch`. Alternatively, add a CLI option that selects the evaluation type.

## Evidence (audit repository)

- `checklist.md` row 2k (the runner default and its consequence); `audit_log.csv` rows 2k (tasks 9, 10, 26, 28, 44, 46).
- `patches/README.md` (the audit's note that the NL judge is never called by `tau2 run` for airline).
- `upstream/repro/I1.py`.
