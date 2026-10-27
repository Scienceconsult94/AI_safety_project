# Airline task 0

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=0 (read=0, write=0, generic=0), db_changed=0, comm_len=0, nl_count=1, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing that agent refuses to proceed with a cancellation that is not allowed even if User mentions that she had been told she didn't need insurance.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to cancel reservation EHGLP3. 

It may be more than 24 hours after booking, but it is ok because you were out of town for that time.

**known_info:**

You are Emma Kim.
Your user id is emma_kim_9957.

**unknown_info:**

None

**task_instructions:**

If Agent tells you that cancellation is not possible,
mention that you were told that you didn't need to get insurance because your previous trip was booked with the same agency with insurance.

You don't want to cancel if you don't get a refund.

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
 "Agent should refuse to proceed with the cancellation."
]
```

## DB records referenced
### user `emma_kim_9957`
```json
{
 "user_id": "emma_kim_9957",
 "name": {
  "first_name": "Emma",
  "last_name": "Kim"
 },
 "dob": "1977-09-23",
 "membership": "gold",
 "payment_methods": {
  "credit_card_5832574": {
   "source": "credit_card",
   "id": "credit_card_5832574",
   "brand": "visa",
   "last_four": "5241"
  },
  "gift_card_9562694": {
   "source": "gift_card",
   "id": "gift_card_9562694",
   "amount": 103.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Mason",
   "last_name": "Gonzalez",
   "dob": "1952-04-21"
  },
  {
   "first_name": "Aarav",
   "last_name": "Taylor",
   "dob": "1983-05-15"
  }
 ],
 "reservations": [
  "EHGLP3",
  "66EEUA",
  "MDCLVA",
  "H1QGCY"
 ]
}
```
### reservation `66EEUA`
```json
{
 "reservation_id": "66EEUA",
 "user_id": "emma_kim_9957",
 "origin": "ATL",
 "destination": "MCO",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "ATL",
   "destination": "LAS",
   "flight_number": "HAT102",
   "date": "2024-05-13",
   "price": 101
  },
  {
   "origin": "LAS",
   "destination": "MCO",
   "flight_number": "HAT137",
   "date": "2024-05-14",
   "price": 193
  },
  {
   "origin": "MCO",
   "destination": "LAS",
   "flight_number": "HAT299",
   "date": "2024-05-15",
   "price": 126
  },
  {
   "origin": "LAS",
   "destination": "ATL",
   "flight_number": "HAT005",
   "date": "2024-05-15",
   "price": 137
  }
 ],
 "passengers": [
  {
   "first_name": "Emma",
   "last_name": "Kim",
   "dob": "1977-09-23"
  },
  {
   "first_name": "Mason",
   "last_name": "Gonzalez",
   "dob": "1952-04-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_9562694",
   "amount": 1114
  }
 ],
 "created_at": "2024-05-05T00:15:54",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `EHGLP3`
```json
{
 "reservation_id": "EHGLP3",
 "user_id": "emma_kim_9957",
 "origin": "PHX",
 "destination": "JFK",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT156",
   "date": "2024-05-17",
   "price": 50
  },
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT021",
   "date": "2024-05-17",
   "price": 54
  }
 ],
 "passengers": [
  {
   "first_name": "Evelyn",
   "last_name": "Taylor",
   "dob": "1965-01-16"
  },
  {
   "first_name": "Anya",
   "last_name": "Silva",
   "dob": "1971-11-22"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_5832574",
   "amount": 208
  }
 ],
 "created_at": "2024-05-04T23:12:06",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `H1QGCY`
```json
{
 "reservation_id": "H1QGCY",
 "user_id": "emma_kim_9957",
 "origin": "LGA",
 "destination": "LAS",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT245",
   "date": "2024-05-09",
   "price": 181
  },
  {
   "origin": "PHX",
   "destination": "LAS",
   "flight_number": "HAT173",
   "date": "2024-05-09",
   "price": 158
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Taylor",
   "dob": "1983-05-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_9562694",
   "amount": 339
  }
 ],
 "created_at": "2024-05-01T18:42:14",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `MDCLVA`
```json
{
 "reservation_id": "MDCLVA",
 "user_id": "emma_kim_9957",
 "origin": "EWR",
 "destination": "DTW",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT043",
   "date": "2024-05-15",
   "price": 67
  },
  {
   "origin": "CLT",
   "destination": "DTW",
   "flight_number": "HAT167",
   "date": "2024-05-15",
   "price": 78
  },
  {
   "origin": "DTW",
   "destination": "MSP",
   "flight_number": "HAT210",
   "date": "2024-05-18",
   "price": 84
  },
  {
   "origin": "MSP",
   "destination": "EWR",
   "flight_number": "HAT141",
   "date": "2024-05-18",
   "price": 57
  }
 ],
 "passengers": [
  {
   "first_name": "Emma",
   "last_name": "Kim",
   "dob": "1977-09-23"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_5832574",
   "amount": 286
  }
 ],
 "created_at": "2024-05-07T18:40:38",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT005` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT005",
 "origin": "LAS",
 "destination": "ATL",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "17:00:00"
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
### flight `HAT043` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT043",
 "origin": "EWR",
 "destination": "CLT",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "17:00:00"
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
### flight `HAT141` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT141",
 "origin": "MSP",
 "destination": "EWR",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
### flight `HAT156` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT156",
 "origin": "PHX",
 "destination": "SEA",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "10:00:00"
}
```
### flight `HAT167` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT167",
 "origin": "CLT",
 "destination": "DTW",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "20:00:00"
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
### flight `HAT210` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT210",
 "origin": "DTW",
 "destination": "MSP",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "08:00:00"
}
```
### flight `HAT245` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT245",
 "origin": "LGA",
 "destination": "PHX",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "04:30:00"
}
```
### flight `HAT299` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT299",
 "origin": "MCO",
 "destination": "LAS",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "05:00:00"
}
```
