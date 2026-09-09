# Change Proposal: P50 — 方法粒度双确认模型（开发主链前置方案确认 + 后置一致性确认）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（开发运行时机制：runtime-develop + implement skill + 任务卡字段） |
| Author | AI Maintainer |
| Created | 2026-09-09 |
| Reference | T-011 布尔折叠（develop-20260909-105848.md，提交后 L3 修订）；T-025/026 followup review（Changes Required → 123af53b 修复 → verify BLOCKED）；cool-italent 20 卡返工统计（2 followup + 1 Changes Required）；用户决策 2026-09-09（采纳方法粒度双确认模型 + karpathy 校验按方案 A）；联动 P49（清单三落点）、P26（分支/流程）、P45（语言门禁 @keep 惯例） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

开发主链当前只有**计划粒度（approach）确认**：runtime-develop Phase 2「Wait for confirmation」+ implement skill Planning Gate 确认的是文件清单/步骤序列/设计决策（D1-D7）。**方法粒度细节（返回粒度、失败分支表示、资源语义、复用决策）在确认范围之外，编码期由 AI 自由决定**，且自检清单无对应维度（P49 缺口）——于是：

- T-011：返回粒度决策（布尔 vs 枚举）在实现自由区丢失 → 提交后用户走查才发现 → L3 修订 + 契约/spec/卡重写；
- T-025/026：复用决策（自研 vs 委托既有 handler）未在计划期澄清 → review 才暴露 → 重构返工 → 修复后 verify 又因缺快速复核 BLOCKED。

共性：**确认点粒度与风险层不匹配**——返工重灾区（接口面/资源语义/复用）恰在「计划确认之后、提交之前」的无确认区。

## 2. Root-Cause

- 确认只在计划粒度发生一次；实现中才定型的**设计关键面**无人确认（计划无法预见全部细节，但接口面/返回语义/资源语义属于可预见且高价值）。
- 两次返工案例的共同点是**用户以方法粒度介入（走查/再审查）才暴露**——说明方法粒度信息是有效决策输入，但现网没有把它前置到提交前。
- 复用纪律（karpathy/REPOSITORY_FIRST）是原则非必答项，计划期无「存量复用扫描 + 复用决策」强制出口（P49 同源，本提案从流程层解决）。
- 现有 L2 变更控制只对「实现中发现的偏差」生效（停止+确认），对「按计划实现了但方法粒度本身不达标」不生效——后者无用户可见点。

## 3. Options

| 选项 | 内容 | 评估 |
|---|---|---|
| **B（推荐）** | 条件式**方法粒度双确认**：前置确认升级为方法粒度方案确认（三面：接口面 + 资源语义 + 复用决策面，AI 先按 P49 清单自检计划）；后置确认门（条件触发，最终提交前呈现实现方法粒度摘要 + 自检证据 + 与方案偏差，用户确认后提交） | 前置拦设计缺陷于编码前，后置降维为一致性核验；条件式防确认疲劳；覆盖 T-011/T-025/026 两类实证 |
| A | 仅后置确认（前置维持 approach 粒度） | 设计缺陷仍到实现后才发现，返工成本已在 |
| C | 全量后置确认（每卡必确认） | 机械卡（DTO/通道 bean）确认无价值；确认疲劳→橡皮图章；违背 ATTENTION_MANAGEMENT |

## 4. Recommendation

**方案 B —— 方法粒度双确认模型**，要点：

1. **前置确认升级（方法粒度，选择性）**：计划含「方法粒度设计摘要」——设计关键面方法（接口/契约面）的签名、返回粒度与失败分支表示、资源/错误语义；重构/行为变更类卡扩展内部关键语义（finally/复位/关键流转）。AI 先按 P49 清单自检计划，再交用户确认【方案】。
2. **复用决策面（karpathy 落地闸）**：计划期必有「存量复用扫描」步骤（REPOSITORY_FIRST 落地）；发现现网类似实现 → 显式给出复用决策（复用/扩展/新建 + 推荐）作为前置确认必答点，禁止 AI 静默 copy/重写。
3. **后置一致性确认（条件触发，最终提交前）**：呈现实现方法粒度摘要（新/改方法签名、返回/失败表示、资源语义、复用决策执行情况）+ 自检证据（门禁摘要 + P49 清单）+ 与确认方案的偏差。用户确认后提交。
4. **漂移处置**：前后对照暴露偏差即 L2 信号（方案缺口/实现走偏）→ 走既有 L2 停止确认，不另设触发。
5. **触发条件**（满足任一触发前后确认）：① 接口/契约面（RPC facade/返回模型/枚举错误码/MQ 消息体）；② 重构/行为变更（删除既有逻辑/委托重构/资源管理变更）；③ 跨组件/跨仓契约。机械卡（DTO/通道 bean/配置/文档）跳过。
6. **触发判定**：task-splitter 阶段在 Task Card 标注（如 `confirm: pre-commit`）为主，develop 时 AI 按实现特征判定兜底。
7. **时序**：前置在编码前；后置在最终提交前（实现中小步自提交不冲突，同卡合并为一次前置 + 一次后置确认）。

## 5. Proposed Changes

1. **templates/runtime/runtime-develop.md**：Phase 2 前置确认内容扩为方法粒度设计摘要（三面 + 复用扫描必答）；Phase 3 末尾新增条件式后置确认门（最终提交前，确认后提交；`@keep` 门禁步骤登记诊断日志，对齐 P45 惯例）。
2. **skills/implement/SKILL.md**：Planning Gate 扩展（计划含方法粒度设计摘要 + 存量复用扫描必答）；Validation 后新增条件式「实现方案确认」步骤（触发类卡）。
3. **task-splitter**：Task Card 模板新增触发标注字段（`confirm: pre-commit` 或等价），按卡验收准则是否涉接口/契约/重构判定。
4. **呈现模板**（runtime-develop 附）：方法清单+签名 / 返回粒度与失败分支 / 资源语义（重构类）/ 复用决策执行情况 / 偏差清单 / 门禁结果摘要——一屏可确认，非全量代码。
5. **联动 P49**：前置「AI 先自检」与后置自检均以 P49 清单为判据（P49 §5.4）。
6. **试点**：security-migration T-001（KA 提交受理，接口类）/ T-008（OSS copy 执行器）两卡先行验证，再推广。

## 6. Validation Plan

- 试点两卡：验证 ① 前置确认含三面 + 复用扫描记录；② 后置确认发生且实现与方案一致时用户快速通过；③ 人为引入偏差时暴露为 L2 信号。
- 门禁：check.py / repo-lint / path-audit 全绿；unittest（若改 cli 逻辑）全量跑；语言门禁 PASS（确认请求按系统语言 zh，@keep 登记）。
- 回归：机械类卡（无触发）确认不产生额外交互。

## 7. Risks

- **确认疲劳**：条件式触发 + 合并确认（同卡两次）+ 一屏摘要缓解；若试点反馈仍重，降级为仅接口/重构类触发。
- **触发漏判**：卡字段（splitter 标注）为主 + develop 特征兜底双保险；漏判可后续补（review 仍兜底）。
- **前置过度设计**：方法粒度摘要仅设计关键面（选择性），内部 helper 不写进计划——避免把实现焊死。
- **不替代 review**：后置确认只拦「实现不符合预期」；review 仍负责工程质量（P49 三落点含 review 层）。
- **流程感知成本**：模板改动对进行中会话不生效（后续会话生效），与既有模板变更惯例一致。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（决策①：采纳方法粒度双确认模型；P50 实施含前置三面+复用决策面+后置一致性确认） | 2026-09-09 |

---

## Implementation Record (2026-09-09)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `templates/runtime/runtime-develop.md`：Phase 2 前置确认扩为方法粒度设计摘要（三面：接口面/资源语义/复用决策面）+ 存量复用扫描必答 + P49 自检先行；Phase 3 增条件式 Post-Implementation Confirmation（触发类卡最终提交前呈现方法粒度摘要待确认，机械卡跳过，偏差即 L2，`@keep` 登记诊断日志）。
2. `skills/implement/SKILL.md`：Planning Gate 扩（方法粒度设计摘要 + 复用决策必答）；新增 Post-Implementation Confirmation (P50, conditional) 节。
3. `methodologies/providers/openspec-cn/templates/tasks-template.md`：任务卡新增 `**实现后置确认**` 字段（required/skip 判定）。
4. `skills/task-splitter/workflow.md`：Task Card 字段 + 推导规则（接口/契约/重构/跨仓 = required；机械类 = skip）。
5. 试点计划（T-001/T-008）随 security-migration 变更推进落地，未在本批次执行。

**Validation**：repo-lint 0/0/26；path-audit OK；check.py PASS（3 已知 WARN）；unittest 242 OK；workflow-command-audit 0 blocker。语言 gate 对英文纪律区资产 FAIL 为既有预期（gate 仅适用用户面报告，未改动模板同样 FAIL，非回归）。
