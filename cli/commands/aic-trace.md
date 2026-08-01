---
description: 分支差异对账 - 对比需求分支与 master 的代码差异，反查 spec/任务卡并驱动补账或生成变更
---

对比当前需求分支与基线分支（默认 master）的代码差异，反向追溯每个差异的任务卡、规格场景与契约；对不上账的部分，经确认后**优化既有变更集**或**生成新变更集**。

**输入**：Project ID；可选 Code Reference（聚焦差异中的特定文件/符号）；可选 Change ID（限定变更集）；可选 Base Branch（默认 master）。

**步骤**

1. **定位工作区与仓库**
   - 变更集根：`workspaces/{project_id}/openspec/changes/`（排除 archive/）
   - 相关服务仓库：从项目上下文 services 列表解析，本地路径 `projects/{service_id}`

2. **差异采集（trace 范围 = 分支 diff，不是全仓）**

   对每个相关服务仓库：

   ```bash
   git diff --name-status {base}...HEAD     # 变更文件清单（merge-base 三点比较）
   git log --oneline {base}..HEAD           # 分支提交，提取 T-xxx 任务号
   ```

   - 提供了 Code Reference → 只保留命中的差异文件
   - 当前分支即基线分支 → 报告"无分支差异"并停止

3. **逐差异文件反查**
   - Git 线索：分支名 `task/{T-xxx}`、提交信息中的 T-xxx → Task ID
   - 工件检索：grep 任务卡（tasks/cards/*.md）、每服务拆分（{service}-tasks.md）、规格场景（specs/*/spec.md）、契约（contracts/interop_contract.yml）

4. **Trace Report（对账矩阵）**

   | Changed File | Commit / Branch | Task Card | Spec Scenario | Contract | Status |
   |---|---|---|---|---|---|

   Status 判定：
   - `MATCHED` — 代码、任务卡、spec 三方一致
   - `TASK_STALE` — 有归属任务卡，但完成定义/验收标准与实现对不上（未勾/漏勾/内容过时）
   - `SPEC_STALE` — 实现行为超出/偏离 spec 场景描述
   - `UNTRACKED` — 差异不属于任何任务卡与 spec 场景

5. **裁决与修复（停机确认后执行 — Change Control 纪律）**

   先输出修复计划清单，等待用户确认，再执行：

   - `TASK_STALE` / `SPEC_STALE` 且属于在途变更 → **优化既有工件**（OPERATIONS.md 1.6 补账）：
     就地更新 `changes/{change_id}/` 的 specs delta、任务卡（补验收依据、校正勾选）、契约条目
   - `UNTRACKED` 且改动是被认可的 → **生成新变更集**：
     推导 kebab-case 变更名 → `openspec-cn new change "<name>"`（/aic-propose 流程）补齐 proposal / specs / tasks，任务卡直接附实现证据
   - 改动属于未经认可的漂移 → 列入**回退建议**（develop 按 spec 修正），本命令不动代码

6. **下一步动作（完成后必问）**

   对账与修复完成后，使用 **AskUserQuestion tool** 让用户选择下一步：

   - **verify**（推荐，若工件已对齐）：就地执行——加载 `ai-system/workflows/verify.md` 与 `ai-system/templates/runtime/runtime-verify.md`，对每个受影响的 Task ID 按契约执行正确性核验，产出验证报告
   - **review**（若涉及实现质量复核）：加载 review 契约执行，之后再 verify（OPERATIONS.md 1.6 标准关门顺序）
   - **spec re-entry**（若对账发现需要更大范围的规格更新）：提示运行 `python -m cli.main prepare --change <change_id> --request "<变动点>" --mode re-entry`
   - **finish**：仅输出 Trace Report 结束

   用户选择后立即执行所选动作，不要自行决定。

   收尾提醒：本次对账中的所有工件修改逐条记入 Deviations。

**输出**

## Trace Report

对账矩阵 + 每个非 MATCHED 项的修复方案与执行结果（或待确认状态）。

**护栏**

- 只修改工件（spec / task / contract / proposal），**永不修改代码**
- 每一批工件修改前必须确认（L2/L3 纪律）
- 差异采集只读 git，禁全仓通读；按 Task → Spec → Contract → Repository 顺序最小加载
- 当前变更未归档时不为同一行为重复开变更集
