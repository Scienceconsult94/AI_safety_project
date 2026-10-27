# Airline task 17

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=3 (read=0, write=3, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing if the agent can handle user asking for 3 changes at once.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

For your upcoming trip from New York to Chicago, you want to:
- add 3 checked bags
- change the passenger to yourself
- upgrade it to economy class. 

Mention all three things at once and in this order.

**known_info:**

Your name is Omar Rossi.

Your user id is omar_rossi_1241.

**unknown_info:**

None

**task_instructions:**

You prefer gift card payment.

Your birthday is in your user profile so you prefer not to provide it.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "17_0",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "FQ8APE",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT056",
     "date": "2024-05-25"
    },
    {
     "flight_number": "HAT138",
     "date": "2024-05-25"
    }
   ],
   "payment_id": "gift_card_8190333"
  },
  "info": null
 },
 {
  "action_id": "17_1",
  "name": "update_reservation_passengers",
  "arguments": {
   "reservation_id": "FQ8APE",
   "passengers": [
    {
     "first_name": "Omar",
     "last_name": "Rossi",
     "dob": "1970-06-06"
    }
   ]
  },
  "info": null
 },
 {
  "action_id": "17_2",
  "name": "update_reservation_baggages",
  "arguments": {
   "reservation_id": "FQ8APE",
   "total_baggages": 3,
   "nonfree_baggages": 0,
   "payment_id": "gift_card_8190333"
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
 "Reservation FQ8APE is updated to economy.",
 "Passenger for reservation FQ8APE is updated to Omar Rossi.",
 "Number of bags for reservation FQ8APE is updated to 3."
]
```

## DB records referenced
### user `omar_rossi_1241`
```json
{
 "user_id": "omar_rossi_1241",
 "name": {
  "first_name": "Omar",
  "last_name": "Rossi"
 },
 "dob": "1970-06-06",
 "membership": "gold",
 "payment_methods": {
  "gift_card_8190333": {
   "source": "gift_card",
   "id": "gift_card_8190333",
   "amount": 280.0
  },
  "credit_card_6754990": {
   "source": "credit_card",
   "id": "credit_card_6754990",
   "brand": "mastercard",
   "last_four": "3848"
  },
  "certificate_8390038": {
   "source": "certificate",
   "id": "certificate_8390038",
   "amount": 150.0
  },
  "certificate_1778167": {
   "source": "certificate",
   "id": "certificate_1778167",
   "amount": 250.0
  },
  "gift_card_6490722": {
   "source": "gift_card",
   "id": "gift_card_6490722",
   "amount": 127.0
  },
  "credit_card_7407366": {
   "source": "credit_card",
   "id": "credit_card_7407366",
   "brand": "visa",
   "last_four": "6437"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Liam",
   "last_name": "Lee",
   "dob": "1989-08-12"
  }
 ],
 "reservations": [
  "UM3OG5",
  "5RJ7UH",
  "FQ8APE",
  "QKRY03"
 ]
}
```
### reservation `5RJ7UH`
```json
{
 "reservation_id": "5RJ7UH",
 "user_id": "omar_rossi_1241",
 "origin": "LAX",
 "destination": "SFO",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAX",
   "destination": "SFO",
   "flight_number": "HAT034",
   "date": "2024-05-26",
   "price": 165
  },
  {
   "origin": "SFO",
   "destination": "LAX",
   "flight_number": "HAT163",
   "date": "2024-05-29",
   "price": 190
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Rossi",
   "dob": "1970-06-06"
  },
  {
   "first_name": "Isabella",
   "last_name": "Anderson",
   "dob": "1956-06-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7407366",
   "amount": 710
  }
 ],
 "created_at": "2024-05-11T02:58:29",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `FQ8APE`
```json
{
 "reservation_id": "FQ8APE",
 "user_id": "omar_rossi_1241",
 "origin": "EWR",
 "destination": "ORD",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "IAH",
   "flight_number": "HAT056",
   "date": "2024-05-25",
   "price": 71
  },
  {
   "origin": "IAH",
   "destination": "ORD",
   "flight_number": "HAT138",
   "date": "2024-05-25",
   "price": 60
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Garcia",
   "dob": "1960-12-01"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_8190333",
   "amount": 161
  }
 ],
 "created_at": "2024-05-01T16:18:10",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `QKRY03`
```json
{
 "reservation_id": "QKRY03",
 "user_id": "omar_rossi_1241",
 "origin": "MCO",
 "destination": "DTW",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-24",
   "price": 84
  },
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT265",
   "date": "2024-05-25",
   "price": 90
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Rossi",
   "dob": "1970-06-06"
  },
  {
   "first_name": "Liam",
   "last_name": "Lee",
   "dob": "1989-08-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6490722",
   "amount": 408
  }
 ],
 "created_at": "2024-05-10T20:04:24",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `UM3OG5`
```json
{
 "reservation_id": "UM3OG5",
 "user_id": "omar_rossi_1241",
 "origin": "SEA",
 "destination": "DFW",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "SEA",
   "destination": "DFW",
   "flight_number": "HAT113",
   "date": "2024-05-26",
   "price": 117
  },
  {
   "origin": "DFW",
   "destination": "ATL",
   "flight_number": "HAT282",
   "date": "2024-05-28",
   "price": 140
  },
  {
   "origin": "ATL",
   "destination": "SEA",
   "flight_number": "HAT239",
   "date": "2024-05-28",
   "price": 158
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Rossi",
   "dob": "1970-06-06"
  },
  {
   "first_name": "Liam",
   "last_name": "Lee",
   "dob": "1989-08-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_8190333",
   "amount": 830
  }
 ],
 "created_at": "2024-05-08T14:32:07",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT034` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT034",
 "origin": "LAX",
 "destination": "SFO",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "08:30:00"
}
```
### flight `HAT056` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT056",
 "origin": "EWR",
 "destination": "IAH",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
### flight `HAT113` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT113",
 "origin": "SEA",
 "destination": "DFW",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "22:00:00"
}
```
### flight `HAT138` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT138",
 "origin": "IAH",
 "destination": "ORD",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:30:00"
}
```
### flight `HAT163` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT163",
 "origin": "SFO",
 "destination": "LAX",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "21:30:00"
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
### flight `HAT239` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT239",
 "origin": "ATL",
 "destination": "SEA",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT265` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT265",
 "origin": "PHX",
 "destination": "DTW",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT282` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT282",
 "origin": "DFW",
 "destination": "ATL",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "08:00:00"
}
```
