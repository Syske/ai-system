# 一致性报告 / Consistency Report

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-01

---

## 一、验证链 / Verification Chain

按 runtime-analysis 的 Phase 4 链路执行：

```text
Workflow → Runtime → Skills → Framework → Templates
```

本次范围为 workflows，重点验证 Workflow ↔ Runtime ↔ Templates 三层，并对跨层引用做抽查。

---

## 二、模板一致性 / Template Conformance

### 2.1 八段模板（workflows/README.md §Workflow Template）

要求：每个工作流文件恰好包含、按序包含：Purpose → Runtime → Preconditions → Inputs → Context → Outputs → Exit Criteria → Next。

| 工作流 | Purpose | Runtime | Preconditions | Inputs | Context | Outputs | Exit Criteria | Next | 合规 |
|---|---|---|---|---|---|---|---|---|---|
| bootstrap.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| prepare.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| spec.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| dev-setup.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| develop.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| review.md | ✅ | ✅（`When to Use` 为可选章节，模板已允许） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| verify.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| release.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| bugfix.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| analysis.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| knowledge.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**结论：11/11 完全合规（review.md 的 `When to Use` 已由模板规范显式允许，F1 解决）。**

---

## 三、命名一致性 / Naming Consistency

### 3.1 命名规则对照（governance/repo-lint.md）

| 规则 | 期望 | 实际 | 结果 |
|---|---|---|---|
| Workflow 目录名 | kebab-case，单词优先 | 全部小写 kebab-case | ✅ |
| 文件命名 | `<name>.md` 小写 | 11/11 | ✅ |
| 配置文件名 | `config/workflows/<name>.yaml` | 11/11 与注册表一致 | ✅ |

### 3.2 语言约定（LANGUAGE_CONVENTION.md）

| 检查 | 结果 |
|---|---|
| 工作流定义（AI 控制流）使用英文 | ✅ 全部文件结构为英文 |
| 用户报告使用中文 | ✅ 本套报告中文 + 双语标题 |
| review.md / release.md 的 Next 中混合中英文括号（`（...）`） | ⚠️ 轻微：`release.md` Next 含中文括号注释 |

---

## 四、跨层引用一致性 / Cross-Layer Reference Consistency

### 4.1 Workflow → Runtime

| 检查 | 结果 |
|---|---|
| 11/11 工作流声明的运行时模板存在 | ✅ |
| 运行时模板 Extends runtime-base.md | ✅（R1 已修复，无 runtime-workspace 残留） |

### 4.2 Workflow → Skills（抽查）

| 引用 | 目标 | 结果 |
|---|---|---|
| review.md → review-changes | skills/review-changes/SKILL.md | ✅ 存在 |
| WORKFLOW-OPTIMIZATION 报告引用 workflow-architect / context-architect / design-review | skills/architecture/*/SKILL.md | ✅ 存在 |

### 4.3 Workflow → Templates

| 引用 | 目标 | 结果 |
|---|---|---|
| prompt_builder.py → templates/prompts/workflow.md | ✅ | |
| 分析运行时声明输出 4 报告 | ✅ 本目录生成 | |

### 4.4 Workflow → Routing / Menu

| 层 | 注册数 | 一致性 |
|---|---|---|
| config/workflow-registry.yaml | 11 | ✅ |
| routing/ai-routing.yaml | 11 + 3 别名 | ✅ 别名指向已存在工作流 |
| config/menu.yaml sections | 11 | ✅ 全部注册 |

---

## 五、治理一致性 / Governance Consistency

### 5.1 上下文加载（CONTEXT_LOADING.md）

所有 11 个工作流的 Context 段均声明"最小加载集"并显式禁止全仓加载（"Never load the entire repository tree"），符合 CONTEXT_LOADING 原则。✅

### 5.2 变更控制（AI_OPERATING_RULES.md）

- develop.md 的 Exit Criteria 显式引用 L2/L3 变更控制 ✅
- review.md / verify.md 失败回路均指向 develop（不新增任务卡片）✅

### 5.3 主链口径不一致（F4 / F5）

| 文档 | 主链定义 | 位置 |
|---|---|---|
| workflows/README.md | `bootstrap → prepare → spec → dev-setup → develop → review → verify → release` | 含 bootstrap |
| config/menu.yaml | prepare(1)…release(7)，bootstrap 归入系统能力 | 不含 bootstrap |
| OPERATIONS.md §1.2 | `prepare → spec → dev-setup → develop → review → verify → release` | 不含 bootstrap |

**结论：主链的起点存在两套口径。README 视 bootstrap 为主链入口，menu 与 OPERATIONS 视 bootstrap 为一次性冷启动、主链从 prepare 开始。此为一致性发现 F4/F5。**

> 处置（同窗口已应用）：`workflows/README.md` 已改为 `Entry & Main Chain` 两段式——bootstrap 为冷启动、变更主链从 prepare 起算。现在三处口径一致：README、menu.yaml、OPERATIONS.md §1.2 均以 prepare 为变更主链起点，bootstrap 为一次性入口。F4/F5 视为已解决。

---

## 六、验证结果汇总 / Summary

| 检查项 | 结果 |
|---|---|
| 八段模板合规 | 11/11 合规（`When to Use` 已列入可选章节） |
| 命名一致性 | ✅ |
| 引用完整性（registry/config/workflow/runtime） | ✅ 11/11 |
| 路由与菜单覆盖 | ✅ 全部注册 |
| 运行时基类统一 | ✅ |
| 上下文最小化 | ✅ |
| 主链口径 | ✅ 已统一（bootstrap=冷启动，变更主链从 prepare 起算） |
| 系统完整性门禁 `python tools/check.py` | PASS |
