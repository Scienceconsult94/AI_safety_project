"""Task set "airline_v2": the pinned airline tasks with the edits of block2/task_fixes.md.

Registered as a tau2 *task set* (not a domain) so that the environment, policy, personas and
language pins stay those of "airline". Loader signature follows tau2's registry contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.airline.environment import get_tasks_split
from tau2.registry import registry

ROOT = Path(__file__).resolve().parents[2]
V2_TASKS = ROOT / "block2" / "tasks_airline_v2.json"
TASK_SET_NAME = "airline_v2"


def get_tasks_v2(task_split_name: Optional[str] = "base", **_: object) -> list[Task]:
    """Tasks v2. When scorer_v2.SWITCHES.nl_enforce is on, NL_ASSERTION is added to every task's
    reward_basis so that tau2's own reward product includes the NL part (live runs). The loader is
    deterministic for a fixed switch state, which tau2's artifact pins require."""
    tasks = [Task.model_validate(t) for t in json.loads(V2_TASKS.read_text(encoding="utf-8"))]
    try:
        import scorer_v2  # local overlay module (same folder)

        if scorer_v2.SWITCHES.nl_enforce:
            tasks = [scorer_v2.with_nl_basis(t) for t in tasks]
    except ImportError:
        pass
    if task_split_name is None:
        return tasks
    ids = set(get_tasks_split()[task_split_name])
    return [t for t in tasks if t.id in ids]


def register() -> str:
    if TASK_SET_NAME not in registry.get_task_sets():
        registry.register_tasks(get_tasks_v2, TASK_SET_NAME, get_task_splits=get_tasks_split)
    return TASK_SET_NAME
