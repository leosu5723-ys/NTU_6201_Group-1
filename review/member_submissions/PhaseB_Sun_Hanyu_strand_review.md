# PE6201 A2 — Phase B Strand Review (R2) — COMPLETED

**Member:** Sun Hanyu  
**Date:** 2026-09-19  
**Assigned strand:** Offline scripted evaluation, negative repetition and hostile-input handling (`script_builder.py`, `fixtures/scripted_trajectories_A.json`, `harness.py`, `guardrail_harness.py`, `artifacts/guardrail_checklist.json`)

---

## Formal Strand Review Response

**Strand reviewed:**  
Offline scripted evaluation, negative repetition and hostile-input handling (`script_builder.py`, `fixtures/scripted_trajectories_A.json`, `harness.py`, `guardrail_harness.py`, `artifacts/guardrail_checklist.json`)

**One design choice I can explain:**  
**Why the scripted results are reproducible and why negative cases run three times:**  

`script_builder.py` constructs the committed trajectories from the local claim facts and tool behaviour, then saves them to `fixtures/scripted_trajectories_A.json`. It does not call a live model, read the answer key or require a network request. The scripted backend can therefore replay the same bounded tool calls and structured outcomes offline.

In `harness.py`, `is_negative` identifies cases whose expected decision is `request_document` or `escalate`. `run_set` assigns three trials to those cases and one trial to ordinary positive cases. This produces 30 positive trials plus 30 repeated negative trials, or 60 trials in total. The repetition is intended to test stability on safety-sensitive boundary decisions, not to inflate a model-quality score.

**One question, correction, or “approved as written”:**  
**Approved as written** (with the following checks recorded):

1. **Scripted evaluation boundary:** The scripted trajectory fixture and `harness.py` scoring checks validate the deterministic evaluation and scoring pipeline. A scripted 60/60 result does not measure live-model intelligence or replace the later live battery.

2. **Negative repetition:** The three-trial policy is applied from the fixed expected decision labels. It makes instability on document-request and escalation paths visible while keeping ordinary positive cases at one trial.

3. **Hostile-input handling:** `script_builder.py` checks the member narrative through the guardrail's untrusted-text inspection before continuing with policy and line lookups. The hostile-input path stops ordinary processing and does not issue a decision letter. `guardrail_harness.py` checks overt override text, tool-result impersonation and role-style instructions; the committed checklist records all ten guardrail cases as passed.

**Name and date:**  
Sun Hanyu / 2026-09-19

---

# Personal Review Notes / Oral-Defence Preparation

## 1. Scripted trajectories and reproducibility

The scripted backend is a deterministic replay layer. `script_builder.py` derives trajectories from the local claim rows and bounded tool results, while `fixtures/scripted_trajectories_A.json` stores the resulting call-and-response sequence for review and replay. Because this path does not make an API request, the default evaluation can be repeated without a key, provider variability or network access.

**Oral-defence sentence:**  
“The scripted fixture tests whether the evaluation and scoring pipeline behaves consistently; it is not a substitute for measuring a live model.”

## 2. Negative cases and the 40-to-60 trial design

`harness.py` treats `request_document` and `escalate` as negative or boundary decisions. Those cases run three times because a single run could hide instability on safety-sensitive routes. With 30 ordinary cases and 10 negative cases, the total is `30 × 1 + 10 × 3 = 60` trials.

**Oral-defence sentence:**  
“The extra repetitions are concentrated on boundary decisions to test stability, not to present 60 scripted trials as 60 independent ordinary cases.”

## 3. Hostile member narratives are untrusted data

The member narrative is not allowed to redefine policy or imitate a trusted tool result. The guardrail path detects the hostile pattern, escalates with the `instruction_in_member_narrative` trigger and keeps `action_count` at zero. In particular, it prevents the irreversible `issue_decision_letter` action from being reached on the hostile-input path.

**Oral-defence sentence:**  
“A member narrative can describe a claim, but it cannot become a system instruction or evidence source.”

## 4. Guardrail checklist and evidence boundary

`guardrail_harness.py` covers turn caps, token ceilings, duplicate actions, confirmation and autonomy gates, and three hostile-input families. `artifacts/guardrail_checklist.json` records the expected and observed guardrail outcomes, with the current deterministic checklist showing 10/10 passed. This is evidence that the coded controls and checklist are working on the supplied scenarios; it does not claim that every possible prompt-injection pattern is detected.

# Phase B Status

Phase B strand review is complete.

**Current conclusion:**

- Scripted trajectory generation: approved.
- Negative-trial policy and 40-to-60 trial accounting: approved.
- Hostile-input handling and zero-write escalation path: approved.
- Guardrail checklist: approved; current deterministic result is 10/10 passed.
- Blocking correction found: none.
