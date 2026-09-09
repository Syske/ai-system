# Change Proposal: P54 — 消除双重计划（implement Stage 2 复用已确认计划）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（implement skill 计划阶段语义收敛 + runtime-develop 联动） |
| Author | AI Maintainer |
| Created | 2026-09-09 |
| Reference | develop 链耗时诊断（2026-09-09）：develop-20260909-153123.md 中断日志 + runtime-develop Phase 2/implement Stage 2 双重 Generate 实证；A1（Plan Gate）已实施同批次；用户决策（其余问题评估价值后立档） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

开发主链每卡存在**两次完整计划推断 + 两次用户确认**：

```
runtime Phase 2：生成计划（含 P50 方法粒度摘要+复用扫描）→ 用户确认 → 持久化 tasks/plans/{id}-plan.md
        ↓
implement Stage 2：「Generate an implementation plan」（workflow.md 明示 Generate，未引用已确认计划文件）
        ↓
Stage 3：又「Wait for user confirmation」
```

P50 前置内容（方法粒度设计摘要 / 复用决策 / P49 自检）在这两处同时出现——双重推断被放大。这是 develop 链「自行推断运行时间过长」的结构性根因之一（诊断根因 E）。

## 2. Root-Cause

- `skills/implement/workflow.md` Stage 2 无条件要求 Generate，**未检查/复用** runtime Phase 2 已确认并持久化的计划文件。
- runtime 与 implement skill 的计划职责重叠：前者负责「计划确认+持久化」（供 review/verify 对比），后者重复做一次。

## 3. Options

| 选项 | 内容 | 评估 |
|---|---|---|
| **A（推荐）** | implement Stage 2 改为**复用已确认计划**：先检查 `tasks/plans/{task_id}-plan.md`，存在即装载并进入实现；仅无计划文件（独立调用 implement 或无 runtime 前置）才 Generate；Stage 3 确认收敛为「计划与 Task Card 一致即通过，有偏差才重开」 | 每卡省 1 次完整计划推断 + 1 次确认；与 A1（Plan Gate：实现前必有已批准计划）联动闭环 |
| B | 维持现状（runtime 与 implement 各自计划） | 冗余但两段隔离；耗时问题不解决 |
| C | 移除 runtime Phase 2 计划 | 不可取——plan 必须在 runtime 层确认持久化（review/verify 对比依据） |

## 4. Recommendation

**方案 A**。理由：① 计划推断是耗时大头，消除重复收益最大（诊断实证）；② A1 已保证「实现前必有已批准计划」，implement 复用它是自然衔接；③ 保留 Generate fallback（无计划文件时），不破坏 implement 作为独立 skill 的可用性。

## 5. Proposed Changes

1. `skills/implement/workflow.md` Stage 2：语义改为「装载已确认计划——`tasks/plans/{task_id}-plan.md` 存在即复用（核对与 Task Card 一致），仅缺失时才 Generate（独立调用场景）」；Stage 3 确认改「与卡一致即通过，有偏差才重开确认」。
2. `skills/implement/SKILL.md` Planning Gate / Post-Implementation Confirmation 描述同步（引用已确认计划；P50 内容不再重复 Generate）。
3. 与 A1 联动：runtime-develop Phase 1 Plan Gate 已保证计划存在；implement 不再重复设计。
4. 不缩 10 阶段骨架、不动其它阶段。

## 6. Validation Plan

- 流程回放：T-009 恢复时——有 T-009-plan.md（A4 补定后）→ implement 直接装载不复推；无计划文件（独立调用）→ Generate fallback 生效。
- 门禁：check.py / repo-lint / path-audit 全绿；unittest 全量。
- 与 A1 联合验收：develop 无计划进入 → 被 Plan Gate 拦截；有计划 → implement 不重复推断。

## 7. Risks

- **implement 独立性**：作为独立 skill 被非主链流程调用时无 runtime plan → Generate fallback 兜底（明确写出）。
- **确认语义收敛**：Stage 3「一致即通过」可能弱化 implement 独立确认——保留「有偏差重开」路径，且 runtime Phase 2 确认在前，安全网仍在。
- **计划陈旧**：复用计划需先核对与当前 Task Card 一致（A1 同语义），不一致走偏差流程（L2）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-09-09 |

---

## Implementation Record

**Implemented 2026-09-09**（方案 A）

- `skills/implement/workflow.md` Stage 2：复用优先——先查 `.../tasks/plans/{task_id}-plan.md`，存在且与卡一致 → 直接进 Stage 4（预批准，不重复 Generate/确认往返）；缺失（独立调用）→ 走 planning.md 生成 + Stage 3 确认。Stage 3 改条件式（仅生成路径强制等确认）。
- `skills/implement/SKILL.md` Planning Gate：同步复用语义（已确认计划装载 + 卡一致性核验；偏差 L2）；生成路径保留 P50 方法粒度摘要 + 复用扫描 + P49 自检。
- 与 A1 联动闭环：runtime Plan Gate 保证实现前有已批准计划；implement 复用它，不再重复设计。
- 不缩 10 阶段骨架，不动其它阶段；planning.md 持久化约定（L317-321）保持为生成路径锚点。

**Validation（2026-09-09）**：unittest 258 OK · repo-lint 0/0/26 · check PASS · language 纪律区 0 残留
