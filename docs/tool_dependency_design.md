# Problem A Tool and Dependency Design

## Design objective

Use the shortest defensible tool set while exposing every external fact needed by Appendix A. A tool should return a bounded business fact, not a whole database and not a hidden final decision.

## Proposed tools

1. `get_claim(claim_id)`
   - Entry point. Returns member, hospital, service date, untrusted narrative, attached documents and all line items.
   - Runs alone in turn 1.

2. `get_policy_context(member_id, date_of_service, claim_total)`
   - Resolves member to policy and returns status, coverage dates, remaining limit and deterministic boundary facts.
   - Supports early exit for lapsed, out-of-date and over-limit claims.

3. `review_claim_line(member_id, procedure_code, attached_documents)`
   - Reviews exactly one line.
   - Resolves the member's policy internally, then returns exclusion rule, pre-authorisation requirement, required document and document-presence status.
   - Uses `member_id`, which is known after `get_claim`, rather than a `policy_id` that another same-turn call has not yet returned.

4. `get_preauthorisation(member_id, procedure_code, date_of_service)`
   - Called only when the line review says pre-authorisation is required.
   - Returns an explicit status of `valid`, `expired`, `not_yet_valid` or `missing`, plus a bounded matching record when one exists.

5. `get_hospital_status(hospital_id)`
   - Returns panel status and identity. Panel status changes the decision record, not the routing outcome.

6. `find_prior_decision(member_id, hospital_id, date_of_service, lines)`
   - Matches all four business facts and returns the prior decision or `None`.

7. `issue_decision_letter(...)`
   - The only irreversible action.
   - It records `approve_in_principle`, `request_document` or a supported business `escalate` only after the required evidence and autonomy gate pass. Hostile-input safety escalation performs no write.
   - It appends one structured record to a per-run local JSONL log.

## Dependency rule

Two calls may share a turn only when neither requires the other's output.

- Turn 1: `get_claim`, alone.
- Turn 2: policy context and prior-decision lookup run together. Both can terminate the run, so line review waits for their observations.
- Turn 3 on eligible non-duplicates: hospital status and all per-line reviews run together.
- Pre-authorisation lookups wait for the corresponding line reviews.
- The gated action waits for the evidence required by its outcome. Approval requires every line; a document request preserves only already-resolved lines; a business escalation stops line work once its trigger is established.

Early-exit cases stop as soon as a decisive escalation trigger is established. Parallel execution may speculatively perform independent calls that an early sequential path would skip; the experiment must report this trade-off.

## Scaffold corrections

The supplied scripted Problem A example calls `lookup_policy(member_id)` and `check_coverage(code, policy_id)` in the same turn even though the policy ID is produced by the first call. That grouping is not valid for a live model. The `review_claim_line(member_id, ...)` signature removes the hidden dependency.

The scaffold also exposes `required_documents.json` in the data but provides no Problem A tool that reads it. `review_claim_line` makes that required system-of-record fact available without adding a separate confusable lookup.
