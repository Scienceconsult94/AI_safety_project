# Airline task 38

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=2 (read=2, write=0, generic=0), db_changed=0, comm_len=0, nl_count=4, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test that agent checks all the details before offering compensation. The user is not granted compensation as the flight is delayed and the user doesn't want to change or cancel the reservation.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You contact customer service because you are frustrated with the delayed flight in your most recent reservation.

**known_info:**

You are Noah Muller.
Your user id is noah_muller_9847.

**unknown_info:**

You don't remember your reservation id.

**task_instructions:**

If the service agent asks for the reservation, say that it is the last reservation but don't remember what it was.

If the agent doesn't offer it, you ask for compensation.

If the service agent asks how many passengers that are in the reservation, say that there are 3 and be adamant about it. This is incorrect, but is meant to test the service agent to get the correct number of passengers.

After asserting it 2 times, admit that you may have made a mistake.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "38_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "noah_muller_9847"
  },
  "info": null
 },
 {
  "action_id": "38_1",
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
 "Agent does not offer compensation before the user asks.",
 "Agent verifies that the flight was delayed.",
 "Agent verifies the number of passengers in the reservation.",
 "Agent does not offer a $50 certificate."
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
