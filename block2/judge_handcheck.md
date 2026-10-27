# Hand-check of judge verdicts (V2, recorded simulations)

46 items selected by `scripts/v2/judge_handcheck.py` (reasons: {'communication': 28, 'process': 12, 'flip': 8, 'reward-changing': 1}). Reader A = author; reader B = blind second reader (Opus), both labelled from the judge-visible transcript without seeing the judge's verdict.

| comparison | agreement |
|---|---|
| A vs B | 46/46 |
| A vs judge | 46/46 |
| B vs judge | 46/46 |
| A = B = judge | 46/46 |

| item | agent | task | trial | assertion | class | why | judge | A | B | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | gt | 3 | 0 | 0 | communication | communication | met (3-0) | met | met | states silver twice / B: gt_3_t0: assistant states records show membership level silver not gold |
| 2 | gt | 3 | 0 | 1 | communication | communication | met (3-0) | met | met | 4 free checked bags stated / B: gt_3_t0: assistant states 2 per economy passenger x 2 = 4 free checked bags |
| 3 | gt | 7 | 0 | 3 | communication | communication | unmet (0-3) | unmet | unmet | GT stated $1,004 (XEHM4B still active), not 708 / B: gt_7_t0: agent lists 7WPL39 $402 and 3EMQJ6 $306 but states total $1,004 incl. X |
| 4 | gt | 8 | 0 | 0 | process | process | met (3-0) | met | met | get_user_details call / B: gt_8_t0: get_user_details({user_id: sophia_silva_7557}) called |
| 5 | gt | 8 | 0 | 1 | process | process | met (3-0) | met | met | get_reservation_details WUNA5K / B: gt_8_t0: get_reservation_details(WUNA5K) called, then agent cites HAT271 from th |
| 6 | gt | 9 | 0 | 2 | process | process | met (3-0) | met | met | search_direct_flight JFK MCO 2024-05-22 / B: gt_9_t0: search_direct_flight(JFK, MCO, 2024-05-22) called |
| 7 | gt | 23 | 0 | 0 | communication | communication | met (3-0) | met | met | $327 / B: gt_23_t0: assistant text 'Your gift cards total $327' |
| 8 | gt | 23 | 0 | 1 | communication | communication | met (3-0) | met | met | $1,000 / B: gt_23_t0: assistant text 'certificates total $1,000' |
| 9 | gt | 23 | 0 | 7 | communication | communication | met (3-0) | met | met | '$1,286 in total' stated in the split plan / B: gt_23_t0: assistant text 'Your Mastercard would be charged $1,286 in total' (spl |
| 10 | gt | 44 | 0 | 1 | communication | communication | unmet (0-3) | unmet | unmet | totals quoted $1,679 / $1,346, not 1380-1390 / B: gt_44_t0: agent states $1,679 business fares and $1,346 additional; neither in $ |
| 11 | haiku | 3 | 0 | 0 | communication | communication | met (2-0) | met | met |  / B: haiku_3_t0: assistant says account shows silver not gold (rechecked via get_user |
| 12 | haiku | 3 | 0 | 1 | communication | communication | met (2-0) | met | met |  / B: haiku_3_t0: assistant states total free checked bag allowance is 4 (2 per each o |
| 13 | haiku | 3 | 1 | 0 | communication | communication | met (3-0) | met | met |  / B: haiku_3_t1: assistant states 'Membership tier on file: Silver' |
| 14 | haiku | 3 | 1 | 1 | communication | communication | met (3-0) | met | met |  / B: haiku_3_t1: assistant states 2 per economy passenger x 2 passengers = 4 free che |
| 15 | haiku | 3 | 2 | 0 | communication | communication | met (3-0) | met | met |  / B: haiku_3_t2: assistant says profile lists membership as silver |
| 16 | haiku | 3 | 2 | 1 | communication | communication | met (3-0) | met | met |  / B: haiku_3_t2: assistant states 2 passengers x 2 bags = 4 free checked bags |
| 17 | haiku | 7 | 0 | 0 | db_dup | flip | met (3-0) | met | met | update_reservation_flights XEHM4B business / B: update_reservation_flights XEHM4B cabin=business with credit_card_2408938 (agent |
| 18 | haiku | 7 | 0 | 1 | db_dup | flip | met (3-0) | met | met | cancel_reservation XEHM4B / B: cancel_reservation(XEHM4B) called after the business upgrade |
| 19 | haiku | 7 | 0 | 2 | db_dup | flip | met (3-0) | met | met | cancel_reservation 59XX6W / B: cancel_reservation(59XX6W) after illness covered by insurance confirmed |
| 20 | haiku | 7 | 0 | 3 | communication | communication+flip | met (3-0) | met | met | combined total $708 stated / B: Assistant text: 7WPL39 $402 + 3EMQJ6 $306, "combined total is $708" |
| 21 | haiku | 7 | 1 | 3 | communication | communication | unmet (0-3) | unmet | unmet | $1,004 stated / B: Agent listed $402 and $306 but stated total $1004 incl. XEHM4B; $708 never state |
| 22 | haiku | 7 | 2 | 3 | communication | communication | unmet (0-3) | unmet | unmet | $1,004 stated / B: Agent table incl. XEHM4B; stated total $1004; $708 never stated |
| 23 | haiku | 8 | 0 | 0 | process | process | met (3-0) | met | met |  / B: get_user_details(sophia_silva_7557) called |
| 24 | haiku | 8 | 0 | 1 | process | process | met (3-0) | met | met | 'Your May 10 reservation (WUNA5K)' / B: Assistant text: "Your May 10 reservation (WUNA5K) lists flight HAT271" |
| 25 | haiku | 8 | 1 | 0 | process | process | met (3-0) | met | met |  / B: get_user_details(sophia_silva_7557) called |
| 26 | haiku | 8 | 1 | 1 | process | process | met (3-0) | met | met | 'I found your May 10 trip (reservation WUNA5K)' / B: Assistant text: "I found your May 10 trip (reservation WUNA5K)" |
| 27 | haiku | 8 | 2 | 0 | process | process | met (3-0) | met | met |  / B: get_user_details(sophia_silva_7557) called (twice) |
| 28 | haiku | 8 | 2 | 1 | process | process | met (3-0) | met | met | 'I checked your May 10 reservation (WUNA5K)' / B: Assistant text: "I checked your May 10 reservation (WUNA5K). It includes HAT271" |
| 29 | haiku | 9 | 0 | 0 | db_dup | flip | met (3-0) | met | met | IFOYYZ not cancelled / B: haiku_9_t0: no cancel_reservation call; agent told user IFOYYZ cannot be cancell |
| 30 | haiku | 9 | 0 | 1 | db_dup | flip | met (3-0) | met | met | NQNU5R not cancelled / B: haiku_9_t0: no cancel_reservation call for NQNU5R; transferred to human instead |
| 31 | haiku | 9 | 0 | 2 | process | flip+process+reward-changing | unmet (0-3) | unmet | unmet | no search_direct_flight call; transferred instead / B: haiku_9_t0: no search_direct_flight call at all; agent transferred before search |
| 32 | haiku | 9 | 0 | 3 | db_dup | flip | met (3-0) | met | met | M20IZO untouched / B: haiku_9_t0: no update/modify call on M20IZO; agent says no changes made |
| 33 | haiku | 9 | 1 | 2 | process | process | met (3-0) | met | met | search_direct_flight JFK MCO 2024-05-22 call / B: haiku_9_t1: search_direct_flight(JFK, MCO, 2024-05-22) called |
| 34 | haiku | 9 | 2 | 2 | process | process | met (3-0) | met | met | search call present / B: haiku_9_t2: search_direct_flight(JFK, MCO, 2024-05-22) called |
| 35 | haiku | 23 | 0 | 0 | communication | communication | met (3-0) | met | met |  / B: t0 assistant turn: "Gift cards: $327 total ($198 ... and $129 ...)" |
| 36 | haiku | 23 | 0 | 1 | communication | communication | met (3-0) | met | met |  / B: t0 assistant turn: "Travel certificates: $1,000 total ($500, $250, $250)" |
| 37 | haiku | 23 | 0 | 7 | communication | communication | met (3-0) | met | met | $1,286 total stated / B: t0 assistant states "Total charged to the Mastercard ending in 9363: $1,286" bef |
| 38 | haiku | 23 | 1 | 0 | communication | communication | met (3-0) | met | met |  / B: t1 assistant turn: "Gift cards: $327 total ($198 ... and $129 ...)" |
| 39 | haiku | 23 | 1 | 1 | communication | communication | met (3-0) | met | met |  / B: t1 assistant turn: "Travel certificates: $1,000 total ($500, $250, $250)" |
| 40 | haiku | 23 | 1 | 7 | communication | communication | met (3-0) | met | met |  / B: t1 assistant states "Total charged to the Mastercard ending in 9363: $1,286" bef |
| 41 | haiku | 23 | 2 | 0 | communication | communication | met (3-0) | met | met |  / B: t2 assistant turn: "Gift cards: $327.00 total ($198.00 ... and $129.00 ...)" |
| 42 | haiku | 23 | 2 | 1 | communication | communication | met (3-0) | met | met |  / B: t2 assistant turn: "Travel certificates: $1,000.00 total ($500, $250, $250)" |
| 43 | haiku | 23 | 2 | 7 | communication | communication | met (3-0) | met | met |  / B: t2 assistant states "Total charged to the Mastercard ending 9363: $1,286" in pla |
| 44 | haiku | 44 | 0 | 1 | communication | communication | unmet (0-3) | unmet | unmet | total quoted $647 / B: Agent stated upgrade total $647 (only NM1VX1+H8Q05L); no total in $1380-1390 |
| 45 | haiku | 44 | 1 | 1 | communication | communication | met (3-0) | met | met | $1,387 / B: Assistant text: combined upgrade total "about $1,387" (NM1VX1+KC18K6+H8Q05L) |
| 46 | haiku | 44 | 2 | 1 | communication | communication | unmet (0-3) | unmet | unmet | $647 (KC18K6 excluded) / B: Agent stated $874 then corrected to $647; no total in $1380-1390 |

Items where both readers disagree with the judge: none.
