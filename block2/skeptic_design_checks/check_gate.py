"""Replay gate, component-wise and strict (read-only; model calls blocked)."""
from __future__ import annotations

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


s2.generate = _blocked
import tau2.utils.llm_utils as lu  # noqa: E402

lu.generate = _blocked
from loguru import logger  # noqa: E402

logger.remove()
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType, evaluate_simulation  # noqa: E402
from tau2.orchestrator.modes import CommunicationMode  # noqa: E402

s2.install()
s2.SWITCHES.set(False, False, False)
tot = strict_err = comp_mismatch = 0
for fn in ("sample20_pass3_haiku.results.json", "sample20_gt_haiku.results.json"):
    res = Results.load(ROOT / "results" / "runs" / fn)
    tasks = {t.id: t for t in res.tasks}
    sc = res.info.effective_communicate_scoring
    for sim in res.simulations:
        tot += 1
        rec = sim.reward_info
        out = {}
        for strict in (False, True):
            try:
                ri = evaluate_simulation(simulation=sim, task=tasks[sim.task_id], evaluation_type=EvaluationType.ALL, solo_mode=False,
                                         domain="airline", mode=CommunicationMode.HALF_DUPLEX, env_kwargs=None, strict_replay=strict,
                                         communicate_scoring=sc)
                out[strict] = ri
            except Exception as e:  # noqa: BLE001
                out[strict] = e
        if isinstance(out[True], Exception):
            strict_err += 1
            print(f"strict replay error {fn[:12]} task {sim.task_id} t{sim.trial}: {str(out[True])[:150]}")
        ri = out[False]
        rec_db = rec.db_check.db_match if rec.db_check else None
        rec_comm = [(c.info, c.met) for c in (rec.communicate_checks or [])]
        new_comm = [(c.info, c.met) for c in (ri.communicate_checks or [])]
        if rec_db != (ri.db_check.db_match if ri.db_check else None) or rec_comm != new_comm or abs(rec.reward - ri.reward) > 1e-9:
            comp_mismatch += 1
            print(f"component mismatch {fn[:12]} task {sim.task_id} t{sim.trial}: rec db={rec_db} comm={rec_comm} vs new db={ri.db_check.db_match} comm={new_comm}")
print(f"\n{tot} sims; component-wise mismatches (lenient replay): {comp_mismatch}; strict-replay exceptions: {strict_err}")
