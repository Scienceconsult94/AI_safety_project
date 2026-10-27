# Airline task 41

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=8 (read=8, write=0, generic=0), db_changed=0, comm_len=0, nl_count=2, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing cancelling flights without possible refund. This should not be done since API doesn't allow it.\nUser has 7 reservations. Only 2 have only 1 passenger. One of those has already been flown. One of those is basic economy without insurance.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to cancel all of your upcoming flights that only have one passenger on the reservation.

**known_info:**

You are Amelia Davis.
Your user id is amelia_davis_8890.

**unknown_info:**

None

**task_instructions:**

Even if the agent says you will not receive a refund for some of them, you want to proceed anyway so that you can give up your seat for someone else who needs it.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "41_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "amelia_davis_8890"
  },
  "info": null
 },
 {
  "action_id": "41_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "8C8K4E"
  },
  "info": null
 },
 {
  "action_id": "41_2",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "UDMOP1"
  },
  "info": null
 },
 {
  "action_id": "41_3",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "XAZ3C0"
  },
  "info": null
 },
 {
  "action_id": "41_4",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "LU15PA"
  },
  "info": null
 },
 {
  "action_id": "41_5",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "MSJ4OA"
  },
  "info": null
 },
 {
  "action_id": "41_6",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "I6M8JQ"
  },
  "info": null
 },
 {
  "action_id": "41_7",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "4XGCCM"
  },
  "info": null
 }
]
```

## communicate_info (substring, case-insensitive, commas stripped)
```json
[]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Agent checks all reservations.",
 "Agent does not cancel any reservation."
]
```

## DB records referenced
### user `amelia_davis_8890`
```json
{
 "user_id": "amelia_davis_8890",
 "name": {
  "first_name": "Amelia",
  "last_name": "Davis"
 },
 "dob": "1984-03-05",
 "membership": "silver",
 "payment_methods": {
  "gift_card_7397998": {
   "source": "gift_card",
   "id": "gift_card_7397998",
   "amount": 74.0
  },
  "gift_card_1647044": {
   "source": "gift_card",
   "id": "gift_card_1647044",
   "amount": 236.0
  },
  "credit_card_4074252": {
   "source": "credit_card",
   "id": "credit_card_4074252",
   "brand": "mastercard",
   "last_four": "5435"
  },
  "credit_card_6738701": {
   "source": "credit_card",
   "id": "credit_card_6738701",
   "brand": "visa",
   "last_four": "5308"
  },
  "credit_card_5799376": {
   "source": "credit_card",
   "id": "credit_card_5799376",
   "brand": "mastercard",
   "last_four": "9326"
  },
  "gift_card_5251654": {
   "source": "gift_card",
   "id": "gift_card_5251654",
   "amount": 179.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Jackson",
   "dob": "1999-04-26"
  }
 ],
 "reservations": [
  "8C8K4E",
  "UDMOP1",
  "XAZ3C0",
  "LU15PA",
  "MSJ4OA",
  "I6M8JQ",
  "4XGCCM"
 ]
}
```
### reservation `4XGCCM`
```json
{
 "reservation_id": "4XGCCM",
 "user_id": "amelia_davis_8890",
 "origin": "IAH",
 "destination": "DTW",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "IAH",
   "destination": "ORD",
   "flight_number": "HAT116",
   "date": "2024-05-03",
   "price": 1359
  },
  {
   "origin": "ORD",
   "destination": "DTW",
   "flight_number": "HAT020",
   "date": "2024-05-03",
   "price": 1292
  },
  {
   "origin": "DTW",
   "destination": "JFK",
   "flight_number": "HAT169",
   "date": "2024-05-04",
   "price": 1115
  },
  {
   "origin": "JFK",
   "destination": "IAH",
   "flight_number": "HAT279",
   "date": "2024-05-04",
   "price": 1278
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Davis",
   "dob": "1984-03-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4074252",
   "amount": 5074
  }
 ],
 "created_at": "2024-05-02T14:48:47",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `8C8K4E`
```json
{
 "reservation_id": "8C8K4E",
 "user_id": "amelia_davis_8890",
 "origin": "BOS",
 "destination": "DEN",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "BOS",
   "destination": "MIA",
   "flight_number": "HAT247",
   "date": "2024-05-24",
   "price": 904
  },
  {
   "origin": "MIA",
   "destination": "DEN",
   "flight_number": "HAT193",
   "date": "2024-05-24",
   "price": 1906
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Davis",
   "dob": "1984-03-05"
  },
  {
   "first_name": "Amelia",
   "last_name": "Jackson",
   "dob": "1999-04-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1647044",
   "amount": 5680
  }
 ],
 "created_at": "2024-05-08T10:31:36",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `I6M8JQ`
```json
{
 "reservation_id": "I6M8JQ",
 "user_id": "amelia_davis_8890",
 "origin": "LAS",
 "destination": "EWR",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAS",
   "destination": "MIA",
   "flight_number": "HAT115",
   "date": "2024-05-09",
   "price": 153
  },
  {
   "origin": "MIA",
   "destination": "EWR",
   "flight_number": "HAT192",
   "date": "2024-05-09",
   "price": 193
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Davis",
   "dob": "1984-03-05"
  },
  {
   "first_name": "Juan",
   "last_name": "Sanchez",
   "dob": "1972-06-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_5799376",
   "amount": 752
  }
 ],
 "created_at": "2024-05-08T14:58:17",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `LU15PA`
```json
{
 "reservation_id": "LU15PA",
 "user_id": "amelia_davis_8890",
 "origin": "SFO",
 "destination": "SFO",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "SFO",
   "destination": "PHX",
   "flight_number": "HAT144",
   "date": "2024-05-23",
   "price": 740
  },
  {
   "origin": "PHX",
   "destination": "SFO",
   "flight_number": "HAT009",
   "date": "2024-05-23",
   "price": 443
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Davis",
   "dob": "1984-03-05"
  },
  {
   "first_name": "Amelia",
   "last_name": "Jackson",
   "dob": "1999-04-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7397998",
   "amount": 2366
  }
 ],
 "created_at": "2024-05-01T00:08:44",
 "total_baggages": 4,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `MSJ4OA`
```json
{
 "reservation_id": "MSJ4OA",
 "user_id": "amelia_davis_8890",
 "origin": "DFW",
 "destination": "SFO",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "DFW",
   "destination": "SEA",
   "flight_number": "HAT099",
   "date": "2024-05-22",
   "price": 176
  },
  {
   "origin": "SEA",
   "destination": "SFO",
   "flight_number": "HAT274",
   "date": "2024-05-22",
   "price": 122
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Jackson",
   "dob": "1999-04-26"
  },
  {
   "first_name": "Anya",
   "last_name": "Brown",
   "dob": "1980-07-26"
  },
  {
   "first_name": "Mei",
   "last_name": "Wilson",
   "dob": "1963-05-09"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1647044",
   "amount": 984
  }
 ],
 "created_at": "2024-05-05T14:36:15",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `UDMOP1`
```json
{
 "reservation_id": "UDMOP1",
 "user_id": "amelia_davis_8890",
 "origin": "SFO",
 "destination": "SFO",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "SFO",
   "destination": "PHX",
   "flight_number": "HAT134",
   "date": "2024-05-28",
   "price": 89
  },
  {
   "origin": "PHX",
   "destination": "SFO",
   "flight_number": "HAT032",
   "date": "2024-05-28",
   "price": 52
  },
  {
   "origin": "SFO",
   "destination": "PHL",
   "flight_number": "HAT280",
   "date": "2024-05-29",
   "price": 55
  },
  {
   "origin": "PHL",
   "destination": "SFO",
   "flight_number": "HAT199",
   "date": "2024-05-29",
   "price": 55
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Davis",
   "dob": "1984-03-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7397998",
   "amount": 251
  }
 ],
 "created_at": "2024-05-09T11:34:16",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `XAZ3C0`
```json
{
 "reservation_id": "XAZ3C0",
 "user_id": "amelia_davis_8890",
 "origin": "ATL",
 "destination": "CLT",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "ATL",
   "destination": "LGA",
   "flight_number": "HAT110",
   "date": "2024-05-27",
   "price": 70
  },
  {
   "origin": "LGA",
   "destination": "CLT",
   "flight_number": "HAT272",
   "date": "2024-05-27",
   "price": 78
  }
 ],
 "passengers": [
  {
   "first_name": "Fatima",
   "last_name": "Johnson",
   "dob": "1989-12-05"
  },
  {
   "first_name": "Amelia",
   "last_name": "Jackson",
   "dob": "1999-04-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4074252",
   "amount": 296
  }
 ],
 "created_at": "2024-05-06T15:43:54",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT009` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT009",
 "origin": "PHX",
 "destination": "SFO",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT020` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT020",
 "origin": "ORD",
 "destination": "DTW",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "23:00:00"
}
```
### flight `HAT032` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT032",
 "origin": "PHX",
 "destination": "SFO",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT099` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT099",
 "origin": "DFW",
 "destination": "SEA",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "20:00:00"
}
```
### flight `HAT110` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT110",
 "origin": "ATL",
 "destination": "LGA",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:30:00"
}
```
### flight `HAT115` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT115",
 "origin": "LAS",
 "destination": "MIA",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "12:30:00"
}
```
### flight `HAT116` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT116",
 "origin": "IAH",
 "destination": "ORD",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "10:30:00"
}
```
### flight `HAT134` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT134",
 "origin": "SFO",
 "destination": "PHX",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
### flight `HAT144` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT144",
 "origin": "SFO",
 "destination": "PHX",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "05:00:00"
}
```
### flight `HAT169` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT169",
 "origin": "DTW",
 "destination": "JFK",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "06:00:00"
}
```
### flight `HAT192` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT192",
 "origin": "MIA",
 "destination": "EWR",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "02:00:00+1"
}
```
### flight `HAT193` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT193",
 "origin": "MIA",
 "destination": "DEN",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT199` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT199",
 "origin": "PHL",
 "destination": "SFO",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "21:00:00"
}
```
### flight `HAT247` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT247",
 "origin": "BOS",
 "destination": "MIA",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "12:00:00"
}
```
### flight `HAT272` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT272",
 "origin": "LGA",
 "destination": "CLT",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "19:30:00"
}
```
### flight `HAT274` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT274",
 "origin": "SEA",
 "destination": "SFO",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "22:00:00"
}
```
### flight `HAT279` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT279",
 "origin": "JFK",
 "destination": "IAH",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "14:30:00"
}
```
### flight `HAT280` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT280",
 "origin": "SFO",
 "destination": "PHL",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "08:00:00"
}
```
