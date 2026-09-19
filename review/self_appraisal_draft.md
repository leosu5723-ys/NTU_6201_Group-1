# Team Self-Appraisal Working Draft

This is a review aid only. Complete the official Word form together after the live evidence and final report exist.

## Header

- Team ID: B-1
- Section: B
- Problem: A
- Members: Meng Sijia; SHI SHUYI; Su Yang; Isha Kirti Ghia; Sun Hanyu; Zhang Jiayang
- Repository: https://github.com/leosu5723-ys/NTU_6201_Group-1
- Date: [FINAL DATE]

## 1. Rubric rating

Do not select bands until the clean-clone test, live batteries, judgement checks and video review are complete.

- Conceptual Understanding: [FINAL TEAM RATING]
- Technical Execution: [FINAL TEAM RATING]
- Reasoning & Justification: [FINAL TEAM RATING]
- Communication & Clarity: [FINAL TEAM RATING]

## 2. The one decision we would defend hardest

We would defend our dependency rule and the related redesign of the line-review tool. The starter example placed a policy lookup and coverage calls requiring its policy ID in the same turn, which a live model could not reproduce without hidden fixture knowledge. We changed the line-review signature to use the member ID already returned by the claim and resolve the policy internally. We also delayed line review until policy eligibility and duplicate history had passed, preserving early exits. In the scripted comparison, this safe parallel design kept 40/40 cases correct while reducing total turns from 251 to 157 and estimated input tokens from 742,622 to 495,381.

## 3. The one we are least sure about

Our hostile-input control is deliberately narrow. It detects the supplied attack families and an additional role-style instruction, but pattern matching cannot establish protection against paraphrased or novel prompt injection. Once `get_claim` returns a matched narrative, the code escalates before that observation is sent back to the model. The scripted checklist therefore measures the shipped guardrail, while the live battery cannot be interpreted as a test of the model's own resistance to those matched attacks. A production system would need broader adversarial testing and independent security review.

## 4. Headline numbers

| Field | Value |
|---|---:|
| Evaluation cases | 40 |
| Guardrail cases | 10 |
| Negative cases | 10 |
| Live runs per model | 60 |
| Pass rate, best model | [LIVE RESULT] |
| Pass rate on negatives only | [LIVE RESULT] |
| Models in battery | 5 v2 families plus one Gemini v1 pass |
| Median turns per run | [LIVE RESULT] |
| Live model each member ran | [INSERT SIX MEMBER RESULTS] |
| Turns saved by parallel calls | 94 total scripted turns across one trial per 40 cases |
| Cost per successful task | [LIVE COST MODEL] |
| Monthly cost at 8,000 claims | [LIVE COST MODEL] |
| Break-even success rate | [LIVE COST MODEL] |
| Tokens per call, v1 to v2 | [LIVE COMPARISON] |
| Pass rate, v1 to v2 | [LIVE COMPARISON] |

## 5. Contribution

Copy only completed and evidenced work from `CONTRIBUTIONS.md`. Do not turn intended ownership into completed contribution.

## 6. Declaration preconditions

Every box can be ticked only after:

- All six members can explain every submitted code block at function level.
- All reported pass rates, token counts, turns and costs come from saved execution evidence.
- The clean scripted run works without a key or network.
- `check_my_data.py` passes and shipped fixture fingerprints remain unchanged.
- No A2 artefact is reused in an individual project.
- Sources, tools and AI assistance are attributed.
