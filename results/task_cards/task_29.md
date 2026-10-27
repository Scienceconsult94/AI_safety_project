# Airline task 29

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=3 (read=1, write=2, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test complex reservation change.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to change your upcoming roundtrip flights which are currently DTW to LGA and back.

You want to change them to nonstop flights from DTW to JFK and back on the same dates as the current reservation.

**known_info:**

You are Raj Brown.

Your user id is raj_brown_5782.

The reservation ID is VA5SGQ for your DTW to LGA trip.

**unknown_info:**

None

**task_instructions:**

You only want early flights that arrive before 7am at the destination.

You also want be sure to get the cheapest Economy (not Basic Economy) options within those constraints.

If the agent asks, you want your return flight to leave on the 19th.

You want the agent to figure out for you which flights fit these requirements.

Since you took insurance for this trip, you want change fees waived (mention your health problem at the start of the conversation).

If and only if the prices are provided to you and you are asked to choose, choose flights HAT169 and HAT033 (if these are available within the options the agent gives you).

You also want to add 1 checked bag.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "29_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "VA5SGQ"
  },
  "info": null
 },
 {
  "action_id": "29_1",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "VA5SGQ"
  },
  "info": null
 },
 {
  "action_id": "29_2",
  "name": "book_reservation",
  "arguments": {
   "user_id": "raj_brown_5782",
   "origin": "DTW",
   "destination": "JFK",
   "flight_type": "round_trip",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT169",
     "date": "2024-05-17"
    },
    {
     "flight_number": "HAT033",
     "date": "2024-05-19"
    }
   ],
   "passengers": [
    {
     "first_name": "Raj",
     "last_name": "Brown",
     "dob": "1967-03-12"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "credit_card_8003957",
     "amount": 282
    }
   ],
   "total_baggages": 1,
   "nonfree_baggages": 0,
   "insurance": "no"
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
 "Agent informs the user that the reservation can't be changed and it can be cancelled instead.",
 "Agent cancelled reservation VA5SGQ.",
 "Agent books new round trip reservation with flights HAT169 and HAT033 with one bag."
]
```

## DB records referenced
### user `raj_brown_5782`
```json
{
 "user_id": "raj_brown_5782",
 "name": {
  "first_name": "Raj",
  "last_name": "Brown"
 },
 "dob": "1967-03-12",
 "membership": "regular",
 "payment_methods": {
  "credit_card_7686643": {
   "source": "credit_card",
   "id": "credit_card_7686643",
   "brand": "mastercard",
   "last_four": "2273"
  },
  "gift_card_6468981": {
   "source": "gift_card",
   "id": "gift_card_6468981",
   "amount": 279.0
  },
  "credit_card_8003957": {
   "source": "credit_card",
   "id": "credit_card_8003957",
   "brand": "visa",
   "last_four": "6521"
  },
  "credit_card_8782472": {
   "source": "credit_card",
   "id": "credit_card_8782472",
   "brand": "mastercard",
   "last_four": "1949"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Juan",
   "last_name": "Thomas",
   "dob": "1990-07-04"
  }
 ],
 "reservations": [
  "VA5SGQ",
  "41WSQQ",
  "D9R9S0",
  "HTGCBX",
  "Q0K59Y",
  "N1EBKX"
 ]
}
```
### reservation `41WSQQ`
```json
{
 "reservation_id": "41WSQQ",
 "user_id": "raj_brown_5782",
 "origin": "PHL",
 "destination": "EWR",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "PHL",
   "destination": "CLT",
   "flight_number": "HAT243",
   "date": "2024-05-19",
   "price": 125
  },
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT108",
   "date": "2024-05-19",
   "price": 110
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT215",
   "date": "2024-05-26",
   "price": 123
  },
  {
   "origin": "CLT",
   "destination": "PHL",
   "flight_number": "HAT205",
   "date": "2024-05-26",
   "price": 177
  }
 ],
 "passengers": [
  {
   "first_name": "Ethan",
   "last_name": "Silva",
   "dob": "1972-01-13"
  },
  {
   "first_name": "Noah",
   "last_name": "Ahmed",
   "dob": "1978-05-11"
  },
  {
   "first_name": "Olivia",
   "last_name": "Wilson",
   "dob": "1982-07-08"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7686643",
   "amount": 1605
  }
 ],
 "created_at": "2024-05-06T01:26:36",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `D9R9S0`
```json
{
 "reservation_id": "D9R9S0",
 "user_id": "raj_brown_5782",
 "origin": "EWR",
 "destination": "PHL",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT270",
   "date": "2024-05-16",
   "price": 178
  },
  {
   "origin": "CLT",
   "destination": "PHL",
   "flight_number": "HAT205",
   "date": "2024-05-16",
   "price": 149
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Brown",
   "dob": "1967-03-12"
  },
  {
   "first_name": "Juan",
   "last_name": "Thomas",
   "dob": "1990-07-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7686643",
   "amount": 654
  }
 ],
 "created_at": "2024-05-02T05:47:45",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `HTGCBX`
```json
{
 "reservation_id": "HTGCBX",
 "user_id": "raj_brown_5782",
 "origin": "PHL",
 "destination": "EWR",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "PHL",
   "destination": "CLT",
   "flight_number": "HAT269",
   "date": "2024-05-13",
   "price": 1261
  },
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT157",
   "date": "2024-05-13",
   "price": 854
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Brown",
   "dob": "1967-03-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7686643",
   "amount": 2145
  }
 ],
 "created_at": "2024-05-08T06:17:30",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `N1EBKX`
```json
{
 "reservation_id": "N1EBKX",
 "user_id": "raj_brown_5782",
 "origin": "MCO",
 "destination": "MSP",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MCO",
   "destination": "MSP",
   "flight_number": "HAT298",
   "date": "2024-05-15",
   "price": 80
  },
  {
   "origin": "MSP",
   "destination": "MCO",
   "flight_number": "HAT036",
   "date": "2024-05-21",
   "price": 62
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Brown",
   "dob": "1967-03-12"
  },
  {
   "first_name": "Mei",
   "last_name": "Lopez",
   "dob": "1988-07-06"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7686643",
   "amount": 344
  }
 ],
 "created_at": "2024-05-11T13:37:11",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `Q0K59Y`
```json
{
 "reservation_id": "Q0K59Y",
 "user_id": "raj_brown_5782",
 "origin": "ATL",
 "destination": "MSP",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "ATL",
   "destination": "MCO",
   "flight_number": "HAT203",
   "date": "2024-05-12",
   "price": 1270
  },
  {
   "origin": "MCO",
   "destination": "MSP",
   "flight_number": "HAT298",
   "date": "2024-05-12",
   "price": 498
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Brown",
   "dob": "1967-03-12"
  },
  {
   "first_name": "Juan",
   "last_name": "Thomas",
   "dob": "1990-07-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_8782472",
   "amount": 3536
  }
 ],
 "created_at": "2024-05-08T09:56:28",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `VA5SGQ`
```json
{
 "reservation_id": "VA5SGQ",
 "user_id": "raj_brown_5782",
 "origin": "DTW",
 "destination": "LGA",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT035",
   "date": "2024-05-17",
   "price": 163
  },
  {
   "origin": "PHX",
   "destination": "LGA",
   "flight_number": "HAT066",
   "date": "2024-05-17",
   "price": 184
  },
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT002",
   "date": "2024-05-19",
   "price": 174
  },
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT106",
   "date": "2024-05-20",
   "price": 135
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Brown",
   "dob": "1967-03-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_8003957",
   "amount": 686
  }
 ],
 "created_at": "2024-05-08T18:28:13",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT002` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT002",
 "origin": "LGA",
 "destination": "PHX",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
}
```
### flight `HAT033` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT033",
 "origin": "JFK",
 "destination": "DTW",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "02:00:00"
}
```
### flight `HAT035` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT035",
 "origin": "DTW",
 "destination": "PHX",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT036` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT036",
 "origin": "MSP",
 "destination": "MCO",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT066` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT066",
 "origin": "PHX",
 "destination": "LGA",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
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
### flight `HAT108` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT108",
 "origin": "CLT",
 "destination": "EWR",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "05:00:00"
}
```
### flight `HAT157` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT157",
 "origin": "CLT",
 "destination": "EWR",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
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
### flight `HAT203` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT203",
 "origin": "ATL",
 "destination": "MCO",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "02:30:00"
}
```
### flight `HAT205` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT205",
 "origin": "CLT",
 "destination": "PHL",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
### flight `HAT215` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT215",
 "origin": "EWR",
 "destination": "CLT",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT243` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT243",
 "origin": "PHL",
 "destination": "CLT",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "01:00:00"
}
```
### flight `HAT269` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT269",
 "origin": "PHL",
 "destination": "CLT",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "08:00:00"
}
```
### flight `HAT270` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT270",
 "origin": "EWR",
 "destination": "CLT",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT298` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT298",
 "origin": "MCO",
 "destination": "MSP",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "06:00:00"
}
```
