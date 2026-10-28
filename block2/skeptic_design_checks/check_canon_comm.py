"""hash_canon soundness probes and comm_boundary battery (read-only; model calls blocked)."""
from __future__ import annotations

import copy
import json
import os
import re
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
from tau2.data_model.message import AssistantMessage  # noqa: E402
from tau2.data_model.simulation import Results  # noqa: E402
from tau2.registry import registry  # noqa: E402

ctor = registry.get_env_constructor("airline")
tasks = {t.id: t for t in registry.get_tasks_loader("airline")("base")}


def fresh():
    env = ctor()
    env.set_state(initialization_data=None, initialization_actions=None, message_history=[], strict=True)
    return env


def call(env, name, **kw):
    try:
        return env.make_tool_call(tool_name=name, requestor="assistant", **kw)
    except Exception as e:  # noqa: BLE001
        return f"ERROR {e}"


def same(a, b):
    return s2.canonical_hash(a.tools.db) == s2.canonical_hash(b.tools.db), s2.raw_hash(a.tools.db) == s2.raw_hash(b.tools.db)


print("=== A1: new certificate used in a booking; certificates sent in two orders ===")
u = "sophia_silva_7557"
book = dict(user_id=u, origin="ORD", destination="PHL", flight_type="one_way", cabin="economy",
            flights=[{"flight_number": "HAT271", "date": "2024-05-26"}],
            passengers=[{"first_name": "Sophia", "last_name": "Silva", "dob": "1957-10-05"}],
            total_baggages=0, nonfree_baggages=0, insurance="no")
A = fresh()
print(" ", call(A, "send_certificate", user_id=u, amount=200))
print(" ", call(A, "send_certificate", user_id=u, amount=300))
r = call(A, "book_reservation", payment_methods=[{"payment_id": "certificate_3221322", "amount": 174}], **book)
print("  A booking:", r if isinstance(r, str) else r.payment_history)
B = fresh()
print(" ", call(B, "send_certificate", user_id=u, amount=300))
print(" ", call(B, "send_certificate", user_id=u, amount=200))
r = call(B, "book_reservation", payment_methods=[{"payment_id": "certificate_3221323", "amount": 174}], **book)
print("  B booking:", r if isinstance(r, str) else r.payment_history)
print("  (canonical equal, raw equal) =", same(A, B), " <- semantically identical end states")
print("  canonical diff:", s2.db_diff(s2.canonical_dump(A.tools.db.model_dump()), s2.canonical_dump(B.tools.db.model_dump()), limit=6))

print("\n=== A1b: the same two certificates WITHOUT a booking ===")
A2 = fresh(); call(A2, "send_certificate", user_id=u, amount=200); call(A2, "send_certificate", user_id=u, amount=300)
B2 = fresh(); call(B2, "send_certificate", user_id=u, amount=300); call(B2, "send_certificate", user_id=u, amount=200)
print("  (canonical equal, raw equal) =", same(A2, B2))

print("\n=== A1c: two identical bookings (duplicate) vs one booking ===")
D2 = fresh(); r1 = call(D2, "book_reservation", payment_methods=[{"payment_id": "certificate_8045380", "amount": 174}], **book)
D1 = fresh(); call(D1, "book_reservation", payment_methods=[{"payment_id": "certificate_8045380", "amount": 174}], **book)
print("  second booking with the same certificate (certificate consumed):", str(call(D2, "book_reservation", payment_methods=[{"payment_id": "certificate_8045380", "amount": 174}], **book))[:80])
E1 = fresh(); E2 = fresh()
cc = [p for p in E1.tools.db.users[u].payment_methods if p.startswith("credit_card")][0]
call(E1, "book_reservation", payment_methods=[{"payment_id": cc, "amount": 174}], **book)
call(E2, "book_reservation", payment_methods=[{"payment_id": cc, "amount": 174}], **book)
call(E2, "book_reservation", payment_methods=[{"payment_id": cc, "amount": 174}], **book)
cd = s2.canonical_dump(E2.tools.db.model_dump())
new = sorted(k for k in cd["reservations"] if k.startswith("NEW_RES"))
print("  duplicate bookings -> canonical ids:", new, "| user list:", [x for x in cd["users"][u]["reservations"] if x.startswith("NEW")])
print("  one vs two identical bookings (canonical equal) =", same(E1, E2)[0])

print("\n=== A3: itinerary order (task 23 gold booking with flights listed return-first) ===")
acts = copy.deepcopy(tasks["23"].evaluation_criteria.actions)
G = fresh()
for a in acts:
    call(G, a.name, **a.arguments)
acts2 = copy.deepcopy(acts)
for a in acts2:
    if a.name == "book_reservation":
        a.arguments["flights"] = [a.arguments["flights"][1], a.arguments["flights"][2], a.arguments["flights"][0]]
H = fresh()
for a in acts2:
    call(H, a.name, **a.arguments)
print("  (canonical equal, raw equal) =", same(G, H), "- same segments, same prices, list order differs")

print("\n=== A-residue: probe_2h_v2 orders that still differ (task 7: 102|120|210; task 32: 10) ===")
for tid, order in (("7", "102"), ("7", "021"), ("32", "10")):
    actions = list(tasks[tid].evaluation_criteria.actions)
    env0 = fresh()
    widx = [i for i, a in enumerate(actions) if env0.tools.tool_type(a.name).value == "write"]
    writes = [actions[i] for i in widx]
    var = list(actions)
    for slot, src in zip(widx, map(int, order)):
        var[slot] = writes[src]
    Gd = fresh(); [call(Gd, a.name, **a.arguments) for a in actions]
    Vd = fresh(); errs = [x for x in (call(Vd, a.name, **a.arguments) for a in var) if isinstance(x, str) and x.startswith("ERROR")]
    eq = same(Gd, Vd)
    print(f"  task {tid} order {order} ({' -> '.join(w.name + ':' + w.arguments.get('reservation_id', '') for w in (writes[int(c)] for c in order))}): canonical equal={eq[0]} errors={errs}")
    for line in s2.db_diff(s2.canonical_dump(Gd.tools.db.model_dump()), s2.canonical_dump(Vd.tools.db.model_dump()), limit=6):
        print("      ", line)

print("\n=== B: comm_boundary battery ===")
cases = [
    ("1000", "$1,000.00"), ("1000", "1000 dollars"), ("1000", "1,000"), ("1000", "USD 1000"), ("1000", "total: 1000."),
    ("1000", "(1000)"), ("1000", "1000%"), ("1000", "1000/"), ("1387", "$1,387"), ("1387", "$1387.00"), ("1387", "1 387"),
    ("1387", "1.387"), ("1387", "$1,387.50"), ("1387", "one thousand three hundred eighty-seven"), ("1387", "1,387,000"),
    ("708", "Flight HAT708 departs at 10:00"), ("708", "$402 + $306 = $708"), ("708", "708.00"), ("708", "$708,"),
    ("708", "$402, $306 (total 708)"), ("708", "402,306"), ("708", "-$708"), ("708", "708k"),
    ("4", "You can bring 4 suitcases."), ("4", "You can bring four suitcases."), ("4", "Your flight departs at 4:15 PM."),
    ("4", "The flight is on May 4."), ("4", "on 5/4/2024"), ("4", "the 4th of May"), ("4", "reservation MZDDS4"),
    ("4", "reservation 4WQ150"), ("4", "a 4% fee"), ("4", "Terminal 4"), ("4", "2024-05-04"), ("4", "4 free bags per... no, 2"),
    ("1286", "$1,286.00"), ("1286", "$1286"), ("23553", "$23,553"), ("23553", "$23 553"), ("5244", "$5,244.00"),
    ("327", "$327.00 and $1,000.00"), ("327", "$1,327"), ("327", "$1 327"),
]
for info, text in cases:
    print(f"  info={info!r:8} text={text!r:45} v2={s2.info_in_text(info, text)!s:5} v1={info.lower() in text.lower().replace(',', '')}")

print("\n=== B2: standalone '4' tokens in the recorded task-3 transcripts (assistant text) ===")
for fn in ("sample20_pass3_haiku.results.json", "sample20_gt_haiku.results.json"):
    res = Results.load(ROOT / "results" / "runs" / fn)
    for sim in res.simulations:
        if sim.task_id != "3":
            continue
        hits = []
        for i, m in enumerate(sim.messages):
            if isinstance(m, AssistantMessage) and m.has_text_content():
                t = s2.normalize_text(m.content)
                for mm in s2.info_pattern("4").finditer(t):
                    hits.append((i, t[max(0, mm.start() - 30): mm.end() + 25].replace("\n", " ")))
        print(f"  {fn[:18]} t{sim.trial} reward={sim.reward_info.reward}: {len(hits)} standalone '4' hits")
        for h in hits[:6]:
            print("     ", h)
print("\ndone; no model call")
