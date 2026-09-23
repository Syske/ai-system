# Change Proposal: P63 — 主链分支命名：非迭代需求形态（省略 `ipd` 段）未文档化

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (governance + runtime + Task Card 模板) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | 用户指令 2026-09-21（"我们的需求不跟随迭代，所以分支名称中不需要 ipd 关键词"）；`AI_OPERATING_RULES §Workspace Discipline`；`templates/runtime/runtime-dev-setup.md` Phase 7；**规则出处 P26**（`P26-MAIN-CHAIN-BRANCH-RULE.md`，其开放待办已覆盖 parser provider 缺口） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 现状

- 主链分支命名规则当前**只文档化了一种形态**：`cc{date}_ipd_{desc}_{service}`（标注"格式暂定"，
  并允许在"需求确认时"由用户指定/调整）。
- 2026-09-21，用户对**非迭代需求**（日志治理技改）明确指令：**省略 `ipd` 段** →
  实际冻结分支 `cc20260921_log-volume-reduction_housekeeping-service-api`（3 段：date/desc/service）。
- 即：**规则变体已在实践中生效，但未进入任何文档**；本次只能把该结论写进项目侧工件
  （`project-context.yaml` 备注、11 张卡的 `branch` 字段说明）。

### 1.2 危害

1. **不可复用**：下一个非迭代需求需再次推导规则、再次与用户确认，形成重复沟通成本。
2. **校验不一致**：主链**没有 branch parser provider**（`extensions/hotfix-branch-parser` 仅服务 bugfix hotfix 模式），
   本次只能以 ad-hoc 正则 `^cc(\d{8})_([a-z0-9-]+)_([a-z0-9-]+)$` 校验 → 各次运行的校验口径可能漂移。
   > **注（Repository First）**：该缺口**已由 P26 的开放待办跟踪**
   > （`P26-MAIN-CHAIN-BRANCH-RULE.md:52`："分支扩展 provider（extensions/ 提供者，按需；契约已预留）"）——
   > **本提案不重复承担该缺口**，仅在规则条款层补"校验口径"描述；parser 落地归 P26。
3. **相邻陷阱未文档化**：已知"服务段含下划线会使解析错位"（同服务在途变更被迫用
   `qa-manage` 连字符替代 `qa_manage`），该结论只存在于某个 workspace 的备注中，未进入规则文档。

### 1.3 根因

规则以"唯一形态"表述，但**分支名承载了两个正交维度**（是否为 IPD 迭代、desc、service），
其中"是否 IPD"是**需求属性**而非命名细节，缺显式条款 → 只能靠"允许用户调整"兜底。

## 2. Goal

把**两种合法形态**（IPD / 非迭代）纳入规则文档，并给出**可判定的选用条件**，
使分支命名在下次使用时无需重新推导、且校验口径统一。

## 3. Options

### 3.1 Option A — 文档化两种形态（最小，推荐）

- 规则：IPD 迭代需求 `cc{date}_ipd_{desc}_{service}`；**非迭代需求 `cc{date}_{desc}_{service}`**。
- 判据：需求是否随迭代（TR）发布 —— 由需求确认阶段判定，写入 Task Card `branch` 字段。
- 校验：沿用"解析器或等价正则"描述，并明确"desc/service 段禁含下划线"（消除 §1.2.3 陷阱）。

### 3.2 Option B — A + 主链 parser provider

- 在 A 基础上，把分支解析能力**纳入主链**（新增主链 provider 或把 hotfix provider 提升为通用），
  供 dev-setup Phase 7 / review / release 统一调用，消除"无 parser → ad-hoc 正则"的现状。
- **该选项的实质内容已由 P26 开放待办覆盖**（见 §1.2 注），故本提案不再重复承担；如需推进，在 P26 上继续。

### 3.3 Option C — 不改变（保持"格式暂定"每次由用户指定）

- 代价：§1.2 的三项危害持续；已被本次实践证伪（需自行推导 + 口径漂移）。

## 4. Recommendation

**推荐 Option A 立即实施**；**Option B（主链 parser provider）归 P26 开放待办推进**，
本提案不重复立项（避免双轨跟踪同一缺口）。

## 5. Proposed Changes（最终实施范围 —— Option A 的实质 + 2 处修正）

> 实施中根据实测调整（用户逐项确认）：**原 §5.3（改 `tasks-template.md` 的 `branch` 字段占位）前提不成立**——
> 实测该模板**没有 `branch` 字段**，且已冻结工件（`tasks/cards/*.md`、`contexts/project-context.yaml`）里
> 存的是**具体分支名**，占位符模板只存在于 ai-system 文档。据此把范围改为下述 6 项。

1. `cli/services/branch_parser.py`：**预设驱动**（`PRESETS` = `plain` / `ipd`）——
   `parse` 与 `render` 同源（模板编译正则）；`parse` 只认预设，**手写格式串 → None**；
   `render` 输出**必然可解析**（段值非法即 fail loud）；新增 `preset_for_scenario()`
   读 `config/branch-formats.yaml` 做「场景 → 预设」解析（bugfix 返回 None = 交 provider）。
2. `config/branch-formats.yaml`（新）：**场景 → 预设映射** SSOT —— `requirement: plain`（默认，
   可改成 `ipd`）、`default_preset: plain`、`bugfix:`（留空 = provider 自有格式，主链预设不适用）。
3. `cli/tests/test_branch_parser.py`：13 项 —— 两预设正例 / 手写格式串与未知形态拒绝 / 段数区分不歧义 /
   场景映射（含自定义为 ipd 与非法映射 fail loud）/ `render` 不变量 / `parse` never raise。
4. `tools/checks/workflow.py` `check_branch_parser`：门禁自检扩为**三例**（两预设 + 手写格式串必须被拒）。
5. `governance/AI_OPERATING_RULES.md` §Workspace Discipline：删「格式暂定 + 由用户指定/调整」，
   改为「AI 按场景预设组装 → 用户确认**具体名** → 冻结；格式串不可手改，特例走 provider」+ 段类说明（禁下划线）。
6. `templates/runtime/runtime-dev-setup.md` Phase 7：同步「组装 → 确认名 → 冻结」三态与校验口径。

## 6. Validation Plan

- `python3 tools/repo-lint.py` / `tools/check.py` / `tools/path-audit.py` 全绿（治理层改动）。
- 用例核对：对本次两种真实分支名
  （`cc20260921_log-volume-reduction_housekeeping-service-api`、
  `cc20260910_ipd_qa-housekeeping-optimization_housekeeping-service-api`）按新条款逐段解析通过。
- 结果记入 Implementation Record + `reports/PROPOSALS.md` 状态同步。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 改治理 + runtime + 模板（3 文件），影响面大于"单点" | 按 §12 走完整流程；改动为条款级补充，不重写章节 |
| 误伤既有冻结分支 | 明确"不回改、两种形态并存合法"；仅在 dev-setup 冻结前生效 |
| Option B 被顺手带上（范围蔓延） | 本提案**明确排除** B；如需 B 另行立项 |
| 选用判据（是否随迭代）主观 | 判据锚定"需求确认阶段由用户/TR 归属判定"，并落 Task Card `branch` 字段留痕 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-09-21 |

---

## Implementation Record (2026-09-23)

**Status → Implemented**（用户逐项确认：预设驱动 → AI 生成 + 用户确认具体名 → 场景映射可配置 → 格式串不可手改）。

**实施中修正了原提案的两条前提**：
1. §1.2.2「主链没有 branch parser」**已过期** —— `cli/services/branch_parser.py` 早已存在（P26 Option B 的
   ai-system 内联实现），缺的是「parser 不认第二种形态」。
2. §5.3「改 `tasks-template.md` 的 branch 字段占位」**前提不成立** —— 该模板无 `branch` 字段；
   实测已冻结工件里存的是**具体名**（`tasks/cards/T-001.md`、`project-context.yaml`），
   占位符只存在于 ai-system 文档 → **收紧格式自由不会破坏任何存量**。

**缺口的新形态（本次实测，比原文更硬）**：`parse("cc20260921_log-volume-reduction_housekeeping-service-api")`
原返回 **None** → 而 `aic-trace` 明写要用该 parser 取 git 线索 → **已冻结在产的非迭代分支无法被 trace 解析**。
本次一并修好（同一提交）。

**验证**：`cli/tests/test_branch_parser.py` **13 项 OK**（含两预设、手写格式串拒绝、段数区分、
场景映射与 fail loud、`render` 不变量）；门禁自检三例通过（`check.py` PASS）；真机分支名实测：
ipd 形态与 plain 形态均解析成功、`cc{date}_x_{desc}` 等格式串一律 None。
**门禁**：单测全绿 · `check.py` PASS · `repo-lint` / `path-audit` / `proposal-audit` 全绿。

**范围外（未做，仍归 P26）**：主链 `extensions` provider 覆盖（`branch.parser` 逻辑名的实际 provider）；
既有已冻结分支不回改（两形态并存合法）。