# Airline task 32  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=5 (read=3, write=2, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test agent's capacity to handle a flight change.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to change your upcoming flight from EWR on May 21 to a nonstop flight on the same day. 

Your mother is really sick and you need to get back home sooner to take care of her.

**known_info:**

You are Ivan Rossi.
Your user id is ivan_rossi_8555.

**unknown_info:**

None

**task_instructions:**

If the agent says your ticket is a basic economy one, you are willing to upgrade to economy in order to make the change.

You are willing to pay up to $100 for the change.

You don't want to buy a new ticket.

First upgrade you to economy and confirm that change, then separately change the flights to nonstop. You want to see both steps completed individually so you can verify each change

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "32_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "ivan_rossi_8555"
  },
  "info": null
 },
 {
  "action_id": "32_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "OWZ4XL"
  },
  "info": null
 },
 {
  "action_id": "32_2",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "EWR",
   "destination": "LAX",
   "date": "2024-05-21"
  },
  "info": null
 },
 {
  "action_id": "32_3",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "OWZ4XL",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT202",
     "date": "2024-05-21"
    },
    {
     "flight_number": "HAT232",
     "date": "2024-05-21"
    }
   ],
   "payment_id": "credit_card_9659780"
  },
  "info": null
 },
 {
  "action_id": "32_4",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "OWZ4XL",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT041",
     "date": "2024-05-21"
    }
   ],
   "payment_id": "credit_card_9659780"
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
 "Agent update reservation OWZ4XL to economy.",
 "Agent updates reservation OWZ4XL to flight HAT041."
]
```

## DB records referenced
### user `ivan_rossi_8555`
```json
{
 "user_id": "ivan_rossi_8555",
 "name": {
  "first_name": "Ivan",
  "last_name": "Rossi"
 },
 "dob": "1954-01-14",
 "membership": "silver",
 "payment_methods": {
  "gift_card_7344518": {
   "source": "gift_card",
   "id": "gift_card_7344518",
   "amount": 183.0
  },
  "gift_card_9823297": {
   "source": "gift_card",
   "id": "gift_card_9823297",
   "amount": 224.0
  },
  "credit_card_9659780": {
   "source": "credit_card",
   "id": "credit_card_9659780",
   "brand": "visa",
   "last_four": "1777"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ava",
   "last_name": "Silva",
   "dob": "1971-01-14"
  },
  {
   "first_name": "Anya",
   "last_name": "Patel",
   "dob": "1990-06-13"
  }
 ],
 "reservations": [
  "OWZ4XL",
  "F3IQK1",
  "8WMF4C",
  "L2H5FP"
 ]
}
```
### reservation `8WMF4C`
```json
{
 "reservation_id": "8WMF4C",
 "user_id": "ivan_rossi_8555",
 "origin": "MIA",
 "destination": "PHX",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MIA",
   "destination": "LAS",
   "flight_number": "HAT062",
   "date": "2024-05-20",
   "price": 189
  },
  {
   "origin": "LAS",
   "destination": "PHX",
   "flight_number": "HAT284",
   "date": "2024-05-21",
   "price": 107
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Rossi",
   "dob": "1954-01-14"
  },
  {
   "first_name": "Ethan",
   "last_name": "Khan",
   "dob": "1971-03-23"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_9823297",
   "amount": 592
  }
 ],
 "created_at": "2024-05-07T04:31:20",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `F3IQK1`
```json
{
 "reservation_id": "F3IQK1",
 "user_id": "ivan_rossi_8555",
 "origin": "PHX",
 "destination": "MCO",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "PHX",
   "destination": "MCO",
   "flight_number": "HAT181",
   "date": "2024-05-10",
   "price": 77
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Rossi",
   "dob": "1954-01-14"
  },
  {
   "first_name": "Yara",
   "last_name": "Garcia",
   "dob": "1955-04-20"
  },
  {
   "first_name": "Anya",
   "last_name": "Patel",
   "dob": "1990-06-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_9823297",
   "amount": 231
  }
 ],
 "created_at": "2024-05-09T22:06:00",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `L2H5FP`
```json
{
 "reservation_id": "L2H5FP",
 "user_id": "ivan_rossi_8555",
 "origin": "CLT",
 "destination": "DFW",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT108",
   "date": "2024-05-03",
   "price": 156
  },
  {
   "origin": "EWR",
   "destination": "DFW",
   "flight_number": "HAT213",
   "date": "2024-05-03",
   "price": 117
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Rossi",
   "dob": "1954-01-14"
  },
  {
   "first_name": "Harper",
   "last_name": "Muller",
   "dob": "1954-09-15"
  },
  {
   "first_name": "Mason",
   "last_name": "Silva",
   "dob": "1952-10-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7344518",
   "amount": 909
  }
 ],
 "created_at": "2024-05-02T03:20:50",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `OWZ4XL`
```json
{
 "reservation_id": "OWZ4XL",
 "user_id": "ivan_rossi_8555",
 "origin": "EWR",
 "destination": "LAX",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "EWR",
   "destination": "MIA",
   "flight_number": "HAT202",
   "date": "2024-05-21",
   "price": 94
  },
  {
   "origin": "MIA",
   "destination": "LAX",
   "flight_number": "HAT232",
   "date": "2024-05-21",
   "price": 80
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Rossi",
   "dob": "1954-01-14"
  },
  {
   "first_name": "Olivia",
   "last_name": "Santos",
   "dob": "1984-06-23"
  },
  {
   "first_name": "Lei",
   "last_name": "Johansson",
   "dob": "1995-10-22"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_9823297",
   "amount": 522
  }
 ],
 "created_at": "2024-05-09T13:43:03",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
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
### flight `HAT062` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT062",
 "origin": "MIA",
 "destination": "LAS",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "02:30:00+1"
}
```
### flight `HAT108` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT108",
 "origin": "CLT",
 "destination": "EWR",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "05:00:00"
}
```
### flight `HAT181` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT181",
 "origin": "PHX",
 "destination": "MCO",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "03:30:00+1"
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
### flight `HAT213` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT213",
 "origin": "EWR",
 "destination": "DFW",
 "scheduled_departure_time_est": "12:00:00",
 "scheduled_arrival_time_est": "15:30:00"
}
```
### flight `HAT232` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT232",
 "origin": "MIA",
 "destination": "LAX",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "18:00:00"
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
