# Code Walkthrough for Team Review

Every member should be able to explain the purpose of each block below. The expectation is functional understanding, not memorising syntax.

## `config.py`

This is the vendor-neutral configuration boundary. The submitted defaults are Problem A, scripted backend, v2 prompt and `confirm` autonomy. The API key comes only from the environment. The model string and token prices are changed by the controlled live runner.

**Be able to explain:** Why the default must remain scripted; why model selection should not leak into the agent or tools; why an API key must never be committed.

## `agent.py`

`run_case` creates fresh guardrails, transcript, counters and a decision log for one isolated claim. Each loop iteration asks the backend for the next move, records API usage, checks the token budget, validates one or more calls, executes them and appends observations. It stops on a final answer or a loud guardrail event.

The loop checks member-supplied narrative immediately after `get_claim`. Every ordinary business outcome passes through the autonomy gate and records exactly one first response. Hostile narrative instructions fail closed before the write, so that security escalation has zero actions.

**Be able to explain:** Why a final answer is not counted as a tool turn; why several independent calls can share one turn; why case state cannot be shared across runs.

## `tools.py`

Tools are bounded interfaces to fixture systems of record. The model never sees the JSON files directly.

- `get_claim`: returns the incoming claim.
- `get_policy_context`: exposes status, coverage dates, remaining limit and boundary booleans.
- `review_claim_line`: resolves one procedure against policy exclusions, pre-authorisation requirements and document rules.
- `get_preauthorisation`: distinguishes valid, expired, not-yet-valid and missing evidence.
- `get_hospital_status`: returns panel status.
- `find_prior_decision`: matches all four duplicate facts.
- `issue_decision_letter`: validates every line and total, checks the gate and appends one local record.

**Be able to explain:** Why an excluded line does not escalate the whole claim; why `review_claim_line` accepts `member_id`; why `None` from pre-authorisation was replaced by an explicit status; why the action validates totals again.

## `guardrails.py`

The code layer contains the turn cap, token ceiling, canonical duplicate-action check, narrow hostile-input detector and autonomy gate. Stops are exceptions with named reasons, then converted into explicit escalation records by the agent.

**Be able to explain:** Why these controls live in code instead of the prompt; why the hostile detector is useful but incomplete; why `confirm` gates the action rather than the entire agent.

## `backends.py`

The scripted backend replays committed moves and estimates tokens deterministically. The live backend sends the same system prompt plus the claim ID to OpenRouter, parses JSON moves, preserves raw responses and reads measured usage from the API response.

Only `_live_call` knows OpenRouter exists.

**Be able to explain:** Why scripted results test our code but not model quality; why raw usage must replace token estimates in the cost model; why malformed JSON becomes a recorded failure.

## `prompt.py`

The prompt contains three blocks: fixed routing rules, tool descriptors and the JSON move schema. v1 has vague descriptors. v2 includes signatures, timing, bounded returns, failure meanings and irreversible status.

**Be able to explain:** Why the answer key is never in the prompt; why v1 and v2 must run on the same model; why a larger v2 prompt has to earn its repeated token cost.

## `harness.py`

The harness loads frozen cases and labels, applies one trial to ordinary cases and three to negatives, invokes isolated runs and performs code checks. Ten representative cases also enter a judgement queue.

**Be able to explain:** Why the exact decision, trigger, missing item and action count are code checks; why reasons require judgement; why a pass rate without a trial count is not a measurement.

## `script_builder.py`

This development tool compiles fixed deterministic trajectories from fixture facts without reading the answer key. The resulting JSON is committed and replayed by the scripted backend.

**Be able to explain:** Why this does not measure model performance; why early policy or duplicate triggers stop before line review; why the generated scripts are committed rather than rebuilt invisibly during marking.

## Experiment modules

- `guardrail_harness.py`: ten deterministic code-control cases.
- `parallel_experiment.py`: same cases and outcomes, with independent calls grouped or split.
- `failure_experiments.py`: deletes one working component at a time and measures the effect.
- `prompt_experiment.py`: freezes exact v1 and v2 text and hashes.
- `live_battery.py`: dry-run preflight and explicit paid execution from a clean commit.
- `cost_model.py`: token cost, expected fallback, fixed cost, sensitivity and break-even.
- `reliability.py`: computes implied per-step reliability from whole-run pass rate and median turns.

## Data files

`make_fixtures_A.py` is the reproducible source. Generated files under `data_A/` are committed for readability. `expected_outcomes_A.json` is the independent truth set. `check_my_data.py` proves that shipped rows were not changed, IDs resolve and cases and labels match.

**Be able to explain:** Why labels are written before model output; why each case starts with the original `used_to_date`; why 40 cases with 10 negatives produce 60 trials per model.

## Questions every member should answer

1. What fact causes the agent to take another turn?
2. Which calls are safe to run together, and why?
3. What is the first irreversible action?
4. What is the difference between a negative evaluation case and a guardrail case?
5. Why can the scripted backend score 100% without proving that a live model is good?
6. Which measurements are estimates and which are API-measured?
7. What failure does the required-document return field prevent?
8. Why might the cheapest model still be the most expensive system to operate?
