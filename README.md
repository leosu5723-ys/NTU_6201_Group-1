# PE6201 A2: Health-Insurance Claim First Response

Team B-1 implementation of Problem A. This repository contains one hand-written ReAct agent, a bounded tool layer over local fixture data, code-level guardrails, a reproducible scripted backend, an evaluation harness, failure reproductions and cost-analysis utilities.

The harness is the primary deliverable. The submitted default uses no network and no API key.

## Reproduce the scripted result

Requirements: Python 3.10 or newer. No third-party packages are required.

```bash
python3 A2_reference_data/check_my_data.py
python3 run_eval.py
python3 -m unittest discover -s tests -v
```

The default command runs 40 cases and 60 trials:

- 30 ordinary cases, one trial each
- 10 negative cases, three trials each

It writes the complete record to `results/scripted/results.json`.

Run one case with its tool turns shown:

```bash
python3 run_eval.py CLM-8842
```

Reproduce the other required evidence:

```bash
python3 run_eval.py --guardrails
python3 run_eval.py --parallel
python3 run_eval.py --failures
python3 run_eval.py --prompt --prompt-version v1
python3 run_eval.py --prompt --prompt-version v2
```

These write deterministic files under `artifacts/`.

## Problem and outcomes

The agent receives a claim ID and must retrieve evidence before reaching one of three outcomes:

- `approve_in_principle`
- `request_document`
- `escalate`

A partly payable claim remains an approval in principle, with one disposition per line and separate approved and refused totals. Missing documents and invalid pre-authorisations produce a specific request. Lapsed or out-of-date policies, claims above the remaining annual limit, duplicate prior decisions and instruction-like member narratives produce an escalation.

## Tool dependency rule

Calls share a turn only when neither requires the other's output.

1. `get_claim` runs alone.
2. Policy eligibility and duplicate history run together because both can end the run before line review.
3. If they pass, hospital status and all per-line reviews run together.
4. Pre-authorisation lookups run only for eligible lines that require them.
5. The simulated decision letter is the last call and sits behind the confirmation gate.

This safe grouping deliberately uses five turns for the worked partly payable claim instead of the scaffold's four. It preserves early exit and avoids the scaffold's hidden same-turn dependency on a policy ID that had not yet been returned.

## Tool set

- `get_claim`
- `get_policy_context`
- `review_claim_line`
- `get_preauthorisation`
- `get_hospital_status`
- `find_prior_decision`
- `issue_decision_letter`

Every callable tool has a complete descriptor with its signature, purpose, timing, inputs, bounded return, failure meaning and irreversible status. `review_claim_line` includes required-document status because that system-of-record fact is necessary for the routing rule and was not exposed by the starter tool layer.

## Guardrails

The code layer implements:

- Step cap
- Token budget ceiling
- Canonical action de-duplication
- Narrow hostile-input detection
- `suggest`, `confirm` and `act` autonomy settings
- Decision-action integrity checks

The selected setting is `confirm`. Only `issue_decision_letter` is irreversible. It appends one structured local JSONL record after confirmation for every ordinary approval, document request or business escalation. Hostile-input safety escalation fails closed without calling it.

`artifacts/guardrail_checklist.json` contains ten deterministic cases. Three use hostile member text. The hostile-text patterns are intentionally described as a limited control, not as a complete solution to prompt injection.

## Evaluation data

The 15 supplied claims and labels are preserved. Twenty-five new claims are declared in the `EXTRA_CLAIMS` block of `A2_reference_data/make_fixtures_A.py`. Their candidate labels are recorded in `design/additional_cases_A.json` and `expected_outcomes_A.json`. Member-authored contracts and review corrections must be merged before the final experimental freeze.

Regenerate and validate after any data change:

```bash
python3 A2_reference_data/make_fixtures_A.py
python3 A2_reference_data/check_my_data.py
```

Do not edit generated JSON rows or any supplied row directly.

## Scripted and live backends

`BACKEND = "scripted"` is committed as the default. It replays the fixed trajectories in `fixtures/scripted_trajectories_A.json`. `script_builder.py` regenerates those trajectories from fixture facts without reading the answer key.

The live backend is isolated in `backends.py`. It sends the case ID, preserves raw API responses, reads token counts from the API usage block and records request IDs and latency. API keys are read only from `OPENROUTER_API_KEY`.

A live command is a dry run unless `--execute` is explicitly present:

```bash
python3 live_battery.py \
  --model google/gemini-2.5-flash-lite \
  --prompt-version v2
```

After the repository is frozen at a clean commit, the assigned member can execute:

```bash
export OPENROUTER_API_KEY='...'
python3 live_battery.py \
  --model google/gemini-2.5-flash-lite \
  --prompt-version v2 \
  --spent-to-date 0.00 \
  --monthly-spent-to-date 0.00 \
  --execute
```

Never commit a key. Replace both `0.00` values with that member's actual A2 and calendar-month spend before the run. Preflight blocks a projected total above either the US$3 A2 battery ceiling or the US$25 monthly per-member ceiling. Final batteries refuse source changes but allow resumable generated files under `results/live/`, so all six runs can use the same clean commit. Each `(case_id, trial)` is checkpointed atomically and a changed commit, prompt or data hash is rejected on resume. A labelled smoke test may use `--smoke CASE_ID --allow-dirty` and must not be merged into measured results. For scoring only, the battery harness supplies an explicit positive confirmation callback so an approval can exercise the simulated local JSONL write. A direct live `run_case` without that callback remains fail-closed at the confirmation gate.

Selected models and checked prices are in `config/model_catalog.json`. Availability and prices must be checked again on the actual run date.

## Required experiments

### Sequential versus parallel

`parallel_experiment.py` splits only same-turn independent calls. Both modes run the same 40 cases with one deterministic trial each. The experimental cap is held above all legitimate sequential paths so call grouping is the only variable. Results are in `artifacts/parallel_experiment.json`.

### Prompt v1 versus v2

The controlled comparison uses Gemini 2.5 Flash Lite for both versions. The only changed component is the `review_claim_line` agent-computer interface. v1 uses an underspecified descriptor and a large nested return. v2 uses the complete six-field descriptor and a smaller, typed return with explicit document status. Model, cases, routing, guardrails and all other code remain fixed.

### Two failures

`failure_experiments.py` reproduces:

1. A loop-control failure after deleting action de-duplication. The run still reaches the correct decision but uses more turns, tool calls, tokens and cost.
2. A tool-interface failure after deleting required-document fields. The agent incorrectly approves a claim that should request an itemised bill.

The complete 60-trial scripted set passes again after each deleted component is restored.

## Repository map

```text
agent.py                      hand-written ReAct loop and instrumentation
backends.py                   fixed scripted replay and OpenRouter live boundary
tools.py                      Problem A tools and descriptors
guardrails.py                 code-level controls
harness.py                    cases, trials, code checks and judgement queue
prompt.py                     frozen v1 and v2 prompt artifacts
script_builder.py             deterministic scripted-trajectory generator
parallel_experiment.py        D2(c) comparison
failure_experiments.py        D7 reproductions
cost_model.py                 three-layer cost and break-even calculations
live_battery.py               paid-run preflight and runner
live_analysis.py              frozen battery validation and live cost analysis
A2_reference_data/            generators, JSON records, checker and answer key
fixtures/                     committed scripted trajectories
design/                       label-first case plan
docs/                         requirements and architecture decisions
artifacts/                    deterministic result tables
results/                      scripted and later live run evidence
tests/                        standard-library test suite
report/                       report work in progress
```

Key review documents include `design/D0_PREBUILD_CONTRACT.md`, `docs/tool_selection_score.md`, `docs/cost_assumptions.md`, `SOURCES.md` and `review/SUBMISSION_MANIFEST.md`.

## Evidence status

The scripted harness, data integrity, guardrail checklist, parallel comparison and both failure reproductions are complete and reproducible. All six first-round measured batteries are preserved unchanged under `results/round1/`, with a SHA-256 manifest. They belong to experiment `42253ad28fc58b36b9014808f9d8e3fd523c01ed`, not to the revised runtime. Round-two outputs belong under `results/live/` and must not be mixed with round one.

The selected Round 2 set is complete at experiment freeze `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`: five v2 model batteries and one Gemini v1 control. See `review/ROUND2_INTEGRATION_SUMMARY.md` and `artifacts/live_analysis_round2.json`. Scripted human judgement is 10/10 complete; calibrated selected live reviews are in `review/round2_judgement/calibrated/`. Final submission status is maintained in `review/SUBMISSION_MANIFEST.md`. The report and cost conclusions are populated; the signed self-appraisal, edited video, final package approval and upload remain separate release gates. Historical run instructions do not request another paid run.
