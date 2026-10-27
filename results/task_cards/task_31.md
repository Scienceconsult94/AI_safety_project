# Airline task 31

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=0 (read=0, write=0, generic=0), db_changed=0, comm_len=0, nl_count=1, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test for flight change. Flight cannot be changed.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

Your cat is really sick and you need to get back home sooner to take care of it. 
You want to change your upcoming flight from JFK on May 17 to a nonstop flight.

**known_info:**

Your name is Daiki Lee.
Your user id is daiki_lee_6144.

**unknown_info:**

You do not know your reservation id.

**task_instructions:**

You are willing to do the change only if it costs less than $100.

You do not want to buy a new flight.

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
 "Agent doesn't book any flight."
]
```

## DB records referenced
### user `daiki_lee_6144`
```json
{
 "user_id": "daiki_lee_6144",
 "name": {
  "first_name": "Daiki",
  "last_name": "Lee"
 },
 "dob": "1976-10-08",
 "membership": "regular",
 "payment_methods": {
  "credit_card_6198952": {
   "source": "credit_card",
   "id": "credit_card_6198952",
   "brand": "visa",
   "last_four": "9734"
  },
  "gift_card_3112961": {
   "source": "gift_card",
   "id": "gift_card_3112961",
   "amount": 51.0
  },
  "gift_card_5128346": {
   "source": "gift_card",
   "id": "gift_card_5128346",
   "amount": 262.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Raj",
   "last_name": "Muller",
   "dob": "1967-10-16"
  }
 ],
 "reservations": [
  "DF89BM",
  "COVE6R",
  "IIHXDG"
 ]
}
```
### reservation `COVE6R`
```json
{
 "reservation_id": "COVE6R",
 "user_id": "daiki_lee_6144",
 "origin": "MCO",
 "destination": "BOS",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "BOS",
   "flight_number": "HAT017",
   "date": "2024-05-27",
   "price": 1394
  }
 ],
 "passengers": [
  {
   "first_name": "Daiki",
   "last_name": "Lee",
   "dob": "1976-10-08"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5128346",
   "amount": 1424
  }
 ],
 "created_at": "2024-05-09T21:28:12",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `DF89BM`
```json
{
 "reservation_id": "DF89BM",
 "user_id": "daiki_lee_6144",
 "origin": "JFK",
 "destination": "DTW",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "ORD",
   "flight_number": "HAT079",
   "date": "2024-05-17",
   "price": 63
  },
  {
   "origin": "ORD",
   "destination": "DTW",
   "flight_number": "HAT020",
   "date": "2024-05-17",
   "price": 78
  },
  {
   "origin": "DTW",
   "destination": "JFK",
   "flight_number": "HAT263",
   "date": "2024-05-24",
   "price": 53
  }
 ],
 "passengers": [
  {
   "first_name": "Daiki",
   "last_name": "Lee",
   "dob": "1976-10-08"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_3112961",
   "amount": 194
  }
 ],
 "created_at": "2024-05-01T23:25:01",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `IIHXDG`
```json
{
 "reservation_id": "IIHXDG",
 "user_id": "daiki_lee_6144",
 "origin": "PHL",
 "destination": "SFO",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "PHL",
   "destination": "SFO",
   "flight_number": "HAT199",
   "date": "2024-05-18",
   "price": 143
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Muller",
   "dob": "1967-10-16"
  },
  {
   "first_name": "Ivan",
   "last_name": "Garcia",
   "dob": "1964-11-26"
  },
  {
   "first_name": "Fatima",
   "last_name": "Moore",
   "dob": "1993-03-01"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_3112961",
   "amount": 519
  }
 ],
 "created_at": "2024-05-07T03:12:00",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT017` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT017",
 "origin": "MCO",
 "destination": "BOS",
 "scheduled_departure_time_est": "10:00:00",
 "scheduled_arrival_time_est": "13:30:00"
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
### flight `HAT263` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT263",
 "origin": "DTW",
 "destination": "JFK",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
