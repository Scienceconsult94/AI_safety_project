# retail task data: reference defects (tasks 2-4, 18, 26, 64, 105, 110; action ids from 95 on) and task texts a faithful user cannot follow to the reference (tasks 0, 1, 15, 34, 52, 100)

| field | value |
|---|---|
| audit ids | I13, I16 |
| type | task data |
| domain | retail |
| severity | 105 high; 52 high (run evidence) and medium (static); 0, 1, 15, 18, 34, 100, 110 medium; 2-4, 26, 64 low; action ids cosmetic |
| status | draft, not filed |

## Summary

Reading all 114 retail tasks against `db.json`, and reading the failed runs, found two groups of task-data defects. (I13) Reference trajectories with errors: a product id that exists nowhere (tasks 2-4), an only reference action that raises (task 105, so the target is the unchanged database while the assertion demands the exchange), a transfer summary copied from another task (26), a no-op user-address write (110), a fallback branch whose premise is false in the data (18), an exchange on a pending order (64), and action ids carrying another task's number (95-113). (I16) Task texts that a scenario-faithful user cannot follow to the reference: a compatibility name absent from the catalogue (0, 1), an option set that two products match (100), a request that no product satisfies (52), an address the user is never given (34), and an ambiguous phrase (15).

## Affected version

Tag `v2.0.0`, commit `989d3285ae669e49503324bdb9981bf14fccedeb`; `data/tau2/domains/retail/tasks.json` and `db.json`. The reference replay swallows exceptions (`src/tau2/evaluator/evaluator_env.py` lines 104-115), so a raising reference action silently changes the target.

## Reproduction

Static checks and reference replays, no model call. Run from the repository root with `uv run --no-sync python <file>`.

### I13: reference defects (`repro_I13.py`)

```python
"""I13: retail reference-trajectory defects (tasks 2-4, 105, 26, 110, 18, 64, action ids from 95 on).

No model call. Run from the tau2-bench root:
    PYTHONUTF8=1 uv run --no-sync python <path>/I13.py
"""

import os

os.environ.setdefault("LOGURU_LEVEL", "ERROR")

from loguru import logger  # noqa: E402

logger.remove()

from tau2.registry import registry  # noqa: E402

ENV = registry.get_env_constructor("retail")
TASKS = {t.id: t for t in registry.get_tasks_loader("retail")("base")}


def replay(task):
    """Replay the reference like EnvironmentEvaluator does; return the env and the raising actions."""
    env = ENV()
    errors = []
    for a in task.evaluation_criteria.actions:
        try:
            env.make_tool_call(tool_name=a.name, requestor=a.requestor, **a.arguments)
        except Exception as e:  # noqa: BLE001
            errors.append((a.action_id, a.name, str(e)))
    return env, errors


db = ENV().tools.db
initial_hash = ENV().get_db_hash()

# (a) a product id that exists nowhere
for tid in ("2", "3", "4"):
    acts = TASKS[tid].evaluation_criteria.actions
    bad = [a.action_id for a in acts if a.name == "get_product_details" and a.arguments["product_id"] not in db.products]
    print(f"(a) task {tid}: get_product_details on an unknown product id in {bad}; replay errors {replay(TASKS[tid])[1]}")
print(f"    task 2 action ids: {[a.action_id for a in TASKS['2'].evaluation_criteria.actions][:4]}")

# (b) task 105: the only reference action raises, so the target is the unchanged DB
task = TASKS["105"]
a = task.evaluation_criteria.actions[0]
order = db.orders[a.arguments["order_id"]]
old = {it.item_id: it.price for it in order.items}
diff = round(sum(db.products[next(it.product_id for it in order.items if it.item_id == o)].variants[n].price - old[o]
                 for o, n in zip(a.arguments["item_ids"], a.arguments["new_item_ids"])), 2)
card = db.users[order.user_id].payment_methods[a.arguments["payment_method_id"]]
env, errors = replay(task)
print(f"(b) task 105: {a.action_id} {a.name} pays a difference of {diff} with {card.id} (balance {card.balance}); "
      f"replay errors {errors}; target hash == initial hash: {env.get_db_hash() == initial_hash}")
print(f"    nl_assertions: {task.evaluation_criteria.nl_assertions}")

# (c) task 26: the transfer summary describes task 25's scenario
summary = TASKS["26"].evaluation_criteria.actions[-1].arguments["summary"]
print(f"(c) task 26 transfer summary: {summary!r}; 'amex' in task 26 scenario: "
      f"{'amex' in TASKS['26'].user_scenario.instructions.reason_for_call}; in task 25 scenario: "
      f"{'amex' in TASKS['25'].user_scenario.instructions.reason_for_call}")

# (d) task 110: the user-address write is a no-op
task = TASKS["110"]
a = next(x for x in task.evaluation_criteria.actions if x.name == "modify_user_address")
current = db.users[a.arguments["user_id"]].address.model_dump()
written = {k: v for k, v in a.arguments.items() if k != "user_id"}
print(f"(d) task 110: {a.action_id} writes the address the user already has: {current == written}; "
      f"assertion: {task.evaluation_criteria.nl_assertions[1]!r}")

# (e) task 18: the fallback presupposes that the ordered chair is unavailable
task = TASKS["18"]
a = task.evaluation_criteria.actions[-1]
order = db.orders[a.arguments["order_id"]]
chair = next(it for it in order.items if it.item_id == a.arguments["item_ids"][0])
print(f"(e) task 18: ordered chair {chair.item_id} available in db.json: "
      f"{db.products[chair.product_id].variants[chair.item_id].available}; reference exchanges it for {a.arguments['new_item_ids']}")

# (f) task 64: a reference exchange on a pending order
print(f"(f) task 64: replay errors {replay(TASKS['64'])[1]}")

# (g) action ids that carry another task's number
mismatch = [t.id for t in TASKS.values() if any(not x.action_id.startswith(f"{t.id}_") for x in t.evaluation_criteria.actions or [])]
print(f"(g) tasks whose action ids do not start with their own id: {mismatch}")
print(f"    task 104 action ids: {[x.action_id for x in TASKS['104'].evaluation_criteria.actions]}")
```

Output:

```text
(a) task 2: get_product_details on an unknown product id in ['2_1']; replay errors [('2_1', 'get_product_details', 'Product not found')]
(a) task 3: get_product_details on an unknown product id in ['3_1']; replay errors [('3_1', 'get_product_details', 'Product not found')]
(a) task 4: get_product_details on an unknown product id in ['4_1']; replay errors [('4_1', 'get_product_details', 'Product not found')]
    task 2 action ids: ['2_0', '2_1', '2_3', '2_4']
(b) task 105: 106_0 exchange_delivered_order_items pays a difference of 21.1 with gift_card_7245904 (balance 17.0); replay errors [('106_0', 'exchange_delivered_order_items', 'Insufficient gift card balance to pay for the price difference')]; target hash == initial hash: True
    nl_assertions: ['Agent should exchange both tea kettles (same style) to the items requested']
(c) task 26 transfer summary: 'The user wants to refund to the amex credit card, but the agent cannot help.'; 'amex' in task 26 scenario: False; in task 25 scenario: True
(d) task 110: 111_1 writes the address the user already has: True; assertion: 'Agent should modify user address'
(e) task 18: ordered chair 8069050545 available in db.json: True; reference exchanges it for ['1071497737']
(f) task 64: replay errors [('64_6', 'exchange_delivered_order_items', 'Non-delivered order cannot be exchanged')]
(g) tasks whose action ids do not start with their own id: ['95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113']
    task 104 action ids: ['105_0', '105_1', '105_2', '105_3', 'action_1746656550382']
```

### I16: task texts vs `db.json` (`repro_I16.py`)

```python
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
```

Output:

```text
(a) 'Google Home' in task 0 / task 1 text: True / True; occurrences of 'Google Home' in db.json: 0
    Smart Thermostat variants: {'8722653925': ('Google Assistant', False), '8593894906': ('Amazon Alexa', False), '2791467853': ('Google Assistant', False), '7747408585': ('Google Assistant', True), '4953074738': ('Amazon Alexa', True), '4983901480': ('Apple HomeKit', True), '9480266227': ('Apple HomeKit', True), '6243148452': ('Amazon Alexa', True), '3377900078': ('Apple HomeKit', True)}
    reference new item for the thermostat: 7747408585
(b) task 100 asks for {'length': '34 inch', 'design': 'custom'}; available matches: {'9594745976': ('plastic', 184.13), '6956751343': ('bamboo', 217.06)}; reference picks 6956751343
(c) task 52: ordered {'resolution': '24MP', 'zoom': '3x', 'storage': 'SD card'} -> reference {'resolution': '30MP', 'zoom': '10x', 'storage': 'SD card'}; available variants with the same resolution and storage: {'5996159312': {'resolution': '24MP', 'zoom': '3x', 'storage': 'SD card'}}
(d) task 34: reference address 224 Elm Street, Suite 491, 10108 == profile address: True; street named in the scenario: False
(e) task 15 text: 'You want to modify the pending boots to a size 8, and want the material, but do '...; size-8 boots: {'2648909398': ('leather', 'yes', False), '3613716226': ('synthetic', 'no', True)}; reference new item: ['3613716226']
```

## Observed vs expected, per task

I13, reference defects:

- (a) Tasks 2, 3, 4: action `*_1` calls `get_product_details("6086499569")`, an id that is not in `db.json` (task 2's ids go `2_0`, `2_1`, `2_3`: an editing slip). The replay skips the raising READ, so the reward is unaffected. Expected: a valid id (the T-shirt product, `9523456873`, is looked up later in the same references) or no action. Severity low.
- (b) Task 105: the only reference action exchanges two kettles and pays the 21.10 difference with `gift_card_7245904`, which holds 17.00; the tool raises "Insufficient gift card balance", so the scored target equals the initial database, while the assertion requires that both kettles be exchanged. No trajectory satisfies both. Expected: a payment method that covers the difference, or a scenario in which the exchange is refused and an assertion that says so. Severity high.
- (c) Task 26: the reference ends with `transfer_to_human_agents` whose summary ("The user wants to refund to the amex credit card, but the agent cannot help.") describes task 25's scenario; task 26's scenario never mentions an amex card. The transfer does not change the database, so the reward is unaffected. Severity low.
- (d) Task 110: action `111_1` writes the address the user already has, while the assertion says "Agent should modify user address". An agent that correctly says no change is needed matches the hash but can fail the assertion; in the runs, one simulation's reward flipped from fail to pass under a 3-vote re-judge on exactly this assertion. Severity medium.
- (e) Task 18: the scenario's fallback ("If the agent mentions that the same product is not available, ask for a gray office chair ...") presupposes that the ordered chair is unavailable, but `db.json` lists `8069050545` as available; the reference (exchange to `1071497737`) is reached only through that fallback. An agent must still refuse an exchange to the identical item, but for another reason (policy line 132: the new item must differ in an option), so a faithful conversation need not reach the scenario's trigger. Severity medium.
- (f) Task 64: action `64_6` is an exchange on a pending order, which the tool rejects; `64_7` then modifies the same item. No effect on the target; the raise is not set up by the scenario. Severity low.
- (g) Tasks 95 to 113: every action id carries the next task's number (task 95 has `96_0`, ...), and task 104 also has `action_1746656550382`. Cosmetic, but it misleads anyone who matches actions to tasks by id.

I16, task texts (the run observations come from the audit's runs with `claude-haiku-5-5` as agent and user simulator, 3 trials per task plus one ground-truth-agent run; these run rows were not adversarially reviewed):

- (a) Tasks 0 and 1 make the exchange conditional on a thermostat "compatible with Google Home". `db.json` contains no "Google Home"; the catalogue's Smart Thermostat variants say "Google Assistant", and the reference picks `7747408585` (Google Assistant). An agent that does not assert the equivalence cannot confirm it, and the user keeps the old item. In task 1, the ground-truth run and two of three trials end without a write. Expected: the scenario names the catalogue value, or says that Google Assistant is acceptable.
- (b) Task 100 asks for a skateboard with `{'length': '34 inch', 'design': 'custom'}`, which two available variants match (plastic `9594745976` at 184.13, bamboo `6956751343` at 217.06); the reference fixes bamboo. In 4 of 4 runs the simulator picked the cheaper deck and the run scored 0. Expected: the scenario states the deck material (or keeps the current one), or both end states are accepted.
- (c) Task 52 asks for maximum zoom with "all the other specifications of the camera ... the same". The only available camera with the ordered resolution and storage is the ordered one (24MP, 3x, SD); the reference `9228757377` changes the resolution to 30MP. The simulator refused it in 4 of 4 runs. Expected: a scenario that allows the resolution change, or a reference that satisfies it. Severity high on the run evidence; the static row (medium) passed an adversarial review.
- (d) Task 34: the reference writes the profile address (224 Elm Street, Suite 491, New York, 10108), but the scenario gives the user only "your NYC place" and the zip code; in the ground-truth run and one trial the user rejected the street the agent read back. Expected: the scenario states the street.
- (e) Task 15: "want the material" was read as a material change in 2 of 4 runs; under that reading the target is unreachable, because the only size-8 boot available is synthetic (`3613716226`) and the leather size 8 (`2648909398`) is unavailable. Expected: unambiguous wording ("keep the material").

## Impact on scores

- Task 105 is unpassable as written (target = unchanged database, assertion = exchange done). In the runs, all 4 conversations (3 trials and the ground-truth run) matched the unchanged target and failed the assertion.
- Tasks 52 and 105 are the two tasks where no compliant conversation reaches the reference (high). Together with tasks 1, 16, 38, 64, 98 and 100, they are the 8 of 23 ground-truth-agent failures that the audit traces to the task or its scoring (run rows, not adversarially reviewed).
- Tasks 0, 1, 15, 34 and 100 fail or flip depending on how the simulator resolves the gap, so they add run-to-run variance that is not about the agent.

## Suggested fix

Edit `tasks.json`: correct the product id in 2-4; make 105 consistent (payment method or assertion); remove or correct the transfer in 26; drop `111_1` or change the assertion in 110; state the availability premise correctly in 18; remove `64_6`; renumber the action ids of 95-113; and add the missing facts to the scenarios of 0, 1, 15, 34, 52 and 100 (or accept the alternative end states). A check in CI that replays every reference and flags raising WRITE actions and no-op WRITE actions would catch (b), (d) and (f).

## Evidence (audit repository)

- `results/retail/static_scan.csv` (columns `replay_errors`, `replay_error_msgs`, `write_noop_ids`), `retail/audit_log.csv` (rows 1b, 1e, 4a, 4b, 4d, 4e, 4f for the tasks above).
- Static reviews: `results/retail/review_batch_1.md` (2-4), `review_batch_2.md` (18), `review_batch_3.md` (26), `review_batch_7.md` (64), `review_batch_11.md` (105), `review_batch_12.md` (110); adversarial review `results/retail/skeptic_report.md` and `results/retail/review_overrides.csv` (18, 26, 64).
- Run reviews: `results/retail/review_agent_A.md` (0, 1, 15), `review_agent_B.md` (34), `review_agent_C.md` (52), `review_agent_E.md` (100); `results/retail/rejudge_summary.md` (110).
- `upstream/repro/I13.py`, `upstream/repro/I16.py`.
