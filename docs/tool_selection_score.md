# D2(a) Tool Selection Score

The table applies the three Class 4 questions to every shipped tool. Prompt cost is the current v2 descriptor length using the same fixed characters-divided-by-four estimate used for prompt auditing. It is not a tokenizer measurement.

| Tool | Does a required task fail without it? | Could the model confuse it with a neighbour? | Standing v2 descriptor cost | Why it earns its place |
|---|---|---|---:|---|
| `get_claim` | Yes. No other tool reveals the incoming claim, its lines or untrusted narrative. | No. It is the unique entry point. | 518 chars, about 129 tokens | Every later argument originates here. |
| `get_policy_context` | Yes. Status, dates and remaining limit create three fixed escalation triggers. | Low. It is claim-level eligibility, not line coverage. | 641 chars, about 160 tokens | It enables early exit before line work. |
| `review_claim_line` | Yes. Every line needs an exclusion, document and pre-authorisation assessment. | Moderate with `get_preauthorisation`; the descriptor separates “is it required?” from “is a valid approval present?” | 830 chars, about 207 tokens | One call per line preserves the data-dependent branch while joining facts that always belong to the same line. |
| `get_preauthorisation` | Yes for marked procedures. Missing and expired approvals must produce a specific request. | Low after the conditional timing rule is stated. | 731 chars, about 182 tokens | It runs only after a line says pre-authorisation is required and distinguishes valid, expired and missing. |
| `get_hospital_status` | Yes. Non-panel status must appear in the decision record even though it does not change the outcome. | No. No other tool answers the network-status question. | 562 chars, about 140 tokens | It prevents a line-based response from claiming a payment basis that was never checked. |
| `find_prior_decision` | Yes. A true duplicate must escalate, while three-fact near misses must not. | No. This is business-history identity, not action de-duplication. | 784 chars, about 196 tokens | It matches all four facts and preserves line multiplicity. |
| `issue_decision_letter` | Yes. The FAQ defines a gated local write for the first-response decision. | No. It is the only callable write. | 1,521 chars, about 380 tokens | It validates outcome-specific evidence, checks trusted gate state, prevents a second write and appends the audit record. |

## Measured pre-cut versus selected block

The rejected candidate contained the seven selected tools plus separate `lookup_member` and `get_required_document_rule` calls. `design/precut_tool_block_A.json` freezes those descriptors. Using the same characters-divided-by-four estimator, the nine-tool block is 6,576 characters (about 1,644 tokens) and the selected seven-tool block is 5,593 characters (about 1,398 tokens). The cut saves an estimated 246 standing tokens per model request. Both removed tools duplicated facts already returned by a selected tool, so the cut reduces cost and call confusion without removing a task-critical fact.

## Tools deliberately not added

### `lookup_member`

Removed as a standalone tool. The member record carries no decision fact beyond the policy join, so a separate call would add a turn and another descriptor without enabling an outcome. `get_policy_context` performs the fixed member-to-policy join.

### `get_required_document_rule`

Tried as a separate concept, then folded into `review_claim_line`. A required document belongs to a procedure line and is always evaluated with that line. Keeping it separate would allow the model to detach a missing document from its code or skip it while still calling the coverage tool.

### `check_coverage(policy_id, code)`

Replaced rather than retained. In the scaffold, `policy_id` is returned by `lookup_policy` but the two calls are placed in the same turn. The new line-review signature accepts the already known `member_id` and resolves the policy internally, making parallel line calls genuine rather than dependent on a hard-coded fixture value.

### Web search or public API

Not added. Every required answer comes from the fixture systems of record. A network tool fails the “task fails without it” test and would weaken reproducibility.

## Cost judgement

The selected descriptor block is approximately 1,398 tokens before routing and answer-format text. The irreversible-action descriptor is the largest because its gate and outcome-integrity contract need explicit treatment. The v1 to v2 live experiment will determine whether the selected `review_claim_line` rewrite earns its recurring prompt cost. Until those measurements exist, the token increase is reported as a cost, not assumed to be an improvement.
