# PE6201 A2: Applied AI System

**Team B-1 | Problem A: Health-insurance claim first response**

## 1. Why an agent

We selected rung 7 to test whether model-directed retrieval can handle claims with different evidence requirements. A single prompt must either guess from the narrative or receive all records upfront. A fixed chain can retrieve reliable facts, but needs explicit branches for policy eligibility, duplicate history, missing documents and pre-authorisation. Routing selects a lane; parallelisation saves turns; neither alone chooses subsequent lookups from observations. Orchestrator-workers would distribute work without removing those dependencies. An evaluator-optimiser can revise wording but cannot recover a policy fact it has not retrieved.

A deterministic workflow could implement this finite routing table and may be the safer production choice. Our agent is therefore an experiment in adaptive retrieval, not proof that fixed workflows are inadequate. It chooses the next lookup, while tools and code retain responsibility for objective rules and action authorization. Read-only retrieval becomes an acting agent at `issue_decision_letter`, the irreversible boundary. We require confirmation there rather than allowing autonomous decisions.

The first diagnostic is machine-speed ground truth. Policy records can contradict an asserted coverage date or remaining limit; procedure tables, pre-authorisations and prior decisions can contradict the narrative. The second is reliability over a multi-step trajectory. The selected DeepSeek v2 battery passed 55/60 trials with median four tool turns, giving the diagnostic proxy `s = (55/60)^(1/4) = 0.9785`. This is not a measured probability for every individual step: dependencies, parallel calls and unequal failure risks violate that interpretation.

A good run follows Appendix A's routing, names the cause and supporting record, resolves all required lines and totals, and requests evidence rather than inventing it. It records one confirmed ordinary decision, or zero writes for hostile-input escalation. These criteria are stricter than matching a final label.

## 2. The tool layer

Seven tools expose only relevant records: `get_claim`, `get_policy_context`, `review_claim_line`, `get_preauthorisation`, `get_hospital_status`, `find_prior_decision` and `issue_decision_letter`. We tried not adding separate member and document-rule lookups because the policy join and line review already return their decision-relevant facts. Web search adds no necessary evidence to this fixture-backed task.

The scaffold's same-turn policy and coverage calls contained a dependency: coverage needed the policy ID returned by the policy lookup. Our line-review signature instead takes the already retrieved member ID and resolves the policy internally. It also returns required-document status. These interface changes remove an unavailable argument and make silent approval with missing documentation harder.

Calls can share a turn only when neither needs the other's output. The scripted policy retrieves the claim, checks eligibility and duplicate history before line work, groups independent hospital and line checks, then retrieves any required pre-authorisation. Live trajectories remain model-selected. The gated write must be alone in its batch and bound to the current claim; after a successful write, only a final response is permitted. Parameter validation precedes confirmation, and revalidation precedes persistence.

| Measured lever | Before | After |
|---|---:|---:|
| Candidate tool block | 9 tools; 1,817 estimated tokens | 7 tools; 1,571 estimated tokens |
| Sequential versus parallel, 40 scripted cases | 251 turns; 911,506 input tokens | 157 turns; 609,144 input tokens |
| Scripted cost for that comparison | $0.0995 | $0.0688 |
| Missing-document observation probe | 115 estimated tokens, v1 | 56 estimated tokens, v2 |

Both execution modes passed 40/40. Token estimates use the scripted estimator, not API billing. Delaying line review until early checks pass limits unnecessary parallel work.

The ACI experiment changes only `review_claim_line`'s descriptor and return shape. Other tool descriptors remain identical. Whole-prompt size rises from 9,976 characters (2,494 estimated tokens) to 10,414 (2,603). Gemini v1 passed 33/60 and v2 20/60; their provider bills were $0.07430 and $0.07534. Across all observations, estimated mean tokens per call fell from 82.37 to 63.42, but reliability did not improve. This result does not justify deploying the rewrite on Gemini, nor does one battery isolate every stochastic difference as an interface effect.

## 3. What the evidence showed

The evaluation contains 40 claims: 15 supplied and 25 additions. Thirty ordinary cases receive one trial; ten negative cases receive three, producing 60 trials per battery. Frozen checks grade decisions, triggers, missing items, totals, line evidence and action integrity. Reason quality and evidential sufficiency require separate human judgement and are not included in the machine-pass claim below.

| Model | Prompt | Strict passes | Negative passes | Median turns | Provider bill |
|---|---|---:|---:|---:|---:|
| DeepSeek V3.2 | v2 | 55/60 | 29/30 | 4 | $0.09518 |
| Llama 4 Maverick | v2 | 53/60 | 27/30 | 6 | $0.22221 |
| Claude Haiku 4.5 | v2 | 35/60 | 18/30 | 5 | $1.23503 |
| Qwen3 30B A3B Instruct | v2 | 33/60 | 21/30 | 6 | $0.07739 |
| Gemini 2.5 Flash Lite | v2 | 20/60 | 15/30 | 5 | $0.07534 |
| Gemini 2.5 Flash Lite | v1 | 33/60 | 18/30 | 5 | $0.07430 |

All selected runs use freeze `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`. DeepSeek's five failures were budget-ceiling stops; Llama had six such stops and one invalid action batch. Qwen had nineteen budget stops, while Gemini v2 also struggled with duplicate calls and action batching. None hit the eight-tool-turn cap. Thus token-budget and execution-contract failures, not only business reasoning, shape these scores.

Claude's selected run is a complete repeat after 23 HTTP 429 failures in its initial second-round battery. An authorized replacement account/key changed access conditions, not code, cases or prompt. Both runs are retained, but no trial rows are mixed. The selected result is 35/60 versus the initial 23/60; stochastic variation prevents attributing the gain solely to the account change. Earlier first-round batteries remain historical evidence, not part of this comparison.

## 4. What it costs

We use escalation cost, not retry-until-success cost. Layer 1 prices measured tokens at the frozen catalogue rates, with provider bills reported separately. Layer 2 is `(1 - p) × $7.60`: twelve minutes at $38 per assessor-hour. Layer 3 assumes $400 monthly for monitoring, evaluation review and lightweight logging. Monthly volume is 8,000 claims.

Cost calculations average repeated trials within each case, then weight the 40 cases equally. This avoids silently treating negatives as half of operational volume. Equal case weighting is still a scenario assumption, not an observed insurer distribution; headline trial pass rates remain unchanged.

| Model, v2 | Case-balanced success | Variable/task | Fallback/task | Combined/task | Monthly including fixed cost |
|---|---:|---:|---:|---:|---:|
| DeepSeek | 89.17% | $0.004250 | $0.82333 | $0.82758 | $7,020.66 |
| Llama | 87.50% | $0.003723 | $0.95000 | $0.95372 | $8,029.79 |
| Claude | 57.50% | $0.022176 | $3.23000 | $3.25218 | $26,417.41 |
| Qwen | 47.50% | $0.001019 | $3.99000 | $3.99102 | $32,328.15 |
| Gemini | 25.00% | $0.002077 | $5.70000 | $5.70208 | $46,016.62 |

The four levers are tool-block size, turns, observation size and success rate. The first three reduce model traffic, but fallback dominates: DeepSeek's expected fallback alone is about $0.82 per claim against under half a cent of variable cost. Cheap tokens cannot compensate for Qwen's failures.

Against DeepSeek, Qwen needs case-balanced success of 89.12% to break even, using `1 - (E - C) / F`; it measured 47.50%. DeepSeek is therefore our provisional selection within this system, not a production approval. Its sensitivity grid crosses success ±10 percentage points with failure cost at 75–125%, yielding monthly estimates of approximately $814–$16,267 at the fixed $400 baseline. This range is a scenario analysis, not a confidence interval. The small observed lead over Llama is not robust evidence of a population ranking when model success rates can vary independently.

Shipped limits are eight tool turns, 25,000 tokens per run, a $3 member A2 allowance and $25 per key owner per month, with declared spend checked before execution. Token guards check both consumption and projected next-request usage; stopping can truncate legitimate work. Account-level limits and repeated experimental spending must be reconciled separately from per-task operating costs.

## 5. The two failures

The loop experiment uses one repeated-action trajectory with and without de-duplication. The guard stops at three turns. Removing only that guard permits seven turns, thirteen calls and 29,154 estimated input tokens at $0.003307, despite reaching the correct decision. The normal trajectory takes five turns, nine calls and 20,278 input tokens at $0.002336. Outcome accuracy alone misses the waste. De-duplication belongs in code: prompt instructions cannot guarantee memory, while a step cap catches damage later. Restored scripted evaluation passes 60/60, with median four and worst five turns, supporting headroom below the eight-turn cap without proving live adequacy.

The interface experiment deletes the 45378 required-document rule while keeping the reactive backend. CLM-8901 then incorrectly approves $1,150 instead of requesting an itemised bill. Both conditions take four turns; estimated costs are $0.000960 faulty and $0.000920 working. Checks detect the incorrect decision, missing item and line disposition. Restoring the rule recovers the request and 60/60 scripted passes. The fix belongs at the interface because prompt wording and loop controls cannot reconstruct a missing authoritative rule. Both demonstrations reproduce without a paid model.

## 6. What we would not deploy

Synthetic fixtures, narrow hostile-input patterns and unfinished human judgement do not establish production safety. Matched hostile narratives are blocked before returning them to the model; those passes measure the shipped guard, not the model's independent injection resistance. Identity, privacy, policy updates, adversarial paraphrases and real latency remain untested. Confirmation and local audit writes are the only autonomy level we defend.

A second reviewing agent might detect unsupported explanations, but would add tokens, latency and another fallible decision-maker. We retained a single agent because fixed-field validation provides more direct controls. We would require independent security testing, monitored human overrides and a controlled pilot; stable structured rules could instead favour a deterministic workflow.

## AI assistance and sources

AI assisted implementation, drafting, debugging and mechanical verification. The team owns review of evidence, live-run execution, interpretation and final approval. Primary sources are the course brief, FAQ and updates, supplied scaffold, Appendix A and Weeks 4–6 materials. Numerical evidence is in `artifacts/`, `results/live/` and the archived runs; human-review completion is tracked separately.
