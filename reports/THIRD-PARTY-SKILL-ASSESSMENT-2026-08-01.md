# 三方 Skill 参考价值评估报告

- 日期 / Date: 2026-08-01
- 来源 / Sources:
  - mattpocock/skills (https://github.com/mattpocock/skills) — 39 skills
  - obra/superpowers (https://github.com/obra/superpowers) — 14 skills
  - affaan-m/ECC (https://github.com/affaan-m/ECC) — 281 skills
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

## 四、affaan-m/ECC 评估（281 skills）

ECC 是**大规模集成平台**（含 hooks / commands / agents / rules 全体系），其 skill 多为该平台生态组件，独立可移植性低于前两个仓库。绝大多数是语言/框架/领域特定 skill，与 ai-system（治理系统）无直接关系。

### 已吸收（高价值 2 项）

| skill | 吸收到 | 内容 | Commit |
|---|---|---|---|
| skill-scout | aic-skill-source 命令 | 创建前搜索本地/多方来源避免重复、外部匹配审查（读 frontmatter / 查危险 shell/网络/凭据 / 评估维护度）、吸收决策选项表（直接吸收/派生扩展/新建） | c601552 |
| agent-self-evaluation | REFLECTION_RULES | 5 轴评分（accuracy/completeness/clarity/actionability/conciseness）1-5 分 + 证据规则（<5 分必须引用具体证据）——评分制补充现有 5 问检查制 | c601552 |

### 未吸收（低/无价值，含原因）

| 类别 | 示例 | 原因 |
|---|---|---|
| 语言/框架特定（~260） | python-patterns, django-*, springboot-*, kotlin-*, postgres-patterns, docker-patterns, kubernetes-patterns, react-* 等 | 技术栈特定，与 ai-system 治理无关 |
| 领域业务特定 | healthcare-*, finance-*, logistics-*, energy-procurement, customs-trade-compliance, visa-doc-translate 等 | 特定业务领域 |
| 平台生态组件 | configure-ecc, ecc-guide, hookify-rules, dynamic-workflow-mode, autonomous-loops, claude-devfleet 等 | 依赖 ECC 平台的 hooks/agents/rules 体系，不可独立移植 |
| 个人/内容创作 | article-writing, brand-*, investor-materials, social-publisher, seo, manim-video, video-editing 等 | 非本领域 |
| 与已有资产重叠 | coding-standards, architecture-decision-records, verification-loop, benchmark-methodology, intent-driven-development | 与 repo-lint / rfc-README ADR / check 门禁 / benchmark 类 skill 重叠 |

### 中价值（未吸收，待真实需求评估）

| skill | 借鉴点 | 未吸收原因 |
|---|---|---|
| delivery-gate | 机械质量门禁（完成前强制检查，检测 rationalization 模式） | 与 verification-before-completion 同源；我们已吸收证据先行 |
| context-budget | 上下文窗口消费审计（识别 bloat） | 依赖 Claude Code 环境；可后续评估 |
| continuous-learning-v2 | 会话经验→原子 instinct→skill 演化 | 与我们 memory/knowledge 工作流理念相关但机制不同 |
| skill-stocktake / skill-comply | skill 质量审计、合规测量（压力场景验证 skill 是否被遵循） | 与 repo-lint / skill-author 重叠；机制较重（需运行 agent） |

---

## 五、协同关系

- **mattpocock**：方法论型（教"怎么做"）→ feedback loop、seam、deep module
- **superpowers**：纪律型（约束"必须做什么"）→ Iron Law、evidence gate
- **ECC**：工程实践型（补充"评价与避免重复"）→ skill-scout（创建前搜索）、
  agent-self-evaluation（5 轴自评）
- 三层互补：方法论提供做法，纪律提供强制约束，评价提供质量量化与去重，
  叠加在 ai-system 的 skill（方法）、governance（规则）、tooling（命令）三层

---

## 六、后续待办（不预先引入）

| 项 | 触发条件 |
|---|---|
| brainstorming HARD-GATE | 若出现"未设计即实现"的真实问题 |
| subagent-driven / parallel-agents | 平台子代理能力可稳定使用且需并行开发 |
| review 反馈纪律（requesting/receiving） | 若 review 反馈处理出现"盲从或盲目反对"问题 |
| Iron Law 强化 tdd | 若出现"无测试即写生产代码"违规 |
| ECC delivery-gate / context-budget | 若验证或上下文开销出现真实问题 |
| ECC skill-stocktake / skill-comply | 若 skill 质量审计需自动化测量 |
