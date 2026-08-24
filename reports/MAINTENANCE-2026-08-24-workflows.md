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

---

## 七、巡检发现问题的后续处置（2026-08-25 追加）

### 新增提案

- **P36（Proposed）** — 初始化脚本完善（`tools/setup.py --env-init` 补齐目录骨架 + 引导指定外部代码仓库）。
  来源：用户反馈（未创建必要文件夹 / 未引导指定代码仓库 / 未生成 workspaces、repositories 等目录）。
  记录仅，不实施（待用户决策）。已登记 PROPOSALS.md + reports/README.md。

### 已实施修复（用户确认）

| # | 修复 | 验证 |
|---|---|---|
| A | **Path Anchor 英文化**（LANGUAGE_CONVENTION：AI 内部层英文）——templates/prompts/command.md + workflow.md 的 Path Anchor 段中文 → 英文；渲染验证：`All relative references ... resolve against these two absolute roots` | 生成 maintain/command 提示词确认英文；无旧中文残留 |
| B' | **提示词不注入悬空 extensions 路径**（用户澄清诉求：不是 lint 不报错，而是提示词内容不含缺失路径）——`_resolve_ref` 对不存在目标返回 None；`_append_main_chain_caps` 跳过不可解析条目；全部不可解析则整段不输出。实测 prepare/spec/develop 中 `extensions/confluence-markdown-publisher` 被跳过、`skills/wayfinder` 保留绝对路径 | +4 测试（dangling skipped / existing resolved / resolve_ref None / absolute），152 全 PASS |

> 说明：B（extensions-lint 缺失根降级 WARN）与 C（extensions-lint 配置化）曾按初判实施，后经用户澄清真实诉求为提示词层面，已**回退** tools/extensions-lint.py 至原状（缺失根仍报 ERROR）；Guardrails「CI 无 extensions 仓 → 降级 WARN」由既有 `bugfix_modes.py::_extensions_available()` 承担，非 extensions-lint。

### Gate（fresh）

- repo-lint 0/0/25（无新增）；path-audit 0 broken；workflow-command-audit 0 blocker/1 WARN
- `python -m unittest discover -s cli/tests`：**152 OK**（+4 新增）
- check.py PASS：5 WARN（P28/P35/P36 开放提案 + extensions 缺失 hotfix 降级，均既有/预期）

### 提示词优化批次（2026-08-25，用户确认实施）

针对生成的 prepare 提示词评审，实施 5 项优化：

| # | 优化 | 改动 | 验证 |
|---|---|---|---|
| 1 | **能力段移到 `# Task` 前** | `_append_main_chain_caps` → `_capabilities_section`（返回段而非 append 末尾）；模板加 `{{external_capabilities}}` 锚点（Task 前） | caps 位于 Task 前（断言通过） |
| 2 | **剥离 workflow/command frontmatter** | 新增 `_strip_frontmatter()`，`_build_workflow`/`_build_command` 双路径应用（机器契约不整段嵌入，八节正文保留） | `name: prepare` 不出现于提示词；Purpose/Exit Criteria 保留 |
| 3 | **runtime 骨架匹配二级 Phase 标题** | `_skeletonize_runtime` 正则 `^# Phase` → `^#{1,2} Phase`（runtime-prepare 用 `## Phase N —`，此前骨架为空仅剩引用行） | prepare 骨架现含 7 个 Phase + 首行要求 + 引用行 |
| 4 | **prepare.md Exit Criteria/Next 空行** | 源文件补空行（渲染粘连根因在源文件） | cat -A 验证 |
| 5 | **capabilities desc 英文化** | config/main-chain-capabilities.yaml 5 条 desc 中文 → 英文（LANGUAGE_CONVENTION AI 内部层）；tr5 desc 含 `&` 加引号修 YAML | yaml.safe_load OK |

Gate：CLI 测试 **156 OK**（+4：frontmatter 剥离 / caps 位置 / 二级 Phase 骨架 / command frontmatter 剥离）；repo-lint 0/0/25；path-audit 0 broken；workflow-command-audit 0 blocker/1 WARN。

> 说明：优化 6（TRIAL 能力注入策略）与 7（Inputs 格式提示）未实施，需用户另行决策。

### wayfinder TRIAL 评估机制落地（2026-08-25，方案 A）

用户评估结论：wayfinder 静态高分（08-17 吸收决策）、实战零证据（全盘 0 `.wayfinder/` 产物 / 0 OPTIMIZATION_LOG / 0 消费记录）、预绑定过早（TRIAL 登记先于真实案例）。按用户选择**方案 A** 落地评估管道：

| 项 | 动作 |
|---|---|
| 采集机制 | 新建 `skills/wayfinder/OPTIMIZATION_LOG.md`（TRIAL 评估期强制；含触发场景/命中/决策图产物/工单/被 spec-develop 消费/验证/影响/复现字段） |
| 注入策略 | 保持 main-chain TRIAL 注入（enabled: true），3 处 desc 强化：未命中触发条件（大块模糊构想/迷雾/超单会话）→ **明确跳过**；实际触发 → **必须写 OPTIMIZATION_LOG** |
| 评估截止 | **提前评估优先，08-30 weekly 为硬截止**：近期将频繁使用（用户 08-25 确认），一旦积累 ≥1 被 spec/develop 消费的真实案例即提前评估；08-30 若无 ≥1 案例或未被消费 → 移除临时登记（main-chain-capabilities + core_skills 撤销，skill 保留 On-Demand）；有效 → 吸收绑定 prepare/spec |
| 覆盖阶段 | prepare / spec（用户明确要的两阶段）+ develop（既有登记保留，评估时一并判定） |
| 判定标准 | 沿用 08-20 M2：案例存在 + 决策图/决策工单产物 + ≥1 决策被后续 spec/develop 实际引用消费 |

### 提示词优化批次 2（2026-08-25，用户确认 1+2+3）

| # | 优化 | 改动 | 验证 |
|---|---|---|---|
| 1 | **骨架引言行合并列表项** | `_skeletonize_runtime`：引言行（Collect:/Invoke:/Analyze: 等）后合并首个列表项（`Collect:` → `Collect:\n  - User Requirements`），消除「只有动词无宾语」 | prepare 骨架 7 Phase 均含列表项 |
| 2 | **Runtime 节去重** | 新增 `_dedupe_runtime_section`（渲染层）：workflow 正文 `## Runtime` 节相对路径 → 指向「See the Runtime Skeleton below」；源文件不动（P25 单一来源） | 相对路径仅存源文件，提示词中不再重复 |
| 3 | **骨架加标题** | 骨架前置 `## Runtime Skeleton` + 引导行（「Phases of the full runtime template...」） | 渲染确认 |

Gate：CLI 测试 **159 OK**（+3：runtime 节指向骨架 / 骨架标题+列表项合并 / command 路径不受影响）；repo-lint 0/0/25；path-audit 0 broken；workflow-command-audit 0 blocker/1 WARN；command 路径实测不受影响（无 Runtime 节）。

### 能力段引导句优化（2026-08-25）

`_capabilities_section` 引导句去掉写死的 `(extensions/)` 来源括号（与实际注入内容解耦——本机注入 wayfinder 来自 skills/ 内置，extensions 存在时段落混含两来源，括号恒失准）；来源由每条能力自带绝对路径表达。文案：`You may use these registered external skills on demand for this stage:`。

Gate：CLI 159 OK；repo-lint 0/0/25；渲染验证 prepare/spec/develop 三阶段引导句已中性化。
