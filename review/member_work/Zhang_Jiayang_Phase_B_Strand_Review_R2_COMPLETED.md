# PE6201 A2 — Phase B Strand Review (R2) — COMPLETED

**Member:** Zhang Jiayang  
**Date:** 2026-09-18  
**Assigned strand:** Tool descriptors, v1-to-v2 ACI experiment, guardrails, and tool-selection design

---

## Formal Strand Review Response

**Strand reviewed:**  
Tool descriptors, the v1-to-v2 `review_claim_line` ACI experiment, code-level guardrails, and the nine-to-seven tool-selection design.

**One design choice I can explain:**  
The v2 ACI moves deterministic line-level interpretation into the `review_claim_line` interface instead of asking the model to reconstruct those facts from broader raw records. In particular, the interface accepts `member_id` rather than an unknown `policy_id`, which removes a model-side dependency and avoids requiring the model to guess or hard-code a policy identifier. The v2 return shape also exposes bounded fields such as exclusion, pre-authorisation requirement, required document, and `required_document_present`. The controlled v1/v2 comparison keeps the model, cases, tool set, routing rules, other six descriptors, guardrails, and agent code fixed; only the `review_claim_line` descriptor and corresponding return shape change. Code-level guardrails then enforce turn and token caps, action de-duplication, a `confirm` autonomy gate in front of the irreversible write, and fail-closed handling of known hostile-input families.

**One question, correction, or “approved as written”:**  
Approved as written; I did not identify a blocking design correction in this strand. The current deterministic evidence supports the implementation structure, but the final claim that v2 improves live-model pass rate or whole-run cost should remain explicitly pending until the frozen Gemini 2.5 Flash Lite v1 and v2 batteries are completed and compared. The hostile-input detector should also continue to be described as a deliberately narrow safeguard for the defined attack families, not as a general solution to prompt injection.

**Name and date:**  
Zhang Jiayang — 2026-09-18

---

# Personal Review Notes / Oral-Defence Preparation

## 1. Tool descriptors and ACI design

The tool layer is the model's operating manual. Each shipped tool should have a six-field descriptor: name/signature, what it answers, inputs, bounded returns, failure conditions, and whether it is irreversible.

The strongest poka-yoke in this strand is the redesign from a coverage tool that would require a model-supplied `policy_id` to `review_claim_line(member_id, procedure_code, attached_documents)`. The model already knows the member ID from the claim, while the policy ID would otherwise depend on another lookup. Resolving the member-to-policy join inside the interface removes the opportunity for the model to guess an unknown identifier.

The v2 return shape also moves deterministic document and line checks into ordinary code. Instead of returning broader raw policy/procedure/document records and expecting the model to reconstruct the relationship, v2 returns bounded line-level facts such as `excluded`, `requires_preauth`, `required_document`, and `required_document_present`.

**Oral-defence sentence:**  
“Where ordinary code can deterministically derive a business fact, we expose that fact through the interface rather than paying the model to infer it repeatedly.”

---

## 2. Controlled v1-to-v2 ACI experiment

This is an ACI experiment, not merely a wording experiment. The intended treatment consists of both the `review_claim_line` descriptor and its corresponding return shape.

The comparison keeps constant:
- model family;
- evaluation cases;
- seven-tool set;
- routing rules;
- answer schema;
- other six tool descriptors;
- guardrails;
- agent code;
- underlying source data.

Only the `review_claim_line` ACI changes.

Current deterministic evidence shows that the v2 standing prompt is larger, while the representative tool observation is smaller. This does **not** yet prove that v2 is cheaper or more reliable overall. Whole-run cost depends on repeated prompt/history transmission, number of turns, unnecessary calls, failures, and fallback rate.

**Oral-defence sentence:**  
“A larger interface description can still reduce cost-to-serve if it produces smaller observations, fewer recovery turns, and a higher success rate; the live v1/v2 batteries are needed to prove whether that trade-off actually pays off.”

---

## 3. Guardrail layer

Prompt instructions are advisory; code guardrails are enforcement.

The reviewed implementation contains:
- a turn cap to stop non-concluding loops;
- a token budget ceiling to bound runaway cost;
- action de-duplication to prevent repeated identical reads or writes;
- an explicit `confirm` autonomy setting;
- a hostile-input detector for defined attack families.

The autonomy gate is placed directly in front of the irreversible `issue_decision_letter` action rather than in front of the entire agent. Read-only investigation can therefore remain autonomous, while the consequential write requires confirmation.

Hostile member narrative is treated as untrusted data. When a defined hostile-input family is detected, the run fails closed to human escalation and produces zero gated writes. This detector is intentionally narrow and should not be presented as a universal prompt-injection solution.

**Oral-defence sentence:**  
“We gate consequences, not intelligence: the agent can investigate autonomously, but the irreversible write is code-gated.”

---

## 4. Tool-selection design

The final tool set is seven tools, selected for task necessity and discriminability rather than maximum capability count.

Two candidate tools were removed:
- `lookup_member`, because the member-to-policy relationship can be resolved inside `get_policy_context` / line review rather than adding another model-visible dependency;
- `get_required_document_rule`, because document requirements are naturally part of line review and can be returned by `review_claim_line`.

A coverage interface requiring `policy_id` was redesigned rather than exposed directly, because the model may not know that identifier at the time it needs to review a line.

The nine-to-seven reduction therefore improves more than prompt size: it also reduces the model's action-selection surface, removes unnecessary dependencies, and reduces opportunities for loop and binding errors.

**Oral-defence sentence:**  
“We use the shortest defensible tool list: consolidate facts that always belong together, but keep operations separate when they have distinct evidence, conditional use, or useful parallelism.”

---

# Phase B Status

Phase B strand review is complete.

**Current conclusion:**  
- Descriptor / ACI design: approved.
- Controlled experiment design: approved; live effectiveness pending.
- Guardrail layer: approved.
- Tool-selection design: approved.
- Blocking correction found: none.

**Next step:**  
Wait for the team to integrate agreed reviews and publish the frozen commit, hashes, deterministic-check confirmation, and final live-run command. Do not run the measured Gemini v1 battery before that freeze.
