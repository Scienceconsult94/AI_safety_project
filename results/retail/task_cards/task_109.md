# Retail task 109

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=3 (read=0, write=3, generic=0), db_changed=1, comm_len=0 (not scored), nl_count=2 (gates the reward), **noop_pass=0**, noop_needs_judge=0

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Address change + exchange",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You live on Elm Avenue in Houston, and recently you moved to a new house on the same street and bought a luggage set sent to this new address. But you realize you have another order sent to the old address, and you want to change your wrong order address to the new home, and also your user default address to the new home. You do not want to reveal your address but the agent should be able to look it up in orders You do not want to reveal your address and insist the agent should be able to look it up in orders. You also want to exchange your tablet to the cheapest one due to moving costs.

**known_info:**

You name is Sophia Martin and your email is sophia.martin4832@example.com.

**unknown_info:**

None

**task_instructions:**

You are organized and outgoing.  Make sure to mention the two address changes then the exchange.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "110_0",
  "name": "modify_pending_order_address",
  "arguments": {
   "order_id": "#W1603792",
   "address1": "592 Elm Avenue",
   "address2": "Suite 978",
   "city": "Houston",
   "country": "USA",
   "state": "TX",
   "zip": "77242"
  },
  "info": null
 },
 {
  "action_id": "110_1",
  "name": "modify_user_address",
  "arguments": {
   "user_id": "sophia_martin_8570",
   "address1": "592 Elm Avenue",
   "address2": "Suite 978",
   "city": "Houston",
   "country": "USA",
   "state": "TX",
   "zip": "77242"
  },
  "info": null
 },
 {
  "action_id": "110_2",
  "name": "modify_pending_order_items",
  "arguments": {
   "order_id": "#W1603792",
   "item_ids": [
    "6501071631"
   ],
   "new_item_ids": [
    "2106335193"
   ],
   "payment_method_id": "credit_card_5694100"
  },
  "info": null
 }
]
```

## communicate_info (NOT in reward_basis: never scored by tau2 run)
```json
[]
```

## nl_assertions (gate the reward through the LLM judge)
```json
[
 "Agent should make changes to address on order and user profile",
 "Agent should modify the pending order."
]
```

## DB records referenced
### user `sophia_martin_8570`
```json
{
 "user_id": "sophia_martin_8570",
 "name": {
  "first_name": "Sophia",
  "last_name": "Martin"
 },
 "address": {
  "address1": "760 Elm Avenue",
  "address2": "Suite 564",
  "city": "Houston",
  "country": "USA",
  "state": "TX",
  "zip": "77034"
 },
 "email": "sophia.martin4832@example.com",
 "payment_methods": {
  "credit_card_5694100": {
   "source": "credit_card",
   "id": "credit_card_5694100",
   "brand": "mastercard",
   "last_four": "3292"
  }
 },
 "orders": [
  "#W1603792",
  "#W1092119"
 ]
}
```
### order `#W1092119` (status: pending)
```json
{
 "order_id": "#W1092119",
 "user_id": "sophia_martin_8570",
 "address": {
  "address1": "592 Elm Avenue",
  "address2": "Suite 978",
  "city": "Houston",
  "country": "USA",
  "state": "TX",
  "zip": "77242"
 },
 "items": [
  {
   "name": "Luggage Set",
   "product_id": "5426915165",
   "item_id": "6690069155",
   "price": 466.47,
   "options": {
    "piece count": "3-piece",
    "color": "silver",
    "material": "softshell"
   }
  }
 ],
 "status": "pending",
 "fulfillments": [],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 466.47,
   "payment_method_id": "credit_card_5694100"
  }
 ]
}
```
### order `#W1603792` (status: pending)
```json
{
 "order_id": "#W1603792",
 "user_id": "sophia_martin_8570",
 "address": {
  "address1": "760 Elm Avenue",
  "address2": "Suite 564",
  "city": "Houston",
  "country": "USA",
  "state": "TX",
  "zip": "77034"
 },
 "items": [
  {
   "name": "Bicycle",
   "product_id": "9783735446",
   "item_id": "5606522780",
   "price": 1902.67,
   "options": {
    "frame size": "large",
    "color": "red",
    "type": "mountain"
   }
  },
  {
   "name": "Grill",
   "product_id": "6819683148",
   "item_id": "1120917161",
   "price": 953.39,
   "options": {
    "type": "electric",
    "size": "portable",
    "features": "none"
   }
  },
  {
   "name": "Headphones",
   "product_id": "6992792935",
   "item_id": "5635439102",
   "price": 353.76,
   "options": {
    "type": "over-ear",
    "connectivity": "wired",
    "color": "blue"
   }
  },
  {
   "name": "Pet Bed",
   "product_id": "2747247837",
   "item_id": "4537595158",
   "price": 193.79,
   "options": {
    "size": "small",
    "material": "fleece",
    "color": "brown"
   }
  },
  {
   "name": "Tablet",
   "product_id": "8024098596",
   "item_id": "6501071631",
   "price": 1018.68,
   "options": {
    "screen size": "7-inch",
    "storage": "32GB",
    "color": "gold"
   }
  }
 ],
 "status": "pending",
 "fulfillments": [],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 4422.29,
   "payment_method_id": "credit_card_5694100"
  }
 ]
}
```
### product `8024098596` (Tablet; all variants)
```json
{
 "name": "Tablet",
 "product_id": "8024098596",
 "variants": {
  "3788616824": {
   "options": {
    "screen size": "10-inch",
    "storage": "128GB",
    "color": "black"
   },
   "available": false,
   "price": 951.21
  },
  "2235648106": {
   "options": {
    "screen size": "10-inch",
    "storage": "32GB",
    "color": "black"
   },
   "available": true,
   "price": 1054.43
  },
  "7535423717": {
   "options": {
    "screen size": "8-inch",
    "storage": "128GB",
    "color": "silver"
   },
   "available": false,
   "price": 904.46
  },
  "2106335193": {
   "options": {
    "screen size": "10-inch",
    "storage": "64GB",
    "color": "silver"
   },
   "available": true,
   "price": 903.95
  },
  "6501071631": {
   "options": {
    "screen size": "7-inch",
    "storage": "32GB",
    "color": "gold"
   },
   "available": true,
   "price": 1018.68
  },
  "2633090267": {
   "options": {
    "screen size": "7-inch",
    "storage": "64GB",
    "color": "silver"
   },
   "available": false,
   "price": 1046.33
  },
  "4803681337": {
   "options": {
    "screen size": "8-inch",
    "storage": "64GB",
    "color": "black"
   },
   "available": false,
   "price": 962.34
  },
  "6065192424": {
   "options": {
    "screen size": "8-inch",
    "storage": "128GB",
    "color": "gold"
   },
   "available": true,
   "price": 989.7
  },
  "7187199153": {
   "options": {
    "screen size": "8-inch",
    "storage": "128GB",
    "color": "black"
   },
   "available": false,
   "price": 983.62
  },
  "4913411651": {
   "options": {
    "screen size": "7-inch",
    "storage": "128GB",
    "color": "black"
   },
   "available": true,
   "price": 941.03
  },
  "8551474201": {
   "options": {
    "screen size": "8-inch",
    "storage": "64GB",
    "color": "silver"
   },
   "available": false,
   "price": 938.92
  },
  "4615543240": {
   "options": {
    "screen size": "7-inch",
    "storage": "32GB",
    "color": "silver"
   },
   "available": true,
   "price": 1042.93
  },
  "6948061616": {
   "options": {
    "screen size": "10-inch",
    "storage": "128GB",
    "color": "gold"
   },
   "available": true,
   "price": 950.96
  },
  "4131464125": {
   "options": {
    "screen size": "10-inch",
    "storage": "128GB",
    "color": "silver"
   },
   "available": false,
   "price": 960.67
  }
 }
}
```
