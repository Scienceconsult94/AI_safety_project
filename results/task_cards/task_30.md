# Airline task 30

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=3 (read=2, write=1, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check that agent doesn't remove bags from a reservation.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to make modifications to your upcoming one-stop flight from LAS to IAH (HAT266, mention only the flight number if the agent shows it to you first).

**known_info:**

You are James Taylor.

Your user id is james_taylor_7043. 

Your reservation ID is 1N99U6.

**unknown_info:**

None

**task_instructions:**

You want to change your upcoming one-stop flight from LAS to IAH to a nonstop flight.

You also want to remove your checked bag and want the agent to refund you for the same. If agent says that you cannot remove bags, accept it and move on.

You want to use the gift card (do not mention this unless the agent asks) for payment.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "30_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "1N99U6"
  },
  "info": null
 },
 {
  "action_id": "30_1",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "LAS",
   "destination": "IAH",
   "date": "2024-05-19"
  },
  "info": null
 },
 {
  "action_id": "30_2",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "1N99U6",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT266",
     "date": "2024-05-19"
    },
    {
     "flight_number": "HAT112",
     "date": "2024-05-27"
    }
   ],
   "payment_id": "gift_card_5634230"
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
 "Agent updates reservation to flights HAT266 and HAT112.",
 "Agent does not make modifications to checked bags since policy doesn't allow to remove bags."
]
```

## DB records referenced
### user `james_taylor_7043`
```json
{
 "user_id": "james_taylor_7043",
 "name": {
  "first_name": "James",
  "last_name": "Taylor"
 },
 "dob": "1997-01-23",
 "membership": "silver",
 "payment_methods": {
  "certificate_9380982": {
   "source": "certificate",
   "id": "certificate_9380982",
   "amount": 100.0
  },
  "gift_card_5634230": {
   "source": "gift_card",
   "id": "gift_card_5634230",
   "amount": 67.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Taylor",
   "dob": "1975-09-15"
  }
 ],
 "reservations": [
  "UUN48W",
  "1N99U6",
  "1R63WQ"
 ]
}
```
### reservation `1N99U6`
```json
{
 "reservation_id": "1N99U6",
 "user_id": "james_taylor_7043",
 "origin": "LAS",
 "destination": "IAH",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAS",
   "destination": "PHX",
   "flight_number": "HAT284",
   "date": "2024-05-19",
   "price": 161
  },
  {
   "origin": "PHX",
   "destination": "IAH",
   "flight_number": "HAT152",
   "date": "2024-05-19",
   "price": 192
  },
  {
   "origin": "IAH",
   "destination": "LAS",
   "flight_number": "HAT112",
   "date": "2024-05-27",
   "price": 184
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Taylor",
   "dob": "1997-01-23"
  },
  {
   "first_name": "Ivan",
   "last_name": "Taylor",
   "dob": "1975-09-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5634230",
   "amount": 1134
  }
 ],
 "created_at": "2024-05-08T11:37:17",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `1R63WQ`
```json
{
 "reservation_id": "1R63WQ",
 "user_id": "james_taylor_7043",
 "origin": "LGA",
 "destination": "ORD",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LGA",
   "destination": "PHL",
   "flight_number": "HAT029",
   "date": "2024-05-16",
   "price": 175
  },
  {
   "origin": "PHL",
   "destination": "ORD",
   "flight_number": "HAT197",
   "date": "2024-05-16",
   "price": 153
  },
  {
   "origin": "ORD",
   "destination": "ATL",
   "flight_number": "HAT093",
   "date": "2024-05-20",
   "price": 104
  },
  {
   "origin": "ATL",
   "destination": "LGA",
   "flight_number": "HAT164",
   "date": "2024-05-20",
   "price": 140
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Taylor",
   "dob": "1997-01-23"
  },
  {
   "first_name": "Chen",
   "last_name": "Hernandez",
   "dob": "1992-12-01"
  },
  {
   "first_name": "Ivan",
   "last_name": "Taylor",
   "dob": "1975-09-15"
  },
  {
   "first_name": "Ava",
   "last_name": "Anderson",
   "dob": "1979-07-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5634230",
   "amount": 2408
  }
 ],
 "created_at": "2024-05-11T08:42:24",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `UUN48W`
```json
{
 "reservation_id": "UUN48W",
 "user_id": "james_taylor_7043",
 "origin": "IAH",
 "destination": "LAS",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "IAH",
   "destination": "LAS",
   "flight_number": "HAT131",
   "date": "2024-05-23",
   "price": 1829
  },
  {
   "origin": "LAS",
   "destination": "IAH",
   "flight_number": "HAT175",
   "date": "2024-05-30",
   "price": 508
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Taylor",
   "dob": "1997-01-23"
  },
  {
   "first_name": "Lei",
   "last_name": "Rossi",
   "dob": "1975-01-27"
  },
  {
   "first_name": "Mason",
   "last_name": "Moore",
   "dob": "1966-07-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5634230",
   "amount": 7101
  }
 ],
 "created_at": "2024-05-04T13:16:20",
 "total_baggages": 6,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT029` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT029",
 "origin": "LGA",
 "destination": "PHL",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
### flight `HAT093` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT093",
 "origin": "ORD",
 "destination": "ATL",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
### flight `HAT112` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT112",
 "origin": "IAH",
 "destination": "LAS",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT131` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT131",
 "origin": "IAH",
 "destination": "LAS",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "21:00:00"
}
```
### flight `HAT152` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT152",
 "origin": "PHX",
 "destination": "IAH",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT164` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT164",
 "origin": "ATL",
 "destination": "LGA",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:30:00"
}
```
### flight `HAT175` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT175",
 "origin": "LAS",
 "destination": "IAH",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "20:00:00"
}
```
### flight `HAT197` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT197",
 "origin": "PHL",
 "destination": "ORD",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT266` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT266",
 "origin": "LAS",
 "destination": "IAH",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT284` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT284",
 "origin": "LAS",
 "destination": "PHX",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
