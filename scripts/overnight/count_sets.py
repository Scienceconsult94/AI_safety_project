"""Count simulations and judge pairs per set for T3 (no model call)."""
import json, sys, os
from pathlib import Path
os.environ.setdefault("LOGURU_LEVEL", "ERROR")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v2"))
import scorer_v2 as s2, tasks_v2
from tau2.data_model.simulation import Results
tasks_v2.register()
t2 = {t.id: t for t in tasks_v2.get_tasks_v2(None)}
sets = {
 "recorded_haiku20": ROOT/"results/runs/sample20_pass3_haiku.results.json",
 "recorded_haiku30": ROOT/"results/runs/rest30_pass3_haiku.results.json",
 "fresh_v2_haiku20": ROOT/"results/v2/runs/v2_sample20_pass3_haiku/results.json",
 "fresh_v2_haiku30": ROOT/"results/v2/runs/v2_rest30_pass3_haiku/results.json",
 "recorded_sonnet20": ROOT/"results/runs/sample20_sonnet_t3.results.json",
}
tot_pairs = 0
for name, p in sets.items():
    if not p.exists():
        print(name, "MISSING", p); continue
    res = Results.load(p)
    n = len(res.simulations); txt = 0; pairs = 0; nass = 0; empty_rule = 0
    for sim in res.simulations:
        a = t2[sim.task_id].evaluation_criteria.nl_assertions or []
        if not a: continue
        if not s2.has_agent_text(sim.messages):
            empty_rule += 1; continue
        txt += 1; pairs += 1; nass += len(a)
    tot_pairs += pairs
    print(f"{name}: sims {n}, judged pairs {pairs} (assertions {nass}), empty-rule {empty_rule}, tasks without assertions: {sum(1 for s in res.simulations if not (t2[s.task_id].evaluation_criteria.nl_assertions or []))}")
print("airline judged pairs total", tot_pairs)
print("tasks v2 without nl_assertions:", sorted(int(k) for k,t in t2.items() if not (t.evaluation_criteria.nl_assertions or [])))
