# 系统巡检报告 — 2026-08-24（on-demand / scope=workflows）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- 范围: workflows（workflows/*.md + config/workflows/*.yaml + workflow-registry + runtime 引用 + 治理一致性 workflows 相关项）
- 日期: 2026-08-24
- 增量基线: maintain-delta verdict=FIRST_RUN（metrics/maintain-delta-state.json 无记录 → 全量审计；记录基线 head=3237f8d）

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **ISSUES**（findings 1） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 1 errors, 0 warnings |
| workflow-command-audit | 0 blockers / 1 WARN（aic-maintain.md 125 行，thin-command 门禁，既有） |
| CLI 单测 | OK（test_maintain_tools + test_prompt_builder） |

补充说明：

- quick-check 的 1 条 ERROR 为 `extensions-lint: extensions root not found: /home/syske/workspace-local/extensions`——本机无 extensions 仓（机器级，按 Guardrails「CI 无 extensions 仓 → parser/mr.provider 降级 WARN」精神，仅进 per-run diagnostic-log，不入 maintenance.yaml）。
- repo-lint WARN 25 条为既有基线，本轮无新增（与 08-24/prepare 一致）。
- path-audit：665 refs / 120 placeholders / 3 known_debt / 0 BROKEN / 0 ABSOLUTE OUTSIDE。
- workflow-command-audit：15 workflows ↔ 15 commands 全对账，仅 aic-maintain.md 超 thin-command 行数门禁（既有，本命令即该文件）。
- 指标快照已写入 `metrics/maintain-2026-08-24.json`。

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期（08-24/prepare） | 本期 | 变化 |
|---|---|---|---|
| Skills | 31 | 31 | = |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 56 | 56 | = |
| Templates | 22 | 22 | = |
| Frontmatter | 30 valid / 1 missing | 30 valid / 1 missing | =（恒定：architecture/ 父分组非回归） |

---

## 二、巡检发现（AI 填写，按严重度分级）

### 高（0）
无。

### 中（0）
无。

### 低（2）

1. **AGENTS.md 缺失（doc-vs-reality 检查对象不存在）** — `aic-maintain.md:77`（本命令 Step 3）、`skills/task-splitter/SKILL.md:113`、`templates/runtime/runtime-spec.md:89` 均引用 AGENTS.md；工作区根与 ai-system 内均无此文件（全盘 find 仅命中 person-learning-note/AGENTS.md，属项目文件非结构图）。08-23 报告曾记载「AGENTS.md 主结构 + 运行目录表匹配 ✅（I4 两处信息级）」并给出删除 `ai-system_bak_260803` 行的修复建议——说明彼时文件存在，后已消失（可能随工作区清理被移除，未随 ai-system 入 git）。**建议**（L2，仅输出建议，需用户决定）：重建工作区根 AGENTS.md（含目录结构图 + 运行目录表），或将 aic-maintain Step 3 的 AGENTS.md 检查项改为「可选（不存在则跳过并记录）」。
2. **README 条件转移表缺 release BLOCKED → develop 一行（信息级文档漂移）** — `workflows/release.md` frontmatter `next: [deployment, develop]` + Next 节「develop — on BLOCKED (Branch Diff Review BLOCKER…)」；`workflows/README.md`「Conditional transitions」仅列 `release: READY → deployment`，未列 `release: BLOCKED → develop`。**建议**（L1，确认后即可就地修）：README 补一行 `release: BLOCKED → develop`。

### 信息（3）

3. **logs/ 目录缺失（gitignored 运行时态）** — `ai-system/logs/` 不存在，历史 diagnostic log 亦无残留（P35 引用的 08-18→08-24 日志已随清理消失）。本轮按 AI_OPERATING_RULES「每 run 落 logs/」创建目录并写入 `maintain-20260824-233830.md`。属预期运行时行为，非漂移。
4. **maintain-delta FIRST_RUN 基线** — metrics/maintain-delta-state.json 无记录，本轮已 `--record`（head=3237f8d），下次运行起增量判定生效。
5. **extensions 仓缺失** — 本机无 `/home/syske/workspace-local/extensions`（机器级；若为 CI 无 extensions 仓场景，按 Guardrails 应降级 WARN 而非 ERROR——工具行为观察，进 diagnostic-log 留档）。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | workflows/*.md 八节齐全且顺序正确 | ✅ | 15 个文件逐一校验：Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next 全部存在、顺序正确 |
| 2 | workflows 术语与 README 选择表一致 | ✅ | README 引用 15 个 workflow 全部存在，无悬空、无遗漏；config↔workflow 1:1（15 对） |
| 3 | Runtime 引用文件存在 | ✅ | config/workflows/*.yaml 引用的 15 个 templates/runtime/runtime-*.md 全部存在；runtime-base.md / runtime-diagnostic-log.md 亦有他处引用（非孤儿） |
| 4 | config/workflows/*.yaml 注册表保持极简 | ✅ | 15 个 yaml 仅 name/workflow/runtime 三键，无 inputs/outputs/next 回膨（防 A1 复发）；bugfix-modes.yaml 为模式辅助非 workflow，符合预期 |
| 5 | config/workflow-registry.yaml 一致性 | ✅ | 15 条目 → 15 个既有 yaml → 15 个既有 workflows/*.md；default(bootstrap) 可解析 |
| 6 | Next 链闭合 | ✅ | 全部 next 目标有效；唯一外部目标 release→deployment 在 README 明示「outside this workflow set」 |
| 7 | 依赖图无异常环 | ✅ | 3 个简单环均为文档化的条件重入（review: Changes Required→develop；verify: FAIL→develop；release: BLOCKED→develop），非架构环 |
| 8 | 引用路径存在 | ✅ | path-audit 0 broken（665 refs）；menu.yaml/intents.yaml 的 workflow 引用、workflows 内引用的 skill（memory-capture）均存在 |
| 9 | 文档-现实一致 | ⚠️ | AI_DEVELOPMENT_CONTRACT 架构树 12/13 顶层目录存在（logs/ 为 gitignored 运行时态，本轮创建，非漂移）；**AGENTS.md 缺失（见发现 1）**；OPERATIONS §1 引用可解析 |
| 10 | 状态卫生 | ✅ | workspaces/.aic-state.yaml 仅 projectless_usage(maintain×2)+last_target，无 project/change 悬空引用 |
| 11 | 提案遗留 | ✅ | proposal-audit 0 gate error / 0 warn（见第六节） |

---

## 四、修复动作与建议清单（AI 填写）

**本轮已做（运行时必需，无结构改动）：**

- 创建 `ai-system/logs/` 并写入 per-run diagnostic log（`logs/maintain-20260824-233830.md`）。
- `maintain-delta.py --record` 记录基线 head=3237f8d。
- 指标快照 `metrics/maintain-2026-08-24.json`。

**修复批次（用户确认后已实施）：**

| # | 动作 | 级别 | 状态 |
|---|---|---|---|
| 1 | README Conditional transitions 补 `release: BLOCKED → develop` | L1 | ✅ 已实施（workflows/README.md:77） |
| 2 | 重建工作区根 AGENTS.md（简写版） | L2 | ✅ 已实施（workspace 根 AGENTS.md，覆盖结构图/运行目录表/关键设计决策/单任务工时/主链 workspace-anchored） |

**建议（未实施，待确认——Change Control）：**

| # | 动作 | 级别 | 说明 |
|---|---|---|---|
| 1 | ~~README Conditional transitions 补 `release: BLOCKED → develop`~~ | L1 | 已实施（见上） |
| 2 | ~~AGENTS.md 重建 或 aic-maintain Step 3 检查项降级为可选~~ | L2 | 已实施（重建简写版） |

**输出建议（结构性，走 OPERATIONS §11 变更管理，不直接实施）：**

- 无结构性建议。workflows 域结构、注册表、引用链全部健康，无需目录调整/模块合并/契约修改。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-08-24 | ISSUES | 1 |

> 仅 1 个快照（extensions 缺失，机器级），趋势待后续累积。

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 2 开放提案 / 4 open action items
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P35-PYTHON-INTERPRETER-ROBUSTNESS.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 B：规则 slug 派生（Change Request 前置收集 + 完整 id 建议）——触发条件未到
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到

**遗留处置（AI 评估）：**

- **P28（Proposed）**：A 已落地；B/D 触发条件未到 → **defer**（与 08-24/prepare 一致，Evolution Principle 不预引入）。
- **P26（Implemented）**：2 条 open action（分支扩展 provider / CI 分支保护）均为后续增强 → **defer**（与上轮一致）。
- **P35（Proposed）**：python 解释器鲁棒性（python→python3 文档统一 + 工具鲁棒化），触及多文件、需用户批准 → **待用户决策（approve/implement/reject/defer）**，本轮仅报告不实施（Change Control）。
- 无新增遗留、无「未登记 README 索引」类门禁问题（08-24/prepare 已补登记）。
