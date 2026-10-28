# Retail task 77

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0 (not scored), nl_count=0 (gates the reward), **noop_pass=0**, noop_needs_judge=0

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

You ordered a perfume and you just tried a little bit and you like it a lot. You want to get the maximum size available for it.

**known_info:**

You name is Ivan Johnson and your zip code is 94183.

**unknown_info:**

You do not remember your email address

**task_instructions:**

If the agent cannot help with placing a new order, ask to exchange your current bottle for the largest size available.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "77_0",
  "name": "exchange_delivered_order_items",
  "arguments": {
   "order_id": "#W1671835",
   "item_ids": [
    "5081446110"
   ],
   "new_item_ids": [
    "3399869890"
   ],
   "payment_method_id": "paypal_6918118"
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
### user `ivan_johnson_6036`
```json
{
 "user_id": "ivan_johnson_6036",
 "name": {
  "first_name": "Ivan",
  "last_name": "Johnson"
 },
 "address": {
  "address1": "581 Hillcrest Drive",
  "address2": "Suite 869",
  "city": "San Francisco",
  "country": "USA",
  "state": "CA",
  "zip": "94183"
 },
 "email": "ivan.johnson5749@example.com",
 "payment_methods": {
  "paypal_6918118": {
   "source": "paypal",
   "id": "paypal_6918118"
  }
 },
 "orders": [
  "#W1671835"
 ]
}
```
### order `#W1671835` (status: delivered)
```json
{
 "order_id": "#W1671835",
 "user_id": "ivan_johnson_6036",
 "address": {
  "address1": "851 Pine Lane",
  "address2": "Suite 428",
  "city": "Fort Worth",
  "country": "USA",
  "state": "TX",
  "zip": "76115"
 },
 "items": [
  {
   "name": "Perfume",
   "product_id": "6858788497",
   "item_id": "5081446110",
   "price": 322.52,
   "options": {
    "scent family": "woody",
    "size": "30ml",
    "gender": "men"
   }
  }
 ],
 "status": "delivered",
 "fulfillments": [
  {
   "tracking_id": [
    "820626058356"
   ],
   "item_ids": [
    "5081446110"
   ]
  }
 ],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 322.52,
   "payment_method_id": "paypal_6918118"
  }
 ]
}
```
### product `6858788497` (Perfume; all variants)
```json
{
 "name": "Perfume",
 "product_id": "6858788497",
 "variants": {
  "9007697085": {
   "options": {
    "scent family": "fresh",
    "size": "50ml",
    "gender": "men"
   },
   "available": true,
   "price": 318.96
  },
  "5081446110": {
   "options": {
    "scent family": "woody",
    "size": "30ml",
    "gender": "men"
   },
   "available": true,
   "price": 322.52
  },
  "1325156478": {
   "options": {
    "scent family": "oriental",
    "size": "30ml",
    "gender": "men"
   },
   "available": true,
   "price": 298.52
  },
  "1002370030": {
   "options": {
    "scent family": "woody",
    "size": "50ml",
    "gender": "women"
   },
   "available": false,
   "price": 290.25
  },
  "3399869890": {
   "options": {
    "scent family": "woody",
    "size": "100ml",
    "gender": "men"
   },
   "available": true,
   "price": 312.04
  },
  "5421902839": {
   "options": {
    "scent family": "oriental",
    "size": "100ml",
    "gender": "men"
   },
   "available": true,
   "price": 328.25
  },
  "1725100896": {
   "options": {
    "scent family": "oriental",
    "size": "30ml",
    "gender": "unisex"
   },
   "available": false,
   "price": 289.66
  },
  "9447903288": {
   "options": {
    "scent family": "fresh",
    "size": "30ml",
    "gender": "men"
   },
   "available": false,
   "price": 296.78
  },
  "8316205423": {
   "options": {
    "scent family": "woody",
    "size": "30ml",
    "gender": "women"
   },
   "available": true,
   "price": 288.75
  },
  "6826843914": {
   "options": {
    "scent family": "fresh",
    "size": "100ml",
    "gender": "men"
   },
   "available": false,
   "price": 326.74
  }
 }
}
```
