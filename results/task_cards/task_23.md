# Airline task 23  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=4 (read=0, write=4, generic=0), db_changed=1, comm_len=3, nl_count=8, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Complex transaction testing understanding of one-certificate-per-reservation policy. Multiple bookings must be made to use three certificates while minimizing charges to a Mastercard.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to know the sum of gift card balances and the sum of certificate balances.

Additionally, you want to change your recent reservation to the cheapest business round trip without changing the dates.

**known_info:**

You are Mohamed Silva. Your user id is mohamed_silva_9265.

**unknown_info:**

None

**task_instructions:**

For your reservation, you don't care about direct flight or stop over. 

If the agent tells you basic economy cannot be changed (do not mention it if the agent does not mention it), you want the agent to cancel the current one and book a new one.

For payment, you want to use the certificates as much as possible, then gift cards as much as possible, and cover the rest with your master card.

But you want to know how much your master card will be charged.

You do not need baggage or insurance.

You want to minimize master card payment, so if cancelling and booking a new one costs less for the master card you will do it.

If the agent wants to confirm the new reservation but due to policy only one certificate can be used, you will come up with a great idea to use all three certificates by booking three separate reservations.

You will then use the 500 dollar certificate and all gift cards for you, certificate_9984806 for Raj, and the other certificate for Liam, and pay the rest with your master card. 

At the end of the day you want to know how much your master card will be charged. 

You are calm.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "23_0",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "K1NW8N"
  },
  "info": null
 },
 {
  "action_id": "23_1",
  "name": "book_reservation",
  "arguments": {
   "user_id": "mohamed_silva_9265",
   "origin": "JFK",
   "destination": "SFO",
   "flight_type": "round_trip",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT023",
     "date": "2024-05-26"
    },
    {
     "flight_number": "HAT204",
     "date": "2024-05-28"
    },
    {
     "flight_number": "HAT100",
     "date": "2024-05-28"
    }
   ],
   "passengers": [
    {
     "first_name": "Mohamed",
     "last_name": "Silva",
     "dob": "1960-11-26"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "certificate_3765853",
     "amount": 500
    },
    {
     "payment_id": "gift_card_8020792",
     "amount": 198
    },
    {
     "payment_id": "gift_card_6136092",
     "amount": 129
    },
    {
     "payment_id": "credit_card_2198526",
     "amount": 44
    }
   ],
   "total_baggages": 0,
   "nonfree_baggages": 0,
   "insurance": "no"
  },
  "info": null
 },
 {
  "action_id": "23_2",
  "name": "book_reservation",
  "arguments": {
   "user_id": "mohamed_silva_9265",
   "origin": "JFK",
   "destination": "SFO",
   "flight_type": "round_trip",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT023",
     "date": "2024-05-26"
    },
    {
     "flight_number": "HAT204",
     "date": "2024-05-28"
    },
    {
     "flight_number": "HAT100",
     "date": "2024-05-28"
    }
   ],
   "passengers": [
    {
     "first_name": "Raj",
     "last_name": "Sanchez",
     "dob": "1986-09-12"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "certificate_9984806",
     "amount": 250
    },
    {
     "payment_id": "credit_card_2198526",
     "amount": 621
    }
   ],
   "total_baggages": 0,
   "nonfree_baggages": 0,
   "insurance": "no"
  },
  "info": null
 },
 {
  "action_id": "23_3",
  "name": "book_reservation",
  "arguments": {
   "user_id": "mohamed_silva_9265",
   "origin": "JFK",
   "destination": "SFO",
   "flight_type": "round_trip",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT023",
     "date": "2024-05-26"
    },
    {
     "flight_number": "HAT204",
     "date": "2024-05-28"
    },
    {
     "flight_number": "HAT100",
     "date": "2024-05-28"
    }
   ],
   "passengers": [
    {
     "first_name": "Liam",
     "last_name": "Wilson",
     "dob": "1980-03-27"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "certificate_2765295",
     "amount": 250
    },
    {
     "payment_id": "credit_card_2198526",
     "amount": 621
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
[
 "327",
 "1000",
 "1286"
]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Agent mentions that total sum on gift cards is $327.",
 "Agent mentions that total sum on certificates is $1000.",
 "Agent cancels reservation K1NW8N.",
 "Agent books a round-trip reservation from JFK to SFO in business with outbound flights HAT023 and HAT204 on 2024-05-26 and return flight HAT100 on 2024-05-28 for Mohamed Silva.",
 "For this reservation Agent charges $500 on certificate_3765853, $198 on gift_card_8020792, $129 on gift_card_6136092\", and $44 on credit_card_2198526.",
 "Agent books a similar reservation for Raj Sanchez with $250 payment on certificate_9984806 and $621 payment on credit_card_2198526.",
 "Agent books a similar reservation for Liam Wilson with $250 on certificate_2765295 and $621 on credit_card_2198526.",
 "Agent communicates that Mastercard will be charged $1286."
]
```

## DB records referenced
### user `mohamed_silva_9265`
```json
{
 "user_id": "mohamed_silva_9265",
 "name": {
  "first_name": "Mohamed",
  "last_name": "Silva"
 },
 "dob": "1960-11-26",
 "membership": "regular",
 "payment_methods": {
  "credit_card_5843230": {
   "source": "credit_card",
   "id": "credit_card_5843230",
   "brand": "visa",
   "last_four": "2395"
  },
  "gift_card_8020792": {
   "source": "gift_card",
   "id": "gift_card_8020792",
   "amount": 198.0
  },
  "certificate_3765853": {
   "source": "certificate",
   "id": "certificate_3765853",
   "amount": 500.0
  },
  "gift_card_6136092": {
   "source": "gift_card",
   "id": "gift_card_6136092",
   "amount": 129.0
  },
  "certificate_9984806": {
   "source": "certificate",
   "id": "certificate_9984806",
   "amount": 250.0
  },
  "credit_card_2198526": {
   "source": "credit_card",
   "id": "credit_card_2198526",
   "brand": "mastercard",
   "last_four": "9363"
  },
  "certificate_2765295": {
   "source": "certificate",
   "id": "certificate_2765295",
   "amount": 250.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1986-09-12"
  },
  {
   "first_name": "Liam",
   "last_name": "Wilson",
   "dob": "1980-03-27"
  }
 ],
 "reservations": [
  "K1NW8N"
 ]
}
```
### reservation `K1NW8N`
```json
{
 "reservation_id": "K1NW8N",
 "user_id": "mohamed_silva_9265",
 "origin": "JFK",
 "destination": "SFO",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "SFO",
   "flight_number": "HAT023",
   "date": "2024-05-26",
   "price": 53
  },
  {
   "origin": "SFO",
   "destination": "SEA",
   "flight_number": "HAT204",
   "date": "2024-05-28",
   "price": 71
  },
  {
   "origin": "SEA",
   "destination": "JFK",
   "flight_number": "HAT021",
   "date": "2024-05-28",
   "price": 65
  }
 ],
 "passengers": [
  {
   "first_name": "Mohamed",
   "last_name": "Silva",
   "dob": "1960-11-26"
  },
  {
   "first_name": "Raj",
   "last_name": "Sanchez",
   "dob": "1986-09-12"
  },
  {
   "first_name": "Liam",
   "last_name": "Wilson",
   "dob": "1980-03-27"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6136092",
   "amount": 567
  }
 ],
 "created_at": "2024-05-14T16:03:16",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT021` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT021",
 "origin": "SEA",
 "destination": "JFK",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT023` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT023",
 "origin": "JFK",
 "destination": "SFO",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "20:00:00"
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
### flight `HAT204` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT204",
 "origin": "SFO",
 "destination": "SEA",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "10:00:00"
}
```
