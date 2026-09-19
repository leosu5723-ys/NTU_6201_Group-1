# Project state — PE6201 A2, Problem A

Snapshot for whoever picks this up next. Read this first, then `review/PE6201_A2_TEAM_FAQ.md` for the member-facing answers and `review/PE6201_A2_PROGRESS_BOARD.md` for the board we share with the team.

**Last updated:** 2026-09-19, late morning. Submission target: tonight.

## What this is

MSc Enterprise AI, PE6201 A2, Team B-1, Problem A (health-insurance claim first response). Six members. One integrated single-agent ReAct system, 40 evaluation cases with exactly 10 negatives, offline scripted harness, guardrails, v1/v2 ACI experiment, sequential/parallel comparison, two reproducible failures, three-layer cost model.

## Repositories and paths

| What | Where |
|---|---|
| Assignment repo (public, submitted) | `/Users/kyle/Projects/NTU/PE6201-A2-Group-B1` |
| Remote | `https://github.com/leosu5723-ys/NTU_6201_Group-1` |
| **Frozen experiment commit** | **`e64d2aa`** — every battery must use this |
| Team assistant project | `/Users/kyle/Projects/NTU/PE6201-Team-Assistant` |
| Team bot profile | `/Users/kyle/.hermes/profiles/pe6201-team` (Telegram, group `-5364848522`) |
| Member submissions received | `review/member_submissions/` and the bot's `runtime/submissions/` |
| Battery results (empty so far) | `results/live/` |

## State right now

**Done**

- Engineering: 101 unit tests pass, scripted run 60/60, 10/10 guardrail cases, privacy scan clean.
- 40-case set with exactly 10 negatives; per-case machine oracle in `evaluation/code_expectations_A.json`.
- Case authorship integrated: 5 of 6 members submitted Phase A; `review/case_author_signoff.json` holds the per-case record.
- Case allocation corrected: Meng Sijia has 6 cases, SHI SHUYI has 8 (CLM-9012 was uncovered because Meng reviewed CLM-9013 instead; SHI SHUYI authored 9012).
- Repo pushed. Contributor attribution fixed for future commits; the six earlier commits are unlinked until Kyle adds `SHUYI013@e.ntu.edu.sg` to his GitHub account and verifies it.
- Team bot rebuilt: 39-document corpus (current docs + source code, deliberately excluding the answer key and scripted trajectories), helpful-by-default SOUL with three red lines, `max_turns` 15, gateway restarted, verified with real queries.

**Outstanding**

1. **Six live batteries: 0 of 6 run.** This is the critical path.
   - Meng Sijia — `google/gemini-2.5-flash-lite`, v2
   - SHI SHUYI — `qwen/qwen3-30b-a3b-instruct-2507`, v2
   - Su Yang — `anthropic/claude-haiku-4.5`, v2
   - Isha Kirti Ghia — `meta-llama/llama-4-maverick`, v2
   - Sun Hanyu — `deepseek/deepseek-v3.2`, v2
   - Zhang Jiayang — `google/gemini-2.5-flash-lite`, v1 (control)
2. **Phase B strand reviews: 1 of 6** (Zhang Jiayang only).
3. **Ten human judgements: 0 of 10** (`review/judgement_verdicts.json`).
4. **Isha's case record is unsigned** — her document still asks her to verify against Appendix A before signing.
5. **Report has ~35 live placeholders** and is at about 1,899 prose words against a 2,000 cap.
6. **Not produced yet:** report PDF, team self-appraisal PDF, video link, final approval record, submission ZIP.

## Decisions already made (do not relitigate)

- Problem A only. Single agent, hand-written loop, no framework.
- Default backend is `scripted`; markers must be able to reproduce at zero cost.
- All three ordinary outcomes (`approve_in_principle`, `request_document`, business `escalate`) go through the one gated action exactly once. Hostile-narrative escalation fails closed with zero writes.
- Exactly 40 cases, exactly 10 negatives, one trial per ordinary case and three per negative — 60 trials per battery.
- Every member runs their own battery on their own key. Kyle does **not** run them all. The brief states this three times.
- Nobody pushes to `main`; each member pushes `member/<name>` and SHI SHUYI merges.
- Do not rewrite git history — it would change `e64d2aa`.
- The bot is not given raw filesystem access. Its corpus is a manifest allowlist; broadening it was explicitly rejected in favour of a richer published snapshot.

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
