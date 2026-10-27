# Airline task 25

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test agent capacity to handle a flight booking plus specifications about how to process payment.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to make a reservation for your friend. It should be exactly the same as your current reservation.

**known_info:**

You are Ivan Muller.

Your user id is ivan_muller_7015.

Your friends name is Ivan Smith.

He is listed in your user profile.

**unknown_info:**

You can't remember Ivan Smith's DOB but it is in your profile.

**task_instructions:**

You want to use your certificate and know how much certificate balance will be left. You will ONLY accept a new booking with just him as the passenger. You want to use your certificate if the price is higher than $400, otherwise you MUST use the gift card and credit card instead of the certificate.

No baggage and insurance.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "25_0",
  "name": "book_reservation",
  "arguments": {
   "user_id": "ivan_muller_7015",
   "origin": "DTW",
   "destination": "SEA",
   "flight_type": "one_way",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT097",
     "date": "2024-05-17"
    },
    {
     "flight_number": "HAT251",
     "date": "2024-05-17"
    }
   ],
   "passengers": [
    {
     "first_name": "Ivan",
     "last_name": "Smith",
     "dob": "1986-03-14"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "gift_card_8516878",
     "amount": 128
    },
    {
     "payment_id": "credit_card_3563913",
     "amount": 247
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
 "Agent books one way economy flight from DTW to SEA on 2024-05-17 with flights HAT097 and HAT251 for passenger Ivan Smith, no baggage, no insurance.",
 "Agent charges $128 to gift_card_8516878 and $247 to credit_card_3563913."
]
```

## DB records referenced
### user `ivan_muller_7015`
```json
{
 "user_id": "ivan_muller_7015",
 "name": {
  "first_name": "Ivan",
  "last_name": "Muller"
 },
 "dob": "1968-04-25",
 "membership": "gold",
 "payment_methods": {
  "certificate_8998287": {
   "source": "certificate",
   "id": "certificate_8998287",
   "amount": 500.0
  },
  "credit_card_3563913": {
   "source": "credit_card",
   "id": "credit_card_3563913",
   "brand": "mastercard",
   "last_four": "6710"
  },
  "gift_card_8516878": {
   "source": "gift_card",
   "id": "gift_card_8516878",
   "amount": 128.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Smith",
   "dob": "1986-03-14"
  },
  {
   "first_name": "Lucas",
   "last_name": "Davis",
   "dob": "1988-10-12"
  }
 ],
 "reservations": [
  "G72NSF"
 ]
}
```
### reservation `G72NSF`
```json
{
 "reservation_id": "G72NSF",
 "user_id": "ivan_muller_7015",
 "origin": "DTW",
 "destination": "SEA",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT097",
   "date": "2024-05-17",
   "price": 158
  },
  {
   "origin": "PHX",
   "destination": "SEA",
   "flight_number": "HAT251",
   "date": "2024-05-17",
   "price": 141
  }
 ],
 "passengers": [
  {
   "first_name": "Ivan",
   "last_name": "Muller",
   "dob": "1968-04-25"
  },
  {
   "first_name": "Isabella",
   "last_name": "Moore",
   "dob": "1952-01-28"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_8516878",
   "amount": 658
  }
 ],
 "created_at": "2024-05-11T19:32:36",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
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
### flight `HAT251` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT251",
 "origin": "PHX",
 "destination": "SEA",
 "scheduled_departure_time_est": "12:00:00",
 "scheduled_arrival_time_est": "15:00:00"
}
```
