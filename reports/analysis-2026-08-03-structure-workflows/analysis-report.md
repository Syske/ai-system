# 结构分析报告 / Structure Analysis Report

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-03

---

## 一、范围界定 / Scope

本次分析仅覆盖 AI System 中 `workflows/` 工作流层及其直接关联物：

- `workflows/*.md`（11 个工作流入口文件 + README）
- `config/workflows/*.yaml`（11 个工作流配置）
- `config/workflow-registry.yaml`（工作流注册表）
- `templates/runtime/runtime-*.md`（每个工作流引用的运行时模板）
- `templates/prompts/workflow.md`、`workflow-trigger.md`（工作流提示模板）
- `cli/services/wizard.py`、`workflow_reader.py`（向导路由与工作流元数据读取）
- `config/menu.yaml`（工作流菜单分组）
- `governance/` 中约束工作流结构的标准（repo-lint.md、AI_OPERATING_RULES.md、SOURCE_OF_TRUTH.md、CONTEXT_LOADING.md、LANGUAGE_CONVENTION.md）
- 既有上下文：`reports/analysis-2026-08-01-workflows-structure/`、`reports/WORKFLOW-OPTIMIZATION-REPORT-2026-07.md`、`archived/ARCHIVE.md`

不包含：skills/、cli/ 命令实现、tool 代码逻辑、governance/ 内部细节。

---

## 二、目录结构 / Directory Structure

### 2.1 工作流目录布局（当前）

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
└── templates/
    ├── prompts/
    │   ├── workflow.md                 # 工作流提示模板（{{workflow_definition}} + {{runtime_definition}}）
    │   └── workflow-trigger.md         # 工作流调用模板
    └── runtime/
        ├── runtime-base.md             # 运行时基类契约
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

### 2.2 与 2026-08-01 分析相比的结构变化

| 项 | 2026-08-01 | 2026-08-03（当前） |
|---|---|---|
| `routing/ai-routing.yaml` | 活跃层，覆盖 11 工作流 + 3 别名 | **已归档至 `archived/routing/`**，无活跃路由表 |
| 路由机制 | 静态路由表 | **向导运行时解析**：`cli/services/wizard.py` 解析工作流 `## Next` 段 + menu.yaml `command_next`（ARCHIVE.md 2026-08-01 记录） |
| `governance/policies/routing-policy.md` | 重写为真实路由策略 | **已删除**（commit 54d36e5，判定冗余） |

结构演进方向：路由表（重复注册表信息）→ 向导从工作流 `## Next` 单一来源派生推荐。符合"单一来源"原则。

---

## 三、工作流分类 / Workflow Classification

### 3.1 按角色分类

| 角色 | 工作流 | 数量 |
|---|---|---|
| 主链 | prepare, spec, dev-setup, develop, review, verify, release | 7 |
| 冷启动 | bootstrap | 1 |
| 分支链 | bugfix | 1 |
| 独立 | analysis, knowledge | 2 |

### 3.2 按状态分类

| 状态 | 工作流 |
|---|---|
| 入口 | bootstrap（冷启动）/ bugfix（分支入口）/ analysis、knowledge（独立） |
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

校验结果：全部 11 个运行时模板均引用 runtime-base.md，层级扁平、无中间抽象、无相互依赖。

---

## 五、工作流关系 / Workflow Relationships

### 5.1 主链

```text
prepare → spec → dev-setup → develop → review → verify → release
```

（bootstrap 为一次性冷启动入口，指向 prepare。）

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
| 模块化 | 高 | 工作流契约、配置、运行时分层清晰，职责单一 |
| 可维护性 | 高 | 单文件 <75 行，八段结构统一；注册表驱动新增 |
| 可复用性 | 高 | 配置最小化（3 字段）；运行时独立于工作流复用 |
| 可扩展性 | 高 | 新增工作流 = 注册表 + 配置 + .md + 菜单条目，无需运行时改动 |
| 一致性 | 高 | 11/11 工作流八段齐全；11/11 运行时引用有效；`tools/check.py` PASS |

---

## 七、主要发现 / Key Findings

### F1（引用完整性 - 内存陈旧引用）
`governance/memory/ai-system/file-contract.md` 的 Solution 仍指引"Rewrite `routing-policy.md` as the real routing policy"，但 `governance/policies/routing-policy.md` 已在 commit 54d36e5（2026-08-01）删除，`routing/` 亦已归档。记忆中的指引指向已不存在的文件，属陈旧引用。

### F2（归档记录与当前不一致）
`archived/ARCHIVE.md`（2026-08-01 Routing & Frameworks Archival）第 51/66 行仍记录"routing-policy.md 现描述 wizard-driven routing"。该文件随后被删除。归档记录描述了一个被取代的中间状态。

### F3（路由机制演进，正向）
向导路由（`cli/services/wizard.py` 解析工作流 `## Next`）已取代静态路由表。`tools/check.py` 校验通过，无悬空引用。路由与工作流定义耦合于单一来源（workflow `## Next` 段），符合 SOURCE_OF_TRUTH。

### F4（上一轮发现处置确认）
上轮（2026-08-01）F1 review.md 额外章节、F2 分析产物落盘、F4/F5 主链口径 均已处置，本次复核确认全部已解决：

- review.md `When to Use` 已由 README 模板显式允许为可选章节（位于 Purpose 之后）
- analysis.md Outputs 已声明落盘目录 `reports/analysis-{date}-{target}-{scope}/`
- 主链口径统一为两段式：bootstrap=冷启动，变更主链从 prepare 起算；README / menu.yaml / OPERATIONS.md §1.2 一致

---

## 八、总结 / Summary

工作流层结构整体健康，且相较 2026-08-01 有两点结构性改善：

- 路由层冗余（ai-routing.yaml 与注册表重复）被移除，路由职责回归工作流 `## Next` 单一来源
- 上轮发现 F1/F2/F4/F5 全部落实

本轮的轻微问题集中在**引用/归档记录的陈旧**：F1 内存文件仍指引已删除的 routing-policy.md，F2 归档记录描述的是已被删除的中间状态。均不影响执行正确性，属于文档与记忆同步问题。
