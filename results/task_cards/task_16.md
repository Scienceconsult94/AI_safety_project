# Airline task 16  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=1 (read=0, write=1, generic=0), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test finding cheapest Economy cabin class (not Basic Economy) flight on the next day.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

For your upcoming trip from ATL to PHL, you want to change for the cheapest flight in Economy cabin class (not Basic Economy) and for the day after the original reservation.

**known_info:**

Your name is Aarav Garcia.

Your user id is aarav_garcia_1177.

**unknown_info:**

None

**task_instructions:**

You are happy with original payment for refund.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "16_0",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "M05KNL",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT110",
     "date": "2024-05-24"
    },
    {
     "flight_number": "HAT172",
     "date": "2024-05-24"
    }
   ],
   "payment_id": "gift_card_8887175"
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
 "Agent updates M05KNL to economy with the following flights: HAT110 and HAT172 on 2024-05-24.",
 "Agent uses payment id gift_card_8887175."
]
```

## DB records referenced
### user `aarav_garcia_1177`
```json
{
 "user_id": "aarav_garcia_1177",
 "name": {
  "first_name": "Aarav",
  "last_name": "Garcia"
 },
 "dob": "1992-09-13",
 "membership": "gold",
 "payment_methods": {
  "certificate_7473723": {
   "source": "certificate",
   "id": "certificate_7473723",
   "amount": 150.0
  },
  "gift_card_8887175": {
   "source": "gift_card",
   "id": "gift_card_8887175",
   "amount": 35.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Lei",
   "last_name": "Ito",
   "dob": "1990-12-07"
  }
 ],
 "reservations": [
  "M05KNL",
  "UHDAHF"
 ]
}
```
### reservation `M05KNL`
```json
{
 "reservation_id": "M05KNL",
 "user_id": "aarav_garcia_1177",
 "origin": "ATL",
 "destination": "PHL",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "ATL",
   "destination": "ORD",
   "flight_number": "HAT227",
   "date": "2024-05-23",
   "price": 1936
  },
  {
   "origin": "ORD",
   "destination": "PHL",
   "flight_number": "HAT139",
   "date": "2024-05-23",
   "price": 851
  }
 ],
 "passengers": [
  {
   "first_name": "Aarav",
   "last_name": "Garcia",
   "dob": "1992-09-13"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_8887175",
   "amount": 2787
  }
 ],
 "created_at": "2024-05-14T06:33:04",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `UHDAHF`
```json
{
 "reservation_id": "UHDAHF",
 "user_id": "aarav_garcia_1177",
 "origin": "CLT",
 "destination": "LAX",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT015",
   "date": "2024-05-19",
   "price": 98
  },
  {
   "origin": "EWR",
   "destination": "LAX",
   "flight_number": "HAT041",
   "date": "2024-05-19",
   "price": 80
  },
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-27",
   "price": 50
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT270",
   "date": "2024-05-28",
   "price": 72
  }
 ],
 "passengers": [
  {
   "first_name": "Liam",
   "last_name": "Rossi",
   "dob": "1992-04-16"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_8887175",
   "amount": 330
  }
 ],
 "created_at": "2024-05-08T02:21:25",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### flight `HAT015` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT015",
 "origin": "CLT",
 "destination": "EWR",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "03:00:00"
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
### flight `HAT110` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT110",
 "origin": "ATL",
 "destination": "LGA",
 "scheduled_departure_time_est": "14:00:00",
 "scheduled_arrival_time_est": "16:30:00"
}
```
### flight `HAT139` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT139",
 "origin": "ORD",
 "destination": "PHL",
 "scheduled_departure_time_est": "17:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT172` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT172",
 "origin": "LGA",
 "destination": "PHL",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "00:00:00+1"
}
```
### flight `HAT227` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT227",
 "origin": "ATL",
 "destination": "ORD",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:00:00"
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
### flight `HAT270` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT270",
 "origin": "EWR",
 "destination": "CLT",
 "scheduled_departure_time_est": "11:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
