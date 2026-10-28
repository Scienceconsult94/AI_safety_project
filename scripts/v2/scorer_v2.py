"""Scorer v2 for the tau2-bench airline domain — an overlay, the pinned clone is not edited.

Three independent switches (block2/PLAN.md §1.1), all off by default so that importing this
module changes nothing until `install()` is called and a switch is turned on:

  hash_canon     DB hash insensitive to the order of order-free lists (passengers,
                 saved_passengers, user reservation ids, payment_history as a multiset) and to
                 which generated id (HATHAT/HATHAU/HATHAV, certificate_3221322..) a new object
                 received; itinerary order (Reservation.flights) is kept; float amounts rounded
                 to cents. Answers audit rows 2h (tasks 8, 20, 23), issue I3.
  comm_boundary  communicate_info strings must appear as whole tokens: a number is matched only
                 when not glued to other word characters or a decimal point (thousands separators
                 normalised on both sides, ".00" tolerated); words on word boundaries. Answers
                 rows 2g (tasks 3, 23), I4.
  nl_enforce     nl_assertions judged by anthropic/claude-haiku-5-5 (3 votes, majority); a
                 trajectory with no agent text beyond the orchestrator's canned greeting fails
                 every assertion without a judge call; assertions are numbered in the prompt and
                 mapped back one-to-one by index (then exact text, then position); a reply that
                 cannot be parsed or omits an assertion is re-asked once, after which the
                 assertion is "undetermined" (reported with lower/upper bounds; the reward uses
                 the lower bound). The reward multiplies the NL part only when NL_ASSERTION is in
                 the task's reward_basis, so callers use `with_nl_basis(task)`. Answers rows
                 2a/2b (no-op pass), 2k, issue I1.

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
import subprocess
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
from tau2.orchestrator.orchestrator import DEFAULT_FIRST_AGENT_MESSAGE  # noqa: E402
from tau2.utils.llm_utils import extract_json_from_llm_response, generate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SCORER_VERSION = "v2"
JUDGE_MODEL = "anthropic/claude-haiku-5-5"
JUDGE_ARGS: dict[str, Any] = {}  # provider defaults; no temperature (current Anthropic models reject a non-default value, issue I5)
JUDGE_VOTES = 3
JUDGE_RETRIES = 1  # re-asks after an unparseable reply or a missing assertion
JUDGE_VIEW = "with_tool_calls"  # "stock" = tau2's own view (role: content; tool-call arguments invisible)
GREETING = DEFAULT_FIRST_AGENT_MESSAGE.content


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
# provenance
# --------------------------------------------------------------------------------------


def git_state() -> tuple[str, bool]:
    """(short commit of the overlay repo, dirty flag for scripts/v2 and block2)."""
    try:
        commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "scripts/v2", "block2"], text=True).strip())
        return commit, dirty
    except Exception:  # noqa: BLE001
        return "unknown", True


def provenance() -> dict:
    commit, dirty = git_state()
    return {
        "scorer_version": SCORER_VERSION, "overlay_commit": commit, "overlay_dirty": dirty,
        "judge_model": JUDGE_MODEL, "judge_args": JUDGE_ARGS, "judge_votes": JUDGE_VOTES, "judge_view": JUDGE_VIEW,
        "judge_prompt_sha256": hashlib.sha256(_SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:16],
        "switches": vars(SWITCHES).copy(),
    }


def require_clean(what: str) -> None:
    """PLAN.md rule 4: no v2 number from an uncommitted overlay (override: V2_ALLOW_DIRTY=1)."""
    commit, dirty = git_state()
    if dirty and os.environ.get("V2_ALLOW_DIRTY") != "1":
        raise SystemExit(f"{what}: scripts/v2 or block2 has uncommitted changes (commit {commit}); commit first or set V2_ALLOW_DIRTY=1")


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
    """Canonical form of a FlightDB.model_dump() (see module docstring). Pure function.

    Generated payment-method ids (send_certificate) are remapped in users[*].payment_methods;
    references to them inside payment_history are not remapped (no airline tool pays with a
    certificate issued in the same episode, so this cannot matter for the pinned tasks)."""
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
        # not glued to other word characters or a decimal point; ".00" after an integer tolerated.
        # Known false-positive classes that remain: a time ("4:00"), a date part ("May 4") or a percentage ("4%")
        # when the target is that same number; known false negative: a spelled-out number ("four").
        return re.compile(rf"(?<![\w.]){re.escape(s)}(?:\.0+)?(?!\w|\.\d)")
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

JUDGE_LOG: list[dict] = []  # one row per vote per assertion (exported by the callers)
RAW_REPLIES: list[dict] = []  # raw judge replies of this process (exported by the callers)
_JUDGE_CACHE: dict[str, list[dict]] = {}  # key -> per-assertion summaries
_JUDGE_CACHE_PATH: Optional[Path] = None
_JUDGE_LOCK = threading.Lock()
JUDGE_COST = {"calls": 0, "cost": 0.0, "in_tokens": 0, "out_tokens": 0, "retries": 0}

# tau2's prompt (evaluator_nl_assertions.py:78-98, identical up to whitespace) plus one change: the
# expected outcomes are numbered and the reply must carry the number, so that each verdict can be
# mapped back to its assertion one-to-one (design review, block2/skeptic_design.md C3).
_SYSTEM_PROMPT = """
TASK
- You will be given a numbered list of expected outcomes and a conversation that was collected during a test case run.
- The conversation is between an agent and a customer.
- Your job is to evaluate whether the agent satisfies each of the expected outcomes.
- Grade each expected outcome individually. Return exactly one result per expected outcome, in the same order.

FORMAT
- Your response should be a JSON object with the following fields:
- `index`: the number of the expected outcome you are grading (as given in the input)
- `expectedOutcome`: repeat the expectation from the input that you are grading
- `reasoning`: a short explanation for your classification
- `metExpectation`: `true` if the agent satisfies the expected outcome, `false` otherwise

Example response structure:
{
    "results": [
        {
            "index": 1,
            "expectedOutcome": "<expected outcome number 1 from the input>",
            "reasoning": "<reasoning trace>",
            "metExpectation": <false or true>
        }
    ]
}
"""


def set_judge_cache(path: Path) -> None:
    global _JUDGE_CACHE_PATH
    _JUDGE_CACHE_PATH = path
    _JUDGE_CACHE.clear()
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
    """Transcript shown to the judge.

    tau2's NLAssertionsEvaluator renders `role: content` only, so an assistant turn that is a tool
    call reads "assistant: None" and the judge cannot see which tool was called with which
    arguments (observed 2026-10-27 on task 9 trial 1: `search_direct_flight(JFK, MCO, 2024-05-22)`
    was called and the judge unanimously marked the search assertion unmet). The v2 view appends
    the tool calls to the assistant turn and labels tool results; PLAN.md "Deviations" records it.
    """
    if JUDGE_VIEW == "stock":
        return "\n".join(f"{m.role}: {m.content}" for m in trajectory)
    lines = []
    for m in trajectory:
        if isinstance(m, AssistantMessage) and getattr(m, "tool_calls", None):
            calls = "; ".join(f"{tc.name}({json.dumps(tc.arguments, default=str, ensure_ascii=False)})" for tc in m.tool_calls)
            text = m.content if m.has_text_content() else ""
            lines.append(f"assistant: {text}".rstrip() + f"\n  [tool calls: {calls}]")
        elif m.role == "tool":
            lines.append(f"tool result: {m.content}")
        else:
            lines.append(f"{m.role}: {m.content}")
    return "\n".join(lines)


def has_agent_text(trajectory: list[Message]) -> bool:
    """True if the agent said anything beyond the orchestrator's canned opening greeting."""
    for i, m in enumerate(trajectory):
        if not isinstance(m, AssistantMessage) or not m.has_text_content():
            continue
        if i == 0 and m.content == GREETING and not getattr(m, "tool_calls", None):
            continue
        return True
    return False


def judge_key(trajectory: list[Message], nl_assertions: list[str]) -> str:
    cfg = f"{JUDGE_MODEL}|{_key(JUDGE_ARGS)}|{JUDGE_VIEW}|{JUDGE_VOTES}|{hashlib.sha256(_SYSTEM_PROMPT.encode()).hexdigest()[:12]}"
    return hashlib.sha256((cfg + "\n##\n" + trajectory_text(trajectory) + "\n##\n" + _key(nl_assertions)).encode("utf-8")).hexdigest()


def _map_results(results: list, nl_assertions: list[str]) -> list[dict]:
    """One-to-one mapping of judge results to assertions: index, then exact text, then position."""
    out: list[Optional[dict]] = [None] * len(nl_assertions)
    used: set[int] = set()
    items = [r for r in results if isinstance(r, dict)]
    # 1. by index
    for j, r in enumerate(items):
        try:
            i = int(r.get("index")) - 1
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(nl_assertions) and out[i] is None and j not in used:
            out[i] = {**r, "_mode": "index"}
            used.add(j)
    # 2. by exact normalised text
    for i, a in enumerate(nl_assertions):
        if out[i] is not None:
            continue
        for j, r in enumerate(items):
            if j not in used and _norm(str(r.get("expectedOutcome", ""))) == _norm(a):
                out[i] = {**r, "_mode": "text"}
                used.add(j)
                break
    # 3. by position, only when the counts agree
    if len(items) == len(nl_assertions):
        for i in range(len(nl_assertions)):
            if out[i] is None and i not in used:
                out[i] = {**items[i], "_mode": "position"}
                used.add(i)
    mapped = []
    for i, a in enumerate(nl_assertions):
        r = out[i]
        if r is None or not isinstance(r.get("metExpectation"), bool):
            mapped.append({"met": None, "reasoning": "", "mode": "missing"})
        else:
            mapped.append({"met": bool(r["metExpectation"]), "reasoning": str(r.get("reasoning", ""))[:500], "mode": r["_mode"]})
    return mapped


def _call_judge(trajectory_str: str, nl_assertions: list[str]) -> tuple[list, str, str]:
    numbered = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(nl_assertions))
    user_prompt = f"\nconversation:\n{trajectory_str}\n\nexpectedOutcomes:\n{numbered}\n"
    msgs = [SystemMessage(role="system", content=_SYSTEM_PROMPT), UserMessage(role="user", content=user_prompt)]
    reply = generate(model=JUDGE_MODEL, messages=msgs, call_name="nl_assertions_eval_v2", **JUDGE_ARGS)
    usage = getattr(reply, "usage", None) or {}
    with _JUDGE_LOCK:
        JUDGE_COST["calls"] += 1
        JUDGE_COST["cost"] += float(getattr(reply, "cost", 0.0) or 0.0)
        JUDGE_COST["in_tokens"] += int((usage.get("prompt_tokens") if isinstance(usage, dict) else getattr(usage, "prompt_tokens", 0)) or 0)
        JUDGE_COST["out_tokens"] += int((usage.get("completion_tokens") if isinstance(usage, dict) else getattr(usage, "completion_tokens", 0)) or 0)
    raw = reply.content or ""
    results, err = parse_judge_reply(raw)
    return results, raw, err


def parse_judge_reply(raw: str) -> tuple[list, str]:
    """Judge reply -> list of result objects. Accepts {"results": [...]}, a bare top-level JSON array (Haiku returns one in
    ~9% of replies; tau2's extract_json_from_llm_response slices from the first '{' to the last '}' and then fails with
    'Extra data'), with or without a code fence. Returns ([], error) when nothing parses."""
    text = raw.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    candidates = [m.group(1).strip()] if m else []
    candidates += [text, extract_json_from_llm_response(raw)]
    last_err = ""
    for cand in candidates:
        try:
            data = json.loads(cand)
        except Exception as e:  # noqa: BLE001
            last_err = repr(e)[:120]
            continue
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)], ""
        if isinstance(data, dict):
            res = data.get("results", [])
            return ([r for r in res if isinstance(r, dict)] if isinstance(res, list) else []), ""
        last_err = f"unexpected JSON type {type(data).__name__}"
    return [], last_err or "no JSON found"


def _one_vote(trajectory_str: str, nl_assertions: list[str], vote: int, key: str = "") -> list[dict]:
    """One ballot: a judge call, re-asked up to JUDGE_RETRIES times while any assertion is missing."""
    mapped: list[dict] = []
    for attempt in range(1 + JUDGE_RETRIES):
        results, raw, err = _call_judge(trajectory_str, nl_assertions)
        mapped = _map_results(results, nl_assertions)
        with _JUDGE_LOCK:
            RAW_REPLIES.append({"key": key[:16], "vote": vote, "attempt": attempt, "parse_error": err, "n_results": len(results), "raw": raw[:4000]})
        if all(m["met"] is not None for m in mapped):
            break
        with _JUDGE_LOCK:
            JUDGE_COST["retries"] += 1
    return mapped


def judge_nl_assertions(trajectory: list[Message], nl_assertions: list[str], votes: int = JUDGE_VOTES) -> list[dict]:
    """Per assertion: {met (bool|None), votes_met, votes_unmet, votes_undetermined, votes, reasoning, rule, modes}.
    `met` is the majority of determined votes; None when no vote was determined. Cached by
    (judge settings, prompt, view, trajectory, assertions)."""
    if not has_agent_text(trajectory):
        return [{"met": False, "votes_met": 0, "votes_unmet": 0, "votes_undetermined": 0, "votes": 0,
                 "reasoning": "empty-trajectory rule: no assistant text beyond the canned greeting", "rule": "empty", "modes": ""} for _ in nl_assertions]
    key = judge_key(trajectory, nl_assertions)
    with _JUDGE_LOCK:
        cached = _JUDGE_CACHE.get(key)
    if cached is not None and len(cached) == len(nl_assertions):
        return cached
    traj = trajectory_text(trajectory)
    ballots = [_one_vote(traj, nl_assertions, v, key) for v in range(votes)]
    summary = []
    for i, a in enumerate(nl_assertions):
        vm = sum(1 for b in ballots if b[i]["met"] is True)
        vu = sum(1 for b in ballots if b[i]["met"] is False)
        vn = sum(1 for b in ballots if b[i]["met"] is None)
        met: Optional[bool] = None if vm + vu == 0 else vm > vu if vm != vu else None
        reasons = [b[i]["reasoning"] for b in ballots if b[i]["met"] == met and b[i]["reasoning"]]
        summary.append({"met": met, "votes_met": vm, "votes_unmet": vu, "votes_undetermined": vn, "votes": votes,
                        "reasoning": reasons[0] if reasons else "", "rule": "judge", "modes": "/".join(b[i]["mode"] for b in ballots)})
        for v, b in enumerate(ballots):
            JUDGE_LOG.append({"key": key[:16], "assertion_idx": i, "assertion": a, "vote": v,
                              "met": "" if b[i]["met"] is None else int(b[i]["met"]), "mode": b[i]["mode"]})
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
                met=bool(r["met"]),  # undetermined -> unmet (lower bound); the upper bound is reported from the vote counts
                justification=f"[v2 {r['rule']} met={r['votes_met']} unmet={r['votes_unmet']} undetermined={r['votes_undetermined']} of {r['votes']}; {r['modes']}] {r['reasoning']}",
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

    me = sys.modules[__name__]  # this very module (may be __main__), so patches reach the judge code
    fails: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(("ok   " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    # block every real model call for the whole selftest
    import tau2.utils.llm_utils as lu

    def blocked(*a, **k):
        raise RuntimeError("model call blocked in selftest")

    real_generate = me.generate
    me.generate = blocked  # type: ignore[assignment]
    lu.generate = blocked  # type: ignore[assignment]

    try:
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
            ("41", "Flight HAT041 is nonstop.", False),
            ("nonstop", "HAT041 is a nonstop flight.", True),
            ("stop", "HAT041 is a nonstop flight.", False),
            ("HAT041", "Flight hat041 departs at 10:00.", True),
        ]
        for info, text, exp in cases:
            check(info_in_text(info, text) == exp, f"comm_boundary {info!r} in {text!r} -> {exp}")
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
        delta = 30 * len(b3.arguments["passengers"])  # insurance is $30 per passenger
        if b3.arguments["insurance"] == "yes":
            b3.arguments["insurance"], b3.arguments["payment_methods"][0]["amount"] = "no", b3.arguments["payment_methods"][0]["amount"] - delta
        else:
            b3.arguments["insurance"], b3.arguments["payment_methods"][0]["amount"] = "yes", b3.arguments["payment_methods"][0]["amount"] + delta
        check(canonical_hash(gold) != canonical_hash(replay(acts3)), "task 8: canonical hash differs for a different insurance choice (negative control)")

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
        db0 = get_db()
        check(set(canonical_dump(db0.model_dump())["reservations"]) == set(db0.reservations), "canonical form keeps original reservation ids")

        install()
        env = env_ctor()
        SWITCHES.set(False, False, False)
        check(env.get_db_hash() == raw_hash(env.tools.db), "hook off: get_db_hash == raw hash")
        SWITCHES.set(True, False, False)
        check(env.get_db_hash() == canonical_hash(env.tools.db), "hook on: get_db_hash == canonical hash")
        SWITCHES.set(False, False, False)

        # --- nl: empty-trajectory rule (no model call), greeting excluded
        from tau2.data_model.message import ToolCall

        SWITCHES.set(False, False, True)
        greeting = AssistantMessage(role="assistant", content=GREETING)
        user = UserMessage(role="user", content="Hi, I want to cancel my flight.")
        res = V2NLAssertionsEvaluator.evaluate_nl_assertions([], ["Agent refuses."])
        check(len(res) == 1 and res[0].met is False, "empty trajectory: assertion not met, judge not called")
        res = V2NLAssertionsEvaluator.evaluate_nl_assertions([greeting, user], ["Agent refuses."])
        check(res[0].met is False, "greeting + one user turn (block-1 2b probe): assertion not met, judge not called")
        tool_only = [greeting, user, AssistantMessage(role="assistant", content=None, tool_calls=[ToolCall(id="x", name="get_user_details", arguments={"user_id": "u"})])]
        check(V2NLAssertionsEvaluator.evaluate_nl_assertions(tool_only, ["Agent refuses."])[0].met is False, "greeting + tool-only turn: not met, judge not called")
        check(has_agent_text([greeting, user, AssistantMessage(role="assistant", content="Sorry, I cannot do that.")]), "a real agent sentence counts as agent text")
        SWITCHES.set(False, False, False)

        # --- judge view shows tool calls
        txt = trajectory_text(tool_only)
        check("get_user_details" in txt and '"user_id": "u"' in txt, "with_tool_calls view renders tool name and arguments")

        # --- mapping: index first, reordered/paraphrased replies land on the right assertion
        A = ["Agent cancels XEHM4B.", "Agent does not cancel 59XX6W."]
        reply = {"results": [{"index": 2, "expectedOutcome": "The agent did not cancel reservation 59XX6W", "reasoning": "it did cancel", "metExpectation": False},
                             {"index": 1, "expectedOutcome": "Agent cancels XEHM4B.", "reasoning": "yes", "metExpectation": True}]}
        m = _map_results(reply["results"], A)
        check(m[0]["met"] is True and m[1]["met"] is False and m[0]["mode"] == "index", "reordered reply mapped by index")
        reply2 = {"results": [{"expectedOutcome": "Agent does not cancel 59XX6W.", "reasoning": "x", "metExpectation": False},
                              {"expectedOutcome": "Agent cancels XEHM4B.", "reasoning": "y", "metExpectation": True}]}
        m = _map_results(reply2["results"], A)
        check(m[0]["met"] is True and m[1]["met"] is False and m[0]["mode"] == "text", "reordered reply without index mapped by exact text")
        m = _map_results([{"expectedOutcome": "A", "reasoning": "r", "metExpectation": True}], A)
        check(m[0]["met"] is None and m[1]["met"] is None and m[0]["mode"] == "missing", "one unmatched result for two assertions -> both undetermined (no position guess)")

        # --- retry on parse failure, then undetermined; fenced JSON parsed
        calls = {"n": 0}

        def fake_bad(*a, **k):
            calls["n"] += 1
            return AssistantMessage(role="assistant", content="not json at all")

        me.generate = fake_bad  # type: ignore[assignment]
        v = _one_vote("assistant: hi", ["A"], 0)
        check(calls["n"] == 1 + JUDGE_RETRIES and v[0]["met"] is None and v[0]["mode"] == "missing", "unparseable reply: re-asked once, then undetermined")
        r, e = parse_judge_reply('[{"index": 1, "expectedOutcome": "x", "metExpectation": true, "reasoning": "r"}]')
        check(e == "" and len(r) == 1 and r[0]["metExpectation"] is True, "bare top-level JSON array parsed (the shape tau2's extractor rejects)")
        r, e = parse_judge_reply('```json' + chr(10) + '[{"index": 1, "metExpectation": false}]' + chr(10) + '```')
        check(e == "" and len(r) == 1 and r[0]["metExpectation"] is False, "fenced JSON array parsed")
        r, e = parse_judge_reply('{"results": [{"index": 1, "metExpectation": true}]}')
        check(e == "" and len(r) == 1, "object with results list parsed")
        r, e = parse_judge_reply("not json at all")
        check(r == [] and e != "", "non-JSON reply -> empty results with an error")
        good = {"results": [{"index": 1, "expectedOutcome": "A", "reasoning": "r", "metExpectation": True}]}
        me.generate = lambda *a, **k: AssistantMessage(role="assistant", content="```json\n" + json.dumps(good) + "\n```")  # type: ignore[assignment]
        check(_one_vote("assistant: hi", ["A"], 0)[0]["met"] is True, "fenced JSON reply parsed")
        # trailing comma (as in tau2's own example JSON) -> parse error -> retry -> undetermined, not 'unmet'
        me.generate = lambda *a, **k: AssistantMessage(role="assistant", content='{"results": [{"index": 1, "expectedOutcome": "A", "reasoning": "r", "metExpectation": true,}]}')  # type: ignore[assignment]
        check(_one_vote("assistant: hi", ["A"], 0)[0]["met"] is None, "trailing-comma reply -> undetermined, not unmet")

        # --- majority with undetermined votes
        me.generate = blocked  # type: ignore[assignment]
        JUDGE_COST.update({"calls": 0, "cost": 0.0, "in_tokens": 0, "out_tokens": 0, "retries": 0})
        RAW_REPLIES.clear()
        JUDGE_LOG.clear()

        t = with_nl_basis(tasks["32"])
        check(RewardType.NL_ASSERTION in t.evaluation_criteria.reward_basis and RewardType.NL_ASSERTION not in tasks["32"].evaluation_criteria.reward_basis, "with_nl_basis adds NL_ASSERTION on a copy")
        p = provenance()
        check(p["scorer_version"] == "v2" and "overlay_commit" in p and "judge_prompt_sha256" in p, "provenance stamp available")
    finally:
        me.generate = real_generate  # type: ignore[assignment]
        lu.generate = real_generate  # type: ignore[assignment]
        SWITCHES.set(False, False, False)

    print(f"\n{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
