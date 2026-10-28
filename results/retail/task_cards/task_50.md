# Retail task 50

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=1 (read=0, write=0, generic=1), db_changed=0, comm_len=0 (not scored), nl_count=0 (gates the reward), **noop_pass=1**, noop_needs_judge=0

## Task description (author annotation, not shown to the agent)
```json
{
 "purpose": null,
 "relevant_policies": null,
 "notes": null
}
```

## User-simulator instructions
**persona:** None

**reason_for_call:**

You're in a rush and you want to undo cancelling an order that you've previously placed. Be insistent that the customer service agent should undo the cancellation and ensure that the order is delivered as soon as possible. Do NOT mention the actual items that were in the order, just that you want to undo the cancellation and receive all the items that were in the initial order as soon as possible.

**known_info:**

You're Chen Smith, living in Jacksonville 32278.

**unknown_info:**

You do not remember your email address

**task_instructions:**

.

## Reference trajectory (evaluation_criteria.actions)
```json
[
 {
  "action_id": "50_0",
  "name": "transfer_to_human_agents",
  "arguments": {
   "summary": "The user urgently needs to undo a cancellation of an order and insists on receiving the items from the initial order as soon as possible. The user acknowledges the policy but requests exceptional measures due to the urgency of the situation."
  },
  "info": null,
  "compare_args": []
 }
]
```

## communicate_info (NOT in reward_basis: never scored by tau2 run)
```json
[]
```

## nl_assertions (gate the reward through the LLM judge)
```json
null
```

## DB records referenced
