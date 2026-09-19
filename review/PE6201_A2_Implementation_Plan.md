# Proposed Plan for Completing PE6201 A2

I will develop the assignment as one integrated system rather than splitting the code into separate pieces. This should keep the agent, tools, evaluation harness, guardrails and cost analysis consistent.

## Phase 1: Freeze the design and evaluation contract

First, I will establish the complete design before expanding the implementation:

- Map every A2 requirement from D0 to D7
- Define five testable conditions for a successful run
- Finalise the tool set and tool dependency rules
- Use `confirm` as the autonomy setting
- Define the v1 and v2 prompt versions
- Prepare a coverage plan for 40 evaluation cases
- Write the expected outcome before running the agent on every new case

This prevents us from changing the evaluation criteria after seeing model outputs.

## Phase 2: Build the agent and tool layer

I will adapt the official scaffold into a single hand-written ReAct agent for Problem A.

The system will:

- Retrieve the claim before making any decision
- Check the member’s policy, policy dates and remaining annual limit
- Review every treatment line separately
- Check exclusions, required documents and pre-authorisations
- Check hospital panel status
- Detect duplicate claims
- Support multiple independent tool calls in one turn
- Produce a structured decision record with a complete evidence trail
- Place the human confirmation gate immediately before the irreversible action

I will also correct the dependency problem in the scaffold, where `check_coverage` currently requires a policy ID that the model has not yet received.

## Phase 3: Build the evaluation set

The final evaluation set will contain:

- 40 cases in total
- All 15 supplied cases, unchanged
- 25 additional cases
- 10 negative cases in total
- Short and long claims
- Single-line and multi-line claims
- Valid, missing and expired pre-authorisations
- Partly payable claims
- Boundary cases around the remaining annual limit
- Missing required documents
- Duplicate and near-duplicate claims
- Hostile narratives and prompt-injection attempts

The generator, generated JSON data and extended answer key will all be committed. `check_my_data.py` must pass after every data change.

## Phase 4: Complete the reproducible harness and guardrails

The submitted default will remain the scripted backend, requiring no API key or network connection.

The harness will record:

- Decision and trigger
- Tool-call sequence
- Number of turns
- Input and output tokens
- Estimated or measured cost
- Latency
- Guardrails triggered
- Whether the irreversible action occurred

The system will include:

- Step cap
- Token budget ceiling
- Duplicate-action prevention
- Autonomy gate

A separate checklist of at least 10 guardrail cases will be created, including at least three hostile-input cases.

## Phase 5: Run the required experiments

The following experiments will be completed:

1. **Sequential versus parallel tool calling**
   Compare turns, tokens, cost and correctness using the same evaluation set.

2. **Prompt v1 versus v2**
   Run both versions on Gemini 2.5 Flash Lite while holding the model and data constant.

3. **Live model battery**
   Run the frozen v2 system on:

   - Gemini 2.5 Flash Lite
   - Qwen3 30B A3B Instruct
   - Claude Haiku 4.5
   - Llama 4 Maverick
   - DeepSeek V3.2

All v2 runs will use the same code commit, evaluation set and prompt. Model availability and pricing will be checked again immediately before the paid runs.

## Phase 6: Reproduce two failures

Two distinct failures will be created and measured on the scripted backend:

- A loop-control failure caused by removing action de-duplication
- A tool-interface failure that causes the agent to miss a required-document rule

For each failure, the submission will show:

- How it was detected
- Turns, tokens, cost and pass rate before the fix
- The fix and its correct architectural layer
- The same measurements after the fix
- Evidence that the fix did not reduce overall correctness

## Phase 7: Complete the cost-to-serve analysis

The cost model will include:

- Per-task token and tool cost
- Expected human fallback cost
- Fixed monthly cost
- A monthly volume of 8,000 claims
- A default failure cost of US$7.60 per escalated claim
- Sensitivity analysis around success rate and failure cost
- The break-even success rate for the cheaper model

The analysis will also measure four cost levers:

- Tool-description size
- Number of turns
- Observation size
- End-to-end success rate

## Phase 8: Prepare the final submission

The final package will include:

- A public GitHub repository
- A copy of the repository files in the NTULearn submission folder
- A README that reproduces the scripted results from a clean clone
- The agent, tools, guardrails, fixtures, answer key and result tables
- A report of no more than 2,000 words
- The completed team self-appraisal
- `CONTRIBUTIONS.md`
- A five-minute demonstration video link

The report will follow the required six-section structure:

1. Why an agent
2. The tool layer
3. What the evidence showed
4. What it costs
5. The two failures
6. What we would not deploy

## Phase 9: Prepare the team presentation

After the results are final, I will prepare:

- A complete five-minute video structure
- An individual speaking script for each member
- The exact screen content to show during each section
- A live demonstration of at least one negative case
- Likely questions and suggested answers
- A technical walkthrough so every member can explain the submitted system

## Final verification

Before submission, the repository will be cloned into a new clean directory and tested without an API key. The final checks will confirm that:

- The scripted run reproduces the reported results
- All tests pass
- The data checker passes
- The default backend is scripted
- No API keys or private local paths are included
- Every reported number matches saved execution evidence
- The report, repository, self-appraisal and video are mutually consistent
- No work from A2 is mixed with any member’s individual course project

Unless the team identifies a concern with this plan, implementation can begin after approval.
