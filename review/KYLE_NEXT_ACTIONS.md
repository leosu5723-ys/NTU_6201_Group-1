# SHI SHUYI — what you do next

Handoff for a new session. Written 2026-09-19. **Deadline: Sunday 20 September 2026, 23:59 SGT.**

Read `review/PROJECT_STATE.md` first for the full project picture. This file is only your own remaining actions.

---

## Part A · Where everything stands

| Thing | State |
|---|---|
| Engineering | Done. 101 unit tests, scripted 60/60, guardrails 10/10 |
| Frozen commit | `42253ad28fc58b36b9014808f9d8e3fd523c01ed` (tip of `main`, will not move until the batteries are in) |
| Your branch | `member/shi-shuyi` — pushed, HEAD `8f1a933` |
| Your battery | ✅ done — qwen3-30b-a3b-instruct-2507 v2, **16/60 (26.7%)**, US$0.0633, commit matches |
| Batteries overall | **3 of 6** — SHI SHUYI ✅, Isha ✅ (llama-4-maverick v2, 10/60, $0.148), Zhang ✅ (gemini-2.5-flash-lite **v1**, 6/60, $0.042) |
| Still to run | **Meng Sijia** (gemini v2), **Su Yang** (claude-haiku-4.5 v2), **Sun Hanyu** (deepseek-v3.2 v2) |
| Strand reviews | 3 in hand: Zhang, Isha, and yours (drafted, needs your sign-off) |
| Judgements | 0 of 10 filled (`review/judgement_verdicts.json`) |
| Report | draft exists, **2021 prose words — over the 2,000 cap** |
| Not produced | report PDF, team self-appraisal, video link file, NTULearn code copy, `PE6201_A2_B-1.zip` |

---

## Part B · Your actions, in order

### 1 · Approve your own strand review (10 minutes)

File: `review/member_work/SHI_SHUYI_phase_b_strand_review.md`

I drafted it from the real engineering work. **It is not yours until you read it and agree.** Correct anything that does not match your understanding. It states one design choice (exactly one recorded decision per case; zero writes on the hostile path) and records one honest limitation (the loop halts on an invalid tool payload instead of letting the model retry — 26.7% strict vs 50% decision agreement).

### 2 · Fill your two judgement cases (30–45 minutes)

You own `CLM-8894` and `CLM-8941`. File: `review/judgement_verdicts.json`.

For each: read the saved transcript and the listed requirements, then set `verdict` to `pass` or `fail`, put your **real name** in `graded_by`, and write notes that cite the evidence. Do not mark anything approved without reading the actual output.

Ask the new session to lay out the run record for both cases side by side — transcript, expected requirements, actual outcome — so you only have to read and decide.

### 3 · Chase the remaining three members

Still owed: **Meng Sijia**, **Su Yang**, **Sun Hanyu**. Each owes a battery JSON plus a strand review.

Check what has arrived at any time:

```bash
cd /Users/kyle/Projects/NTU/PE6201-A2-Group-B1
git fetch --all
git ls-remote --heads origin | sed 's|refs/heads/||'
git diff --stat origin/main origin/member/<name>
```

When each one pushes, verify their result the same way you verified Isha's and Zhang's — model, prompt version, recorded commit `42253ad…`, `dirty: false`, 60 trials.

### 4 · Merge all six branches (after the last battery lands)

Runbook: `review/MERGE_STEPS.md`. GitHub web (six clicks) or the terminal loop, both documented.

**This step is what puts everyone into the contributors list** — the list only counts commits on `main`. Do not skip it.

After merging, verify all six result files record the identical commit:

```bash
python3 -c "
import json, glob
for f in sorted(glob.glob('results/live/*.json')):
    d = json.load(open(f)); m = d.get('metadata', {})
    print(f.split('/')[-1][:52], '|', m.get('git',{}).get('commit','?')[:12], '|', m.get('prompt_version'), '|', m.get('model'))
"
```

### 5 · Report: trim, then fill real numbers

File: `report/PE6201_A2_Report_Draft.md`

- **It is 2021 prose words against a 2,000 cap.** The live numbers will add more, so trim first. Tables and figures do not count toward the cap.
- Section 3 ("What the evidence showed") needs the six pass rates and the cost spread.
- Section 4 ("What it costs") needs the measured costs and the break-even.
- Run the four numbers through the real model rather than pasting estimates: cost-to-serve = `V + (1−P) × F`, with `F = US$7.60` (US$38/hour × 12 minutes).

### 6 · Team self-appraisal — ONE sheet, not one per member

Template: `PE6201_A2_Team_Self_Appraisal.docx` (NTULearn). Draft: `review/self_appraisal_draft.md`. Completed together, checked into the submission folder alongside everything else.

### 7 · Record the 5-minute demonstration

Requirements from the brief: the system running, **one negative case demonstrated live**, and the numbers. **Every member speaks.** Over-length is penalised.

Plan the running order together after the batteries are in, so everything on screen is a real number. Then put the link **in two places**: inside the repository, and in a text file in the submission folder.

### 8 · Package and submit

- Archive name: **`PE6201_A2_B-1.zip`**
- Inside: the report, the self-appraisal, and the **code files copied in** — the brief requires the code in **two places**: the public GitHub repo *and* a copy inside the NTULearn submission folder. Both are required.
- Plus the video link.
- `CONTRIBUTIONS.md` must be in the repo and the commit history must corroborate it.
- One member uploads for the group: Blackboard → Assignments → Submission - A2.

---

## Part C · Critical path and risks

**Critical path:** three batteries → merge → report numbers → video → package → submit.

**Risks to watch**

1. **A member's result records a different commit.** Their checkout drifted. That battery has to be rerun, not edited. Catch it right after they push.
2. **The report stays over 2,000 words.** Trim before adding live data, not after.
3. **The merge is forgotten.** The work exists but nobody is credited.
4. **The code is only in the repo, not in the NTULearn folder.** The brief calls this out explicitly.
5. **The video is recorded before the numbers exist.** Then the screen shows placeholders.

**Safe to ignore**

- The pinned-session/project sidebar behaviour was your own pin, not a fault.
- Qwen's 26.7% is genuine data, not a bug. Report both the strict pass rate and the decision-agreement rate (30/60 = 50%).
