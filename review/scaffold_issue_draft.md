# Draft Scaffold Issue Report for Instructor Review

**Status:** Do not send before team approval.

## Summary

The supplied Problem A scripted example groups `lookup_policy(member_id)` and `check_coverage(code, policy_id)` in the same turn. The descriptor states that `policy_id` must come from `lookup_policy`, while the initial claim record contains only `member_id`. A live model therefore cannot construct the coverage calls at the start of that turn without knowing a fixture value that has not yet appeared in its transcript.

## Where

- `A2_scaffold/backends.py`, scripted trajectory for `CLM-8842`
- `A2_scaffold/tools.py`, descriptors for `lookup_policy` and `check_coverage`
- Problem A worked parallel-calling example in the A2 brief

## Observed

The scripted trajectory hard-codes `POL-3310` into three coverage calls that execute alongside the lookup expected to reveal `POL-3310`.

## Expected

Under the stated dependency rule, either:

1. `lookup_policy` must complete in an earlier turn; or
2. `check_coverage` must accept a value already available after `get_claim`, such as `member_id`, and resolve the policy internally; or
3. the claim lookup must deliberately return the policy ID, with that interface change documented.

## Team workaround

We selected option 2. `review_claim_line(member_id, procedure_code, attached_documents)` resolves the member's policy internally. Policy eligibility and duplicate history run first so decisive escalations still exit before line review. This makes the later line calls genuinely independent and also exposes required-document status, which the supplied Problem A tool set did not otherwise make available.
