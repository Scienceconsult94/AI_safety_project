Status: partly covered, do not file those parts: I9 (tool calls invisible to the judge) is #553; the fenced-reply part of I10 is #555; I14 (an omitted or empty verdict counts as met) is #554. Remaining part, the bare top-level JSON array reply of I10: still reproduces at da0835f6c67baef58bdda18f2a3b037dfb3a1754 (by reading the code; not run)

Source draft: `upstream/issue_I9_I10_I14_nl_assertion_judge.md`. Upstream `main` read at `da0835f6c67baef58bdda18f2a3b037dfb3a1754` (2026-10-29 22:37 -0700, merge of #692), shallow clone in `<fresh-folder>\upstream_main`.

Tracker checked on 2026-10-31: `https://api.github.com/repos/sierra-research/tau2-bench/issues?state=all&per_page=100`, pages 1-8 (page 9 empty). 706 items, numbers #1-#711 (#133, #134, #146, #324, #561 not returned), 202 issues and 504 pull requests. Every title read; bodies read where the title was close; file diffs read for pull requests #469, #562, #581, #584.

Items on the same problem:

- #553 (issue, open): same as I9. Tool-call turns are rendered as `assistant: None`, so the judge cannot see tool names or arguments.
- #584 (PR, open, not merged): fix for #553. It drops the contentless turns and, as it says itself, does not show tool calls to the judge, so the I9 fix suggested in the draft (render tool calls) is not in it.
- #555 (issue, open): same as the fenced part of I10 (bare `json.loads`; a fenced reply raises). No mention of bare arrays. Its suggested fix is `extract_json_from_llm_response`, which breaks a bare array.
- #562 (PR, open, not merged): fix for #555. It decodes the raw reply first and unwraps an outer fence only on failure, so a bare array still reaches `.get` (diff read).
- #469 (PR, open, not merged, for #211): retries the judge and parses through `extract_json_from_llm_response`; after 3 failures every assertion is unmet. A bare array of two or more results still fails to parse.
- #554 (issue, open): same as I14 (an empty or short verdict list scores 1.0; one verdict for two assertions awards both).
- #581 (PR, open, not merged): fix for #554. It raises on a count mismatch; the attached patch instead matches by text or position and counts a missing verdict as unmet. Same problem, different fix.
- #646 (issue, open): section 2 repeats the `all([])` pass of #554 and says the judge grades the narrative. Tool calls and reply formats are not named.
- #211 (issue, open): many retries after the judge model was changed. The symptom fits I10, but no mechanism is given. Not the same report.
- #556 (issue) and #593 (PR), both open: judge cost is not recorded. This is the draft's side remark on cost, left out of the text below.
- #493 and #672 (issues, open): infrastructure errors are excluded from the metrics. Same consequence path, different trigger.
- Not the same: #22, #23, #59 (NL assertions off by default or marked experimental); #213, #226 (`EvaluationType.ALL` and the NL reward basis); #274, #474 (closed), #479 (judge model choice and override); #352 (language hints); #384 (empty criteria auto-pass, kept apart from this in #554); #436 (a verdict that contradicts its own justification).

Code check at HEAD. The `src/tau2/evaluator/` folder is byte-identical to `v2.0.0`.

- I9: `src/tau2/evaluator/evaluator_nl_assertions.py` lines 75-77: `f"{message.role}: {message.content}"` for every message. Still exists.
- I10: same file, lines 117-131: `generate(...)`, then `json.loads(assistant_message.content)` and `result_data.get("results", [])`. Still exists. `src/tau2/utils/llm_utils.py` lines 785-804 (`extract_json_from_llm_response`, first `{` to last `}`): unchanged.
- I14: same file, lines 46-48: `all(result.met ...)` over the returned checks, with no count check. Still exists. `FullDuplexNLAssertionsEvaluator` delegates at lines 186-197.
- Live-run path: evaluation runs inside `run_simulation` (`src/tau2/runner/simulation.py` line 142). `src/tau2/runner/progress.py` lines 96-107 at HEAD (92-103 at v2.0.0) retry every exception. New at HEAD: lines 94-95 re-raise `NonRetryableError` (`src/tau2/utils/errors.py`, a `RuntimeError` subclass), but `JSONDecodeError` and `AttributeError` are not that type, so they are still retried. Lines 116-134 record `INFRASTRUCTURE_ERROR`. `src/tau2/metrics/agent_metrics.py` lines 217-226 exclude it.
- Stock judge: `src/tau2/config.py` lines 49-50 at HEAD (45-46 at `v2.0.0`), unchanged values.
- `git apply --check` of `upstream/patches/I10_I14.patch` on the HEAD clone: clean.

Optional, not written here: the draft's I9 evidence could be posted as a comment on #553. The evidence: on airline task 9, trial 1, the tool-use assertion was judged unmet in 3 of 3 votes with the stock transcript and met with tool calls rendered.

---

## NL-assertion judge: a reply that is a bare JSON array raises `AttributeError`, and the helper suggested in #555 does not parse it either

**Versions.** Reproduced at tag `v2.0.0` (commit `989d3285ae669e49503324bdb9981bf14fccedeb`). Checked by reading the code at `main` `da0835f6c67baef58bdda18f2a3b037dfb3a1754`: `src/tau2/evaluator/` and `src/tau2/utils/llm_utils.py` are unchanged.

**What happens.** `evaluate_nl_assertions` parses the judge reply with `json.loads(assistant_message.content)`, then calls `result_data.get("results", [])` (`src/tau2/evaluator/evaluator_nl_assertions.py`, lines 123-131). A reply that is a bare top-level array of the per-assertion objects decodes to a `list`, and `.get` raises `AttributeError`. This is a separate case from the fenced reply in #555:

- `extract_json_from_llm_response` (`src/tau2/utils/llm_utils.py`, lines 785-804) is suggested in #555 and used in #469. It cuts an unfenced reply from the first `{` to the last `}`, so the two-result array below becomes invalid JSON.
- #562 decodes the raw reply first, so a bare array still reaches `.get`.

In a live run the exception restarts the simulation (`src/tau2/runner/progress.py`, lines 92-103 at v2.0.0, 96-107 at HEAD da0835f6). After the last attempt the simulation is recorded as `infrastructure_error` (line 120 at v2.0.0, 124 at HEAD), and the metrics exclude it (`src/tau2/metrics/agent_metrics.py`, lines 217-226).

With `anthropic/claude-haiku-5-5` as the judge and a variant of the stock prompt with numbered assertions, 53 of 610 replies were bare arrays. The stock judge was not run.

**Reproduction** (no model call; the judge is stubbed), from a tau2-bench root:

```text
PYTHONUTF8=1 uv run --no-sync python <audit repo>/upstream/repro/I10.py
```

The script is `upstream/repro/I10.py` in https://github.com/Scienceconsult94/AI_safety_project. Output at `v2.0.0` (line 2 is #555):

```text
JSON object (the format the prompt asks for): reward 0.0, 2 verdicts
same object inside a ```json code fence: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
bare top-level JSON array: AttributeError: 'list' object has no attribute 'get'
extract_json_from_llm_response(bare array) -> starts '{"', ends 'e}': invalid JSON (Extra data)
```

**Expected vs actual.** Expected: a bare array of valid verdicts is parsed like the wrapped object, and only a reply with no list of results is an error. Actual: `AttributeError`. The simulation is retried and can drop out of the score.

**Fix.** `upstream/patches/I10_I14.patch` in the same repository (`git apply --check` is clean on `v2.0.0` and on `main`). It adds `parse_judge_results`, which accepts a fenced or bare object or array and raises `ValueError` when no list of results is present. The patch also returns one verdict per assertion and counts an omitted one as unmet, so it overlaps #562 and #581. It leaves `extract_json_from_llm_response` unchanged, since other judges use it.
