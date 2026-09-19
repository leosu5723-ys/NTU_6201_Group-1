# PE6201 A2 — Phase B Strand Review (R2) — COMPLETED

**Member:** Meng Sijia  
**Date:** 2026-09-18  
**Assigned strand:** Evaluation harness / scripted evaluation design (`harness.py`, `code_expectations_A.json`, `JUDGEMENT_REVIEW_SCRIPTED.md`, `EVIDENCE_TABLES.md`)

---

## Formal Strand Review Response

**Strand reviewed:**  
Evaluation harness / scripted evaluation design (`harness.py`, `code_expectations_A.json`, `JUDGEMENT_REVIEW_SCRIPTED.md`, `EVIDENCE_TABLES.md`)

**One design choice I can explain:**  
**Why negative cases run 3 times:**  
In `harness.py`, the `run_set` function defaults to `trials_for = lambda case_id: 3 if is_negative(key[case_id]) else 1`. A case is classified as negative if its `expected_decision` is `request_document` or `escalate`. These decisions are safety-critical and highly sensitive to model stochasticity. A single trial might pass or fail due to incidental hallucination or formatting deviation. Running negative cases 3 times validates the model's stability and robustness under boundary conditions. If any of the 3 trials fails to trigger the correct escalation or document request, the model's variance on safety-critical paths is unacceptable.

**One question, correction, or “approved as written”:**  
**Approved as written** (With explanations for the remaining two core questions):

1. **Why 40 cases ultimately become 60 trials:**  
   According to `EVIDENCE_TABLES.md`, there are 40 cases but 60 trials. The two relevant 10-case lists must be kept separate. The **negative cases** are CLM-8888, CLM-8894, CLM-8901, CLM-8910, CLM-8917, CLM-8925, CLM-8933, CLM-8941, CLM-8952, and CLM-9025; these are the cases whose expected decision is `request_document` or `escalate`, so each runs three times. Therefore, the calculation is: **10 negative cases × 3 trials + 30 ordinary cases × 1 trial = 30 + 30 = 60 trials**. `JUDGEMENT_CASE_IDS` is instead the separate human-judgement queue: it includes CLM-8842 and CLM-9019 (ordinary approval cases) and does not include CLM-8917 or CLM-9025. It must not be used to identify the negative cases or the repetition policy.

2. **Why scripted 60/60 only proves the harness / scoring pipeline works, not live model quality:**  
   `EVIDENCE_TABLES.md` explicitly states these are *Scripted deterministic estimates, not live API billing evidence.* and marks the live run as `LIVE RUN PENDING`. The `run_set` function executes predefined `scripted_scripts` rather than actual LLM inference.
   - **What it proves:** The evaluation framework itself (the `code_check` function in `harness.py`) is logically correct. It accurately parses JSON and matches `decision`, `trigger`, `missing`, `approved_total`, and `line_dispositions`. It proves the scoring pipeline has no bugs and correctly scores a correct format.
   - **What it does NOT prove:** It does not prove that a live model can generate the expected output when faced with unseen inputs. Scripted tests are "open-book exams" with fixed answers, whereas live models are "closed-book" and prone to hallucinations. Thus, scripted 60/60 is a **unit test for the pipeline**, not a **performance test for the live model**. True live model quality must wait for the actual API call results.

**Name and date:**  
Meng Sijia / 2026-09-18

---

# Personal Review Notes / Oral-Defence Preparation

## 1. Harness trial policy: negative cases and repetition

The harness deliberately runs negative cases three times while positive cases run once. This is not arbitrary. Negative decisions (`request_document`, `escalate`) are safety-critical and must be robust against model stochasticity. A single lucky or unlucky trial could misrepresent the model's reliability. Triple repetition gives a clearer signal of whether the model consistently triggers the correct escalation or document request. If any of the three trials fails, the model's variance is unacceptable for production.

**Oral-defence sentence:**  
“We repeat negative cases not to inflate the trial count, but to measure stability on the decisions that matter most.”

---

## 2. From 40 cases to 60 trials

The arithmetic is straightforward once the case mix is known. There are 10 negative cases (CLM-8888, 8894, 8901, 8910, 8917, 8925, 8933, 8941, 8952, and 9025) and 30 ordinary cases. Each negative case contributes 3 trials, each ordinary case contributes 1 trial. Total = 10×3 + 30×1 = 60. This matches the harness trial policy and the `EVIDENCE_TABLES.md` summary. The human-judgement queue is a different 10-case list: it overlaps the negative list in eight cases, but also includes ordinary cases CLM-8842 and CLM-9019, while CLM-8917 and CLM-9025 are negative cases outside that queue.

**Oral-defence sentence:**  
“The 40-to-60 expansion is a deliberate sampling strategy: it concentrates extra trials on the negative decision cases, not on the separate human-judgement queue.”

---

## 3. Scripted 60/60 versus live model quality

The scripted harness passes 60/60 because it runs deterministic `scripted_scripts`, not live LLM inference. This validates the scoring pipeline: `code_check` correctly parses and compares JSON fields, and the harness correctly applies trial policies. However, it says nothing about how a real model will perform on unseen inputs. Scripted tests are open-book with fixed answers; live models are closed-book and prone to hallucination. Therefore, the 60/60 result is a unit test for the evaluation machinery, not a performance test for the model.

**Oral-defence sentence:**  
“A green scripted harness tells us the ruler is accurate, not that the student can pass the exam.”

---

## 4. Judgement review and evidence tables

`JUDGEMENT_REVIEW_SCRIPTED.md` and `EVIDENCE_TABLES.md` document the human-judgement layer. The judgement review specifies, for each selected case, what the reason and tool evidence must support. It is not a substring match; it requires a human to verify that the narrative actually justifies the decision. `EVIDENCE_TABLES.md` maps code-checked fields versus human-judged fields per case, making clear which cases need human eyes. Together they keep the evaluation honest: deterministic checks handle fixed fields, while humans handle reason quality and evidential sufficiency.

**Oral-defence sentence:**  
“Code checks catch format errors; humans catch reasoning errors—the two layers are complementary.”

---

# Phase B Status

Phase B strand review is complete.

**Current conclusion:**  
- Harness design: approved.  
- Trial policy for negative cases: approved.  
- Scripted vs live distinction: approved; live effectiveness pending.  
- Judgement review and evidence tables: approved.  
- Blocking correction found: none.