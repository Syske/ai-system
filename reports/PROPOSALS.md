# Proposals Index

集中索引 ai-system 的所有变更提案（`reports/P*.md`），便于查看与确认。

- 每行一个提案：状态 / 主题 / 创建日期 / 文件。
- 状态定义见 `governance/policies/proposal-policy.md`（Proposed / Approved / Rejected / Implemented / Archived）。
- 维护：新增提案时登记一行；状态变更时同步更新本表 + 提案文件 Status 字段。
- 门禁：`python tools/proposal-audit.py` 校验本表与提案文件 Status 一致性、遗留项清单。

---

## 提案清单

| 状态 | 提案 | 创建 | 文件 |
|---|---|---|---|
| Implemented | skill-optimizer 脚本拆分（消除 3 个超限文件 + 双入口重复） | 2026-08-06 | `P10-SKILL-OPTIMIZER-SPLIT.md` |
| Implemented | Skill Optimizer 网络思想吸收（SkillOpt / DSPy / TextGrad / Claude skill-creator） | 2026-08-06 | `P11-SKILL-OPTIMIZER-ABSORPTION.md` |
| Implemented | 移除 langchain 依赖（openai SDK 直调） | 2026-08-06 | `P12-LANGCHAIN-REMOVAL.md` |
| Implemented | 破除 3 个 Skill 依赖环（S3） | 2026-08-06 | `P13-DEPENDENCY-CYCLE-CLEANUP.md` |
| Implemented | 跨服务 SNAPSHOT 治理纪律（S4） | 2026-08-06 | `P14-SNAPSHOT-GOVERNANCE.md` |
| Implemented | 多-SKILL.md 输入防护（E3 缺陷修复） | 2026-08-06 | `P15-MULTISKILL-GUARD.md` |
| Implemented | wizard 状态写入增加项目存在性校验（S2 根因修复） | 2026-08-08 | `P16-STATE-WRITE-GUARD.md` |
| Implemented | java-maven 委派规范（D1 根治） | 2026-08-08 | `P17-MAVEN-DELEGATION-GOVERNANCE.md` |
| Implemented | aic-apply / aic-explore 命令瘦身（thin-command 门禁） | 2026-08-08 | `P18-THIN-COMMAND-SLIMMING.md` |
| Implemented | explore 与 explore-codebase 技能合并评估（D5） | 2026-08-08 | `P19-EXPLORE-SKILLS-RELATIONSHIP.md` |
| Implemented | hotfix-test-doc 发布链护栏增强（校验误报 + 空单元格自动修复） | 2026-08-11 | `P20-HOTFIX-TEST-DOC-GUARDRAILS.md` |
| Implemented | hotfix-test-doc 模板标题渲染缺陷修复与回填工具 | 2026-08-12 | `P21-HOTFIX-TEST-DOC-RENDER-FIX.md` |
| Approved | WSL 环境集成与初始化能力 | 2026-08-14 | `P22-WSL-ENVIRONMENT-INTEGRATION.md` |
| Implemented | 跨平台（Linux/WSL + Windows）混合维护治理约定 | 2026-08-14 | `P23-CROSS-PLATFORM-MAINTENANCE-GOVERNANCE.md` |
| Implemented | Provider Wizard 契约测试夹具修复（win32 平台 check.py 回归） | 2026-08-17 | `P24-PROVIDER-CONTRACT-TEST-FIX.md` |
| Implemented | 统一 Workflow 资产语法为 SKILL.md frontmatter 约定 | 2026-08-20 | `P25-WORKFLOW-FRONTMATTER-SYNTAX.md` |
| Implemented | 开发主链分支创建规则（cc{date}_ipd_{desc}_{service}，暂定）+ 创建后不可变 | 2026-08-20 | `P26-MAIN-CHAIN-BRANCH-RULE.md` |
| Proposed | Change ID 自动生成（规则 slug 派生优先，AI 可选后续） | 2026-08-21 | `P28-CHANGE-ID-GENERATION.md` |
| Approved | 机器层环境配置迁移至 ~/.config（跨平台原生，首启按系统生成） | 2026-08-23 | `P29-HOME-ENV-CONFIG.md` |
| Implemented | 提示词渲染期解析根路径占位符（{workspace_root} 等，模板零改动） | 2026-08-23 | `P30-PROMPT-ROOT-PLACEHOLDERS.md` |
| Implemented | standards/cool 公司规范迁出通用层（extensions + loader 可配置） | 2026-08-23 | `P31-STANDARDS-COOL-MIGRATION.md` |
| Implemented | prepare 工作流子报告输出位置与 AGENTS.md 约定对齐 | 2026-08-24 | `P32-PREPARE-OUTPUTS-LOCATION.md` |
| Implemented | 日常运行中发现变更时的上下文加载触发规则（Issue Capture） | 2026-08-24 | `P33-ISSUE-CAPTURE-CONTEXT-LOADING.md` |
| Implemented | maintenance 状态纳入 ai-system 提交（拆分：系统级入 git / 机器级留本地） | 2026-08-24 | `P34-MAINTENANCE-STATE-INTO-GIT.md` |
| Implemented | python 解释器鲁棒性（`python` shim 在 WSL 不可用，scripts/docs 用法不一） | 2026-08-24 | `P35-PYTHON-INTERPRETER-ROBUSTNESS.md` |
| Proposed | 初始化脚本完善（--env-init 补齐目录骨架 + 引导指定代码仓库） | 2026-08-25 | `P36-SETUP-ENV-INIT-SCAFFOLD.md` |
| Proposed | 工作流必填参数必要性评估（省掉不必要的必填项，提升用户使用效率） | 2026-08-25 | `P37-REQUIRED-INPUTS-TRIAGE.md` |
| Implemented | 逐 aic 工作流用户交互审计（wizard 交互序列/确认节奏/呈现） | 2026-08-25 | `P38-WORKFLOW-INTERACTION-AUDIT.md` |
| Implemented | extensions-lint 隐藏目录误判为扩展（--fix-missing-log 污染 .git/.githooks） | 2026-08-25 | `P39-EXTENSIONS-LINT-HIDDEN-DIRS.md` |
| Implemented | OpenSpec-CN Change Name 字母开头约束与 workspace 命名惯例冲突 | 2026-08-25 | `P40-OPENSPEC-CHANGE-NAME-NAMING.md` |
| Proposed | tr5 脚本健壮性批次（§1 语义 + 工时校验 + 服务名正则 + tr4_url 条件化） | 2026-08-26 | `P41-TR5-SECTION1-SEMANTICS.md` |
| Proposed | 新增 tr5_template.md 一页纸骨架模板 | 2026-08-26 | `P42-TR5-TEMPLATE-SKELETON.md` |
| Implemented | tr5 §0 数据槽位恒空（inline 正文解析缺失 → 发布页 §0 露引导占位符） | 2026-08-28 | `P43-TR5-SECTION0-INLINE-BODIES.md` |
| Implemented | Worktree 约定完善（项目级隔离 + 生命周期管理） | 2026-08-31 | `P44-WORKTREE-CONVENTION.md` |
| Implemented | 运行时语言门禁（completion-time language gate，方案 B 正式化） | 2026-09-01 | `P45-RUNTIME-LANGUAGE-GATE.md` |
| Proposed | tr5 发布债收口 + review/verify 验证标记检查 | 2026-09-01 | `P46-TR5-DEBT-VALIDATION-MARKER.md` |
| Implemented | develop 前置处理规则与产物目录约定 | 2026-09-02 | `P47-WORKFLOW-PRECONDITIONS-OUTPUTS.md` |
| Implemented | Skill Size Reconciliation | 2026-08-01 | `P6-SKILL-SIZE-PROPOSAL.md` |
| Implemented | `aic-workflow` Authoring Command | 2026-08-05 | `P7-WORKFLOW-AUTHOR-COMMAND.md` |
| Implemented | `aic-command` Authoring Command | 2026-08-05 | `P8-COMMAND-AUTHOR.md` |
| Implemented | `aic-skill-launch` Skill Launcher | 2026-08-05 | `P9-SKILL-LAUNCHER.md` |

## 当前遗留（未关闭）

由 `python tools/proposal-audit.py` 生成：

<!-- proposal-audit 结果会在此区更新；不要手工维护本段 -->
