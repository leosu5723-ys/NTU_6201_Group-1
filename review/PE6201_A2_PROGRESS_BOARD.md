# PE6201 A2 · Progress Board / 项目总进度看板

**Problem A · Team B-1 · Deadline: Sunday 20 September 2026, 23:59 SGT**
**截止时间：2026年9月20日（周日）23:59**

---

## 1 · Where we are / 目前位置

**EN:** The engineering work is finished and frozen on GitHub — 101 unit tests pass and the offline scripted evaluation passes 60/60. One member's live battery is already complete. Everything remaining is human work that each member must do personally; the brief does not allow one person to do it on behalf of the team.

**中文：** 工程部分已经完成并在 GitHub 上冻结——101项单元测试通过，离线评测 60/60。已经有一套 live battery 跑完。剩下的全部是人工作业，必须每位成员亲自完成，老师不允许由一个人代劳。

---

## 2 · Progress / 进度

| # | Task | 任务 | Status |
|---|---|---|---|
| 1 | System: single-agent loop, 7 tools, harness, guardrails, experiments, cost model | 工程系统：Agent循环、7个工具、评测框架、guardrails、实验、成本模型 | ✅ Done / 完成 |
| 2 | 40-case evaluation set with exactly 10 negative cases | 40个评测案例（含10个 negative） | ✅ Done / 完成 |
| 3 | Everyone writes 5–8 evaluation cases | 全队案例撰写（每人5–8个） | ✅ 6 of 6 / 已交6人 |
| 4 | Code review — each member reviews their own strand | 代码审阅：每人负责自己的 strand | 🟡 1 of 6 / 已交1人 |
| 5 | Freeze one version and push to GitHub | 冻结统一版本并 push 到 GitHub | ✅ Done / 完成 |
| 6 | Six live model batteries, one per member | 六套 live 模型测试（每人一套） | 🟡 **1 of 6**（SHI SHUYI 完成）|
| 7 | Ten human judgements | 10项人工判定 | 🔴 0 of 10 |
| 8 | Report with real live numbers | 报告填入真实数据 | 🟡 Draft exists / 草稿已有 |

---

## 3 · What each member delivers now / 每人现在要交的三样东西

1. **Live result** — the complete JSON file from your assigned model
   **Live 结果** — 你负责模型的完整 JSON 结果文件

2. **Strand review** — findings or an explicit approval for your strand
   **代码审阅** — 你负责模块的问题，或明确批准

3. **Judgement cases** — the human verdict on the cases assigned to you
   **人工判定** — 你负责案例的人工判定结果

---

## 4 · Model assignment / 模型分配

| Member | Model | Prompt |
|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | v2 |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | v2 ✅ done |
| Su Yang | `anthropic/claude-haiku-4.5` | v2 |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | v2 |
| Sun Hanyu | `deepseek/deepseek-v3.2` | v2 |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | **v1** (control / 对照组) |

---

## 5 · Rules from the brief / 老师的硬性要求

**EN:**

- Every member writes 5–8 evaluation cases.
- Every member runs one full live battery on **their own** API key.
- All six runs use the **same commit, same case set, same v2 prompt** — the model name is the only thing that differs.
- The models must span at least two price tiers, and no two members may use the same model family.
- Any member may be asked about any part of the submitted code.
- Never share an API key in the group, in a file or in a screenshot.

**中文：**

- 每人必须写 5–8 个评测案例。
- 每人必须用**自己的** API key 跑一整套 live battery。
- 六次运行必须使用**同一个 commit、同一套案例、同一个 v2 prompt**，唯一变量是模型名。
- 模型至少覆盖两个价位档，且不能有两人用同一家族。
- 任何成员都可能被问到提交代码的任何部分。
- 绝不要在群里、文件里或截图里分享 API key。

---

## 6 · Frozen version / 冻结版本

**Repository:** `https://github.com/leosu5723-ys/NTU_6201_Group-1`
**Frozen experiment commit:** `42253ad28fc58b36b9014808f9d8e3fd523c01ed` — the tip of `main`. `main` will not move until all six batteries are collected, so pulling `main` is enough. Confirm with `git rev-parse HEAD` before your paid run.

```bash
git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
cd NTU_6201_Group-1

git rev-parse HEAD                        # must print 42253ad28fc...
python3 -m unittest discover -s tests -q  # expect: OK (101 tests)
python3 run_eval.py                       # expect: "passed": 60
```

**Nobody pushes to `main`.** Each member pushes `member/<name>`; SHI SHUYI merges at the end.

---

## 7 · Pipeline / 流程

```
1. Freeze and push            → 冻结版本并推送            ✅ done / 已完成
2. Everyone runs their battery → 全队各自跑自己的 battery   ← now / 现在
3. Send back your five answers → 回报五行简短回答
4. Collect six results         → 收齐六份结果
          ↓
   Next step comes from SHI SHUYI / 下一步由 SHI SHUYI 发出
```
