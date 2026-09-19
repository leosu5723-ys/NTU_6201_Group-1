# Instructor Clarification Draft: Gated Action on Negative Outcomes

**Status:** Superseded by the team's documented implementation decision; do not send.

The current documents appear to support two readings of Problem A's simulated write:

1. The FAQ's full example defines `issue_decision_letter` with a `decision` argument that accepts `approve_in_principle`, `request_document`, or `escalate`, then gates and appends the record.
2. D4 defines a negative case as an ASK or ESCALATE outcome, meaning anything except the ACT outcome. The Appendix A negative examples show structured request or escalation records but do not show `issue_decision_letter` being called. The hostile-input guidance also emphasises refusal and zero unsafe action.

The team resolved this ambiguity by following the FAQ function signature. Ordinary `approve_in_principle`, `request_document`, and business `escalate` outcomes call the gated `issue_decision_letter` exactly once. Hostile-input escalation remains fail closed with zero actions because the untrusted narrative is intercepted before any write.

## Superseded proposed question

> For Problem A, should the simulated `issue_decision_letter` tool be called and gated for all three first-response outcomes, including `request_document` and `escalate`, as the FAQ function signature suggests? Or should it fire only for the ACT outcome, `approve_in_principle`, with ASK and ESCALATE recorded without invoking the gated action, as the negative-case terminology and examples suggest? We want our action-count code checks to follow the intended interpretation.

The repository records the adopted interpretation explicitly rather than presenting the source documents as unambiguous.
