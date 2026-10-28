# Upstream issue and pull-request drafts for tau2-bench

Target: `sierra-research/tau2-bench`, tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`. Source drafts: `issues_draft.md` rows I1 and I3 to I16. Nothing here has been filed or opened.

## Issues

| order | audit ids | title | type | domain | severity | file | status |
|---|---|---|---|---|---|---|---|
| 1 | I11 | `modify_pending_order_items` stores the last new variant in every modified item; price difference not rounded | bug | retail | medium | `issue_I11_modify_items_last_variant.md` | draft, not filed |
| 2 | I12 | address change accepted after an item change, against the policy; the forbidden order reaches the target | bug | retail | medium | `issue_I12_modify_after_item_change.md` | draft, not filed |
| 3 | I9, I10, I14 | NL-assertion judge: tool calls invisible, fenced or array replies rejected, omitted assertion counts as met | scoring validity, bug | retail; any task judged on `nl_assertions` | medium | `issue_I9_I10_I14_nl_assertion_judge.md` | draft, not filed |
| 4 | I1 | docs say the runner defaults to `ALL_WITH_NL_ASSERTIONS`; the code defaults to `ALL` | docs | all (visible in airline) | low | `issue_I1_docs_default_evaluation_type.md` | draft, not filed |
| 5 | I5 | default `temperature: 0.0` rejected by current Anthropic models; failed run reported as success; agent cost always `None` | bug (reporting) | all | medium | `issue_I5_default_temperature_and_run_reporting.md` | draft, not filed |
| 6 | I4, I6, I8 | airline task data: accidental substring matches (3, 23), wrong required total (7), budget clause that forbids the reference (32) | task data | airline | I4 medium, I6 medium, I8 high | `issue_I4_I6_I8_airline_task_data.md` | draft, not filed |
| 7 | I13, I16 | retail task data: reference defects (2-4, 18, 26, 64, 105, 110, action ids) and task texts a faithful user cannot follow (0, 1, 15, 34, 52, 100) | task data | retail | 105 and 52 high; others medium to cosmetic | `issue_I13_I16_retail_task_data.md` | draft, not filed |
| 8 | I3 | DB hash depends on list order and on generated reservation ids | scoring validity | airline (hash shared by all domains) | medium | `issue_I3_db_hash_order_and_generated_ids.md` | draft, not filed |
| 9 | I7, I15 | text-mode simulator guidelines lack three rules of the voice guidelines; simulator deviations decide many failures and flips | simulator | all text-mode runs | medium | `issue_I7_I15_user_simulator_text_mode.md` | draft, not filed |

Suggested filing order: first the two small retail tool bugs, whose patches change one function each and are fully verified (1, 2); then the judge-path fix, which also comes with a patch (3); then the two reporting items, one docs-only (4) and one partial fix that leaves a policy decision to the maintainers (5); then the task-data items, which need the maintainers' judgement per task (6, 7); then the two design-level items, where the fix changes what the benchmark measures and needs discussion (8, 9).

## Pull requests

| issue | description | patch | `git apply --check` on `v2.0.0` | fix verified on a patched copy |
|---|---|---|---|---|
| I11 | `pr_I11.md` | `patches/I11.patch` | clean | yes: repro, 3 new tests, retail tests, all 114 retail references replayed |
| I12 | `pr_I12.md` | `patches/I12.patch` | clean | yes: repro, 3 new tests, retail tests, 14 forbidden-order tasks, 0 target hashes changed |
| I10, I14 | `pr_I10_I14.md` | `patches/I10_I14.patch` | clean | yes: repros, 9 new tests, evaluator tests, 169 recorded judge replies re-parsed |
| I5 (partial) | `pr_I5.md` | `patches/I5.patch` | clean | yes: repro, 4 new tests, runner and orchestrator tests; no live run |
| I1 | `pr_I1.md` | `patches/I1.patch` | clean | docs only; statements checked against the code and the I1 repro |

All five patches also apply together to one copy of `v2.0.0`; with all of them applied, the related existing tests and the new ones give 160 passed, 6 skipped (unpatched: 141 passed, 6 skipped on the same existing files).

## Reproductions

`repro/<id>.py`, one per draft id: I1, I3, I4, I5, I6, I8, I9, I10, I11, I12, I13, I14, I15, I16. Each is self-contained, uses tau2 APIs only, makes no model call (judge and provider calls are replaced by stubs where needed), and runs from the tau2-bench root:

```text
PYTHONUTF8=1 uv run --no-sync python <path to repro>/<id>.py
```

Their output, as pasted into the issues, was produced on the unpatched clone at the pinned commit. I7's run-level findings need model calls and have no snippet; its template difference is reproduced by `I15.py`.

## How the patches were checked

- Each patch was made from copies of the touched files in a scratch folder, never by editing the clone, and checked with `git -C tau2-bench apply --check ../upstream/patches/<id>.patch`.
- Verification: a copy of the clone's `src/` and `tests/` with the patch applied, the reproduction run through the same `uv` command with `PYTHONPATH` pointing at the copy, and the tests run with pytest 9.0.2 from outside the project environment (the pinned environment has no pytest, and nothing was installed into it).

## Conventions

- English, impersonal; model ids appear only where a run used them.
- Evidence paths in the issues are paths in the audit repository; code references are file and line at the pinned commit.
- Numbers come from the audit's result files named in each issue. Run-based retail findings that were not adversarially reviewed are marked as such where they are cited.
