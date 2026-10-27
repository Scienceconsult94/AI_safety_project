# Airline task 20  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Book a flight with time and payment constraints.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to fly from New York to Seattle on May 20 (one way).

**known_info:**

Your name is Mia Li.
Your user id is mia_li_3668.

**unknown_info:**

None

**task_instructions:**

You do not want to fly before 11am est.

You want to fly in economy.

You prefer direct flights but one stopover also fine.

If there are multiple options, you prefer the one with the lowest price. 

You have 3 baggages.

You do not want insurance.

You want to use your two certificates to pay. 

If only one certificate can be used, you prefer using the larger one, and pay the rest with your 7447 card.

You are reactive to the agent and will not say anything that is not asked.

Your birthday is in your user profile so you do not prefer to provide it.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "20_0",
  "name": "book_reservation",
  "arguments": {
   "user_id": "mia_li_3668",
   "origin": "JFK",
   "destination": "SEA",
   "flight_type": "one_way",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT136",
     "date": "2024-05-20"
    },
    {
     "flight_number": "HAT039",
     "date": "2024-05-20"
    }
   ],
   "passengers": [
    {
     "first_name": "Mia",
     "last_name": "Li",
     "dob": "1990-04-05"
    }
   ],
   "payment_methods": [
    {
     "payment_id": "certificate_7504069",
     "amount": 250
    },
    {
     "payment_id": "credit_card_4421486",
     "amount": 5
    }
   ],
   "total_baggages": 3,
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
 "Agent books one-way one-stop economy trip from JFK to SEA with flights HAT136 and HAT039 on 2024-05-20, 3 baggages, no insurance.",
 "Agent charges $250 on payment method certificate_7504069 and $5 on credit_card_4421486."
]
```

## DB records referenced
### user `mia_li_3668`
```json
{
 "user_id": "mia_li_3668",
 "name": {
  "first_name": "Mia",
  "last_name": "Li"
 },
 "dob": "1990-04-05",
 "membership": "gold",
 "payment_methods": {
  "credit_card_4421486": {
   "source": "credit_card",
   "id": "credit_card_4421486",
   "brand": "visa",
   "last_four": "7447"
  },
  "certificate_4856383": {
   "source": "certificate",
   "id": "certificate_4856383",
   "amount": 100.0
  },
  "certificate_7504069": {
   "source": "certificate",
   "id": "certificate_7504069",
   "amount": 250.0
  },
  "credit_card_1955700": {
   "source": "credit_card",
   "id": "credit_card_1955700",
   "brand": "visa",
   "last_four": "1907"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Ahmed",
   "dob": "1957-03-21"
  }
 ],
 "reservations": [
  "NO6JO3",
  "AIXC49",
  "HKEG34"
 ]
}
```
### reservation `AIXC49`
```json
{
 "reservation_id": "AIXC49",
 "user_id": "mia_li_3668",
 "origin": "LAX",
 "destination": "BOS",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "LAX",
   "destination": "SFO",
   "flight_number": "HAT094",
   "date": "2024-05-20",
   "price": 73
  },
  {
   "origin": "SFO",
   "destination": "BOS",
   "flight_number": "HAT294",
   "date": "2024-05-20",
   "price": 50
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Ahmed",
   "dob": "1957-03-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4421486",
   "amount": 123
  }
 ],
 "created_at": "2024-05-03T12:14:19",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `HKEG34`
```json
{
 "reservation_id": "HKEG34",
 "user_id": "mia_li_3668",
 "origin": "DEN",
 "destination": "LAS",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "DEN",
   "destination": "LAS",
   "flight_number": "HAT290",
   "date": "2024-05-27",
   "price": 1395
  }
 ],
 "passengers": [
  {
   "first_name": "Amelia",
   "last_name": "Ahmed",
   "dob": "1957-03-21"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1955700",
   "amount": 1395
  }
 ],
 "created_at": "2024-05-09T17:50:39",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `NO6JO3`
```json
{
 "reservation_id": "NO6JO3",
 "user_id": "mia_li_3668",
 "origin": "JFK",
 "destination": "DFW",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "JFK",
   "destination": "SEA",
   "flight_number": "HAT083",
   "date": "2024-05-16",
   "price": 483
  },
  {
   "origin": "SEA",
   "destination": "DFW",
   "flight_number": "HAT221",
   "date": "2024-05-16",
   "price": 1991
  }
 ],
 "passengers": [
  {
   "first_name": "Mia",
   "last_name": "Li",
   "dob": "1990-04-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_1955700",
   "amount": 2504
  }
 ],
 "created_at": "2024-05-09T16:15:57",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT039` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT039",
 "origin": "ATL",
 "destination": "SEA",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "03:00:00+1"
}
```
### flight `HAT083` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT083",
 "origin": "JFK",
 "destination": "SEA",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "07:00:00"
}
```
### flight `HAT094` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT094",
 "origin": "LAX",
 "destination": "SFO",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "05:30:00"
}
```
### flight `HAT136` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT136",
 "origin": "JFK",
 "destination": "ATL",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "21:30:00"
}
```
### flight `HAT221` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT221",
 "origin": "SEA",
 "destination": "DFW",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT290` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT290",
 "origin": "DEN",
 "destination": "LAS",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:00:00"
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
