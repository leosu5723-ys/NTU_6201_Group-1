# PE6201 A2 · What to do next / 下一步怎么做

**English first, then 中文. / 先英文，后中文。**
**Deadline: Sunday 20 September 2026, 23:59 SGT. / 截止：9月20日（周日）23:59。**

---

# PART 1 · ENGLISH

## Where we are

The system is built, tested and frozen on GitHub. What is left is the part only **you** can do:

1. run your **live battery** (one model, your own course key),
2. write your **strand review** (code review of your module),
3. fill your **judgement cases** (human decision on real outputs).

That is the whole of this round. When all six results are in, I will send the next step.

## The one rule

**You may use an AI coding agent** (Codex, Claude Code, Cursor, etc.) to run the commands for you. That is fine and expected — nobody has to be a programmer.

But three things are not allowed:

- Do not let it invent or "fix" results. Real numbers only.
- Do not hand-edit the result JSON, and do not delete failing trials.
- Do not share your API key — not in the group, not in a file, not in a screenshot.

If you cannot explain what your part does in your own words, you are not done.

## Step 0 · Use the course API key

Use the key the course released on **NTULearn** (it starts with `sk-or-v1-`). It has **US$10** loaded. Do **not** use a personal OpenRouter account.

## Step 1 · Give this to your AI agent

Copy the block below into Codex / Claude Code / your agent, and fill in the `<...>` parts from the table under it.

```text
I need to run a measured experiment from a course repository. Follow these
steps in order. Stop and ask me whenever I have to type something myself.

1. git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
   cd NTU_6201_Group-1

2. Ask me for my full name and my GitHub email, then run:
   git config user.name "<MY NAME>"
   git config user.email "<MY GITHUB EMAIL>"
   (this makes my commits count as mine on GitHub)

3. git checkout -b member/<MY-BRANCH-NAME> main

4. Run: git rev-parse HEAD
   It must print 42253ad28fc58b36b9014808f9d8e3fd523c01ed
   If it prints anything else, run:
     git fetch origin && git checkout main && git pull
   and check again. If it still differs, stop and tell me.

5. Verify the checkout works:
   python3 -m unittest discover -s tests -q      # expect: OK (101 tests)
   python3 A2_reference_data/check_my_data.py    # expect: Your data hangs together.
   python3 run_eval.py                           # expect: "passed": 60
   git status --porcelain                        # expect: nothing
   If any of these fail, STOP and tell me. Do not continue.

6. Free dry run (no network, no cost):
   python3 live_battery.py --model <MY MODEL> --prompt-version <MY PROMPT>

7. STOP. Ask me to export my API key in my own terminal.
   I will run:  export OPENROUTER_API_KEY='...'
   Never ask me to paste the key into this chat, and never write it to a file.

8. After I confirm the key is exported, run:
   python3 live_battery.py --model <MY MODEL> --prompt-version <MY PROMPT> \
     --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute

9. When it finishes, report to me:
   - how many trials ran and the pass rate
   - the measured cost recorded in the JSON
   - which cases failed, if any
   Then confirm the JSON is valid and that the git commit recorded inside it
   equals the SHA from step 4.

10. Do not modify, reformat or delete anything in results/live/.

11. mkdir -p review/member_work
    Copy my Phase A case document and my strand review into review/member_work/

12. git add review/member_work results/live
    git commit -m "<MY NAME>: Phase A cases, Phase B strand review and <MODEL> battery"
    git push -u origin member/<MY-BRANCH-NAME>

13. Tell me my branch name and whether the push succeeded.
    If the push is rejected, tell me and stop — do not force it.
```

## Step 2 · Your values for the block above

| Member | `<MY MODEL>` | `<MY PROMPT>` | `<MY-BRANCH-NAME>` |
|---|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | `v2` | `meng-sijia` |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | `v2` | `shi-shuyi` |
| Su Yang | `anthropic/claude-haiku-4.5` | `v2` | `su-yang` |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | `v2` | `isha-kirti-ghia` |
| Sun Hanyu | `deepseek/deepseek-v3.2` | `v2` | `sun-hanyu` |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | `v1` | `zhang-jiayang` |

Zhang Jiayang runs `v1` on purpose: it is the control for the v1-versus-v2 comparison. Do not change Meng Sijia's `v2` result.

**Why branches, not `main`:** all six batteries must run on the exact same frozen commit. If anyone pushes to `main`, the tip moves and anyone who clones afterwards gets a different version — their result would record a different commit and the six runs would no longer be comparable. SHI SHUYI merges all six branches at the end.

## Step 3 · Your strand review

Read the files listed for your strand in `review/TEAM_ACTION_PACK.md`, then write a short response containing:

- one design choice you can explain in your own words, and
- any question or correction, **or** the words "approved as written".

Reading the code with your AI agent is fine. The opinion must be yours.

## Step 4 · Your judgement cases

Each of you reviews the cases listed in `review/TEAM_ACTION_PACK.md` under "Phase E judgement". Look at what the model actually did on those cases and record the human verdict. Do not mark them approved without reading the actual output.

## Step 5 · Report back

Send these five lines with your branch name:

```text
Model and prompt version:
Observed pass rate:
Most important failure or surprising behaviour:
Was the quality worth the measured cost? Why?
Name and date:
```

## Red lines

- Never share an API key.
- Never edit a result file.
- Never delete a failing trial.
- Never sign off work you did not read.
- If something fails, stop and tell SHI SHUYI.

---

# PART 2 · 中文

## 我们现在在哪

系统已经做好、测试通过、并在 GitHub 上冻结。剩下的只有**你本人**能做的三件事：

1. 跑你的 **live battery**（一个模型，用你自己的课程 key）
2. 写你的 **strand review**（你负责模块的代码审阅）
3. 填你的 **judgement cases**（对真实输出做人工判定）

这一轮就这些。等六份结果都收齐，我再发下一步。

## 唯一的底线

**你可以用 AI 编程助手**（Codex、Claude Code、Cursor 等）帮你执行命令。这完全没问题，不会写代码也照样能做。

但三件事绝对不允许：

- 不允许让 AI **编造或"修正"结果**，只能是真实数字
- 不允许**手改结果 JSON**，也不允许删掉失败的 trial
- 不允许**分享你的 API key**——不在群里、不写进文件、不发截图

如果某一部分你没法用自己的话讲清楚，那就不算完成。

## 第 0 步 · 用课程的 API key

用老师在 **NTULearn** 上发的那把 key（以 `sk-or-v1-` 开头），里面有 **US$10** 额度。**不要**用自己个人 OpenRouter 账号里的 key。

## 第 1 步 · 把上面那段交给你的 AI 助手

**第 1 步的代码块和英文部分完全相同，直接用上面那一整段，不用另外复制。** 只要按下面表格把 `<...>` 填成你自己的值就行。

## 第 2 步 · 上面要填的值

| 成员 | `<MY MODEL>` | `<MY PROMPT>` | `<MY-BRANCH-NAME>` |
|---|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | `v2` | `meng-sijia` |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | `v2` | `shi-shuyi` |
| Su Yang | `anthropic/claude-haiku-4.5` | `v2` | `su-yang` |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | `v2` | `isha-kirti-ghia` |
| Sun Hanyu | `deepseek/deepseek-v3.2` | `v2` | `sun-hanyu` |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | `v1` | `zhang-jiayang` |

Zhang Jiayang 跑 `v1` 是故意的：他是 v1/v2 对照实验的对照组。**不要**动 Meng Sijia 的 `v2` 结果。

**为什么要用分支而不是直接推 main：** 六套 battery 必须跑在**完全同一个 commit** 上。只要有人推了 main，分支顶端就会移动，之后才 clone 的人拿到的版本就不同了——他们结果里记录的 commit 会和大家对不上，六套结果就不能作为一组比较。最后由 SHI SHUYI 统一合并六个分支。

## 第 3 步 · 你的 strand review

先读 `review/TEAM_ACTION_PACK.md` 里列出的、属于你这个 strand 的文件，然后写一段简短回应：

- 一个你能用自己的话讲清楚的设计选择，以及
- 任何疑问或修正意见，**或者**明确写一句 "approved as written"

用 AI 助手陪你读代码没问题，但**观点必须是你自己的**。

## 第 4 步 · 你的 judgement cases

每人在 `review/TEAM_ACTION_PACK.md` 的 "Phase E judgement" 下有自己的案例编号。去看模型在这些案例上**实际**做了什么，再记录人工判定。**没看真实输出就不要签字。**

## 第 5 步 · 回报

把下面五行连同你的分支名发出来：

```text
Model and prompt version:
Observed pass rate:
Most important failure or surprising behaviour:
Was the quality worth the measured cost? Why?
Name and date:
```

## 红线

- 绝不分享 API key
- 绝不修改结果文件
- 绝不删除失败的 trial
- 绝不对没读过的内容签字
- 出问题就停下来，告诉 SHI SHUYI
