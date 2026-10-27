# Airline task 33

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=5 (read=3, write=2, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "User wants change flight dates. Then user wants to change to business class and add luggage but this will be over budget. User will try to change only one leg to business but this is not allowed. User will just add more bags.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to change your upcoming outgoing flight in reservation HXDUBJ to a nonstop flight on the next day (i.e. delay by one day).

You also want to move back your return from SFO by one day.

**known_info:**

You are Yara Garcia.
Your user id is yara_garcia_1905.

**unknown_info:**

None

**task_instructions:**

You only want flights departing after 8am and before 9pm. 

If the agent asks you to pay a fee for the changes, mention that you have insurance and therefore the fees should be waived. 

You have read that on the website and want the agent to honor the policy. 

Be persistent.

Only after you have been able to make the modifications to your flights, you suddenly decide that you'd also like to change upgrade your ticket to business class and add 2 checked bags. 

You are willing to pay up to $200 for that. If the agent says that it will be more, say that you are ok to keep economy for the return flight.

If and only if that is not possible, you are ok with economy for both legs. But you do want to add the 2 bags.

You are ok with paying for it using the original form of payment.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "33_0",
  "name": "get_reservation_details",
  "arguments": {
   "reservation_id": "HXDUBJ"
  },
  "info": null
 },
 {
  "action_id": "33_1",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "IAH",
   "destination": "SFO",
   "date": "2024-05-19"
  },
  "info": null
 },
 {
  "action_id": "33_2",
  "name": "search_direct_flight",
  "arguments": {
   "origin": "SFO",
   "destination": "IAH",
   "date": "2024-05-21"
  },
  "info": null
 },
 {
  "action_id": "33_3",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "HXDUBJ",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT072",
     "date": "2024-05-19"
    },
    {
     "flight_number": "HAT278",
     "date": "2024-05-23"
    }
   ],
   "payment_id": "gift_card_6941833"
  },
  "info": null
 },
 {
  "action_id": "33_4",
  "name": "update_reservation_baggages",
  "arguments": {
   "reservation_id": "HXDUBJ",
   "total_baggages": 2,
   "nonfree_baggages": 0,
   "payment_id": "gift_card_6941833"
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
 "Agent updates reservation HXDUBJ to flights HAT072 on 2024-05-19 and HAT278 on 2024-05-23.",
 "Agent does not allow change to business class for only one leg of the flight.",
 "Agent add 2 free baggages to reservation HXDUBJ."
]
```

## DB records referenced
### user `yara_garcia_1905`
```json
{
 "user_id": "yara_garcia_1905",
 "name": {
  "first_name": "Yara",
  "last_name": "Garcia"
 },
 "dob": "1974-08-15",
 "membership": "gold",
 "payment_methods": {
  "certificate_2345996": {
   "source": "certificate",
   "id": "certificate_2345996",
   "amount": 150.0
  },
  "gift_card_6941833": {
   "source": "gift_card",
   "id": "gift_card_6941833",
   "amount": 152.0
  },
  "gift_card_1646646": {
   "source": "gift_card",
   "id": "gift_card_1646646",
   "amount": 200.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "James",
   "last_name": "Khan",
   "dob": "1959-08-18"
  }
 ],
 "reservations": [
  "HXDUBJ",
  "DXG8T6",
  "46BBSE",
  "P9VXUO"
 ]
}
```
### reservation `46BBSE`
```json
{
 "reservation_id": "46BBSE",
 "user_id": "yara_garcia_1905",
 "origin": "MCO",
 "destination": "DTW",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT214",
   "date": "2024-05-22",
   "price": 102
  },
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT265",
   "date": "2024-05-23",
   "price": 130
  }
 ],
 "passengers": [
  {
   "first_name": "Yara",
   "last_name": "Garcia",
   "dob": "1974-08-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6941833",
   "amount": 232
  }
 ],
 "created_at": "2024-05-11T15:08:46",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `DXG8T6`
```json
{
 "reservation_id": "DXG8T6",
 "user_id": "yara_garcia_1905",
 "origin": "PHX",
 "destination": "MSP",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "PHX",
   "destination": "DTW",
   "flight_number": "HAT106",
   "date": "2024-05-20",
   "price": 1886
  },
  {
   "origin": "DTW",
   "destination": "MSP",
   "flight_number": "HAT237",
   "date": "2024-05-20",
   "price": 1216
  },
  {
   "origin": "MSP",
   "destination": "MCO",
   "flight_number": "HAT054",
   "date": "2024-05-24",
   "price": 1154
  },
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT161",
   "date": "2024-05-24",
   "price": 989
  }
 ],
 "passengers": [
  {
   "first_name": "Yara",
   "last_name": "Garcia",
   "dob": "1974-08-15"
  },
  {
   "first_name": "Olivia",
   "last_name": "Garcia",
   "dob": "1998-12-12"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1646646",
   "amount": 10490
  }
 ],
 "created_at": "2024-05-13T21:53:11",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `HXDUBJ`
```json
{
 "reservation_id": "HXDUBJ",
 "user_id": "yara_garcia_1905",
 "origin": "IAH",
 "destination": "SFO",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "IAH",
   "destination": "JFK",
   "flight_number": "HAT085",
   "date": "2024-05-18",
   "price": 177
  },
  {
   "origin": "JFK",
   "destination": "SFO",
   "flight_number": "HAT023",
   "date": "2024-05-18",
   "price": 146
  },
  {
   "origin": "SFO",
   "destination": "IAH",
   "flight_number": "HAT278",
   "date": "2024-05-22",
   "price": 180
  }
 ],
 "passengers": [
  {
   "first_name": "Yara",
   "last_name": "Garcia",
   "dob": "1974-08-15"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6941833",
   "amount": 533
  }
 ],
 "created_at": "2024-05-04T06:04:48",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `P9VXUO`
```json
{
 "reservation_id": "P9VXUO",
 "user_id": "yara_garcia_1905",
 "origin": "ORD",
 "destination": "PHX",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "ORD",
   "destination": "DTW",
   "flight_number": "HAT230",
   "date": "2024-05-20",
   "price": 846
  },
  {
   "origin": "DTW",
   "destination": "PHX",
   "flight_number": "HAT035",
   "date": "2024-05-20",
   "price": 782
  }
 ],
 "passengers": [
  {
   "first_name": "James",
   "last_name": "Khan",
   "dob": "1959-08-18"
  },
  {
   "first_name": "Sofia",
   "last_name": "Kovacs",
   "dob": "1979-08-23"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_1646646",
   "amount": 3256
  }
 ],
 "created_at": "2024-05-12T02:41:19",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
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
### flight `HAT035` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT035",
 "origin": "DTW",
 "destination": "PHX",
 "scheduled_departure_time_est": "15:00:00",
 "scheduled_arrival_time_est": "19:00:00"
}
```
### flight `HAT054` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT054",
 "origin": "MSP",
 "destination": "MCO",
 "scheduled_departure_time_est": "08:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT072` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT072",
 "origin": "IAH",
 "destination": "SFO",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "13:00:00"
}
```
### flight `HAT085` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT085",
 "origin": "IAH",
 "destination": "JFK",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:30:00"
}
```
### flight `HAT106` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT106",
 "origin": "PHX",
 "destination": "DTW",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "08:00:00"
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
### flight `HAT214` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT214",
 "origin": "MCO",
 "destination": "PHX",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "02:30:00+1"
}
```
### flight `HAT230` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT230",
 "origin": "ORD",
 "destination": "DTW",
 "scheduled_departure_time_est": "00:00:00",
 "scheduled_arrival_time_est": "01:00:00"
}
```
### flight `HAT237` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT237",
 "origin": "DTW",
 "destination": "MSP",
 "scheduled_departure_time_est": "20:00:00",
 "scheduled_arrival_time_est": "22:00:00"
}
```
### flight `HAT265` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT265",
 "origin": "PHX",
 "destination": "DTW",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "11:00:00"
}
```
### flight `HAT278` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT278",
 "origin": "SFO",
 "destination": "IAH",
 "scheduled_departure_time_est": "16:00:00",
 "scheduled_arrival_time_est": "20:00:00"
}
```
