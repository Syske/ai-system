# Reports Index

集中索引 `reports/` 下所有分析、维护、提案、迁移与规范文档，便于查找与跟进待办。

- 每项一行：类型 / 主题 / 日期 / 文件 / 遗留待办。
- 提案（P 系列）状态与门禁见 `PROPOSALS.md`（proposal-audit 维护，勿手工改状态）。
- 新报告入目录即登记；本文件不参与 proposal-audit 门禁。

---

## 提案（P 系列）

状态与门禁见 [PROPOSALS.md](PROPOSALS.md)，此处仅列主题索引：

| 提案 | 主题 | 日期 |
|------|------|------|
| [P6](P6-SKILL-SIZE-PROPOSAL.md) | Skill Size Reconciliation | 2026-08-01 |
| [P7](P7-WORKFLOW-AUTHOR-COMMAND.md) | `aic-workflow` Authoring Command | 2026-08-05 |
| [P8](P8-COMMAND-AUTHOR.md) | `aic-command` Authoring Command | 2026-08-05 |
| [P9](P9-SKILL-LAUNCHER.md) | `aic-skill-launch` Skill Launcher | 2026-08-05 |
| [P10](P10-SKILL-OPTIMIZER-SPLIT.md) | skill-optimizer 脚本拆分（超限文件 + 双入口去重） | 2026-08-06 |
| [P11](P11-SKILL-OPTIMIZER-ABSORPTION.md) | skill-optimizer 网络思想吸收（held-out 门控/demo-augment/description 调优） | 2026-08-06 |
| [P12](P12-LANGCHAIN-REMOVAL.md) | 移除 langchain 依赖（openai SDK 直调） | 2026-08-06 |
| [P13](P13-DEPENDENCY-CYCLE-CLEANUP.md) | 破除 3 个 Skill 依赖环（检测器语义分层） | 2026-08-06 |
| [P14](P14-SNAPSHOT-GOVERNANCE.md) | 跨服务 SNAPSHOT 治理纪律（S4） | 2026-08-06 |
| [P15](P15-MULTISKILL-GUARD.md) | 多-SKILL.md 输入防护（E3 缺陷修复） | 2026-08-06 |
| [P16](P16-STATE-WRITE-GUARD.md) | wizard 状态写入增加项目存在性校验（S2 根因修复） | 2026-08-08 |
| [P17](P17-MAVEN-DELEGATION-GOVERNANCE.md) | java-maven 委派规范（D1 根治） | 2026-08-08 |
| [P18](P18-THIN-COMMAND-SLIMMING.md) | aic-apply / aic-explore 命令瘦身（thin-command 门禁） | 2026-08-08 |
| [P19](P19-EXPLORE-SKILLS-RELATIONSHIP.md) | explore 与 explore-codebase 技能关系澄清（季度评估合并） | 2026-08-08 |
| [P20](P20-HOTFIX-TEST-DOC-GUARDRAILS.md) | hotfix-test-doc 发布链护栏增强（校验误报 + 空单元格自动修复） | 2026-08-11 |
| [P21](P21-HOTFIX-TEST-DOC-RENDER-FIX.md) | hotfix-test-doc 模板标题渲染缺陷修复与回填工具 | 2026-08-12 |
| [P22](P22-WSL-ENVIRONMENT-INTEGRATION.md) | WSL 环境集成与初始化能力 | 2026-08-14 |
| [P24](P24-PROVIDER-CONTRACT-TEST-FIX.md) | Provider Wizard 契约测试夹具修复（win32 平台 check.py 回归，已实施 exit 0） | 2026-08-17 |
| [P25](P25-WORKFLOW-FRONTMATTER-SYNTAX.md) | 统一 Workflow 资产语法为 SKILL.md frontmatter 约定（Implemented） | 2026-08-20 |
| [P26](P26-MAIN-CHAIN-BRANCH-RULE.md) | 开发主链分支创建规则（cc{date}_ipd_{desc}_{service} 暂定）+ 不可变（Proposed） | 2026-08-20 |
| [P28](P28-CHANGE-ID-GENERATION.md) | Change ID 自动生成（规则 slug 派生优先，AI 可选后续） | 2026-08-21 |
| [P29](P29-HOME-ENV-CONFIG.md) | 机器层环境配置迁移至 ~/.config（跨平台原生，首启按系统生成） | 2026-08-23 |
| [P30](P30-PROMPT-ROOT-PLACEHOLDERS.md) | 提示词渲染期解析根路径占位符（{workspace_root} 等，模板零改动）— **Implemented** | 2026-08-23 |
| [P31](P31-STANDARDS-COOL-MIGRATION.md) | standards/cool 公司规范迁出通用层（extensions + loader 可配置）— **Implemented** | 2026-08-23 |
| [P32](P32-PREPARE-OUTPUTS-LOCATION.md) | prepare 工作流子报告输出位置与 AGENTS.md 约定对齐（outputs/prepare→workspace-anchored）— **Implemented** | 2026-08-24 |
| [P33](P33-ISSUE-CAPTURE-CONTEXT-LOADING.md) | 日常运行中发现变更时的上下文加载触发规则（Issue Capture：JIT 加载 proposal-policy + OPERATIONS §12 + 尺寸分流）— **Implemented** | 2026-08-24 |
| [P34](P34-MAINTENANCE-STATE-INTO-GIT.md) | maintenance 状态纳入 ai-system 提交（拆分：系统级 maintenance 块 → config/maintenance.yaml 入 git，机器级留 workspaces 本地）— **Implemented** | 2026-08-24 |
| [P35](P35-PYTHON-INTERPRETER-ROBUSTNESS.md) | python 解释器鲁棒性（命令文档统一 python3 + 工具调用鲁棒化）— **Implemented** 2026-09-01 | 2026-08-24 |
| [P38](P38-WORKFLOW-INTERACTION-AUDIT.md) | 逐 aic 工作流用户交互审计（wizard 提示序列/确认节奏/可选字段呈现/中途检查点；与 P37 互补：P37 定必填归属、P38 定交互呈现）— **Implemented**（批次 1；批次 2 defer：全推导字段静默推导等） | 2026-08-25 |
| [P39](P39-EXTENSIONS-LINT-HIDDEN-DIRS.md) | extensions-lint 隐藏目录误判为扩展（--fix-missing-log 向 .git/.githooks 写入脚手架；修复：枚举过滤 `.` 开头目录）— **Implemented** | 2026-08-25 |
| [P40](P40-OPENSPEC-CHANGE-NAME-NAMING.md) | OpenSpec-CN change name 字母开头约束与 workspace `<YYYYMM>-` 命名惯例冲突（openspec changes 目录用字母开头，workspace 目录不变 + 映射注明）— **Implemented** | 2026-08-25 |
| [P41](P41-TR5-SECTION1-SEMANTICS.md) | tr5 脚本健壮性批次：§1 语义矛盾（推荐 validate 特判改查结构化字段）+ 工时 4-8h 自动校验 + check_spec 服务名正则收紧 + tr4_url 技改降级 info — **Proposed** | 2026-08-26 |
| [P42](P42-TR5-TEMPLATE-SKELETON.md) | tr5 templates 缺 markdown 骨架（tr5_template.md 每项目从 storage XML 反推；新增 19 节骨架模板 + SKILL 拷贝指引）— **Proposed** | 2026-08-26 |
| [P43](P43-TR5-SECTION0-INLINE-BODIES.md) | tr5 §0 数据槽位恒空（`_split_section0` 不识别头行内联正文 → 0_1/0_2/0_3 恒空且 merge 僵尸保留 → 发布页 §0 露引导占位符；推荐解析器支持 inline）— **Implemented** | 2026-08-28 |
| [P44](P44-WORKTREE-CONVENTION.md) | Worktree 约定完善（项目级隔离 + 生命周期管理）— **Implemented** | 2026-08-31 |
| [P45](P45-RUNTIME-LANGUAGE-GATE.md) | 运行时语言门禁（completion-time language gate，方案 B 正式化）— **Implemented** 2026-09-01 | 2026-09-01 |
| [P46](P46-TR5-DEBT-VALIDATION-MARKER.md) | tr5 发布债收口（check_tr5 8 FAIL）+ review/verify 验证标记检查 — **Proposed** | 2026-09-01 |
| [P47](P47-WORKFLOW-PRECONDITIONS-OUTPUTS.md) | develop 前置处理规则与产物目录约定（前置不满足→先跑 dev-setup；完成报告落 completion-reports/）— **Implemented** 2026-09-02 | 2026-09-02 |
| [P36](P36-SETUP-ENV-INIT-SCAFFOLD.md) | 初始化脚本完善（--env-init 补齐目录骨架 + 引导指定外部代码仓库；2026-09-03 增补触发层：aic 首次运行只读检测+交互确认，否决静默自动）— **Proposed** | 2026-08-25 |
| [P37](P37-REQUIRED-INPUTS-TRIAGE.md) | 工作流必填参数必要性评估（降可选/自动推导/保持，提升使用效率）— **Proposed** | 2026-08-25 |

---

## 维护报告（MAINTENANCE）

| 日期 | 模式 | 范围 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| 2026-07-22 | weekly | 首次全量巡检 + release.md 评估 | `MAINTENANCE-20260722.md` | — |
| 2026-08-01 | monthly | 结构/能力/生命周期/演进 | `MAINTENANCE-20260801.md` | — |
| 2026-08-05 | on-demand | aic-sync 同步核查 | `MAINTENANCE-2026-08-05.md` | — |
| 2026-08-06 | monthly | 架构/能力矩阵/一致性抽查 + 修复批次 | `MAINTENANCE-2026-08-06.md` | —（S1-S4 已闭环） |
| 2026-08-06 | on-demand | aic-sync 复查 | `MAINTENANCE-2026-08-06-aic-sync.md` | — |
| 2026-08-06 | on-demand | live-facade SNAPSHOT 风险 | `MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md` | —（P14 已闭环） |
| 2026-08-06 | on-demand | 方法长度与注释约定 | `MAINTENANCE-2026-08-06-method-comment-convention.md` | P1/P2/P3 → propose（见 P11 记录） |
| 2026-08-08 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 A1-A4 | `MAINTENANCE-2026-08-08.md` | F1-F3 已修复（A1-A4 已闭环） |
| 2026-08-13 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 S-A/S-B | `MAINTENANCE-2026-08-13.md` | F1-F2 已修复（S-A/S-B 已执行）；P18/P19 已闭环(2026-08-14)；P20 遗留 |
| 2026-08-13 | on-demand | extensions 域巡检（Scope=extensions） | `EXTENSIONS-MAINTENANCE-2026-08-13.md` | F1: 6 个 OPTIMIZATION_LOG 空模板待补录 |
| 2026-08-14 | on-demand | 巡检当前提案 + 治理一致性抽查 | `MAINTENANCE-2026-08-14.md` | P22 已 approve（阶段二 defer 至新提案）；F2/F3 已修复 |
| 2026-08-14 | on-demand | 跨平台治理落地（P23 批次：gitattributes/hook/lint） | `P23-CROSS-PLATFORM-MAINTENANCE-GOVERNANCE.md` | —（P23 已 Implemented） |
| 2026-08-17 | on-demand | 工具校验/周度巡检/一致性抽查 | `MAINTENANCE-2026-08-17.md` | R1: check.py 回归（FakeWizard 缺 projects_root）→ 已立提案 P24 待评审；其余全 PASS |
| 2026-08-20 | on-demand | openapi-gateway OOM 流程提案（P1–P7 评估） | `MAINTENANCE-2026-08-20.md` | P7 简体规范已就地修（LANGUAGE_CONVENTION）；P4 技能触发词已登记 skills/README；P1/P2/P3/P5/P6 结构建议待变更管理立项 |
| 2026-08-23 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次（提示词路径绝对化 + Windows 路径归一化 + env-init） | `MAINTENANCE-2026-08-23.md` | 批次 A 已落地：P26 置 Implemented；P28 已补 README 索引；workflow-trigger 死模板已归档；方案 3（根占位符填充）待立项 |
| 2026-08-24 | on-demand/prepare | 增量基线 CHANGED→对应子集；scope=prepare 一致性抽查（8 项 7 过/1 失败）+ 实施 P32 方案 A | `MAINTENANCE-2026-08-24.md` | P32 已闭环（prepare.md Outputs 位置对齐 workspace-anchored）；P28/P26 开放项 defer |
| 2026-08-24 | on-demand/workflows | 全量审计（delta FIRST_RUN→record）；workflows 域结构/注册表/引用链/Next 链全绿；AGENTS.md 缺失（doc-vs-reality 对象） | `MAINTENANCE-2026-08-24-workflows.md` | AGENTS.md 决策（重建/检查项降级，L2）；README 条件转移表补 release BLOCKED 行（L1 待确认）；P35 待用户决策 |
| 2026-08-25 | on-demand | prepare 工作流集成外部扩展 tr5（含受影响区域增量子集：cli / config / governance / reports / skills / templates / workflows + extensions 域） | `MAINTENANCE-2026-08-25.md` | tr5 已注册；P38 批次 1 已实施；P39 已实施；增量基线刷新 |
| 2026-08-26 | on-demand | extensions/tr5 — 前后端需求区分机制确认 | `MAINTENANCE-2026-08-26.md` | — |
| 2026-08-31 | weekly | 增量 NO_CHANGES；工具校验 OK；code-review.md 节顺序违规；7 项提案开放 | `MAINTENANCE-2026-08-31.md` | code-review.md 节结构调整需 L2 变更审批 |
| 2026-08-31 | on-demand | task 制定/拆分对齐（task-splitter → cards/ 位置 + Task Card 字段）+ 淘汰根 tasks.md + 堵 archive 归档完成度缺口 | `MAINTENANCE-2026-08-31-task-splitter.md` | task-splitter 1.1.0；tasks.md 淘汰；archive/explore/aic-propose 同步 |
| 2026-09-01 | on-demand/workflows | 语言边界专项：根因定位（执行层未按 locale 转换）+ pilot A（aic-maintain 交互语言约束，自测+实测通过） | `MAINTENANCE-2026-09-01.md` | 方案 B/C 延后（待 §11）；P35 复现实锤建议实施 |
| 2026-09-01 | on-demand | 最新改动诊断（提交 3580bb0 + 孤儿 runtime-base.md 改动）+ 最新运行日志巡检 | `MAINTENANCE-2026-09-01-logs.md` | 孤儿改动 B1/B2/B3 待决策（建议 B1）；README 索引补登；code-review.md 节序待 L2 |
| 2026-09-03 | on-demand | pi-lens 扩展安装评估（结论：现在不安装，用户已确认）+ env-init 首次运行触发场景并入 P36（触发层增补）+ 迁移后基线重置（FIRST_RUN 全量审计顺延 09-07） | `MAINTENANCE-2026-09-03.md` | extensions 仓恢复待用户（aic extensions-init 已覆盖）；P47 索引补登（本次）；P36 增补待季度回顾决策是否提前 |

---

## 评估与评审报告

| 类型 | 主题 | 日期 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| Quarterly | 季度评估（E9） | 2026-08-06 | `QUARTERLY-REVIEW-2026-08-06.md` | Q4/Q5 下季度 |
| Assessment | CLI 规范化评估 | 2026-08-06 | `CLI-STANDARDIZATION-ASSESSMENT.md` | **C1 待办（明日执行）→ C2/C3/C4** |
| Business | 业务仓 Java 格式治理建议（CLI 路线 v2：用户裁定不改 pom，C2 校准定稿） | 2026-09-03 | `SPOTLESS-FORMAT-GATE-PROPOSAL.md` | 待业务侧拍板 master 基线执行与 Checkstyle 引入；工具链已入库（c7eef0b/b5e9f70） |
| Assessment | bugfix skill 优化评估 | 2026-08-08 | `BUGFIX-SKILL-ASSESSMENT-2026-08-08.md` | — |
| Maintenance | 语言检查存量债登记 | 2026-08-08 | `MAINTENANCE-2026-08-08-language-lint-debt.md` | #1-3 参数说明可接受 / #4 顺手修 / #5-7 memory 翻译待办 |
| Maintenance | aic 项目识别与状态记录修复 | 2026-08-08 | `MAINTENANCE-2026-08-08-aic-project-recognition.md` | workspace.yaml 初始化未自动化 |
| Assessment | 上下文/注意力/架构缺口评估+修复 | 2026-08-08 | `GAP-ASSESSMENT-2026-08-08-context-attention-architecture.md` | memory 沉淀/跨会话状态持久化遗留(已闭环于 skills) |
| Assessment | ADR-0009 合规性系统诊断 | 2026-08-13 | `ADR-0009-COMPLIANCE-DIAGNOSIS-2026-08-13.md` | **P1 standards/cool 迁移待评审；P2 废弃命令待清理** |
| Assessment | Token 缓存命中率优化 | 2026-08-13 | `CACHE-OPTIMIZATION-2026-08-13.md` | **R1 骨架化 agent 读取待实测；R2 实际命中率待验证；R3 强制全量开关待实现** |
| Daily | 日终报告 | 2026-08-08 | `DAILY-2026-08-08.md` | — |
| Assessment | 架构评估 | 2026-07 | `ARCHITECTURE-ASSESSMENT-2026-07.md` | — |
| Assessment | 三方 Skill 参考价值 | 2026-08-01 | `THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md` | — |
| Assessment | Skill 来源评估: mattpocock wayfinder（吸收为 skills/wayfinder, On-Demand） | 2026-08-17 | `skill-source-2026-08-17-wayfinder/skill-source-report.md` | M2: 等待真实大块模糊构想用例验证决策图层 |
| Assessment | aic 交互与提示词链路专项优化（B1/H1-H6/M1-M8 等 16 项） | 2026-08-18 | `CLI-INTERACTION-OPTIMIZATION-2026-08-18.md` | 意图链连续执行/P22 阶段二待后续 |
| Assessment | 运行诊断日志机制（logs/ 每运行落盘, 模板 + governance 契约） | 2026-08-17 | `templates/runtime/runtime-diagnostic-log.md`（经 AI_OPERATING_RULES §Completion、REFLECTION_RULES 落盘条目登记） | 待随一次实际 command/workflow 跑一轮验证字段/拆分阈值 |
| Decision | Value-Burden Check: 归档 skill-optimizer + iterative-optimizer（无价值证据的 10k 行 meta 工具） | 2026-08-17 | `VALUE-BURDEN-DECISION-skill-optimizer-2026-08-17.md` | 归档联动清理已执行；后续 MAINTENANCE/QUARTERLY 对 >3000 行技能强制检查 |
| Assessment | Value-Burden: implement skill 保留（已兑现价值 + 健康负担，最大活跃技能 2368 行） | 2026-08-17 | `VALUE-BURDEN-ASSESSMENT-implement-2026-08-17.md` | — |
| Review | Workflow 层优化 | 2026-07 | `WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` | — |
| Report | Repository Optimization | — | `REPOSITORY-OPTIMIZATION-REPORT.md` | — |
| Report | Repository Architecture v2 | — | `REPOSITORY-ARCHITECTURE-REPORT-v2.md` | — |
| Review | 架构评审 | 2026-07 | `architecture-review-2026-07.md` | — |

---

## 规范速查

| 主题 | 文件 | 说明 |
|------|------|------|
| AI-System 扩展规范（命名/流程/命令） | `EXTENSION-STANDARDS.md` | 新增资产前的权威速查（Golden Rule） |

---

## 迁移（MIGRATION）

| 主题 | 文件 | 状态 |
|------|------|------|
| AI System Repository Migration Plan v2 | `MIGRATION-PLAN-v2.md` | — |
| AI System Repository Migration Report v1 | `MIGRATION-REPORT-v1.md` | — |

---

## 结构分析目录（analysis-*）

各目录含 `analysis-report.md` / `consistency-report.md` / `dependency-report.md` / `recommendations.md`：

| 目录 | 主题 | 日期 |
|------|------|------|
| `analysis-2026-08-01-structure-governance/` | governance 结构分析 | 2026-08-01 |
| `analysis-2026-08-01-workflows-structure/` | workflows 结构分析 | 2026-08-01 |
| `analysis-2026-08-03-structure-workflows/` | workflows 结构复查 | 2026-08-03 |

---

## 维护纪律

- 新增 `MAINTENANCE-*` / `P*` 报告：登记上方对应表（proposal-audit 自动扫门禁）。
- 新增评估/规范/迁移文档：登记对应表。
- 遗留待办列有内容的报告，在下一次维护/评估中优先跟进；闭环后更新该列。
