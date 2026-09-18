# Change Proposal: P56 — SenSpec 价值吸收上链（证据等级/读取纪律/熔断/指针/图形规则）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Governance/Standard（标准 + 任务卡/评审/运行时模板 + 纪律文档） |
| Author | AI Maintainer |
| Created | 2026-09-17 |
| Reference | 用户确认（1+2 + P2）；第三方后端规格库评估（SenSpec，**来源路径已脱敏**，评估材料见 outputs/comparison/，不入库）；与 tr5 扩展既有的 coolspec 规则资产同源（extensions/tr5/references/，来源路径已脱敏） |
| Process | OPERATIONS §12 Change Management（用户确认后执行；本提案为追溯归档） |

---

## 1. Problem

外部后端规格库（SenSpec，来源路径已脱敏）中经评估确认有价值的规约要素，此前仅在
TR5 扩展侧吸收（coolspec 规则资产：quality-gates / behavior-discipline / coding-depth，
来源路径已脱敏），**主链（任务卡/评审报告/运行时纪律/上下文加载）尚未接入**。其中
两批要素经评估价值明确、成本低：①证据等级纪律（E1-E4）；②读取纪律（读账本 + 数值硬上限）。
另有三项顺带落地：修复重验熔断、指针不重抄、TR5 图形规则分层。

## 2. 评估结论（脱敏摘要）

- 证据等级：该库行为纪律将技术结论分级（代码事实/文档事实/推断/假设）——主链技术结论
  （任务卡完成定义、评审 findings、设计结论）无强制分级，存在捏造/虚报风险；
- 读取纪律：该库对上下文读取设数值硬上限（同文件单步 ≤2 次、整篇 ≤1 次）——与
  CONTEXT_LOADING 预算纪律互补，可数值化；
- 修正配额/指针引用/图形规则分层：主链已有等效纪律（一次一问/L3 防扩/任务卡引用），
  增量有限，仅取"修复重验轮次上限""不重抄""画不画-怎么画分层"三点低成本落地。

## 3. Options

| 选项 | 说明 | 取舍 |
|---|---|---|
| A. 仅 TR5 扩展侧吸收 | 维持现状 | ❌ 主链纪律缺口仍在（评审/任务卡无证据等级） |
| B. 主链全量接入 | 全部要素上链 | ❌ 过度（多数要素已被既有纪律覆盖） |
| C. **选择性上链** | 证据等级 + 读取纪律 + 三点低成本项 | ✅ 采用 |

## 4. Decision（2026-09-17，用户确认 1+2 + P2）

**方案 C**：①E1-E4 证据等级上提主链；②读账本 + 数值硬上限入 CONTEXT_LOADING；
③修复重验熔断、指针不重抄、TR5 图形规则分层顺带落地。

## Implementation Record (2026-09-17)

1. 证据等级：新建 `governance/standards/common/evidence-levels.md`（E1 代码事实/E2 文档事实/
   E3 推断/E4 假设 + `⚠️ 待确认: {owner}/{deadline}` 占位符 + 降级规则 + 应用点）；
   任务卡模板（task-splitter + templates/prompts/tasks-template 两处对齐）新增证据等级字段；
   review SKILL findings 事实性结论须标等级（未标视为 E4）。
2. 读取纪律：`governance/CONTEXT_LOADING.md` 新增 Read Discipline（读账本、同文件 Step ≤2 次/
   整篇 ≤1 次、触限停止改占位符、检索优先、读后总结）。
3. 修复重验熔断：`runtime-review.md` + `runtime-verify.md` 新增 Fix-Reverify Circuit
   （驳回/FAIL 循环 ≤2 轮，第 3 次停止交用户裁决，每轮 fresh 验证）。
4. 指针不重抄：`runtime-develop.md` Phase 1 新增 Pointer discipline（任务卡/计划单一事实源，
   工作产物只引用卡 ID+计划路径）。
5. TR5 图形规则分层：`extensions/tr5/references/drawing-rules.md`（画不画→画什么→怎么画→
   落盘→配说明→自查六节，收敛既有脚本约束与布局规则）。

**Validation**：check.py PASS（2 已知 WARN）；repo-lint 0/0/25 基线（迁移 skill 后 28 属既有口径）；
path-audit 0 broken；unittest 294 OK；runtime 英文纪律区新增内容全英文（双语标题为许可模式）。
