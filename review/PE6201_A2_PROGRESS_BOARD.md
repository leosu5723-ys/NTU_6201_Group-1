# PE6201 A2 · Progress Board / 项目总进度看板

**Problem A · Team B-1 · Deadline: Sunday 20 September 2026, 23:59 SGT — all artefacts, including the peer rating**
**截止时间：2026年9月20日（周日）23:59，全部提交物（含 peer rating）**

**Last updated / 更新于:** 19 September 2026, 16:50 SGT

---

## 1 · Where we are / 目前位置

**EN:** The engineering work is finished and frozen on GitHub — 101 unit tests pass and the offline scripted evaluation passes 60/60. **Five of the six live batteries have been run**, and all five ran on the frozen commit `42253ad` with identical case, answer-key and v2 prompt hashes. One battery is still outstanding (**Su Yang**), and one has arrived in the wrong form (**Sun Hanyu** — the run itself is complete and valid, but it was uploaded as an archive under `results/scripted/` instead of being committed under `results/live/`). Everything remaining is human work that each member must do personally; the brief does not allow one person to do it on behalf of the team.

**中文：** 工程部分已经完成并在 GitHub 上冻结——101项单元测试通过，离线评测 60/60。**六套 live battery 已跑完五套**，且全部在冻结 commit `42253ad` 上运行，案例、答案键与 v2 prompt 哈希一致。还差 **Su Yang** 一套；**Sun Hanyu** 那套已经跑完、数据有效，但以压缩包形式上传到了 `results/scripted/`，需要按 `results/live/` 重新提交。剩下的全部是人工作业，必须每位成员亲自完成，老师不允许由一个人代劳。

---

## 2 · Progress / 进度

| # | Task | 任务 | Status |
|---|---|---|---|
| 1 | System: single-agent loop, 7 tools, harness, guardrails, experiments, cost model | 工程系统：Agent循环、7个工具、评测框架、guardrails、实验、成本模型 | ✅ Done / 完成 |
| 2 | 40-case evaluation set with exactly 10 negative cases | 40个评测案例（含10个 negative） | ✅ Done / 完成 |
| 3 | Everyone writes 5–8 evaluation cases | 全队案例撰写（每人5–8个） | ✅ 6 of 6 / 已交6人 |
| 4 | Code review — each member reviews their own strand | 代码审阅：每人负责自己的 strand | 🟡 **4 of 6 已交**（SHI SHUYI、Isha、Zhang 已在仓库；Meng 已通过团队 bot 提交，待推送到她的分支）|
| 5 | Freeze one version and push to GitHub | 冻结统一版本并 push 到 GitHub | ✅ Done / 完成 |
| 6 | Six live model batteries, one per member | 六套 live 模型测试（每人一套） | 🟡 **5 of 6 已跑**（4 套已入库；Sun Hanyu 待按规范提交）|
| 7 | Ten human judgements | 10项人工判定 | 🟡 **2 of 10**（SHI SHUYI 的两项已填；其余在六套合并后统一收集）|
| 8 | Report with real live numbers | 报告填入真实数据 | 🟡 Draft exists / 草稿已有（2,021 词，已超 2,000 词上限）|

---

## 3 · What each member delivers / 每人要交的三样东西

1. **Live result** — the complete JSON file from your assigned model, committed under `results/live/`
   **Live 结果** — 你负责模型的完整 JSON 结果文件，放在 `results/live/` 下提交

2. **Strand review** — findings or an explicit approval for your strand
   **代码审阅** — 你负责模块的问题，或明确批准

3. **Judgement cases** — the human verdict on the cases assigned to you
   **人工判定** — 你负责案例的人工判定结果

---

## 4 · Delivery status / 交付情况

| Member | Battery | Strand review | Note / 备注 |
|---|---|---|---|
| Meng Sijia | ✅ done | ✅ returned | 结果已在 `member/meng-sijia`；审阅通过团队 bot 于 9月19日 16:31 提交，**尚未在仓库里**，需她推到 `review/member_work/` |
| SHI SHUYI | ✅ done | ✅ returned | 结果与审阅均在 `member/shi-shuyi` |
| Su Yang | ⏳ not yet | ⏳ not yet | 分支尚未建立 / branch not created yet |
| Isha Kirti Ghia | ✅ done | ✅ returned | Phase A 仍待她本人确认签署 |
| Sun Hanyu | ⚠️ run complete, still in the wrong path | ⏳ not yet | 9月19日 16:57 重新上传了一次，但 JSON 落在**仓库根目录**而不是 `results/live/`；根目录那份和 `results/scripted/live_results_backup.zip` 都需要删掉后重传 |
| Zhang Jiayang | ✅ done | ✅ returned | — |

**One correction to send back to Meng Sijia / 需要退回给 Meng 的一处更正：** her Phase B review states that the ten *negative* cases are `CLM-8842, 8888, 8894, 8901, 8910, 8925, 8933, 8941, 8952, 9019`. Those are the ten **human-judgement** cases, not the negatives. The rule she quotes is correct (`is_negative` = expected decision `request_document` or `escalate`), and both sets happen to contain ten cases, so her 40→60 arithmetic still holds — but the case lists differ. The real negative set is `CLM-8888, 8894, 8901, 8910, **8917**, 8925, 8933, 8941, 8952, **9025**`; `CLM-8842` and `CLM-9019` are in the judgement queue but are ordinary approvals (one trial each). She should correct this before it goes into the report or the video.
她的 Phase B 审阅把"十个人工判定案例"当成了"十个负面案例"。她引用的判定规则是对的（负面 = 期望结果是 `request_document` 或 `escalate`），两组恰好都是 10 个，所以 40→60 的算术没错，但名单不同。真正的负面集合见上；`CLM-8842`、`CLM-9019` 在判定队列里，但属于普通通过案例（只跑一次）。建议她在报告和视频里更正这一点。

---

## 5 · Measured results / 实测结果

| Member | Model | Prompt | Passed | Negative trials | Measured cost |
|---|---|---|---|---|---|
| Meng Sijia | `google/gemini-2.5-flash-lite` | v2 | **9/60** (15.0%) | 9/30 | US$0.0436 |
| SHI SHUYI | `qwen/qwen3-30b-a3b-instruct-2507` | v2 | **16/60** (26.7%) | 11/30 | US$0.0633 |
| Su Yang | `anthropic/claude-haiku-4.5` | v2 | — | — | — |
| Isha Kirti Ghia | `meta-llama/llama-4-maverick` | v2 | **10/60** (16.7%) | 9/30 | US$0.1481 |
| Sun Hanyu | `deepseek/deepseek-v3.2` | v2 | **16/60** (26.7%) | 13/30 | US$0.0773 |
| Zhang Jiayang | `google/gemini-2.5-flash-lite` | v1 (control) | **6/60** (10.0%) | 6/30 | US$0.0420 |

All five recorded runs used the **same commit `42253ad`**, a clean tree, and identical case / answer-key / v2 prompt hashes. Five of five consistent — no rerun needed so far.
五套已记录的运行使用**同一 commit `42253ad`**、树干净、案例/答案键/prompt 哈希一致。5/5 一致，目前没有一套需要重跑。

The ACI comparison now has both halves of its pair: the **same model** scores 9/60 under the v2 prompt (Meng) and 6/60 under v1 (Zhang).
v1/v2 对照现在两半都齐了：**同一个模型**在 v2 下 9/60（Meng），在 v1 下 6/60（Zhang）。

---

## 6 · Rules from the brief / 老师的硬性要求

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

## 7 · Frozen version and branches / 冻结版本与分支

**Repository:** `https://github.com/leosu5723-ys/NTU_6201_Group-1`
**Frozen experiment commit:** `42253ad28fc58b36b9014808f9d8e3fd523c01ed` — the tip of `main`. `main` has not moved and will not move until all six batteries are collected, so pulling `main` is enough. Confirm with `git rev-parse HEAD` before your paid run.

```bash
git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
cd NTU_6201_Group-1

git rev-parse HEAD                        # must print 42253ad28fc...
python3 -m unittest discover -s tests -q  # expect: OK (101 tests)
python3 run_eval.py                       # expect: "passed": 60
```

**Branches pushed so far:** `member/meng-sijia`, `member/shi-shuyi`, `member/isha-kirti-ghia`, `member/sun-hanyu`, `member/zhang-jiayang`. No branch yet for Su Yang.
**已推送分支：** 上述五条；Su Yang 尚未建立。

An open pull request from `member/isha-kirti-ghia` **must not be merged yet** — merging moves `main` off `42253ad` and would void any checkout that is still to run. Merging happens once, at the end.

**Nobody pushes to `main`.** Each member pushes `member/<name>`; SHI SHUYI merges at the end.

---

## 8 · Pipeline / 流程

```
1. Freeze and push               → 冻结版本并推送              ✅ done / 已完成
2. Everyone runs their battery   → 全队各自跑自己的 battery      🟡 5 of 6（等 Su Yang；Sun 需重交）
3. Send back your answers        → 回报五行简短回答
4. Collect six results           → 收齐六份结果
5. Merge the six branches        → 合并六条分支（贡献者列表只在 main 上生效）
6. Ten human judgements          → 十项人工判定（合并后统一发出）
7. Report numbers, video, package → 报告填数、视频、打包提交
```

`main` stays frozen until step 4 is complete. / 第 4 步完成前 `main` 保持不动。
