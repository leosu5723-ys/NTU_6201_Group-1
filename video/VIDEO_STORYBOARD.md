# Five-Minute Demonstration Storyboard

This storyboard fixes the flow and screen actions. Final spoken wording must be generated after the live results are frozen.

## 0:00 to 0:35: Meng Sijia

**Purpose:** Introduce the problem and what is being demonstrated.

**Screen:** Repository README and the three valid outcomes.

**Content:** Health-insurance claim first response; evidence must be retrieved before a conclusion; the harness, not a lucky demo, is the deliverable.

## 0:35 to 1:15: SHI SHUYI

**Purpose:** Explain the single-agent architecture.

**Screen:** Tool dependency diagram or concise repository map.

**Content:** Hand-written ReAct loop; claim first; policy and duplicate checks before line review; conditional pre-authorisation; confirmation gate before the only write.

## 1:15 to 1:50: Isha Kirti Ghia

**Purpose:** Explain the tool-interface decision.

**Screen:** `review_claim_line` descriptor and dependency rule.

**Content:** Why the policy-ID dependency in the scaffold was changed; why required-document status belongs in the bounded line-review return; why separate web or document tools were not added.

## 1:50 to 2:25: Zhang Jiayang

**Purpose:** Explain descriptors and guardrails.

**Screen:** v1 and v2 prompt diff, followed by guardrail checklist summary.

**Content:** The one-variable Gemini comparison; six-field descriptor contract; step cap, budget ceiling, de-duplication and confirm gate; three hostile-input cases.

## 2:25 to 3:05: Sun Hanyu

**Purpose:** Explain the evaluation design and model evidence.

**Screen:** Evaluation table and model battery table.

**Content:** 40 frozen cases, 10 negatives and 60 trials per model; code checks versus judgement checks; best model, negative-case spread and the most important model divergence. `[LIVE RESULTS REQUIRED]`

## 3:05 to 3:45: Su Yang

**Purpose:** Explain cost and the two reproduced failures.

**Screen:** Cost table followed by compact before-and-after failure table.

**Content:** Three cost layers, US$7.60 fallback and 8,000 monthly claims; dominant lever and break-even conclusion `[LIVE RESULTS REQUIRED]`; loop failure and missing-document interface failure.

## 3:45 to 4:40: Live negative-case demonstration

**Speaker:** SHI SHUYI, with another member controlling the screen if preferred.

**Command:**

```bash
python3 run_eval.py CLM-8941
```

**Show:**

- Member narrative contains a system-directed instruction.
- The narrative is treated as untrusted data.
- Decision is `escalate`.
- Trigger is `instruction_in_member_narrative`.
- `action_count` is zero.
- The hostile-input guardrail event appears in the record.

Alternative if the team wants a missing-evidence case:

```bash
python3 run_eval.py CLM-8901
```

This must request the itemised bill for line 45378 and record that ordinary first response exactly once after the confirmation gate.

## 4:40 to 5:00: Closing

**Speaker:** Meng Sijia.

**Screen:** Final evidence-status slide.

**Content:** State the selected model `[LIVE RESULT REQUIRED]`, the main deployment limitation and why the team would retain human confirmation.

## Recording checks

- Every member speaks.
- Total edited duration does not exceed five minutes.
- One negative case runs visibly rather than appearing only in a static table.
- The screen shows the same clean commit and result files cited by the report.
- No API key, terminal history containing a key or private local path is visible.
- Numbers are read from final tables rather than memory.
- The final script uses the members' real work and review evidence.
