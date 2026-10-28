# Trajectory review brief — retail agent runs (checks 1e, 4f, 5c, 5d, 2j per task)

You review recorded conversations from the retail runs of tau2-bench v2.0.0 (commit `989d3285ae669e49503324bdb9981bf14fccedeb`): agent and user simulator both `claude-haiku-5-5`, stock scorer (`EvaluationType.ALL`), NL judge substituted by `claude-haiku-5-5`. Two runs: `retail_pass3_haiku` (every task x 3 trials, agent `llm_agent`) and `retail_gt_haiku` (one trial per task with reference actions, agent `llm_agent_gt`, which sees the reference actions). Your batch is a list of task ids; you read every trajectory listed for them in `results/retail/agent_triage.md` and, for flipped tasks, the successful trials too (all trials of a flipped task are rendered).

The question for every failed or flipped trajectory: **why did the score come out as it did, and does the cause sit in the agent, in the user simulator, in the judge, or in the task and its scoring?** Evidence beats impression: quote turn numbers (`[n]` markers in the transcript), tool calls and their results, and the scenario text.

## Inputs

- `results/retail/agent_triage.md` — the list (task, trial, reward, db_match, unmet assertions, termination, transcript path).
- `results/retail/trajectories/<task>_<haiku|gt>_t<k>.md` — transcripts (system prompt omitted; tool calls and results included; the user simulator's scenario is the task's `user_scenario`).
- `results/retail/task_cards/task_<id>.md` — scenario, reference actions with arguments, `nl_assertions`, `communicate_info`, reward basis.
- `results/retail/agent_runs_summary.md` — per-task rewards, `judge-only fails`, GT outcome.
- `results/retail/haiku_pass.csv` — rows with note `REVIEW` are the ones your verdict replaces.
- `retail/audit_log.csv` — the static audit rows of your tasks (reference defects already known: 1b, 1d, 1g, 2d, 2e, 2h, 4a–4e); use them to recognise a known reference problem when a trajectory runs into it.
- `tau2-bench/data/tau2/domains/retail/policy.md`; `tau2-bench/src/tau2/domains/retail/tools.py` (read-only); `tau2-bench/src/tau2/user/guidelines.py` (what the simulator is told); `checklist.md` and `retail/checklist.md` (check definitions and severities).
- Do not open `tau2-bench/data/tau2/domains/retail/tasks.json` or `task_issues/`. Do not call any model. Do not edit anything under `tau2-bench/`.

## Cause classes (one per trajectory, a second one in brackets when it contributes)

- **A agent slip** — the agent misreads data, states a wrong amount, picks a wrong tool argument, forgets a step, refuses something the policy allows, or does something the policy forbids.
- **B user-simulator deviation** — the simulator says something the scenario does not support (invents a fact or a preference, contradicts the scenario, withholds an instruction at its trigger, refuses what the scenario says it accepts, ends early against the scenario). Asking for a human is a deviation only where the scenario gives another instruction for that situation.
- **C defensible alternative reading** — the agent's path is a correct reading of the scenario and policy but not the reference's (another payment method the scenario allows, another variant that matches the stated options, a different but allowed order of actions).
- **D reference or scoring problem** — the reference actions, the `nl_assertions`, the scorer (hash, judge, order sensitivity) or the task text make a correct conversation score 0 or a wrong one score 1 (a reference that raises, an assertion that asks for something the user never asked for, an assertion that is unsatisfiable, a hash that depends on an order the scenario leaves open, a tool bug).
- **E judge error** — the DB matched and the only unmet item is an `nl_assertion` that the transcript does in fact satisfy (the agent said it, in substance, before the end), or the reverse: an assertion marked met that the transcript does not satisfy. Decide E by reading the assertion text against the agent's turns; the judge saw `role: content` lines only.

## Rows to file (CSV header `task_id,check,defect,severity,evidence,note`)

Per task in your batch, exactly one row for each of 1e, 4f, 5c, 5d, 2j (no duplicates; a task with no GT run gets 1e with defect=0 and note "no GT run"):

- **1e** (GT agent failed): defect=1 when the GT failure traces to class D (high if the reference cannot be reached by a policy-compliant conversation; medium otherwise); defect=0 for classes A, B, C, E with the class in the note. GT success: defect=0, note "GT reached reward 1.0".
- **4f** (a trajectory reveals a reference or scoring problem): defect=1 medium when any trajectory of the task shows class D that the static rows did not already carry (note which static row covers it if one does, then defect=0 with note "already in <check>"); high if the problem makes the task unsolvable by a compliant agent.
- **5c** (flip 1/3 or 2/3 traced to the simulator): defect=1 medium when the failing trial(s) fail because of class B while a successful trial shows the same agent behaviour succeeding; defect=0 with note "agent" / "judge, see 2j" / "stable" otherwise.
- **5d** (simulator deviation from the scenario): defect=1 medium when any read trajectory shows class B, whether or not it changed the reward; cite the turn and the scenario sentence it contradicts.
- **2j** (judge decides wrongly in a read trajectory): defect=1 medium for class E with the assertion text and the turn that satisfies (or fails) it; defect=0 with note "judge not involved" / "judge verdict matches the transcript" otherwise.

`evidence`: turn pointers and the facts (amounts, ids, tool results) in one line. `note`: cause class and one sentence. Severity empty when defect=0.

Also keep a `.md` with one short reading per trajectory (the pattern of `results/review_agent.md` of the airline block: what the user wanted, what the agent did, where the run diverged from the reference and why, decisive turns), then a per-task cause-class table.

## Output

- `results/retail/review_agent_<batch>.csv` and `results/retail/review_agent_<batch>.md` (batch letter given in your assignment).
- English, impersonal; no names of people; no mention of which model or tool wrote the review. Return in your final message: the rows with defect=1 (task, check, severity, one line) and the trajectories you could not decide.
