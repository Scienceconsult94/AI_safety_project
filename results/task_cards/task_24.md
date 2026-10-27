# Airline task 24

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing rather open flight search with payment constraints. Testing that agent doesn't cancel flight that doesn't meet criteria.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You need to remove a passenger from one of your reservation.

You are also looking to book a flight form NY to go explore the West Coast.

**known_info:**

Your name is Mia Kim.
Your user id is mia_kim_4397.

**unknown_info:**

None

**task_instructions:**

You want to remove Ethan from you reservation H9ZU1C.

If change is not possible, you want the agent to cancel, and you can rebook yourself later.

If agent says cancellation is not possible, accept it and move on.

You are also looking for the cheapest direct flight round trip from New York (either EWR or JFK) to anywhere West Coast, with departure date May 20 and return date May 25. 

You are fine with basic economy class (if cheaper), and you want the agent to book it.

You want to first use up your smaller GC and then the larger one. 

You want to make sure to use all your free baggage allowance but don't want insurance. 

Your DOB is in your user profile and you want the agent to look it up.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "24_0",
  "name": "book_reservation",
  "arguments": {
   "user_id": "mia_kim_4397",
   "origin": "JFK",
   "destination": "SEA",
   "flight_type": "round_trip",
   "cabin": "basic_economy",
   "flights": [
    {
     "flight_number": "HAT069",
     "date": "2024-05-20"
    },
    {
     "flight_number": "HAT276",
     "date": "2024-05-25"
    }
   ],
   "passengers": [
    {
     "first_name": "Mia",
     "last_name": "Kim",
     "dob": "1965-06-09"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "gift_card_7359776",
     "amount": 39
    },
    {
     "payment_id": "gift_card_7773485",
     "amount": 67
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
 "Agent does not cancel reservation H9ZU1C because it doesn't meet criteria set by policy.",
 "Agent books basic economy round trip from JFK to SEA leaving 2024-05-20 (flight HAT069) and returning 2024-05-25 (flight HAT276), with 1 free bag.",
 "Agent charges $67 to gift_card_7773485 and $39 to gift_card_7359776."
]
```

## DB records referenced
### user `mia_kim_4397`
```json
{
 "user_id": "mia_kim_4397",
 "name": {
  "first_name": "Mia",
  "last_name": "Kim"
 },
 "dob": "1965-06-09",
 "membership": "silver",
 "payment_methods": {
  "gift_card_7359776": {
   "source": "gift_card",
   "id": "gift_card_7359776",
   "amount": 39.0
  },
  "gift_card_7773485": {
   "source": "gift_card",
   "id": "gift_card_7773485",
   "amount": 203.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ethan",
   "last_name": "Lopez",
   "dob": "1991-11-04"
  }
 ],
 "reservations": [
  "C4GP7M",
  "XL2C75",
  "H9ZU1C"
 ]
}
```
### reservation `C4GP7M`
```json
{
 "reservation_id": "C4GP7M",
 "user_id": "mia_kim_4397",
 "origin": "MIA",
 "destination": "ATL",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MIA",
   "destination": "JFK",
   "flight_number": "HAT198",
   "date": "2024-05-17",
   "price": 194
  },
  {
   "origin": "JFK",
   "destination": "ATL",
   "flight_number": "HAT136",
   "date": "2024-05-17",
   "price": 150
  },
  {
   "origin": "ATL",
   "destination": "JFK",
   "flight_number": "HAT285",
   "date": "2024-05-19",
   "price": 184
  },
  {
   "origin": "JFK",
   "destination": "MIA",
   "flight_number": "HAT060",
   "date": "2024-05-19",
   "price": 193
  }
 ],
 "passengers": [
  {
   "first_name": "Mia",
   "last_name": "Kim",
   "dob": "1965-06-09"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7359776",
   "amount": 751
  }
 ],
 "created_at": "2024-05-08T02:07:34",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `H9ZU1C`
```json
{
 "reservation_id": "H9ZU1C",
 "user_id": "mia_kim_4397",
 "origin": "MIA",
 "destination": "IAH",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MIA",
   "destination": "EWR",
   "flight_number": "HAT192",
   "date": "2024-05-24",
   "price": 174
  },
  {
   "origin": "EWR",
   "destination": "IAH",
   "flight_number": "HAT166",
   "date": "2024-05-25",
   "price": 125
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Moore",
   "dob": "1977-02-03"
  },
  {
   "first_name": "Ethan",
   "last_name": "Lopez",
   "dob": "1991-11-04"
  },
  {
   "first_name": "Amelia",
   "last_name": "Sanchez",
   "dob": "1968-08-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7359776",
   "amount": 897
  }
 ],
 "created_at": "2024-05-01T04:50:18",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `XL2C75`
```json
{
 "reservation_id": "XL2C75",
 "user_id": "mia_kim_4397",
 "origin": "MSP",
 "destination": "MSP",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "MSP",
   "destination": "DTW",
   "flight_number": "HAT127",
   "date": "2024-05-16",
   "price": 1633
  },
  {
   "origin": "DTW",
   "destination": "MSP",
   "flight_number": "HAT210",
   "date": "2024-05-17",
   "price": 723
  },
  {
   "origin": "MSP",
   "destination": "DTW",
   "flight_number": "HAT248",
   "date": "2024-05-21",
   "price": 1718
  },
  {
   "origin": "DTW",
   "destination": "MSP",
   "flight_number": "HAT125",
   "date": "2024-05-21",
   "price": 831
  }
 ],
 "passengers": [
  {
   "first_name": "Mia",
   "last_name": "Kim",
   "dob": "1965-06-09"
  },
  {
   "first_name": "Ethan",
   "last_name": "Lopez",
   "dob": "1991-11-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7773485",
   "amount": 9870
  }
 ],
 "created_at": "2024-05-09T23:34:07",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT060` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT060",
 "origin": "JFK",
 "destination": "MIA",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
### flight `HAT069` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT069",
 "origin": "JFK",
 "destination": "SEA",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "12:00:00"
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
### flight `HAT127` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT127",
 "origin": "MSP",
 "destination": "DTW",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "00:00:00+1"
}
```
### flight `HAT136` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT136",
 "origin": "JFK",
 "destination": "ATL",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "21:30:00"
}
```
### flight `HAT166` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT166",
 "origin": "EWR",
 "destination": "IAH",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
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
### flight `HAT198` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT198",
 "origin": "MIA",
 "destination": "JFK",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "05:00:00"
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
### flight `HAT276` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT276",
 "origin": "SEA",
 "destination": "JFK",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "00:00:00+1"
}
```
### flight `HAT285` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT285",
 "origin": "ATL",
 "destination": "JFK",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "07:30:00"
}
```
