# PE6201 A2 — Phase A Case Authoring

**Member:** Meng Sijia  
**Assigned cases:** `CLM-8842`, `CLM-8901`, `CLM-8910`, `CLM-9001`, `CLM-9007`, `CLM-9013`, `CLM-9018`

## Phase A Rules

Use only:
- the source facts below; and
- the official Problem A Appendix A routing rules.

Do **not** use:
- Agent outputs;
- the project answer key;
- Phase B code/results.

For each case, independently author the final evaluation contract. A simple "looks correct" is not sufficient.

For every case, complete:
1. Decision
2. Exact trigger / missing item / escalation target, where applicable
3. Approved total / refused total, where applicable
4. Required line dispositions / evidence IDs
5. Decision boundary and business-rule rationale
6. Fixed machine-check fields and action-count requirement
7. Case-specific `must_record` requirements
8. Your authorship or substantive revision
9. Name and date

---

# CLM-8842

## Source Facts

- **Claim**
  - Member: (not stated in source)
  - Hospital: `H-114`
  - Service date: `2026-09-02`
  - Total: `2480`

- **Lines**
  - `47120` — SGD 1,400
  - `62480` — SGD 780
  - `31255` — SGD 300

- **Pre-authorisation**
  - `PA-5521`, procedure `62480`, valid `2026-08-01` to `2026-10-31`, covering service date `2026-09-02`

- **Exclusion**
  - `EX-14` cosmetic dermatology applies to `31255`

- **Policy context**
  - Active and service date covered.

## Member Response

- **Decision:** `approve_in_principle`
- **Trigger or missing item and escalation target (if applicable):** None.
- **Approved total / refused total (or explain why not applicable):** SGD 2,180 approved / SGD 300 refused.
- **Required line dispositions or evidence IDs:**
  - `47120` — SGD 1,400 — covered
  - `62480` — SGD 780 — covered; pre-authorisation `PA-5521`, valid `2026-08-01` to `2026-10-31`, covering service date `2026-09-02`
  - `31255` — SGD 300 — not_covered; exclusion `EX-14` cosmetic dermatology
  - Evidence: `get_claim`, `get_policy_context`, `review_claim_line` x3, `get_preauthorisation`, `get_hospital_status`, `find_prior_decision`
- **Decision boundary and business-rule rationale:** The policy is active and the service date is covered. All three lines resolve: two are payable and one is clearly excluded. Under Appendix A, a partly payable claim remains an `approve_in_principle`, not an escalation.
- **Fixed machine-check fields and action-count requirement:** `decision == approve_in_principle`; approved total `2180`; refused total `300`; all 3 line dispositions present; exclusion recorded for `31255`; `issue_decision_letter` called exactly once.
- **Case-specific `must_record` requirements:** `PA-5521` and its validity dates; `EX-14` cosmetic dermatology; approved/refused totals; all three line statuses.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract based on Appendix A and supplied fixture data.
- **Name and date:** Meng Sijia / 13 Sep 2026

The source confirms the three line amounts and coverage/pre-authorisation results.

---

# CLM-8901

## Source Facts

- **Claim**
  - Line: `45378` — SGD 1,150
  - Documents: none
- **Policy context**
  - Active and service date covered.
- **Line requirement**
  - Required document `itemised_bill` is absent.

## Member Response

- **Decision:** `request_document`
- **Trigger or missing item and escalation target (if applicable):** Missing `itemised_bill` for line `45378`. Escalation target: Not applicable.
- **Approved total / refused total (or explain why not applicable):** Not applicable because the claim cannot yet be fully resolved.
- **Required line dispositions or evidence IDs:** `45378` — SGD 1,150 — coverage itself is not excluded, but required document `itemised_bill` is absent. Evidence: `get_claim`, `get_policy_context`, `review_claim_line`.
- **Decision boundary and business-rule rationale:** Policy is active and the service date is covered. The line requires an `itemised_bill`, but documents are none. Appendix A requires the specific document name and the line it belongs to, rather than a generic request for more information.
- **Fixed machine-check fields and action-count requirement:** `decision := request_document`; `missing.item := itemised_bill`; `missing.for_line = 45378`; `issue_decision_letter` exactly once.
- **Case-specific `must_record` requirements:** Exact missing item `itemised_bill`, linked to line `45378`.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026

---

# CLM-8910

## Source Facts

- **Claim**
  - Service date: `2026-09-11`
- **Policy context**
  - Policy `POL-5588` lapsed; end date `2026-03-31`.
- **Lines**
  - Three lines present (pricing/review should not continue after early escalation condition is established).

## Member Response

- **Decision:** `escalate`
- **Trigger or missing item and escalation target (if applicable):** Trigger: `policy_lapsed` / policy outside its coverage dates. Escalation target: human claims assessor.
- **Approved total / refused total (or explain why not applicable):** Not applicable.
- **Required line dispositions or evidence IDs:** Evidence: `get_claim`, `get_policy_context`; line pricing/review should not continue after the early escalation condition is established.
- **Decision boundary and business-rule rationale:** Policy `POL-5588` is lapsed, with end date `2026-03-31`, while the service date is `2026-09-11`. Therefore the claim cannot be decided at this level. Appendix A explicitly treats a lapsed/out-of-date policy as an escalation condition.
- **Fixed machine-check fields and action-count requirement:** `decision := escalate`; `trigger := policy_lapsed`; `escalate_to := human claims assessor`; `issue_decision_letter` exactly once. Early exit is required; do not review all three lines after the lapsed-policy trigger.
- **Case-specific `must_record` requirements:** Policy ID `POL-5588`; lapsed status; policy end date `2026-03-31`; service date `2026-09-11`; single trigger only.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026

This is an important negative case because the correct behaviour is early escalation, not wasting turns reviewing procedures that cannot ultimately be decided. TEAM_ACTION_PACK also explicitly states that action count is part of the fixed harness.

---

# CLM-9001

## Source Facts

- **Claim**
  - Line: `99213` — SGD 200
- **Policy context**
  - Active, service date covered, hospital on panel, no duplicate.
- **Line requirement**
  - Covered with no required document or pre-authorisation.

## Member Response

- **Decision:** `approve_in_principle`
- **Trigger or missing item and escalation target (if applicable):** None.
- **Approved total / refused total (or explain why not applicable):** SGD 200 / SGD 0.
- **Required line dispositions or evidence IDs:** `99213` — SGD 200 — covered. Evidence: `get_claim`, `get_policy_context`, `review_claim_line`, `get_hospital_status`, `find_prior_decision`.
- **Decision boundary and business-rule rationale:** Policy is active, service date is covered, hospital is on panel, there is no duplicate, and the single line is covered with no required document or pre-authorisation.
- **Fixed machine-check fields and action-count requirement:** `decision=approve_in_principle`; approved total `200`; refused total `0`; one line disposition; `issue_decision_letter` exactly once.
- **Case-specific `must_record` requirements:** `99213=covered`; approved total `200`; no refusal.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026

---

# CLM-9007

## Source Facts

- **Claim**
  - Line: `27447` — SGD 9,000
  - Documents: `discharge_summary` present
- **Policy context**
  - Active, service date covered.
- **Pre-authorisation**
  - `PA-5702` valid `2026-07-01` to `2026-12-31`, exactly covering service date `2026-07-01`.

## Member Response

- **Decision:** `approve_in_principle`
- **Trigger or missing item and escalation target (if applicable):** None.
- **Approved total / refused total (or explain why not applicable):** SGD 9,000 / SGD 0.
- **Required line dispositions or evidence IDs:** `27447` — SGD 9,000 — covered; required `discharge_summary` is present; pre-authorisation `PA-5702` is valid `2026-07-01` to `2026-12-31`, exactly covering the service date `2026-07-01`.
- **Decision boundary and business-rule rationale:** The policy is active and the service date is covered. The knee-replacement line requires pre-authorisation, and a valid authorisation exists on the service date. Therefore the line resolves as covered and the claim is approved in principle.
- **Fixed machine-check fields and action-count requirement:** `decision=approve_in_principle`; approved total `9000`; refused total `0`; line `27447=covered`; pre-authorisation evidence recorded; `issue_decision_letter` exactly once.
- **Case-specific `must_record` requirements:** `PA-5702`; procedure `27447`; validity interval `2026-07-01`–`2026-12-31`; `discharge_summary` present.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026

Boundary point: This case should be kept because it tests the exact beginning boundary of pre-authorisation validity.

---

# CLM-9013

## Source Facts

- **Claim**
  - Line: `70553` — SGD 600
- **Policy context**
  - Annual limit `6000`; used `5400`; remaining `600`; claim total `600`.
  - Active and service date covered.
- **Line requirement**
  - Not excluded and requires no pre-authorisation.

## Member Response

- **Decision:** `approve_in_principle`
- **Trigger or missing item and escalation target (if applicable):** None.
- **Approved total / refused total (or explain why not applicable):** SGD 600 / SGD 0.
- **Required line dispositions or evidence IDs:** `70553` — SGD 600 — covered.
- **Decision boundary and business-rule rationale:** The claim total is exactly SGD 600, and the remaining annual limit is exactly SGD 600. Appendix A says escalation applies when line items exceed the remaining annual limit, so equality does not trigger escalation. The policy is active and the service date is covered. The line is not excluded and requires no pre-authorisation.
- **Fixed machine-check fields and action-count requirement:** `decision=approve_in_principle`; approved total `600`; refused total `0`; `70553=covered`; no `annual_limit_exceeded` trigger; `issue_decision_letter` exactly once.
- **Case-specific `must_record` requirements:** Annual limit `6000`; used `5400`; remaining `600`; claim total `600`; explicitly record that claim total = remaining limit and therefore does not exceed it.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026

This is one of your most important contracts because the team guide specifically asks you to pay attention to exact annual-limit equality.

---

# CLM-9018

## Source Facts

- **Claim**
  - Lines:
    - `99213` — SGD 180
    - `80053` — SGD 90
    - `70553` — SGD 620
    - `45378` — SGD 1,100
  - Total reconciliation: 180 + 90 + 620 + 1,100 = SGD 1,990
- **Documents**
  - Required `itemised_bill` present for `45378`
- **Policy context**
  - Active, covered service date, panel hospital, no duplicate, no excluded lines.

## Member Response

- **Decision:** `approve_in_principle`
- **Trigger or missing item and escalation target (if applicable):** None.
- **Approved total / refused total (or explain why not applicable):** SGD 1,990 / SGD 0.
- **Required line dispositions or evidence IDs:**
  - `99213` — SGD 180 — covered
  - `80053` — SGD 90 — covered
  - `70553` — SGD 620 — covered
  - `45378` — SGD 1,100 — covered; required `itemised_bill` present
  - Total reconciliation: 180 + 90 + 620 + 1,100 = SGD 1,990
  - Evidence: `get_claim`, `get_policy_context`, `review_claim_line` x4, `get_hospital_status`, `find_prior_decision`
- **Decision boundary and business-rule rationale:** Active policy, covered service date, panel hospital, no duplicate, no excluded lines, and the only required document is present. All four lines resolve as covered, so the claim is approved in principle.
- **Fixed machine-check fields and action-count requirement:** `decision=approve_in_principle`; 4 line dispositions; approved total `1990`; refused total `0`; line amounts reconcile to claim total; `issue_decision_letter` exactly once.
- **Case-specific `must_record` requirements:** All four line codes/statuses; `itemised_bill` present for `45378`; total reconciliation `1990 = 180 + 90 + 620 + 1100`.
- **My authorship or substantive revision (identify what I wrote or changed):** Independently authored contract.
- **Name and date:** Meng Sijia / 13 Sep 2026
