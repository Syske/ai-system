# AI System — AI 编码工作流编排引擎

> Orchestration framework：Workflows（决定做什么）→ Runtimes（执行怎么做）
> → Operating Rules（约束行为）→ Standards（定义质量）→ Skills（提供方法）。

面向 AI 编码工作流的编排引擎。系统把「做什么」与「怎么做」分离，由治理与质量门禁约束
每个环节，端到端驱动变更从 `prepare` 到 `release` 落地；并提供一个交互式 CLI（`aic`）
作为统一入口，配置驱动、支持国际化，方便扩展。

---

## 核心能力

- **交互式 CLI（`aic`）**：向导式选择项目 / 工作流 / 命令；字段带中文备注与 emoji、
  支持输入即过滤（fzf 风格）、多选、自由文本；菜单结构在 `config/menu.yaml`，文案在
  `config/i18n/{locale}.yaml`，新增命令 / 分组 / 改文案多为改配置不改代码。
- **工作流链**：`prepare → spec → dev-setup → develop → review → verify → release`，
  含 `bugfix` 并行分支与 `bootstrap` / `analysis` / `knowledge` 支撑工作流；主链拓扑唯一
  来源是 `workflows/README.md`。
- **命令体系**：`cli/commands/aic-*.md` 即插即用（`propose` / `apply` / `archive` /
  `explore` / `scan` / `trace` / `maintain` / `pack` / `skill-source` /
  `command` / `workflow` / `skill-launch` / `skill-optimize`，共 13 个），支持命令生命周期
  钩子（`command_hooks`）与动态字段候选（`providers`）。
- **治理优先**：`governance/` 定义质量门禁、命名规范、变更管理（`OPERATIONS.md`）；
  工作流 / 命令 / 技能均受 `repo-lint` 校验。
- **完整性门禁**：`tools/check.py` 校验编译、菜单 / 注册表引用、Next 段机读约定、
  命令可构建、向导可运行——维护后必跑；`tools/path-audit.py` 审计文档路径引用。
- **可维护架构**：wizard 已拆分（`menu_config` / `state_store` / `workflow_reader` /
  `command_hooks` / `providers`），字段、钩子、推荐逻辑各自独立，便于后续扩展与优化。

## 工作流链

```text
bootstrap → prepare → spec → dev-setup → develop → review → verify → release
                                              ↑ 变更 → develop
bugfix → review（并行分支）
analysis / knowledge（支撑：系统分析、知识沉淀）
```

条件跳转：`review`（Changes Required）→ `develop`；`verify`（FAIL）→ `develop`；
`release`（READY）→ deployment（系统外）。详见 `workflows/README.md`。

## 文档导航

| 文件 | 用途 | 维护 |
|---|---|---|
| `README.md` | 入口 / 概览（结构、快速命令） | 手动 |
| `OPERATIONS.md` | 运维手册 — 入口流程、lint/check 用法、菜单维护、工作流规则 | 手动 |
| `README_MIGRATION.md` | 迁移包清单（随打包副本发布） | **由 `tools/pack.py` 生成**，勿手动改 |

工作流链 / 选择表：唯一来源为 `workflows/README.md`（OPERATIONS 与本文档均引用，不重复维护）。

## 快速开始

```shell
pip install -e .          # 注册 aic 命令
aic                        # 交互式向导
python -m cli.main         # 或直接运行
```

```text
ai-system/
├── cli/          CLI（交互向导 + 命令生成），命令定义在 cli/commands/aic-*.md
├── config/       menu.yaml、workflow-registry、环境与 i18n 配置
├── governance/   质量门禁、生命周期、评审流程、命名规范
├── loaders/      按需加载策略（standards-loader）
├── rfc/          RFC 规范 + 架构决策记录（ADR）
├── skills/       Agent 技能（实现行为、决策逻辑、执行步骤）
├── templates/    Runtime / prompt / asset 模板
├── tools/        repo-lint、check、path-audit、pack、setup 等维护脚本
├── workflows/    工作流入口契约（README 含选择表）
├── reports/      生成的分析与维护报告
├── metrics/      健康指标快照（repo-metrics 输出）
├── logs/         运行日志
└── archived/     已归档资产（workflows/skills/templates 等）
```

## 常用命令

```shell
# 系统完整性门禁 — 修改后必跑
python tools/check.py

# 规范校验（命名 / 结构）
python tools/repo-lint.py --repo-root .

# 路径引用审计
python tools/path-audit.py

# 健康指标
python tools/repo-metrics.py --repo-root .

# 依赖图 / 迁移打包
python tools/dependency-graph.py --repo-root .
python tools/pack.py [--zip]
```

## 技术栈

| 项 | 说明 |
|---|---|
| 语言 | Python ≥ 3.10 |
| 交互 | `prompt_toolkit`（输入即过滤、多行编辑） |
| 配置 | `PyYAML`；`config/menu.yaml`（结构/key）+ `config/i18n/{locale}.yaml`（文案） |
| 模型 | Workflow（md 契约）→ Runtime（templates/runtime）→ Skill（skills/）分层 |

## 修改本仓库

1. **阅读 `governance/repo-lint.md`** — 了解命名规则与校验流程。
2. **遵循 `rfc/` 规范** — RFC-0001（架构）、RFC-0002（skill）、RFC-0003（workflow）、RFC-0004（playbook）。
3. **运行 `python tools/repo-lint.py --repo-root .` 与 `python tools/check.py`** —
   结构性改动前必须通过（BLOCKER / ERROR 清零）。
4. **改动架构时更新 `reports/`** 中的架构状态。
5. **保持工作区产物向后兼容**（`openspec/`、`.opencode/`、`.pi/`）——这些由平台管理，勿在此修改。

## 关键规则

| 规则 | 来源 |
|---|---|
| 每个 Skill 需含合法 YAML frontmatter 的 `skill.md` | RFC-0002 |
| Skill 单文件不得超过 1000 行 | RFC-0002 |
| Skill 的 Maven 执行必须委托 `java-maven` | ADR-0003 |
| Skill 不得重复共享 checklist / playbook 内容 | RFC-0002 |
| Workflow 只编排，不实现 | RFC-0003 |
| Playbook 只教育，不执行 | RFC-0004 |

## 目录索引

| 路径 | 内容 |
|---|---|
| `governance/standards/common/task-quality-checklist.md` | 任务级质量校验基线 |
| `governance/standards/common/ai-coding-rules.md` | AI 编码规则 |
| `governance/standards/common/clean-code.md` | 整洁代码约定 |
| `governance/review-standard.md` | Skill 评审流程与检查单 |
| `governance/repo-lint.md` | 全组件命名规则 |
| `governance/violation-rules.md` | 违规分级与严重度 |
| `governance/karpathy-guidelines.md` | LLM agent 编码指南 |
| `governance/AI_OPERATING_RULES.md` | 核心运行规则（所有工作流） |
| `governance/policies/quality-gates.md` | BLOCKER/ERROR/WARNING/INFO 质量定义 |
| `governance/policies/skill-policy.md` | Skill 创建与维护策略 |
| `governance/policies/skill-lifecycle.md` | Skill 生命周期阶段 |
| `governance/policies/security-policy.md` | 安全指南 |
| `rfc/RFC-0001-repository-architecture.md` | 组件定义与分层模型 |
| `rfc/RFC-0002-skill-specification.md` | 强制组件与质量门禁 |
| `rfc/RFC-0003-workflow-specification.md` | 编排规则与禁止项 |
| `rfc/RFC-0004-playbook-specification.md` | 知识层规范 |
| `rfc/ADR-0001-*.md` ~ `ADR-0007-*.md` | 架构决策记录 |
| `reports/WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` | 工作流优化分析 |
| `reports/ARCHITECTURE-ASSESSMENT-2026-07.md` | 完整架构评估 |
