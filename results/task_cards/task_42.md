# Airline task 42

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=10 (read=8, write=2, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check agent's capacity to look up reservation info, find duplicates, reason about locations, passengers, times and cancel the correct flights. User will be in arriving in New York from Dallas on May 17 and will be leaving Boston on May 22. Agent should reason about the locations, passengers, times and cancel the correct flights. The flight from LAX on May 17 is not relevant because the user is not a passenger. The flight from JFK on May 17 leaves before the flight from EWR arrives so should be cancelled. User will be leaving Boston on May 22 so cannot fly out of ORD. The flight from ORD should be cancelled.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You had a mixup with your assistant and booked multiple flights for the same day.

**known_info:**

You are Sophia Martin.
Your user id is sophia_martin_4574.

**unknown_info:**

None

**task_instructions:**

You want to first check if there are cases like this in your profile. You want the agent to fix the situation for you. You just know that you will be in arriving in New York from Dallas on May 17 and will be leaving Boston on May 22. You want to let the agent figure out which flights should be cancelled. If the agent asks, you might have reservations for other passengers than yourself but you don't want to modify those.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "42_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "sophia_martin_4574"
  },
  "info": null
 },
 {
  "action_id": "42_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "MFRB94"
  },
  "info": null
 },
 {
  "action_id": "42_2",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "PUNERT"
  },
  "info": null
 },
 {
  "action_id": "42_3",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "HSR97W"
  },
  "info": null
 },
 {
  "action_id": "42_4",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "SE9KEL"
  },
  "info": null
 },
 {
  "action_id": "42_5",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "FDZ0T5"
  },
  "info": null
 },
 {
  "action_id": "42_6",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "HTR26G"
  },
  "info": null
 },
 {
  "action_id": "42_7",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "5BGGWZ"
  },
  "info": null
 },
 {
  "action_id": "42_8",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "FDZ0T5"
  },
  "info": null
 },
 {
  "action_id": "42_9",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "HSR97W"
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
 "Agent cancels reservation FDZ0T5",
 "Agent cancels reservation HSR97W"
]
```

## DB records referenced
### user `sophia_martin_4574`
```json
{
 "user_id": "sophia_martin_4574",
 "name": {
  "first_name": "Sophia",
  "last_name": "Martin"
 },
 "dob": "1990-10-25",
 "membership": "gold",
 "payment_methods": {
  "certificate_4156052": {
   "source": "certificate",
   "id": "certificate_4156052",
   "amount": 500.0
  },
  "gift_card_6829926": {
   "source": "gift_card",
   "id": "gift_card_6829926",
   "amount": 35.0
  },
  "certificate_4328067": {
   "source": "certificate",
   "id": "certificate_4328067",
   "amount": 100.0
  },
  "credit_card_1402274": {
   "source": "credit_card",
   "id": "credit_card_1402274",
   "brand": "visa",
   "last_four": "8834"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Brown",
   "dob": "1979-12-22"
  },
  {
   "first_name": "Emma",
   "last_name": "Li",
   "dob": "1972-12-12"
  }
 ],
 "reservations": [
  "MFRB94",
  "PUNERT",
  "HSR97W",
  "SE9KEL",
  "FDZ0T5",
  "HTR26G",
  "5BGGWZ"
 ]
}
```
### reservation `5BGGWZ`
```json
{
 "reservation_id": "5BGGWZ",
 "user_id": "sophia_martin_4574",
 "origin": "EWR",
 "destination": "DFW",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "DFW",
   "flight_number": "HAT231",
   "date": "2024-05-10",
   "price": 123
  },
  {
   "origin": "DFW",
   "destination": "EWR",
   "flight_number": "HAT142",
   "date": "2024-05-17",
   "price": 192
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6829926",
   "amount": 345
  }
 ],
 "created_at": "2024-05-03T06:57:21",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `FDZ0T5`
```json
{
 "reservation_id": "FDZ0T5",
 "user_id": "sophia_martin_4574",
 "origin": "JFK",
 "destination": "PHL",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "JFK",
   "destination": "ORD",
   "flight_number": "HAT079",
   "date": "2024-05-17",
   "price": 1956
  },
  {
   "origin": "ORD",
   "destination": "PHL",
   "flight_number": "HAT289",
   "date": "2024-05-17",
   "price": 1822
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 3778
  }
 ],
 "created_at": "2024-05-13T08:25:23",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `HSR97W`
```json
{
 "reservation_id": "HSR97W",
 "user_id": "sophia_martin_4574",
 "origin": "ORD",
 "destination": "SFO",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "ORD",
   "destination": "PHL",
   "flight_number": "HAT289",
   "date": "2024-05-22",
   "price": 705
  },
  {
   "origin": "PHL",
   "destination": "SFO",
   "flight_number": "HAT199",
   "date": "2024-05-22",
   "price": 492
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 1227
  }
 ],
 "created_at": "2024-05-11T10:09:09",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `HTR26G`
```json
{
 "reservation_id": "HTR26G",
 "user_id": "sophia_martin_4574",
 "origin": "MSP",
 "destination": "DFW",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MSP",
   "destination": "EWR",
   "flight_number": "HAT300",
   "date": "2024-05-16",
   "price": 168
  },
  {
   "origin": "EWR",
   "destination": "DFW",
   "flight_number": "HAT231",
   "date": "2024-05-16",
   "price": 181
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 349
  }
 ],
 "created_at": "2024-05-03T16:11:42",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `MFRB94`
```json
{
 "reservation_id": "MFRB94",
 "user_id": "sophia_martin_4574",
 "origin": "MCO",
 "destination": "LGA",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-27",
   "price": 1592
  },
  {
   "origin": "PHX",
   "destination": "LGA",
   "flight_number": "HAT256",
   "date": "2024-05-28",
   "price": 412
  },
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT219",
   "date": "2024-05-30",
   "price": 730
  },
  {
   "origin": "PHX",
   "destination": "MCO",
   "flight_number": "HAT181",
   "date": "2024-05-30",
   "price": 1654
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 4418
  }
 ],
 "created_at": "2024-05-13T02:40:44",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `PUNERT`
```json
{
 "reservation_id": "PUNERT",
 "user_id": "sophia_martin_4574",
 "origin": "BOS",
 "destination": "DEN",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "BOS",
   "destination": "MIA",
   "flight_number": "HAT086",
   "date": "2024-05-22",
   "price": 721
  },
  {
   "origin": "MIA",
   "destination": "DEN",
   "flight_number": "HAT148",
   "date": "2024-05-22",
   "price": 1606
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Martin",
   "dob": "1990-10-25"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 2327
  }
 ],
 "created_at": "2024-05-06T12:18:24",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `SE9KEL`
```json
{
 "reservation_id": "SE9KEL",
 "user_id": "sophia_martin_4574",
 "origin": "LAX",
 "destination": "BOS",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAX",
   "destination": "SFO",
   "flight_number": "HAT034",
   "date": "2024-05-17",
   "price": 411
  },
  {
   "origin": "SFO",
   "destination": "BOS",
   "flight_number": "HAT026",
   "date": "2024-05-17",
   "price": 1541
  },
  {
   "origin": "BOS",
   "destination": "MIA",
   "flight_number": "HAT247",
   "date": "2024-05-29",
   "price": 933
  },
  {
   "origin": "MIA",
   "destination": "LAX",
   "flight_number": "HAT250",
   "date": "2024-05-29",
   "price": 1998
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Brown",
   "dob": "1979-12-22"
  },
  {
   "first_name": "Emma",
   "last_name": "Li",
   "dob": "1972-12-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1402274",
   "amount": 9826
  }
 ],
 "created_at": "2024-05-13T19:18:07",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT026` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT026",
 "origin": "SFO",
 "destination": "BOS",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "22:00:00"
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
### flight `HAT079` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT079",
 "origin": "JFK",
 "destination": "ORD",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "02:30:00"
}
```
### flight `HAT086` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT086",
 "origin": "BOS",
 "destination": "MIA",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
### flight `HAT142` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT142",
 "origin": "DFW",
 "destination": "EWR",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "21:30:00"
}
```
### flight `HAT148` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT148",
 "origin": "MIA",
 "destination": "DEN",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "02:00:00+1"
}
```
### flight `HAT181` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT181",
 "origin": "PHX",
 "destination": "MCO",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "03:30:00+1"
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
### flight `HAT219` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT219",
 "origin": "LGA",
 "destination": "PHX",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "18:30:00"
}
```
### flight `HAT231` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT231",
 "origin": "EWR",
 "destination": "DFW",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "19:30:00"
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
### flight `HAT250` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT250",
 "origin": "MIA",
 "destination": "LAX",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "03:00:00+1"
}
```
### flight `HAT256` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT256",
 "origin": "PHX",
 "destination": "LGA",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "17:30:00"
}
```
### flight `HAT289` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT289",
 "origin": "ORD",
 "destination": "PHL",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "07:00:00"
}
```
### flight `HAT300` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT300",
 "origin": "MSP",
 "destination": "EWR",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
