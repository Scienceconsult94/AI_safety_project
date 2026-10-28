"""Judge overlay for the retail audit: the stock NL-assertion evaluator with the judge model substituted.

What stays stock (tau2 v2.0.0, `src/tau2/evaluator/evaluator_nl_assertions.py`): the prompt, the single vote, the
`role: content` transcript view, the mapping of results to assertions by echoed text, the `all()` over whatever the
judge returns. What this module changes, in-process only (the clone is not edited):
  * the judge model: `DEFAULT_LLM_NL_ASSERTIONS` (an OpenAI model) -> `anthropic/claude-haiku-5-5`, args {} (retail/PLAN.md §2);
  * `json.loads` inside that module -> a tolerant parser that also accepts a fenced block or a bare top-level array
    (the stock strict parser would abort the simulation); every reply is recorded with the flag `strict_ok` = whether
    the stock parser would have accepted it (check 2j);
  * `generate` inside that module -> the same call, plus a log of token usage, the raw reply, the number of assertions
    asked and results returned (an omitted assertion is silently uncounted by the stock code).
`install()` applies the patches; `drain()` returns and clears the per-call log. Thread-safe (the runner uses threads).
"""

from __future__ import annotations

import json
import re
import threading
from typing import Any

from tau2.evaluator import evaluator_nl_assertions as nle

JUDGE_MODEL = "anthropic/claude-haiku-5-5"
JUDGE_ARGS: dict[str, Any] = {}
PRICE_IN, PRICE_OUT = 0.10, 0.50  # USD per MTok, cache ignored (upper bound), as in block 1
_LOCK = threading.Lock()
CALLS: list[dict] = []
TOTALS = {"calls": 0, "in_tokens": 0, "out_tokens": 0, "strict_rejected": 0, "unparsed": 0, "results_short": 0}
_stock_generate = nle.generate
_stock_json = nle.json
_last_call: dict = {}
_last_lock = threading.local()


def strict_loads_ok(raw: str) -> bool:
    try:
        d = _stock_json.loads(raw)
    except Exception:  # noqa: BLE001
        return False
    return isinstance(d, dict) and isinstance(d.get("results", []), list)


def tolerant_loads(raw: str) -> dict:
    """Return {"results": [...]}; raises ValueError only when nothing parses (then the stock code path raises as it would)."""
    text = (raw or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    candidates = ([m.group(1).strip()] if m else []) + [text]
    i, k = text.find("{"), text.rfind("}")
    if i != -1 and k > i:
        candidates.append(text[i:k + 1])
    i, k = text.find("["), text.rfind("]")
    if i != -1 and k > i:
        candidates.append(text[i:k + 1])
    for cand in candidates:
        try:
            d = _stock_json.loads(cand)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, list):
            return {"results": [r for r in d if isinstance(r, dict)]}
        if isinstance(d, dict):
            if isinstance(d.get("results"), list):
                return d
            if "metExpectation" in d:  # a single result object
                return {"results": [d]}
    raise ValueError("judge reply: no JSON object or array found")


class _JsonShim:
    """Stands in for the `json` module inside evaluator_nl_assertions: `loads` is tolerant and records the call."""

    @staticmethod
    def loads(raw: str):
        rec = getattr(_last_lock, "rec", None)
        ok = strict_loads_ok(raw)
        try:
            data = tolerant_loads(raw)
            n_results = len(data.get("results", []))
            err = ""
        except ValueError as e:
            data, n_results, err = None, 0, str(e)
        with _LOCK:
            if rec is not None:
                rec.update({"strict_ok": int(ok), "n_results": n_results, "parse_error": err})
                CALLS.append(rec)
                TOTALS["calls"] += 1
                TOTALS["in_tokens"] += rec.get("in_tokens", 0)
                TOTALS["out_tokens"] += rec.get("out_tokens", 0)
                TOTALS["strict_rejected"] += int(not ok)
                TOTALS["unparsed"] += int(bool(err))
                TOTALS["results_short"] += int(n_results < rec.get("n_assertions", 0))
        _last_lock.rec = None
        if data is None:
            raise ValueError(err)
        return data

    def __getattr__(self, name):
        return getattr(_stock_json, name)


def _logged_generate(model: str, messages, **kwargs):
    reply = _stock_generate(model=model, messages=messages, **kwargs)
    usage = getattr(reply, "usage", None) or {}
    get = (lambda k: usage.get(k)) if isinstance(usage, dict) else (lambda k: getattr(usage, k, None))
    user_prompt = next((m.content for m in messages if getattr(m, "role", "") == "user"), "") or ""
    n_assertions = 0
    m = re.search(r"expectedOutcomes:\s*(\[[\s\S]*\])\s*$", user_prompt.strip())
    if m:
        try:
            import ast
            n_assertions = len(ast.literal_eval(m.group(1)))
        except Exception:  # noqa: BLE001
            n_assertions = m.group(1).count("', '") + m.group(1).count('", "') + 1
    _last_lock.rec = {"model": model, "n_assertions": n_assertions, "in_tokens": int(get("prompt_tokens") or 0),
                      "out_tokens": int(get("completion_tokens") or 0), "raw": (reply.content or "")[:6000],
                      "prompt_sha": __import__("hashlib").sha256(user_prompt.encode("utf-8")).hexdigest()[:16]}
    return reply


def install() -> dict:
    """Patch the evaluator module in-process and return the provenance dict."""
    nle.DEFAULT_LLM_NL_ASSERTIONS = JUDGE_MODEL
    nle.DEFAULT_LLM_NL_ASSERTIONS_ARGS = dict(JUDGE_ARGS)
    nle.generate = _logged_generate
    nle.json = _JsonShim()
    return provenance()


def provenance() -> dict:
    import hashlib
    import inspect
    src = inspect.getsource(nle.NLAssertionsEvaluator.evaluate_nl_assertions)
    return {"judge_model": JUDGE_MODEL, "judge_args": JUDGE_ARGS, "judge_votes": 1, "judge_view": "stock (role: content)",
            "judge_parser": "tolerant (fence / bare array accepted); strict_ok recorded per reply",
            "stock_evaluate_nl_assertions_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest()[:16],
            "stock_default_model": "gpt-5.4-mini-2026-03-17", "stock_default_args": {"reasoning_effort": "low"}}


def drain() -> list[dict]:
    with _LOCK:
        out = list(CALLS)
        CALLS.clear()
    return out


def totals() -> dict:
    with _LOCK:
        t = dict(TOTALS)
    t["own_estimate_usd"] = t["in_tokens"] / 1e6 * PRICE_IN + t["out_tokens"] / 1e6 * PRICE_OUT
    return t


def reset_totals() -> None:
    with _LOCK:
        for k in TOTALS:
            TOTALS[k] = 0


def selftest() -> None:
    assert strict_loads_ok('{"results": []}') and not strict_loads_ok('[{"a": 1}]') and not strict_loads_ok('```json\n{"results": []}\n```')
    assert tolerant_loads('[{"metExpectation": true}]')["results"][0]["metExpectation"] is True
    assert tolerant_loads('```json\n{"results": [{"metExpectation": false}]}\n```')["results"][0]["metExpectation"] is False
    assert tolerant_loads('Sure.\n{"results": [{"metExpectation": true}]}')["results"]
    assert tolerant_loads('{"expectedOutcome": "x", "metExpectation": true, "reasoning": ""}')["results"][0]["metExpectation"] is True
    try:
        tolerant_loads("no json here")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("judge_overlay selftest ok")


if __name__ == "__main__":
    selftest()
