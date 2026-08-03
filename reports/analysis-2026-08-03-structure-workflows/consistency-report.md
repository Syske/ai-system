# 一致性报告 / Consistency Report

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-03

---

## 一、验证链 / Verification Chain

按 runtime-analysis 的 Phase 4 链路执行：

```text
Workflow → Runtime → Skills → Framework → Templates
```

本次范围为 workflows，重点验证 Workflow ↔ Runtime ↔ Templates 三层，并对跨层引用（向导路由、菜单、注册表）做抽查。

---

## 二、模板一致性 / Template Conformance

### 2.1 八段模板（workflows/README.md §Workflow Template）

要求：每个工作流文件恰好包含、按序包含：Purpose → Runtime → Preconditions → Inputs → Context → Outputs → Exit Criteria → Next。可选章节（When to Use 等）仅允许置于 Purpose 之后。

| 工作流 | 八段齐全 | 顺序正确 | 额外章节 | 合规 |
|---|---|---|---|---|
| bootstrap.md | ✅ | ✅ | 无 | ✅ |
| prepare.md | ✅ | ✅ | 无 | ✅ |
| spec.md | ✅ | ✅ | 无 | ✅ |
| dev-setup.md | ✅ | ✅ | 无 | ✅ |
| develop.md | ✅ | ✅ | 无 | ✅ |
| review.md | ✅ | ✅ | `When to Use`（可选，模板已允许） | ✅ |
| verify.md | ✅ | ✅ | 无 | ✅ |
| release.md | ✅ | ✅ | 无 | ✅ |
| bugfix.md | ✅ | ✅ | 无 | ✅ |
| analysis.md | ✅ | ✅ | 无 | ✅ |
| knowledge.md | ✅ | ✅ | 无 | ✅ |

**结论：11/11 完全合规。**

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
| 工作流定义（AI 控制流）使用英文 | ✅ workflows/*.md 中 CJK 残留 = 0 |
| 运行时控制流指令使用英文 | ✅ |
| 运行时内嵌用户报告/交互提示模板使用中文 | ✅ 允许（runtime-release.md、runtime-review.md 的报告块与双语决策表） |
| 用户报告使用中文 | ✅ 本套报告中文 + 双语标题 |

---

## 四、跨层引用一致性 / Cross-Layer Reference Consistency

### 4.1 Workflow → Runtime

| 检查 | 结果 |
|---|---|
| 11/11 工作流声明的运行时模板存在 | ✅ |
| 运行时模板 Extends runtime-base.md | ✅ 11/11 |

### 4.2 Workflow → Skills（抽查）

| 引用 | 目标 | 结果 |
|---|---|---|
| review.md → review-changes | skills/review-changes/SKILL.md | ✅ 存在 |

### 4.3 Workflow → Templates / 向导

| 引用 | 目标 | 结果 |
|---|---|---|
| prompt_builder.py → templates/prompts/workflow.md | ✅ | |
| wizard.py `_parse_next` → workflows/*.md `## Next` 段 | ✅ 所有解析目标存在 | |
| 分析运行时声明输出 4 报告 | ✅ 本目录生成 | |

### 4.4 Workflow → Registry / Menu

| 层 | 注册数 | 一致性 |
|---|---|---|
| config/workflow-registry.yaml | 11 | ✅ |
| config/menu.yaml sections（kind: workflow） | 11（主链 7 + bugfix 1 + 能力 3） | ✅ 全部注册 |

---

## 五、治理一致性 / Governance Consistency

### 5.1 上下文加载（CONTEXT_LOADING.md）

所有 11 个工作流的 Context 段均声明"最小加载集"并显式禁止全仓加载（"Never load the entire repository tree"），符合 CONTEXT_LOADING 原则。✅

### 5.2 变更控制（AI_OPERATING_RULES.md）

- develop.md 的 Exit Criteria 显式引用 L2/L3 变更控制 ✅
- review.md / verify.md 失败回路均指向 develop（不新增任务卡片）✅

### 5.3 主链口径一致性

| 文档 | 主链定义 | 一致 |
|---|---|---|
| workflows/README.md | 冷启动 bootstrap + 变更主链 prepare→…→release | ✅ |
| config/menu.yaml | flow_main 编号 prepare(1)…release(7)；bootstrap 归系统能力 | ✅ |
| OPERATIONS.md §1.2 | 主链拓扑以 workflows/README.md 为唯一来源 | ✅ |

**结论：三处口径统一，上轮 F4/F5 已解决。**

---

## 六、验证结果汇总 / Summary

| 检查项 | 结果 |
|---|---|
| 八段模板合规 | 11/11 合规 |
| 命名一致性 | ✅ |
| 引用完整性（registry/config/workflow/runtime） | ✅ 11/11 |
| 菜单覆盖 | ✅ 全部注册 |
| 运行时基类统一 | ✅ |
| 上下文最小化 | ✅ |
| 主链口径 | ✅ 统一（bootstrap=冷启动，变更主链从 prepare 起算） |
| 语言边界 | ✅ 控制流英文、用户模板中文 |
| 系统完整性门禁 `python tools/check.py` | PASS（0 warnings） |
| 命名门禁 `python tools/repo-lint.py` | 0 BLOCKER / 0 ERROR / 9 WARNING（均为 skills 层，不在本次 scope） |
