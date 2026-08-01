# 依赖分析报告 / Dependency Report

- 目标 / Target: structure
- 范围 / Scope: governance
- 日期 / Date: 2026-08-01

---

## 一、依赖类型 / Dependency Types

1. 外部 → governance 引用（workflows/templates/loaders/tools 引用治理规则）
2. governance 内部引用（文件互引）
3. governance → 外部引用（RFC、tools 路径、产出物）

---

## 二、外部依赖 governance / Inbound References

### 2.1 运行时模板引用（templates/runtime/*.md）

| 被引用文档 | 引用次数 | 存在 |
|---|---|---|
| REFLECTION_RULES.md | 23 | ✅ |
| CONTEXT_LOADING.md | 23 | ✅ |
| SOURCE_OF_TRUTH.md | 15 | ✅ |
| REPOSITORY_FIRST.md | 12 | ✅ |
| AI_OPERATING_RULES.md | 12 | ✅ |
| standards/common/task-quality-checklist.md | 8 | ✅ |
| standards/cool/rpc-conventions.md | 4 | ✅ |
| standards/common/cross-project-sync.md | 4 | ✅ |
| standards/cool/rocketmq-conventions.md | 2 | ✅ |
| policies/quality-gates.md | 2 | ✅ |
| standards/cool/enum-naming.md | 1 | ✅ |
| standards/cool/enum-dml.md | 1 | ✅ |
| standards/common/clean-code.md | 1 | ✅ |

**结论：14 个运行时引用全部有效。** 高频依赖：REFLECTION_RULES、CONTEXT_LOADING、SOURCE_OF_TRUTH（横切所有 Runtime）。

### 2.2 loaders/standards-loader.md 引用

| 被引用文档 | 状态 |
|---|---|
| AI_OPERATING_RULES.md / SOURCE_OF_TRUTH.md / CONTEXT_LOADING.md / REPOSITORY_FIRST.md / REFLECTION_RULES.md / LANGUAGE_CONVENTION.md | ✅ |
| standards/common/ai-coding-rules.md / clean-code.md / copy-review.md / cross-project-sync.md / documentation.md / review-checklist.md / task-quality-checklist.md / testing.md / chinese-documentation.md | ✅ |
| standards/cool/{enum-dml,enum-naming,i18n}.md | ✅ |
| standards/java/java-alibaba.md | ✅ |
| **api/rest.md / database/sql.md / go/go-style.md / java/mybatis.md / java/spring.md / mq/rocketmq.md / python/pep8.md** | ❌ 不存在 |
| **common/code-quality.md** | ❌ 已归档 |

### 2.3 README.md / OPERATIONS.md 引用

- README.md 引用 `standards/common/code-quality.md` → ❌ 已归档（F6）
- OPERATIONS.md 引用 AI_OPERATING_RULES.md、repo-lint.md → ✅

---

## 三、governance 内部依赖 / Internal References

| 源文件 | 目标 | 状态 |
|---|---|---|
| routing-policy.md | review-standard.md | ✅ |
| routing-policy.md | scripts/repo-lint.py、scripts/repo-metrics.py | ❌ 路径失效（F4） |
| skill-policy.md | RFC-0001、RFC-0002、review-standard.md | ✅（跨目录） |
| skill-policy.md | tools/repo-lint.py 等 | ✅ |
| quality-gates.md | scripts/repo-lint.py | ❌ 路径失效（F4） |
| review-standard.md | scripts/repo-lint.py | ❌ 路径失效（F4） |
| MEMORY_GUIDELINES.md | standards/documentation.md | ⚠️ 说明性引用，实际为 standards/common/documentation.md |
| archive/standards/common/code-quality.md | task-quality-checklist.md、clean-code.md | ✅（active 替代品存在） |

---

## 四、循环依赖检测 / Circular Dependency

- governance 文档层：无循环引用（单向：规则 → 工具）
- 外部层 → governance：单向依赖，无回边
- **结论：无循环依赖。**

---

## 五、悬空引用汇总 / Dangling References

| 类型 | 引用 | 缺失目标 |
|---|---|---|
| 路径失效 | scripts/repo-lint.py ×3 文件 | tools/ 实为正确位置 |
| 已归档未清理 | README.md、standards-loader.md → common/code-quality.md | archive/standards/common/ |
| 扩展预留位 | standards-loader → 6 个语言/框架标准 | 从未创建，未标注为预留 |
| 索引悬空 | memory/coding-memory.md → python/、integration/ | 目录不存在 |

---

## 六、结论 / Summary

依赖结构主体健康：外部层引用治理规则的链路全部有效（运行时引用 100% 命中）。问题集中于**已失效的路径**（scripts/ 前缀）与**迁移残留**（归档后引用未清理、预留位未标注）。
