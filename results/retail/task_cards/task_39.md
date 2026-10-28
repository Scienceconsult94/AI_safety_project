# Retail task 39

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=5 (read=4, write=1, generic=0), db_changed=1, comm_len=1 (not scored), nl_count=1 (gates the reward), **noop_pass=0**, noop_needs_judge=0

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

You just moved from Florida to Phoenix. Unfortunately your address is still the old one, and you want to update it. Your current address should be in your recent order (you can mention this to the agent), and you do not want to reveal it. Also, you want to know what is the price of the cheapest available t-shirt right now, and if you can order it through the agent.

**known_info:**

You are fatima_taylor_3452, and you just moved from Florida (32169) to Phoenix (85033).

**unknown_info:**

You do not remember your email address

**task_instructions:**

You are a funny person with lots of jokes, and you want to make the agent laugh.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "39_0",
  "name": "find_user_id_by_name_zip",
  "arguments": {
   "first_name": "Fatima",
   "last_name": "Taylor",
   "zip": "85033"
  },
  "info": null
 },
 {
  "action_id": "39_1",
  "name": "find_user_id_by_name_zip",
  "arguments": {
   "first_name": "Fatima",
   "last_name": "Taylor",
   "zip": "32169"
  },
  "info": null
 },
 {
  "action_id": "39_2",
  "name": "get_user_details",
  "arguments": {
   "user_id": "fatima_taylor_3452"
  },
  "info": null
 },
 {
  "action_id": "39_3",
  "name": "get_order_details",
  "arguments": {
   "order_id": "#W5285031"
  },
  "info": null
 },
 {
  "action_id": "39_4",
  "name": "modify_user_address",
  "arguments": {
   "user_id": "fatima_taylor_3452",
   "address1": "157 Oak Street",
   "address2": "Suite 258",
   "city": "Phoenix",
   "state": "AZ",
   "country": "USA",
   "zip": "85033"
  },
  "info": null
 }
]
```

## communicate_info (NOT in reward_basis: never scored by tau2 run)
```json
[
 "46.66"
]
```

## nl_assertions (gate the reward through the LLM judge)
```json
[
 "Agent should tell the user the cheapest t-shirt costs $46.66."
]
```

## DB records referenced
### user `fatima_taylor_3452`
```json
{
 "user_id": "fatima_taylor_3452",
 "name": {
  "first_name": "Fatima",
  "last_name": "Taylor"
 },
 "address": {
  "address1": "922 Pine Lane",
  "address2": "Suite 395",
  "city": "Jacksonville",
  "country": "USA",
  "state": "FL",
  "zip": "32169"
 },
 "email": "fatima.taylor7676@example.com",
 "payment_methods": {
  "credit_card_7952624": {
   "source": "credit_card",
   "id": "credit_card_7952624",
   "brand": "visa",
   "last_four": "7684"
  }
 },
 "orders": [
  "#W5285031"
 ]
}
```
### order `#W5285031` (status: delivered)
```json
{
 "order_id": "#W5285031",
 "user_id": "fatima_taylor_3452",
 "address": {
  "address1": "157 Oak Street",
  "address2": "Suite 258",
  "city": "Phoenix",
  "country": "USA",
  "state": "AZ",
  "zip": "85033"
 },
 "items": [
  {
   "name": "Wireless Earbuds",
   "product_id": "9924732112",
   "item_id": "4063058357",
   "price": 243.34,
   "options": {
    "color": "black",
    "battery life": "4 hours",
    "water resistance": "not resistant"
   }
  },
  {
   "name": "Tablet",
   "product_id": "8024098596",
   "item_id": "2235648106",
   "price": 1054.43,
   "options": {
    "screen size": "10-inch",
    "storage": "32GB",
    "color": "black"
   }
  },
  {
   "name": "Gaming Mouse",
   "product_id": "5713490933",
   "item_id": "8214883393",
   "price": 150.58,
   "options": {
    "color": "black",
    "sensor type": "laser",
    "connectivity": "wireless"
   }
  }
 ],
 "status": "delivered",
 "fulfillments": [
  {
   "tracking_id": [
    "517174610452"
   ],
   "item_ids": [
    "4063058357",
    "2235648106",
    "8214883393"
   ]
  }
 ],
 "payment_history": [
  {
   "transaction_type": "payment",
   "amount": 1448.35,
   "payment_method_id": "credit_card_7952624"
  }
 ]
}
```
