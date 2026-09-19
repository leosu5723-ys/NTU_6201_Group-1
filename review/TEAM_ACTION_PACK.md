# PE6201 Assignment 2 Problem A: Team Execution Guide

**Release:** R2 (2026-09-08). Replaces the incomplete earlier review pack.
**Team:** B-1, six members  
**Current stage:** Integrated engineering candidate completed; team review required before the experimental freeze  
**Audience:** All six team members  
**Companion file:** [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md)

> This is the team's single working guide. Please read the project overview and common workflow first, then follow the section under your own name. The immediate work is to author assigned case contracts first, then review the code; use your own API key for the assigned live-model test only after SHI SHUYI shares the approved frozen commit and final run instruction.

## Distribution and reading order

1. Open `PE6201_A2_PHASE_A_CASE_AUTHORING_R2.zip` first. Read its `START_HERE.md`, this guide, the official Appendix A, and your worksheet section. This package contains no answer key, Agent trajectories or result tables.
2. Return your independently written case contracts before opening `PE6201_A2_PHASE_B_CODE_REVIEW_R2.zip`. That separate package contains answers and full engineering evidence. The Phase B file links below refer to files inside that package; they are intentionally absent from Phase A.
3. The Phase B ZIP is a local engineering snapshot, not a Git clone or frozen live-run release. Use it for code review and free offline checks only. A frozen repository commit and final commands will be issued later.

Allocation authority: [`case_review_assignments.md`](case_review_assignments.md). Do not confuse Phase A case authorship with the different Phase E cross-review allocation. Complete a personal copy of the worksheet; do not edit the generated blank distribution template.

## 1. What this project is

We are completing **Problem A: Health-insurance claim first response**. The system receives one synthetic health-insurance claim and uses a single ReAct Agent to gather evidence before producing one of three ordinary business responses:

1. `approve_in_principle`;
2. `request_document`;
3. `escalate`.

The Agent is not a chatbot UI and is not a production insurance system. It is a course experiment designed to show how an Agent loop, tool interfaces, guardrails, evaluation and cost analysis work together.

The implementation uses one integrated codebase rather than six separately coded modules. This prevents the Agent loop, tool schemas, evaluation labels and cost measurements from drifting apart. Team contribution therefore comes from real case design and review, strand ownership, live execution, result interpretation, report review and the video, not from artificially splitting one coherent Agent into incompatible pieces.

## 2. How the integrated Agent has been developed

### Step 1: Freeze the task and data boundary

The team selected Problem A and kept all 15 supplied cases and reference data unchanged. We added 25 candidate cases in the permitted extension area, giving:

- 40 total cases;
- exactly 10 negative cases;
- 30 ordinary cases run once;
- 10 negative cases run three times;
- 60 trials in one complete model battery.

The default backend is `scripted`, so the complete deterministic workflow runs offline without an API key.

### Step 2: Build one manual ReAct Agent

The Agent loop is handwritten in [`agent.py`](../agent.py). It does not use LangChain, LangGraph or a multi-agent framework. On each turn it receives either a tool-call move or a final structured result.

The seven bounded tools are implemented in [`tools.py`](../tools.py):

1. `get_claim`;
2. `get_policy_context`;
3. `review_claim_line`;
4. `get_preauthorisation`;
5. `get_hospital_status`;
6. `find_prior_decision`;
7. `issue_decision_letter`.

Independent calls can run in the same turn, but a call cannot be grouped with another call that depends on its output. Every ordinary approval, document request or business escalation is recorded exactly once through `issue_decision_letter` after confirmation. A hostile instruction inside the member narrative fails closed and produces no write.

### Step 3: Build the evaluation before live model runs

The evaluation harness in [`harness.py`](../harness.py) checks fixed fields such as decision, trigger, missing item, totals, line dispositions and action count. Ten representative cases also enter a human-judgement queue for explanation and evidence quality.

The saved candidate scripted trajectories validate the code and scoring pipeline. They do **not** measure live-model intelligence. Live-model quality can only be discussed after the six measured batteries are run from one frozen commit.

### Step 4: Build the required experiments

The repository now contains:

- v1 versus v2 Agent–Computer Interface experiment in [`prompt_experiment.py`](../prompt_experiment.py);
- sequential versus safe-parallel comparison in [`parallel_experiment.py`](../parallel_experiment.py);
- ten guardrail checks in [`guardrail_harness.py`](../guardrail_harness.py);
- two reproducible deletion failures in [`failure_experiments.py`](../failure_experiments.py);
- three-layer cost, sensitivity and break-even logic in [`cost_model.py`](../cost_model.py).

### Step 5: Verify the current engineering candidate

Current deterministic evidence:

- 101/101 unit tests passed;
- 60/60 scripted trials passed;
- 30/30 repeated negative trials passed;
- 10/10 guardrail cases passed;
- sequential and parallel modes both passed 40/40 cases;
- no live API request has been made;
- no API cost has been incurred;
- no API key is stored in the repository.

The current engineering candidate is ready for team review, but it is **not yet the frozen live-run commit and not submission-ready**.

## 3. Why every member must participate now

The engineering scaffold can be integrated centrally, but the remaining work cannot be completed truthfully by one person on behalf of everyone. The list below separates the instructor's explicit requirements from the team's chosen evidence process.

### Explicit requirements from the brief, FAQ and document updates

1. Every member writes 5–8 evaluation cases.
2. Every member runs one full live battery on their own key.
3. In a six-person team, the expected design is five different v2 model families plus one v1 pass on a model already run under v2.
4. Every v2 runner uses the identical evaluation set and identical v2 prompt, with the model name as the only changed variable. The brief also states that the runs use the same commit.
5. The models span at least two price tiers, with no duplicate family among the five v2 models.
6. Any member may be asked about any submitted code block and must be able to explain what it does and why it is present.
7. Every member speaks in the five-minute recorded demonstration.

### Team process chosen to satisfy those requirements

The instructor does not prescribe a formal code-review form, a case-signoff JSON file or our exact ten-case cross-review allocation. Those are internal controls chosen by the team. We use them to make authorship traceable, prevent label changes after model output is seen, and prove that all six batteries came from one reviewed experimental state.

The sequence is therefore: members author their assigned evaluation contracts and inspect their declared strands; agreed corrections are integrated; one commit is frozen; then all six members run their assigned live batteries. Free offline scripted tests may be run after you return your independently written Phase A contracts, because the code package includes expected outputs.

A signature means that the member actually reviewed the named cases or strand. It must not be added merely to make the submission look complete.

## 4. Common workflow for everyone

### Phase A: Author and review your assigned evaluation cases now

Open [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md) and find the section under your name. The worksheet shows source facts but deliberately does not show the Agent's output or the answer-key label. The current rows are candidate source material prepared for integration; merely confirming them is not enough. Your completed decision contract, rationale, fixed checks and `must_record` requirements are the evaluation case you author.

For every assigned case:

1. Read the claim, policy context, duplicate result, hospital status and line reviews.
2. Apply the official Appendix A routing order yourself.
3. Write the expected decision.
4. If it is an escalation, write the exact trigger and escalation target.
5. If it is a document request, write the exact missing item.
6. If it is an approval, calculate the approved and refused totals and list every line disposition. For a document request, retain already-resolved lines where required; for an early escalation, explain why further line pricing is not applicable.
7. Record the evidence IDs that the response must preserve, such as policy, pre-authorisation or exclusion evidence.
8. Write one case-specific business-rule observation.
9. Author the final evaluation contract for that case: explain its decision boundary and specify or materially improve at least one case-specific expected field, rationale or `must_record` requirement. A bare “looks correct” is not enough.

If a case appears to match two routing rows or no routing row, flag it instead of inventing a new rule. Do not open the answer key or Agent result file while doing this phase.

**Return:** your completed worksheet section and any proposed corrections.

### Phase B: Review your declared strand now

Read [`CODE_WALKTHROUGH.md`](CODE_WALKTHROUGH.md), then inspect the specific files listed under your name below. You do not need to memorise Python syntax or rewrite the code. You must understand the purpose, check that the design is defensible and return:

```text
Strand reviewed:
One design choice I can explain:
One question, correction, or "approved as written":
Name and date:
```

### Phase C: Wait for the experimental freeze

After finishing the code, strand and case review, wait before using your API key. After Phase A is returned, offline scripted tests are allowed and encouraged at this stage. SHI SHUYI will first merge agreed corrections, obtain team approval and share:

- the exact frozen Git commit;
- the final fixture, answer-key, script and prompt hashes;
- the final command for each member;
- confirmation that all deterministic checks still pass.

After the freeze, nobody may silently change the cases, labels, prompt, tools or scoring rules to improve a model result.

### Phase D: Run your assigned live battery after the freeze

Use [`docs/live_battery_instructions.md`](../docs/live_battery_instructions.md) as the command authority.

This is the stage in which every member uses their own API key to test the assigned live model. The delay in Phase C is only to ensure that all six members run exactly the same reviewed code, cases, labels and prompt. It is not a cancellation of the live tests.

Before executing:

```bash
git checkout FROZEN_COMMIT
python3 -m unittest discover -s tests -v
python3 A2_reference_data/check_my_data.py
python3 run_eval.py
git status --porcelain
```

The tests and data checker must pass, the scripted run must show 60/60, and `git status --porcelain` must print nothing.

Run the command once without `--execute` first. This is a free preflight and makes no network request. Only then enter your own key temporarily in the terminal and run the measured battery.

```bash
export OPENROUTER_API_KEY='YOUR_OWN_KEY'
```

Never send the key to the group, put it in a document, commit it, or show it in a screenshot. Replace both spend values in the final command with your true prior A2 spending and calendar-month spending. The limits are US$3 for this A2 battery and US$25 per key owner in the calendar month.

Keep all failures. Do not delete failed trials, selectively rerun them, edit the JSON or change the model route. The runner checkpoints every trial and resumes only unfinished trials after an interruption.

**Return:** the complete generated JSON under `results/live/`, plus:

```text
Model and prompt version:
Observed pass rate:
Most important failure or surprising behaviour:
Was the quality worth the measured cost? Why?
Name and date:
```

### Phase E: Cross-review human judgement after the live results

After all six batteries are merged, SHI SHUYI will generate the final ten-case judgement surface. Each reviewer checks whether the explanation and evidence trail satisfy the fixed `must_record` requirements. This is separate from the machine code check.

Use `pass`, `fail` or `uncertain`, cite the visible evidence, and do not repair the model output. Proposed cross-review allocation:

| Reviewer | Cases to judge |
|---|---|
| Meng Sijia | CLM-8952, CLM-9019 |
| SHI SHUYI | CLM-8894, CLM-8941 |
| Su Yang | CLM-8842, CLM-8901 |
| Isha Kirti Ghia | CLM-8888, CLM-8910 |
| Sun Hanyu | CLM-8925 |
| Zhang Jiayang | CLM-8933 |

### Phase F: Interpret results, review the report and record the video

The team will jointly decide:

- which model met the quality bar at the lowest cost;
- which negative families separated the models;
- whether v2 earned its additional standing prompt cost over v1;
- whether the conclusion survives cost sensitivity analysis;
- what the team would not deploy and why.

Every member must check that the final report accurately represents their work and record an approximately 30–40 second video segment aligned with their strand or live result.

## 5. Individual instructions

## Meng Sijia

### Your responsibilities

- Review the evaluation harness and scripted evaluation design.
- Author and review seven assigned evaluation contracts.
- Run the Gemini 2.5 Flash Lite v2 measured battery after the freeze.
- Cross-review two final judgement cases.
- Explain evaluation design or the Gemini v2 result in the report/video.

### Phase A cases

`CLM-8842`, `CLM-8901`, `CLM-8910`, `CLM-9001`, `CLM-9007`, `CLM-9012`, `CLM-9018`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to partial payment, exact document naming, lapsed policy, pre-authorisation boundary dates, exact annual-limit equality and multi-line reconciliation.

### Phase B files

- [`harness.py`](../harness.py): trial policy and machine code checks;
- [`evaluation/code_expectations_A.json`](../evaluation/code_expectations_A.json): fixed structural oracle;
- [`review/JUDGEMENT_REVIEW_SCRIPTED.md`](JUDGEMENT_REVIEW_SCRIPTED.md): current human-review format;
- [`artifacts/EVIDENCE_TABLES.md`](../artifacts/EVIDENCE_TABLES.md): current deterministic evidence.

Be able to explain why negatives run three times, why 40 cases become 60 trials, and why scripted 60/60 validates the harness but not live-model quality.

### Phase D model

```bash
python3 live_battery.py --model google/gemini-2.5-flash-lite --prompt-version v2 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

### Phase E judgement

Review `CLM-8952` and `CLM-9019`.

### Final evidence you return

- seven completed case records;
- evaluation-harness strand response;
- complete Gemini v2 JSON;
- short result interpretation;
- two judgement verdicts;
- final report approval and video contribution.

## SHI SHUYI

### Your responsibilities

- Coordinate the integrated build and experimental freeze.
- Review the ReAct loop, tools and overall consistency.
- Author and review seven assigned evaluation contracts.
- Run the Qwen3 30B A3B Instruct v2 measured battery after the freeze.
- Merge evidence, coordinate the report and final submission checks.

### Phase A cases

`CLM-8850`, `CLM-8888`, `CLM-8925`, `CLM-9002`, `CLM-9008`, `CLM-9013`, `CLM-9019`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to missing pre-authorisation, routing priority, annual-limit escalation, mixed covered/excluded lines and multi-condition approvals.

### Phase B files

- [`agent.py`](../agent.py): manual loop, final/action integrity and case isolation;
- [`tools.py`](../tools.py): seven bounded tools and irreversible write validation;
- [`guardrails.py`](../guardrails.py): caps, duplicate protection, hostile input and confirmation;
- [`docs/architecture.md`](../docs/architecture.md): system structure;
- [`docs/tool_dependency_design.md`](../docs/tool_dependency_design.md): safe call ordering.

Be able to explain why ordinary decisions are written exactly once, why hostile-input safety escalation performs zero writes, and why the integrated implementation is reviewed by strand rather than split into six separate systems.

### Phase D model

```bash
python3 live_battery.py --model qwen/qwen3-30b-a3b-instruct-2507 --prompt-version v2 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

### Phase E judgement

Review `CLM-8894` and `CLM-8941`.

### Final evidence you return

- seven completed case records;
- loop/tools and integration review;
- complete Qwen v2 JSON;
- short result interpretation;
- two judgement verdicts;
- frozen-commit record, merged evidence, report/video coordination and final approval package.

## Su Yang

### Your responsibilities

- Review the cost model, ledger assumptions, sensitivity analysis and break-even logic.
- Author and review seven assigned evaluation contracts.
- Run the Claude Haiku 4.5 v2 measured battery after the freeze.
- Cross-review two final judgement cases.
- Explain measured versus estimated cost in the report/video.

### Phase A cases

`CLM-8861`, `CLM-8894`, `CLM-8933`, `CLM-9003`, `CLM-9009`, `CLM-9014`, `CLM-9020`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to line-level exclusions, expired pre-authorisation, duplicate evidence, mixed payable/excluded totals and multi-line pre-authorisation.

### Phase B files

- [`cost_model.py`](../cost_model.py): three-layer formula, sensitivity and break-even;
- [`docs/cost_assumptions.md`](../docs/cost_assumptions.md): labour, fixed-cost and volume assumptions;
- [`config/model_catalog.json`](../config/model_catalog.json): model IDs and list prices;
- [`live_analysis.py`](../live_analysis.py): case-balanced live metrics and cost aggregation.

Be able to explain the difference between provider variable cost, expected human fallback cost and fixed monthly cost; why negative repetitions are not triple-weighted in cost-to-serve; and why a cheap model may become expensive if failures require human fallback.

### Phase D model

```bash
python3 live_battery.py --model anthropic/claude-haiku-4.5 --prompt-version v2 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

### Phase E judgement

Review `CLM-8842` and `CLM-8901`.

### Final evidence you return

- seven completed case records;
- cost-model strand response and checked assumptions;
- complete Claude v2 JSON;
- short result and cost interpretation;
- two judgement verdicts;
- final report approval and video contribution.

## Isha Kirti Ghia

### Your responsibilities

- Review the tools, dependencies and safe parallel call design.
- Author and review seven assigned evaluation contracts.
- Run the Llama 4 Maverick v2 measured battery after the freeze.
- Cross-review two final judgement cases.
- Explain tool design or the Llama result in the report/video.

### Phase A cases

`CLM-8874`, `CLM-8941`, `CLM-8960`, `CLM-9004`, `CLM-9010`, `CLM-9015`, `CLM-9021`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to non-panel hospitals, hostile narrative handling, missing documents, out-of-coverage dates and policy start/end boundaries.

### Phase B files

- [`tools.py`](../tools.py): tool arguments, bounded returns and evidence validation;
- [`docs/tool_dependency_design.md`](../docs/tool_dependency_design.md): dependency graph and early exits;
- [`parallel_experiment.py`](../parallel_experiment.py): sequential/parallel controlled comparison;
- [`artifacts/parallel_experiment.json`](../artifacts/parallel_experiment.json): measured deterministic results.

Be able to explain why policy and duplicate checks can run together, why line review waits for early eligibility checks, and why calls sharing one turn must not depend on each other's output.

### Phase D model

```bash
python3 live_battery.py --model meta-llama/llama-4-maverick --prompt-version v2 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

### Phase E judgement

Review `CLM-8888` and `CLM-8910`.

### Final evidence you return

- seven completed case records;
- tool/dependency strand response;
- complete Llama v2 JSON;
- short result interpretation;
- two judgement verdicts;
- final report approval and video contribution.

## Sun Hanyu

### Your responsibilities

- Review offline scripted evaluation, negative repetition and hostile-input handling.
- Author and review seven assigned evaluation contracts.
- Run the DeepSeek V3.2 v2 measured battery after the freeze.
- Cross-review one final judgement case.
- Explain reproducibility, negative stability or the DeepSeek result in the report/video.

### Phase A cases

`CLM-8917`, `CLM-8952`, `CLM-8971`, `CLM-9005`, `CLM-9011`, `CLM-9016`, `CLM-9022`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to policy service-date boundaries, hostile narrative versus trusted records, pre-authorisation date boundaries and ordinary follow-up claims.

### Phase B files

- [`script_builder.py`](../script_builder.py): deterministic trajectory generation;
- [`fixtures/scripted_trajectories_A.json`](../fixtures/scripted_trajectories_A.json): committed offline trajectories;
- [`harness.py`](../harness.py): negative trial policy and scoring;
- [`guardrail_harness.py`](../guardrail_harness.py): ten guardrail scenarios;
- [`artifacts/guardrail_checklist.json`](../artifacts/guardrail_checklist.json): current results.

Be able to explain why scripted results are reproducible, why negatives receive three independent trials, why hostile narrative is treated as untrusted data and why the key is never needed for the default run.

### Phase D model

```bash
python3 live_battery.py --model deepseek/deepseek-v3.2 --prompt-version v2 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

### Phase E judgement

Review `CLM-8925`.

### Final evidence you return

- seven completed case records;
- scripted/negative/guardrail strand response;
- complete DeepSeek v2 JSON;
- short result interpretation;
- one judgement verdict;
- final report approval and video contribution.

## Zhang Jiayang

### Your responsibilities

- Review tool descriptors, the v1-to-v2 ACI experiment and guardrails.
- Author and review five assigned evaluation contracts.
- Run the Gemini 2.5 Flash Lite v1 control battery after the freeze.
- Cross-review one final judgement case.
- Explain the controlled ACI comparison in the report/video.

### Phase A cases

`CLM-9006`, `CLM-9017`, `CLM-9023`, `CLM-9024`, `CLM-9025`

Complete your section in [`CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md). Pay particular attention to exact date boundaries, extra-document tolerance, multi-line reconciliation and the third hostile-input family.

### Phase B files

- [`prompt.py`](../prompt.py): routing rules, tool descriptors and move schema;
- [`prompt_experiment.py`](../prompt_experiment.py): frozen v1/v2 comparison;
- [`artifacts/prompt_comparison.json`](../artifacts/prompt_comparison.json): prompt hashes and sizes;
- [`guardrails.py`](../guardrails.py): code-level controls;
- [`docs/tool_selection_score.md`](../docs/tool_selection_score.md): nine-to-seven tool decision.

Confirm that v1 and v2 change only the `review_claim_line` descriptor and return shape, while the model, cases, other six descriptors, routing, guardrails and code remain fixed. Be able to explain why a larger prompt can still lower total operating cost if it prevents expensive failures.

### Phase D model

```bash
python3 live_battery.py --model google/gemini-2.5-flash-lite --prompt-version v1 --spent-to-date YOUR_A2_SPEND --monthly-spent-to-date YOUR_MONTHLY_SPEND --execute
```

Do not rerun or modify Meng's Gemini v2 battery. That frozen v2 result is the comparison partner.

### Phase E judgement

Review `CLM-8933`.

### Final evidence you return

- five completed case records;
- descriptor/ACI/guardrail strand response;
- complete Gemini v1 JSON;
- short v1-versus-v2 interpretation;
- one judgement verdict;
- final report approval and video contribution.

## 6. File map

| File | What it is | Who should use it |
|---|---|---|
| [`review/TEAM_ACTION_PACK.md`](TEAM_ACTION_PACK.md) | This complete team workflow and individual instructions | Everyone |
| [`review/CASE_WORKSHEETS.md`](CASE_WORKSHEETS.md) | Source-only facts and response fields for all 40 assigned cases | Everyone, Phase A |
| [`review/CODE_WALKTHROUGH.md`](CODE_WALKTHROUGH.md) | Plain-language explanation of the codebase and oral-defence questions | Everyone, Phase B |
| [`review/case_author_signoff_template.json`](case_author_signoff_template.json) | Final structured record of case-by-case authorship/revision | Integration owner after reviews |
| [`README.md`](../README.md) | Installation, commands and repository overview | Anyone reproducing the system |
| [`report/PE6201_A2_Report_Draft.md`](../report/PE6201_A2_Report_Draft.md) | Current report draft; live sections remain visibly pending | Everyone during final review |
| [`artifacts/EVIDENCE_TABLES.md`](../artifacts/EVIDENCE_TABLES.md) | Readable deterministic experiment results | Strand reviewers and report writers |
| [`docs/live_battery_instructions.md`](../docs/live_battery_instructions.md) | Authoritative live-run safety and command guide | Everyone, only after freeze |
| [`CONTRIBUTIONS.md`](../CONTRIBUTIONS.md) | Evidence-backed contribution ledger; pending work remains pending | Integration owner and all members |
| [`video/VIDEO_STORYBOARD.md`](../video/VIDEO_STORYBOARD.md) | Five-minute video structure and screen cues | Everyone after live analysis |

## 7. What not to do

- Review the code and cases now, but do not use your API key for the measured live-model battery before the frozen commit is announced.
- Do not look at the answer key or Agent output before completing your case review.
- Do not share an API key in Telegram, GitHub, documents, screenshots or result files.
- Do not change the model ID, provider route, prompt, cases or scoring during a battery.
- Do not delete failures or selectively rerun only failed cases.
- Do not sign another member's work or claim work that was not completed.
- Do not describe scripted 60/60 as live-model performance.

## 8. Completion checklist

### Before the freeze

- [ ] All 40 case worksheets completed by the assigned six members.
- [ ] Every case has a specific authorship or substantive-revision record.
- [ ] All proposed corrections merged before model output is viewed.
- [ ] Six strand-review responses returned.
- [ ] Team approves the final 40-case contract and current positive-heavy design.
- [ ] One clean commit selected and hashes recorded.

### After the freeze

- [ ] Five v2 batteries and one Gemini v1 battery completed.
- [ ] All six raw JSON files returned unchanged.
- [ ] Ten human judgement verdicts completed.
- [ ] Cost, reliability and sensitivity tables regenerated from live evidence.
- [ ] Every member reviews the final report and self-appraisal.
- [ ] Every member records or attends the agreed video segment.
- [ ] Final clean-clone and privacy verification passes.
- [ ] Final PDF, video link and ZIP are approved before submission.
