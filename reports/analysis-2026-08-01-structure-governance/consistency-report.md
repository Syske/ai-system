# 一致性报告 / Consistency Report

- 目标 / Target: structure
- 范围 / Scope: governance
- 日期 / Date: 2026-08-01

---

## 一、验证链 / Verification Chain

按 runtime-analysis Phase 4：

```text
Workflow → Runtime → Skills → Framework → Templates
```

本次聚焦 governance 层内部的**文件名-内容一致性**、**索引-实际一致性**、**引用-目标一致性**。

---

## 二、文件名与内容一致性 / Filename ↔ Content

| 文件 | 内容主题（首行标题） | README 描述 | 一致 |
|---|---|---|---|
| AI_OPERATING_RULES.md | AI Operating Rules | Global AI behavior rules | ✅ |
| SOURCE_OF_TRUTH.md | Single Source of Truth | Authoritative priority hierarchy | ✅ |
| CONTEXT_LOADING.md | Context Loading Strategy | Minimal context loading | ✅ |
| REPOSITORY_FIRST.md | Repository First | Search-before-create | ✅ |
| REFLECTION_RULES.md | Reflection Rules | Mandatory reflection | ✅ |
| LANGUAGE_CONVENTION.md | Language Convention | English flow / Chinese reports | ✅ |
| karpathy-guidelines.md | Karpathy Guidelines | Coding guidelines | ✅ |
| repo-lint.md | Naming Conventions | Structural naming rules | ✅ |
| review-standard.md | Skill Review Process | Skill review workflow | ✅ |
| **violation-rules.md** | **Repository Governance** | **Violation severity classification** | ❌ F2 |
| **policies/routing-policy.md** | **Skill Lifecycle** | **Routing configuration rules** | ❌ F1 |
| policies/skill-policy.md | Contribution Guide | Skill creation/lifecycle | ⚠️ 内容偏贡献指南 |
| policies/security-policy.md | Security Policy (占位符) | Security practices | ⚠️ F3 未完成 |
| policies/quality-gates.md | Quality Gates | BLOCKER/ERROR/WARNING/INFO | ✅ |

**核心规则 8 个 + 工具类 3 个全部一致；3 处异常（F1/F2/F3）集中于 policies/ 与迁移残留文件。**

---

## 三、索引与实际一致性 / Index ↔ Reality

### 3.1 governance/README.md

| 检查 | 结果 |
|---|---|
| 列出的 14 个文件全部存在 | ✅ |
| routing-policy.md 描述 "Routing configuration rules" | ❌ 与实际内容（Skill Lifecycle）不符 |
| violation-rules.md 描述 "Violation severity classification" | ❌ 与实际内容（Repository Governance）不符 |

### 3.2 根 README.md

| 检查 | 结果 |
|---|---|
| 引用 governance/standards/common/code-quality.md | ❌ 已归档（F6） |
| routing-policy.md / violation-rules.md 描述 | ❌ 与内容不符 |

### 3.3 memory/coding-memory.md 索引

| 类别 | 目录存在 |
|---|---|
| Java → governance/memory/java/ | ✅ |
| Python → governance/memory/python/ | ❌ F7 |
| Integration → governance/memory/integration/ | ❌ F7 |
| AI System → governance/memory/ai-system/ | ✅ |

---

## 四、语言约定一致性 / Language Convention

LANGUAGE_CONVENTION 要求 governance 层（Rules/standards/policies）MUST 英文：

| 文件 | CJK 情况 | 判定 |
|---|---|---|
| archive/* (4 文件) | 15-58 行中文 | ✅ 已归档历史文档 |
| standards/common/chinese-documentation.md | 42 行中文 | ✅ 本身是中文写作规范 |
| standards/common/documentation.md | 3 行示例 | ✅ 说明性示例 |
| LANGUAGE_CONVENTION.md | 3 行双语标题 | ✅ Hybrid 合法示例 |
| standards/cool/i18n.md | 1 行配置示例 | ✅ 示例文本 |
| **其余 active 文件** | 0 CJK | ✅ |

**结论：语言约定良好，无违规。**

---

## 五、跨层一致性 / Cross-Layer Consistency

| 检查 | 结果 |
|---|---|
| 运行时模板引用 governance 文档 | ✅ 14/14 有效 |
| governance 引用 RFC（skill-policy → RFC-0001/0002） | ✅ 存在 |
| governance 引用 tools 路径（scripts/） | ❌ F4 失效 |
| archive 中废弃标准 → 活跃替代 | ✅ code-quality.md → task-quality-checklist + clean-code |
| 活跃标准与归档标准是否重复 | ✅ archive 中文版、active 英文版，无重复 |

---

## 六、验证结果汇总 / Summary

| 检查项 | 结果 |
|---|---|
| 核心规则文件名-内容一致 | 8/8 ✅ |
| 索引文件存在性 | ✅ |
| policies/ 一致性 | ⚠️ F1/F2/F3 共 3 处 |
| 语言约定 | ✅ |
| 外部引用治理文档 | ✅ 100% 有效 |
| 工具路径引用 | ❌ scripts/ 失效 |
| memory 索引 | ⚠️ 悬空 2 类 |

**系统完整性门禁**：`python tools/check.py` → PASS（治理层问题未被门禁捕获，需专项修复）
