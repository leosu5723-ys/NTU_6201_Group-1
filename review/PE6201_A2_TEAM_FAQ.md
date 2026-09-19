# PE6201 A2 · Team FAQ (current stage)

**Problem A · Team B-1 · Frozen version `e64d2aa`**

This is the current-stage reference for the team assistant. If your question is about the project, the answer should be here or in the documents this file points to.

---

## 1 · Where are we now?

The engineering work is finished. The frozen version is on GitHub at commit `e64d2aa`:

```
https://github.com/leosu5723-ys/NTU_6201_Group-1
```

What is already done: the single-agent ReAct loop, the seven tools, the 40-case evaluation set with exactly 10 negative cases, the offline scripted harness, the ten guardrail cases, the v1/v2 ACI experiment, the sequential/parallel comparison, the two failure reproductions, and the three-layer cost model. 101 unit tests pass and the offline scripted run passes 60/60.

What is still missing: the six live model batteries, the ten human judgements, the report's live numbers, the self-appraisal, the video, and the final package.

---

## 2 · What do I personally have to do?

Every member has four deliverables:

1. **Evaluation cases** — author the contracts for your assigned cases.
2. **Strand review** — read your declared strand and report one design choice you can explain, plus any question, correction or "approved as written".
3. **Live battery** — run your assigned model once, on your own API key, and return the generated JSON.
4. **Video segment** — speak your part in the five-minute demonstration.

Your assigned cases are listed in `CASE_WORKSHEETS.md` and `TEAM_ACTION_PACK.md`.

---

## 3 · How do I run my battery?

```bash
git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
cd NTU_6201_Group-1
git checkout e64d2aa
python3 -m unittest discover -s tests -q   # expect 101 tests OK
python3 run_eval.py                        # expect 60/60
```

Free dry run first (no network, no cost):

```bash
python3 live_battery.py --model YOUR_MODEL_ID --prompt-version v2
```

Then the measured battery with your own key:

```bash
export OPENROUTER_API_KEY='***'
python3 live_battery.py --model YOUR_MODEL_ID --prompt-version v2 \
  --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
```

The result file is written under `results/live/`.

---

## 4 · Which model do I run?

| Member | Model | Prompt |
|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | v2 |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | v2 |
| Su Yang | `anthropic/claude-haiku-4.5` | v2 |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | v2 |
| Sun Hanyu | `deepseek/deepseek-v3.2` | v2 |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | v1 |

All six runs must use the **same commit, the same 40-case set and the same v2 prompt**. The model name is the only thing that may differ. That is what makes the comparison meaningful.

---

## 5 · What are v1 and v2?

They are two versions of the same system prompt. The only difference is the descriptor and return shape of one tool, `review_claim_line`.

- **v1** describes the tool vaguely and returns raw nested policy/procedure/document records (463 characters, about 115 tokens per call).
- **v2** states the types, when to use it, what it returns (one 8-field object, about 160 tokens maximum), and what a failure means. Its descriptor is longer but its return is smaller (227 characters, about 56 tokens).

The whole prompt grows from 7,630 to 8,068 characters, so v2 costs slightly more per turn. The experiment asks whether that extra standing cost earns itself back by preventing failures.

To compare prompt versions you must hold the **model** fixed. That is why v1 runs once, on the same model as one of the v2 runs (Gemini 2.5 Flash Lite), and not on every model.

---

## 6 · What is a negative case?

A negative case is an evaluation case whose correct outcome is **not** the acting outcome. In Problem A the three outcomes are `approve_in_principle`, `request_document` and `escalate`; the act is the approval, so a negative case is one that must ask or escalate.

Negative cases get **three trials** each because they are the ones that flip between runs, and a single trial cannot tell a real refusal from a lucky one. Ordinary cases get one trial. 30 ordinary cases plus 10 negatives at three trials each gives 60 trials per model.

---

## 7 · How much will this cost?

One battery is 56 runs of the evaluation set. On the cheap tier that is about US$0.27. On the mid tier it is about US$2.76. A frontier model would exceed the whole course allowance, which is why we do not use one.

The runner refuses to start a battery that would push you past the US$3 A2 cap or the US$25 calendar-month cap. Pass your real spend-to-date if you have already used your key.

---

## 8 · Where do I find things?

| What | Where |
|---|---|
| Progress and status | `review/PE6201_A2_PROGRESS_BOARD.md` |
| Your cases and full instructions | `review/TEAM_ACTION_PACK.md` |
| Your case source facts | `review/CASE_WORKSHEETS.md` |
| Code explanation and defence questions | `review/CODE_WALKTHROUGH.md` |
| Live run safety and commands | `docs/live_battery_instructions.md` |
| Tool design reasoning | `docs/tool_selection_score.md` |
| Dependency rule | `docs/tool_dependency_design.md` |
| Cost assumptions | `docs/cost_assumptions.md` |
| Experiment evidence | `artifacts/EVIDENCE_TABLES.md` |
| Report draft | `report/PE6201_A2_Report_Draft.md` |
| Video structure | `video/VIDEO_STORYBOARD.md` |
| Who did what | `CONTRIBUTIONS.md` |

---

## 9 · What should I not do?

- Do not share your API key in the group, in a file or in a screenshot.
- Do not edit the result JSON, and do not delete failing trials.
- Do not change the model, prompt, cases or scoring during a battery.
- Do not sign for another member's work.

---

## 10 · What do I send back?

1. Your completed strand review (one design choice you can explain, plus any question or correction).
2. The generated JSON from `results/live/`.
3. These four short answers:

```
Model and prompt version:
Observed pass rate:
Most important failure or surprising behaviour:
Was the quality worth the measured cost? Why?
Name and date:
```

---

## 11 · Note on one case reassignment

`CLM-9013` and `CLM-9012` are two different claims. The original allocation gave `CLM-9012` to Meng Sijia and `CLM-9013` to SHI SHUYI. Meng's submitted document instead reviewed `CLM-9013`, so `CLM-9012` was left uncovered and SHI SHUYI authored it during integration.

Final allocation after integration: Meng Sijia authors 6 cases (`CLM-8842`, `CLM-8901`, `CLM-8910`, `CLM-9001`, `CLM-9007`, `CLM-9018`) and her `CLM-9013` review is retained as an additional cross-check; SHI SHUYI authors 8 cases (`CLM-8850`, `CLM-8888`, `CLM-8925`, `CLM-9002`, `CLM-9008`, `CLM-9012`, `CLM-9013`, `CLM-9019`). All 40 cases are covered exactly once.

If someone asks about `CLM-9012` or `CLM-9013`, explain this reassignment rather than telling anyone they owe a contract they do not owe.
