# Change Proposal: P62 — 任务提交信息 `T-<id>` 强制性与实践脱节（Standard ↔ Practice ↔ Gate 三方不一致）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (standard + tool check + runtime 引用) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | 本次运行（2026-09-21）review 阶段 F-1 / F-7；`governance/standards/common/commit-content.md`；`tools/format-check.py` |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 标准、实践、门禁三方不一致（本次实证）

| 方 | 表现 |
|---|---|
| **标准** | `commit-content.md`（自称 Single authoritative source）规定 `<type>(<scope>): T-<id> <subject>`，且 `T-<id>` 标注 **"required when the change belongs to a task card"** |
| **实践** | 同服务在途主链变更 `cc20260910_ipd_qa-housekeeping-optimization_housekeeping-service-api` 的 **18/18 提交全部省略 `T-`**（`git log master..origin/…`），其中 `7c149ec` 连 `type(scope)` 前缀都没有 |
| **门禁** | `format-check.py --check-commit` 的实现规则为："subject **含** `T-` → 必须 `<type>(<scope>): T-\d{3}`；**不含** `T-` → PASS（视为非任务提交）" → **只能拦"格式错"，不能拦"缺失"** |

本次 T-011 提交 `a9b7afe` 同样省略 `T-`（`fix(housekeeping-service): 删除慢操作判据改用独立毫秒配置`），
且该行为**有据可依**：既有任务卡 `1.1.md` 明确记载惯例 *"subject 无 T-，task 引用入 body"* —— 即
**任务卡层级把"省略 T-"当成了既定惯例**，与标准直接冲突。review 判为 **Major（F-1）**。

### 1.2 危害

1. **可追溯性退化**：commit ↔ task 的机器可读关联丢失（仅靠 body 自然语言 `Refs: …`，不可机械校验）。
2. **治理空洞**：标准自称权威却被 0/18 实践违反且工具不报错 —— 这正是 ai-system 反复强调要消除的
   "声明与执行不一致"（对比 P60 门禁自校验、P45 运行时语言门禁的同类治理）。
3. **每个任务提交都会重复该问题**：未裁决前，主链每一次提交都在制造"合规但违反标准"的中间态。

### 1.3 根因

标准条款面向"人写提交信息"的意图，但**未定义机器可判定的"本提交是否属于任务卡"**；
工具因此只能用"是否含 `T-`"做单向校验，导致**缺失场景无检查**。

## 2. Goal

使 `commit-content.md` 的 `T-<id>` 要求**机器可判定、可执行、且与实际实践一致**，
消除标准↔实践↔门禁三方分歧。

## 3. Options

### 3.1 Option A — 强制（扩门禁 + 保留标准）

- 扩展 `format-check.py --check-commit`：当判定"本提交属于任务"时，**缺失 `T-` 也 FAIL**。
- 判定依据（需机器可得）：**分支名**匹配任务分支规则（`cc{date}_[ipd_]{desc}_{service}`、`task/*`、`bugfix/*`），
  或提交 body 含 `T-\d{3}` 引用。
- 代价：历史分支上已有 18 条不合规提交 → 需明确**存量豁免**（如仅校验"最后一次提交"的现状语义，天然只影响新提交）。

### 3.2 Option B — 放宽（改标准）

- 承认实践，把 `T-<id>` 从"required"改为"optional，推荐 body 引用"。
- 代价：放弃机器可追溯；与 P46（验证标记检查）、P50（双确认）等的"可校验化"方向相反。

### 3.3 Option C — 条件强制 + 分支可判定（混合，推荐）

- 标准改为：**任务分支上的非 merge 提交，subject MUST 携带 `T-<id>`**；非任务提交（治理/chore）可省略。
- 门禁以**分支名**为判据（主链任务分支命名已被 P58/dev-setup 冻结规则覆盖），实现确定、无歧义。
- 与 `AI_OPERATING_RULES §Workspace Discipline`「一任务一分支」天然一致。
- 明确存量豁免：历史提交不回改、不判负。

## 4. Recommendation

**推荐 Option C** —— 以分支名（已被治理冻结）作为机器判据，既恢复可追溯性，又与既有实践的最低改动
（只需在新提交上生效）兼容；避免 B 造成的治理回退，也避免 A 在"如何判定属于任务"上的歧义。

配套：`runtime-develop` 的提交纪律文字同步（当前隐含"subject 无 T-"惯例的来源是任务卡注释而非标准）。

## 5. Proposed Changes

1. `governance/standards/common/commit-content.md`：明确"任务分支非 merge 提交 MUST 带 `T-<id>`"，
   补充判据说明与存量豁免条款；删除/纠正与任务卡惯例冲突的表述来源。
2. `tools/format-check.py`：`--check-commit` 增加"任务分支 + 缺 `T-`" → FAIL（含分支名判据与豁免规则）。
3. `tools/checks/`（如适用）：登记新检查项及其正反例（对齐 P60 门禁自校验要求）。
4. `templates/runtime/runtime-develop.md`：提交纪律段落引用本提案结论（不复制条款）。
5. 任务卡模板/既有卡注释中的 *"subject 无 T-，task 引用入 body"* 惯例表述 → 改为引用标准。

## 6. Validation Plan

- `python3 tools/format-check.py <src> --changed --check-commit` 正例（带 T-）/反例（任务分支缺 T-）。
- `tools/check.py`（含门禁自校验项 P60）与 `repo-lint.py` 全绿。
- 在既有任务分支上试跑，确认**存量提交不被判负**（豁免生效）。
- 结果记入本提案 Implementation Record + `reports/PROPOSALS.md` 状态同步。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 存量 18+ 提交不合规被"追溯判负" | 采用"仅校验最后一次提交"的现语义 + 显式存量豁免，不回改历史 |
| 分支名判据被绕过（在任务分支上发治理提交） | 允许 `chore/docs/style: …` 类型在任务分支上豁免 T-；仅 `feat/fix/refactor/perf/test` 强制 |
| 与 P46（验证标记检查）重叠 | 二者互补：P62 管**提交信息**，P46 管**卡/报告验证标记**；交叉引用即可，不合并 |
| 标准改动影响其他仓/其他服务 | 本规则为 ai-system 治理层，作用于主链提交纪律；先在 housekeeping 变更上试跑一轮 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（按修正后方案实施） | 2026-09-23 |
| AI Maintainer | **Implemented** | 2026-09-23 |

---

## Implementation Record (2026-09-23)

**Status → Implemented**（用户确认按修正后方案实施）。改动三处 + 一个回归测试文件：

| # | 文件 | 改动 |
|---|---|---|
| 1 | `governance/standards/common/commit-content.md` | 新增 `### Id level — Task Card id ≠ plan position`（**修正 §1.3 未涵盖的根因**：卡按计划位置编号时 `T-1.1` 必然 FAIL `T-\d{3}`，AI 因此学会整个省掉 `T-`，即**门禁逼出的规避**）；新增 `## Task-branch rule (enforced)`（分支名判据 + `feat|fix|refactor|perf|test` 强制 + `chore|docs|style|ci|revert`/merge 豁免 + 祖父条款）；Machine check 段补"任务分支缺 `T-` 也 FAIL" |
| 2 | `tools/format-check.py` | 新增 `TASK_BRANCH_RE` / `COMMIT_TASK_ENFORCED_TYPES` / `COMMIT_TYPE_RE` + `_current_branch()` / `_missing_task_id()`；`--check-commit` 在既有"格式错"之外补"任务分支缺 id"分支（两者均 FAIL，信息含分支名与标准出处） |
| 3 | `templates/prompts/tasks-template.md` | H1 下补 HTML 注释：`{编号}` = **3 位数字**、文件路径 `tasks/cards/T-{编号}.md`、历史按计划位置编号的旧卡不改名（祖父条款，引用入 body） |

**相对提案的修正（L1，均已在实施前向你说明并获确认）**：

- 提案把根因写成"未定义机器可判定的'是否属任务'"，**实测根因有两层**：① 习惯漂移
  （`log-volume-reduction` 的卡已是 `T-001…T-011`、**本已合规却仍 18/18 省略**）；
  ② **结构性冲突**（`qa-housekeeping` 的卡是 `1.1…1.11`，`T-1.1` 与 `T-\d{3}` 不可兼得——
  日志实证「初次误写 `T-1.1` 已 amend 修正」）。只加分支判据会**原地复发**，故必须先拆 id 层级
  （任务级 id 进 subject，计划位置进 body），并在模板侧固定 `T-\d{3}` 编号。
- `templates/runtime/runtime-develop.md` **未改**：其提交纪律段已 `→ commit-content.md` 指针
  （SSOT），提案 §5.4 的诉求由"标准即单一来源"满足；不再复制一套条款。

**验证（运行实证）**：`cli/tests/test_p62_commit_traceability.py`（12 项）= 纯函数层（强制类型/豁免类型/
merge/非任务分支/分支形态判据）+ **真临时 git 仓端到端**跑门禁本体：事故场景（任务分支 + `fix` 缺 `T-`）→
**exit 2**；合规 `T-011` → PASS；任务分支 `chore` → 豁免 PASS；`master` 无 `T-` → PASS（治理仓不受影响）；
`T-1.1` → 仍判**格式错**（既有规则保留，且正是结构性冲突的留证）；`bugfix/*` 同样受约束；merge → 豁免。
门禁：`check.py` PASS · 单测全绿 · `repo-lint` / `path-audit` / `proposal-audit` 全绿。

**未处置（转登记）**：业务侧既有任务分支的历史提交（含 18/18 省略者）**不回改、不追溯判负**（祖父条款）；
受影响仓库下次任务提交起自动受检。
