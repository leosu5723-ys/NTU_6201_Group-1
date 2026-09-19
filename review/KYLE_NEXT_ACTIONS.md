# SHI SHUYI — what you do next

Handoff for a new session. Rewritten 2026-09-19, 18:55 SGT. **Deadline: Sunday 20 September 2026, 23:59 SGT, for every artefact including the peer rating.**

Read `review/PROJECT_STATE.md` first for the full project picture, and `review/PE6201_A2_PROGRESS_BOARD.md` for the board shared with the team. This file is only your own remaining actions.

---

## Part A · Where everything stands

| Thing | State |
|---|---|
| Engineering | Done. 101 unit tests, scripted 60/60, guardrails 10/10 |
| Frozen commit | `42253ad28fc58b36b9014808f9d8e3fd523c01ed`. `main` has **not** moved |
| Your branch | `member/shi-shuyi` at `ce0bd7f` (16 commits ahead of `main`) |
| Batteries | **6 of 6 submitted** — see the table below |
| Merge rehearsal | Six merges clean, 101 tests OK, scripted 60/60, **but `live_analysis.py` crashes** — two blockers, Part C |
| Strand reviews | **5 of 6** — Zhang, Isha, SHI SHUYI, Meng, Su. Missing: **Sun Hanyu** |
| Judgements | **2 of 10 filled** — your `CLM-8894` and `CLM-8941`, both `pass` with cited evidence |
| Report | 1,899 prose words (under the 2,000 cap as the verifier counts it), **35 live placeholders** to fill |
| Not produced yet | report PDF, team self-appraisal sheet, 5-minute video, video-link text file, NTULearn code copy, `PE6201_A2_B-1.zip`, `FINAL_APPROVAL.json`, updated `CONTRIBUTIONS.md` |

### The six batteries (all on the frozen commit, clean tree, matching hashes)

| Member | Model | Prompt | Passed | Negative | Cost |
|---|---|---|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | v2 | 9/60 (15.0%) | 9/30 | US$0.0436 |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | v2 | 16/60 (26.7%) | 11/30 | US$0.0633 |
| Su Yang | `anthropic/claude-haiku-4.5` | v2 | **0/60** — see the caveat | 0/30 | US$0.1446 |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | v2 | 10/60 (16.7%) | 9/30 | US$0.1481 |
| Sun Hanyu | `deepseek/deepseek-v3.2` | v2 | 16/60 (26.7%) | 13/30 | US$0.0773 |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | v1 (control) | 6/60 (10.0%) | 6/30 | US$0.0420 |

Total measured spend across all six: about **US$0.52**. The v1/v2 pair is complete: the same model scores 9/60 under v2 and 6/60 under v1.

**The Claude caveat (do not lose this).** All 60 trials stopped before the first turn completed: the model wrapped its JSON in a ```json code fence, the parser rejected it, and the fail-closed fallback recorded an escalation. The record shows `tool_or_schema_error`, 58 trials, plus two `backend_error` trials from a 429 rate limit. Report it as an output-format compliance failure with the cause stated, never as a quality score.

---

## Part B · Actions in order

1. **Fix the two blockers, then re-run the merge rehearsal.** You were asked "改吗" and have not answered yet. Details in Part C. Nothing else can be verified until this is done.
2. **Merge the six branches** into `main` — `review/MERGE_STEPS.md`. All six merged cleanly in rehearsal, so no conflicts are expected.
3. **Update `CONTRIBUTIONS.md`** with the real statuses and each member's commit hash, so the file and the history corroborate each other (the brief requires exactly this).
4. **Send the ten human judgements.** The surface is the frozen **scripted** run (`review/JUDGEMENT_REVIEW_SCRIPTED.md`), so it does not depend on the live batteries. Collect verdicts through the group, fill them centrally in `review/judgement_verdicts.json` — do not let six people edit that file on six branches.
5. **Fill the report's live numbers** from the six JSONs; keep it under 2,000 prose words; state both harness limits honestly (see Part D).
6. **Team self-appraisal** — one collective sheet. **Video** — 5 minutes, every member speaks, one negative case demonstrated live. Put the link in two places: the repository and a text file in the submission folder.
7. **Package and submit** — `PE6201_A2_B-1.zip` with the report, the self-appraisal and the **code copy** (the brief requires the code in the repository *and* in the NTULearn folder), then upload to Blackboard → Assignments → Submission - A2.
8. **Two items still owed by members:** Sun Hanyu must rename his result file to `results/live/deepseek__deepseek-v3.2__v2.json` (it currently carries an extra prefix) and send his strand review. Su Yang's commit uses a local machine email, so GitHub shows `author=null` — he must re-push with the email registered on his GitHub account, or add that address to his account, or he will not appear in the contributor list.

---

## Part C · The two blockers, with the fix that was proposed

Both were found by the merge rehearsal in the temporary clone at `/tmp/a2_merge_dry` (it is safe to reuse or delete; it is not the project repository).

**Blocker 1 — `live_analysis.py:217-219`.** It compares the commit recorded in the six batteries against `git rev-parse HEAD` and raises `Measured battery commit does not match the checked-out commit`. After the merge, `main` necessarily sits later than `42253ad`, so this check can never pass on the submitted repository, and `verify_submission.py` reports `live_set_valid: false`.
*Proposed fix:* compare against an explicit `FROZEN_EXPERIMENT_COMMIT` constant instead of `HEAD`; keep the requirement that all six batteries record the same commit, and keep the content-hash checks unchanged. The repository may still record the current HEAD for information. This weakens nothing: the brief requires the six batteries to share one commit, not to match the reader's checkout.
*Tests to update:* `tests/test_live_analysis.py` — `setUp` patches `live_analysis.subprocess.check_output` to answer `rev-parse HEAD` (lines 15-20) and `_valid_payloads` records `TEST_COMMIT`; both need to follow the new reference.

**Blocker 2 — `live_analysis.py:301`.** `implied_step_reliability(pass_rate, median_turns)` is called for every battery, and the helper raises when `median_turns <= 0`. Claude's median is 0, so the analysis crashes here as soon as Blocker 1 is fixed.
*Proposed fix:* guard at the **call site** — emit `None` plus a short note when the median is 0, preserving that battery's failures and spend. Leave `reliability.py` and its unit test (which asserts the exception) untouched.

Su Yang's stranded review raises further D6 items beyond these two: use list prices for the headline baseline rather than provider billing, publish priced/unpriced request coverage instead of a total, include fixed monthly cost in the sensitivity grid, preserve break-even thresholds outside [0, 1], and reconcile spend-to-date at owner level. Decide which of these are stated as limits in the report and which can be implemented in the time left; none of them blocks the merge.

---

## Part D · Honesty boundaries to keep

- The Claude battery is a **format-compliance failure**, not a measured quality result. Say so where the number appears.
- Scripted 60/60 is determinism, not model quality. Never present it as live performance.
- The strict pass rate conflates "wrong outcome" with "right outcome, invalid payload" — Qwen's battery shows 16/60 strict against 30/60 on decision agreement. Report both.
- Do not sign on anyone's behalf. Do not edit or rerun a member's battery. Keep failures and the raw files as they are.
- `CONTRIBUTIONS.md` may not claim work that has no review, run file, commit or approval behind it.

## Part E · Risks

1. **Sun Hanyu's strand review never arrives** — then the record says so and the team proceeds; it is not a reason to delay the submission.
2. **Su Yang's attribution stays unlinked** — his work is in the history but his account is not credited.
3. **The report is filled with estimates instead of the six measured JSONs.** It must come from the files.
4. **The code copy is missing from the NTULearn folder.** The brief calls this out explicitly.
5. **The video is recorded before the numbers exist**, so the screen shows placeholders.
6. **The merge is skipped.** The work exists but nobody is credited; the contributor list only counts commits on `main`.
