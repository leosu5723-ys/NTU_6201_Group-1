# Contribution Record

This file records completed, reviewable work. Intended responsibilities are not marked complete until evidence exists. Counts and statuses are refreshed from the integrated repository at the time of writing.

## Collaboration method

The repository is maintained as one integrated system so that the Agent loop, tool interfaces, evaluation contract and cost ledger do not drift apart. AI assistance has been used substantially for implementation drafts, test generation, debugging, documentation and mechanical verification. Every member authors evaluation cases, reviews a declared strand, runs one assigned live model battery and takes part in the recorded demonstration; the credit for those parts depends on the member's own review and sign-off, not on the integrator's drafting.

## Phase A — evaluation-case authorship

Each member's Phase A document is preserved unchanged in `review/member_submissions/`. The per-case record is in `review/case_author_signoff.json`.

| Member | Assigned Phase A cases | Submission received | Notes |
|---|---|---|---|
| Meng Sijia | 6 cases: CLM-8842, CLM-8901, CLM-8910, CLM-9001, CLM-9007, CLM-9018 | 2026-09-14 | Independently authored contracts. Her document reviewed `CLM-9013` (another member's assigned case) instead of the assigned `CLM-9012`, so `CLM-9012` was authored by the integration owner. Her `CLM-9013` review is retained as an additional cross-check. |
| SHI SHUYI | 8 cases: CLM-8850, CLM-8888, CLM-8925, CLM-9002, CLM-9008, CLM-9012, CLM-9013, CLM-9019 | 2026-09-19 | Authored `CLM-9012` after integration review found it uncovered; authored `CLM-9013` as originally assigned. |
| Su Yang | 7 cases: CLM-8861, CLM-8894, CLM-8933, CLM-9003, CLM-9009, CLM-9014, CLM-9020 | 2026-09-14 | Disclosed AI-assisted drafting reviewed and accepted without requested substantive changes. Recorded as disclosed rather than as unaided authorship. |
| Isha Kirti Ghia | 7 cases: CLM-8874, CLM-8941, CLM-8960, CLM-9004, CLM-9010, CLM-9015, CLM-9021 | 2026-09-19 | Updated review committed in `d18883b`, with a signed ending but an inconsistent “awaiting confirmation” header. Both are preserved; the member must reconcile the status. |
| Sun Hanyu | 7 cases: CLM-8917, CLM-8952, CLM-8971, CLM-9005, CLM-9011, CLM-9016, CLM-9022 | 2026-09-14 | Contracts derived from a local scripted-backend run rather than solely from source facts and Appendix A. Recorded as disclosed; the decisions agree with the frozen oracle. |
| Zhang Jiayang | 5 cases: CLM-9006, CLM-9017, CLM-9023, CLM-9024, CLM-9025 | 2026-09-17 | Independently authored contracts with explicit decision boundaries and counterfactuals. |

All 40 cases are covered exactly once, and no member's recorded decision contradicts the frozen answer key.

## Phase B — declared strand review

| Member | Declared strand | Status |
|---|---|---|
| Zhang Jiayang | Descriptors, v1→v2 ACI, guardrails, tool selection | Received 2026-09-19 |
| SHI SHUYI | Integrated loop and tool layer | Signed 2026-09-19; `review/member_work/SHI_SHUYI_phase_b_strand_review.md` |
| Meng Sijia | Evaluation harness and scripted evaluation | Received; corrected negative-case list in `40c7dd9` |
| Su Yang | Cost model, ledger, sensitivity | Received; cost-method corrections and Claude diagnostic in `5080930` |
| Isha Kirti Ghia | Tool dependencies and safe parallel calls | Received in `d18883b`; separately proposed loop/interface repairs in `4e89994` |
| Sun Hanyu | Scripted evaluation, negative cases, hostile input | Received; final member-work files included by `cb1d6f4` |

## Phase C — live model battery

| Member | Assigned live battery | Status |
|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite`, v2 | Round one received: 9/60; member tip `40c7dd9` |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507`, v2 | Round one received: 16/60; member tip `6162b93` |
| Su Yang | `anthropic/claude-haiku-4.5`, v2 | Round one received: 0/60; member tip `5080930`; 58 format failures and 2 HTTP 429 failures |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick`, v2 | Round one received: 10/60; member tip `d18883b` |
| Sun Hanyu | `deepseek/deepseek-v3.2`, v2 | Round one received: 16/60; member tip `cb1d6f4` |
| Zhang Jiayang | `google/gemini-2.5-flash-lite`, v1 | Round one received: 6/60; member tip `7089eb5` |

All six original batteries recorded experiment commit `42253ad28fc58b36b9014808f9d8e3fd523c01ed`. Their complete files are preserved byte-for-byte under `results/round1/`, separately from the pending second-round results under `results/live/`. These are strict end-to-end scores, not pure model-capability scores. Original author commits are preserved by ordinary merges, not squashed or recreated by the integration owner.

Round two is not yet measured. No member is credited with a second run, final judgement, presentation or approval before their evidence arrives. SHI SHUYI coordinates integration and reviews the combined evidence with AI assistance; this does not replace the members' own execution or authorship.

## Integrated build evidence

Current local evidence includes:

- a 40-case fixture set and an independent answer key;
- a 60-trial scripted harness with one trial per ordinary case and three per negative case;
- a standard-library test suite covering the agent, tools, data, guardrails, experiments, live-run controls and privacy;
- ten guardrail cases run on the scripted backend;
- a sequential-versus-parallel comparison and two deterministic failure reproductions;
- a dry-run-only live battery runner that refuses to spend beyond the A2 and monthly caps.

This file must not be used to claim a member completed work that has no corresponding review, run file, commit, approval or presentation evidence.
