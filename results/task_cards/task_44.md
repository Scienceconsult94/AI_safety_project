# Airline task 44  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=19 (read=16, write=3, generic=0), db_changed=1, comm_len=0, nl_count=5, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test that agent can collect information about reservation, reason about durations as well as cancellation and upgrades options.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to cancel all your future reservations that contain any flights that are longer than 4 hours. 

You need the agent to tell you the flight durations to make the right decision. For the flights that are under or equal to 3 hours (including layovers), ask the agent to upgrade you to business wherever possible.

**known_info:**

You are Sophia Silva.
Your user id is sophia_silva_7557.

**unknown_info:**

None

**task_instructions:**

You are busy so for both the cancellation and upgrade you want to let the agent figure out which flights meet the duration conditions you have set.

Before they do the upgrade to business, ask the agent to tell you how much it will cost you in total.

You DO NOT want to upgrade to business and then cancel it. You do NOT have a health related issue, you are healthy now.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "44_0",
  "name": "get_user_details",
  "arguments": {
   "user_id": "sophia_silva_7557"
  },
  "info": null
 },
 {
  "action_id": "44_1",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "NM1VX1"
  },
  "info": null
 },
 {
  "action_id": "44_2",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "KC18K6"
  },
  "info": null
 },
 {
  "action_id": "44_3",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "S61CZX"
  },
  "info": null
 },
 {
  "action_id": "44_4",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "H8Q05L"
  },
  "info": null
 },
 {
  "action_id": "44_5",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "WUNA5K"
  },
  "info": null
 },
 {
  "action_id": "44_6",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "MSP",
   "destination": "EWR",
   "date": "2024-05-25"
  },
  "info": null
 },
 {
  "action_id": "44_7",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "EWR",
   "destination": "MSP",
   "date": "2024-05-27"
  },
  "info": null
 },
 {
  "action_id": "44_8",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "MSP",
   "destination": "EWR",
   "date": "2024-05-21"
  },
  "info": null
 },
 {
  "action_id": "44_9",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "EWR",
   "destination": "CLT",
   "date": "2024-05-21"
  },
  "info": null
 },
 {
  "action_id": "44_10",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "LAX",
   "destination": "EWR",
   "date": "2024-05-23"
  },
  "info": null
 },
 {
  "action_id": "44_11",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "EWR",
   "destination": "CLT",
   "date": "2024-05-24"
  },
  "info": null
 },
 {
  "action_id": "44_12",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "CLT",
   "destination": "EWR",
   "date": "2024-05-24"
  },
  "info": null
 },
 {
  "action_id": "44_13",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "EWR",
   "destination": "LAX",
   "date": "2024-05-25"
  },
  "info": null
 },
 {
  "action_id": "44_14",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "JFK",
   "destination": "ATL",
   "date": "2024-05-24"
  },
  "info": null
 },
 {
  "action_id": "44_15",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "ORD",
   "destination": "PHL",
   "date": "2024-05-10"
  },
  "info": null
 },
 {
  "action_id": "44_17",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "NM1VX1",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT300",
     "date": "2024-05-25"
    },
    {
     "flight_number": "HAT208",
     "date": "2024-05-27"
    }
   ],
   "payment_id": "credit_card_4196779"
  },
  "info": null
 },
 {
  "action_id": "44_18",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "H8Q05L",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT268",
     "date": "2024-05-24"
    }
   ],
   "payment_id": "credit_card_4196779"
  },
  "info": null
 },
 {
  "action_id": "44_19",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "KC18K6",
   "cabin": "business",
   "flights": [
    {
     "flight_number": "HAT300",
     "date": "2024-05-21"
    },
    {
     "flight_number": "HAT215",
     "date": "2024-05-21"
    }
   ],
   "payment_id": "credit_card_4196779"
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
 "Agent does not cancel reservation S61CZX as the user is healthy.",
 "The total cost that the agent mentions is between $1380 and $1390.",
 "Agent upgrades NM1VX1 to business.",
 "Agent upgrades H8Q05L to business.",
 "Agent updates KC18K6 to business."
]
```

## DB records referenced
### user `sophia_silva_7557`
```json
{
 "user_id": "sophia_silva_7557",
 "name": {
  "first_name": "Sophia",
  "last_name": "Silva"
 },
 "dob": "1957-10-05",
 "membership": "regular",
 "payment_methods": {
  "certificate_8045380": {
   "source": "certificate",
   "id": "certificate_8045380",
   "amount": 500.0
  },
  "certificate_3887113": {
   "source": "certificate",
   "id": "certificate_3887113",
   "amount": 150.0
  },
  "credit_card_4196779": {
   "source": "credit_card",
   "id": "credit_card_4196779",
   "brand": "visa",
   "last_four": "7238"
  },
  "gift_card_5094406": {
   "source": "gift_card",
   "id": "gift_card_5094406",
   "amount": 274.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Yara",
   "last_name": "Silva",
   "dob": "1972-06-16"
  },
  {
   "first_name": "Isabella",
   "last_name": "Moore",
   "dob": "1988-06-04"
  }
 ],
 "reservations": [
  "NM1VX1",
  "KC18K6",
  "S61CZX",
  "H8Q05L",
  "WUNA5K"
 ]
}
```
### reservation `H8Q05L`
```json
{
 "reservation_id": "H8Q05L",
 "user_id": "sophia_silva_7557",
 "origin": "JFK",
 "destination": "ATL",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "JFK",
   "destination": "ATL",
   "flight_number": "HAT268",
   "date": "2024-05-24",
   "price": 74
  }
 ],
 "passengers": [
  {
   "first_name": "Harper",
   "last_name": "Kovacs",
   "dob": "1973-10-26"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4196779",
   "amount": 104
  }
 ],
 "created_at": "2024-05-03T15:12:00",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `KC18K6`
```json
{
 "reservation_id": "KC18K6",
 "user_id": "sophia_silva_7557",
 "origin": "MSP",
 "destination": "CLT",
 "flight_type": "one_way",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MSP",
   "destination": "EWR",
   "flight_number": "HAT300",
   "date": "2024-05-21",
   "price": 55
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT215",
   "date": "2024-05-21",
   "price": 51
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Silva",
   "dob": "1957-10-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4196779",
   "amount": 136
  }
 ],
 "created_at": "2024-05-04T14:07:11",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `NM1VX1`
```json
{
 "reservation_id": "NM1VX1",
 "user_id": "sophia_silva_7557",
 "origin": "MSP",
 "destination": "EWR",
 "flight_type": "round_trip",
 "cabin": "basic_economy",
 "flights": [
  {
   "origin": "MSP",
   "destination": "EWR",
   "flight_number": "HAT300",
   "date": "2024-05-25",
   "price": 100
  },
  {
   "origin": "EWR",
   "destination": "MSP",
   "flight_number": "HAT208",
   "date": "2024-05-27",
   "price": 53
  }
 ],
 "passengers": [
  {
   "first_name": "Yara",
   "last_name": "Silva",
   "dob": "1972-06-16"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5094406",
   "amount": 183
  }
 ],
 "created_at": "2024-05-03T08:46:43",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `S61CZX`
```json
{
 "reservation_id": "S61CZX",
 "user_id": "sophia_silva_7557",
 "origin": "LAX",
 "destination": "CLT",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-23",
   "price": 131
  },
  {
   "origin": "EWR",
   "destination": "CLT",
   "flight_number": "HAT043",
   "date": "2024-05-24",
   "price": 163
  },
  {
   "origin": "CLT",
   "destination": "EWR",
   "flight_number": "HAT157",
   "date": "2024-05-24",
   "price": 157
  },
  {
   "origin": "EWR",
   "destination": "LAX",
   "flight_number": "HAT041",
   "date": "2024-05-25",
   "price": 186
  }
 ],
 "passengers": [
  {
   "first_name": "Harper",
   "last_name": "Jackson",
   "dob": "1974-09-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "credit_card_4196779",
   "amount": 667
  }
 ],
 "created_at": "2024-05-02T04:38:01",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `WUNA5K`
```json
{
 "reservation_id": "WUNA5K",
 "user_id": "sophia_silva_7557",
 "origin": "ORD",
 "destination": "PHL",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "ORD",
   "destination": "PHL",
   "flight_number": "HAT271",
   "date": "2024-05-10",
   "price": 160
  },
  {
   "origin": "PHL",
   "destination": "ORD",
   "flight_number": "HAT197",
   "date": "2024-05-11",
   "price": 100
  }
 ],
 "passengers": [
  {
   "first_name": "Sophia",
   "last_name": "Silva",
   "dob": "1957-10-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_5094406",
   "amount": 260
  }
 ],
 "created_at": "2024-05-08T19:01:02",
 "total_baggages": 1,
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
### flight `HAT157` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT157",
 "origin": "CLT",
 "destination": "EWR",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "01:00:00+1"
}
```
### flight `HAT197` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT197",
 "origin": "PHL",
 "destination": "ORD",
 "scheduled_departure_time_est": "17:00:00",
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
### flight `HAT215` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT215",
 "origin": "EWR",
 "destination": "CLT",
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
### flight `HAT268` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT268",
 "origin": "JFK",
 "destination": "ATL",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "09:30:00"
}
```
### flight `HAT271` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT271",
 "origin": "ORD",
 "destination": "PHL",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "21:00:00"
}
```
### flight `HAT300` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT300",
 "origin": "MSP",
 "destination": "EWR",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
