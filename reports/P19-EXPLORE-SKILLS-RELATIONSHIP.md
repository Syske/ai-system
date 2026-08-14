# Change Proposal: P19 — explore 与 explore-codebase 技能合并评估（D5）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (capability consolidation evaluation) |
| Author | AI Maintainer |
| Created | 2026-08-08 |
| Reference | MAINTENANCE-2026-08-08.md D5 / S4 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

两个"代码库探索"能力技能并存：

- `skills/explore/skill.md`（64 行）：OpenSpec-aware 探索，加载方为 `aic-explore` 命令，非独立使用。
- `skills/explore-codebase/skill.md`（28 行）：基于知识图谱的代码库结构理解，独立技能。

用途声明重叠（"understand the codebase before a change"），机制不同（OpenSpec 工作区 vs 知识图谱）、入口不同（CLI 命令 vs 独立技能）。当前判定 LOW-MED 重叠、暂不合并，但长期并存增加维护成本与选择歧义。

## 2. Root-Cause

两个技能在不同需求点分别创建（explore 为 aic-explore 命令配套、explore-codebase 为知识图谱探索流程），未在创建时做能力矩阵重叠检查；repository-maintainer 能力矩阵（Dimension 4）的 >60% 重叠阈值未触发显式合并流程。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A | 合并：explore 吸收 explore-codebase 的知识图谱方法（explore 作为主技能，explore-codebase 归档），或反之 | 单能力单主 | 需处理命令/技能引用迁移（aic-explore、知识图谱流程） |
| B（推荐，先行） | 保持并存，但明确职责边界：explore = 命令配套（OpenSpec 工作区导航），explore-codebase = 独立代码库结构理解（知识图谱）；在双方 skill.md 增加交叉引用与"何时用哪个"决策表 | 改动小、无迁移风险 | 未消除重复，仅消除歧义 |
| C | 维持现状 | 零改动 | 选择歧义持续 |

## 4. Recommendation

**Option B（本周期）**：先做职责澄清与互引决策表，观察实际使用；**季度评估**是否升级 Option A 合并（需统计两技能实际触发频次后决定）。理由：两技能机制与入口不同，合并收益不确定，最小改动优先（遵循 Evolution Principle：真实使用数据驱动结构性变更）。

## 5. Proposed Changes

1. `skills/explore/skill.md`：新增「与 explore-codebase 的关系」小节——explore 定位（OpenSpec 工作区导航、aic-explore 命令配套）；指向 explore-codebase。
2. `skills/explore-codebase/skill.md`：新增「与 explore 的关系」小节——explore-codebase 定位（独立、知识图谱驱动的代码库结构理解）；指向 explore。
3. 双方各附 3-4 行「何时用哪个」决策表。
4. 季度维护时统计两技能引用/触发，评估 Option A。

## 6. Validation Plan

- `python tools/repo-lint.py --repo-root .`：0 BLOCKER/ERROR
- 交叉引用检查：两文件互相指向存在。
- 无命令/流程引用破坏（explore 仍由 aic-explore 加载；explore-codebase 独立可用）。

## 7. Risks

- 交叉引用可能被 dependency-graph 误判为依赖环（与 P13 同类）。缓解：文档性提及已由检测器 doc-only 语义分层处理，实测验证。
- 边界定义若含糊会导致选择仍然模糊。缓解：决策表按触发场景（"被 aic-explore 调用" vs "独立结构理解任务"）区分。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved & Implemented** | 2026-08-14 |

---

## Implementation Record (2026-08-14)

Applied per approval (OPERATIONS §12 → Implement → Validate), Option B:

1. `skills/explore/SKILL.md`（129 → 158 行）: 新增「Relationship with
explore-codebase」小节——定位（aic-explore 命令配套, OpenSpec 工作区导航）
+ 指向 explore-codebase + 4 行「Which to use」决策表。
2. `skills/explore-codebase/SKILL.md`（28 → 59 行）: 新增「Relationship with
explore」小节——定位（独立, 知识图谱驱动的代码库结构理解）+ 指向 explore
+ 4 行「Which to use」决策表。

**Validation**: 交叉引用检查（双向互引存在）/ repo-lint 0 BLOCKER 0 ERROR /
path-audit OK（无 broken path）/ check.py PASS。

**Deviations**: 无。技能行数增长（explore-codebase 28→59 行, 未超 80 阈值）。

**Next**: 季度维护统计两技能实际触发频次, 评估 Option A 合并（遵循 Evolution
Principle: 真实使用数据驱动结构性变更）。
