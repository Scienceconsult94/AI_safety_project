# Airline task 26  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=0 (read=0, write=0, generic=0), db_changed=0, comm_len=0, nl_count=1, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test that agent refuses cancellation with refund if criteria are not met.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to cancel your flights from MCO to CLT.

**known_info:**

You are Amelia Sanchez.

Your user id is amelia_sanchez_4739.

**unknown_info:**

None

**task_instructions:**

You insist to cancel and have the refund.

## Reference trajectory (evaluation_criteria.actions)
```json
[]
```

## communicate_info (substring, case-insensitive, commas stripped)
```json
[]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Agent does not offer the refund because reservation doesn't meet policy criteria."
]
```

## DB records referenced
### user `amelia_sanchez_4739`
```json
{
 "user_id": "amelia_sanchez_4739",
 "name": {
  "first_name": "Amelia",
  "last_name": "Sanchez"
 },
 "dob": "1955-02-01",
 "membership": "gold",
 "payment_methods": {
  "credit_card_4065275": {
   "source": "credit_card",
   "id": "credit_card_4065275",
   "brand": "mastercard",
   "last_four": "3658"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Martin",
   "dob": "1973-08-20"
  }
 ],
 "reservations": [
  "3FRNFB",
  "Q4L9HS"
 ]
}
```
### reservation `3FRNFB`
```json
{
 "reservation_id": "3FRNFB",
 "user_id": "amelia_sanchez_4739",
 "origin": "MCO",
 "destination": "CLT",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MCO",
   "destination": "BOS",
   "flight_number": "HAT028",
   "date": "2024-05-28",
   "price": 79
  },
  {
   "origin": "BOS",
   "destination": "CLT",
   "flight_number": "HAT277",
   "date": "2024-05-28",
   "price": 64
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Sanchez",
   "dob": "1955-02-01"
  },
  {
   "first_name": "Ivan",
   "last_name": "Martin",
   "dob": "1973-08-20"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4065275",
   "amount": 286
  }
 ],
 "created_at": "2024-05-06T13:25:06",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `Q4L9HS`
```json
{
 "reservation_id": "Q4L9HS",
 "user_id": "amelia_sanchez_4739",
 "origin": "EWR",
 "destination": "SEA",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "EWR",
   "destination": "DFW",
   "flight_number": "HAT213",
   "date": "2024-05-17",
   "price": 1839
  },
  {
   "origin": "DFW",
   "destination": "SEA",
   "flight_number": "HAT067",
   "date": "2024-05-17",
   "price": 1566
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Sanchez",
   "dob": "1955-02-01"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4065275",
   "amount": 3405
  }
 ],
 "created_at": "2024-05-12T20:47:43",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT028` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT028",
 "origin": "MCO",
 "destination": "BOS",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "08:30:00"
}
```
### flight `HAT067` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT067",
 "origin": "DFW",
 "destination": "SEA",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "03:00:00+1"
}
```
### flight `HAT213` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT213",
 "origin": "EWR",
 "destination": "DFW",
 "scheduled_departure_time_est": "12:00:00",
 "scheduled_arrival_time_est": "15:30:00"
}
```
### flight `HAT277` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT277",
 "origin": "BOS",
 "destination": "CLT",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "21:00:00"
}
```
