# PE6201 A2 Implementation Contract

## Authority

The current A2 brief, FAQ, Document Updates, Appendix A routing table, supplied fixture generators and supplied answer key are authoritative. The scaffold is a starting point, not a specification.

## Fixed problem and routing

Problem A: health-insurance claim first response.

The only valid outcomes are:

- `approve_in_principle`: every line resolves as covered, covered with valid pre-authorisation, or excluded with its rule recorded.
- `request_document`: a required document or valid pre-authorisation is missing; the exact item, line and relevant date must be named.
- `escalate`: policy lapsed, date of service outside policy dates, claim total above remaining annual limit, duplicate prior decision, or instructions embedded in member-supplied narrative.

The routing rule and gated action are fixed. Tool names, signatures, grouping and return shapes are design decisions.

## Build constraints

- One hand-written ReAct agent. No framework owns the loop.
- No multi-agent implementation.
- Local fixture data only; no live records or irreversible external action.
- The submitted default is `BACKEND="scripted"` and runs without a key or network.
- Live model selection is isolated to configuration and one backend boundary.
- The irreversible action is simulated by one structured local log write behind the autonomy gate.
- `confirm` is the selected autonomy setting.

The frozen scripted set has a median of 4 turns and a legitimate maximum of 5. The deployment step cap is 8, leaving three recovery turns before a loud stop. The largest v2 scripted estimate is 15,763 tokens; the budget ceiling is 25,000, leaving approximately 59% headroom for tokenizer and response variation. These caps must be revisited if live traces show a legitimate run approaching either boundary.

## Evaluation contract

- 40 evaluation cases total.
- All 15 supplied cases remain byte-for-byte unchanged.
- 25 additions use new IDs and are generated reproducibly.
- Exactly 10 negative cases under the brief definition; the 15 supplied cases already contain 9.
- Ordinary cases receive one trial per model; negative cases receive three.
- Labels are fixed from Appendix A before model outputs are viewed.
- Code checks cover outcome, trigger, named missing item, gated-action count and case-specific fixed fields.
- Judgement checks cover whether the reason and evidence trail support the outcome.
- Every pass rate is reported with model, prompt version and trial count.

## Required experiments

1. Descriptor and return-shape v1 versus v2 on one fixed cheap model.
2. Sequential versus parallel execution on the same cases, with turns, tokens, cost and correctness.
3. One scripted full-system run that a marker can reproduce.
4. A live v2 model battery across five distinct model families and at least two price tiers.
5. Ten scripted guardrail cases, including at least three hostile-input cases.
6. Two scripted D7 failures: one loop-control failure and one distinct tool-interface failure.
7. Three-layer cost-to-serve model, sensitivity range, four measured levers and cheap-model break-even success rate.

## Evidence and provenance

- Generated data, generator, extended answer key, raw run records and derived tables travel together.
- Live smoke tests are separate from measured batteries.
- Raw responses, usage, latency, errors and configuration are preserved per trial.
- No live result, pass rate or cost is prewritten.
- A code or prompt change after a battery invalidates that battery and requires rerun.
- Prices and model IDs are rechecked on the run date.

## Final artefacts

- Public repository plus the same code files in the NTULearn folder.
- Reproducible README and `CONTRIBUTIONS.md`.
- Agent, tools, guardrails, fixtures, answer key, harness, raw results, result tables and cost model.
- Team report of at most 2,000 prose words in the required six-section order.
- Five-minute recorded demonstration with every member speaking and one negative case shown live.
- One collective team self-appraisal.

## Release gates

No paid battery begins until the evaluation set, answer key, v2 prompt and code commit are frozen. No remote push occurs without Kyle's review of the local candidate. No final package is called complete until a clean clone reproduces the scripted results without a key.
