# 系统巡检报告 — 2026-08-31（weekly）

- 类型: 系统巡检（MAINTENANCE）
- 模式: weekly
- 日期: 2026-08-31

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |
| maintain-delta | **NO_CHANGES** — 2026-08-25 后无提交变更，跳过全量审计，仅 quick-check + 状态卫生 |

### 指标对比（2026-08-25 → 2026-08-31）

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 31 | 31 | = |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 57 | 57 | = |
| Templates | 22 | 22 | = |

**说明**：指标全部持平，与 maintain-delta NO_CHANGES 一致。lint 25 WARNINGS 来自 frontmatter 校验（非结构性问题），quick-check 近 7 日趋势稳定 OK。

---

## 二、巡检发现（按严重度分级）

### 高（BLOCKER/ERROR）

- **0 项** — 无 BLOCKER 或 ERROR。

### 中（WARN）

1. **code-review.md 工作流节顺序违规**（workflows/code-review.md:51-84）
   - `## Target Branch Resolution`（Inputs 与 Context 之间）和 `## Spec-Comparison Review Mode`（Outputs 与 Exit Criteria 之间）两个可选节插入了必选节之间。
   - 违反 README.md §Workflow Template："Optional sections (inserted after Purpose when needed, **do not reorder required sections**)"。
   - 建议：将 Target Branch Resolution 移至 Purpose 之后、Runtime 之前；将 Spec-Comparison Review Mode 移至 Purpose 之后（或作为 Runtime 补充）。属于结构性调整，需走 OPERATIONS §11 变更流程。

2. **reports/ 未注册索引**（proposal-audit 2 warnings）
   - `MAINTENANCE-2026-08-25.md` 和 `MAINTENANCE-2026-08-26.md` 未在 `reports/README.md` 索引中登记。
   - 建议：将两条记录加入 reports/README.md 索引表。

### 低

3. **开放提案积压**（7 项 Proposed 状态）
   - P28（Change ID 自动生成）、P35（python 解释器鲁棒性）、P36（init 脚本完善）、P37（必填参数必要性）、P41-P43（tr5 脚本批次）。
   - 建议：P28/P35/P36/P37 为技术改进类，可安排季度回顾时集中决策；P41-P43 为 tr5 增强，取决于 tr5 工作流推进优先级。

4. **maintenance.yaml next_maintenance 已过期**
   - `next_maintenance: 2026-08-30`，今日 2026-08-31，逾期 1 天。本次巡检正常覆盖，后续应按时执行。

### 信息

5. **ai-system 目录无变更** — 自 2026-08-25 增量基线记录后无新提交，属于维护间隔期内的正常状态。
6. **scope 指向 proposal 输出** — `outputs/proposal/260831-cool-italent-sync-plus-dev-setup-worktree/solution.md` 为 dev-setup worktree 隔离提案，已决策（D1-D6 用户拍板），待运维执行，不属于 ai-system 系统变更。

---

## 三、一致性抽查结论（逐项）

| 检查项 | 结果 |
|---|---|
| workflows/*.md 八节完整 + 顺序 | ⚠️ code-review.md 两个可选节插入必选节之间（见发现 #2）；其余 14 个工作流均通过 |
| workflows/README.md 术语表 vs 实际 | ✅ 通过 |
| config/workflows/*.yaml 最小化（name/workflow/runtime） | ✅ 通过，无 re-bloating |
| Referenced paths（standards/, loaders/, templates/prompts/, cli/commands/）| ✅ 全部存在 |
| Runtime 引用路径（config/workflows/*.yaml → templates/runtime/）| ✅ 全部存在 |
| Link health（projects/ symlink）| ✅ 存在且可访问 |
| AGENTS.md 目录结构图 vs 实际目录布局 | ✅ 一致（9 个顶级目录均存在）|
| AI_DEVELOPMENT_CONTRACT 架构图 vs 实际 | ✅ 通过 |
| .aic-state.yaml 项目引用存在性 | ✅ 4 个活跃项目均存在 |
| state hygiene（bootstrap.status）| ✅ done |

---

## 四、修复动作与建议清单

| # | 类型 | 项目 | 建议动作 |
|---|---|---|---|
| 1 | 建议（结构性，需审批）| code-review.md 节顺序 | 将两个可选节移至 Purpose 之后，走 OPERATIONS §11 变更流程 |
| 2 | 小修复（可确认后修复）| reports/README.md 索引 | 将 MAINTENANCE-2026-08-25.md、MAINTENANCE-2026-08-26.md 加入索引表 |
| 3 | 信息 | 开放提案 | 7 项 Proposed 状态，季度回顾时集中决策 |
| 4 | 信息 | maintenance.yaml | 更新 next_maintenance 至 2026-09-07（weekly +7d） |
| 5 | 已修复（doc-drift）| runtime-spec Phase 6 skill 引用 | 修正 `planning`/`task-planning` → 实际 `task-splitter` skill；同步 task-splitter SKILL.md 触发条件为 AI 决策触发（无需单独流程） |
| 6 | 已修复（doc-drift）| runtime skill 入口引用 | runtime-spec/runtime-develop 中 skill 入口由 `workflow.md` 统一修正为 `SKILL.md`（符合 DIRECTORY-RESPONSIBILITY 入口约定） |

---

## 五、quick-check 趋势（近 10 日）

| 日期 | verdict | findings |
|---|---|---|
| 2026-08-13 | OK | 0 |
| 2026-08-14 | OK | 0 |
| 2026-08-17 | OK | 0 |
| 2026-08-18 | OK | 0 |
| 2026-08-20 | OK | 0 |
| 2026-08-23 | OK | 0 |
| 2026-08-24 | OK | 0 |
| 2026-08-25 | ISSUES | 1 |
| 2026-08-26 | OK | 0 |
| 2026-08-31 | OK | 0 |

趋势：8/25 ISSUES（yapi-openapi 缺 OPTIMIZATION_LOG，已修复后回落），其余 9 天全部 OK。

---

## 六、提案状态

- proposal-audit: 0 gate error / 2 warn / 7 开放提案 / 4 open action items
  - WARN MAINTENANCE-2026-08-25.md: not registered in reports/README.md index (proposal-policy §6)
  - WARN MAINTENANCE-2026-08-26.md: not registered in reports/README.md index (proposal-policy §6)
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P35-PYTHON-INTERPRETER-ROBUSTNESS.md
  - 开放: P36-SETUP-ENV-INIT-SCAFFOLD.md
  - 开放: P37-REQUIRED-INPUTS-TRIAGE.md
  - 开放: P41-TR5-SECTION1-SEMANTICS.md
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P43-TR5-SECTION0-INLINE-BODIES.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到
