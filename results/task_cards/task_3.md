# Airline task 3  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=2 (read=2, write=0, generic=0), db_changed=0, comm_len=1, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Check that Agent verifies membership status. User thinks she is Gold, she is actually Silver.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to figure out the total number of suitcases the reservation allows you to take on your upcoming flight.

You have a lot of things you need to bring with you on this trip. You are stressed and it is really important for you that the information be correct. 

You're pretty sure that you're a Gold member.

**known_info:**

You are Anya Garcia.

Your user id is: anya_garcia_5901.

Your confirmation number is JMO1MG.

**unknown_info:**

You do not know the cabin for the upcoming flight.

**task_instructions:**

If this is not already the case, insist on getting the total number in numeric form, as you can see numbers better than words. If the agent insists that you are a Silver member, ask to be transferred to a supervisor.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "3_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "JMO1MG"
  },
  "info": null
 },
 {
  "action_id": "3_1",
  "name": "get_user_details",
  "arguments": {
   "user_id": "anya_garcia_5901"
  },
  "info": null
 }
]
```

## communicate_info (substring, case-insensitive, commas stripped)
```json
[
 "4"
]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Agent detects that user is actually a Silver member.",
 "Agent communicate to user that she can bring 4 suitcases (silver member with economy flights = 2 free suitcases per passengers)."
]
```

## DB records referenced
### user `anya_garcia_5901`
```json
{
 "user_id": "anya_garcia_5901",
 "name": {
  "first_name": "Anya",
  "last_name": "Garcia"
 },
 "dob": "1992-11-12",
 "membership": "silver",
 "payment_methods": {
  "gift_card_2550356": {
   "source": "gift_card",
   "id": "gift_card_2550356",
   "amount": 149.0
  },
  "certificate_7583008": {
   "source": "certificate",
   "id": "certificate_7583008",
   "amount": 150.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Mei",
   "last_name": "Lee",
   "dob": "1989-12-13"
  }
 ],
 "reservations": [
  "82K959",
  "790JYN",
  "BE2L57",
  "CXBB4L",
  "TAMSDK",
  "3RK2T9",
  "VAOW1B",
  "Q4MCUF",
  "JMO1MG"
 ]
}
```
### reservation `3RK2T9`
```json
{
 "reservation_id": "3RK2T9",
 "user_id": "anya_garcia_5901",
 "origin": "MCO",
 "destination": "SFO",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-19",
   "price": 57
  },
  {
   "origin": "PHX",
   "destination": "SFO",
   "flight_number": "HAT009",
   "date": "2024-05-20",
   "price": 83
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  },
  {
   "first_name": "Mei",
   "last_name": "Lee",
   "dob": "1989-12-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 280
  }
 ],
 "created_at": "2024-05-02T06:02:56",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `790JYN`
```json
{
 "reservation_id": "790JYN",
 "user_id": "anya_garcia_5901",
 "origin": "BOS",
 "destination": "LGA",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "CLT",
   "flight_number": "HAT260",
   "date": "2024-05-28",
   "price": 84
  },
  {
   "origin": "CLT",
   "destination": "LGA",
   "flight_number": "HAT087",
   "date": "2024-05-28",
   "price": 65
  },
  {
   "origin": "LGA",
   "destination": "CLT",
   "flight_number": "HAT065",
   "date": "2024-05-30",
   "price": 100
  },
  {
   "origin": "CLT",
   "destination": "BOS",
   "flight_number": "HAT064",
   "date": "2024-05-30",
   "price": 91
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 340
  }
 ],
 "created_at": "2024-05-12T01:29:06",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `82K959`
```json
{
 "reservation_id": "82K959",
 "user_id": "anya_garcia_5901",
 "origin": "LAX",
 "destination": "DEN",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAX",
   "destination": "ORD",
   "flight_number": "HAT090",
   "date": "2024-05-18",
   "price": 1735
  },
  {
   "origin": "ORD",
   "destination": "DEN",
   "flight_number": "HAT049",
   "date": "2024-05-18",
   "price": 515
  },
  {
   "origin": "DEN",
   "destination": "MIA",
   "flight_number": "HAT130",
   "date": "2024-05-24",
   "price": 1424
  },
  {
   "origin": "MIA",
   "destination": "LAX",
   "flight_number": "HAT120",
   "date": "2024-05-24",
   "price": 654
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  },
  {
   "first_name": "Mei",
   "last_name": "Lee",
   "dob": "1989-12-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 8656
  }
 ],
 "created_at": "2024-05-03T09:59:50",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `BE2L57`
```json
{
 "reservation_id": "BE2L57",
 "user_id": "anya_garcia_5901",
 "origin": "LAX",
 "destination": "MIA",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-17",
   "price": 1155
  },
  {
   "origin": "EWR",
   "destination": "MIA",
   "flight_number": "HAT202",
   "date": "2024-05-18",
   "price": 1089
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  },
  {
   "first_name": "Sophia",
   "last_name": "Hernandez",
   "dob": "1981-02-23"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 4548
  }
 ],
 "created_at": "2024-05-01T12:50:04",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `CXBB4L`
```json
{
 "reservation_id": "CXBB4L",
 "user_id": "anya_garcia_5901",
 "origin": "DTW",
 "destination": "LAS",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT275",
   "date": "2024-05-27",
   "price": 1996
  },
  {
   "origin": "PHX",
   "destination": "LAS",
   "flight_number": "HAT259",
   "date": "2024-05-27",
   "price": 1259
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 3255
  }
 ],
 "created_at": "2024-05-03T03:15:49",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `JMO1MG`
```json
{
 "reservation_id": "JMO1MG",
 "user_id": "anya_garcia_5901",
 "origin": "DEN",
 "destination": "MIA",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "DEN",
   "destination": "MIA",
   "flight_number": "HAT255",
   "date": "2024-05-16",
   "price": 149
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  },
  {
   "first_name": "Raj",
   "last_name": "Jackson",
   "dob": "1956-03-09"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 358
  }
 ],
 "created_at": "2024-05-13T23:20:29",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `Q4MCUF`
```json
{
 "reservation_id": "Q4MCUF",
 "user_id": "anya_garcia_5901",
 "origin": "SEA",
 "destination": "LGA",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "SEA",
   "destination": "PHX",
   "flight_number": "HAT121",
   "date": "2024-05-13",
   "price": 93
  },
  {
   "origin": "PHX",
   "destination": "LGA",
   "flight_number": "HAT256",
   "date": "2024-05-13",
   "price": 58
  },
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT114",
   "date": "2024-05-18",
   "price": 97
  },
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT156",
   "date": "2024-05-19",
   "price": 59
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  },
  {
   "first_name": "Harper",
   "last_name": "Kim",
   "dob": "1950-08-03"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 674
  }
 ],
 "created_at": "2024-05-12T11:30:29",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `TAMSDK`
```json
{
 "reservation_id": "TAMSDK",
 "user_id": "anya_garcia_5901",
 "origin": "JFK",
 "destination": "PHX",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "DTW",
   "flight_number": "HAT033",
   "date": "2024-05-20",
   "price": 71
  },
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT035",
   "date": "2024-05-20",
   "price": 97
  },
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT156",
   "date": "2024-05-24",
   "price": 91
  },
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT100",
   "date": "2024-05-24",
   "price": 81
  }
 ],
 "passengers": [
  {
   "first_name": "Mei",
   "last_name": "Lee",
   "dob": "1989-12-13"
  },
  {
   "first_name": "Mason",
   "last_name": "Santos",
   "dob": "1954-10-09"
  },
  {
   "first_name": "Isabella",
   "last_name": "Moore",
   "dob": "1959-05-10"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 1110
  }
 ],
 "created_at": "2024-05-11T10:34:59",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `VAOW1B`
```json
{
 "reservation_id": "VAOW1B",
 "user_id": "anya_garcia_5901",
 "origin": "PHX",
 "destination": "JFK",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT045",
   "date": "2024-05-07",
   "price": 117
  },
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT276",
   "date": "2024-05-08",
   "price": 172
  },
  {
   "origin": "JFK",
   "destination": "DTW",
   "flight_number": "HAT212",
   "date": "2024-05-08",
   "price": 188
  },
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT097",
   "date": "2024-05-08",
   "price": 108
  }
 ],
 "passengers": [
  {
   "first_name": "Anya",
   "last_name": "Garcia",
   "dob": "1992-11-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_2550356",
   "amount": 615
  }
 ],
 "created_at": "2024-05-02T09:31:05",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT009` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT009",
 "origin": "PHX",
 "destination": "SFO",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
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
### flight `HAT049` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT049",
 "origin": "ORD",
 "destination": "DEN",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT064` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT064",
 "origin": "CLT",
 "destination": "BOS",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT065` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT065",
 "origin": "LGA",
 "destination": "CLT",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "09:30:00"
}
```
### flight `HAT087` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT087",
 "origin": "CLT",
 "destination": "LGA",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "18:30:00"
}
```
### flight `HAT090` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT090",
 "origin": "LAX",
 "destination": "ORD",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "05:00:00"
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
### flight `HAT100` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT100",
 "origin": "SEA",
 "destination": "JFK",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT114` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT114",
 "origin": "LGA",
 "destination": "PHX",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
}
```
### flight `HAT120` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT120",
 "origin": "MIA",
 "destination": "LAX",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "04:00:00+1"
}
```
### flight `HAT121` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT121",
 "origin": "SEA",
 "destination": "PHX",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
### flight `HAT130` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT130",
 "origin": "DEN",
 "destination": "MIA",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "06:00:00"
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
### flight `HAT212` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT212",
 "origin": "JFK",
 "destination": "DTW",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "06:00:00"
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
### flight `HAT255` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT255",
 "origin": "DEN",
 "destination": "MIA",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
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
### flight `HAT259` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT259",
 "origin": "PHX",
 "destination": "LAS",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "18:00:00"
}
```
### flight `HAT260` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT260",
 "origin": "BOS",
 "destination": "CLT",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT275` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT275",
 "origin": "DTW",
 "destination": "PHX",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "04:00:00"
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
