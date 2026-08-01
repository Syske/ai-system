# 结构分析报告 / Structure Analysis Report

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-01

---

## 一、范围界定 / Scope

本次分析仅覆盖 AI System 中 `workflows/` 工作流层及其直接关联物：

- `workflows/*.md`（11 个工作流入口文件 + README）
- `config/workflows/*.yaml`（11 个工作流配置）
- `config/workflow-registry.yaml`（工作流注册表）
- `templates/runtime/runtime-*.md`（每个工作流引用的运行时模板）
- `templates/prompts/workflow.md`、`workflow-trigger.md`（工作流提示模板）
- `routing/ai-routing.yaml`（工作流路由）
- `config/menu.yaml`（工作流菜单分组）
- `governance/` 中约束工作流结构的标准（repo-lint.md、AI_OPERATING_RULES.md、SOURCE_OF_TRUTH.md、CONTEXT_LOADING.md、LANGUAGE_CONVENTION.md）
- `OPERATIONS.md`、`reports/WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` 作为既有上下文

不包含：skills/、frameworks/、cli/ 命令实现、tool 代码逻辑。

---

## 二、目录结构 / Directory Structure

### 2.1 工作流目录布局

```text
ai-system/
├── workflows/                          # 工作流入口契约（markdown）
│   ├── README.md                       # 选择表、主链、术语、模板规范
│   ├── bootstrap.md
│   ├── prepare.md
│   ├── spec.md
│   ├── dev-setup.md
│   ├── develop.md
│   ├── review.md
│   ├── verify.md
│   ├── release.md
│   ├── bugfix.md
│   ├── analysis.md
│   └── knowledge.md
├── config/
│   ├── workflow-registry.yaml          # 工作流注册表（名称 → 配置路径）
│   └── workflows/                      # 工作流配置（每个 .md 对应一个 .yaml）
│       ├── bootstrap.yaml
│       ├── prepare.yaml
│       ├── spec.yaml
│       ├── dev-setup.yaml
│       ├── develop.yaml
│       ├── review.yaml
│       ├── verify.yaml
│       ├── release.yaml
│       ├── bugfix.yaml
│       ├── analysis.yaml
│       └── knowledge.yaml
├── templates/
│   ├── prompts/
│   │   ├── workflow.md                 # 工作流提示模板（{{workflow_definition}} + {{runtime_definition}}）
│   │   └── workflow-trigger.md         # 工作流调用模板
│   └── runtime/
│       ├── runtime-base.md             # 运行时基类契约
│       ├── runtime-bootstrap.md
│       ├── runtime-prepare.md
│       ├── runtime-spec.md
│       ├── runtime-dev-setup.md
│       ├── runtime-develop.md
│       ├── runtime-review.md
│       ├── runtime-verify.md
│       ├── runtime-release.md
│       ├── runtime-bugfix.md
│       ├── runtime-analysis.md
│       └── runtime-knowledge.md
└── routing/
    └── ai-routing.yaml                 # 意图 → 工作流路由
```

### 2.2 布局模式总结

| 层 | 位置 | 内容 |
|---|---|---|
| 工作流契约 | `workflows/<name>.md` | 八段结构（Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next） |
| 工作流配置 | `config/workflows/<name>.yaml` | 最小配置：name + workflow 路径 + runtime 路径 |
| 注册表 | `config/workflow-registry.yaml` | 11 个工作流全部注册 |
| 运行时 | `templates/runtime/runtime-<name>.md` | 执行生命周期 |
| 路由 | `routing/ai-routing.yaml` | 意图 → 工作流映射 |

命名规则符合 `governance/repo-lint.md`：kebab-case，单文件 `<name>.md`。

---

## 三、工作流分类 / Workflow Classification

### 3.1 按角色分类

| 角色 | 工作流 | 数量 |
|---|---|---|
| 主链 | bootstrap, prepare, spec, dev-setup, develop, review, verify, release | 8 |
| 分支链 | bugfix | 1 |
| 独立 | analysis, knowledge | 2 |

### 3.2 按状态分类

| 状态 | 工作流 |
|---|---|
| 入口 | bootstrap（主链）/ bugfix（分支入口）/ analysis、knowledge（独立） |
| 中间 | prepare, spec, dev-setup, develop |
| 闸门 | review, verify |
| 出口 | release（→ 部署，外部） |
| 终端 | knowledge（Next: None） |

---

## 四、运行时层级 / Runtime Hierarchy

```text
runtime-base.md (契约)
   ├── runtime-bootstrap.md
   ├── runtime-prepare.md
   ├── runtime-spec.md
   ├── runtime-dev-setup.md
   ├── runtime-develop.md
   ├── runtime-review.md
   ├── runtime-verify.md
   ├── runtime-release.md
   ├── runtime-bugfix.md
   ├── runtime-analysis.md
   └── runtime-knowledge.md
```

所有 11 个运行时模板均声明 `Extends: runtime-base.md`（经 WORKFLOW-OPTIMIZATION-REPORT-2026-07 R1 修复后一致），层级扁平、无中间抽象。

---

## 五、工作流关系 / Workflow Relationships

### 5.1 主链

```text
bootstrap → prepare → spec → dev-setup → develop → review → verify → release
```

### 5.2 条件回路

```text
review: Changes Required → develop
verify: FAIL → develop
release: BLOCKED (Branch Diff Review) → develop
develop: L3 → suspend → prepare(scoped) → spec → resume develop
```

### 5.3 分支与独立

```text
bugfix → review → verify
analysis → knowledge（收集可复用发现）
```

---

## 六、质量评估 / Quality Assessment

| 维度 | 评分 | 说明 |
|---|---|---|
| 模块化 | 高 | 工作流契约、配置、运行时、路由分层清晰，职责单一 |
| 可维护性 | 高 | 单文件 <70 行，八段结构统一；注册表驱动新增 |
| 可复用性 | 高 | 配置最小化（3 字段）；运行时独立于工作流复用 |
| 可扩展性 | 高 | 新增工作流 = 3 个文件 + 注册表 + 菜单，无运行时改动（OPERATIONS.md §1.10.1） |
| 一致性 | 高 | 11/11 工作流八段齐全；11/11 运行时引用有效；`tools/check.py` PASS |

---

## 七、主要发现 / Key Findings

### F1（结构规范偏离）
`workflows/review.md` 包含标准八段之外的第 2 节 `## When to Use`（review-changes skill 使用场景），违反 `workflows/README.md` 第 83 行 "必须恰好包含这些章节、按此顺序" 的契约。属于可辩护的例外（区分 review 工作流与 review-changes 技能），但需在模板规范中显式允许或移入 review 技能。

> 处置：已在 `workflows/README.md` §Workflow Template 显式允许可选章节 `When to Use`，F1 视为已解决。

### F2（命名规范偏离）
`config/workflows/*.yaml` 中的 `analysis.yaml` 引用 `workflows/analysis.md` 与 `runtime-analysis.md`，与 AI_OPERATING_RULES.md 中分析类运行时的存在保持一致，但分析运行时的输出（4 份报告）未指明存放目录。结构上缺少"分析产物落盘位置"约定。

> 处置：已在 `workflows/analysis.md` Outputs 补充落盘约定 `reports/analysis-{date}-{target}-{scope}/`，F2 视为已解决。

### F3（路由覆盖完整）
`routing/ai-routing.yaml` 覆盖全部 11 个工作流，且提供 3 个别名（implement→develop、openspec→spec、debug→bugfix），路由层与工作流层命名一致。

### F4（菜单分组与主链不一致）
`config/menu.yaml` 中主链分组为 prepare(1)→spec(2)→dev-setup(3)→develop(4)→review(5)→verify(6)→release(7)，**不含 bootstrap**；而 `workflows/README.md` 主链图以 `bootstrap` 起始。bootstrap 被归入"系统能力"分组。两处对主链的定义不一致，可能造成使用方对入口的理解分歧。

> 处置：`workflows/README.md` 主链已改为"冷启动 bootstrap + 变更主链 prepare→…→release"两段式，与 menu.yaml、OPERATIONS.md 口径统一，F4 视为已解决。

### F5（术语：主链命名）
README.md 主链写 `bootstrap → prepare → ...`，而 OPERATIONS.md §1.2 写 `prepare → spec → dev-setup → develop → review → verify → release`（不含 bootstrap，视为一次性冷启动）。术语表将 bootstrap 视为环境准备而非变更生命周期步骤。建议统一口径。

> 处置：随 F4 一并统一为两段式口径，F5 视为已解决。

---

## 八、总结 / Summary

工作流层结构整体健康：

- 11 个工作流契约完整、模板统一、引用有效
- 注册表 / 配置 / 路由 / 菜单四方一致
- 分层（契约 / 配置 / 运行时 / 路由）职责清晰，符合 SOURCE_OF_TRUTH 层级

主要结构问题是三处轻微的口径不一致（F1 review.md 额外章节、F4/F5 bootstrap 在主链中的位置），均不影响执行正确性，属于文档一致性问题。
