# Airline task 21  (in sample20)

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'COMMUNICATE']
static scan: n_actions=2 (read=0, write=2, generic=0), db_changed=1, comm_len=0, nl_count=3, **noop_pass=0**

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": "Test capacity of agent to reason about shortest flight option. Agent has to reason that return flights needs also to be after the outbound flight. Also not all flights have economy option. Agent also has to reason about payment amounts.",
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You want to change the return flights for your upcoming Houston to Denver trip.
You want to change it to the fastest return trip (including stopover time) possible on the same day as the departure trip (May 27). If the fastest is not available, you are ok with the next fastest.

**known_info:**

Your name is Sofia Kim.

Your user id is sofia_kim_7287.
 
Your Houston to Denver trip's departure date is May 27.

**unknown_info:**

You don't remember your reservation id.

**task_instructions:**

You don't care about money but want to stay in economy. 

You also want to add one more checked bag. 

You want to be sure the agent uses your gift card with the smallest balance to pay.

You are reactive to the agent and will not say anything that is not asked. 

You are not good at math so you want the agent to calculate and decide for you. 

This is urgent. You want to get this done ASAP.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "21_0",
  "name": "update_reservation_flights",
  "arguments": {
   "reservation_id": "OBUT9V",
   "cabin": "economy",
   "flights": [
    {
     "flight_number": "HAT078",
     "date": "2024-05-27"
    },
    {
     "flight_number": "HAT118",
     "date": "2024-05-27"
    },
    {
     "flight_number": "HAT290",
     "date": "2024-05-27"
    },
    {
     "flight_number": "HAT175",
     "date": "2024-05-27"
    }
   ],
   "payment_id": "gift_card_6276644"
  },
  "info": null
 },
 {
  "action_id": "21_1",
  "name": "update_reservation_baggages",
  "arguments": {
   "reservation_id": "OBUT9V",
   "total_baggages": 2,
   "nonfree_baggages": 0,
   "payment_id": "gift_card_6276644"
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
 "Agent updates reservation OBUT9V return flights to HAT290 and HAT175 on May 27.",
 "Agent assigns payment to gift_card_6276644.",
 "Agent updates reservation OBUT9V to 2 free baggages."
]
```

## DB records referenced
### user `sofia_kim_7287`
```json
{
 "user_id": "sofia_kim_7287",
 "name": {
  "first_name": "Sofia",
  "last_name": "Kim"
 },
 "dob": "1950-06-24",
 "membership": "silver",
 "payment_methods": {
  "certificate_8544743": {
   "source": "certificate",
   "id": "certificate_8544743",
   "amount": 250.0
  },
  "credit_card_9879898": {
   "source": "credit_card",
   "id": "credit_card_9879898",
   "brand": "mastercard",
   "last_four": "9725"
  },
  "gift_card_7091239": {
   "source": "gift_card",
   "id": "gift_card_7091239",
   "amount": 157.0
  },
  "gift_card_6276644": {
   "source": "gift_card",
   "id": "gift_card_6276644",
   "amount": 113.0
  },
  "gift_card_7480005": {
   "source": "gift_card",
   "id": "gift_card_7480005",
   "amount": 6.0
  },
  "certificate_9932251": {
   "source": "certificate",
   "id": "certificate_9932251",
   "amount": 250.0
  }
 },
 "saved_passengers": [
  {
   "first_name": "Mia",
   "last_name": "Jackson",
   "dob": "1986-05-05"
  }
 ],
 "reservations": [
  "OI5L9G",
  "AQLBTL",
  "KA7I60",
  "I57WUD",
  "OBUT9V",
  "4BMN53",
  "Q0ZF0J"
 ]
}
```
### reservation `4BMN53`
```json
{
 "reservation_id": "4BMN53",
 "user_id": "sofia_kim_7287",
 "origin": "LGA",
 "destination": "LAS",
 "flight_type": "one_way",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT201",
   "date": "2024-05-22",
   "price": 173
  },
  {
   "origin": "PHX",
   "destination": "LAS",
   "flight_number": "HAT173",
   "date": "2024-05-22",
   "price": 156
  }
 ],
 "passengers": [
  {
   "first_name": "Juan",
   "last_name": "Wilson",
   "dob": "1982-12-20"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7480005",
   "amount": 359
  }
 ],
 "created_at": "2024-05-10T11:36:51",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `AQLBTL`
```json
{
 "reservation_id": "AQLBTL",
 "user_id": "sofia_kim_7287",
 "origin": "LAX",
 "destination": "LAX",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "LAX",
   "destination": "SFO",
   "flight_number": "HAT249",
   "date": "2024-05-19",
   "price": 127
  },
  {
   "origin": "SFO",
   "destination": "LAX",
   "flight_number": "HAT273",
   "date": "2024-05-19",
   "price": 156
  },
  {
   "origin": "LAX",
   "destination": "EWR",
   "flight_number": "HAT228",
   "date": "2024-05-26",
   "price": 145
  },
  {
   "origin": "EWR",
   "destination": "LAX",
   "flight_number": "HAT041",
   "date": "2024-05-27",
   "price": 138
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7480005",
   "amount": 596
  }
 ],
 "created_at": "2024-05-01T16:22:47",
 "total_baggages": 0,
 "nonfree_baggages": 0,
 "insurance": "yes"
}
```
### reservation `I57WUD`
```json
{
 "reservation_id": "I57WUD",
 "user_id": "sofia_kim_7287",
 "origin": "DFW",
 "destination": "DFW",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "DFW",
   "destination": "ATL",
   "flight_number": "HAT128",
   "date": "2024-05-18",
   "price": 1247
  },
  {
   "origin": "ATL",
   "destination": "DFW",
   "flight_number": "HAT297",
   "date": "2024-05-18",
   "price": 983
  },
  {
   "origin": "DFW",
   "destination": "SEA",
   "flight_number": "HAT067",
   "date": "2024-05-22",
   "price": 1207
  },
  {
   "origin": "SEA",
   "destination": "DFW",
   "flight_number": "HAT221",
   "date": "2024-05-23",
   "price": 1135
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  },
  {
   "first_name": "Mia",
   "last_name": "Jackson",
   "dob": "1986-05-05"
  },
  {
   "first_name": "Ava",
   "last_name": "Kim",
   "dob": "1962-04-02"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7480005",
   "amount": 13716
  }
 ],
 "created_at": "2024-05-01T11:03:53",
 "total_baggages": 4,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `KA7I60`
```json
{
 "reservation_id": "KA7I60",
 "user_id": "sofia_kim_7287",
 "origin": "DEN",
 "destination": "DTW",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "DEN",
   "destination": "CLT",
   "flight_number": "HAT160",
   "date": "2024-05-26",
   "price": 169
  },
  {
   "origin": "CLT",
   "destination": "DTW",
   "flight_number": "HAT167",
   "date": "2024-05-26",
   "price": 142
  },
  {
   "origin": "DTW",
   "destination": "CLT",
   "flight_number": "HAT191",
   "date": "2024-05-28",
   "price": 107
  },
  {
   "origin": "CLT",
   "destination": "DEN",
   "flight_number": "HAT262",
   "date": "2024-05-28",
   "price": 137
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7480005",
   "amount": 555
  }
 ],
 "created_at": "2024-05-07T16:05:48",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `OBUT9V`
```json
{
 "reservation_id": "OBUT9V",
 "user_id": "sofia_kim_7287",
 "origin": "IAH",
 "destination": "DEN",
 "flight_type": "round_trip",
 "cabin": "economy",
 "flights": [
  {
   "origin": "IAH",
   "destination": "ORD",
   "flight_number": "HAT078",
   "date": "2024-05-27",
   "price": 146
  },
  {
   "origin": "ORD",
   "destination": "DEN",
   "flight_number": "HAT118",
   "date": "2024-05-27",
   "price": 167
  },
  {
   "origin": "DEN",
   "destination": "LAS",
   "flight_number": "HAT084",
   "date": "2024-05-28",
   "price": 122
  },
  {
   "origin": "LAS",
   "destination": "IAH",
   "flight_number": "HAT266",
   "date": "2024-05-28",
   "price": 131
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7091239",
   "amount": 566
  }
 ],
 "created_at": "2024-05-07T16:32:35",
 "total_baggages": 1,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `OI5L9G`
```json
{
 "reservation_id": "OI5L9G",
 "user_id": "sofia_kim_7287",
 "origin": "MCO",
 "destination": "CLT",
 "flight_type": "one_way",
 "cabin": "business",
 "flights": [
  {
   "origin": "MCO",
   "destination": "BOS",
   "flight_number": "HAT017",
   "date": "2024-05-25",
   "price": 523
  },
  {
   "origin": "BOS",
   "destination": "CLT",
   "flight_number": "HAT277",
   "date": "2024-05-25",
   "price": 501
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  },
  {
   "first_name": "Mia",
   "last_name": "Jackson",
   "dob": "1986-05-05"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_6276644",
   "amount": 2048
  }
 ],
 "created_at": "2024-05-01T09:08:54",
 "total_baggages": 2,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### reservation `Q0ZF0J`
```json
{
 "reservation_id": "Q0ZF0J",
 "user_id": "sofia_kim_7287",
 "origin": "LGA",
 "destination": "MCO",
 "flight_type": "round_trip",
 "cabin": "business",
 "flights": [
  {
   "origin": "LGA",
   "destination": "PHX",
   "flight_number": "HAT201",
   "date": "2024-05-28",
   "price": 1002
  },
  {
   "origin": "PHX",
   "destination": "MCO",
   "flight_number": "HAT181",
   "date": "2024-05-28",
   "price": 1413
  },
  {
   "origin": "MCO",
   "destination": "PHX",
   "flight_number": "HAT161",
   "date": "2024-05-30",
   "price": 1540
  },
  {
   "origin": "PHX",
   "destination": "LGA",
   "flight_number": "HAT066",
   "date": "2024-05-30",
   "price": 1920
  }
 ],
 "passengers": [
  {
   "first_name": "Sofia",
   "last_name": "Kim",
   "dob": "1950-06-24"
  },
  {
   "first_name": "Ethan",
   "last_name": "Patel",
   "dob": "1968-11-03"
  }
 ],
 "payment_history": [
  {
   "payment_id": "gift_card_7480005",
   "amount": 11750
  }
 ],
 "created_at": "2024-05-09T12:27:05",
 "total_baggages": 3,
 "nonfree_baggages": 0,
 "insurance": "no"
}
```
### flight `HAT017` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT017",
 "origin": "MCO",
 "destination": "BOS",
 "scheduled_departure_time_est": "10:00:00",
 "scheduled_arrival_time_est": "13:30:00"
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
### flight `HAT066` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT066",
 "origin": "PHX",
 "destination": "LGA",
 "scheduled_departure_time_est": "21:00:00",
 "scheduled_arrival_time_est": "01:30:00+1"
}
```
### flight `HAT067` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT067",
 "origin": "DFW",
 "destination": "SEA",
 "scheduled_departure_time_est": "23:00:00",
 "scheduled_arrival_time_est": "03:00:00+1"
}
```
### flight `HAT078` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT078",
 "origin": "IAH",
 "destination": "ORD",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "03:30:00"
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
### flight `HAT118` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT118",
 "origin": "ORD",
 "destination": "DEN",
 "scheduled_departure_time_est": "04:00:00",
 "scheduled_arrival_time_est": "06:00:00"
}
```
### flight `HAT128` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT128",
 "origin": "DFW",
 "destination": "ATL",
 "scheduled_departure_time_est": "01:00:00",
 "scheduled_arrival_time_est": "03:00:00"
}
```
### flight `HAT160` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT160",
 "origin": "DEN",
 "destination": "CLT",
 "scheduled_departure_time_est": "06:00:00",
 "scheduled_arrival_time_est": "09:00:00"
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
### flight `HAT167` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT167",
 "origin": "CLT",
 "destination": "DTW",
 "scheduled_departure_time_est": "18:00:00",
 "scheduled_arrival_time_est": "20:00:00"
}
```
### flight `HAT173` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT173",
 "origin": "PHX",
 "destination": "LAS",
 "scheduled_departure_time_est": "09:00:00",
 "scheduled_arrival_time_est": "10:00:00"
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
### flight `HAT191` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT191",
 "origin": "DTW",
 "destination": "CLT",
 "scheduled_departure_time_est": "07:00:00",
 "scheduled_arrival_time_est": "09:00:00"
}
```
### flight `HAT201` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT201",
 "origin": "LGA",
 "destination": "PHX",
 "scheduled_departure_time_est": "03:00:00",
 "scheduled_arrival_time_est": "07:30:00"
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
### flight `HAT249` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT249",
 "origin": "LAX",
 "destination": "SFO",
 "scheduled_departure_time_est": "19:00:00",
 "scheduled_arrival_time_est": "20:30:00"
}
```
### flight `HAT262` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT262",
 "origin": "CLT",
 "destination": "DEN",
 "scheduled_departure_time_est": "13:00:00",
 "scheduled_arrival_time_est": "16:00:00"
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
### flight `HAT273` (schedule only; per-date status/prices omitted)
```json
{
 "flight_number": "HAT273",
 "origin": "SFO",
 "destination": "LAX",
 "scheduled_departure_time_est": "22:00:00",
 "scheduled_arrival_time_est": "23:30:00"
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
