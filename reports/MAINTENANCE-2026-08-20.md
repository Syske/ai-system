# 系统巡检报告 — 2026-08-20（on-demand，范围：openapi-gateway OOM 流程问题提案）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- 范围: `outputs/proposal/260820-openapi-gateway-oom-flow-issues/` 巡检记录提案（P1–P7 流程问题评估）
- 日期: 2026-08-20
- 环境: WSL（默认 `python` shim 指向 Windows pyenv 路径不可执行，实测全部工具改用 `/usr/bin/python3` 运行正常）

---

## 一、工具校验结果

| 工具 | 结果 | 说明 |
|---|---|---|
| quick-check | verdict OK（0 findings） | 记录至 `metrics/quick-check-2026-08-20.json`；lint 25 WARN 为既有债 |
| quick-check --history | 5 snapshot 全 OK | 08-13/14/17/18/20 均 OK，趋势平稳 |
| repo-lint | **0 BLOCKER / 0 ERROR / 25 WARN** | 较 08-17 的 27 WARN **净 -2**，无回退 |
| repo-metrics | snapshot 已存 | 见下方指标对比 |
| path-audit | files=249，refs=646，**0 BROKEN** | 无断裂路径 |
| check.py（完整性门禁） | **PASS（0 warning）** | 15 workflows / 13 commands 全通过 |
| workflow-command-audit | **0 blocker / 0 warning** | 15 workflows 八段齐全、Next 链闭合、无悬空命令引用 |
| proposal-audit | **0 leftover / gate 0 err 0 warn** | `reports/` 53 文件扫描，无未闭合提案/未关 action item |

**结论：无 BLOCKER / ERROR，全部工具门禁通过，可放心进入后续巡检。**

### 指标对比（vs 08-17 快照）

| 指标 | 08-17 | 08-20 | 变化 |
|---|---|---|---|
| Skills | 33 | **31** | **-2**（技能收敛） |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 61 | 61 | = |
| Templates | 22 | 22 | = |
| 平均技能行数 | 760 | **468** | **-292**（大技能离仓） |

Skills 33→31 已核对为 08-17 VALUE-BURDEN 决策的落实：`skill-optimizer` / `iterative-optimizer`
移入 `archived/skills/`，`routing/outcome-benchmark-generator` 移除，新增 `deepseek-share-to-md` /
`wayfinder`。移除的技能均为超长大技能（skill-optimizer 曾 9968 行），故平均行数骤降——与
Evolution Principle / Value-Burden Check 方向一致，**属预期收敛，非异常**。

25 个 WARN 为既有债，与 08-17 记录同源：8 个 skill 缺 workflow.md、10 个英文代码注释 /
language 提示等；本巡检不处理（跟踪项）。

---

## 二、巡检发现（按严重度分级）— 范围提案 P1–P7 评估

对 `260820-openapi-gateway-oom-flow-issues` 的每一项，逐一对照当前 ai-system 实际代码/文档核验如下。

### 高

**P1. 链命令输入透传缺失 —— 确认属实（代码级定位）**
- 证据：`cli/main.py:288-310` 构建链命令时以**空上下文** `builder.build(cmd, {})` 触发后续步骤，
  字段留待 AI 在会话中向用户收集；`config/intents.yaml` 仅传**命令名**，不传数据。`## Next` 仅是
  菜单推荐（`workflow_reader.py` / `wizard/selection.py`），**无输出→下一步输入传递机制**。
- 缺输入提示：CLI wizard（`steps.py:171-175`）会点名缺失字段重问；但进入 AI 会话后
  `templates/runtime/*.md` **零**输入校验/询问指令，仅靠 `workflow-trigger.md` 通用“停止 / BLOCKED /
  不臆测”，不会列出“缺哪些项、如何补”。
- 处置：**确认**。属 CLI 编排结构性改动 → **仅输出建议，走变更管理（OPERATIONS 11）**，不在本巡检直接改。

**P2. 输入来源难以定位 —— 部分属实（操作/规范缺口）**
- 现状：项目中并无“问题输入”标准交付路径文档；`deepseek-share-to-md` 技能存在（提案所言好起点成真）。
  外部 URL / 日志如何进入消息流的约定未标准化。
- 处置：建议在 `governance/CONTEXT_LOADING.md` 或新增约定中定义“问题输入标准交付路径”；属治理/文档更新
  （低风险），仍按变更管理提议，确认后实施。

### 中

**P3. 外部 AI 结论未被系统化管理 —— 确认缺口**
- 证据：全库**无**任何“第三方 AI 结论核查”模板/流程/检查点。`SOURCE_OF_TRUTH.md` 优先级层级**不含外部来源**；
  `AI_OPERATING_RULES.md` 的 gate function 只约束自身产出的“所有声明”，未明确外部结论须先过核查。
  `runtime-knowledge.md` 第4/5阶段最接近（Accuracy/Source 校验）但面向知识入库，非第三方 AI 结论受检。
- 处置：建议新增 `templates/prompts/` 下的“外部 AI 结论核查”模板（可仿 `aic-skill-source.md` 的 vetting
  步骤），并把外部来源纳入 `SOURCE_OF_TRUTH.md`。**仅建议，走变更管理。**

**P4. 技能无法被工作流自动发现 —— 确认（且比提案更严）**
- 证据：系统**无任何技能自动发现/路由引擎**——`skill-launch.md` 只加载 CLI 预选名单，runtime/workflow
  **硬编码**技能名，frontmatter 触发词（description）**无任何代码扫描**。`deepseek-share-to-md` 仅登记于
  `skills/README.md`（手动栏），**未**进 `config/skill-groups.yaml` / `config/menu.yaml` / `intents.yaml`，
  即从 `aic-skill` 菜单都不可达。
- 处置：低成本可立即见效项——把 `deepseek-share-to-md` 注册进 `config/skill-groups.yaml`（配置改动，
  需确认后实施）；完整“按任务特征路由”属结构性改造，仅建议、走变更管理。

### 低

**P5. Direct-path 项目缺 workspace 容器 —— 确认**
- 证据：`repositories/openapi-gateway.yaml` 存在；`workspaces/` 无 `openapi-gateway` 容器
  （现仅有 archived / opencode-test / openspec-test / pi-agent-develop / pywechat-live-2608）。
- 处置：若该项目需长期 request→spec→develop 全流程，创建容器属**项目接入**动作，交给
  prepare / dev-setup / 项目 onboarding 流程，非本巡检改动。

**P6. 诊断数据命名/归档无序 —— 部分确认（主要在工作区外）**
- 证据：工作区侧归档约定已存在（`outputs/<workflow>/<date>-<desc>/`，本次即 `outputs/bugfix/260820-openapi-gateway-oom-jmx/`）。
  capture/watchdog 脚本在工作区外（用户 Downloads），非 ai-system 资产。
- 处置：采集脚本命名/头嵌入服务名+Pod 名的约定属外部工具建议；可在 AGENTS/约定文档中记录为指南，无需
  ai-system 结构性改动。

**P7. 工作过程中文未统一简体 —— 确认规范缺口**
- 证据：`governance/LANGUAGE_CONVENTION.md` 规定“中文（用户向）”，但**未**显式强制“简体”
  （全库 grep `简体/繁体` 无命中）。本次运行过程措辞曾混用繁体，最终产物已为简体。
- 处置：**最小文档修正候选**——在 `LANGUAGE_CONVENTION.md` 显式声明“所有中文统一简体”。
  属 step-4 “minor doc drift” 类，可在用户确认后就地小修。本巡检未擅自改动，列为待确认修正。

---

## 三、一致性抽查结论（逐项）

| 项目 | 结果 |
|---|---|
| 链式命令输入透传（P1） | 无机制（见 P1） |
| 技能自动发现/登记（P4） | 无引擎；deepseek-share-to-md 菜单不可达 |
| 外部 AI 结论核查模板（P3） | 无 |
| workflows/*.md 八段齐全且有序 | ✅ 通过（workflow-command-audit 0 warning） |
| config/workflows/*.yaml 保持最小（name/workflow/runtime） | ✅ 通过（无 A1 回胀；bugfix-modes.yaml 为合法配置） |
| 引用路径存在（standards/、loaders/、templates/prompts/、cli/commands/） | ✅ 通过（path-audit 0 broken） |
| 链接健康（projects/ 等联接/符号链接目标可达） | ✅ 通过（无断链；各目录可访问） |
| Doc-vs-reality（AGENTS.md 结构图 / OPERATIONS 段 vs 实际目录） | ✅ 通过（10 个顶层目录全部存在） |
| 状态卫生（.aic-state.yaml 项目引用仍存在） | ✅ 通过（pywechat-live-2608 容器在） |
| 提案遗留（proposal-audit） | ✅ 通过（0 leftover；本次范围提案以巡检记录存于 outputs/proposal，不入 reports/P# 索引） |

**一致性抽查 11 项全部通过；范围提案 P1–P7 全部核验出处置结论。**

---

## 四、修复动作与建议清单

**待确认的次要就地修正（步骤 4 允许，但按 Change Control 需用户确认后实施）**
1. P7 最小修正：`LANGUAGE_CONVENTION.md` 显式加入“所有中文（正文/注释/命令行说明）统一简体”。

**结构性改动建议（仅输出建议，走 OPERATIONS 11 变更管理：Analyze→Propose→Review→Approve）**
2. **P1（高）**：链命令上下文传递——`cli/main.py` 链命令由 `{}` 改为透传已收集上下文；并发运行时缺输入提示
   （列出缺失字段+如何补），不只“停止”。
3. **P2（高）**：在 `CONTEXT_LOADING.md` / 约定文档定义“问题输入标准交付路径”（日志落约定目录、URL 明文入消息流）。
4. **P3（中）**：新增“外部 AI 结论核查”模板（证据核对→标注保留/修正），并纳入 `SOURCE_OF_TRUTH.md` 外部来源优先级说明。
5. **P4（中）**：将 `deepseek-share-to-md` 注册进 `config/skill-groups.yaml` / menu（低成本）；完整技能路由另议。
6. **P5（低）**：openapi-gateway 建 workspace 容器 → 走 project onboarding / dev-setup，非本巡检。
7. **P6（低）**：采集脚本命名/归档约定写入外部工具指南（非 ai-system 结构性改动）。

> 全部为建议项；本巡检**read-first，未做任何代码/配置改动**。

---

## 五、quick-check 趋势（近 5 日快照对比）

| 日期 | verdict | findings | lint WARN |
|---|---|---|---|
| 08-13 | OK | 0 | — |
| 08-14 | OK | 0 | — |
| 08-17 | OK | 0 | 27 |
| 08-18 | OK | 0 | — |
| 08-20 | OK | 0 | **25** |

趋势平稳，08-20 lint WARN 较 08-17 少 2，无回退。quick-check 汇总 0 发现（25 WARN 为 repo-lint 既有债，
不判定为“发现”，与历史记录口径一致）。

---

## 六、经验记录（运维经验 → 供后续 consult）

- WSL 下默认 `python`（Windows pyenv shim）不可执行，`python3` 可用；P23 跨平台约定已覆盖此类退化，
  门禁均用显式解释器跑通。
- 技能数 / 平均行数骤降的指标变化需与 VALUE-BURDEN 归档决策对照解读，避免误判为异常。

## 附

- 范围提案: `outputs/proposal/260820-openapi-gateway-oom-flow-issues/巡检记录提案-流程问题.md`
- 根因分析: `outputs/bugfix/260820-openapi-gateway-oom-jmx/根因分析报告-内存OOM重启.md`
- 本报告: `reports/MAINTENANCE-2026-08-20.md`

---

## 八、后续修复批次（用户授权继续修复后执行，2026-08-20）

### 已落地（低风险/直改，门禁与测试全绿）

| 项 | 改动 | 文件 | 验证 |
|---|---|---|---|
| P1 | 链命令透传已收集 context（`{}`→`context`，字段按契约自动过滤填充，如 Project ID）；workflow-trigger 缺输入提示改为“列出缺失必填字段并向用户确认，无法补齐才 BLOCKED” | `cli/main.py`、`templates/prompts/workflow-trigger.md` | 实测 bugfix/develop 透传 Project ID 成功；change-impact/scan 按契约过滤正确不下漏；空 context 向后兼容；unchanged 其余行为；**CLI 87 测试全过** |
| P3 | 新增外部 AI 结论核查模板（证据逐条 KEEP/REVISE/REJECT/UNVERIFIABLE）；SOURCE_OF_TRUTH 增 Rule 0（外部结论为未验证输入，须先过核查，冲突由用户仲裁） | `templates/prompts/external-ai-review.md`、`governance/SOURCE_OF_TRUTH.md` | check.py PASS 0 |
| P2 | CONTEXT_LOADING 增“问题输入标准交付路径”（日志落约定目录、URL 明文入消息流、share 用 deepseek-share-to-md、外部结论先核查） | `governance/CONTEXT_LOADING.md` | check.py PASS 0 |
| P6 | OPERATIONS 1.8.2 增现场诊断数据命名/归档约定（service-pod-timestamp、随产物归档） | `OPERATIONS.md` | check.py PASS 0 |
| P4（菜单可达部分） | launcher 新增 `core` 源：`config/skill-groups.yaml` 增 `core_skills` 登记 + `source: core` 分组；`skill_scan.scan()` 扫描登记的核心 on-demand 技能；i18n 标题；源码标记（🧬 core） | `cli/services/skill_scan.py`、`skill_launcher.py`、`config/skill-groups.yaml`、`config/i18n/zh.yaml`、`cli/tests/test_skill_launcher.py` | 实测 deepseek-share-to-md 从菜单可达；**CLI 88 测试全过** |

### 结论

- 门禁：check.py PASS 0 warning / repo-lint 25 WARN（无新增）/ path-audit 0 broken；CLI 88 项测试全过。

### 未直改（结构性 / 项目接入，登记为后续项）

- **P4 完整技能自动路由**：属架构特性（任务特征→技能语义匹配），需提案 + 评审，非本批次直改。已落地的最小部分 = 触发词登记（skills/README）+ 外部结论路由到核查工具 + **launcher core 源**（deepseek-share-to-md 从 aic-skill 菜单可达）。
- **P5 openapi-gateway workspace 容器**：属项目 onboarding（prepare / dev-setup），且空容器违反 Evolution Principle（built-but-unused）。待真实 request→spec→develop 需求出现时创建。

## 九、链路（积木组合）能力（用户新增需求，2026-08-20 后续）

用户提出：从**场景**出发，把工作流/命令/技能当**积木**自由组合成**链路**运行（如
`scan + confluence-markdown-publisher`=分析并发布到 wiki；`bugfix + codeup-submit-mr +
hotfix-test-doc`=改 bug 并出转测文档）。经讨论确认 3 点后实现**最小可用**：

- **块**：type ∈ workflow / command / skill。
- **松耦合 + 显式交接**：每次运行建 `outputs/chain/{yyMMdd}-{desc}/chain-manifest.yaml`，登记每块产物路径，下游块从 manifest 读上游产物（不硬编码路径）。
- **可复用 + 可进化**：内置 `config/chains.yaml`（analyze-and-publish / bugfix-release-doc）；AI 维护链存入 `.aic-state.yaml → ai_chains`（对齐 ai_intents），按使用可调整。
- **入口**：新增轻量命令 `aic-chain`（`cli/services/chain.py` 注册表/上下文 + `chain_launcher.py` 选/描述→建上下文→组装各块 prompt）复用 skill-launch 模板。
- 配套：`cli/commands/aic-chain.md`、menu.yaml 注册（commands_analysis）、`_INTERACTIVE_COMMANDS` 接入、`cli/tests/test_chain.py`（8 用例）。
- 验证：check.py PASS 0（15 workflows / 14 commands）/ repo-lint 25 WARN 无新增 / workflow-audit 0 / path-audit 0 / **CLI 96 测试全过**（含 chain）。
