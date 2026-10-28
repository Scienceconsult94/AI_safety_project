# Five-minute demo: how an agent exam fails

Audience: someone who knows what an LLM agent is but has not seen tau2-bench. Everything shown runs offline, makes no model call and finishes in about 12 seconds.

## Before the talk

- Prepare the pinned clone and its environment as `STRUCTURE.md` describes. Run the demo once to confirm it works:

  ```bash
  cd tau2-bench
  PYTHONUTF8=1 uv run --no-sync python ../scripts/demo/demo.py
  ```

- Open three files next to the terminal: `README.md` (headline tables), `retail/fig_comparison.png` (airline beside retail) and `strong_vs_weak/fig_per_task.png` (two models on the same exam).
- Use a large terminal font. Each step below runs one reproduction with `--only N`.

## Script

**0:00–0:30 — The claim.**
Agent benchmarks are exams, and their pass rates feed leaderboards and deployment decisions. This project checks the exam itself. The target is tau2-bench v2.0.0, a widely used customer-service agent benchmark: airline (all 50 tasks; 20 sampled first) and retail (all 114 tasks). The tools are a fixed checklist of 52 checks, probes with known answers, paid agent runs and an adversarial review of every finding.

**0:30–1:30 — An agent that says nothing.**
Run `--only 1`. On screen: full reward on 23 of 50 airline tasks for an empty conversation.
Say: these tasks expect a refusal or a look-up, so the database does not change and nothing is required to be said. The exam cannot tell a correct refusal from an agent that did nothing. Across the benchmark's own domains the same floor is 46% (airline), 5% (retail) and 0% (telecom): one benchmark, floors from 0 to 46%.

**1:30–2:30 — A rule only the policy text enforces.**
Run `--only 2`. On screen: retail task 72 replayed in two orders. The address change is accepted even though the order is already "pending (item modified)", and both orders end in the same database.
Say: the policy forbids any change after the items are modified. The tool tests the status by substring and lets the change through, and the scorer compares only the end state, so it cannot see the violation. 14 retail tasks behave like this.

**2:30–3:15 — A tool that stores the wrong item.**
Run `--only 3`. On screen: one call swaps four items, and three of them are stored with the price and options of a makeup kit.
Say: the loop that writes the items reuses the last variant from the validation loop. The reference's target is this corrupted order. An agent that lists the same swaps in another order reaches a different state and scores 0.

**3:15–3:45 — A task no one can pass.**
Run `--only 4`. On screen: retail task 105's only reference action is rejected (a 21.10 difference, a 17.00 gift card), while its assertion demands the exchange.
Say: to pass the hash the database must stay unchanged; to pass the assertion the exchange must happen. Both cannot hold.

**3:45–4:30 — What this does to model comparisons.**
Show `strong_vs_weak/fig_per_task.png`.
Say: the same 20 airline tasks were run with a stronger agent model. It is ahead on 6 tasks and behind on 1, but the difference is not significant (p = 0.125). Nine of the 20 tasks tie both models by construction: 7 pass for doing nothing and 2 cannot be passed. Correcting one wrong reference answer widens the gap (p = 0.039, before correcting for the three comparisons). In retail, the user simulator, not the agent, explains 12 of the 23 failures of an agent that sees the answer key.

**4:30–5:00 — The point.**
A pass rate measures the agent, the user simulator and the exam together. The exam has to be validated as an instrument before its numbers are read. Every number here is rebuilt by script from recorded runs, and 16 issue drafts with reproductions are prepared for the maintainers.

## Likely questions

- **Isn't the pass for doing nothing documented as intended?** The documentation calls the refusal outcome intended. The finding is about resolution: the exam cannot distinguish a refusal from inaction. Block 2 shows a stricter protocol in which an empty conversation scores 0 on all 50 airline tasks.
- **How solid are the defect counts?** In retail, every defect row went through an adversarial review: the rows from reading and probes first, the rows from the agent runs later, in a second review in four parts. A second model reader re-labelled 12 tasks blind and agreed with the first reviewers on 97 of 98 labels; the adversarial review settled the one difference in favour of the blind reader. With the 6 tasks that pass for doing nothing counted on their own line, 38 of 114 tasks are defective from reading and probes, and 61 counting the agent runs.
- **Is the tool bug fixed upstream?** Not at the pinned commit. The fix takes a few lines; the patch and its description are drafted in `upstream/` and have not been filed.
- **Does this generalize beyond tau2-bench?** See the external null-agent table in `results/null_agent/external.md`.
- **What did it cost?** About $28 of API calls in total (`cost.md`).

## If the live run fails

Expected output of `demo.py`, shortened:

```text
1. Airline: what does an agent get for saying nothing?
  full reward on 23 of 50 tasks: 0, 1, 2, 4, 5, 6, 9, 10, 13, 26, 27, 28, 31, 34, 36, 38, 41, 43, 45, 46, 47, 48, 49

2. Retail task 72: the order of changes the policy forbids scores the same
  reference order (address first, then items):
    modify_pending_order_address     order status before: 'pending'                  -> accepted
    modify_pending_order_items       order status before: 'pending'                  -> accepted
  forbidden order (items first, then address):
    modify_pending_order_items       order status before: 'pending'                  -> accepted
    modify_pending_order_address     order status before: 'pending (item modified)'  -> accepted
  final database identical: True

3. Retail task 20: the tool stores the wrong item
  requested variant  product          catalogue price  stored price
  4579334072         Water Bottle               54.85        261.11   <- wrong
  1151293680         Mechanical Keybo          272.33        261.11   <- wrong
  4107812777         Running Shoes             155.33        261.11   <- wrong
  2882812427         Makeup Kit                261.11        261.11
  3 of 4 items carry another variant's price and options.

4. Retail task 105: a task no conversation can pass
  price difference to pay: 21.10; gift card balance: 17.00
  reference action rejected: Insufficient gift card balance to pay for the price difference
  scored target state equals the starting state: True
  the task's assertion: ['Agent should exchange both tea kettles (same style) to the items requested']
```
