# Change Proposal: P49 — 返回值粒度可区分性 + 非必要不新增实体/方法 + 实现层复用核验（清单三落点）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Standards（review/implement 检查清单补充） |
| Author | AI Maintainer |
| Created | 2026-09-09 |
| Reference | T-011 方法级走查（develop-20260909-105848.md，布尔折叠设计缺陷 → L3 修订）；T-025/026 followup review（自研删除循环重复实现既有 onDelete 语义 → 97424ef2 重构）；cool-italent 20 卡返工统计（2 followup + 1 Changes Required）；用户决策（2026-09-09，karpathy 转强制校验按方案 A） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

现网 review/implement 检查清单存在两类缺口，均已在真实运行中造成提交后返工：

- **返回值粒度缺口（T-011）**：`MigrationValidateResult` 仅 `owned(boolean)`，validate() 5 个失败分支（入参不完整/查无/eid 不符/storage 为空/storageType 不符）全部折叠为 `owned=false`，下游 T-001 一律落 `FAILED(OWNERSHIP_MISMATCH)`——数据异常与真实归属不可区分。该缺陷在 **review PASS 之后**、用户要求的方法级走查才暴露，触发 L3 修订（契约+spec+2 卡+代码重写）。
- **实现层复用缺口（T-025/026）**：AI 自研删除循环与既有标准同步 handler（`BsUserSyncHandler.onDelete`/`BsDeptSyncHandler.onDelete`）重复实现两套北森删除语义（200/417/429 判定、清 mapping、失败补偿），违背 Single Source of Truth；followup review 才暴露 → 重构为委托（97424ef2）。

两案共性：**AI 自查清单与 review 清单都不含「返回值信息量」「非必要不新增实体/方法（复用）」检查维度**，缺陷在实现期自由产生、提交后才发现。

## 2. Root-Cause

- 检查清单核验「正确性」但不核验「返回值信息量」——布尔折叠使下游失去原因维度（T-011 类）。
- 复用纪律（karpathy Read Existing Code / REPOSITORY_FIRST Required Search / task-quality-checklist「Reuse first」）是**原则**而非**可核对检查项**；plan 期扫描可浅、实现期自查可宽松、review 无实现层复用核验（T-025/026 类）。
- quality-gates Gate 4「Duplication」只查**资产层**（checklists/playbook/模板重复），不查**代码实现层**（自研替代既有）。
- 调研结论（2026-09-09）：karpathy 无自动化校验方案；实现层复用核验属语义级判断，自动检测（相似度）不可靠——须靠清单 + review 人工核验（见 §5 / §7）。

## 3. Options

| 选项 | 内容 | 评估 |
|---|---|---|
| **A（推荐）** | 清单三落点：前置计划自检 / 实现后置自检 / review 复核，各增「返回值粒度可区分性 + 非必要不新增实体/方法 + 实现层复用核验」条目；review 报告增复用核验结论字段 | 轻量、覆盖 T-011/T-025/026 两类实证；与 P50 双确认模型联动（清单喂给前置 AI 自检） |
| B | A + quality-gates 自动化（实现层复用 Gate） | 更硬，但语义级检测启发式高误报；转后续待办 |
| C | 仅加 review 条目（不动 implement 清单） | 缺实现期自查，拦截点后移 |

## 4. Recommendation

**方案 A**。理由：① 两条实证缺陷恰好落在「自查清单无此项」的空隙，清单补齐即拦截；② 三落点（计划/实现/review）让 AI 先自检、review 兜底，符合「AI 先自检、用户后决策」；③ 自动化检测不可靠（调研结论），B 项转后续待办（quality-gates），不在本提案范围。

## 5. Proposed Changes

1. **skills/implement/checklists.md**（Code Quality / Unit Tests 节）增：
   - 「返回值粒度可区分性」：失败分支是否可区分？布尔折叠反模式 → 枚举/原因码（对齐 T-011 教训：双层模型 = 技术码 + 呈现层文案）；
   - 「非必要不新增实体/方法」：每个新方法/新类自问——存量能否复用/扩展现有？理由是什么？（对齐 karpathy Read Existing Code / Simplicity）
2. **skills/review/SKILL.md** 执行节增：
   - 「返回值粒度核验」：diff 中新增/修改方法返回语义是否满足下游可区分性；
   - 「实现层复用核验」：新方法是否绕过既有实现重新实现（自研替代既有）——对齐 T-025/026 followup 做法，固化为常规检查项。
3. **review 报告**（可选字段）：增「实现层复用核验」结论行（复用/扩展/新建 + 依据），供 verify 与审计追溯。
4. **与 P50 联动**：P49 清单作为 P50 前置确认「AI 先自检」的判据（plan 自检 + 实现自检两次喂入）。
5. **不新增自动检测**：quality-gates 实现层复用 Gate 登记为后续待办（引用本提案调研结论）。

## 6. Validation Plan

- 清单条目落位后，用 T-011（布尔折叠）与 T-025/026（自研删除循环）两个历史案例回放：模拟清单逐项自检，确认两项均能命中。
- check.py / repo-lint / path-audit 全绿；语言门禁 PASS（清单为英文纪律区，检查项文案英文）。
- 试点：随 P50 在 security-migration T-001/T-008 或下张接口/重构卡验证清单实际拦截效果。

## 7. Risks

- **清单被表面勾选**：AI 自查项可能形式化打勾——由 review 复核兜底（三落点中 review 是强制层）。
- **误判边界**：复用 vs 新建是 judgement call（对齐 smell-baseline「Always a judgement call」语义），清单保持启发式标注，不作硬性阻断。
- **过度约束**：规则化「必须复用」可能迫使为复用而复用（坏抽象）——条目表述为「先自问再决策」，保留新建的合法路径（如既有实现不满足契约语义时）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（决策②：karpathy 转强制校验按方案 A；quality-gates 转后续待办） | 2026-09-09 |

---

## Implementation Record (2026-09-09)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `skills/implement/checklists.md`：Code Quality 节增「Return-granularity check (P49)」「Non-necessary entities/methods (karpathy Read Existing Code)」2 项；Unit Tests 节增「Failure-branch distinctiveness covered」1 项。
2. `skills/review/SKILL.md`：Code Review 阶段增「Return-Granularity Verification (P49)」「Implementation-Layer Reuse Verification (P49)」2 项。
3. 与 P50 联动：P49 清单作为 P50 前置/后置 AI 自检判据（plan + implementation 两次喂入）。
4. quality-gates 实现层复用 Gate：**后续待办**（调研结论见 §3/§7，不纳入本提案实施）。

**Validation**：repo-lint 0/0/26（无新增 WARN）；path-audit OK；check.py PASS（3 已知 WARN）；unittest 242 OK；workflow-command-audit 0 blocker。语言 gate 对英文纪律区资产 FAIL 为既有预期（gate 仅适用于用户面报告，未改动模板/技能亦同样 FAIL，非本提案回归）。
