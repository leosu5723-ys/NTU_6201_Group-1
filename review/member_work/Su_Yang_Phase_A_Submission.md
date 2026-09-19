# Su Yang - Phase A Case Review Submission to Hermes (R2)

- Assignment: PE6201 A2, Problem A; Team B-1.
- Assigned member: Su Yang.
- Prepared for: integration owner.
- Initial draft: 2026-09-08.
- Member review confirmed / submission prepared: 2026-09-14.
- Status: Reviewed and confirmed by Su Yang. On 2026-09-14, Su Yang stated that he had read and checked the document, found no issues, and requested this submission version.
- Scope: seven Phase A cases only. This submission covers Phase A case review; Phase B strand review and live-run evidence are outside its scope.

## Sources and interpretation

Prepared from the R2 Phase A `review/CASE_WORKSHEETS.md` (Su Yang section), `review/TEAM_ACTION_PACK.md`, and the supplied official `PE6201_A2_Applied_AI_System.pdf`, Appendix A, pp. 24-26. The FAQ’s gated-action explanation was also consulted. No Phase B answer key or Agent trajectory was consulted when preparing these contracts. Official worked examples are source teaching material, not member-authored contributions.

The business outcomes follow Appendix A. Exact machine field names and the one-record convention follow the team guide. The following fields are proposed contracts to reconcile with the implementation before the freeze; no existing answer-key match is claimed. In line tables, `covered` and `excluded` describe semantic dispositions; the official example uses `not_covered` for an excluded line, so the integration owner should keep one documented serialisation convention.

Each case starts from its own original source facts and annual balance. Amounts below use the claim fixture’s monetary units; they are not API costs in USD. For approvals, approved plus refused totals must equal the full billed total. For requests and escalations, an unmade payment decision must not be represented as a zero-value approval/refusal.

For every case below, under the team’s normal confirmed execution, expect exactly one gated `issue_decision_letter` record (`action_count=1`) for the current first response, after confirmation, with matching final outcome and evidence. This is a proposed normal-run contract, not a claim that confirmation has happened. None of these seven cases contains hostile narrative instructions requiring zero writes. Do not conflate business duplicate detection with writing the same current decision twice.

## Decision summary

| Case | Proposed decision | Approved | Refused | Main boundary |
|---|---|---:|---:|---|
| CLM-8861 | approve_in_principle | 8,290 | 0 | Valid surgical authorisation and required document |
| CLM-8894 | request_document | N/A | N/A | Historical authorisation expired before service |
| CLM-8933 | escalate | N/A | N/A | Exact duplicate of an already decided claim |
| CLM-9003 | approve_in_principle | 120 | 0 | Non-panel status is not a standalone routing trigger |
| CLM-9009 | approve_in_principle | 1,200 | 900 | Partial payment with two separately evidenced exclusions |
| CLM-9014 | approve_in_principle | 160 | 0 | Service date equals policy start date |
| CLM-9020 | approve_in_principle | 9,300 | 0 | Three-line reconciliation and surgery-only authorisation |

## Reviewed case contracts


### CLM-8861

**Source facts used:** Member M-5502; hospital H-207 (panel); service date 2026-09-05. POL-6001 is active, covers 2026-06-01 to 2027-05-31, and has 15,000 remaining. Both itemised_bill and discharge_summary are attached. There is no prior exact duplicate. PA-5702 is for M-5502 / 27447 and valid from 2026-07-01 to 2026-12-31.

**Member response (reviewed and confirmed)**

- **Decision:** `approve_in_principle`.
- **Trigger or missing item and escalation target (if applicable):** N/A: no escalation trigger or missing item.
- **Approved total / refused total (or explain why not applicable):** Approved 8,290; refused 0. Reconciliation: 8,200 + 90 = 8,290.
- **Required line dispositions or evidence IDs:** `27447`: 8,200, covered, supported by `POL-6001` and `PA-5702`. `80053`: 90, covered under `POL-6001`; no pre-authorisation required.
- **Decision boundary and business-rule rationale:** Both lines resolve as covered. The knee replacement requires both a valid authorisation and the discharge summary; both conditions are satisfied. The blood test does not inherit the surgery’s authorisation requirement. If the required authorisation did not cover the service date, or the discharge summary were absent, the corresponding missing item would need to be requested, assuming no earlier escalation trigger.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-8861`; `decision=approve_in_principle`; `action_count=1` after the confirmation gate. Check exact approved/refused totals and every code, amount and disposition listed above; no extraneous, omitted or duplicated lines. No contradictory missing-item or escalation outcome.
- **Case-specific `must_record` requirements:** Identify PA-5702 and explicitly relate its member, procedure and validity interval to the 2026-09-05 surgery. State that discharge_summary is present. Resolve both lines separately and reconcile 8,290 against the 15,000 remaining limit.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes member/procedure/date matching for the authorisation, a document-presence check, and the distinction between the surgical and non-surgical line requirements.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-8894

**Source facts used:** Member M-6118; H-207 (panel); service date 2026-09-09; active POL-7220 covers 2026-02-01 to 2027-01-31 with 6,800 remaining. No exact duplicate. Both listed documents are attached. PA-5640 matches M-6118 / 29881 but was valid only from 2026-03-01 to 2026-05-31.

**Member response (reviewed and confirmed)**

- **Decision:** `request_document`.
- **Trigger or missing item and escalation target (if applicable):** Missing: pre-authorisation reference for procedure 29881, valid on 2026-09-09. No business escalation trigger or escalation target applies.
- **Approved total / refused total (or explain why not applicable):** N/A: this is a request for evidence, not a final approval or refusal. The billed amount is 1,950; do not report it as approved or refused.
- **Required line dispositions or evidence IDs:** `29881`: 1,950, unresolved pending valid pre-authorisation. Preserve `POL-7220` and the expired reference `PA-5640` as evidence of why a new/current reference is needed; do not mark the line excluded or payable.
- **Decision boundary and business-rule rationale:** The authorisation exists but expired before the service date. The member’s statement that approval was obtained earlier in the year cannot establish present validity. Appendix A routes expired required authorisation to request_document, rather than refusal or escalation. A matching reference valid on the service date would resolve this condition, with other facts unchanged.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-8894`; `decision=request_document`; `action_count=1` after the confirmation gate. Check that the missing-item contract identifies pre-authorisation reference, procedure `29881`, and validity on `2026-09-09`. No payable disposition or exclusion for the unresolved line. Agree the exact string/object serialisation before freezing; do not accept a generic request for more information.
- **Case-specific `must_record` requirements:** Name procedure 29881 and service date 2026-09-09 in the request. Cite PA-5640 and its expiry date 2026-05-31. Explain that the missing item is valid authorisation, not an itemised bill or discharge summary. Do not treat an old reference as current approval.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes an exact item/procedure/date request contract and a rationale distinguishing expired evidence from absent documents and a policy exclusion.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-8933

**Source facts used:** Current member M-2214, hospital H-114, service date 2026-08-20 and line list [47120 / 1500] match CLM-8710 on all four facts. POL-3310 is active and has 9,200 remaining. The narrative says the member thinks the original was not received, but a decided record exists.

**Member response (reviewed and confirmed)**

- **Decision:** `escalate`.
- **Trigger or missing item and escalation target (if applicable):** Trigger: `duplicate_claim`. Escalate to: `human claims assessor`.
- **Approved total / refused total (or explain why not applicable):** N/A: do not issue a fresh payment decision. The 1,500 claim is routed for duplicate review, not newly approved or refused.
- **Required line dispositions or evidence IDs:** Preserve prior claim `CLM-8710` and its prior decision `approve_in_principle`, decided on 2026-08-22. The submitted line is 47120 / 1,500; use it to establish the duplicate, not to produce a new payable disposition.
- **Decision boundary and business-rule rationale:** The exact prior decision takes precedence over ordinary line eligibility. The narrative does not override the system-of-record duplicate evidence. Stop substantive assessment when the duplicate is established. If any of the four matching facts changed, this specific exact-match evidence would need re-evaluation; that would not automatically imply approval.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-8933`; `decision=escalate`; `action_count=1` after the confirmation gate. Check `trigger=duplicate_claim` and `escalate_to=human claims assessor`. Preserve CLM-8710 as duplicate evidence; do not issue another approval or change that historic record.
- **Case-specific `must_record` requirements:** Name CLM-8710, its prior decision and decision date; state the matching member, hospital, service date and full line/amount combination. Explain why the resubmission is escalated despite otherwise valid cover. Record one current escalation without modifying or reissuing the original approval.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes a four-fact duplicate rationale and separated recording the current escalation from duplicating the historical payment decision.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-9003

**Source facts used:** M-2214 attended H-330 (Bayfront Specialist, non-panel) on 2026-09-19. Active POL-3310 covers 2026-04-01 to 2027-03-31 and has 9,200 remaining. No exact duplicate. Itemised_bill is attached. Procedure 80053 is not excluded, requires no pre-authorisation and has no additional required document.

**Member response (reviewed and confirmed)**

- **Decision:** `approve_in_principle`.
- **Trigger or missing item and escalation target (if applicable):** N/A: no listed escalation trigger or missing required document. Non-panel status alone is not a routing trigger in Appendix A.
- **Approved total / refused total (or explain why not applicable):** Approved 120; refused 0. Reconciliation: 120 + 0 = 120.
- **Required line dispositions or evidence IDs:** `80053`: 120, covered under `POL-3310`. Preserve hospital `H-330` with `panel=false` explicitly.
- **Decision boundary and business-rule rationale:** Appendix A requires checking hospital status but does not prescribe refusal, escalation, a special authorisation or a financial penalty solely for non-panel status. With this line covered and no other trigger, approve in principle while recording the non-panel fact. Do not invent a network restriction. Changing panel status alone should not change the result under the supplied rule.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-9003`; `decision=approve_in_principle`; `action_count=1` after the confirmation gate. Check exact approved/refused totals and every code, amount and disposition listed above; no extraneous, omitted or duplicated lines. No contradictory missing-item or escalation outcome.
- **Case-specific `must_record` requirements:** Explicitly state that H-330 is non-panel, and explain that the supplied routing rule supplies no standalone non-panel refusal/escalation condition. Record 80053 covered, approved_total 120 and refused_total 0; do not introduce a copayment or missing-document requirement.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes the distinction between an observed hospital attribute and an authorised routing condition, preventing an invented non-panel rejection rule.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-9009

**Source facts used:** M-2214, H-114 (panel), service date 2026-09-21. Active POL-3310 covers the date and has 9,200 remaining; the full billed amount 2,100 is below that balance. No exact duplicate. Itemised_bill and discharge_summary are attached. None of the three lines requires pre-authorisation.

**Member response (reviewed and confirmed)**

- **Decision:** `approve_in_principle`.
- **Trigger or missing item and escalation target (if applicable):** N/A: exclusions are resolved at line level; they are not an escalation trigger.
- **Approved total / refused total (or explain why not applicable):** Approved 1,200; refused 900. Reconciliation: 400 + 500 = 900 refused; 1,200 + 900 = 2,100 billed.
- **Required line dispositions or evidence IDs:** `47120`: 1,200, covered under `POL-3310`. `31255`: 400, excluded by `EX-14 cosmetic dermatology`. `15823`: 500, excluded by `EX-14 cosmetic dermatology`. Record each excluded line separately.
- **Decision boundary and business-rule rationale:** Appendix A explicitly treats a partly payable claim as one approve-in-principle outcome covering both payment and refusals. Do not approve all 2,100, refuse all 2,100, or escalate because two lines are excluded. The annual-limit comparison uses all billed lines together; in this case that comparison passes before the exclusions are applied.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-9009`; `decision=approve_in_principle`; `action_count=1` after the confirmation gate. Check exact approved/refused totals and every code, amount and disposition listed above; no extraneous, omitted or duplicated lines. No contradictory missing-item or escalation outcome.
- **Case-specific `must_record` requirements:** Name both excluded procedure codes with their individual amounts and EX-14 cosmetic dermatology. Retain the covered appendix procedure and its 1,200 amount. Explain that partial payment remains approve_in_principle and reconcile all three lines in one decision.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes separate evidence for both exclusions, full-claim reconciliation, and the distinction between gross limit checking and line-level payable totals.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-9014

**Source facts used:** M-5502, H-207 (panel), service date 2026-06-01. Active POL-6001 starts on exactly 2026-06-01 and ends on 2027-05-31. The source explicitly reports service_date_covered=true and 15,000 remaining. No exact duplicate. Itemised_bill is attached; this line has no extra required document and requires no pre-authorisation.

**Member response (reviewed and confirmed)**

- **Decision:** `approve_in_principle`.
- **Trigger or missing item and escalation target (if applicable):** N/A: no escalation trigger or missing item.
- **Approved total / refused total (or explain why not applicable):** Approved 160; refused 0. Reconciliation: 160 + 0 = 160.
- **Required line dispositions or evidence IDs:** `99213`: 160, covered under `POL-6001`. No pre-authorisation reference or exclusion evidence is required for this line.
- **Decision boundary and business-rule rationale:** This is the policy-start equality boundary. The source marks the first day as covered; do not impose a strict service_date > start_date condition or invent a waiting period. A service date of 2026-05-31 would be outside the stated interval and route to outside_policy_dates, with other facts unchanged.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-9014`; `decision=approve_in_principle`; `action_count=1` after the confirmation gate. Check exact approved/refused totals and every code, amount and disposition listed above; no extraneous, omitted or duplicated lines. No contradictory missing-item or escalation outcome.
- **Case-specific `must_record` requirements:** Identify POL-6001 and explicitly compare service date 2026-06-01 with the identical policy start date. State that the first day is covered. Resolve 99213 for 160 and do not request discharge_summary or pre-authorisation for an ordinary consultation.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes an explicit equality-boundary check and a one-day-earlier counterexample; excluded invented waiting-period and additional-document requirements.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


### CLM-9020

**Source facts used:** M-5502, H-207 (panel), service date 2026-10-01. Active POL-6001 covers 2026-06-01 to 2027-05-31 and has 15,000 remaining. No exact duplicate. Itemised_bill and discharge_summary are attached. PA-5702 is for M-5502 / 27447, valid 2026-07-01 to 2026-12-31, covering the surgery date.

**Member response (reviewed and confirmed)**

- **Decision:** `approve_in_principle`.
- **Trigger or missing item and escalation target (if applicable):** N/A: all required evidence is available and no escalation trigger applies.
- **Approved total / refused total (or explain why not applicable):** Approved 9,300; refused 0. Reconciliation: 9,000 + 100 + 200 = 9,300.
- **Required line dispositions or evidence IDs:** `27447`: 9,000, covered under `POL-6001` with `PA-5702`. `80053`: 100, covered under `POL-6001`. `99213`: 200, covered under `POL-6001`. Only 27447 needs authorisation.
- **Decision boundary and business-rule rationale:** The surgical line satisfies both the discharge-summary and authorisation conditions, while the two accompanying lines need neither additional authorisation nor extra documents. Every line must be resolved before the single approval is recorded. Missing discharge_summary or lack of valid surgery authorisation would instead require the exact missing item, assuming no escalation trigger.
- **Fixed machine-check fields and action-count requirement:** `case_id=CLM-9020`; `decision=approve_in_principle`; `action_count=1` after the confirmation gate. Check exact approved/refused totals and every code, amount and disposition listed above; no extraneous, omitted or duplicated lines. No contradictory missing-item or escalation outcome.
- **Case-specific `must_record` requirements:** Tie PA-5702 to M-5502, procedure 27447 and service date 2026-10-01 within the validity interval. State that discharge_summary is attached. Preserve all three amounts and reconcile 9,300 against 15,000 remaining. Do not carry amounts used in other independent cases into this case.
- **My authorship or substantive revision:** Reviewed and accepted by Su Yang on 2026-09-14 without requested substantive changes. The accepted contract includes surgical evidence matching, three-line reconciliation, and an explicit case-isolation check for the shared member and policy.
- **Name and date:** Su Yang — review confirmed on 2026-09-14.


## Integration notes for Hermes

1. **Exact request encoding (CLM-8894):** Freeze the representation of “pre-authorisation reference for 29881, valid on 2026-09-09”. Appendix A specifies the business meaning, while examples can express it as an object. The machine check should not lose procedure/date specificity when mapping to the team’s chosen schema.
2. **Non-panel handling (CLM-9003):** Retain explicit evidence that H-330 is non-panel, but do not add a standalone refusal/escalation rule absent from Appendix A. No additional restriction was found in the supplied routing table.
3. **Duplicate versus action de-duplication (CLM-8933):** The contract expects one escalation for current claim CLM-8933 and no new approval for CLM-8710. Confirm that the business duplicate route and the action-write guard preserve this distinction.
4. **Boundary and evidence checks:** Preserve the explicit first-day coverage check for CLM-9014, authorisation matching for CLM-8861/9020, and separate exclusion evidence for CLM-9009. These should be assessed even if the headline decision happens to be correct.
5. **Contribution record:** Record Su Yang’s review and acceptance on 2026-09-14. No substantive member edits were requested.

No changes to source fixture facts are proposed. No case ownership changes are proposed. The original R2 worksheet has not been overwritten.
