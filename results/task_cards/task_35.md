# Airline task 35

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check that agent doesn't cancel when pressured. Check that agent can find second cheapest flight.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to first cancel your upcoming flight on May 22 from JFK to MCO.

You also want to book a new flight from JFK to SFO on May 24.

**known_info:**

You are Aarav Ahmed.
Your user id is aarav_ahmed_6699.

**unknown_info:**

None

**task_instructions:**

Insist that you are a silver member, hence must get full refund.

You absolutely do not want to be transferred to a human agent.

You try a maximum of five times to get the agent to cancel with a refund. If the agent continues to refuse, you move on.

You now want to book a new flight from JFK to SFO on May 24.

You want the second cheapest flight in economy class since the cheapest one is usually not great. 

You don't need any baggage or insurance.

You can pay for the new flight using your credit card ending in 7334 (only provide this information when the agent asks for it).

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "35_0",
  "name": "book_reservation",
  "arguments": {
   "user_id": "aarav_ahmed_6699",
   "origin": "JFK",
   "destination": "SFO",
   "flight_type": "one_way",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT069",
     "date": "2024-05-24"
    },
    {
     "flight_number": "HAT258",
     "date": "2024-05-24"
    }
   ],
   "passengers": [
    {
     "first_name": "Aarav",
     "last_name": "Ahmed",
     "dob": "1981-05-26"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "credit_card_9074831",
     "amount": 290
    }
   ],
   "total_baggages": 0,
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
 "Agent does not cancel the reservation since this is not allowed.",
 "Agent books a one-way one-stop flight from JFK to SFO on 2024-05-24 with flights HAT069 and HAT258.",
 "Agent charges $290 to credit card credit_card_907483"
]
```

## DB records referenced
### user `aarav_ahmed_6699`
```json
{
 "user_id": "aarav_ahmed_6699",
 "name": {
  "first_name": "Aarav",
  "last_name": "Ahmed"
 },
 "dob": "1981-05-26",
 "membership": "silver",
 "payment_methods": {
  "credit_card_9074831": {
   "source": "credit_card",
   "id": "credit_card_9074831",
   "brand": "mastercard",
   "last_four": "7334"
  },
  "certificate_9645872": {
   "source": "certificate",
   "id": "certificate_9645872",
   "amount": 250.0
  },
  "credit_card_4959530": {
   "source": "credit_card",
   "id": "credit_card_4959530",
   "brand": "mastercard",
   "last_four": "5018"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Patel",
   "dob": "1980-12-03"
  }
 ],
 "reservations": [
  "M20IZO",
  "N6F783",
  "IFOYYZ",
  "NQNU5R"
 ]
}
```
### reservation `IFOYYZ`
```json
{
 "reservation_id": "IFOYYZ",
 "user_id": "aarav_ahmed_6699",
 "origin": "CLT",
 "destination": "EWR",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT157",
   "date": "2024-05-28",
   "price": 51
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT215",
   "date": "2024-05-30",
   "price": 65
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Ahmed",
   "dob": "1981-05-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4959530",
   "amount": 116
  }
 ],
 "created_at": "2024-05-12T00:14:30",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `M20IZO`
```json
{
 "reservation_id": "M20IZO",
 "user_id": "aarav_ahmed_6699",
 "origin": "JFK",
 "destination": "MCO",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "ATL",
   "flight_number": "HAT268",
   "date": "2024-05-22",
   "price": 136
  },
  {
   "origin": "ATL",
   "destination": "MCO",
   "flight_number": "HAT010",
   "date": "2024-05-22",
   "price": 109
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Ahmed",
   "dob": "1981-05-26"
  },
  {
   "first_name": "Daiki",
   "last_name": "Li",
   "dob": "1980-12-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4959530",
   "amount": 490
  }
 ],
 "created_at": "2024-05-12T09:36:29",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `N6F783`
```json
{
 "reservation_id": "N6F783",
 "user_id": "aarav_ahmed_6699",
 "origin": "IAH",
 "destination": "EWR",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "IAH",
   "destination": "EWR",
   "flight_number": "HAT195",
   "date": "2024-05-18",
   "price": 1268
  },
  {
   "origin": "EWR",
   "destination": "IAH",
   "flight_number": "HAT166",
   "date": "2024-05-21",
   "price": 867
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Ahmed",
   "dob": "1981-05-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9074831",
   "amount": 2135
  }
 ],
 "created_at": "2024-05-08T09:17:09",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `NQNU5R`
```json
{
 "reservation_id": "NQNU5R",
 "user_id": "aarav_ahmed_6699",
 "origin": "MCO",
 "destination": "SEA",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-13",
   "price": 1377
  },
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT045",
   "date": "2024-05-14",
   "price": 1712
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Ahmed",
   "dob": "1981-05-26"
  },
  {
   "first_name": "Aarav",
   "last_name": "Patel",
   "dob": "1980-12-03"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4959530",
   "amount": 6178
  }
 ],
 "created_at": "2024-05-13T05:37:57",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT010` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT010",
 "origin": "ATL",
 "destination": "MCO",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "20:30:00"
}
```
### flight `HAT045` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT045",
 "origin": "PHX",
 "destination": "SEA",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "02:00:00+1"
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
### flight `HAT195` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT195",
 "origin": "IAH",
 "destination": "EWR",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "17:00:00"
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
### flight `HAT258` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT258",
 "origin": "SEA",
 "destination": "SFO",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT268` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT268",
 "origin": "JFK",
 "destination": "ATL",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "09:30:00"
}
```
