# Zhang Jiayang: supplementary confirmation and report review

Feedback receipt: fb_a7949f8ff7390f79e949c92f. Original team-session message 399, platform message 322.

Zhang Jiayang — supplementary confirmation

I agree with separating “correctness of the persisted business decision/evidence” from “final delivery completeness and consistency”, and using the latter as the final Pass/Fail verdict.

Accordingly, I would revise the affected live judgements as follows:

CLM-8842 Trial 1: Fail — the correct approve_in_principle decision, line dispositions, evidence, and totals were already persisted, but the run later hit budget_ceiling and returned an inconsistent escalation as the final output. Please retain the fact that the persisted business decision itself was correct in the notes.
CLM-8901 Trials 1–2: Fail — the correct request_document decision (itemised bill for line 45378) had already been persisted, but each run subsequently hit budget_ceiling and returned escalation, so the final delivery was inconsistent.
CLM-8901 Trial 3: Pass — the correct request-document result was both persisted and returned consistently, with no later budget stop.

All my other live and scripted verdicts remain unchanged.

For the report review, I have the following comments:

Section 2 — ACI comparison: the draft currently reports v1/v2 observation tokens and evaluation pass rates, but D2(b) also requires the number of guardrail cases passed for each version. Please add the evidence-backed v1/v2 guardrail result.
Section 2 — poka-yoke: please express the two poka-yoke design choices explicitly in terms of what error each one makes impossible. The current wording, “make silent approval with missing documentation harder,” does not fully match the brief’s requirement.
Section 5 — loop failure: please state the measured before/after correctness or pass-rate result explicitly alongside turns, tokens, and cost. If a full-suite deletion pass rate was not measured, please do not infer one.
After all human judgements are reconciled: Section 3 should briefly capture the difference between machine scoring and human evidence-quality review, and Section 6 should replace “unfinished human judgement” with a limitation that reflects the completed but limited human review.

Apart from these points, I have no further corrections at this stage.
