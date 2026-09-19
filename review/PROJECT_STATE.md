# Project state — PE6201 A2, Problem A

Snapshot for whoever picks this up next. Read this first, then `review/PE6201_A2_TEAM_FAQ.md` for the member-facing answers and `review/PE6201_A2_PROGRESS_BOARD.md` for the board we share with the team.

**Last updated:** 2026-09-19, 17:00 SGT. **Deadline: Sunday 2026-09-20, 23:59 SGT** (confirmed by Kyle against the Blackboard announcement of 9 September; the brief PDF still prints the superseded 13 September date). One member uploads for the group to Blackboard → Assignments → Submission - A2.

## What this is

MSc Enterprise AI, PE6201 A2, Team B-1, Problem A (health-insurance claim first response). Six members. One integrated single-agent ReAct system, 40 evaluation cases with exactly 10 negatives, offline scripted harness, guardrails, v1/v2 ACI experiment, sequential/parallel comparison, two reproducible failures, three-layer cost model.

## Repositories and paths

| What | Where |
|---|---|
| Assignment repo (public, submitted) | `/Users/kyle/Projects/NTU/PE6201-A2-Group-B1` |
| Remote | `https://github.com/leosu5723-ys/NTU_6201_Group-1` |
| **Frozen experiment commit** | **`42253ad28fc58b36b9014808f9d8e3fd523c01ed`** (short `42253ad`), the tip of `main`. Code/prompt/cases are byte-identical to `e64d2aa`. |
| Team assistant project | `/Users/kyle/Projects/NTU/PE6201-Team-Assistant` |
| Team bot profile | `/Users/kyle/.hermes/profiles/pe6201-team` (Telegram, group `-5364848522`) |
| Member submissions received | `review/member_submissions/` and the bot's `runtime/submissions/` |
| Battery results | `results/live/` |

## Submission requirements (authoritative, from `PE6201_A2_Applied_AI_System.pdf` §4 and D5)

**Four artefacts, one archive named `PE6201_A2_[TeamID].zip` → `PE6201_A2_B-1.zip`, plus the video link.**

1. **Code repository, in TWO places.** (a) the public GitHub repo, and (b) a copy of the same code files inside the NTULearn submission folder. The brief is explicit that both are required — the repository shows history and contribution, the folder copy means marking never depends on a link working. README must get a stranger from clone to a reproduced scripted run.
2. **Team report**, at most 2,000 words (tables and figures excluded).
3. **Recorded demonstration, 5 minutes.** Must show the system running, **one negative case demonstrated live**, and the numbers. **Every member speaks.** Over-length is penalised.
4. **Team self-appraisal** — **one collective sheet per team**, not one per member.

Plus, from §4: the repository must contain a `CONTRIBUTIONS.md` naming who did what, **and the commit history must corroborate it**.

**Video link must live in two places** in the submission: inside the repository, and in a text file.

**D5 battery rules (quoted, non-negotiable):**

- "Split the models across team members — one member owns one model, and runs it on their own key."
- "When the battery is run every member runs one — because a member who never sends a live request has not met a real model's latency, variance or refusals."
- "same commit, same v2 prompt, MODEL the only string that differs. With three runners drift is survivable; with six it silently voids the whole battery."

## State right now

**Done**

- Engineering: 101 unit tests pass, scripted run 60/60, 10/10 guardrail cases, privacy scan clean.
- 40-case set with exactly 10 negatives; per-case machine oracle in `evaluation/code_expectations_A.json`.
- Case authorship integrated: all 6 members submitted Phase A. Case allocation corrected (Meng Sijia 6, SHI SHUYI 8).
- Repo pushed; `main` frozen at `42253ad` and not moving until the batteries are collected.
- Contributor attribution verified (19 Sep): every commit on `main` resolves to an account (`SHUYI013@e.ntu.edu.sg` and the Stone441 noreply address both map to **Stone441**; Isha's to `Isha-prog578`, Zhang's to `Jy135zhang`). Nothing outstanding here — the earlier concern about unlinked commits is closed.
- **SHI SHUYI's live battery is done**: `qwen/qwen3-30b-a3b-instruct-2507` v2, 60/60 trials, **16 passed (26.7%)**, all 9 hostile-narrative trials correctly escalated with zero writes, measured cost **US$0.0633**, recorded commit `42253ad`, clean tree. Committed on branch `member/shi-shuyi` (`0b9f5fe`), attributed to Stone441. File: `results/live/qwen__qwen3-30b-a3b-instruct-2507__v2.json`.
- Team bot rebuilt: 40-document corpus (current docs + source code, deliberately excluding the answer key and scripted trajectories), helpful-by-default SOUL with three red lines, `max_turns` 15, gateway restarted, verified with real queries.
- **SHI SHUYI's strand review is signed** (19 Sep) in `review/member_work/SHI_SHUYI_phase_b_strand_review.md`; the two properties it asserts were re-checked in `agent.py` (`:184`/`:298`/`:315`, `:326`/`:334`).
- **Human-judgement surface fixed**: `prepare_judgement_check` now projects `escalate_to`, which five cases require reviewers to confirm. The regenerated scripted payload is otherwise identical (same summary, all 60 result rows and every decision log byte-identical; frozen fixture hash unchanged), and the three collected batteries still validate.
- **Readiness test made stage-independent** (`tests/test_verify_submission.py`): it now compares the reported live/judgement counts with the files present instead of pinning zero, so the suite passes before and after the batteries merge. Verified OK with 0, 1 and 3 batteries present; full suite 101 OK.
- `review/MERGE_STEPS.md` corrected: the documented `git push -c ...` form fails (option must precede the subcommand), and the shared `review/judgement_verdicts.json` file is now flagged as the one file six reviewers must not fill on separate branches.

**Outstanding**

1. **Live batteries: 5 of 6 run.** All five recorded the frozen commit `42253ad` with a clean tree and matching case / answer-key / v2 prompt hashes, so none needs a rerun:
   - Meng Sijia — `google/gemini-2.5-flash-lite`, v2 — 9/60 (15.0%), US$0.0436 — pushed on `member/meng-sijia`
   - SHI SHUYI — `qwen/qwen3-30b-a3b-instruct-2507`, v2 — 16/60 (26.7%), US$0.0633
   - Isha Kirti Ghia — `meta-llama/llama-4-maverick`, v2 — 10/60 (16.7%), US$0.1481
   - Zhang Jiayang — `google/gemini-2.5-flash-lite`, v1 (control) — 6/60 (10.0%), US$0.0420
   - Sun Hanyu — `deepseek/deepseek-v3.2`, v2 — 16/60 (26.7%), US$0.0773 — **delivered in the wrong form**: uploaded through the web UI as `results/scripted/live_results_backup.zip`. The battery inside is valid (commit `42253ad`, hashes match, 60 trials) and contains no keys, but it must be committed under `results/live/` with its `-logs` directory before the merge.
   - **Still missing: Su Yang** (`anthropic/claude-haiku-4.5`, v2) — no branch created yet.
2. **Phase B strand reviews: 4 of 6 returned** (Zhang Jiayang, Isha Kirti Ghia, SHI SHUYI in their branches; Meng Sijia sent hers to the team bot on 19 Sep 16:31 and it is **not yet in the repository** — she still needs to commit it to `review/member_work/`). Missing: Sun Hanyu, Su Yang.
   - **Correction owed by Meng Sijia:** her review lists the ten *judgement* cases as the ten *negative* cases. Her quoted rule is right and the 40→60 arithmetic still holds, but the sets differ: the negatives are `CLM-8888, 8894, 8901, 8910, 8917, 8925, 8933, 8941, 8952, 9025`, while `CLM-8842` and `CLM-9019` are ordinary approvals that only appear in the judgement queue. Fix before the report and the video.
3. **Ten human judgements: 2 of 10 filled** — SHI SHUYI's `CLM-8894` and `CLM-8941`, both `pass` with cited evidence. The remaining eight wait for the merge. Note the judgement surface is the frozen **scripted** run, so it does not depend on the live batteries.
4. **Isha's Phase A case record is unsigned** — her document still reads "Awaiting Isha Kirti Ghia's personal confirmation before final sign-off", although she sent a completed worksheet to the team bot on 18 September.
5. **Report has live placeholders and is over the cap** (2,021 prose words against 2,000); trim before inserting the real numbers from the six JSONs.
6. **Not produced yet:** report PDF, team self-appraisal sheet, video link text file, the NTULearn folder copy of the code, final approval record, `PE6201_A2_B-1.zip`.
7. **Merge step not yet done:** five member branches are pushed (`meng-sijia`, `shi-shuyi`, `isha-kirti-ghia`, `sun-hanyu`, `zhang-jiayang`); Su Yang's does not exist. An open pull request from `member/isha-kirti-ghia` must stay unmerged until the last battery lands — merging moves `main` off `42253ad` and would void any checkout that has not run yet.

## Known limitation to state honestly in the report

`agent.py` wraps the whole turn loop in one `try`. A tool-level validation failure (an unsupported disposition, a missing evidence reference) raises `ValueError`, which propagates to the outer handler and **halts the run immediately** — the model never sees the error and never gets a retry. The failure is recorded as a business escalation with `stopped_by = "tool_or_schema_error"`.

This is a deliberate fail-closed choice — an unvalidatable decision goes to a human rather than being guessed — and it is consistent with the cost model's `(1-P) × F` fallback term. But it means the strict pass rate conflates "the model chose the wrong outcome" with "the model chose correctly but produced an invalid payload". Report **both** numbers:

- strict end-to-end pass rate (Qwen3: 16/60 = 26.7%)
- decision-level agreement (Qwen3: 30/60 = 50%)

Do not present the strict pass rate as a pure model-quality measure.

## Decisions already made (do not relitigate)

- Problem A only. Single agent, hand-written loop, no framework.
- Default backend is `scripted`; markers must be able to reproduce at zero cost.
- All three ordinary outcomes (`approve_in_principle`, `request_document`, business `escalate`) go through the one gated action exactly once. Hostile-narrative escalation fails closed with zero writes.
- Exactly 40 cases, exactly 10 negatives, one trial per ordinary case and three per negative — 60 trials per battery.
- Every member runs their own battery on their own key. Kyle does **not** run them all. The brief states this three times.
- Nobody pushes to `main`; each member pushes `member/<name>` and SHI SHUYI merges at the end.
- The build is one integrated codebase reviewed by strand, not six split modules. The brief leaves the division to the team; splitting one coherent agent into six incompatible pieces was rejected on purpose. Each member still has distinct visible files: `review/member_work/<name>.md` and `results/live/<model>.json`.
- Do not rewrite git history — it would change the frozen SHA everyone is checking out.
- Members use the **course-issued OpenRouter key** (US$10 cap, released on NTULearn), not a personal account. The working copy lives at `~/.hermes/openrouter_course.key` (mode 600). Never print, paste or commit it.
- The bot is not given raw filesystem access. Its corpus is a manifest allowlist.

## Useful commands

```bash
cd /Users/kyle/Projects/NTU/PE6201-A2-Group-B1
python3 -m unittest discover -s tests -q     # expect 101 OK
python3 run_eval.py                          # expect 60/60
python3 verify_submission.py                 # deterministic_ready, submission_ready
python3 build_case_worksheets.py --output review/CASE_WORKSHEETS.md   # refuses to overwrite; move the old file first
```

Team bot checks:

```bash
hermes -p pe6201-team chat -q "your question here"
```

## Honesty boundaries to keep

- Scripted 60/60 is determinism, not model quality. Never present it as live performance.
- No live number, cost, latency or model comparison may be written before the batteries exist.
- Member contributions are recorded as disclosed, including the AI-assisted drafting in Su Yang's and Isha's documents and the scripted-run derivation in Sun Hanyu's.
- Do not sign on anyone's behalf.
- Do not let a teammate's summary substitute for their real live run. Each battery must come from its owner's own key.
