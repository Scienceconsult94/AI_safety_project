# nl_assertion classes (airline, 50 tasks, 123 assertions)

Source: `tau2-bench/data/tau2/domains/airline/tasks.json` (v2.0.0); sample = `sample.json` task_ids (20 tasks). Row-level detail: `nl_assertion_classes.csv`.

Classes: `db_dup` = restates a state change (or non-change) that the database (DB) hash check against the reference already enforces; `communication` = what the agent must tell the user; `negative` = must not do/offer something the DB check cannot see; `process` = how the agent worked (tool use, verification steps). Mixed assertions take the class that decides pass/fail; the secondary class is in the note.

## Counts

| class | all 50 tasks | 20 sampled tasks |
|---|---|---|
| db_dup | 87 (71%) | 39 (74%) |
| communication | 19 (15%) | 7 (13%) |
| negative | 10 (8%) | 4 (8%) |
| process | 7 (6%) | 3 (6%) |
| total | 123 | 53 |

## All `process` assertions

- task 2 [1]: Agent should check that the flight was indeed delayed. -- verification step; note: reference has no get_flight_status call
- task 8 [0] (sample): Agent get sophia_silva_7557 user details. -- tool usage (get_user_details)
- task 8 [1] (sample): Agent identifies reservation id as WUNA5K. -- lookup step (get_reservation_details WUNA5K)
- task 9 [2] (sample): Check that Agent searched for direct flights between JFK and MCO on May 22 2024. -- tool usage (search_direct_flight JFK-MCO 2024-05-22) matches reference
- task 38 [1]: Agent verifies that the flight was delayed. -- verification step; note: reference has no get_flight_status call
- task 38 [2]: Agent verifies the number of passengers in the reservation. -- verification step (get_reservation_details 4OG6T3)
- task 41 [0]: Agent checks all reservations. -- verification step (get_reservation_details for all 7 reservations)

## CONTRADICTS_REFERENCE flags

- task 8 [2] (sample) (db_dup): Agent books one-way flight HAT271, May 26, in economy, no travel insurance, no baggage. Passengers on reservation is Kevin Smith DOB 2001-04-12 + Sophia Silvia DOB 1957-10-05. -- CONTRADICTS_REFERENCE: passenger name "Sophia Silvia" vs reference "Sophia Silva"
- task 23 [3] (sample) (db_dup): Agent books a round-trip reservation from JFK to SFO in business with outbound flights HAT023 and HAT204 on 2024-05-26 and return flight HAT100 on 2024-05-28 for Mohamed Silva. -- CONTRADICTS_REFERENCE: says HAT204 outbound on 05-26; reference/DB: HAT204 SFO-SEA dated 05-28 (return leg)
- task 27 [1] (communication): Agent confirms that user can receive compensation because he has Silver status. -- CONTRADICTS_REFERENCE: reference issues no certificate and idx2 forbids it; policy: no delay comp w/o change/cancel
- task 35 [2] (db_dup): Agent charges $290 to credit card credit_card_907483 -- CONTRADICTS_REFERENCE: payment id "credit_card_907483" truncated; reference credit_card_9074831

## Other wording defects (not contradictions)

- task 9 [0] (sample): reference leaves it unchanged; DB hash enforces; rationale sentence garbled ("cannot be cancelled" twice)
- task 12 [0]: explanation of all-passengers-same-cabin policy; wording garbled ("only does not allow")
- task 14 [1]: stated balance; communicate_info 1000 (typo "if")
- task 14 [3]: book_reservation; ambiguous grouping "HAT023 and HAT204, HAT100" (HAT204 is 05-28 return leg)
- task 23 [4] (sample): payment_methods of 1st book_reservation; stray quote char in text
