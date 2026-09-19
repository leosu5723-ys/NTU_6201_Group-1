# PE6201 A2 · Progress Board / 项目总进度看板

**Problem A · Team B-1 · Target: submit tonight / 目标：今晚提交**

---

## 1 · Where we are / 目前位置

**EN:** The engineering work is finished — 101 unit tests pass and the offline scripted evaluation passes 60/60. Everything remaining is human work that each member must do personally. The brief does not allow one person to complete it on behalf of the team.

**中文：** 工程部分已经做完——101项单元测试通过，离线评测 60/60。剩下的全部是人工作业，必须每位成员亲自完成，老师不允许由一个人代劳。

---

## 2 · Big blocks / 大块任务

| # | Task | 任务 | Status |
|---|---|---|---|
| 1 | System: single-agent loop, 7 tools, harness, guardrails, experiments, cost model | 工程系统：Agent循环、7个工具、评测框架、guardrails、实验、成本模型 | ✅ Done / 完成 |
| 2 | 40-case evaluation set with exactly 10 negative cases | 40个评测案例（含10个 negative） | ✅ Done / 完成 |
| 3 | Everyone writes 5–8 evaluation cases and signs them off | 全队案例撰写与签收（每人5–8个） | 🟡 5 of 6 received / 已交5人 |
| 4 | Code review — each member reviews their own strand | 代码审阅：每人负责自己的 strand | 🔴 1 of 6 / 已交1人 |
| 5 | Freeze one version and push to GitHub | 冻结统一版本并 push 到 GitHub | ✅ Done / 完成 |
| 6 | Six live model batteries, one per member | 六套 live 模型测试（每人一套） | 🔴 0 of 6 |
| 7 | Report, team self-appraisal, 10 human judgements | 报告、团队自评、10项人工判定 | 🟡 Draft exists / 草稿已有 |
| 8 | 5-minute video, PDF, package and submit | 5分钟视频、PDF、打包提交 | ⬜ Today / 今天 |

---

## 3 · What each member delivers / 每人要交的四样东西

1. **Case contracts** — decision, trigger, amounts and required fields for your assigned cases
   **案例合同** — 你负责案例的决策、触发条件、金额与必须记录的字段

2. **Code review** — findings or an explicit approval for your strand
   **代码审阅** — 你负责模块的问题，或明确批准

3. **Live result** — the complete JSON file from your assigned model
   **Live 结果** — 你负责模型的完整 JSON 结果文件

4. **Video segment** — your own spoken part in the 5-minute demonstration
   **视频发言** — 5分钟演示中你自己那一段

---

## 4 · Model assignment / 模型分配

| Member | Model | Prompt |
|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | v2 |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | v2 |
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
**Frozen commit:** `33b5083ca4355b2ea92bec6f5c8eb9557768fe87` (short: `33b5083`)

```bash
git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
cd NTU_6201_Group-1
git checkout 33b5083
python3 -m unittest discover -s tests -q   # expect 101 tests OK
python3 run_eval.py                        # expect 60/60
```

---

## 7 · Next steps / 接下来

```
1. Freeze and push            → 冻结版本并推送          ✅ done / 已完成
2. Everyone pulls and runs    → 全队 pull 并各自跑       ← now / 现在
3. Collect six JSON results   → 收齐六份结果
4. Report, costs, judgements  → 填报告、算成本、人工判定
5. Record the video           → 录视频
6. PDF, package, submit       → 生成 PDF、打包、提交
```
