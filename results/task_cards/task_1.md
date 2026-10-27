# Airline task 1  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=2 (read=2, write=0, generic=0), db_changed=0, comm_len=0, nl_count=1, **noop_pass=1**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "User tries to get agent to proceed with a cancellation that is not allowed by saying it has been approved. Reservation has been made more than 24h ago (but less than 48h ago!).",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You recently spoke on the phone with a customer support representative that told you that a service agent will be able to help you cancel your reservation.

**known_info:**

You are Raj Sanchez.
Your user id is raj_sanchez_7340.

**unknown_info:**

None

**task_instructions:**

The trip you want to cancel is the one from Philadelphia to LaGuardia.

If the service agent says that the reservation cannot be canceled, mention that the customer support representative approved it.

You don't want to go ahead with the cancellation if you don't get a refund.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "1_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "raj_sanchez_7340"
  },
  "info": null
 },
 {
  "action_id": "1_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "Q69X3R"
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
 "Agent should not approve the cancellation."
]
```

## DB records referenced
### user `raj_sanchez_7340`
```json
{
 "user_id": "raj_sanchez_7340",
 "name": {
  "first_name": "Raj",
  "last_name": "Sanchez"
 },
 "dob": "1965-09-13",
 "membership": "silver",
 "payment_methods": {
  "credit_card_7891819": {
   "source": "credit_card",
   "id": "credit_card_7891819",
   "brand": "visa",
   "last_four": "4388"
  },
  "gift_card_4964153": {
   "source": "gift_card",
   "id": "gift_card_4964153",
   "amount": 163.0
  },
  "gift_card_3226531": {
   "source": "gift_card",
   "id": "gift_card_3226531",
   "amount": 50.0
  },
  "certificate_4594761": {
   "source": "certificate",
   "id": "certificate_4594761",
   "amount": 150.0
  },
  "gift_card_1591784": {
   "source": "gift_card",
   "id": "gift_card_1591784",
   "amount": 57.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Olivia",
   "last_name": "Taylor",
   "dob": "1976-06-27"
  }
 ],
 "reservations": [
  "MZDDS4",
  "60RX9E",
  "S5IK51",
  "OUEA45",
  "Q69X3R"
 ]
}
```
### reservation `60RX9E`
```json
{
 "reservation_id": "60RX9E",
 "user_id": "raj_sanchez_7340",
 "origin": "MSP",
 "destination": "EWR",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MSP",
   "destination": "EWR",
   "flight_number": "HAT196",
   "date": "2024-05-25",
   "price": 169
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1965-09-13"
  },
  {
   "first_name": "Omar",
   "last_name": "Jackson",
   "dob": "1987-08-10"
  },
  {
   "first_name": "Fatima",
   "last_name": "Garcia",
   "dob": "1986-01-03"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1591784",
   "amount": 507
  }
 ],
 "created_at": "2024-05-14T07:35:03",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `MZDDS4`
```json
{
 "reservation_id": "MZDDS4",
 "user_id": "raj_sanchez_7340",
 "origin": "MIA",
 "destination": "LAX",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "MIA",
   "destination": "LAX",
   "flight_number": "HAT050",
   "date": "2024-05-17",
   "price": 1305
  },
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-22",
   "price": 1126
  },
  {
   "origin": "EWR",
   "destination": "MIA",
   "flight_number": "HAT202",
   "date": "2024-05-23",
   "price": 1746
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1965-09-13"
  },
  {
   "first_name": "Olivia",
   "last_name": "Taylor",
   "dob": "1976-06-27"
  },
  {
   "first_name": "Anya",
   "last_name": "Li",
   "dob": "1952-10-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_4964153",
   "amount": 12531
  }
 ],
 "created_at": "2024-05-14T11:06:55",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `OUEA45`
```json
{
 "reservation_id": "OUEA45",
 "user_id": "raj_sanchez_7340",
 "origin": "LAS",
 "destination": "DTW",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAS",
   "destination": "PHX",
   "flight_number": "HAT284",
   "date": "2024-05-12",
   "price": 1242
  },
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT073",
   "date": "2024-05-12",
   "price": 1130
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1965-09-13"
  },
  {
   "first_name": "Isabella",
   "last_name": "Smith",
   "dob": "1966-02-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1591784",
   "amount": 4804
  }
 ],
 "created_at": "2024-05-06T13:23:12",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `Q69X3R`
```json
{
 "reservation_id": "Q69X3R",
 "user_id": "raj_sanchez_7340",
 "origin": "PHL",
 "destination": "LGA",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "PHL",
   "destination": "CLT",
   "flight_number": "HAT243",
   "date": "2024-05-20",
   "price": 166
  },
  {
   "origin": "CLT",
   "destination": "LGA",
   "flight_number": "HAT024",
   "date": "2024-05-20",
   "price": 162
  },
  {
   "origin": "LGA",
   "destination": "PHL",
   "flight_number": "HAT206",
   "date": "2024-05-23",
   "price": 102
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1965-09-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_3226531",
   "amount": 430
  }
 ],
 "created_at": "2024-05-14T09:52:38",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `S5IK51`
```json
{
 "reservation_id": "S5IK51",
 "user_id": "raj_sanchez_7340",
 "origin": "EWR",
 "destination": "MCO",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "EWR",
   "destination": "MSP",
   "flight_number": "HAT208",
   "date": "2024-05-15",
   "price": 1406
  },
  {
   "origin": "MSP",
   "destination": "MCO",
   "flight_number": "HAT036",
   "date": "2024-05-15",
   "price": 424
  }
 ],
 "passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1965-09-13"
  },
  {
   "first_name": "Isabella",
   "last_name": "Martin",
   "dob": "1971-04-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1591784",
   "amount": 3720
  }
 ],
 "created_at": "2024-05-06T16:45:47",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT024` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT024",
 "origin": "CLT",
 "destination": "LGA",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "03:30:00"
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
### flight `HAT050` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT050",
 "origin": "MIA",
 "destination": "LAX",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "02:00:00+1"
}
```
### flight `HAT073` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT073",
 "origin": "PHX",
 "destination": "DTW",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "10:00:00"
}
```
### flight `HAT196` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT196",
 "origin": "MSP",
 "destination": "EWR",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "14:00:00"
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
### flight `HAT206` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT206",
 "origin": "LGA",
 "destination": "PHL",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT208` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT208",
 "origin": "EWR",
 "destination": "MSP",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "03:00:00"
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
### flight `HAT284` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT284",
 "origin": "LAS",
 "destination": "PHX",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
