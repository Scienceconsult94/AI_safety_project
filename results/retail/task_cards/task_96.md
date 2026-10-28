# Retail task 96

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=2 (read=0, write=2, generic=0), db_changed=1, comm_len=0 (not scored), nl_count=0 (gates the reward), **noop_pass=0**, noop_needs_judge=0

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": null,
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to change your LA order to your NYC address (you prefer not to reveal it but it is in your other order). You also want to exchange Bluetooth Speaker to be the cheapest green type.

**known_info:**

You name is Yusuf Li and your zip code is 91148.

**unknown_info:**

You do not remember your email address.

**task_instructions:**

You are cautious, insecure, organized.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "97_0",
  "name": "modify_pending_order_address",
  "arguments": {
   "order_id": "#W6750959",
   "address1": "476 Maple Drive",
   "address2": "Suite 432",
   "city": "New York",
   "country": "USA",
   "state": "NY",
   "zip": "10093"
  },
  "info": null
 },
 {
  "action_id": "97_1",
  "name": "modify_pending_order_items",
  "arguments": {
   "order_id": "#W6750959",
   "item_ids": [
    "3254583681"
   ],
   "new_item_ids": [
    "9440686670"
   ],
   "payment_method_id": "paypal_8080730"
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
null
```

## DB records referenced
### user `yusuf_li_7255`
```json
{
 "user_id": "yusuf_li_7255",
 "name": {
  "first_name": "Yusuf",
  "last_name": "Li"
 },
 "address": {
  "address1": "909 Spruce Street",
  "address2": "Suite 599",
  "city": "Los Angeles",
  "country": "USA",
  "state": "CA",
  "zip": "91148"
 },
 "email": "yusuf.li3523@example.com",
 "payment_methods": {
  "paypal_8080730": {
   "source": "paypal",
   "id": "paypal_8080730"
  }
 },
 "orders": [
  "#W6750959",
  "#W3407479"
 ]
}
```
### order `#W3407479` (status: processed)
```json
{
 "order_id": "#W3407479",
 "user_id": "yusuf_li_7255",
 "address": {
  "address1": "476 Maple Drive",
  "address2": "Suite 432",
  "city": "New York",
  "country": "USA",
  "state": "NY",
  "zip": "10093"
 },
 "items": [
  {
   "name": "E-Reader",
   "product_id": "3801771308",
   "item_id": "5510402676",
   "price": 267.07,
   "options": {
    "screen size": "6-inch",
    "connectivity": "Wi-Fi",
    "storage": "8GB"
   }
  },
  {
   "name": "Jigsaw Puzzle",
   "product_id": "1808611083",
   "item_id": "9370300555",
   "price": 45.9,
   "options": {
    "pieces": "1000",
    "theme": "art",
    "difficulty level": "expert"
   }
  },
  {
   "name": "Skateboard",
   "product_id": "1968349452",
   "item_id": "3232433601",
   "price": 204.14,
   "options": {
    "deck material": "maple",
    "length": "28 inch",
    "design": "plain"
   }
  },
  {
   "name": "Running Shoes",
   "product_id": "6938111410",
   "item_id": "9791469541",
   "price": 147.05,
   "options": {
    "size": "9",
    "color": "yellow",
    "material": "synthetic",
    "sole": "rubber"
   }
  }
 ],
 "status": "processed",
 "fulfillments": [
  {
   "tracking_id": [
    "758121863229"
   ],
   "item_ids": [
    "5510402676",
    "9370300555",
    "3232433601",
    "9791469541"
   ]
  }
 ],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 664.16,
   "payment_method_id": "paypal_8080730"
  }
 ]
}
```
### order `#W6750959` (status: pending)
```json
{
 "order_id": "#W6750959",
 "user_id": "yusuf_li_7255",
 "address": {
  "address1": "909 Spruce Street",
  "address2": "Suite 599",
  "city": "Los Angeles",
  "country": "USA",
  "state": "CA",
  "zip": "91148"
 },
 "items": [
  {
   "name": "Bluetooth Speaker",
   "product_id": "4768869376",
   "item_id": "3254583681",
   "price": 302.67,
   "options": {
    "color": "blue",
    "battery life": "20 hours",
    "water resistance": "yes"
   }
  },
  {
   "name": "E-Reader",
   "product_id": "3801771308",
   "item_id": "4273929280",
   "price": 244.95,
   "options": {
    "screen size": "7-inch",
    "connectivity": "Wi-Fi + Cellular",
    "storage": "32GB"
   }
  }
 ],
 "status": "pending",
 "fulfillments": [],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 547.62,
   "payment_method_id": "paypal_8080730"
  }
 ]
}
```
### product `4768869376` (Bluetooth Speaker; all variants)
```json
{
 "name": "Bluetooth Speaker",
 "product_id": "4768869376",
 "variants": {
  "5967152432": {
   "options": {
    "color": "green",
    "battery life": "10 hours",
    "water resistance": "yes"
   },
   "available": false,
   "price": 292.71
  },
  "9179378709": {
   "options": {
    "color": "green",
    "battery life": "10 hours",
    "water resistance": "no"
   },
   "available": false,
   "price": 326.59
  },
  "9440686670": {
   "options": {
    "color": "green",
    "battery life": "20 hours",
    "water resistance": "no"
   },
   "available": true,
   "price": 298.91
  },
  "4716977452": {
   "options": {
    "color": "blue",
    "battery life": "10 hours",
    "water resistance": "yes"
   },
   "available": true,
   "price": 289.69
  },
  "2652637226": {
   "options": {
    "color": "green",
    "battery life": "20 hours",
    "water resistance": "yes"
   },
   "available": false,
   "price": 295.94
  },
  "5650803029": {
   "options": {
    "color": "black",
    "battery life": "20 hours",
    "water resistance": "no"
   },
   "available": false,
   "price": 324.63
  },
  "5855700373": {
   "options": {
    "color": "black",
    "battery life": "10 hours",
    "water resistance": "yes"
   },
   "available": false,
   "price": 293.46
  },
  "7751905257": {
   "options": {
    "color": "red",
    "battery life": "10 hours",
    "water resistance": "yes"
   },
   "available": true,
   "price": 321.18
  },
  "2635605237": {
   "options": {
    "color": "blue",
    "battery life": "20 hours",
    "water resistance": "no"
   },
   "available": true,
   "price": 271.89
  },
  "6704763132": {
   "options": {
    "color": "blue",
    "battery life": "10 hours",
    "water resistance": "no"
   },
   "available": true,
   "price": 305.45
  },
  "7597543861": {
   "options": {
    "color": "black",
    "battery life": "10 hours",
    "water resistance": "no"
   },
   "available": false,
   "price": 310.47
  },
  "7617930199": {
   "options": {
    "color": "red",
    "battery life": "20 hours",
    "water resistance": "yes"
   },
   "available": true,
   "price": 285.94
  },
  "1052700637": {
   "options": {
    "color": "red",
    "battery life": "20 hours",
    "water resistance": "no"
   },
   "available": true,
   "price": 285.81
  },
  "1689914594": {
   "options": {
    "color": "red",
    "battery life": "10 hours",
    "water resistance": "no"
   },
   "available": true,
   "price": 315.2
  },
  "3254583681": {
   "options": {
    "color": "blue",
    "battery life": "20 hours",
    "water resistance": "yes"
   },
   "available": true,
   "price": 302.67
  },
  "6455132774": {
   "options": {
    "color": "black",
    "battery life": "20 hours",
    "water resistance": "yes"
   },
   "available": false,
   "price": 273.38
  }
 }
}
```
