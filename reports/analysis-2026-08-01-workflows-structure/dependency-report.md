# 依赖分析报告 / Dependency Report

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-01

---

## 一、依赖类型 / Dependency Types

工作流层存在三类依赖：

1. 运行时依赖（workflow → runtime template）
2. 配置依赖（registry → config/workflows/*.yaml → workflow.md + runtime）
3. 链路依赖（workflow → workflow，通过 Next / Preconditions）

---

## 二、运行时依赖 / Runtime Dependencies

| 工作流 | 运行时模板 | 存在 |
|---|---|---|
| bootstrap | templates/runtime/runtime-bootstrap.md | ✅ |
| prepare | templates/runtime/runtime-prepare.md | ✅ |
| spec | templates/runtime/runtime-spec.md | ✅ |
| dev-setup | templates/runtime/runtime-dev-setup.md | ✅ |
| develop | templates/runtime/runtime-develop.md | ✅ |
| review | templates/runtime/runtime-review.md | ✅ |
| verify | templates/runtime/runtime-verify.md | ✅ |
| release | templates/runtime/runtime-release.md | ✅ |
| bugfix | templates/runtime/runtime-bugfix.md | ✅ |
| analysis | templates/runtime/runtime-analysis.md | ✅ |
| knowledge | templates/runtime/runtime-knowledge.md | ✅ |

**结论：11/11 运行时引用有效，全部存在且 Extends runtime-base.md。**

---

## 三、配置依赖 / Configuration Dependencies

### 3.1 注册表完整性

`config/workflow-registry.yaml` 注册全部 11 个工作流，映射到 `config/workflows/*.yaml`，全部 11 个配置存在。

| 注册表键 | 配置路径 | workflow 路径 | runtime 路径 |
|---|---|---|---|
| bootstrap | config/workflows/bootstrap.yaml | workflows/bootstrap.md | templates/runtime/runtime-bootstrap.md |
| prepare | config/workflows/prepare.yaml | workflows/prepare.md | templates/runtime/runtime-prepare.md |
| spec | config/workflows/spec.yaml | workflows/spec.md | templates/runtime/runtime-spec.md |
| dev-setup | config/workflows/dev-setup.yaml | workflows/dev-setup.md | templates/runtime/runtime-dev-setup.md |
| develop | config/workflows/develop.yaml | workflows/develop.md | templates/runtime/runtime-develop.md |
| review | config/workflows/review.yaml | workflows/review.md | templates/runtime/runtime-review.md |
| verify | config/workflows/verify.yaml | workflows/verify.md | templates/runtime/runtime-verify.md |
| release | config/workflows/release.yaml | workflows/release.md | templates/runtime/runtime-release.md |
| bugfix | config/workflows/bugfix.yaml | workflows/bugfix.md | templates/runtime/runtime-bugfix.md |
| analysis | config/workflows/analysis.yaml | workflows/analysis.md | templates/runtime/runtime-analysis.md |
| knowledge | config/workflows/knowledge.yaml | workflows/knowledge.md | templates/runtime/runtime-knowledge.md |

**结论：注册表 ↔ 配置 ↔ 工作流 ↔ 运行时 四方一一对应，无缺失、无悬空引用。**

### 3.2 提示构建链路

`cli/services/prompt_builder.py` 读取 registry → 配置 → workflow.md + runtime.md → 渲染 `templates/prompts/workflow.md`。链路闭合，`tools/check.py` 的 prompt build 冒烟测试 PASS。

---

## 四、链路依赖 / Workflow-to-Workflow Dependencies

### 4.1 Next 转移图

```text
bootstrap   → prepare | any workflow requiring Environment Context
prepare     → spec (On Ready)
spec        → dev-setup (On Ready)
dev-setup   → develop
develop     → review
review      → verify (On Approved) | develop (Changes Required)
verify      → release (On PASS) | develop (FAIL)
release     → deployment (external) | develop (BLOCKED)
bugfix      → review
analysis    → knowledge (collect findings)
knowledge   → None
```

### 4.2 依赖矩阵

| 工作流 | 上游依赖（Preconditions） | 下游（Next） |
|---|---|---|
| bootstrap | 无（入口） | prepare |
| prepare | Bootstrap | spec |
| spec | Prepare | dev-setup |
| dev-setup | Bootstrap + spec (Task Card) | develop |
| develop | Dev Setup | review |
| review | develop / bugfix | verify / develop |
| verify | review | release / develop |
| release | verify (all tasks PASS) | deployment / develop |
| bugfix | Dev Setup | review |
| analysis | 无 | knowledge |
| knowledge | 无 | None |

---

## 五、循环依赖检测 / Circular Dependency Detection

### 5.1 结构环

按 Next 直接转移构建有向图，静态环检测：

- 主链无环（bootstrap→…→release 线性）
- 存在条件回边：review→develop、verify→develop、release→develop

这三个回边均为**有条件的失败/返工回路**（Changes Required / FAIL / BLOCKED），并非无条件循环。在图论上是环，但在执行语义上是受退出准则约束的返工通道，符合设计意图（WORKFLOW-OPTIMIZATION-REPORT-2026-07 五：链路闭合通过）。

### 5.2 运行时依赖环

所有运行时 Extends runtime-base.md，运行时之间无相互依赖，无环。

### 5.3 结论

无病态循环依赖。3 个条件回边是有意为之的返工闸门，应保留并继续由 Exit Criteria 显式约束。

---

## 六、悬空引用 / Dangling References

| 检查 | 结果 |
|---|---|
| 所有工作流 Next 目标 | 存在或显式 external/None |
| review.md 引用 review-changes 技能 | ✅ skills/review-changes/SKILL.md 存在 |
| analysis.md 引用 knowledge 工作流 | ✅ workflows/knowledge.md 存在 |
| workflows/README.md 主链 | ✅ 全部目标存在 |

无悬空引用。
