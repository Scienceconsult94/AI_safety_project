"""Summarise one tau2 results.json: reward per task/trial, pass^k, LiteLLM cost.

Usage (from inside tau2-bench):  uv run --no-sync python ../summarize_run.py <results.json> [more.json ...]
Prints a compact table; never edits any file. Costs are LiteLLM estimates - the
Anthropic Console figure is authoritative and is what goes into cost.md.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def summarize(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    sims = data.get("simulations") or []
    info = data.get("info") or {}
    by_task: dict[str, list[float]] = defaultdict(list)
    agent_cost = user_cost = 0.0
    term = defaultdict(int)
    for s in sims:
        r = (s.get("reward_info") or {}).get("reward")
        by_task[str(s.get("task_id"))].append(float(r) if r is not None else float("nan"))
        agent_cost += float(s.get("agent_cost") or 0.0)
        user_cost += float(s.get("user_cost") or 0.0)
        term[str(s.get("termination_reason"))] += 1
    n_tasks = len(by_task)
    trials = max((len(v) for v in by_task.values()), default=0)
    print(f"== {path}")
    print(f"agent={info.get('agent_info', {}).get('llm') or info.get('agent_llm')}  "
          f"user={info.get('user_info', {}).get('llm') or info.get('user_llm')}  "
          f"tasks={n_tasks} trials/task={trials} sims={len(sims)}")
    print("task_id  rewards")
    for tid in sorted(by_task, key=lambda x: int(x) if x.isdigit() else x):
        print(f"{tid:>7}  {' '.join(f'{r:.0f}' for r in by_task[tid])}")
    for k in range(1, trials + 1):
        # pass^k = fraction of tasks whose first k trials all succeed (tasks with >= k trials)
        elig = [v for v in by_task.values() if len(v) >= k]
        pk = sum(all(r == 1.0 for r in v[:k]) for v in elig) / len(elig) if elig else float("nan")
        print(f"pass^{k} = {pk:.3f}  (n={len(elig)})")
    print(f"litellm cost: agent ${agent_cost:.4f} + user ${user_cost:.4f} = ${agent_cost + user_cost:.4f}")
    print("termination:", dict(term))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        summarize(Path(p))
