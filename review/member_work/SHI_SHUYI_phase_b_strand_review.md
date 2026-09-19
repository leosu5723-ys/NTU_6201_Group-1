# Strand review — SHI SHUYI

**Strand:** the ReAct loop, the tool layer and their integration
**Files read:** `agent.py`, `tools.py`, `guardrails.py`, `docs/architecture.md`, `docs/tool_dependency_design.md`
**Status:** draft for SHI SHUYI to read, correct if needed, and own. Nothing here is signed on anyone's behalf.

## The design choice I can explain

**One case, one recorded decision — and nothing written on the hostile path.**

The loop is allowed to call read-only tools as many times as it needs, in any order it needs, but the case ends with **exactly one** call to the gated action (`issue_decision_letter`), and the business fields of that call must match the model's final answer. If the count is wrong, or the final answer disagrees with what was actually recorded, the run is rewritten as an escalation with `stopped_by = "action_integrity_error"` rather than being accepted.

That is deliberate. The system's whole reason for being on Class 4's rung 7 is that it can write. A first-response system that writes a decision letter is making something irreversible, so the invariant has to be *checked*, not *hoped for*. Counting the writes and cross-checking them against the final answer is cheap, deterministic, and catches the failure mode that matters: a model that narrates one decision while recording another.

The same logic drives the hostile path. When `get_claim` returns a narrative containing instruction-like text, the loop stops immediately, escalates with trigger `instruction_in_member_narrative`, and performs **zero writes**. The text is treated as untrusted data, never as a command. That is why the negative battery includes hostile cases: the property being tested is not "did it answer well" but "did it refuse to act on injected instructions".

Two supporting details I would defend in the oral:

- Each case runs through a single `run_case()` call, and the evidence list, action counter and recorded action payload are all initialised **inside** that function. `harness.py` then iterates the case ids one at a time. Nothing carries over between cases, so a decision cannot cite a tool result produced for a different claim.
- The gated action is validated *before* it is persisted (required evidence, disposition order, no fabricated resolved lines), so an invalid letter never reaches the receipt log at all.

## What I checked, and one honest limitation

I read the loop's error handling closely. `agent.py` wraps the whole turn loop in a single `try`; a tool that raises `ValueError` (an unsupported disposition, a missing evidence reference) propagates to the outer handler and **halts the run**, which is then recorded as a business escalation with `stopped_by = "tool_or_schema_error"`. The model never sees the validation error and never gets a retry.

This is fail-closed, and it is consistent with the cost model's `(1 - P) × F` fallback term — an unvalidatable decision goes to a human rather than being guessed. But it does mean the strict pass rate counts two different things as one failure: *the model chose the wrong outcome* and *the model chose correctly but produced an invalid payload*. **My own Qwen3 battery shows this clearly: 16/60 strict (26.7%) but 30/60 on decision agreement (50%).** I am recording it here rather than leaving it implicit, and the report states both numbers.

I would also flag what the battery validation caught during review: an earlier version of `validate_battery_set()` accepted a seventh battery duplicated from an existing one. It now requires exactly six and rejects tampering with the summary, the trial matrix or the decision receipts by recomputing their hashes.

## Verdict

**Approved as written, with the limitation above recorded.**

No further correction requested. The loop, the tool layer and the guardrails behave as the design documents describe them, and the two properties I care about — exactly one recorded decision per case, and zero writes on the hostile path — hold under test.
