# Team Self-Appraisal: review-ready answers

Transfer the approved answers into the official PE6201_A2_Team_Self_Appraisal.docx. This working copy is not a signed form.

## Header

- Team ID: B-1; Section B; Problem A.
- Members: Meng Sijia; SHI SHUYI; Su Yang; Isha Kirti Ghia; Sun Hanyu; Zhang Jiayang.
- Repository: https://github.com/leosu5723-ys/NTU_6201_Group-1
- Signing date: complete at actual team approval.

## 1. Rubric rating

Team decision required for each: Conceptual Understanding (25%); Technical Execution (30%); Reasoning & Justification (25%); Communication & Clarity (20%). Available bands: Excellent (4), Proficient (3), Developing (2), Limited (1). No rating is selected here. Communication should be assessed after reviewing the actual video.

## 2. The decision we would defend hardest

We would defend the dependency rule behind our parallel calls. The starter example paired a policy lookup with coverage calls that needed the policy ID it had not yet returned. Our line-review interface instead uses the member ID already available from the claim and resolves the policy internally. The scripted comparison retained 40/40 correct cases while reducing turns from 251 to 157 and estimated input tokens from 911,506 to 609,144. This is measured efficiency on the scripted trajectories, not proof that every live model will choose the same ordering.

## 3. The decision we are least sure about

Our hostile-input protection is deliberately narrow. Known instruction patterns are detected in code before the claim observation returns to the model. Passing these cases demonstrates the shipped guard, not independent model resistance to prompt injection. We would require broader adversarial testing and independent security review before deployment, including paraphrases that do not match the current patterns.

## 4. Headline numbers

| Official field | Evidence-backed value |
|---|---|
| Evaluation cases | 40 |
| Guardrail cases | 10 scripted guardrail checklist cases; distinguish these from the 3 live injection cases |
| Negative cases | 10 |
| Live runs per model | 60: 30 ordinary cases once and 10 negative cases three times |
| Best-model strict pass rate | DeepSeek V3.2 v2: 55/60 (91.7%) |
| Best-model negative pass rate | 29/30 (96.7%) |
| Models in battery | Five v2 model families plus Gemini v1 control |
| Median turns | DeepSeek: 4 |
| Turns saved by parallel calls | 94 across 40 scripted cases; 251 to 157 |
| Cost per successful task | Escalation-cost convention: $0.82758 per incoming task resolved by agent or human fallback, before monthly fixed cost. Not API spend divided by agent successes and not retry-until-success cost. |
| Monthly cost at 8,000 claims | DeepSeek scenario: $7,020.66 including $400 fixed cost |
| Break-even success rate | Qwen requires 89.12% case-balanced success to match DeepSeek's expected cost; measured 47.50% |
| Tokens per call, v1 to v2 | Gemini mean observation estimate: 82.37 to 63.42; representative missing-document observation: 115 to 56. Estimates, not billed token counts. |
| Pass rate, v1 to v2 | Same Gemini model: 33/60 (55.0%) to 20/60 (33.3%) |

### All members' live runs

| Member | Model / version | Strict passes |
|---|---|---:|
| Meng Sijia | Gemini 2.5 Flash Lite v2 | 20/60 |
| SHI SHUYI | Qwen3 30B A3B Instruct v2 | 33/60 |
| Su Yang | Claude Haiku 4.5 v2, selected complete rerun | 35/60 |
| Isha Kirti Ghia | Llama 4 Maverick v2 | 53/60 |
| Sun Hanyu | DeepSeek V3.2 v2 | 55/60 |
| Zhang Jiayang | Gemini 2.5 Flash Lite v1 control | 33/60 |

All selected runs use f8a1d7450a4bee92c24f38a6924436bc9faabdaf. Claude's initial rate-limited run remains archived separately; no trials were spliced.

## 5. Contribution wording for team review

| Member | Owned | Also contributed to |
|---|---|---|
| Meng Sijia | Case contracts; evaluation-harness strand review; Gemini v2 battery | Live judgement, scripted CLM-8933 and report review |
| SHI SHUYI | Case contracts; integrated-loop/tool-layer review; Qwen v2 battery; integration coordination | Combined evidence interpretation, human-review calibration and report review |
| Su Yang | Case contracts; cost/ledger/sensitivity review; Claude v2 battery | Live judgement, scripted CLM-8952 and report review |
| Isha Kirti Ghia | Case contracts; dependency/parallel-call review; Llama v2 battery | Loop/interface repair proposals; live judgement, scripted CLM-8910 and report review |
| Sun Hanyu | Case contracts; scripted/negative/hostile-input review; DeepSeek v2 battery | Live judgement, scripted CLM-8925 and report review |
| Zhang Jiayang | Case contracts; descriptors/ACI/guardrails/tool-selection review; Gemini v1 battery | Live judgement, scripted CLM-8888/CLM-9019 and report corrections |

Match the final contribution log and preserved member commits. Video participation is not yet credited. Original Phase A disclosures remain in the source records; this table does not assert unaided drafting.

## 6. Declaration: leave unticked until team confirmation

Use the official wording without weakening it. Each member must confirm code-block understanding, actual execution underlying reported measurements, no-key/no-network scripted reproducibility, fixture preservation and labelled cases, no reuse from or into the individual project, and attribution of sources/tools/assistance. Actual execution with AI assistance is not invented measurement; disclose assistance accurately. The signatory and signing date must be supplied by the team. Do not infer signatures from report feedback.

Evidence: report/PE6201_A2_Report_Draft.md; artifacts/live_analysis_round2.json; review/ROUND2_INTEGRATION_SUMMARY.md; review/round2_judgement/calibrated/; original member commits. The official template contains historical deadline text; check the later course extension when submitting rather than treating the printed date as current.
