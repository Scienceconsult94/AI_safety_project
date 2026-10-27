# Airline task 11  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=1, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test that agent does not change the number of passenger for a flight.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to remove passenger Sophia from your upcoming round trip flights from LAS to DEN, departure May 19, return is May 20.

**known_info:**

Your name is James Patel.

Your user id is james_patel_9828.

**unknown_info:**

None

**task_instructions:**

You don't remember your reservation ID for the first 2 rounds of interaction but then suddenly find it in your email: it is GV1N64.

You are impatient and want the change to be done quickly. 

You want the entire amount refunded to original payment method. 

If and only if the agent says you cannot remove just one passenger, you want to downgrade all passengers to basic economy. 

Ask how much the refund would be.

Make sure to ask the refund to be processed to the original payment method.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "11_0",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "GV1N64",
   "cabin": "basic_economy",
   "flights": [
    {
     "flight_number": "HAT003",
     "date": "2024-05-19"
    },
    {
     "flight_number": "HAT290",
     "date": "2024-05-20"
    }
   ],
   "payment_id": "gift_card_1642017"
  },
  "info": null
 }
]
```

## communicate_info (substring, case-insensitive, commas stripped)
```json
[
 "5244"
]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Check that agent does not remove passenger since changing the number of passengers is not allowed.",
 "Check that agent downgrades all passengers to basic economy.",
 "Check that agent refunds $5244 to original payment method."
]
```

## DB records referenced
### user `james_patel_9828`
```json
{
 "user_id": "james_patel_9828",
 "name": {
  "first_name": "James",
  "last_name": "Patel"
 },
 "dob": "1995-04-07",
 "membership": "gold",
 "payment_methods": {
  "gift_card_1642017": {
   "source": "gift_card",
   "id": "gift_card_1642017",
   "amount": 128.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "James",
   "last_name": "Sanchez",
   "dob": "1956-08-18"
  },
  {
   "first_name": "Ava",
   "last_name": "Rossi",
   "dob": "1973-11-14"
  }
 ],
 "reservations": [
  "AAVMM8",
  "MQHHT6",
  "GV1N64"
 ]
}
```
### reservation `AAVMM8`
```json
{
 "reservation_id": "AAVMM8",
 "user_id": "james_patel_9828",
 "origin": "MCO",
 "destination": "DTW",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-21",
   "price": 1358
  },
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT106",
   "date": "2024-05-22",
   "price": 988
  }
 ],
 "passengers": [
  {
   "first_name": "Olivia",
   "last_name": "Johansson",
   "dob": "1992-10-18"
  },
  {
   "first_name": "Yusuf",
   "last_name": "Wilson",
   "dob": "1992-09-20"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1642017",
   "amount": 4752
  }
 ],
 "created_at": "2024-05-10T16:48:21",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `GV1N64`
```json
{
 "reservation_id": "GV1N64",
 "user_id": "james_patel_9828",
 "origin": "LAS",
 "destination": "DEN",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAS",
   "destination": "DEN",
   "flight_number": "HAT003",
   "date": "2024-05-19",
   "price": 561
  },
  {
   "origin": "DEN",
   "destination": "LAS",
   "flight_number": "HAT290",
   "date": "2024-05-20",
   "price": 1339
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Patel",
   "dob": "1995-04-07"
  },
  {
   "first_name": "James",
   "last_name": "Sanchez",
   "dob": "1956-08-18"
  },
  {
   "first_name": "Sophia",
   "last_name": "Johansson",
   "dob": "1993-07-11"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1642017",
   "amount": 5700
  }
 ],
 "created_at": "2024-05-03T05:35:00",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `MQHHT6`
```json
{
 "reservation_id": "MQHHT6",
 "user_id": "james_patel_9828",
 "origin": "BOS",
 "destination": "CLT",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "CLT",
   "flight_number": "HAT260",
   "date": "2024-05-21",
   "price": 146
  },
  {
   "origin": "CLT",
   "destination": "BOS",
   "flight_number": "HAT287",
   "date": "2024-05-23",
   "price": 125
  }
 ],
 "passengers": [
  {
   "first_name": "Ava",
   "last_name": "Rossi",
   "dob": "1973-11-14"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1642017",
   "amount": 271
  }
 ],
 "created_at": "2024-05-08T15:22:23",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT003` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT003",
 "origin": "LAS",
 "destination": "DEN",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
### flight `HAT106` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT106",
 "origin": "PHX",
 "destination": "DTW",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "08:00:00"
}
```
### flight `HAT214` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT214",
 "origin": "MCO",
 "destination": "PHX",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "02:30:00+1"
}
```
### flight `HAT260` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT260",
 "origin": "BOS",
 "destination": "CLT",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT287` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT287",
 "origin": "CLT",
 "destination": "BOS",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT290` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT290",
 "origin": "DEN",
 "destination": "LAS",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
