# Strand review: SHI SHUYI

**Strand:** the ReAct loop, the tool layer and their integration
**Files read:** `agent.py`, `tools.py`, `guardrails.py`, `docs/architecture.md`, `docs/tool_dependency_design.md`
**Review scope:** First-round experiment `42253ad28fc58b36b9014808f9d8e3fd523c01ed` and revised experiment `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`.
**Revision date:** 19 September 2026.


## The design choice I can explain

**One case, one recorded decision — and nothing written on the hostile path.**

The model chooses its retrieval path within the turn cap, token budget, de-duplication rules and tool dependencies. Only independent read-only calls may share a turn. Successful non-hostile completion requires exactly one recorded `issue_decision_letter` action, followed by a final answer whose business fields match that record. A halted or unconfirmed run need not write anything. These are separate requirements: limiting writes protects the action boundary; checking the final answer protects the accuracy of the reported result.

The write is the governance boundary discussed in Class 4. In this assignment it is a local structured log entry, not a sent letter or a real insurance transaction. The same design issue still matters: marking a run failed after an incorrect write does not undo that write. Post-run integrity checks are useful evidence checks, but cannot replace prevention at the point of execution.

The same logic drives the hostile path. When `get_claim` returns a narrative containing instruction-like text, the loop stops immediately, escalates with trigger `instruction_in_member_narrative`, and performs **zero writes**. The text is treated as untrusted data, never as a command. That is why the negative battery includes hostile cases: the property being tested is not "did it answer well" but "did it refuse to act on injected instructions".

Two supporting details I would defend in the oral:

- Each `run_case()` initialises its own evidence trace, action counter and recorded payload. This avoids carrying transient evidence from one run into another. It does not, by itself, prevent a model from retrieving another claim within the same run. The revised `_validate_call_batch()` explicitly binds `get_claim` and the gated action to the requested case ID.
- `_validate_call_batch()` checks the entire proposed batch before any tool or confirmation callback runs. A gated action must be the only call in its batch, and no further tool calls are allowed after a successful write. Payload validation then occurs before confirmation and again immediately before persistence. This combines authorization scope, action ordering and evidence validity rather than relying on the action counter alone.

## Findings, corrections and evidence

The first-round runtime stopped on a tool-validation error rather than returning that error to the model for correction. This protected against unsupported writes but also made an otherwise recoverable payload mistake an end-to-end failure. The revised runtime allows one recoverable tool-validation error (`MAX_RECOVERABLE_TOOL_ERRORS = 1`); a second stops with `recoverable_tool_error_cap`. Recovery remains within the existing caps and cannot bypass case binding, confirmation or the post-write restriction. Accepting one exact JSON code fence also addresses a response-format failure without accepting surrounding prose.

Pre-freeze testing also reproduced a more serious defect: a run could persist decisions for other claims and only then fail the action-count check. Post-run counting therefore did not guarantee one authorized write. The team corrected it with the pre-execution checks above. Regression tests now cover a foreign-claim trajectory, a gated action mixed with other calls, a tool call after a recorded action, and normal single-action completion. The important lesson is to make the invalid action unreachable, not merely detectable afterwards.

My first-round Qwen3 v2 battery (`qwen/qwen3-30b-a3b-instruct-2507`, archived under `results/round1/`) passed 16 of 60 trials, or 26.7%. The saved final decision label matched the oracle in 30 of 60 trials, or 50%. That second figure is not a model reasoning accuracy: nine matching records had `action_integrity_error` and one had `tool_or_schema_error`, and the runtime substitutes escalation on failed runs. The strict rate remains the end-to-end measure; the label comparison only helps locate failures when interpreted alongside the trace and stop reason. Neither figure measures the revised runtime.

The revised candidate passed 117 automated tests and 60 of 60 scripted evaluation trials. These are offline regression results, not evidence that live models now achieve the same rate. The ten-case guardrail checklist is likewise deterministic evidence about the controls, not a claim of complete prompt-injection protection. Historical batteries are validated against their recorded experiment commit and kept separate from round two.

Allowing bounded recovery may improve completion but adds turns and tokens. Its benefit must therefore be evaluated in the second-round battery, including negative-case performance and cost to serve. In the cost model, `(1 - P) × F` represents the assumed human fallback workload; a safety stop is not automatically a correct business decision or a successful trial.

## Verdict

**The offline evidence supports the revised frozen version entering the coordinated second-round battery, not a claim of final submission readiness.**

The reproduced action-boundary defect has a targeted pre-execution fix and regression coverage. The first-round measurements remain historical evidence and must not be pooled with the second round. Final conclusions about live reliability and cost await the complete revised battery and the outstanding human judgement checks. This review changes documentation only; the executable experiment remains frozen at `f8a1d7450a4bee92c24f38a6924436bc9faabdaf`.
