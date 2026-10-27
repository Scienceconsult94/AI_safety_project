# Airline task 18

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=5 (read=0, write=5, generic=0), db_changed=1, comm_len=1, nl_count=6, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Checking that agent can properly downgrade the right flights and calculate total savings.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You just faced some money issue and want to downgrade all business flights to economy, without changing the flights or passengers.

**known_info:**

Your name is Omar Davis.

Your user id is omar_davis_3817.

**unknown_info:**

You don't remember the payment method you used.

**task_instructions:**

You are fine with refunding to original payment for each reservation.

You want to know how much money you have saved in total, but you are fine having that information after the refunds are processed.

You are emotional and a bit angry, but you are willing to cooperate with the agent.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "18_0",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "JG7FMM",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT028",
     "date": "2024-05-21"
    },
    {
     "flight_number": "HAT277",
     "date": "2024-05-21"
    }
   ],
   "payment_id": "credit_card_2929732"
  },
  "info": null
 },
 {
  "action_id": "18_1",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "2FBBAH",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT080",
     "date": "2024-05-28"
    },
    {
     "flight_number": "HAT076",
     "date": "2024-05-28"
    },
    {
     "flight_number": "HAT255",
     "date": "2024-05-30"
    },
    {
     "flight_number": "HAT148",
     "date": "2024-05-30"
    }
   ],
   "payment_id": "gift_card_3481935"
  },
  "info": null
 },
 {
  "action_id": "18_2",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "X7BYG1",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT232",
     "date": "2024-05-24"
    },
    {
     "flight_number": "HAT228",
     "date": "2024-05-24"
    }
   ],
   "payment_id": "credit_card_2929732"
  },
  "info": null
 },
 {
  "action_id": "18_3",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "EQ1G6C",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT084",
     "date": "2024-05-23"
    },
    {
     "flight_number": "HAT175",
     "date": "2024-05-23"
    }
   ],
   "payment_id": "gift_card_6847880"
  },
  "info": null
 },
 {
  "action_id": "18_4",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "BOH180",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT276",
     "date": "2024-05-21"
    },
    {
     "flight_number": "HAT279",
     "date": "2024-05-22"
    }
   ],
   "payment_id": "credit_card_9525117"
  },
  "info": null
 }
]
```

## communicate_info (substring, case-insensitive, commas stripped)
```json
[
 "23553"
]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Reservation JG7FMM is updated to economy.",
 "Reservation 2FBBAH is updated to economy.",
 "Reservation X7BYG1 is updated to economy. ",
 "Reservation BOH180 is updated to economy. ",
 "Reservation EQ1G6C is updated to economy.",
 "Agent communicates that user will save $23553 in total."
]
```

## DB records referenced
### user `omar_davis_3817`
```json
{
 "user_id": "omar_davis_3817",
 "name": {
  "first_name": "Omar",
  "last_name": "Davis"
 },
 "dob": "1982-10-19",
 "membership": "regular",
 "payment_methods": {
  "gift_card_3481935": {
   "source": "gift_card",
   "id": "gift_card_3481935",
   "amount": 22.0
  },
  "credit_card_2929732": {
   "source": "credit_card",
   "id": "credit_card_2929732",
   "brand": "visa",
   "last_four": "7803"
  },
  "credit_card_9525117": {
   "source": "credit_card",
   "id": "credit_card_9525117",
   "brand": "visa",
   "last_four": "2172"
  },
  "gift_card_6847880": {
   "source": "gift_card",
   "id": "gift_card_6847880",
   "amount": 31.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Juan",
   "last_name": "Ahmed",
   "dob": "1992-11-19"
  },
  {
   "first_name": "Anya",
   "last_name": "Thomas",
   "dob": "1990-10-11"
  }
 ],
 "reservations": [
  "JG7FMM",
  "LQ940Q",
  "2FBBAH",
  "X7BYG1",
  "EQ1G6C",
  "BOH180"
 ]
}
```
### reservation `2FBBAH`
```json
{
 "reservation_id": "2FBBAH",
 "user_id": "omar_davis_3817",
 "origin": "DEN",
 "destination": "DEN",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "DEN",
   "destination": "PHL",
   "flight_number": "HAT080",
   "date": "2024-05-28",
   "price": 537
  },
  {
   "origin": "PHL",
   "destination": "DEN",
   "flight_number": "HAT076",
   "date": "2024-05-28",
   "price": 996
  },
  {
   "origin": "DEN",
   "destination": "MIA",
   "flight_number": "HAT255",
   "date": "2024-05-30",
   "price": 1440
  },
  {
   "origin": "MIA",
   "destination": "DEN",
   "flight_number": "HAT148",
   "date": "2024-05-30",
   "price": 1417
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_3481935",
   "amount": 4420
  }
 ],
 "created_at": "2024-05-14T10:44:24",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `BOH180`
```json
{
 "reservation_id": "BOH180",
 "user_id": "omar_davis_3817",
 "origin": "SEA",
 "destination": "IAH",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT276",
   "date": "2024-05-21",
   "price": 1981
  },
  {
   "origin": "JFK",
   "destination": "IAH",
   "flight_number": "HAT279",
   "date": "2024-05-22",
   "price": 820
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  },
  {
   "first_name": "Anya",
   "last_name": "Thomas",
   "dob": "1990-10-11"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_9525117",
   "amount": 5662
  }
 ],
 "created_at": "2024-05-06T19:53:46",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `EQ1G6C`
```json
{
 "reservation_id": "EQ1G6C",
 "user_id": "omar_davis_3817",
 "origin": "DEN",
 "destination": "IAH",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "DEN",
   "destination": "LAS",
   "flight_number": "HAT084",
   "date": "2024-05-23",
   "price": 1820
  },
  {
   "origin": "LAS",
   "destination": "IAH",
   "flight_number": "HAT175",
   "date": "2024-05-23",
   "price": 940
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6847880",
   "amount": 2790
  }
 ],
 "created_at": "2024-05-01T08:38:39",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `JG7FMM`
```json
{
 "reservation_id": "JG7FMM",
 "user_id": "omar_davis_3817",
 "origin": "MCO",
 "destination": "CLT",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "BOS",
   "flight_number": "HAT028",
   "date": "2024-05-21",
   "price": 1859
  },
  {
   "origin": "BOS",
   "destination": "CLT",
   "flight_number": "HAT277",
   "date": "2024-05-21",
   "price": 1679
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  },
  {
   "first_name": "Fatima",
   "last_name": "Patel",
   "dob": "1950-05-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_2929732",
   "amount": 7136
  }
 ],
 "created_at": "2024-05-11T08:28:51",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `LQ940Q`
```json
{
 "reservation_id": "LQ940Q",
 "user_id": "omar_davis_3817",
 "origin": "SFO",
 "destination": "MCO",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "SFO",
   "destination": "BOS",
   "flight_number": "HAT294",
   "date": "2024-05-16",
   "price": 133
  },
  {
   "origin": "BOS",
   "destination": "MCO",
   "flight_number": "HAT013",
   "date": "2024-05-16",
   "price": 166
  },
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT161",
   "date": "2024-05-19",
   "price": 103
  },
  {
   "origin": "PHX",
   "destination": "SFO",
   "flight_number": "HAT009",
   "date": "2024-05-19",
   "price": 101
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6847880",
   "amount": 533
  }
 ],
 "created_at": "2024-05-11T01:11:41",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `X7BYG1`
```json
{
 "reservation_id": "X7BYG1",
 "user_id": "omar_davis_3817",
 "origin": "MIA",
 "destination": "EWR",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MIA",
   "destination": "LAX",
   "flight_number": "HAT232",
   "date": "2024-05-24",
   "price": 1505
  },
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-24",
   "price": 1519
  }
 ],
 "passengers": [
  {
   "first_name": "Omar",
   "last_name": "Davis",
   "dob": "1982-10-19"
  },
  {
   "first_name": "Juan",
   "last_name": "Ahmed",
   "dob": "1992-11-19"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_2929732",
   "amount": 6108
  }
 ],
 "created_at": "2024-05-12T05:51:40",
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
### flight `HAT013` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT013",
 "origin": "BOS",
 "destination": "MCO",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "22:30:00"
}
```
### flight `HAT028` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT028",
 "origin": "MCO",
 "destination": "BOS",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "08:30:00"
}
```
### flight `HAT076` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT076",
 "origin": "PHL",
 "destination": "DEN",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "16:30:00"
}
```
### flight `HAT080` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT080",
 "origin": "DEN",
 "destination": "PHL",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "10:30:00"
}
```
### flight `HAT084` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT084",
 "origin": "DEN",
 "destination": "LAS",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "06:00:00"
}
```
### flight `HAT148` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT148",
 "origin": "MIA",
 "destination": "DEN",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "02:00:00+1"
}
```
### flight `HAT161` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT161",
 "origin": "MCO",
 "destination": "PHX",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "15:30:00"
}
```
### flight `HAT175` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT175",
 "origin": "LAS",
 "destination": "IAH",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "20:00:00"
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
### flight `HAT277` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT277",
 "origin": "BOS",
 "destination": "CLT",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "21:00:00"
}
```
### flight `HAT279` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT279",
 "origin": "JFK",
 "destination": "IAH",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "14:30:00"
}
```
### flight `HAT294` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT294",
 "origin": "SFO",
 "destination": "BOS",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
