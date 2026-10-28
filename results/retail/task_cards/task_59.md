# Retail task 59

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=5 (read=3, write=2, generic=0), db_changed=1, comm_len=2 (not scored), nl_count=2 (gates the reward), **noop_pass=0**, noop_needs_judge=0

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

You recently placed two orders, and now you would like to make several changes and checks. You'll first inquire about the status difference between your two orders, #W2702727 and #W8268610, since both are "pending," but one was placed much earlier in the year. You are considering cancelling the older order as you find the wait time unreasonable. If the agent cannot guarantee the older order will be processed within 5 days, you want to cancel it. You also want to confirm the total price of the refund. 

    For order #W2702727, you intend to switch the shipping address to your new home in a different city because you plan to move prior to its delivery next month. Your new address is 1234 Elm St, Springfield, IL, 62701. You want the agent to confirm the change and ensure the order will be delivered to the new address. You also want to confirm the total price of the order after the address change.

**known_info:**

You are Yusuf Taylor from San Jose, CA, 95154.

**unknown_info:**

You do not remember your email address.

**task_instructions:**

Your approach will be firm, as you are unhappy with the pending status's duration but try to make all requests in one go and ask for them to be resolved efficiently and correctly in context with each other.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "59_0",
  "name": "find_user_id_by_name_zip",
  "arguments": {
   "first_name": "Yusuf",
   "last_name": "Taylor",
   "zip": "95154"
  },
  "info": null
 },
 {
  "action_id": "59_1",
  "name": "get_order_details",
  "arguments": {
   "order_id": "#W2702727"
  },
  "info": null
 },
 {
  "action_id": "59_2",
  "name": "get_order_details",
  "arguments": {
   "order_id": "#W8268610"
  },
  "info": null
 },
 {
  "action_id": "59_3",
  "name": "cancel_pending_order",
  "arguments": {
   "order_id": "#W8268610",
   "reason": "no longer needed"
  },
  "info": null
 },
 {
  "action_id": "59_4",
  "name": "modify_pending_order_address",
  "arguments": {
   "order_id": "#W2702727",
   "address1": "1234 Elm St",
   "address2": "",
   "city": "Springfield",
   "state": "IL",
   "country": "USA",
   "zip": "62701"
  },
  "info": null
 }
]
```

## communicate_info (NOT in reward_basis: never scored by tau2 run)
```json
[
 "164.28",
 "625.60"
]
```

## nl_assertions (gate the reward through the LLM judge)
```json
[
 "Agent should tell the user the refund for the cancelled desk lamp order is $164.28.",
 "Agent should tell the user the total price of order #W2702727 is $625.60."
]
```

## DB records referenced
### user `yusuf_taylor_7149`
```json
{
 "user_id": "yusuf_taylor_7149",
 "name": {
  "first_name": "Yusuf",
  "last_name": "Taylor"
 },
 "address": {
  "address1": "163 Cedar Street",
  "address2": "Suite 165",
  "city": "San Jose",
  "country": "USA",
  "state": "CA",
  "zip": "95154"
 },
 "email": "yusuf.taylor6118@example.com",
 "payment_methods": {
  "credit_card_3599838": {
   "source": "credit_card",
   "id": "credit_card_3599838",
   "brand": "visa",
   "last_four": "4012"
  }
 },
 "orders": [
  "#W2702727",
  "#W5690487",
  "#W8268610"
 ]
}
```
### order `#W2702727` (status: pending)
```json
{
 "order_id": "#W2702727",
 "user_id": "yusuf_taylor_7149",
 "address": {
  "address1": "163 Cedar Street",
  "address2": "Suite 165",
  "city": "San Jose",
  "country": "USA",
  "state": "CA",
  "zip": "95154"
 },
 "items": [
  {
   "name": "Bookshelf",
   "product_id": "8600330539",
   "item_id": "7373893106",
   "price": 531.22,
   "options": {
    "material": "glass",
    "color": "white",
    "height": "4 ft"
   }
  },
  {
   "name": "Yoga Mat",
   "product_id": "4635925001",
   "item_id": "2733768059",
   "price": 94.38,
   "options": {
    "thickness": "6mm",
    "material": "natural rubber",
    "color": "pink"
   }
  }
 ],
 "status": "pending",
 "fulfillments": [],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 625.6,
   "payment_method_id": "credit_card_3599838"
  }
 ]
}
```
### order `#W5690487` (status: delivered)
```json
{
 "order_id": "#W5690487",
 "user_id": "yusuf_taylor_7149",
 "address": {
  "address1": "227 Oak Street",
  "address2": "Suite 699",
  "city": "Washington",
  "country": "USA",
  "state": "DC",
  "zip": "20564"
 },
 "items": [
  {
   "name": "Electric Toothbrush",
   "product_id": "7352963235",
   "item_id": "6555827912",
   "price": 199.42,
   "options": {
    "color": "black",
    "speed settings": "low",
    "battery type": "AA batteries"
   }
  },
  {
   "name": "Cycling Helmet",
   "product_id": "7765186836",
   "item_id": "3358616356",
   "price": 197.33,
   "options": {
    "size": "S",
    "color": "red",
    "ventilation": "low"
   }
  }
 ],
 "status": "delivered",
 "fulfillments": [
  {
   "tracking_id": [
    "467544979708"
   ],
   "item_ids": [
    "6555827912",
    "3358616356"
   ]
  }
 ],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 396.75,
   "payment_method_id": "credit_card_3599838"
  }
 ]
}
```
### order `#W8268610` (status: pending)
```json
{
 "order_id": "#W8268610",
 "user_id": "yusuf_taylor_7149",
 "address": {
  "address1": "163 Cedar Street",
  "address2": "Suite 165",
  "city": "San Jose",
  "country": "USA",
  "state": "CA",
  "zip": "95154"
 },
 "items": [
  {
   "name": "Desk Lamp",
   "product_id": "6817146515",
   "item_id": "9083642334",
   "price": 164.28,
   "options": {
    "color": "white",
    "brightness": "high",
    "power source": "USB"
   }
  }
 ],
 "status": "pending",
 "fulfillments": [],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 164.28,
   "payment_method_id": "credit_card_3599838"
  }
 ]
}
```
