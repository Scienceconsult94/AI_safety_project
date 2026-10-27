# Airline task 19  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=1, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing that Agent follows the policy that basic economy flights cannot be modified.\n\nInstructions should lead to a flight cancellation.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You will have a crazy half-day trip to Texas.

It is in your reservations but you don't remember the reservation id.

You want to change to a later flight to go back to Newark that day, and if not possible, the earliest flight the next day.

Your current return flight departs 3pm (on the 28th).

**known_info:**

Your name is Olivia Gonzalez.

Your user id is olivia_gonzalez_2305.

You currently reside in Newark.

**unknown_info:**

None

**task_instructions:**

You do not accept JFK, only EWR. 

If basic economy cannot be modified, you are willing to cancel the trip using the travel insurance as you feel unwell. You will book the flight again yourself later.

You are reactive to the agent and will not say anything that is not asked.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "19_0",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "Z7GOZK"
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
 "Agent cancels reservation Z7GOZK"
]
```

## DB records referenced
### user `olivia_gonzalez_2305`
```json
{
 "user_id": "olivia_gonzalez_2305",
 "name": {
  "first_name": "Olivia",
  "last_name": "Gonzalez"
 },
 "dob": "1988-06-13",
 "membership": "regular",
 "payment_methods": {
  "gift_card_2200803": {
   "source": "gift_card",
   "id": "gift_card_2200803",
   "amount": 123.0
  },
  "credit_card_9969263": {
   "source": "credit_card",
   "id": "credit_card_9969263",
   "brand": "mastercard",
   "last_four": "9475"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Mei",
   "last_name": "Johansson",
   "dob": "1981-09-25"
  },
  {
   "first_name": "Yara",
   "last_name": "Lopez",
   "dob": "1975-09-15"
  }
 ],
 "reservations": [
  "Z7GOZK",
  "K67C4W",
  "THY2DG"
 ]
}
```
### reservation `K67C4W`
```json
{
 "reservation_id": "K67C4W",
 "user_id": "olivia_gonzalez_2305",
 "origin": "LAS",
 "destination": "MCO",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAS",
   "destination": "MCO",
   "flight_number": "HAT137",
   "date": "2024-05-17",
   "price": 114
  }
 ],
 "passengers": [
  {
   "first_name": "Olivia",
   "last_name": "Gonzalez",
   "dob": "1988-06-13"
  },
  {
   "first_name": "Mei",
   "last_name": "Johansson",
   "dob": "1981-09-25"
  },
  {
   "first_name": "Yara",
   "last_name": "Lopez",
   "dob": "1975-09-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9969263",
   "amount": 342
  }
 ],
 "created_at": "2024-05-11T06:28:05",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `THY2DG`
```json
{
 "reservation_id": "THY2DG",
 "user_id": "olivia_gonzalez_2305",
 "origin": "MSP",
 "destination": "ORD",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MSP",
   "destination": "DTW",
   "flight_number": "HAT248",
   "date": "2024-05-26",
   "price": 160
  },
  {
   "origin": "DTW",
   "destination": "ORD",
   "flight_number": "HAT119",
   "date": "2024-05-26",
   "price": 178
  }
 ],
 "passengers": [
  {
   "first_name": "Yara",
   "last_name": "Martin",
   "dob": "1950-01-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9969263",
   "amount": 338
  }
 ],
 "created_at": "2024-05-03T23:15:42",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `Z7GOZK`
```json
{
 "reservation_id": "Z7GOZK",
 "user_id": "olivia_gonzalez_2305",
 "origin": "EWR",
 "destination": "IAH",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "IAH",
   "flight_number": "HAT188",
   "date": "2024-05-28",
   "price": 52
  },
  {
   "origin": "IAH",
   "destination": "EWR",
   "flight_number": "HAT207",
   "date": "2024-05-28",
   "price": 87
  }
 ],
 "passengers": [
  {
   "first_name": "Olivia",
   "last_name": "Gonzalez",
   "dob": "1988-06-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2200803",
   "amount": 169
  }
 ],
 "created_at": "2024-05-13T19:41:32",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT119` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT119",
 "origin": "DTW",
 "destination": "ORD",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT137` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT137",
 "origin": "LAS",
 "destination": "MCO",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT188` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT188",
 "origin": "EWR",
 "destination": "IAH",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "05:00:00"
}
```
### flight `HAT207` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT207",
 "origin": "IAH",
 "destination": "EWR",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT248` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT248",
 "origin": "MSP",
 "destination": "DTW",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "07:00:00"
}
```
