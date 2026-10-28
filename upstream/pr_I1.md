# docs: the runner defaults to `EvaluationType.ALL`; say when `nl_assertions` are judged

Status: draft, not opened. Patch: `patches/I1.patch` (paths relative to the repository root; base tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Issue text: `issue_I1_docs_default_evaluation_type.md`.

## Description

`docs/evaluation.md` and `docs/running_simulations.md` say that the CLI runner and `run_tasks` default to `EvaluationType.ALL_WITH_NL_ASSERTIONS`. In the code, `run_tasks`, `run_single_task`, `prepare_batch` and `run_simulation` default to `EvaluationType.ALL`, and `run_domain` (behind `tau2 run`) passes no evaluation type. Under `ALL` the NL-assertion judge runs only for tasks whose `reward_basis` contains `NL_ASSERTION`.

Changes (docs only):

- `docs/evaluation.md`, worked example (airline task 1): the assertion does not affect the reward; under the default `ALL` it is not evaluated at all, and `ALL_WITH_NL_ASSERTIONS` runs it as a diagnostic.
- `docs/evaluation.md`, "How to inspect action correctness anyway": the CLI runner uses `ALL`, which runs the `ActionEvaluator` on every simulation (so `action_checks` and `partial_action_reward` are still populated, as the paragraph says); a new bullet says when `nl_assertions` are judged and how to request them (`run_tasks(..., evaluation_type=EvaluationType.ALL_WITH_NL_ASSERTIONS)`; `tau2 run` has no option for it).
- `docs/running_simulations.md`, Layer 3: `run_tasks` defaults to `ALL`, like `run_simulation`.

## Testing done

- `git apply --check` against `v2.0.0`: clean; applied to a copy of `v2.0.0` together with the other four patches of this audit.
- Every statement was checked against the code at `v2.0.0`: `src/tau2/runner/batch.py` lines 367, 850, 1011 and 1248-1254; `src/tau2/runner/simulation.py` line 23; `src/tau2/evaluator/evaluator.py` lines 202-230; `src/tau2/cli.py` (no evaluation-type option for `run` or `evaluate-trajs`).
- The issue's reproduction (`repro/I1.py`) shows the defaults and the judge calls per evaluation type: airline task 1, 0 calls under `ALL` and 1 under `ALL_WITH_NL_ASSERTIONS`; retail task 62, 1 call under both.

## Risk

None for behaviour (no code change). If the maintainers intend `ALL_WITH_NL_ASSERTIONS` to be the default, the code should change instead, which would add one judge call per simulation for every airline task (the stock judge is `gpt-5.4-mini-2026-03-17`). The reward would not change (`evaluator.py` lines 261-264 multiply the NL reward only when `NL_ASSERTION` is in the basis), but at v2.0.0 a judge reply that fails to parse would then abort the evaluation of airline simulations too (see the I10 part of `issue_I9_I10_I14_nl_assertion_judge.md`).
