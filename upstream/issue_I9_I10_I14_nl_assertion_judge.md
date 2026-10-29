# NL-assertion judge: tool calls are invisible in the transcript, the reply parser rejects fenced or array replies, and an omitted assertion counts as met

| field | value |
|---|---|
| audit ids | I9, I10, I14 |
| type | scoring validity (judge path), bug |
| domain | every task whose `reward_basis` contains `NL_ASSERTION` (retail: 112 of 114 tasks, 40 of them with assertions); every task under `ALL_WITH_NL_ASSERTIONS` |
| severity | medium |
| status | draft, not filed |

## Summary

`NLAssertionsEvaluator.evaluate_nl_assertions` has three gaps. (I9) It renders the conversation for the judge as `role: content` lines, so an assistant turn that only calls a tool appears as `assistant: None`, and the judge cannot see which tool was called with which arguments. (I10) It parses the reply with bare `json.loads(...)` and then `.get("results")`: a reply inside a markdown code fence raises `JSONDecodeError`, and a bare top-level JSON array raises `AttributeError`. (I14) The reward is `all(met)` over whatever results the judge returns, so an assertion the judge leaves out is never checked, and a reply with an empty `results` list gives reward 1.0.

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`.

- `src/tau2/evaluator/evaluator_nl_assertions.py` lines 75-77 (transcript), 117-131 (judge call and parsing), 46-48 (reward); `FullDuplexNLAssertionsEvaluator` (lines 186-197) delegates to the same method.
- `src/tau2/utils/llm_utils.py` lines 785-804 (`extract_json_from_llm_response`, used by other judges, slices from the first `{` to the last `}` and so also breaks a bare array; the NL evaluator does not call it).
- In a live run, an exception during evaluation is raised inside `run_simulation`, so `run_with_retry` (`src/tau2/runner/progress.py` lines 19-110) re-runs the whole simulation and, after the last attempt, records it as an `infrastructure_error`, which the metrics exclude (`src/tau2/metrics/agent_metrics.py` lines 217-226).

## Reproduction

No model call: the judge call (`generate`) is replaced by a stub that records the prompt or returns a fixed reply text. Run each from the tau2-bench root with `PYTHONUTF8=1 uv run --no-sync python <path to repro>/<id>.py` (the scripts are in `upstream/repro/` of the audit repository).

### I9: the transcript the judge sees (`upstream/repro/I9.py`)

The tool call is the reference action of airline task 9; the assertion is task 9's third `nl_assertion`.

```python
"""I9: the NL-assertion judge sees the conversation as `role: content` lines, so a tool call is
rendered as `assistant: None` and the judge cannot see which tool was called with which arguments.

No model call: the judge call (`generate`) is replaced by a stub that records the prompt.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I9.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, ToolCall, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("airline")("base")}["9"]
assertion = task.evaluation_criteria.nl_assertions[2]
reference = task.evaluation_criteria.actions[0]  # search_direct_flight(JFK, MCO, 2024-05-22)

env = registry.get_env_constructor("airline")()
call = ToolCall(id="call_0", name=reference.name, arguments=dict(reference.arguments), requestor="assistant")
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="Are there direct flights from JFK to MCO on May 22?"),
    AssistantMessage(role="assistant", content=None, tool_calls=[call]),
    env.get_response(call),
]

prompts = []


def fake_generate(**kwargs):
    prompts.append(kwargs["messages"][-1].content)
    return SimpleNamespace(content=json.dumps({"results": []}))


nl_module.generate = fake_generate
NLAssertionsEvaluator.evaluate_nl_assertions(trajectory, [assertion])
conversation = prompts[0].split("expectedOutcomes:")[0]
print("assertion:", assertion)
print("tool call made:", f"{call.name}({json.dumps(call.arguments)})")
print("conversation as sent to the judge:")
for line in conversation.strip().splitlines():
    print("   ", line.strip())
print("tool name in judge prompt:", call.name in prompts[0], "| arguments in judge prompt:", "2024-05-22" in prompts[0])
```

Output:

```text
assertion: Check that Agent searched for direct flights between JFK and MCO on May 22 2024.
tool call made: search_direct_flight({"origin": "JFK", "destination": "MCO", "date": "2024-05-22"})
conversation as sent to the judge:
    conversation:
    assistant: Hi! How can I help you today?
    user: Are there direct flights from JFK to MCO on May 22?
    assistant: None
    tool: []
tool name in judge prompt: False | arguments in judge prompt: False
```

### I10: reply formats (`upstream/repro/I10.py`)

```python
"""I10: the NL-assertion evaluator parses the judge reply with bare `json.loads(...)` and then
`.get("results")`; a reply in a markdown code fence raises JSONDecodeError and a bare top-level JSON
array raises AttributeError. `extract_json_from_llm_response` also mangles a bare array.

No model call: the judge call (`generate`) is replaced by a stub returning fixed reply texts.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I10.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402
from tau2.utils.llm_utils import extract_json_from_llm_response  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["62"]
assertions = task.evaluation_criteria.nl_assertions
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="###STOP###"),
]
results = [{"expectedOutcome": a, "reasoning": "not stated", "metExpectation": False} for a in assertions]
replies = {
    "JSON object (the format the prompt asks for)": json.dumps({"results": results}),
    "same object inside a ```json code fence": "```json\n" + json.dumps({"results": results}, indent=2) + "\n```",
    "bare top-level JSON array": json.dumps(results),
}

for label, content in replies.items():
    nl_module.generate = lambda content=content, **kwargs: SimpleNamespace(content=content)
    try:
        info = NLAssertionsEvaluator.calculate_reward(task, trajectory)
        outcome = f"reward {info.reward}, {len(info.nl_assertions)} verdicts"
    except Exception as e:  # noqa: BLE001
        outcome = f"{type(e).__name__}: {e}"
    print(f"{label}: {outcome}")

bare = json.dumps(results)
extracted = extract_json_from_llm_response(bare)
try:
    json.loads(extracted)
    status = "valid JSON"
except json.JSONDecodeError as e:
    status = f"invalid JSON ({e.msg})"
print(f"extract_json_from_llm_response(bare array) -> starts {extracted[:2]!r}, ends {extracted[-2:]!r}: {status}")
```

Output:

```text
JSON object (the format the prompt asks for): reward 0.0, 2 verdicts
same object inside a ```json code fence: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
bare top-level JSON array: AttributeError: 'list' object has no attribute 'get'
extract_json_from_llm_response(bare array) -> starts '{"', ends 'e}': invalid JSON (Extra data)
```

### I14: omitted assertions (`upstream/repro/I14.py`)

```python
"""I14: the NL reward is `all(met)` over whatever results the judge returns. An assertion that the
judge leaves out is never checked, so it counts as met; a reply with an empty `results` list gives
reward 1.0.

No model call: the judge call (`generate`) is replaced by a stub returning fixed reply texts.
Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I14.py
"""

import json
import os
from types import SimpleNamespace

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

import tau2.evaluator.evaluator_nl_assertions as nl_module  # noqa: E402
from tau2.data_model.message import AssistantMessage, UserMessage  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.registry import registry  # noqa: E402

task = {t.id: t for t in registry.get_tasks_loader("retail")("base")}["62"]
assertions = task.evaluation_criteria.nl_assertions
trajectory = [
    AssistantMessage(role="assistant", content="Hi! How can I help you today?"),
    UserMessage(role="user", content="###STOP###"),
]
print(f"task 62 has {len(assertions)} nl_assertions: {assertions}")

replies = {
    "verdict for both assertions, second unmet": [
        {"expectedOutcome": assertions[0], "reasoning": "-", "metExpectation": True},
        {"expectedOutcome": assertions[1], "reasoning": "-", "metExpectation": False},
    ],
    "verdict for the first assertion only (second omitted)": [
        {"expectedOutcome": assertions[0], "reasoning": "-", "metExpectation": True},
    ],
    "empty results list": [],
}
for label, results in replies.items():
    content = json.dumps({"results": results})
    nl_module.generate = lambda content=content, **kwargs: SimpleNamespace(content=content)
    info = NLAssertionsEvaluator.calculate_reward(task, trajectory)
    print(f"{label}: reward {info.reward}, verdicts recorded {len(info.nl_assertions)} of {len(assertions)}")
```

Output:

```text
task 62 has 2 nl_assertions: ['Agent should tell the user the Bluetooth speaker costs $302.67.', 'Agent should tell the user the battery life is 20 hours.']
verdict for both assertions, second unmet: reward 0.0, verdicts recorded 2 of 2
verdict for the first assertion only (second omitted): reward 1.0, verdicts recorded 1 of 2
empty results list: reward 1.0, verdicts recorded 0 of 2
```

## Observed vs expected

- I9: the judge prompt contains `assistant: None` and `tool: []`; neither the tool name nor its arguments appear. Expected: tool calls rendered with name and arguments, and tool results labelled as such.
- I10: a fenced object and a bare array, both carrying valid verdicts, raise. Expected: both parsed; only a reply without a list of results is an error.
- I14: with one of two verdicts the reward is 1.0; with none it is 1.0. Expected: one verdict per assertion, and an assertion without a verdict counts as unmet (or the reply is re-asked).

## Impact on scores

Measured with `anthropic/claude-haiku-5-5` as the judge; the stock judge is `gpt-5.4-mini-2026-03-17` (`src/tau2/config.py` line 45), which the audit did not run, so the reply-format shares describe the substituted judge.

- I9: on a recorded airline trajectory (task 9, trial 1) in which the agent called `search_direct_flight(JFK, MCO, 2024-05-22)`, the audit's 3-vote judge (its own prompt with numbered assertions) given tau2's `role: content` transcript marked "Check that Agent searched for direct flights between JFK and MCO on May 22 2024" unmet in 3 of 3 votes; with tool calls rendered into the transcript the same assertion was judged met. Assertions about tool use are then judged from tool results alone.
- I10: with the stock prompt and stock evaluator, 103 of 169 recorded judge replies (the two retail runs and a no-op probe) came inside a code fence and would have been rejected by the stock `json.loads` (the audit's overlay parsed them and recorded which ones the stock code would reject). With the audit's own judge prompt (a variant of the stock prompt with numbered assertions), the same model returned a bare top-level array in 53 of 610 replies. In a live run a rejected reply restarts the whole simulation, and a simulation whose every attempt fails is excluded from the metrics, so the score can be computed over fewer simulations without saying why.
- I14: in the 169 recorded retail replies, no reply had fewer results than assertions, so no recorded reward depended on it. The property means that an incomplete or empty judge reply passes the assertions it does not mention.
- With 3 votes instead of one, 1 of 243 assertion verdicts in the retail runs changed and 1 of 159 rewards flipped (task 110, fail to pass), so the single vote is stable on these transcripts once its replies are parsed.
- Judge cost is not reported: `RewardInfo` has no field for it, and in the audit's judge runs tau2's `get_response_cost` logged "LLM Provider NOT provided ... model=claude-haiku-5-5" for the judge calls (252 lines in one run log) and returned 0.0. The cause of that error was not investigated.

## Suggested fix

- I10 and I14 (patch attached, `pr_I10_I14.md` / `patches/I10_I14.patch`): accept a fenced or bare JSON object or array; match results to assertions by the echoed text, then by position when the counts allow; return exactly one check per assertion, in assertion order, and count an assertion without a verdict as unmet. A reply without any list of results still raises.
- I9: render tool calls into the judge transcript, for example `assistant: [tool call] search_direct_flight({"origin": "JFK", ...})` and `tool (search_direct_flight): [...]`. This changes the judge input, so verdicts before and after are not comparable; it is not in the attached patch. The audit's version is `trajectory_text` in `scripts/v2/scorer_v2.py`.
- Optionally: number the assertions in the prompt and ask for an `index` field, re-ask once when a reply cannot be parsed or omits an assertion, and record the judge model, prompt version and cost in `results.json`.

## Evidence (audit repository)

- I9: `results/v2/rescore_stockview.csv` vs `results/v2/rescore.csv` (task 9, trial 1), `block2/PLAN.md` (deviation of 2026-10-27, judge transcript view), `scripts/v2/scorer_v2.py` (`trajectory_text`), `results/v2/rescore_judge_run.log` (cost error).
- I10: `results/retail/runs/retail_pass3_haiku/judge_calls.json`, `results/retail/runs/retail_gt_haiku/judge_calls.json`, `results/retail/judge_calls_noop.json` (raw replies, `strict_ok` per reply), `results/retail/rejudge_summary.md`, `results/v2/judge_reparse_check.md`, `results/v2/judge_raw*.json`.
- I14: `results/retail/rejudge_summary.md`, `results/retail/noop_judge_probe.md`, `retail/summary_numbers.md` (Table 6).
- `upstream/repro/I9.py`, `upstream/repro/I10.py`, `upstream/repro/I14.py`.
