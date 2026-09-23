# Change Proposal: P64 — spec 前置条件口径不一致（"Prepare completed" 无 SSOT、实际 0/12 变更具备 prepare 产物）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (workflow 前置契约 + runtime Pre-flight + 变更元数据约定) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | 用户指示立案 2026-09-21；来源 I-10（`workspaces/202609-housekeeping-log-volume-reduction/openspec/changes/log-volume-reduction/issues.md`）+ T-011 review 运行（`logs/review-20260921-184156.md`） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 同一前置条件有两处表述，且都不是可执行清单

| 层 | 文本 | 实际要求 |
|---|---|---|
| Workflow | `workflows/spec.md:27` Preconditions：`Prepare completed for this change (Preparation Report available)` | **Preparation Report** 可用 |
| Runtime | `templates/runtime/runtime-spec.md:82-91` Pre-flight：校验 `workspaces/<project_id>/openspec/changes/<change-id>/proposal.md`**（或该变更的 Preparation Report）**存在且非空 | **proposal.md**（Preparation Report 仅作"或"的备选） |

两处指向**不同产物**，且 runtime 的"或"写法使验收标准不可判定。

### 1.2 实测：prepare 声明的产物**从未落地**（0/12）

- `workflows/prepare.md` Outputs 明列**必需产物**：Requirement Summary、Architecture Summary、Impact Report、**Preparation Report**，
  路径 `workspaces/<project-id>/openspec/changes/<change-id>/prepare/preparation-report.md`。
- 实测（2026-09-21，全工作区）：**12+ 个 change 全部没有 `prepare/` 目录**；非 archive 变更**均有 `proposal.md`**。
- 本次变更 `log-volume-reduction` 的工作区内，"Preparation Report" 字样**仅出现在 `issues.md` 的 I-10 登记本身**——
  即 prepare 产物既未在规范路径、也未在任何其它位置产生。
- `templates/runtime/runtime-spec.md` Inputs 却把 **Preparation Report / Architecture Summary / Impact Analysis** 列为
  "Provided by Prepare Runtime" —— **声明消费的输入在实际中不存在**。

### 1.3 后果

1. **Workflow 层前置不可满足**：按字面执行，spec 永远无法开始（0/12 变更都不合格）。
2. **Runtime 层静默放行**：改用 `proposal.md`（存在）替代 → 未 prepare 的变更照常进入 spec；
   T-011 review 运行把该现象记为 **L1 偏差**（"按操作性标准放行"），并登记为 I-10。
3. **语义循环**：`proposal.md` 由 `propose` 触发器在 **spec 阶段**创建（`config/menu.yaml`：`propose` = "变更集创建（spec 环节 CLI 触发器）"），
   并**不是** prepare 的产物 → 用"spec 阶段的产物"作为"spec 的前置"，逻辑上循环。
   （附注：`workflows/proposal.md` 的 Outputs 是 `solution.md`，与变更目录下的 `proposal.md` **不是同一物**，命名易混。）

### 1.4 归属（Repository First）

- **P32**（`prepare` 产物**位置**对齐，已 Implemented）：管"产物该放哪"；本提案管"**前置怎么验收**"→ 互补，不重复。
- **P62**（标准↔实践↔门禁三方不一致）、**P60**（门禁失效必须响亮）：同族病症（声明与执行脱节且不报警）→ 交叉引用，不合并。

## 2. Root-Cause

1. **缺 SSOT**：全仓"Prepare completed"仅出现一次（`workflows/spec.md:27`），既无清单也无判定方法。
2. **产物契约与实践脱节**：prepare 声明 4 项必需产物，实际 0 落地 → 契约成为死条文（与 P62 §1.3 同型）。
3. **静默替代掩盖缺口**：runtime 用另一个（且属于后置阶段的）产物替代 → 前置检查在形式上"通过"，
   使"没有 prepare"这一事实**不产生任何信号**。

## 3. Options

### 3.1 Option A — 就低（把 workflow 文本改为 `proposal.md` 存在）

最省事，但等于把"未 prepare 也放行"固化为规范，并让 prepare 的 Outputs 与 spec 的 Inputs 双双成为永久死条文
（即再制造一个 P62）。**不建议**。

### 3.2 Option B — 就高（严格强制 prepare 4 项产物）

按 prepare Outputs 硬性要求。**代价**：现存 0/12 变更即刻全部被拦，无过渡路径 → 要么补造产物、要么长期红。**风险过高**。

### 3.3 Option C — SSOT + 显式 skip + 祖父条款（推荐）

1. **SSOT**：在 `workflows/prepare.md` 定义唯一 **Completion Criteria** 块（可执行清单：4 项必需产物 + 规范路径 + 非空要求）。
2. `workflows/spec.md` 的 Precondition 改为**引用**该块（不重述条款）。
3. `templates/runtime/runtime-spec.md` Pre-flight **按同一清单实现**：
   - 清单齐备 → 放行；
   - 缺项 → **Stop**（并给出缺失项与规范路径）；
   - **唯一例外**：变更元数据显式声明 `Prepare: skipped (<理由>)` → 放行且理由留痕可审计。
4. **祖父条款**：规则生效日之前创建的变更降级为 **WARN**（不阻断），之后严格；存量可在下次触碰时补声明。

### 3.4 附带决议点 D — prepare 产物契约本身是否维持

"3 项摘要"（Requirement/Architecture/Impact）是否真为必需？建议**维持并要求**（它们是 spec 的声明输入），
但允许把"摘要"降为 on-demand、仅 **Preparation Report 必需**（交用户裁决）。
无论选哪种，都必须**同时改** `workflows/prepare.md`（契约侧）与 spec 侧（验收侧）——只改一侧就会再产生本提案所治的分歧。

## 4. Recommendation

**采纳 Option C**，并按 D 做一次二选一裁决（推荐"仅 Preparation Report 必需 + 摘要 on-demand"，以匹配实际使用强度）。

理由：C 把"前置"变成**单一定义、双处实现一致、可判定、可审计、且不误拦存量**；
显式 skip 保留了"确实无需 prepare"的合法路径（不靠静默替代）；祖父条款避免生效即红。
与 P60「门禁失效必须响亮」一致：**缺产物必须 Stop，而不是悄悄换一个产物放行**。

## 5. Proposed Changes

1. `workflows/prepare.md`：新增 `## Completion Criteria (consumed by spec)`——必需产物清单 + 规范路径 + 非空 +
   `Prepare: skipped (<理由>)` 的声明写法与适用条件。
2. `workflows/spec.md`：Preconditions 的第 27 行改为**指向**该块的引用（删除无判定的括号表述）。
3. `templates/runtime/runtime-spec.md` Pre-flight：
   - 按 Completion Criteria 逐项校验；**删除** `proposal.md … (or … Preparation Report)` 的替代语义；
   - 保留 P32 的"产物错位 → Stop + 纠正到主链约定"行为；
   - 新增 skip 分支（读变更元数据声明，校验格式与理由非空）。
4. **变更元数据约定**：`openspec/changes/<change-id>/proposal.md` 元数据块增 `- **Prepare**: skipped (<理由>)`
   （沿用其既有 `- **<字段>**: <值>` 风格）；`runtime-prepare.md`/`runtime-spec.md` 只引用该字段名，不复制说明。
5. `templates/runtime/runtime-prepare.md`：产物位置段与 Completion Criteria 交叉引用（不复制条款）。
6. 交叉引用：P32（位置，Implemented）/ P62（三方不一致）/ P60（fail loud）——均不合并。
7. 索引登记：`reports/PROPOSALS.md` + `reports/README.md`。

## 6. Validation Plan

**三例只读 dry-run 实证**（在既有 change 上，不改业务代码）：

| # | 场景 | 期望 |
|---|---|---|
| a | Completion Criteria 齐备 | 放行 |
| b | 缺 Preparation Report 且**无** skip 声明 | **Stop**（当前行为=放行 → 缺陷复现，作为反例基线） |
| c | 缺产物但声明 `Prepare: skipped (<理由>)` | 放行，且理由留痕可审计 |

- **存量核对**：对现存 12 个变更跑一遍判定，确认祖父条款（或补声明）后**不产生常红**。
- **门禁**：`check.py` / `repo-lint` / `path-audit` / `proposal-audit` 全绿；`workflow-command-audit` 无新增。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 生效即拦停存量 12 变更 | 祖父条款（生效日前降级 WARN）+ 允许补 `Prepare: skipped` 声明 |
| `skip` 被当作逃生门滥用 | 理由必填并留痕；可由 `proposal-audit`/维护巡检列出全部 skip 声明供复核 |
| 与 P32 重叠 | 互补：P32 管**位置**，本提案管**前置验收**；交叉引用不合并 |
| 只改 spec 侧导致分歧再现 | §3.4 已明确：契约侧（prepare.md）与验收侧必须同时改 |
| 与 P62 同因（契约死条文）但分头处理 | 二者同族：P62 治"提交可追溯"，本提案治"spec 前置"；均由同一根因（声明无机器判据）驱动，可在季度回顾中合并评估根因治理 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（按修正后方案实施） | 2026-09-23 |
| AI Maintainer | **Implemented** | 2026-09-23 |

---

## Implementation Record (2026-09-23)

**Status → Implemented**（用户确认按修正后方案实施）。改动四处 + 两个回归测试文件：

| # | 文件 | 改动 |
|---|---|---|
| 1 | `workflows/prepare.md` | `## Exit Criteria` 内新增 **`### Completion Criteria (consumed by spec)`** 作为唯一定义（4 条：规范路径+非空 / 显式 skip+理由 / 遗留命名 / 祖父条款）；`## Outputs` 按决议点 D 收敛为**仅 Preparation Report 必需**，3 项摘要转 on-demand。体量 94 行（RFC-0003 门禁上限 100） |
| 2 | `workflows/spec.md` | Preconditions 改为**引用**该块（删除 `(Preparation Report available)` 的重述） |
| 3 | `templates/runtime/runtime-spec.md` | Pre-flight 按同一清单实现：删掉 `proposal.md`（或 …）这一**恒真**替代；缺项 → Stop 并报缺失项+规范路径；新增 skip / 遗留 / 祖父分支；Runtime Context 的 3 项摘要标注 `(when produced — on-demand)` |
| 4 | `templates/runtime/runtime-prepare.md` | `## Outputs` 改为引用判定规则 + **禁止把报告写进 OpenSpec 的 `proposal.md`**（堵住产物碰撞的产生端） |

**相对提案的修正（L1，均已在实施前向你说明并获确认）**：

1. **Completion Criteria 放在 `## Exit Criteria` 内（`###` 子块），不是新增顶层 `##` 小节** ——
   `workflows/README.md:125` 的工作流小节契约只允许 8 个必需节 + 1 个可选节（When to Use）；
   新增顶层节会改契约，而 Exit Criteria 语义上正是"何时算完成"。
2. **新增"遗留命名"判定（提案未含）** —— 实测 4/12 变更的 prepare 产物已落地，只是被写成
   `proposal.md`（H1 = `Preparation Report` / `准备报告`）。若无此条，生效即拦停 4 个存量变更。
3. **祖父条款的判据可操作化** —— "生效日前创建"改为可机器观测的
   「`proposal.md` mtime < 2026-09-23」。
4. **清单名对偶保留** —— `checks/workflow.py:check_outputs_consistency` 要求 workflow `## Outputs`
   的每条 bullet 逐字出现在 runtime `# Outputs`；因此产物**名**两侧镜像（由门禁强制的声明↔生产一致性），
   而**判定规则**仍单一来源。提案 §5.5「不复制条款」按"不复制判定规则"落地。

**验证（运行实证，非只读）**：判定表实现后对**全部 12 个真实变更**跑一遍 →
`WARN(legacy) 4 · WARN(grandfather) 7 · STOP 0`（**存量零常红**，祖父/遗留条款按设计生效）；
构造场景 6 例全部符合预期，其中决定性反例「缺产物且无 skip 声明 → **STOP**」在旧口径下**会放行**
（`proposal.md` 恒存在）；回归测试 `cli/tests/test_p64_prepare_criteria.py`（8 项，含 SSOT 形状断言 +
判定表）。门禁：`check.py` PASS · 单测全绿 · `path-audit` 0 broken · `workflow-command-audit` 0/0。

**未处置（转登记）**：4 个遗留命名的变更需要**迁移**报告到规范路径（WARN 已标记）——属业务工作区数据整理，
不在本仓改动范围；下一次触碰这些变更时按 WARN 提示迁移或补 `Prepare: skipped` 声明。
