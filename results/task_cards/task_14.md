# Airline task 14

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=2 (read=0, write=2, generic=0), db_changed=1, comm_len=3, nl_count=5, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test the capacity of the agent to look for the cheapest flights with constraints on dates, cities and cabin. \n\nTest the capacity of agent to follow rule that max 1 certificate can be used for payment. \n\n\nTest capacity of agents to reason about money amounts.\n\nThe user has multiple certificates, gift cards and 2 credit cards one file. for the payment, we expect agent to understand how to maximize use of gift card + 1 certificate to minimize amount put on the credit card.\n\nThe total cost of the new flight will be $2613. The correct split is to use first both gift cards for $327, the $500 certificate, and put the remaining $1786 dollars on the master card.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to know how much you have on your gift cards and certificates. Then you want to change your upcoming reservation.

**known_info:**

Your name is Mohamed Silva.

Your user id is mohamed_silva_9265.

**unknown_info:**

None

**task_instructions:**

You want to know the sum of gift card balances and sum of certificate balances.

If the agent gives you individual balances, you want the sums.

Then you want to change your recent reservation. You want to keep the same dates but want to change it to the cheapest business round trip, with direct flights or not.

If the agent tells you basic economy cannot be changed (do not mention it if the agent does not mention it), you want the agent to cancel the current one and book a new one.

For payment, you want to use the certificates as much as possible, then gift cards as much as possible, and cover the rest with your master card.

But you want to know how much your master card will be charged.

You do not need baggage or insurance.

You want to minimize master card payment so you will only book the new flight if the mastercard charges are less than $2000.

You are calm.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "14_0",
  "name": "cancel_reservation",
  "arguments": {
   "reservation_id": "K1NW8N"
  },
  "info": null
 },
 {
  "action_id": "14_1",
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
     "amount": 1786
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
 "1786"
]
```

## nl_assertions (diagnostic only, do not gate reward)
```json
[
 "Agent communicates that total gift card balance is $327.",
 "Agent communicates that total certificate balance if $1000.",
 "Agent should cancel reservation K1NW8N.",
 "Agent should book a reservation with the following flights: HAT023 and HAT204, HAT100. No insurance. No baggage. Departure on 2024-05-26, return on 2024-05-28.",
 "Agent communicated that the $1786 will be charged to the mastercard."
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
