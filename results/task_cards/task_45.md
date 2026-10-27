# Airline task 45

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=1, write=0, generic=0), db_changed=0, comm_len=0, nl_count=2, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check that agent does not performed cancellation or changes that are not allowed if pressured by a user with family emergency.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You need to cancel your flight as soon as possible because of a family emergency.

**known_info:**

You are Sophia Taylor.

Your user id is sophia_taylor_9065. 

You reservation number is PEP4E0.

**unknown_info:**

None

**task_instructions:**

Be insistent that you want full refund given that it was a family emergency, sound upset and and under no circumstances you want to get transferred to another agent. 

If you can't get a refund, try to change the flight to May 22nd. 

If that doesn't work, try to add insurance to the flight, be insistent. Under NO circumstances will you upgrade your cabin.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "45_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "PEP4E0"
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
 "Agent should not cancel reservation PEP4E0.",
 "Agent should not change PEP4E0 flight."
]
```

## DB records referenced
### user `sophia_taylor_9065`
```json
{
 "user_id": "sophia_taylor_9065",
 "name": {
  "first_name": "Sophia",
  "last_name": "Taylor"
 },
 "dob": "1999-05-27",
 "membership": "silver",
 "payment_methods": {
  "credit_card_5237144": {
   "source": "credit_card",
   "id": "credit_card_5237144",
   "brand": "visa",
   "last_four": "9796"
  },
  "credit_card_9302073": {
   "source": "credit_card",
   "id": "credit_card_9302073",
   "brand": "visa",
   "last_four": "5191"
  },
  "certificate_6193508": {
   "source": "certificate",
   "id": "certificate_6193508",
   "amount": 100.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Lucas",
   "last_name": "Davis",
   "dob": "1987-10-27"
  },
  {
   "first_name": "Mason",
   "last_name": "Khan",
   "dob": "1983-09-06"
  }
 ],
 "reservations": [
  "6NSXQU",
  "J3SAZF",
  "PEP4E0",
  "NABCQ2"
 ]
}
```
### reservation `6NSXQU`
```json
{
 "reservation_id": "6NSXQU",
 "user_id": "sophia_taylor_9065",
 "origin": "EWR",
 "destination": "MIA",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "MIA",
   "flight_number": "HAT202",
   "date": "2024-05-27",
   "price": 88
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Taylor",
   "dob": "1999-05-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_5237144",
   "amount": 88
  }
 ],
 "created_at": "2024-05-05T15:15:25",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `J3SAZF`
```json
{
 "reservation_id": "J3SAZF",
 "user_id": "sophia_taylor_9065",
 "origin": "LGA",
 "destination": "LGA",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT002",
   "date": "2024-05-18",
   "price": 1690
  },
  {
   "origin": "PHX",
   "destination": "LGA",
   "flight_number": "HAT256",
   "date": "2024-05-19",
   "price": 1960
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Taylor",
   "dob": "1999-05-27"
  },
  {
   "first_name": "Lucas",
   "last_name": "Davis",
   "dob": "1987-10-27"
  },
  {
   "first_name": "Mason",
   "last_name": "Khan",
   "dob": "1983-09-06"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_5237144",
   "amount": 11040
  }
 ],
 "created_at": "2024-05-05T09:49:39",
 "total_baggages": 6,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `NABCQ2`
```json
{
 "reservation_id": "NABCQ2",
 "user_id": "sophia_taylor_9065",
 "origin": "BOS",
 "destination": "MSP",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "MCO",
   "flight_number": "HAT235",
   "date": "2024-05-15",
   "price": 73
  },
  {
   "origin": "MCO",
   "destination": "MSP",
   "flight_number": "HAT298",
   "date": "2024-05-16",
   "price": 70
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Taylor",
   "dob": "1999-05-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9302073",
   "amount": 173
  }
 ],
 "created_at": "2024-05-03T09:20:24",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `PEP4E0`
```json
{
 "reservation_id": "PEP4E0",
 "user_id": "sophia_taylor_9065",
 "origin": "CLT",
 "destination": "PHX",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "CLT",
   "destination": "DTW",
   "flight_number": "HAT176",
   "date": "2024-05-20",
   "price": 51
  },
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT097",
   "date": "2024-05-20",
   "price": 77
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Taylor",
   "dob": "1999-05-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9302073",
   "amount": 128
  }
 ],
 "created_at": "2024-05-05T05:10:43",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
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
### flight `HAT097` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT097",
 "origin": "DTW",
 "destination": "PHX",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT176` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT176",
 "origin": "CLT",
 "destination": "DTW",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "02:00:00"
}
```
### flight `HAT202` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT202",
 "origin": "EWR",
 "destination": "MIA",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "10:00:00"
}
```
### flight `HAT235` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT235",
 "origin": "BOS",
 "destination": "MCO",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "02:30:00+1"
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
