# PE6201 A2 — Phase A Case Authoring (R2)

**Member:** SHI SHUYI
**Assigned cases:** `CLM-8850`, `CLM-8888`, `CLM-8925`, `CLM-9002`, `CLM-9008`, `CLM-9013`, `CLM-9019`
**Date:** 2026-09-19
**Basis:** The source facts below come from the frozen fixture records and read-only tool lookups. The contracts are written against the official Problem A routing rules. No Agent trajectory was used.

---

# CLM-8850

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. Policy `POL-6001` is active, the service date is covered, the line is not excluded and no document or pre-authorisation is required.
- **Approved total / refused total:** Approved **SGD 180**; refused **SGD 0**.
- **Required line dispositions / evidence:**
  - `99213` — SGD 180 — covered — evidence `POL-6001`
  - Hospital `H-207` (Mount Elizabeth East) is on panel.
- **Decision boundary and rationale:** This is the baseline ordinary approval. All three early-exit checks pass (policy live, no duplicate, panel hospital), the only line resolves as covered, and the claim total equals the approved total. The routing rule therefore requires the acting outcome. If the service date fell before `2026-06-01` the outcome would become `escalate` with trigger `outside_policy_dates`.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 180`; `refused_total = 0`; line `99213` status `covered`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record policy `POL-6001` as active with the service date inside its dates, the single line disposition `99213 covered 180`, and an approved total of SGD 180 with SGD 0 refused.
- **My authorship or substantive revision:** Defined the decision boundary for the baseline approval, fixed the line disposition and totals, and added the counterfactual escalation boundary for an out-of-dates service date.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-8888

## Final Evaluation Contract

- **Decision:** `request_document`
- **Trigger / missing item / escalation target:** Missing item — **pre-authorisation reference for line 62480, valid on 2026-09-08**. No escalation trigger applies.
- **Approved total / refused total:** Not applicable. This is a document-request outcome, so no payable totals are issued.
- **Required line dispositions / evidence:**
  - `47120` — SGD 900 — covered — evidence `POL-7220`
  - `31255` — SGD 300 — excluded — evidence `EX-14` (cosmetic dermatology)
  - `62480` — SGD 1,200 — unresolved: requires pre-authorisation and none exists
- **Decision boundary and rationale:** Procedure `62480` requires a pre-authorisation, and `get_preauthorisation` returns `status = missing` for member `M-6118` on `2026-09-08`. Appendix A requires a document request, naming the exact thing missing and the line it belongs to. The other two lines are already resolved, which is why the record must show resolved lines alongside the single unresolved one rather than treating the whole claim as undecidable. If the pre-authorisation existed and was valid on the service date, the outcome would become an approval.
- **Fixed machine-check fields:** `decision = request_document`; `missing = "pre-authorisation reference for line 62480, valid on 2026-09-08"`; `expected_action_count = 1`; no approved or refused total.
- **Case-specific `must_record`:** Must record the exact missing item together with line `62480` and the required validity date `2026-09-08`, and must preserve the two already-resolved dispositions (`47120` covered, `31255` excluded under `EX-14`).
- **My authorship or substantive revision:** Defined the missing-item contract for an absent pre-authorisation, fixed the resolved-line dispositions that must survive alongside the request, and added the counterfactual that a valid pre-authorisation converts the outcome to an approval.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-8925

## Final Evaluation Contract

- **Decision:** `escalate`
- **Trigger / missing item / escalation target:** Trigger `annual_limit_exceeded`; escalate to **human claims assessor**.
- **Approved total / refused total:** Not applicable. The claim is escalated before any payable decision is issued.
- **Required line dispositions / evidence:** None should be issued. The decisive evidence is policy `POL-3310` with `remaining = 9200` against a claim total of SGD 11,400.
- **Decision boundary and rationale:** The claim total of SGD 11,400 exceeds the SGD 9,200 remaining on annual limit for `POL-3310`, so `annual_limit_exceeded` is true. The routing rule escalates when the lines together exceed the remaining annual limit. This is also the early-exit case: once the limit breach is established the agent must stop rather than price individual lines it would never pay. If the claim total were within the remaining limit, the lines would be priced normally.
- **Fixed machine-check fields:** `decision = escalate`; `trigger = annual_limit_exceeded`; `escalate_to = human claims assessor`; `expected_action_count = 1`; no approved or refused total; no line dispositions.
- **Case-specific `must_record`:** Must record the single trigger `annual_limit_exceeded`, the escalation target, and the limit arithmetic (claim total SGD 11,400 against SGD 9,200 remaining). Must record that the run stopped before line pricing.
- **My authorship or substantive revision:** Defined the annual-limit escalation contract, required the limit arithmetic rather than a generic "cannot be decided" phrase, and specified that the early exit must be visible in the record.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-9002

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. Policy active, service date covered, hospital on panel, no duplicate, no document or pre-authorisation requirement.
- **Approved total / refused total:** Approved **SGD 1,700**; refused **SGD 0**.
- **Required line dispositions / evidence:**
  - `47120` — SGD 1,700 — covered — evidence `POL-3310`
- **Decision boundary and rationale:** Single-line surgical claim that resolves cleanly. Claim total SGD 1,700 is well inside the SGD 9,200 remaining, so no limit trigger applies. This case confirms that a claim sharing a member and hospital with other cases is still decided on its own facts, which is the isolation requirement.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 1700`; `refused_total = 0`; line `47120` status `covered`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record policy `POL-3310` as active and the remaining limit as sufficient, the single covered disposition for `47120`, and the approved total of SGD 1,700 with SGD 0 refused.
- **My authorship or substantive revision:** Defined the clean single-line approval contract and added the case-isolation requirement that this case is decided only on its own facts despite sharing member `M-2214` with other cases.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-9008

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. The pre-authorisation is valid on the service date.
- **Approved total / refused total:** Approved **SGD 9,500**; refused **SGD 0**.
- **Required line dispositions / evidence:**
  - `27447` — SGD 9,500 — covered — evidence `PA-5702` (valid `2026-07-01` to `2026-12-31`)
- **Decision boundary and rationale:** This case tests the inclusive end boundary of a pre-authorisation. Service date `2026-12-31` equals `PA-5702`'s `valid_to` date `2026-12-31`, and the official rule only requires a document request when the pre-authorisation is absent or expired *before* the date of service. The last authorised day is still authorised, so the line resolves as covered. If the service date were `2027-01-01` with the same pre-authorisation, the outcome would become `request_document`.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 9500`; `refused_total = 0`; line `27447` status `covered`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record pre-authorisation `PA-5702` and show that `valid_to = 2026-12-31` covers a service date of `2026-12-31` on an inclusive reading, plus the covered disposition and the SGD 9,500 approved total.
- **My authorship or substantive revision:** Defined the inclusive pre-authorisation end-date boundary, fixed the required evidence reference `PA-5702`, and added the next-day counterfactual that would flip the outcome to a document request.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-9013

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. The claim total stays inside the remaining annual limit.
- **Approved total / refused total:** Approved **SGD 599**; refused **SGD 0**.
- **Required line dispositions / evidence:**
  - `70553` — SGD 599 — covered — evidence `POL-4102`
- **Decision boundary and rationale:** This case tests the just-under-the-limit boundary. Policy `POL-4102` has SGD 600 remaining, and the claim total is SGD 599, so the lines do not exceed the remaining limit and `annual_limit_exceeded` is false. The outcome stays an approval. A one-dollar increase to SGD 600 changes the arithmetic but still does not exceed the limit; SGD 601 would trigger `annual_limit_exceeded`. The case exists to prove the agent compares the claim total against the remaining limit rather than against the annual limit alone.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 599`; `refused_total = 0`; line `70553` status `covered`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record policy `POL-4102`, the remaining limit of SGD 600, the claim total of SGD 599, and that the total stays within the remaining limit so no escalation trigger applies.
- **My authorship or substantive revision:** Defined the near-limit boundary against the *remaining* limit rather than the annual limit, fixed the covered disposition and SGD 599 total, and stated the exact threshold that would change the outcome.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-9019

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. This is a partly payable claim, which is an acting outcome, not an escalation.
- **Approved total / refused total:** Approved **SGD 3,200**; refused **SGD 500**.
- **Required line dispositions / evidence:**
  - `47120` — SGD 1,200 — covered — evidence `POL-3310`
  - `62480` — SGD 2,000 — covered — evidence `PA-5521` (valid `2026-08-01` to `2026-10-31`)
  - `15823` — SGD 500 — excluded — evidence `EX-14` (cosmetic dermatology)
- **Decision boundary and rationale:** Three lines with three different resolutions: a plain covered line, a line covered only because a valid pre-authorisation exists, and a line refused under an explicit exclusion. The claim total is SGD 3,700 and stays inside the SGD 9,200 remaining, so no limit trigger applies. The hospital `H-330` (Bayfront Specialist) is **not** on the panel, which is recorded as the payment basis; it is not an escalation trigger under the routing rule. The claim is still one decision letter with an excluded line refused inside the same decision. Collapsing this into an escalation, or approving the full SGD 3,700, are both wrong.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 3200`; `refused_total = 500`; line statuses `47120 covered`, `62480 covered`, `15823 excluded`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record all three dispositions with their amounts and evidence (`POL-3310`, `PA-5521`, `EX-14`), the non-panel hospital as payment basis, and show that SGD 1,200 + SGD 2,000 = SGD 3,200 approved with SGD 500 refused, reconciling to the SGD 3,700 claim total.
- **My authorship or substantive revision:** Defined the mixed-outcome contract that combines partial payment, a valid pre-authorisation and an explicit exclusion in one decision, required the non-panel fact to be recorded as payment basis rather than as a trigger, and added the reconciliation between line amounts and the approved/refused totals.
- **Name and date:** SHI SHUYI — 2026-09-19

---

# CLM-9012

## Final Evaluation Contract

- **Decision:** `approve_in_principle`
- **Trigger / missing item / escalation target:** Not applicable. The claim total equals the remaining annual limit exactly and does not exceed it.
- **Approved total / refused total:** Approved **SGD 600**; refused **SGD 0**.
- **Required line dispositions / evidence:**
  - `70553` — SGD 600 — covered — evidence `POL-4102`
- **Decision boundary and rationale:** This is the exact-equality limit boundary, and it is the partner case to `CLM-9013`. Policy `POL-4102` has SGD 600 remaining and the claim total is exactly SGD 600. The routing rule escalates only when the lines together **exceed** the remaining limit. Equality does not exceed, so `annual_limit_exceeded` is false and the claim is approved. One further dollar would flip the outcome to `escalate`. Reading the rule as "reaching the limit escalates" is the specific error this case exists to catch.
- **Fixed machine-check fields:** `decision = approve_in_principle`; `approved_total = 600`; `refused_total = 0`; line `70553` status `covered`; `expected_action_count = 1`.
- **Case-specific `must_record`:** Must record policy `POL-4102`, the remaining limit of SGD 600, the claim total of SGD 600, and that equality with the remaining limit is not an excess, so no escalation trigger applies.
- **My authorship or substantive revision:** Authored this contract when integration review found that the originally assigned reviewer had covered `CLM-9013` instead of `CLM-9012`, leaving this case uncovered. Defined the exact-equality limit boundary against the remaining limit and stated the one-dollar threshold that would change the outcome.
- **Name and date:** SHI SHUYI — 2026-09-19

---

## Submission Note

This file contains SHI SHUYI's Phase A evaluation contracts for the seven assigned Problem A cases and is ready for team integration review.
