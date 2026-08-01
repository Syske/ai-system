# 三方 Skill 参考价值评估报告

- 日期 / Date: 2026-08-01
- 来源 / Sources:
  - mattpocock/skills (https://github.com/mattpocock/skills) — 39 skills
  - obra/superpowers (https://github.com/obra/superpowers) — 14 skills
- 原则 / Principle: Evolution Principle（只基于真实缺口吸收，不预先引入推测性能力）

---

## 一、评估框架

按三类判定每个三方 skill 的参考价值：

1. **高价值** — 填补真实缺口，方法论可直接吸收
2. **中价值** — 方法论可借鉴，非直接复制
3. **低/无价值** — 平台特定 / 个人写作 / 已内化 / 依赖外部工具 / 已废弃

吸收方式：**以原生资产重写**（skill-policy），不复制三方文件。

---

## 二、mattpocock/skills 评估（39 skills）

### 已吸收（高价值 3 项）

| skill | 吸收到 | 内容 | Commit |
|---|---|---|---|
| grilling | skills/grilling/ + runtime-spec Phase 2.5 | 决策树压力测试访谈（设计决策） | 59e0040 |
| diagnosing-bugs | skills/bugfix/feedback-loop.md | 反馈回路第一性、最小化复现、可证伪假设、修复前回归测试 | 808125d |
| writing-great-skills | RFC-0002 + skill-author/design.md | invocation 设计（model vs user invoked） | 29da289 |
| codebase-design | design-review/vocabulary.md | 深模块词汇表（deletion test、test surface） | 29da289 |

### 已借鉴（中价值 4 项）

| skill | 借鉴到 | 内容 | Commit |
|---|---|---|---|
| to-tickets | task-splitter T3 | 垂直切片、blocking 边、expand-contract 宽重构 | c711940 |
| tdd | testing 标准 | Seams 概念、测试即规格、3 种 anti-pattern | c711940 |
| code-review | review/smell-baseline.md | Fowler 12 种坏味道基线 | c711940 |
| domain-modeling | rfc/README + grilling 2.5 | ADR 三条件、术语挑战纪律 | 13efd45 |

### 未吸收（低/无价值，含原因）

| 类别 | skill | 原因 |
|---|---|---|
| 平台特定 | git-guardrails-claude-code, setup-pre-commit, migrate-to-shoehorn, setup-ts-deep-modules | Claude/TypeScript 专属 |
| 个人写作 | edit-article, obsidian-vault, writing-beats/fragments/shape, teach, scaffold-exercises | 非本领域 |
| 已内化 | grill-me, grill-with-docs, batch-grill-me | grilling 变体，已吸收核心 |
| 依赖外部工具 | triage, to-spec, to-tickets, ask-matt, wayfinder | 依赖 issue tracker（我们无）；router 由菜单替代 |
| 已废弃 | design-an-interface, qa, request-refactor-plan, ubiquitous-language | deprecated |
| 工程方法论（非资产） | prototype, research, resolving-merge-conflicts | 通用纪律，非 ai-system 资产 |
| 部分适用 | to-spec（seam 决策）、wayfinder（fog vs ticket） | spec 由 methodology provider 生成；无 tracker |

---

## 三、superpowers 评估（14 skills）

### 已吸收（高价值 3 项）

| skill | 吸收到 | 内容 | Commit |
|---|---|---|---|
| verification-before-completion | AI_OPERATING_RULES Validation | 证据先行 gate function、禁止 should/probably 声称 | 236f2ba |
| writing-skills | skill-author/design.md | TDD-Driven Skill Authoring（压力场景先失败） | 236f2ba |
| systematic-debugging | bugfix/feedback-loop.md | Iron Law：无根因调查不得修复 | 236f2ba |

### 中价值（未吸收，待真实需求评估）

| skill | 借鉴点 | 未吸收原因 |
|---|---|---|
| brainstorming | HARD-GATE（未展示设计获批准不得实现）、2-3 方案权衡 | 与 spec Discovery/grilling 部分重叠；HARD-GATE 语义已在 workflow Preconditions 隐含 |
| subagent-driven-development | 每任务独立子代理 + 任务后评审 | 依赖平台子代理能力，与 develop 单任务卡架构不同 |
| dispatching-parallel-agents | 独立问题域并行子代理 | 依赖平台子代理能力 |
| requesting/receiving-code-review | 评审反馈"验证后实现"纪律 | 与 review 流程重叠，可后续并入 |
| test-driven-development | Iron Law（无失败测试不得写生产代码） | 已吸收 tdd 的 seam/anti-pattern；Iron Law 纪律性可后续强化 |

### 低价值（未吸收）

| skill | 原因 |
|---|---|
| executing-plans / finishing-a-development-branch / using-git-worktrees / using-superpowers | 平台特定（Claude/Codex），或架构差异 |

---

## 四、协同关系

- **mattpocock**：方法论型（教"怎么做"）→ feedback loop、seam、deep module
- **superpowers**：纪律型（约束"必须做什么"）→ Iron Law、evidence gate
- 两层互补：方法论提供做法，纪律提供强制约束，二者叠加在 ai-system 的
  skill（方法）与 governance（规则）两层

---

## 五、后续待办（不预先引入）

| 项 | 触发条件 |
|---|---|
| brainstorming HARD-GATE | 若出现"未设计即实现"的真实问题 |
| subagent-driven / parallel-agents | 平台子代理能力可稳定使用且需并行开发 |
| review 反馈纪律（requesting/receiving） | 若 review 反馈处理出现"盲从或盲目反对"问题 |
| Iron Law 强化 tdd | 若出现"无测试即写生产代码"违规 |
