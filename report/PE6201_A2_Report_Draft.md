# PE6201 A2: Applied AI System

**Team B-1 | Problem A: Health-insurance claim first response**

> **Draft status:** Sections containing `[LIVE RESULT REQUIRED]` must be completed only from the frozen live battery. They are not submission-ready placeholders.

## 1. Why an agent

Problem A sits on rung 7 of the Class 4 ladder because the claim determines both the sequence and number of retrieval steps. A single call would either guess from the member narrative or require every policy, procedure and history record to be placed in context. A fixed prompt chain would perform the same checks on every claim, including line-level work after a lapsed policy had already made escalation mandatory. Routing and parallelisation reduce cost but do not decide whether a particular line needs pre-authorisation. An evaluator-optimiser could improve wording, but it would not obtain missing ground truth. Our ReAct loop instead chooses its next lookup from tool observations and can stop, branch or query another record.

| Rung | What it would deliver here | Why it is not the complete instrument |
|---|---|---|
| 1. Single call | One fixed response | Either guesses or receives every record up front |
| 2. Prompt chain | Fixed checks with review points | Runs the same subtasks on every claim |
| 3. Routing | Selects a known lane | Does not decide later lookups from observations |
| 4. Parallelisation | Collapses independent checks | Saves turns but does not choose the path |
| 5. Orchestrator-workers | Splits work at runtime | Adds workers but not the evidence-driven gated loop we need |
| 6. Evaluator-optimiser | Revises against stated criteria | Cannot retrieve a missing policy fact |
| 7. Agent | Chooses, repeats and stops retrieval at runtime | Selected, with explicit caps and confirmation |

This is not a claim that an agent is always the production answer. The current routing table is structured enough that a deterministic workflow could be safer if it remained stable. We use an agent here to test adaptive retrieval and variable trajectories, while keeping the external action behind confirmation. Read-only model-directed lookups are agentic retrieval; the governance cliff into an acting agent is `issue_decision_letter`, our first irreversible action. If the records became subjective, slow to update or impossible to verify, the ground-truth test would fail and we would move down the ladder to a workflow with a human gate.

The loop receives objective correction within seconds. Policy status, coverage dates and remaining limit come from the policy record. Procedure, exclusion and document requirements come from reference tables. Pre-authorisations and prior decisions provide additional machine-speed checks. Before implementation, we defined a good run as follows:

1. It names the actual cause and traces it to a record.
2. It follows Appendix A's fixed routing rule.
3. It resolves every claim line and reconciles both totals.
4. It asks or escalates rather than inventing missing evidence.
5. It executes the gated action at most once and records turns, tokens, cost and guardrail events.

The final v2 battery measured an end-to-end pass rate of **[LIVE P AND TRIAL COUNT REQUIRED]** with median **[LIVE T REQUIRED]** turns. This implies per-step reliability of **[CALCULATE s = P^(1/T) AFTER LIVE RUN]**. We will use this as a diagnostic rather than a physical constant because steps are dependent and some tool boundaries are more error-prone than others.

## 2. The tool layer

We shipped seven tools. `get_claim` is the entry point. `get_policy_context` exposes status, policy dates, remaining limit and explicit boundary checks. `review_claim_line` returns the exclusion, pre-authorisation and required-document facts for one line. `get_preauthorisation` distinguishes valid, expired, not-yet-valid and missing evidence. `get_hospital_status` records the payment basis. `find_prior_decision` matches member, hospital, service date and complete lines. `issue_decision_letter` is the only write and records each supported ordinary first response after confirmation.

We first tried not adding separate member and document tools. A member row contains no decision fact beyond its policy ID, so `get_policy_context` performs that join. Document rules belong to line resolution, so `review_claim_line` returns them with the other bounded line facts. This produced a shorter and less confusable interface than separate lookups. We also omitted web search because no task fails without it.

The scaffold placed `lookup_policy(member_id)` and `check_coverage(code, policy_id)` in the same turn even though the first call produces the policy ID required by the second. Its scripted example could hard-code that value, but a live model could not know it. We changed the line-review signature to accept the already known `member_id` and resolve the policy internally. We also added the document status absent from the starter tool set. These are poka-yoke changes: the first removes an impossible same-turn dependency, and the second makes silent approval without a required document harder.

Our dependency rule is that calls share a turn only when neither requires the other's output. Turn 1 retrieves the claim. Turn 2 checks policy eligibility and duplicate history because both can end the run before line review. If they pass, hospital status and all per-line reviews run together. Only lines marked as requiring pre-authorisation create another lookup. The decision write comes last.

Across 40 scripted cases, parallel execution preserved 40/40 code-check passes while reducing total turns from 251 to 157. Estimated input tokens fell from 742,622 to 495,381 and estimated scripted cost from US$0.0826 to US$0.0574. These are deterministic scaffold estimates, not live billing evidence. The main limit is that parallel calls may perform work that a sequential observation would have made unnecessary, so we delay line review until the early escalation checks pass.

The six non-selected tool descriptors are byte-identical across the ACI comparison. v1 uses only an underspecified `review_claim_line` descriptor and its raw nested policy/document return; its whole prompt is 7,630 characters, approximately 1,907 tokens. v2 changes that selected descriptor to the complete six-field form and pairs it with the bounded return, making the whole prompt 8,068 characters, approximately 2,017 tokens. For the missing-document probe, the return contracts shrink from 463 characters (about 115 tokens) to 227 (about 56). Thus the one selected ACI changes together while the model, cases, routing, guardrails, the other six descriptors and the rest of the code stay fixed. On Gemini 2.5 Flash Lite, v1 achieved **[LIVE V1 RESULT REQUIRED]** and v2 achieved **[LIVE V2 RESULT REQUIRED]** over 60 trials each. Their measured live costs were **[LIVE COMPARISON REQUIRED]**.

Before the seven-tool design was selected, the candidate block also contained separate `lookup_member` and `get_required_document_rule` calls. They duplicated facts already returned by `get_policy_context` and `review_claim_line`. The frozen nine-tool block measured 6,576 characters (about 1,644 tokens); the selected seven-tool block measures 5,593 characters (about 1,398), saving an estimated 246 standing tokens per model request while removing two confusable calls.

## 3. What the evidence showed

The frozen evaluation set contains 40 claims: all 15 supplied records plus 25 additions. Thirty cases are approvals and ten are negative decisions. The negatives receive three trials, producing 60 trials per model. Labels were derived from Appendix A before model output was viewed. Code checks compare the decision, escalation trigger, exact missing item and gated-action count. A separate judgement queue asks whether each explanation and evidence trail satisfies the case-specific `must_record` items.

| Model | Prompt | Trials | Overall pass | Negative pass | Median turns | Live cost |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 2.5 Flash Lite | v2 | [LIVE] | [LIVE] | [LIVE] | [LIVE] | [LIVE] |
| Qwen3 30B A3B Instruct | v2 | [LIVE] | [LIVE] | [LIVE] | [LIVE] | [LIVE] |
| Claude Haiku 4.5 | v2 | [LIVE] | [LIVE] | [LIVE] | [LIVE] | [LIVE] |
| Llama 4 Maverick | v2 | [LIVE] | [LIVE] | [LIVE] | [LIVE] | [LIVE] |
| DeepSeek V3.2 | v2 | [LIVE] | [LIVE] | [LIVE] | [LIVE] | [LIVE] |

**[LIVE RESULT REQUIRED: discuss the cheapest model that met the bar, the most expensive model that did not earn its price, and the negative families that separated them. Do not write this before the raw runs exist.]**

## 4. What it costs

We use the Class 5 escalation model rather than dividing by success rate. A failed first response goes to a human assessor rather than being retried until the model succeeds. The official 60-trial pass rate still reports all repeated negative runs. Cost-to-serve first averages repeated trials within each case, then gives all 40 cases equal weight. This avoids treating ten negative cases as half of production volume, although the equal-case mix remains an evaluation proxy rather than a measured insurer distribution. Layer 1 uses provider-billed cost when available and reconciles it against token-count list price. Layer 2 is `(1 - success rate) × US$7.60`, based on a claims assessor earning US$38 per hour and spending 12 minutes on an escalation. Layer 3 uses a stated US$400 monthly baseline: eight hours of monitoring and maintenance, two hours of evaluation review at the same labour rate, and US$20 for lightweight logging infrastructure. Monthly volume is 8,000 claims. The fixed hours are our assumptions and are tested from US$200 to US$800. Each member's live-run CLI also enforces the brief's US$3 A2 battery ceiling and requires spend-to-date input before execution.

| Model | Variable cost/task | Expected fallback/task | Cost to serve/task | Monthly total |
|---|---:|---:|---:|---:|
| [LIVE MODEL ROWS REQUIRED] | | | | |

The four measured levers were the tool block, turn count, observation size and success rate. Parallel grouping reduced the turn term without removing observations. The v1 to v2 experiment tests whether a larger but safer interface earns its repeated prompt cost. The live pass rate sets expected fallback, which is likely to dominate token price because one failure costs US$7.60. The shipped experiment caps are 8 turns and 25,000 total tokens per run, US$3 per member for the A2 battery, and US$25 per API-key owner per calendar month; the CLI requires both spend-to-date values and checks them before execution. **[LIVE RESULT REQUIRED: identify the dominant lever from measured values.]**

We will show success rate at minus ten points, measured value and plus ten points, crossed with failure cost at 75%, 100% and 125% of the default. For the cheapest and selected higher-cost models, the break-even success rate is `1 - (E - C) / F`, where `C` is the cheap model's variable cost, `E` is the expensive model's measured cost to serve and `F` is US$7.60. The resulting deployment recommendation remains **[LIVE RESULT REQUIRED]** across **[STATE WHETHER THE SENSITIVITY RANGE CHANGES IT]**.

## 5. The two failures

The loop-control experiment records three conditions. The normal working claim passed in 5 turns, 9 tool calls, 16,760 estimated input tokens and US$0.001984. Under one fixed repeated-action trajectory, the guard stopped loudly after 3 turns with `duplicate_action`; deleting only de-duplication allowed the same fault to continue for 7 turns and 13 calls, consuming 24,461 input tokens and US$0.002837 before returning the correct decision. A case-level pass alone would therefore miss the loop and its 43% higher cost than the normal run. Across all legitimate restored trajectories, pass rate was 60/60, median was 4 turns, the worst was 5, and no run hit the 8-turn cap. The fix belongs in code because a prompt cannot reliably remember for the model, while the cap only bounds the damage later.

The second experiment removed the 45378 required-document rule from `review_claim_line` while keeping the same reactive backend. CLM-8901 should request an itemised bill. With the faulty interface, both the model-facing observation and the trusted action-boundary check saw an incorrect “no document required” fact, so the run approved US$1,150 in 4 turns at US$0.000960 instead of recording the correct document request in 4 turns at US$0.000920. The code check caught the wrong decision, missing item and line disposition. Restoring the rule recovered the request and the full set returned to 60/60. The fix belongs at the interface because neither prompt wording nor loop controls can recreate a missing system-of-record rule.

## 6. What we would not deploy

This is a fixture-backed teaching system, not an insurance product. Its policy data is synthetic, its hostile-input detector covers named patterns rather than every possible attack, and its judgement checks still require human review. We have not tested policy updates, identity verification, privacy controls, adversarial paraphrases, provider outages or real operational latency. `confirm` is therefore the strongest autonomy setting we would defend. Ordinary approvals, requests and business escalations create only a confirmed local audit record; hostile-input escalation fails closed before the write.

A second reviewing agent might catch an unsupported reason or incomplete line disposition. It would also add another model, another prompt, more tokens, another failure surface and a harder attribution problem when the two agents disagree. We stayed with one agent because the code checks and confirmation gate cover the fixed high-risk fields more directly. Before deployment, we would prefer deterministic validation of totals and required fields, independent security testing, monitored human overrides and a controlled pilot. If the insurer's rules remain fully structured, we would also reconsider whether a deterministic workflow is safer than continuing to use an agent.

## AI assistance and sources

AI assistance supported implementation, drafting, debugging and mechanical verification. The team is responsible for reviewing the ground truth, running the live batteries, interpreting the measured results, understanding the submitted code and approving the final submission. Course brief, FAQ, supplied scaffold, Appendix A routing table and Week 4 to Week 6 materials are the primary sources.
