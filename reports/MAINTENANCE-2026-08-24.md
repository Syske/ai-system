# 系统巡检报告 — 2026-08-24（on-demand / scope=prepare）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- 范围: prepare（prepare 工作流 + 其 runtime/skill/governance/outputs 一致性）
- 日期: 2026-08-24
- 增量基线: maintain-delta verdict=CHANGED（自 2026-08-23 起 4 提交 / 13 文件，涉及 cli, reports, templates, tools → 跑对应子集）

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期(08-23) | 本期(08-24) | 变化 | 说明 |
|---|---|---|---|---|
| Skills | 31 | 31 | = | 无增减 |
| Workflows | 15 | 15 | = | 无增减 |
| RFC | 14 | 14 | = | 无增减 |
| Governance | 61 | 56 | -5 | P31 standards/cool 迁出至 extensions（company_standards_root 配置化） |
| Templates | 23 | 22 | -1 | 模板层随 P30/P31 调整 |
| Frontmatter | 30 valid / 1 missing | 30 valid / 1 missing | = | 恒定：`skills/architecture/` 父分组无 SKILL.md（7 个子 skill 各自有 SKILL.md），属既有结构非回归 |
| lint WARN | 25 | 25 | = | 既有，无新增 |

---

## 二、巡检发现（按严重度分级）

### 低（Low）——已闭环

1. **prepare.md Outputs 位置文本不一致（P32，已实施闭环）** — `workflows/prepare.md:68` body 原写 `sub-reports → outputs/prepare/{yyMMdd}-{desc}/`，与同文件 frontmatter `outputs.base: "workspaces/<change-id>/"` 矛盾，亦与 AGENTS.md「主链 workspace-anchored、不入 outputs/<workflow>/」冲突。**本轮已按 P32 方案 A 实施修复**：该行改为 `sub-reports → workspaces/<change-id>/reports/`；repo-lint/path-audit/quick-check/proposal-audit 复验全绿；P32 状态置 Implemented。

### 信息（Info）

2. **frontmatter「1 missing」为既有结构** — `skills/architecture/` 是 7 个子 skill 的父分组目录，无根级 SKILL.md；repo-metrics 将其计为 1 missing，08-23 与 08-24 均为 30 valid/1 missing，非回归。
3. **P28 Change ID 生成增强待触发** — 选项 A（`{YYYYMM}-` 规则默认）已落地；B（规则 slug 派生）/ D（AI 可选生成 skill）触发条件未到，维持现状。
4. **lint 25 WARN 恒定** — 既有告警，本次无新增、无 BLOCKER/ERROR。
5. **指标回落（governance -5 / templates -1）** — 对应 P31 standards/cool 迁出 + P30 根路径占位符渲染期解析，属计划内迁移，非异常缩减。

### 高 / 中

无。

---

## 三、一致性抽查结论（scope=prepare，逐项）

| 项 | 结论 | 证据 |
|---|---|---|
| prepare.md 八节齐全且有序（Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next） | ✅ 通过 | 逐节核对，顺序正确 |
| 术语与 workflows/README.md 选择表一致 | ✅ 通过 | README.md:18「Prepare context for a new change \| prepare.md」 |
| Runtime 引用文件存在（runtime-prepare.md） | ✅ 通过 | templates/runtime/runtime-prepare.md 存在 |
| 链闭合（bootstrap → prepare → spec） | ✅ 通过 | bootstrap.md `next: [prepare]`；spec.md 有 Preconditions 段 |
| config/workflows/prepare.yaml 注册表最小化（仅 name/workflow/runtime） | ✅ 通过 | 三字段，无 inputs/outputs/next 回填（防 A1 复发） |
| 引用路径存在（prepare 相关 runtime/skill 路径） | ✅ 通过 | path-audit: OK no broken path dependencies |
| Outputs 位置：body 与 frontmatter 一致 | ✅ 通过 | prepare.md:68 已对齐 `workspaces/<change-id>/reports/`（P32 方案 A 本轮实施） |
| 工作区状态引用仍存在 | ✅ 通过 | workspaces/.aic-state.yaml 引用有效 |

**小结**：8 项全部通过（P32 本轮实施后 Outputs 一致性转通过）。

---

## 四、修复动作与建议清单

### 本次执行的修复动作

1. **【P32 方案 A，已实施】** — `workflows/prepare.md:68`：`sub-reports → outputs/prepare/{yyMMdd}-{desc}/` → `workspaces/<change-id>/reports/`（与 frontmatter `outputs.base` 及 AGENTS.md 主链约定对齐）。
   - 复验（gate，fresh）：`grep -rn "outputs/prepare" workflows/` → 0 命中（EXIT=1）；`repo-lint.py` BLOCKER/ERROR 0 / WARN 25（无新增）；`path-audit.py` 0 broken（664 refs）；`quick-check.py` OK(0)；`proposal-audit.py` 0 gate error / 0 gate warn（此前 1 WARN 因维护报告未登记 README 索引，已补登记后清零）。
   - P32 状态 Proposed → Implemented；PROPOSALS.md 索引已刷新（26 proposals）；reports/README.md 维护报告表已补登记 08-24 行。
   - 不动 AGENTS.md / RFC-0003 / 无 ADR（已按 P32 判定）。

### 建议（后续）

1. **P32/P33 均已闭环**，无后续动作。

2. **行为回归待验证**（P33 生效后）：下一次日常运行发现 doc drift 时应走就地小修旁路（diagnostic-log + 报告），不再立 P 提案；发现结构级缺口时应 JIT 加载 proposal-policy 后按 §1 立案并登记索引。

3. **P28 开放项维持 defer** — B/D 触发条件未到，按 Evolution Principle 不预引入；保持现状，无需动作。

3. **P26 开放项维持 defer** — 分支扩展 provider / CI 分支保护均为后续增强，触发后再评估。

### 结构性变更

- 无。本报告不涉及架构/目录/契约调整（Guardrails：结构性变更仅出建议、走 OPERATIONS §11 变更管理流）。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-08-13 | OK | 0 |
| 2026-08-14 | OK | 0 |
| 2026-08-17 | OK | 0 |
| 2026-08-18 | OK | 0 |
| 2026-08-20 | OK | 0 |
| 2026-08-23 | OK | 0 |
| 2026-08-24 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 2 开放提案 / 4 open action items
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P32-PREPARE-OUTPUTS-LOCATION.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到
