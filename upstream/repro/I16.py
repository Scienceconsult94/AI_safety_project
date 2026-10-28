"""I16: retail task texts that a scenario-faithful user cannot follow to the reference
(tasks 0, 1, 100, 52, 34, 15). Static checks against db.json.

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I16.py
"""

import json
import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from tau2.registry import registry  # noqa: E402

TASKS = {t.id: t for t in registry.get_tasks_loader("retail")("base")}
db = registry.get_env_constructor("retail")().tools.db
dump = json.dumps(db.model_dump())


def variants(name):
    product = next(p for p in db.products.values() if p.name == name)
    return {vid: v for vid, v in product.variants.items()}


def reason(tid):
    return TASKS[tid].user_scenario.instructions.reason_for_call


# (a) tasks 0 and 1: "Google Home"
thermostats = variants("Smart Thermostat")
print(f"(a) 'Google Home' in task 0 / task 1 text: {'Google Home' in reason('0')} / {'Google Home' in reason('1')}; "
      f"occurrences of 'Google Home' in db.json: {dump.count('Google Home')}")
print("    Smart Thermostat variants:", {vid: (dict(v.options).get('compatibility'), v.available) for vid, v in thermostats.items()})
print(f"    reference new item for the thermostat: {TASKS['0'].evaluation_criteria.actions[-1].arguments['new_item_ids'][-1]}")

# (b) task 100: two available skateboards match the stated options
wanted = {"length": "34 inch", "design": "custom"}
matches = {vid: (v.options.get("deck material"), v.price) for vid, v in variants("Skateboard").items()
           if v.available and all(v.options.get(k) == x for k, x in wanted.items())}
print(f"(b) task 100 asks for {wanted}; available matches: {matches}; "
      f"reference picks {TASKS['100'].evaluation_criteria.actions[0].arguments['new_item_ids'][1]}")

# (c) task 52: the reference camera changes the resolution
cams = variants("Digital Camera")
ref = TASKS["52"].evaluation_criteria.actions[-1].arguments
old, new = cams[ref["item_ids"][0]].options, cams[ref["new_item_ids"][0]].options
same_specs = {vid: dict(v.options) for vid, v in cams.items() if v.available and v.options["resolution"] == old["resolution"]
              and v.options["storage"] == old["storage"]}
print(f"(c) task 52: ordered {dict(old)} -> reference {dict(new)}; available variants with the same resolution and storage: {same_specs}")

# (d) task 34: the reference address is the profile address; the scenario never states the street
task = TASKS["34"]
write = task.evaluation_criteria.actions[-1].arguments
user = db.users[db.orders[write["order_id"]].user_id]
text = " ".join(str(x) for x in task.user_scenario.instructions.model_dump().values())
print(f"(d) task 34: reference address {write['address1']}, {write['address2']}, {write['zip']} == profile address: "
      f"{(user.address.address1, user.address.zip) == (write['address1'], write['zip'])}; street named in the scenario: {write['address1'] in text}")

# (e) task 15: size 8 exists only in one material
boots = variants("Hiking Boots")
size8 = {vid: (v.options.get("material"), v.options.get("waterproof"), v.available) for vid, v in boots.items() if v.options.get("size") == "8"}
print(f"(e) task 15 text: {reason('15')[:80]!r}...; size-8 boots: {size8}; "
      f"reference new item: {TASKS['15'].evaluation_criteria.actions[-1].arguments['new_item_ids']}")
