# Adversarial review brief: retail agent-run rows, four parts (2026-10-28)

This brief replaces the single pass of `retail/skeptic_brief_agent.md`. That pass stopped on a usage limit before it wrote any output. The review now runs in four parts on disjoint task sets, with the account owner's approval. The consistency rules below are fixed in advance so that the four parts decide alike, and they follow the airline precedents so that one reading holds for the whole audit.

## Files you must not open (read this list first)

- `tau2-bench/data/tau2/domains/retail/tasks.json` and anything under `task_issues/`.
- `report.md`, `README.md`, `ONE_PAGER.md`, `retail/summary_numbers.md`, `retail/comparison.md`: they state headline counts that this review may change.
- The temporary folders and outputs of the other parts.

## Object

- The rows of your tasks in `results/retail/review_agent.csv`: exactly one row per task for each of 1e, 4f, 5c, 5d and 2j. Five reviewers wrote them on disjoint batches (`results/retail/review_agent_<A..E>.csv`). Their readings per trajectory are in `results/retail/review_agent_<A..E>.md` (grep for your task ids).
- The 3-vote re-judge, for 2j: `results/retail/rejudge.csv`, `results/retail/rejudge_summary.md`.

Try to kill every `defect=1` row before it counts. Catch the rows that should have been defects. Apply the rules below to every row of your tasks, zeros included.

## Parts

| part | tasks | defect=1 rows |
|---|---|---|
| p1 | 0, 1, 5, 9, 11, 15, 16, 19, 21, 27, 28, 29 | 16 |
| p2 | 30, 31, 32, 34, 38, 39, 43, 46, 49, 51, 52 | 18 |
| p3 | 55, 59, 64, 66, 71, 72, 80, 82, 83, 87, 91 | 21 |
| p4 | 93, 98, 99, 100, 101, 103, 104, 105, 108, 110, 112 | 19 |

## Inputs

- `retail/review_agent_brief.md`: what the trajectory reviewers were told (cause classes A to E, row rules).
- `checklist.md`, `retail/checklist.md`: check definitions and severities.
- `retail/PLAN.md`: the dated Deviations at the end are binding.
- Transcripts: `results/retail/trajectories/<task>_<haiku|gt>_t<k>.md`. Read every trajectory a row cites, and the successful trials of every flipped task. Turn numbers are the `[n]` markers.
- `results/retail/agent_triage.md`, `results/retail/agent_runs_summary.md`, `results/retail/haiku_pass.csv`.
- Task cards: `results/retail/task_cards/task_<id>.md` (scenario, reference actions with arguments, `nl_assertions`, `communicate_info`, reward basis).
- `tau2-bench/data/tau2/domains/retail/policy.md`; `tau2-bench/src/tau2/domains/retail/tools.py`; `tau2-bench/src/tau2/user/guidelines.py` (what the simulator is told); `tau2-bench/src/tau2/evaluator/evaluator_nl_assertions.py` (what the judge sees).
- The static log and its adversarial review: `retail/audit_log.csv`, `results/retail/skeptic_report.md`.
- Airline precedents: `results/skeptic_report_agent.md` (block 1, run rows) and `results/consistency_pass.md`.

## Scoring facts (retail)

- **Reward = DB × NL assertions.** `reward_basis` is `["DB","NL_ASSERTION"]` on 112 tasks and `["DB"]` on tasks 33 and 34. `COMMUNICATE` is never in the basis.
- **DB:** the agent's final database is compared with the database after replaying the reference actions on a fresh environment. `get_pydantic_hash` sorts dict keys and keeps list order. Any conversation that reaches the same end state passes the DB part.
- **NL assertions:** in the runs, one vote of `claude-haiku-5-5` as judge, which sees `role: content` lines only. The 3-vote re-judge is in `rejudge.csv`.
- **Ground-truth (GT) agent** (`llm_agent_gt`): it sees the reference actions, not `nl_assertions`. One trial on 112 tasks; tasks 24 and 57 have no reference actions and were skipped.
- **Simulator:** `claude-haiku-5-5`, text mode. The text-mode guidelines lack the "do not end the conversation prematurely" rule that the voice-mode guidelines carry.

## Cause classes (as the reviewers had them)

- **A, agent slip:** misreads data, states a wrong amount, picks a wrong argument, forgets a step, refuses what the policy allows, or does what the policy forbids.
- **B, simulator deviation:** see rule 1.
- **C, defensible alternative reading:** the agent's path is a correct reading of the scenario and the policy but not the reference's.
- **D, reference or scoring problem:** the reference actions, the `nl_assertions`, the scorer or the task text make a correct conversation score 0 or a wrong one score 1.
- **E, judge error:** see rule 6.

## Rules fixed for all parts

Apply these. A departure needs a stated reason in your report.

1. **5d, simulator fidelity** (block-1 rule, `results/skeptic_report_agent.md`).
   - **Counts:**
     - a fabricated fact or preference that the scenario does not contain and that bears on what the agent must do;
     - a contradiction of a scenario fact;
     - a scenario instruction withheld at its trigger (the agent asked, or the situation the scenario names occurred);
     - refusing what the scenario says the user accepts;
     - ending the conversation before the scenario's requests are done, when the scenario gives no reason to stop.
   - **Does not count:**
     - persona-scripted behaviour, including scripted escalation;
     - a choice the scenario leaves open (a scenario gap; see rule 5);
     - wording, politeness, small talk, and details with no bearing on what the agent must do.
   - 5d = 1 (medium) when any read trajectory of the task shows a counted deviation, whether or not it changed the reward. Cite the turn and the scenario sentence it departs from.
2. **Asking for a human** is a deviation only where it replaces an instruction the scenario gives for that situation.
3. **5c, a flip through the simulator.** 5c = 1 (medium) when 1 or 2 of 3 trials pass and the failing and passing trials differ in what the simulator said, while the agent behaved alike. The difference may be:
   - a deviation under rule 1: tag the note `5c-infidelity`;
   - a different choice inside a scenario gap: tag the note `5c-gap`; 5d stays 0 for it, and the gap goes under rule 5 (airline block-1 precedent: task 8 has 5c = 1 and 5d = 0);
   - an early stop or a different disclosure that the scenario does not fix: tag it `5c-gap`, and if it breaks rule 1, tag it `5c-infidelity` instead.

   Otherwise 5c = 0, with the note "agent", "judge, see 2j" or "stable".
4. **Agent refusals.**
   - Class A when `policy.md` permits the action under the facts the conversation established.
   - Class C only when a policy sentence, read plainly, supports the refusal. Quote the sentence.
   - Class D when the reference requires an action the policy forbids, or the policy requires an action the reference omits.
5. **Scenario gaps** are class D. A gap is a choice the scenario leaves open while the reference fixes it: a payment method, an item variant among those that match the stated options, the order of actions, an amount split, a yes/no the scenario never settles.
   - 4f: if the static log already carries the same mechanism on that task (4c, 4d, 2e, 2h or another static row), 4f = 0 with the note "already in <task>/<check>". Otherwise 4f = 1 medium.
   - 1e: a GT failure that runs through a gap gives 1e = 1 medium.
   - The reviewers applied this unevenly: tasks 0, 1 and 98 carry the gap under the task text only, while 15 and 100 also carry 5c or 5d (`retail/PLAN.md`, last deviation, point 3). Decide those five tasks explicitly under rules 1, 3 and 5.
6. **Judge, class E** only when the transcript satisfies the assertion in substance before the end, or the reverse: an assertion marked met that the transcript does not satisfy. Quote the assertion and the agent turn.
   - If the agent never said it, the cause is class A (an omission).
   - It is class D if the assertion asks for something the user never asked for and the policy does not require.
7. **1e severity:** high only when no policy-compliant conversation reaches the reference; medium otherwise. Classes A, B, C and E give 1e = 0, with the class in the note.
8. **One cause, one row per question.** Among the run rows, one event is not filed under both 5d and 4f/1e: fidelity and task text are exclusive. 5c answers a different question (what made the trials differ), so it may sit beside either. A static row and a run row on the same cause both stay, because they come from different methods (airline consistency pass, task 39).
9. **Severity** follows the checklists. Do not invent likelihood levels. If an issue is real but improbable, keep the checklist severity and say so in the note.
10. **Evidence** must let a stranger reproduce the verdict: the trajectory file, the turn numbers, a short quote, the ids and the amounts. Recompute every amount a row depends on.

## Also check

- **2j against the re-judge.** For every judge-only failure in your tasks (DB matched, an assertion unmet), compare the reading with the 3-vote majority in `rejudge.csv`. A disagreement is not decisive either way; say which you believe and why.
- **Open question 6 of the static review** (`results/retail/skeptic_report.md`): in p3, check the minimal-change reading of task 91 against its trajectories; in p4, the same for task 100.

## Tools and limits

- **Read-only Python:** `<system python> -I` for JSON, CSV and arithmetic.
- **Replays inside the pinned benchmark**, only if a verdict needs one (for example a claim that no compliant path reaches the reference). From `tau2-bench/`, run `uv run --no-sync python <script>`, where the script lives in your temporary folder. Allowed: environment construction through the registry, `make_tool_call` and `get_db_hash`.
- **Prohibited:** editing the clone; `uv sync`, `pip` or any install; model or API calls; network; git.
- **Temporary folder:** `<temporary folder>\skeptic_retail_<part>\`. Create files only there, and only the three outputs below. Do not modify any existing file.

## Output (part `<part>` = p1, p2, p3 or p4)

Write with Python through Bash, UTF-8, LF line endings, into your temporary folder. Append the CSV rows as each task is decided, so that the work survives an interruption.

1. `skeptic_verdicts_agent_<part>.csv`, header `task_id,check,skeptic_ok,note`.
   - One row per `defect=1` row of your tasks: `skeptic_ok` 1 (holds: the cited turns say what the row says; class, check and severity follow the rules) or 0 (does not hold, or belongs under another check or severity).
   - One row per escalation: `skeptic_ok` empty, note starting `should be defect=1 <severity>:`.
   - A re-filing (wrong check) is a 0 on the old check plus an escalation on the new one.
2. `review_agent_overrides_<part>.csv`, header `task_id,check,defect,severity,evidence,note`. One row for every value that changes: a rejection sets defect 0, and re-filings, escalations and severity changes give the corrected row. Use the same evidence standard. Rows that stay as filed need no override.
3. `skeptic_report_agent_<part>.md`:
   - a verdict table (row; holds, fails or re-filed; one line why);
   - the rules as applied, with any departure and its reason;
   - a per-trajectory table of cause classes after your pass (A to E, with the 5c tags);
   - the GT failures of your tasks by class; your unstable tasks and how many flips run through the simulator, split into infidelity and gap;
   - the 2j cross-check table;
   - what you could not verify;
   - disclosures: every file opened outside the inputs above, and every command run inside `tau2-bench/`.

If a write is refused, return the full contents of the three files in your final message, each after a line `===== FILE <name> =====`.

Write in English and in an impersonal voice: no names of people, and no mention of which model or tool wrote the review. Your final message returns:
- the counts: rows reviewed, confirmed, rejected, re-filed, escalated;
- every changed row, one line each;
- the GT failures by class and the flips through the simulator (infidelity and gap) for your tasks;
- open questions.
