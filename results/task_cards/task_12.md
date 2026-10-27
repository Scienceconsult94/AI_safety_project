# Airline task 12

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=5 (read=3, write=1, generic=1), db_changed=1, comm_len=0, nl_count=2, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test that agent doesn't offer to modify the cabin for only one of the passenger of a reservation.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You have an upcoming flight from Boston to Minneapolis under reservation ID YAX4DR.

You want to change your class for all passengers to business.

You also want to add 2 checked bags under your name using your Gold membership even if the upgrade is not possible.

**known_info:**

Your name is Chen Lee.

Your user id is chen_lee_6825.

**unknown_info:**

None

**task_instructions:**

You are willing to pay a fee for the business class changes, up to $650.

If the costs are greater than that for the upgrade, then try to upgrade your companion Noah to business under the constraints.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "12_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "YAX4DR"
  },
  "info": null
 },
 {
  "action_id": "12_1",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "BOS",
   "destination": "MCO",
   "date": "2024-05-18"
  },
  "info": null
 },
 {
  "action_id": "12_2",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "MCO",
   "destination": "MSP",
   "date": "2024-05-19"
  },
  "info": null
 },
 {
  "action_id": "12_3",
  "name": "calculate",
  "arguments": {
   "expression": "2 * ((350 - 122) + (499 - 127))"
  },
  "info": null
 },
 {
  "action_id": "12_4",
  "name": "update_reservation_baggages",
  "arguments": {
   "reservation_id": "YAX4DR",
   "total_baggages": 2,
   "nonfree_baggages": 0,
   "payment_id": "credit_card_4938634"
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
 "Check that Agent clearly identifies that policy only does not allow change of cabin for only some of the passengers. All passengers must fly in the same cabin.",
 "Check that agent correctly adds 2 checked bags for free."
]
```

## DB records referenced
### user `chen_lee_6825`
```json
{
 "user_id": "chen_lee_6825",
 "name": {
  "first_name": "Chen",
  "last_name": "Lee"
 },
 "dob": "1967-12-12",
 "membership": "gold",
 "payment_methods": {
  "certificate_6730850": {
   "source": "certificate",
   "id": "certificate_6730850",
   "amount": 250.0
  },
  "certificate_9982533": {
   "source": "certificate",
   "id": "certificate_9982533",
   "amount": 100.0
  },
  "credit_card_4938634": {
   "source": "credit_card",
   "id": "credit_card_4938634",
   "brand": "visa",
   "last_four": "9990"
  }
 },
 "saved_passengers": [
  {
   "first_name": "Noah",
   "last_name": "Hernandez",
   "dob": "1968-01-06"
  }
 ],
 "reservations": [
  "JW6LEQ",
  "ICJ5WM",
  "TVN3KL",
  "ZBCR1P",
  "4KG36I",
  "YAX4DR",
  "9NK7W8"
 ]
}
```
### reservation `4KG36I`
```json
{
 "reservation_id": "4KG36I",
 "user_id": "chen_lee_6825",
 "origin": "ORD",
 "destination": "LAS",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "ORD",
   "destination": "DEN",
   "flight_number": "HAT238",
   "date": "2024-05-04",
   "price": 1358
  },
  {
   "origin": "DEN",
   "destination": "LAS",
   "flight_number": "HAT084",
   "date": "2024-05-04",
   "price": 1044
  },
  {
   "origin": "LAS",
   "destination": "IAH",
   "flight_number": "HAT266",
   "date": "2024-05-05",
   "price": 1516
  },
  {
   "origin": "IAH",
   "destination": "ORD",
   "flight_number": "HAT044",
   "date": "2024-05-05",
   "price": 1145
  }
 ],
 "passengers": [
  {
   "first_name": "Mei",
   "last_name": "Jackson",
   "dob": "1963-09-28"
  },
  {
   "first_name": "Noah",
   "last_name": "Hernandez",
   "dob": "1968-01-06"
  },
  {
   "first_name": "Amelia",
   "last_name": "Johansson",
   "dob": "1979-12-09"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 15189
  }
 ],
 "created_at": "2024-05-03T20:36:52",
 "total_baggages": 4,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `9NK7W8`
```json
{
 "reservation_id": "9NK7W8",
 "user_id": "chen_lee_6825",
 "origin": "BOS",
 "destination": "MIA",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "MIA",
   "flight_number": "HAT247",
   "date": "2024-05-10",
   "price": 101
  },
  {
   "origin": "MIA",
   "destination": "BOS",
   "flight_number": "HAT184",
   "date": "2024-05-13",
   "price": 119
  }
 ],
 "passengers": [
  {
   "first_name": "Yusuf",
   "last_name": "Rossi",
   "dob": "1961-08-04"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 250
  }
 ],
 "created_at": "2024-05-09T15:10:04",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `ICJ5WM`
```json
{
 "reservation_id": "ICJ5WM",
 "user_id": "chen_lee_6825",
 "origin": "LAS",
 "destination": "ATL",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "LAS",
   "destination": "SEA",
   "flight_number": "HAT040",
   "date": "2024-05-27",
   "price": 1097
  },
  {
   "origin": "SEA",
   "destination": "ATL",
   "flight_number": "HAT220",
   "date": "2024-05-27",
   "price": 1475
  }
 ],
 "passengers": [
  {
   "first_name": "Chen",
   "last_name": "Lee",
   "dob": "1967-12-12"
  },
  {
   "first_name": "Noah",
   "last_name": "Hernandez",
   "dob": "1968-01-06"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 5144
  }
 ],
 "created_at": "2024-05-07T01:12:59",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `JW6LEQ`
```json
{
 "reservation_id": "JW6LEQ",
 "user_id": "chen_lee_6825",
 "origin": "ORD",
 "destination": "LAS",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "ORD",
   "destination": "IAH",
   "flight_number": "HAT147",
   "date": "2024-05-26",
   "price": 1259
  },
  {
   "origin": "IAH",
   "destination": "LAS",
   "flight_number": "HAT112",
   "date": "2024-05-26",
   "price": 1214
  },
  {
   "origin": "LAS",
   "destination": "ATL",
   "flight_number": "HAT077",
   "date": "2024-05-30",
   "price": 1839
  },
  {
   "origin": "ATL",
   "destination": "ORD",
   "flight_number": "HAT227",
   "date": "2024-05-30",
   "price": 485
  }
 ],
 "passengers": [
  {
   "first_name": "Chen",
   "last_name": "Lee",
   "dob": "1967-12-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 4797
  }
 ],
 "created_at": "2024-05-05T17:48:42",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `TVN3KL`
```json
{
 "reservation_id": "TVN3KL",
 "user_id": "chen_lee_6825",
 "origin": "SEA",
 "destination": "ATL",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "SEA",
   "destination": "ATL",
   "flight_number": "HAT220",
   "date": "2024-05-18",
   "price": 148
  },
  {
   "origin": "ATL",
   "destination": "DFW",
   "flight_number": "HAT297",
   "date": "2024-05-30",
   "price": 129
  },
  {
   "origin": "DFW",
   "destination": "SEA",
   "flight_number": "HAT234",
   "date": "2024-05-30",
   "price": 138
  }
 ],
 "passengers": [
  {
   "first_name": "Chen",
   "last_name": "Lee",
   "dob": "1967-12-12"
  },
  {
   "first_name": "James",
   "last_name": "Davis",
   "dob": "1954-07-06"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 830
  }
 ],
 "created_at": "2024-05-02T23:08:45",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `YAX4DR`
```json
{
 "reservation_id": "YAX4DR",
 "user_id": "chen_lee_6825",
 "origin": "BOS",
 "destination": "MSP",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "BOS",
   "destination": "MCO",
   "flight_number": "HAT235",
   "date": "2024-05-18",
   "price": 122
  },
  {
   "origin": "MCO",
   "destination": "MSP",
   "flight_number": "HAT298",
   "date": "2024-05-19",
   "price": 127
  }
 ],
 "passengers": [
  {
   "first_name": "Chen",
   "last_name": "Lee",
   "dob": "1967-12-12"
  },
  {
   "first_name": "Noah",
   "last_name": "Hernandez",
   "dob": "1968-01-06"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 498
  }
 ],
 "created_at": "2024-05-05T23:00:15",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `ZBCR1P`
```json
{
 "reservation_id": "ZBCR1P",
 "user_id": "chen_lee_6825",
 "origin": "MIA",
 "destination": "CLT",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "MIA",
   "destination": "EWR",
   "flight_number": "HAT192",
   "date": "2024-05-14",
   "price": 666
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT043",
   "date": "2024-05-15",
   "price": 1584
  },
  {
   "origin": "CLT",
   "destination": "BOS",
   "flight_number": "HAT216",
   "date": "2024-05-18",
   "price": 732
  },
  {
   "origin": "BOS",
   "destination": "MIA",
   "flight_number": "HAT247",
   "date": "2024-05-18",
   "price": 471
  }
 ],
 "passengers": [
  {
   "first_name": "Chen",
   "last_name": "Lee",
   "dob": "1967-12-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4938634",
   "amount": 3453
  }
 ],
 "created_at": "2024-05-13T04:12:28",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "no"
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
### flight `HAT043` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT043",
 "origin": "EWR",
 "destination": "CLT",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "17:00:00"
}
```
### flight `HAT044` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT044",
 "origin": "IAH",
 "destination": "ORD",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "22:30:00"
}
```
### flight `HAT077` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT077",
 "origin": "LAS",
 "destination": "ATL",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "09:00:00"
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
### flight `HAT112` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT112",
 "origin": "IAH",
 "destination": "LAS",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT147` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT147",
 "origin": "ORD",
 "destination": "IAH",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "11:30:00"
}
```
### flight `HAT184` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT184",
 "origin": "MIA",
 "destination": "BOS",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
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
### flight `HAT216` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT216",
 "origin": "CLT",
 "destination": "BOS",
 "scheduled_departure_time_est": "05:00:00",
 "scheduled_arrival_time_est": "07:00:00"
}
```
### flight `HAT220` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT220",
 "origin": "SEA",
 "destination": "ATL",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "08:00:00"
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
### flight `HAT234` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT234",
 "origin": "DFW",
 "destination": "SEA",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "23:00:00"
}
```
### flight `HAT235` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT235",
 "origin": "BOS",
 "destination": "MCO",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "02:30:00+1"
}
```
### flight `HAT238` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT238",
 "origin": "ORD",
 "destination": "DEN",
 "scheduled_departure_time_est": "02:00:00",
 "scheduled_arrival_time_est": "04:00:00"
}
```
### flight `HAT247` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT247",
 "origin": "BOS",
 "destination": "MIA",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "12:00:00"
}
```
### flight `HAT266` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT266",
 "origin": "LAS",
 "destination": "IAH",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "16:00:00"
}
```
### flight `HAT297` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT297",
 "origin": "ATL",
 "destination": "DFW",
 "scheduled_departure_time_est": "12:00:00",
 "scheduled_arrival_time_est": "14:00:00"
}
```
### flight `HAT298` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT298",
 "origin": "MCO",
 "destination": "MSP",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "06:00:00"
}
```
