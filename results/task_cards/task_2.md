# Airline task 2

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=3 (read=3, write=0, generic=0), db_changed=0, comm_len=0, nl_count=4, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Testing capacity of agent to handle change of topic + capacity to double check claims made by client.\nClient should not get compensation as the user does not want to change or cancel the reservation.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

First, try to book a flight from sf to ny. 

You will have 3 passengers.

Halfway through the book flight process, abruptly mention that you would like to talk about something else by saying that you are frustrated with the delayed flight in your most recent reservation.

**known_info:**

You are Noah Muller.
Your user id is noah_muller_9847.

**unknown_info:**

None

**task_instructions:**

If the service agent asks for the reservation number of the delayed flight, say that it is the last reservation you made but don't remember what it was.

If the service agent asks how many passenger were in that reservation, say that there are 3. 

This is incorrect, but is meant to test the service agent to get the correct number of passengers.

You are willing to admit that you are wrong if the agent corrects you.

Don't ask for compensation right away. First complain. Try to get the agent to be the one offering the compensation. If the agent doesn't after a few exchanges, ask explicitly.

If the agent asks if you want to continue with your initial reservation of a sf to ny flight, say that you will call back later.

You will never change or cancel the reservation.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "2_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "noah_muller_9847"
  },
  "info": null
 },
 {
  "action_id": "2_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "SDZQKO"
  },
  "info": null
 },
 {
  "action_id": "2_2",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "4OG6T3"
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
 "Agent should not offer compensation unless the user asks for it.",
 "Agent should check that the flight was indeed delayed.",
 "Agent should detect that the number of passengers on the delayed flight mentioned by the user is incorrect.",
 "Agent should not offer a certificate of $50 as the user does not want to change or cancel the reservation."
]
```

## DB records referenced
### user `noah_muller_9847`
```json
{
 "user_id": "noah_muller_9847",
 "name": {
  "first_name": "Noah",
  "last_name": "Muller"
 },
 "dob": "1963-01-22",
 "membership": "gold",
 "payment_methods": {
  "credit_card_1245537": {
   "source": "credit_card",
   "id": "credit_card_1245537",
   "brand": "mastercard",
   "last_four": "1167"
  },
  "credit_card_6040264": {
   "source": "credit_card",
   "id": "credit_card_6040264",
   "brand": "visa",
   "last_four": "2076"
  },
  "credit_card_3255100": {
   "source": "credit_card",
   "id": "credit_card_3255100",
   "brand": "visa",
   "last_four": "2604"
  },
  "certificate_8301303": {
   "source": "certificate",
   "id": "certificate_8301303",
   "amount": 100.0
  },
  "credit_card_3983998": {
   "source": "credit_card",
   "id": "credit_card_3983998",
   "brand": "visa",
   "last_four": "8413"
  },
  "credit_card_7574394": {
   "source": "credit_card",
   "id": "credit_card_7574394",
   "brand": "visa",
   "last_four": "1798"
  },
  "credit_card_6873705": {
   "source": "credit_card",
   "id": "credit_card_6873705",
   "brand": "visa",
   "last_four": "2267"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Lei",
   "last_name": "Patel",
   "dob": "1959-11-15"
  }
 ],
 "reservations": [
  "SDZQKO",
  "4OG6T3"
 ]
}
```
### reservation `4OG6T3`
```json
{
 "reservation_id": "4OG6T3",
 "user_id": "noah_muller_9847",
 "origin": "BOS",
 "destination": "LAS",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "SEA",
   "flight_number": "HAT006",
   "date": "2024-05-11",
   "price": 87
  },
  {
   "origin": "SEA",
   "destination": "LAS",
   "flight_number": "HAT018",
   "date": "2024-05-11",
   "price": 96
  },
  {
   "origin": "LAS",
   "destination": "SEA",
   "flight_number": "HAT040",
   "date": "2024-05-17",
   "price": 63
  },
  {
   "origin": "SEA",
   "destination": "BOS",
   "flight_number": "HAT253",
   "date": "2024-05-17",
   "price": 52
  }
 ],
 "passengers": [
  {
   "first_name": "Noah",
   "last_name": "Muller",
   "dob": "1963-01-22"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_7574394",
   "amount": 328
  }
 ],
 "created_at": "2024-05-09T15:14:07",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `SDZQKO`
```json
{
 "reservation_id": "SDZQKO",
 "user_id": "noah_muller_9847",
 "origin": "LAX",
 "destination": "MIA",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-27",
   "price": 76
  },
  {
   "origin": "EWR",
   "destination": "MIA",
   "flight_number": "HAT202",
   "date": "2024-05-28",
   "price": 54
  },
  {
   "origin": "MIA",
   "destination": "EWR",
   "flight_number": "HAT192",
   "date": "2024-05-28",
   "price": 67
  },
  {
   "origin": "EWR",
   "destination": "LAX",
   "flight_number": "HAT041",
   "date": "2024-05-29",
   "price": 58
  }
 ],
 "passengers": [
  {
   "first_name": "Noah",
   "last_name": "Muller",
   "dob": "1963-01-22"
  },
  {
   "first_name": "Lucas",
   "last_name": "Anderson",
   "dob": "1971-04-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_3983998",
   "amount": 510
  }
 ],
 "created_at": "2024-05-13T03:26:54",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT006` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT006",
 "origin": "BOS",
 "destination": "SEA",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "08:30:00"
}
```
### flight `HAT018` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT018",
 "origin": "SEA",
 "destination": "LAS",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "18:30:00"
}
```
### flight `HAT040` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT040",
 "origin": "LAS",
 "destination": "SEA",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "02:30:00"
}
```
### flight `HAT041` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT041",
 "origin": "EWR",
 "destination": "LAX",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "12:30:00"
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
### flight `HAT228` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT228",
 "origin": "LAX",
 "destination": "EWR",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
}
```
### flight `HAT253` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT253",
 "origin": "SEA",
 "destination": "BOS",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
}
```
