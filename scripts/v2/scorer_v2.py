"""Scorer v2 for the tau2-bench airline domain — an overlay, the pinned clone is not edited.

Three independent switches (block2/PLAN.md §1.1), all off by default so that importing this
module changes nothing until `install()` is called and a switch is turned on:

  hash_canon     DB hash insensitive to the order of order-free lists (passengers,
                 saved_passengers, user reservation ids, payment_history as a multiset) and to
                 which generated id (HATHAT/HATHAU/HATHAV, certificate_3221322..) a new object
                 received; itinerary order (Reservation.flights) is kept; float amounts rounded
                 to cents. Answers audit rows 2h (tasks 8, 20, 23), issue I3.
  comm_boundary  communicate_info strings must appear as whole tokens: a number is matched only
                 when not glued to other digits (thousands separators normalised on both sides,
                 ".00" tolerated); words on word boundaries. Answers rows 2g (tasks 3, 23), I4.
  nl_enforce     nl_assertions judged by anthropic/claude-haiku-5-5 (3 votes, majority), an
                 empty or tool-only trajectory fails every assertion without a judge call, and a
                 judge reply that omits an assertion counts it as not met. The reward multiplies
                 the NL part only when NL_ASSERTION is in the task's reward_basis, so callers use
                 `with_nl_basis(task)`. Answers rows 2a/2b (no-op pass), 2k, issue I1.

Mechanism: `install()` swaps module globals that tau2.evaluator.evaluator.evaluate_simulation
reads at call time (CommunicateEvaluator, NLAssertionsEvaluator) and wraps
ToolKitBase.get_db_hash. Nothing is written into tau2-bench/.

Selftest (no model call, run from inside tau2-bench):
    uv run --no-sync python ../scripts/v2/scorer_v2.py --selftest
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.data_model.message import AssistantMessage, Message, SystemMessage, UserMessage  # noqa: E402
from tau2.data_model.simulation import CommunicateCheck, NLAssertionCheck  # noqa: E402
from tau2.data_model.tasks import RewardType, Task  # noqa: E402
from tau2.domains.airline.data_model import FlightDB, get_db  # noqa: E402
from tau2.environment import toolkit as _toolkit  # noqa: E402
from tau2.evaluator import evaluator as _evaluator  # noqa: E402
from tau2.evaluator.evaluator_communicate import CommunicateEvaluator  # noqa: E402
from tau2.evaluator.evaluator_nl_assertions import NLAssertionsEvaluator  # noqa: E402
from tau2.utils.llm_utils import extract_json_from_llm_response, generate  # noqa: E402

SCORER_VERSION = "v2"
JUDGE_MODEL = "anthropic/claude-haiku-5-5"
JUDGE_ARGS: dict[str, Any] = {}  # no temperature: current Anthropic models reject a non-default value (issue I5)
JUDGE_VOTES = 3


@dataclass
class Switches:
    hash_canon: bool = False
    comm_boundary: bool = False
    nl_enforce: bool = False

    def set(self, hash_canon: bool, comm_boundary: bool, nl_enforce: bool) -> None:
        self.hash_canon, self.comm_boundary, self.nl_enforce = hash_canon, comm_boundary, nl_enforce

    def label(self) -> str:
        return "+".join(n for n, v in (("hash", self.hash_canon), ("comm", self.comm_boundary), ("nl", self.nl_enforce)) if v) or "stock"


SWITCHES = Switches()

# --------------------------------------------------------------------------------------
# hash_canon
# --------------------------------------------------------------------------------------

_INITIAL: dict[str, set[str]] | None = None


def _initial_ids() -> dict[str, set[str]]:
    """Ids present in the pinned db.json; anything else was created during the episode."""
    global _INITIAL
    if _INITIAL is None:
        db = get_db()
        pm = set()
        for u in db.users.values():
            pm.update(u.payment_methods.keys())
        _INITIAL = {"reservations": set(db.reservations.keys()), "payment_methods": pm}
    return _INITIAL


def _key(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def _round_amounts(obj: Any) -> Any:
    if isinstance(obj, float):
        return round(obj, 2)
    if isinstance(obj, dict):
        return {k: _round_amounts(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_amounts(v) for v in obj]
    return obj


def canonical_dump(dump: dict) -> dict:
    """Canonical form of a FlightDB.model_dump() (see module docstring). Pure function."""
    initial = _initial_ids()
    d = _round_amounts(copy.deepcopy(dump))

    # reservations: order-free inner lists, then content-derived ids for new reservations
    res_map: dict[str, str] = {}
    new_res: dict[str, dict] = {}
    for rid, r in list(d.get("reservations", {}).items()):
        r["passengers"] = sorted(r.get("passengers", []), key=_key)
        r["payment_history"] = sorted(r.get("payment_history", []), key=_key)
        # flights: itinerary order is semantic -> unchanged
        if rid not in initial["reservations"]:
            content = {k: v for k, v in r.items() if k != "reservation_id"}
            new_id = "NEW_RES:" + hashlib.sha256(_key(content).encode()).hexdigest()[:16]
            res_map[rid] = new_id
            new_res[rid] = r
    for rid, r in new_res.items():
        del d["reservations"][rid]
        nid = res_map[rid]
        while nid in d["reservations"]:  # identical content twice: keep both
            nid += "+"
        res_map[rid] = nid
        r["reservation_id"] = nid
        d["reservations"][nid] = r

    # users: saved passengers, reservation id list, generated payment methods
    for u in d.get("users", {}).values():
        u["saved_passengers"] = sorted(u.get("saved_passengers", []), key=_key)
        u["reservations"] = sorted(res_map.get(x, x) for x in u.get("reservations", []))
        pms = u.get("payment_methods", {})
        for pid in [p for p in pms if p not in initial["payment_methods"]]:
            pm = pms.pop(pid)
            content = {k: v for k, v in pm.items() if k != "id"}
            nid = "NEW_PM:" + hashlib.sha256(_key(content).encode()).hexdigest()[:16]
            while nid in pms:
                nid += "+"
            pm["id"] = nid
            pms[nid] = pm
    return d


def canonical_hash(db: FlightDB) -> str:
    return hashlib.sha256(_key(canonical_dump(db.model_dump())).encode()).hexdigest()


def raw_hash(db: FlightDB) -> str:
    return hashlib.sha256(_key(db.model_dump()).encode()).hexdigest()


def db_diff(a: dict, b: dict, prefix: str = "", limit: int = 30) -> list[str]:
    """Paths where two dumps differ (first `limit`), for evidence tables."""
    out: list[str] = []

    def walk(x: Any, y: Any, p: str) -> None:
        if len(out) >= limit:
            return
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                if k not in x:
                    out.append(f"{p}/{k}: only in B")
                elif k not in y:
                    out.append(f"{p}/{k}: only in A")
                else:
                    walk(x[k], y[k], f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                out.append(f"{p}: list len {len(x)} vs {len(y)}")
            for i, (xi, yi) in enumerate(zip(x, y)):
                walk(xi, yi, f"{p}[{i}]")
        elif x != y:
            out.append(f"{p}: {json.dumps(x, default=str)[:60]} vs {json.dumps(y, default=str)[:60]}")

    walk(a, b, prefix)
    return out


_ORIG_GET_DB_HASH = _toolkit.ToolKitBase.get_db_hash


def _get_db_hash_v2(self):  # type: ignore[no-untyped-def]
    if SWITCHES.hash_canon and isinstance(getattr(self, "db", None), FlightDB):
        return canonical_hash(self.db)
    return _ORIG_GET_DB_HASH(self)


# --------------------------------------------------------------------------------------
# comm_boundary
# --------------------------------------------------------------------------------------

_THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")
_NUMERIC = re.compile(r"\d+(?:\.\d+)?")


def normalize_text(text: str) -> str:
    return _THOUSANDS.sub("", text.lower())


def info_pattern(info: str) -> re.Pattern[str]:
    s = normalize_text(info).strip()
    if _NUMERIC.fullmatch(s):
        # not glued to other digits or a decimal point; ".00" after an integer tolerated
        return re.compile(rf"(?<![\d.]){re.escape(s)}(?:\.0+)?(?!\d|\.\d)")
    return re.compile(rf"(?<!\w){re.escape(s)}(?!\w)")


def info_in_text(info: str, text: str) -> bool:
    return info_pattern(info).search(normalize_text(text)) is not None


class V2CommunicateEvaluator(CommunicateEvaluator):
    @classmethod
    def evaluate_communicate_info(cls, full_trajectory, communicate_info, *, scoring, customer_language=None):  # type: ignore[override]
        from tau2.data_model.semantic_communication import CommunicateScorer

        if not SWITCHES.comm_boundary or scoring.scorer == CommunicateScorer.SEMANTIC:
            return super().evaluate_communicate_info(
                full_trajectory, communicate_info, scoring=scoring, customer_language=customer_language
            )
        outputs = []
        for info_str in communicate_info:
            pat = info_pattern(info_str)
            hit: Optional[str] = None
            for message in full_trajectory:
                if not isinstance(message, AssistantMessage) or not message.has_text_content():
                    continue
                if pat.search(normalize_text(message.content)):
                    hit = message.content
                    break
            outputs.append(
                CommunicateCheck(
                    info=info_str,
                    met=hit is not None,
                    justification=(
                        f"[v2 boundary] '{info_str}' found as a whole token in: '{hit[:200]}'"
                        if hit is not None
                        else f"[v2 boundary] '{info_str}' not found as a whole token in any assistant message"
                    ),
                )
            )
        return outputs


# --------------------------------------------------------------------------------------
# nl_enforce
# --------------------------------------------------------------------------------------

JUDGE_LOG: list[dict] = []  # one row per vote per assertion (exported by rescore.py)
_JUDGE_CACHE: dict[str, list[dict]] = {}  # key -> per-assertion summaries
_JUDGE_CACHE_PATH: Optional[Path] = None
_JUDGE_LOCK = threading.Lock()
JUDGE_COST = {"calls": 0, "cost": 0.0, "in_tokens": 0, "out_tokens": 0}

_SYSTEM_PROMPT = NLAssertionsEvaluator.evaluate_nl_assertions.__doc__ and """
        TASK
        - You will be given a list of expected outcomes and a conversation that was collected during a test case run.
        - The conversation is between an agent and a customer.
        - Your job is to evaluate whether the agent satisfies each of the expected outcomes.
        - Grade each expected outcome individually.

        FORMAT
        - Your response should be a JSON object with the following fields:
        - `reasoning`: a short explanation for your classification
        - `metExpectation`: `true` if the agent satisfies the expected outcomes, `false` otherwise
        - `expectedOutcome`: repeat the expectation from the input that you are grading

        Example response structure:
        {
            "results": [
                {
                    "expectedOutcome": "<one of the expected outcomes from the input>",
                    "reasoning": "<reasoning trace>",
                    "metExpectation": <false or true>,
                }
            ]
        }
        """  # identical to tau2 evaluator_nl_assertions.py:78-98 so that only the model differs


def set_judge_cache(path: Path) -> None:
    global _JUDGE_CACHE_PATH
    _JUDGE_CACHE_PATH = path
    if path.exists():
        _JUDGE_CACHE.update(json.loads(path.read_text(encoding="utf-8")))


def _save_cache() -> None:
    if _JUDGE_CACHE_PATH is not None:
        tmp = _JUDGE_CACHE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(_JUDGE_CACHE, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_JUDGE_CACHE_PATH)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def trajectory_text(trajectory: list[Message]) -> str:
    return "\n".join(f"{m.role}: {m.content}" for m in trajectory)  # same view as tau2


def has_agent_text(trajectory: list[Message]) -> bool:
    return any(isinstance(m, AssistantMessage) and m.has_text_content() for m in trajectory)


def judge_key(trajectory: list[Message], nl_assertions: list[str]) -> str:
    return hashlib.sha256((trajectory_text(trajectory) + "\n##\n" + _key(nl_assertions)).encode("utf-8")).hexdigest()


def _one_vote(trajectory_str: str, nl_assertions: list[str], vote: int) -> list[dict]:
    user_prompt = f"""
        conversation:
        {trajectory_str}

        expectedOutcomes:
        {nl_assertions}
        """
    msgs = [SystemMessage(role="system", content=_SYSTEM_PROMPT), UserMessage(role="user", content=user_prompt)]
    reply = generate(model=JUDGE_MODEL, messages=msgs, call_name="nl_assertions_eval_v2", **JUDGE_ARGS)
    cost = float(getattr(reply, "cost", 0.0) or 0.0)
    usage = getattr(reply, "usage", None) or {}
    with _JUDGE_LOCK:
        JUDGE_COST["calls"] += 1
        JUDGE_COST["cost"] += cost
        JUDGE_COST["in_tokens"] += int((usage.get("prompt_tokens") if isinstance(usage, dict) else getattr(usage, "prompt_tokens", 0)) or 0)
        JUDGE_COST["out_tokens"] += int((usage.get("completion_tokens") if isinstance(usage, dict) else getattr(usage, "completion_tokens", 0)) or 0)
    try:
        data = json.loads(extract_json_from_llm_response(reply.content or ""))
        results = data.get("results", []) if isinstance(data, dict) else []
    except Exception as e:  # unparseable reply: strict -> nothing met
        results = []
        parse_error = repr(e)
    else:
        parse_error = ""
    # map replies to assertions: by normalised text, else by position when counts agree
    by_text = {_norm(str(r.get("expectedOutcome", ""))): r for r in results if isinstance(r, dict)}
    out = []
    for i, a in enumerate(nl_assertions):
        r = by_text.get(_norm(a))
        if r is None and len(results) == len(nl_assertions) and isinstance(results[i], dict):
            r = results[i]
        if r is None:
            out.append({"met": False, "reasoning": f"[v2] assertion missing from judge reply {parse_error}".strip(), "matched": False})
        else:
            out.append({"met": bool(r.get("metExpectation", False)), "reasoning": str(r.get("reasoning", ""))[:500], "matched": True})
    return out


def judge_nl_assertions(trajectory: list[Message], nl_assertions: list[str], votes: int = JUDGE_VOTES) -> list[dict]:
    """Per assertion: {met, votes_met, votes, reasoning, rule}. Cached by (trajectory, assertions)."""
    if not has_agent_text(trajectory):
        return [{"met": False, "votes_met": 0, "votes": 0, "reasoning": "empty-trajectory rule: no assistant text, nothing to judge", "rule": "empty"} for _ in nl_assertions]
    key = judge_key(trajectory, nl_assertions)
    with _JUDGE_LOCK:
        cached = _JUDGE_CACHE.get(key)
    if cached is not None and len(cached) == len(nl_assertions):
        return cached
    traj = trajectory_text(trajectory)
    ballots = [_one_vote(traj, nl_assertions, v) for v in range(votes)]
    summary = []
    for i, a in enumerate(nl_assertions):
        met_votes = sum(1 for b in ballots if b[i]["met"])
        met = met_votes * 2 > votes
        reasons = [b[i]["reasoning"] for b in ballots if b[i]["met"] == met]
        summary.append({"met": met, "votes_met": met_votes, "votes": votes, "reasoning": reasons[0] if reasons else "", "rule": "judge"})
        for v, b in enumerate(ballots):
            JUDGE_LOG.append({"key": key[:16], "assertion_idx": i, "assertion": a, "vote": v, "met": int(b[i]["met"]), "matched": int(b[i]["matched"])})
    with _JUDGE_LOCK:
        _JUDGE_CACHE[key] = summary
        _save_cache()
    return summary


class V2NLAssertionsEvaluator(NLAssertionsEvaluator):
    @classmethod
    def evaluate_nl_assertions(cls, trajectory, nl_assertions):  # type: ignore[override]
        if not SWITCHES.nl_enforce:
            return super().evaluate_nl_assertions(trajectory, nl_assertions)
        res = judge_nl_assertions(trajectory, nl_assertions)
        return [
            NLAssertionCheck(
                nl_assertion=a,
                met=r["met"],
                justification=f"[v2 {r['rule']} {r['votes_met']}/{r['votes']}] {r['reasoning']}",
            )
            for a, r in zip(nl_assertions, res)
        ]


def with_nl_basis(task: Task) -> Task:
    """Copy of the task whose reward_basis includes NL_ASSERTION (so the NL part multiplies)."""
    t = task.model_copy(deep=True)
    if t.evaluation_criteria is not None and RewardType.NL_ASSERTION not in t.evaluation_criteria.reward_basis:
        t.evaluation_criteria.reward_basis = list(t.evaluation_criteria.reward_basis) + [RewardType.NL_ASSERTION]
    return t


# --------------------------------------------------------------------------------------
# install
# --------------------------------------------------------------------------------------

_INSTALLED = False


def install() -> None:
    """Idempotent. Swaps the evaluator components tau2 looks up at call time."""
    global _INSTALLED
    if _INSTALLED:
        return
    _toolkit.ToolKitBase.get_db_hash = _get_db_hash_v2  # type: ignore[assignment]
    _evaluator.CommunicateEvaluator = V2CommunicateEvaluator  # type: ignore[attr-defined]
    _evaluator.NLAssertionsEvaluator = V2NLAssertionsEvaluator  # type: ignore[attr-defined]
    _INSTALLED = True


# --------------------------------------------------------------------------------------
# selftest (no model calls)
# --------------------------------------------------------------------------------------


def _selftest() -> int:
    from tau2.registry import registry

    fails: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(("ok   " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    # --- comm_boundary
    cases = [
        ("4", "You can check 4 bags free of charge.", True),
        ("4", "Your flight on May 16, 2024 costs $149 and the 24-hour rule applies.", False),
        ("327", "You have $1,327 in certificates and gift cards combined.", False),
        ("327", "Your gift cards total $327 and certificates $1,000.", True),
        ("1000", "Your gift cards total $327 and certificates $1,000.", True),
        ("1628", "The total is $1,628.00 for those flights.", True),
        ("708", "The total comes to 708.5 dollars.", False),
        ("708", "The remaining flights total $708.", True),
        ("1286", "Your Mastercard will be charged $1,286.", True),
        ("1286", "reference 51286 applies", False),
        ("nonstop", "HAT041 is a nonstop flight.", True),
        ("stop", "HAT041 is a nonstop flight.", False),
        ("HAT041", "Flight hat041 departs at 10:00.", True),
    ]
    for info, text, exp in cases:
        check(info_in_text(info, text) == exp, f"comm_boundary {info!r} in {text!r} -> {exp}")
    # stock behaviour for the same collisions (documents what v1 did)
    check("4" in "May 16, 2024".lower().replace(",", ""), "v1 substring: '4' matches '2024' (the defect)")
    check("327" in "$1,327".replace(",", ""), "v1 substring: '327' matches '$1,327' (the defect)")

    # --- hash_canon on real tasks
    env_ctor = registry.get_env_constructor("airline")
    tasks = {t.id: t for t in registry.get_tasks_loader("airline")("base")}

    def replay(actions):
        env = env_ctor()
        env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
        for a in actions:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        return env.tools.db

    # task 8: passenger order in book_reservation
    acts = copy.deepcopy(tasks["8"].evaluation_criteria.actions)
    book = [a for a in acts if a.name == "book_reservation"][0]
    check(len(book.arguments["passengers"]) >= 2, "task 8 has >=2 passengers")
    gold = replay(acts)
    acts2 = copy.deepcopy(acts)
    b2 = [a for a in acts2 if a.name == "book_reservation"][0]
    b2.arguments["passengers"] = list(reversed(b2.arguments["passengers"]))
    alt = replay(acts2)
    check(raw_hash(gold) != raw_hash(alt), "task 8: raw hash differs when passengers are reversed (v1 defect)")
    check(canonical_hash(gold) == canonical_hash(alt), "task 8: canonical hash equal when passengers are reversed")
    acts3 = copy.deepcopy(acts)
    b3 = [a for a in acts3 if a.name == "book_reservation"][0]
    b3.arguments["insurance"] = "no" if b3.arguments["insurance"] == "yes" else "yes"  # same price only if 'no'->... so adjust payment
    if b3.arguments["insurance"] == "yes":  # insurance costs 30 per passenger: pay it from the first method
        b3.arguments["payment_methods"][0]["amount"] += 30 * len(b3.arguments["passengers"])
    else:
        b3.arguments["payment_methods"][0]["amount"] -= 30 * len(b3.arguments["passengers"])
    check(canonical_hash(gold) != canonical_hash(replay(acts3)), "task 8: canonical hash differs for a different insurance choice (negative control)")

    # task 20: payment_methods order in book_reservation -> payment_history order
    acts = copy.deepcopy(tasks["20"].evaluation_criteria.actions)
    book = [a for a in acts if a.name == "book_reservation"][0]
    check(len(book.arguments["payment_methods"]) >= 2, "task 20 has >=2 payment methods")
    gold = replay(acts)
    acts2 = copy.deepcopy(acts)
    b2 = [a for a in acts2 if a.name == "book_reservation"][0]
    b2.arguments["payment_methods"] = list(reversed(b2.arguments["payment_methods"]))
    alt = replay(acts2)
    check(raw_hash(gold) != raw_hash(alt), "task 20: raw hash differs when payment_methods are reversed (v1 defect)")
    check(canonical_hash(gold) == canonical_hash(alt), "task 20: canonical hash equal when payment_methods are reversed")

    # task 23: order of the three bookings -> generated ids swap
    acts = copy.deepcopy(tasks["23"].evaluation_criteria.actions)
    idx = [i for i, a in enumerate(acts) if a.name == "book_reservation"]
    check(len(idx) == 3, "task 23 has 3 bookings")
    gold = replay(acts)
    acts2 = copy.deepcopy(acts)
    acts2[idx[0]], acts2[idx[2]] = acts2[idx[2]], acts2[idx[0]]
    alt = replay(acts2)
    check(raw_hash(gold) != raw_hash(alt), "task 23: raw hash differs when bookings are reordered (v1 defect)")
    check(canonical_hash(gold) == canonical_hash(alt), "task 23: canonical hash equal when bookings are reordered")
    check(len(db_diff(gold.model_dump(), alt.model_dump())) > 0, "db_diff reports raw differences for task 23")
    check(db_diff(canonical_dump(gold.model_dump()), canonical_dump(alt.model_dump())) == [], "db_diff empty after canonicalisation")
    # the initial DB is unchanged by canonicalisation of ids (no new objects)
    db0 = get_db()
    check(set(canonical_dump(db0.model_dump())["reservations"]) == set(db0.reservations), "canonical form keeps original reservation ids")

    # --- hook: switch off -> stock hash; on -> canonical
    install()
    env = env_ctor()
    SWITCHES.set(False, False, False)
    check(env.get_db_hash() == raw_hash(env.tools.db), "hook off: get_db_hash == raw hash")
    SWITCHES.set(True, False, False)
    check(env.get_db_hash() == canonical_hash(env.tools.db), "hook on: get_db_hash == canonical hash")
    SWITCHES.set(False, False, False)

    # --- nl empty-trajectory rule, no model call
    me = sys.modules[__name__]  # this very module (may be __main__), so the patch reaches _one_vote

    called = []
    orig = me.generate
    me.generate = lambda *a, **k: called.append(1)  # type: ignore[assignment]
    try:
        SWITCHES.set(False, False, True)
        res = V2NLAssertionsEvaluator.evaluate_nl_assertions([], ["Agent refuses."])
        check(len(res) == 1 and res[0].met is False and not called, "empty trajectory: assertion not met, judge not called")
        from tau2.data_model.message import ToolCall

        tool_only = [AssistantMessage(role="assistant", content=None, tool_calls=[ToolCall(id="x", name="get_user_details", arguments={"user_id": "u"})])]
        res = V2NLAssertionsEvaluator.evaluate_nl_assertions(tool_only, ["Agent refuses."])
        check(res[0].met is False and not called, "tool-only trajectory: assertion not met, judge not called")
    finally:
        me.generate = orig  # type: ignore[assignment]
        SWITCHES.set(False, False, False)

    # --- vote mapping helper: missing assertion in reply -> not met
    fake_reply = {"results": [{"expectedOutcome": "A", "reasoning": "r", "metExpectation": True}]}
    me_gen = me.generate
    me.generate = lambda *a, **k: AssistantMessage(role="assistant", content=json.dumps(fake_reply))  # type: ignore[assignment]
    try:
        v = _one_vote("assistant: hi", ["A", "B"], 0)
        check(v[0]["met"] is True and v[1]["met"] is False and v[1]["matched"] is False, "judge reply missing an assertion -> that assertion not met")
        me.generate = lambda *a, **k: AssistantMessage(role="assistant", content="```json\n" + json.dumps(fake_reply) + "\n```")  # type: ignore[assignment]
        v = _one_vote("assistant: hi", ["A"], 0)
        check(v[0]["met"] is True, "fenced JSON reply parsed")
    finally:
        me.generate = me_gen  # type: ignore[assignment]
    JUDGE_COST.update({"calls": 0, "cost": 0.0, "in_tokens": 0, "out_tokens": 0})

    # with_nl_basis
    t = with_nl_basis(tasks["32"])
    check(RewardType.NL_ASSERTION in t.evaluation_criteria.reward_basis and RewardType.NL_ASSERTION not in tasks["32"].evaluation_criteria.reward_basis, "with_nl_basis adds NL_ASSERTION on a copy")

    print(f"\n{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
