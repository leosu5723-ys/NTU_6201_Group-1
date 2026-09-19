# Round two — run only after the freeze announcement

This supersedes the round-one branch instructions. The team target is to complete round two and aim to submit on Saturday 19 September evening. The official submission deadline remains Sunday 20 September 2026, 23:59 SGT.

**This document alone is not permission to start a paid run.** SHI SHUYI will announce the exact verified commit SHA in the group. Never infer the experiment version from a moving branch tip.

## What changes and what stays

- The six original member histories are integrated without squashing. Round-one JSONs and logs are preserved unchanged in `results/round1/`; `MANIFEST.json` records their hashes.
- Round-two outputs go to `results/live/`. Do not copy old batteries into that directory.
- Model ownership, case set, answer key, strict scoring and v1/v2 comparison design stay unchanged. The candidate repairs the loop/JSON/interface problems identified in round one.
- A rerun is needed because runtime code and prompts change, not because member commits are merged.
- Each person runs their own assigned model on their own course-issued key. No third optimisation round is planned.

## Member-specific values

| Member | NAME_SLUG | MODEL_ID | PROMPT_VERSION | OUTPUT_STEM |
|---|---|---|---|---|
| Meng Sijia | meng-sijia | google/gemini-2.5-flash-lite | v2 | google__gemini-2.5-flash-lite__v2 |
| SHI SHUYI | shi-shuyi | qwen/qwen3-30b-a3b-instruct-2507 | v2 | qwen__qwen3-30b-a3b-instruct-2507__v2 |
| Su Yang | su-yang | anthropic/claude-haiku-4.5 | v2 | anthropic__claude-haiku-4.5__v2 |
| Isha Kirti Ghia | isha-kirti-ghia | meta-llama/llama-4-maverick | v2 | meta-llama__llama-4-maverick__v2 |
| Sun Hanyu | sun-hanyu | deepseek/deepseek-v3.2 | v2 | deepseek__deepseek-v3.2__v2 |
| Zhang Jiayang | zhang-jiayang | google/gemini-2.5-flash-lite | v1 | google__gemini-2.5-flash-lite__v1 |

## Instructions to your coding assistant

Replace the placeholders using the table and the group's freeze announcement. This round is only the assigned battery and its short interpretation; do not rewrite the member's case authorship or sign reviews on their behalf.

```text
Help me execute my PE6201 A2 round-two battery and commit my actual results.

Repository: https://github.com/leosu5723-ys/NTU_6201_Group-1
Frozen commit: <FROZEN_SHA_FROM_GROUP>
My name: <FULL_NAME>
Name slug: <NAME_SLUG>
Model: <MODEL_ID>
Prompt version: <PROMPT_VERSION>
Output stem: <OUTPUT_STEM>

1. Check my existing repository and git status first. Preserve all existing work.
   Fetch origin. Do not reset, force-push, rewrite history or clean my files.
   Create member/<NAME_SLUG>-round2 from the EXACT announced SHA, not local main
   or my round-one branch. If the round-two branch already exists, inspect it;
   do not recreate it or discard a checkpoint. Print `git rev-parse HEAD` and
   confirm it matches the announced SHA before running anything paid.

2. Verify my repository-local git name/email map to my own GitHub identity.
   Never use SHI SHUYI's identity or another member's identity.

3. Run:
   python3 -m unittest discover -s tests -q
   python3 A2_reference_data/check_my_data.py
   python3 run_eval.py
   git status --porcelain
   Require all tests to pass, scripted 60/60 and a clean source tree. If a check
   changes tracked files or fails, stop and report; do not fix source locally
   or commit a different experiment version.

4. Dry-run preflight (free, no model request):
   python3 live_battery.py --model <MODEL_ID> --prompt-version <PROMPT_VERSION>

5. STOP and hand control to me to set my own OPENROUTER_API_KEY in my terminal
   environment securely. Never ask me to paste a key into chat, never print it,
   never write it to a file, and do not change your assistant's credentials.
   Ask for my actual previous A2 and calendar-month spend, INCLUDING round one,
   interrupted attempts and any other relevant usage. Do not default to zero
   or equate a fresh key with zero owner-level monthly spending.

6. After I confirm setup and spending, run only my assigned battery:
   python3 live_battery.py --model <MODEL_ID> --prompt-version <PROMPT_VERSION> \
     --spent-to-date <A2_PRIOR_USD> --monthly-spent-to-date <MONTH_PRIOR_USD> --execute
   Do not use --allow-dirty. Do not edit source, stage other work or commit
   during execution. If interrupted, retain the checkpoint and reissue the
   same command at the same SHA with the SAME pre-run spending values. The
   runner includes checkpoint spending itself. Do not rerun just failed cases.

7. Completion requires results/live/<OUTPUT_STEM>.json with 60 unique trials
   over 40 cases, recorded commit equal to the announced SHA, dirty=false and
   no remaining checkpoint. Keep all failures and raw responses unchanged.
   Check that my output and its companion <OUTPUT_STEM>-logs contain no key.

8. Only after completion, write my brief interpretation to
   review/member_work/<NAME_SLUG>_round2_result.md: actual model/version,
   passes/trials, important failure, whether quality justified observed cost,
   and my own comments. Ask me for my judgement; do not invent it.
   Stage ONLY my result JSON, its generated log directory if present, and my
   interpretation. Do not stage anyone else's files or an incomplete checkpoint.
   Commit under my identity and push member/<NAME_SLUG>-round2. Never push main.
   Verify the remote branch SHA equals the local commit.

9. Return the branch name, commit, push verification, observed results and any
   unresolved errors to me for sharing with SHI SHUYI. Never alter raw scores,
   delete failures or claim a run completed merely because a branch exists.
```

## 中文说明

先等待群里公布的新冻结 SHA，再把上面整段交给自己的编程助手，并替换表格中的个人参数。新建 `member/<姓名>-round2`，不要继续在第一轮分支上跑，也不要直接推送 main。

第一轮已发生的花费必须计入本轮的历史支出；API key 只由本人在终端安全设置，不发给助手或群聊。中断保留 checkpoint，用相同命令续跑，不在中途 commit。

本轮交回自己的完整结果、生成日志和简短真实解读。不要修改失败记录、代签或替别人运行。新的 SHA 尚未公布时，不要抢跑。
