# Retail task 24

bench_commit: `989d3285ae669e49503324bdb9981bf14fccedeb` · reward_basis: ['DB', 'NL_ASSERTION']
static scan: n_actions=0 (read=0, write=0, generic=0), db_changed=0, comm_len=2 (not scored), nl_count=1 (gates the reward), **noop_pass=0**, noop_needs_judge=1

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

You want to cancel the grill, but if the agent asks you to confirm, you regret and want to keep it. You then want to ask which two t-shirts you have ordered in another order, and what materials are they.

**known_info:**

You are Sofia Hernandez, and you live in Seattle, WA, 98193.

**unknown_info:**

You do not remember your email address

**task_instructions:**

Make everything sound very natural and make up reasons.

## Reference trajectory (evaluation_criteria.actions)
```json
[]
```

## communicate_info (NOT in reward_basis: never scored by tau2 run)
```json
[
 "polyester",
 "cotton"
]
```

## nl_assertions (gate the reward through the LLM judge)
```json
[
 "Agent should tell the user the materials of the two t-shirts are polyester and cotton."
]
```

## DB records referenced
