# Airline task 10  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=0 (read=0, write=0, generic=0), db_changed=0, comm_len=0, nl_count=1, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check that agent doesn't make changes to cabin for only some of the flights in a reservation. Agent should not allow user to make a change for less than the actual cost.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to push back your upcoming flight from IAH to SEA on May 23 to May 24.

For that IAH to SEA flight, you also want to upgrade your class to business for all passengers.

**known_info:**

Your name is Liam Khan.

Your user id is liam_khan_2521.

**unknown_info:**

None

**task_instructions:**

IF and ONLY IF the agent says that is not possible, you are willing to upgrade for both the outbound and return flights. DO NOT volunteer to do this on your own!

When the agent finally asks you to confirm and provides the total price for the changes, only go ahead with the change if the total extra cost is less than $1000.

You are very persistent to try and get what you want under your budget.

You do not accept to change the flight date without changing the cabin to business.

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
 "Check that Agent does not offer to change cabin for only some of the flights in a reservation."
]
```

## DB records referenced
### user `liam_khan_2521`
```json
{
 "user_id": "liam_khan_2521",
 "name": {
  "first_name": "Liam",
  "last_name": "Khan"
 },
 "dob": "1979-09-27",
 "membership": "gold",
 "payment_methods": {
  "certificate_9254323": {
   "source": "certificate",
   "id": "certificate_9254323",
   "amount": 500.0
  },
  "gift_card_7194529": {
   "source": "gift_card",
   "id": "gift_card_7194529",
   "amount": 62.0
  },
  "credit_card_7434610": {
   "source": "credit_card",
   "id": "credit_card_7434610",
   "brand": "mastercard",
   "last_four": "9448"
  },
  "credit_card_7231150": {
   "source": "credit_card",
   "id": "credit_card_7231150",
   "brand": "visa",
   "last_four": "3422"
  },
  "certificate_1849235": {
   "source": "certificate",
   "id": "certificate_1849235",
   "amount": 250.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Fatima",
   "last_name": "Ito",
   "dob": "1983-03-27"
  }
 ],
 "reservations": [
  "4NQLHD",
  "KHIK97",
  "NO6SVK",
  "AJVCTQ",
  "ZB7LBX"
 ]
}
```
### reservation `4NQLHD`
```json
{
 "reservation_id": "4NQLHD",
 "user_id": "liam_khan_2521",
 "origin": "IAH",
 "destination": "SEA",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "IAH",
   "destination": "LAS",
   "flight_number": "HAT190",
   "date": "2024-05-23",
   "price": 126
  },
  {
   "origin": "LAS",
   "destination": "SEA",
   "flight_number": "HAT047",
   "date": "2024-05-23",
   "price": 139
  },
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT021",
   "date": "2024-05-26",
   "price": 148
  },
  {
   "origin": "JFK",
   "destination": "IAH",
   "flight_number": "HAT279",
   "date": "2024-05-27",
   "price": 114
  }
 ],
 "passengers": [
  {
   "first_name": "Liam",
   "last_name": "Khan",
   "dob": "1979-09-27"
  },
  {
   "first_name": "James",
   "last_name": "Kim",
   "dob": "1956-07-08"
  },
  {
   "first_name": "Aarav",
   "last_name": "Lee",
   "dob": "1972-06-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7434610",
   "amount": 1671
  }
 ],
 "created_at": "2024-05-08T11:24:52",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `AJVCTQ`
```json
{
 "reservation_id": "AJVCTQ",
 "user_id": "liam_khan_2521",
 "origin": "PHX",
 "destination": "LAS",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "PHX",
   "destination": "LAS",
   "flight_number": "HAT173",
   "date": "2024-05-10",
   "price": 140
  },
  {
   "origin": "LAS",
   "destination": "PHX",
   "flight_number": "HAT244",
   "date": "2024-05-12",
   "price": 170
  }
 ],
 "passengers": [
  {
   "first_name": "Liam",
   "last_name": "Khan",
   "dob": "1979-09-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7434610",
   "amount": 340
  }
 ],
 "created_at": "2024-05-06T14:43:34",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `KHIK97`
```json
{
 "reservation_id": "KHIK97",
 "user_id": "liam_khan_2521",
 "origin": "ORD",
 "destination": "MSP",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "ORD",
   "destination": "DTW",
   "flight_number": "HAT230",
   "date": "2024-05-18",
   "price": 92
  },
  {
   "origin": "DTW",
   "destination": "MSP",
   "flight_number": "HAT125",
   "date": "2024-05-18",
   "price": 82
  }
 ],
 "passengers": [
  {
   "first_name": "Liam",
   "last_name": "Khan",
   "dob": "1979-09-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7231150",
   "amount": 204
  }
 ],
 "created_at": "2024-05-11T15:45:54",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `NO6SVK`
```json
{
 "reservation_id": "NO6SVK",
 "user_id": "liam_khan_2521",
 "origin": "ATL",
 "destination": "PHX",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "ATL",
   "destination": "LAS",
   "flight_number": "HAT102",
   "date": "2024-05-19",
   "price": 101
  },
  {
   "origin": "LAS",
   "destination": "PHX",
   "flight_number": "HAT095",
   "date": "2024-05-20",
   "price": 188
  }
 ],
 "passengers": [
  {
   "first_name": "Liam",
   "last_name": "Khan",
   "dob": "1979-09-27"
  },
  {
   "first_name": "Fatima",
   "last_name": "Ito",
   "dob": "1983-03-27"
  },
  {
   "first_name": "Emma",
   "last_name": "Khan",
   "dob": "1972-05-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7231150",
   "amount": 957
  }
 ],
 "created_at": "2024-05-10T10:33:57",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `ZB7LBX`
```json
{
 "reservation_id": "ZB7LBX",
 "user_id": "liam_khan_2521",
 "origin": "JFK",
 "destination": "DTW",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "DTW",
   "flight_number": "HAT092",
   "date": "2024-05-15",
   "price": 98
  }
 ],
 "passengers": [
  {
   "first_name": "Fatima",
   "last_name": "Ito",
   "dob": "1983-03-27"
  },
  {
   "first_name": "Ethan",
   "last_name": "Kim",
   "dob": "1998-07-28"
  },
  {
   "first_name": "Juan",
   "last_name": "Taylor",
   "dob": "1982-03-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7231150",
   "amount": 384
  }
 ],
 "created_at": "2024-05-08T15:29:42",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT021` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT021",
 "origin": "SEA",
 "destination": "JFK",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT047` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT047",
 "origin": "LAS",
 "destination": "SEA",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "15:30:00"
}
```
### flight `HAT092` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT092",
 "origin": "JFK",
 "destination": "DTW",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "02:00:00"
}
```
### flight `HAT095` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT095",
 "origin": "LAS",
 "destination": "PHX",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT102` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT102",
 "origin": "ATL",
 "destination": "LAS",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT125` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT125",
 "origin": "DTW",
 "destination": "MSP",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
### flight `HAT173` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT173",
 "origin": "PHX",
 "destination": "LAS",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "10:00:00"
}
```
### flight `HAT190` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT190",
 "origin": "IAH",
 "destination": "LAS",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
### flight `HAT230` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT230",
 "origin": "ORD",
 "destination": "DTW",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "01:00:00"
}
```
### flight `HAT244` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT244",
 "origin": "LAS",
 "destination": "PHX",
 "scheduled_departure_time_est": "10:00:00",
 "scheduled_arrival_time_est": "11:00:00"
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
