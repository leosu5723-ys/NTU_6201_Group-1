# Phase B strand review - Tool dependencies and safe parallel calls

Reviewer: Isha Kirti Ghia  
Date: 19 September 2026
Status: Reviewed and confirmed by Isha Kirti Ghia.

Files reviewed:

- `tools.py`
- `docs/tool_dependency_design.md`
- `parallel_experiment.py`
- `artifacts/parallel_experiment.json`

## Design choice I can explain

The design allows calls to share a turn only when neither call requires the other's result. `get_claim` must run first because it supplies the member, hospital, service date, documents and line items needed by later tools. Once those facts are available, `get_policy_context` and `find_prior_decision` can run together: both use claim facts, neither consumes the other's output, and either may establish an early escalation trigger.

Line review deliberately waits until those eligibility and duplicate checks finish. This prevents the Agent from spending turns reviewing procedures when a lapsed policy, out-of-date service, exceeded annual limit or duplicate has already made line review unnecessary. For an eligible non-duplicate, `get_hospital_status` and the per-line `review_claim_line` calls can run together because they are independent reads. A pre-authorisation lookup cannot join the corresponding line review in the same turn because the Agent first needs the line-review result to know whether pre-authorisation is required.

The gated `issue_decision_letter` call comes last and must wait for the evidence required by the chosen outcome. The validation functions in `tools.py` fail closed when exact claim-level policy, duplicate, hospital or line evidence is missing. The tool also accepts only the three fixed outcomes and checks the autonomy gate before writing. Hostile-input safety escalation is intentionally handled without a write.

## Measured sequential/parallel comparison

The deterministic experiment held the cases and outcomes constant:

| Measure | Safe parallel | Sequential control |
|---|---:|---:|
| Cases passed | 40/40 | 40/40 |
| Total turns | 157 | 251 |
| Median turns | 4 | 6 |
| Estimated tokens in | 495,381 | 742,622 |
| Catalog cost | US$0.0573773 | US$0.0825918 |

Correctness was unchanged in this scripted comparison, while safe grouping reduced total turns by 94 (about 37.5%) and the catalog-cost estimate by about 30.5%. This does not prove that arbitrary calls are safe to parallelise. Parallel calls can do unnecessary speculative work, and grouping calls removes intermediate model decision points. The dependency rule must therefore be preserved.

## Review conclusion

Approved as written. The signatures remove the hidden same-turn dependency that would occur if a line check required a policy ID returned by another call in that turn: `review_claim_line` accepts the already-known `member_id` and resolves the policy internally. I found no correction required in this strand. My main caution is that future tool changes must not group a pre-authorisation lookup with the line review that determines whether that lookup is needed, and must not move line review ahead of eligibility and duplicate early exits.

