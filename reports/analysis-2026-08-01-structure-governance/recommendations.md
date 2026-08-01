# 优化建议 / Recommendations

- 目标 / Target: structure
- 范围 / Scope: governance
- 日期 / Date: 2026-08-01

---

## 一、改进建议 / Improvement Suggestions

### R1（高）：修复 `routing-policy.md` 文件名-内容脱节

**问题**：文件名为 routing-policy，内容却是 Skill Lifecycle；README 索引描述与内容不符；路由策略无实际文档。

**建议**：二选一：
- 选项 A（推荐）：将 `policies/routing-policy.md` 内容替换为真正的路由配置策略（意图→workflow 路由规则），将现有 Skill Lifecycle 内容移至 `policies/skill-lifecycle.md` 或并入 `skill-policy.md`
- 选项 B：保持 Skill Lifecycle 内容，将文件重命名回 `skill-lifecycle.md`，路由策略另立文档

**落点**：`governance/policies/routing-policy.md`、`governance/README.md`、`README.md`

### R2（高）：修复 `violation-rules.md` 文件名-内容脱节

**问题**：文件名为 violation-rules，内容为 Repository Governance 总览。

**建议**：
- 将总览内容迁至 `governance/README.md`（治理入口索引）或 `governance/README.md` 扩充
- `violation-rules.md` 重写为真正的违规严重度分级规则（BLOCKER/ERROR/WARNING/INFO + 处置）

**落点**：`governance/violation-rules.md`、`governance/README.md`

### R3（中）：完成或归档 `security-policy.md` 占位符

**问题**：5 行占位符被多文档引用为正式策略。

**建议**：二选一：
- 完成安全策略（推荐，security 属必要治理），或
- 若当前无安全约束，在文档中显式标注 `status: placeholder / not enforced` 并在引用处澄清

### R4（中）：修正 `scripts/` 路径引用

**问题**：3 个文件引用 `scripts/repo-lint.py`、`scripts/repo-metrics.py`，实际在 `tools/`。

**建议**：统一改为 `tools/repo-lint.py`、`tools/repo-metrics.py`。

**落点**：`policies/quality-gates.md`、`policies/routing-policy.md`、`review-standard.md`

### R5（中）：清理 standards-loader 悬空引用

**问题**：7 个引用目标不存在。

**建议**：
- `common/code-quality.md`：从 standards-loader 移除（已由 task-quality-checklist.md 取代），或改为指向归档说明
- 其余 6 个语言/框架预留位（api/rest、database/sql、go/go-style、java/mybatis、java/spring、mq/rocketmq、python/pep8）：在 standards-loader 中显式标注 `(extension reserved)`，或创建最小骨架

### R6（低）：清理 README 对已归档 `code-quality.md` 的引用

**建议**：README.md 第 71 行改为引用 `task-quality-checklist.md` 或删除该行。

### R7（低）：修复 memory 索引悬空类别

**建议**：`governance/memory/coding-memory.md` 中移除 `python/`、`integration/` 条目，或创建对应目录；与 MEMORY_GUIDELINES 推荐结构对齐。

### R8（低）：规范 `standards/java/rpc.md` 结构

**建议**：补全为完整文档结构（一级标题 + Purpose/Scope），或并入 `standards/dependency-version.md`（RPC 依赖版本规则）与 `standards/cool/rpc-conventions.md`。

---

## 二、重构机会 / Refactoring Opportunities

### R9 — skill-policy 与 routing-policy(Skill Lifecycle) 职责梳理

- `skill-policy.md`（Contribution Guide）与 `routing-policy.md`（Skill Lifecycle）在技能生命周期上职责重叠
- 建议：生命周期状态定义（Draft→Proposed→Active→Deprecated→Archived）保留一处权威，另一处引用

### R10 — governance/README.md 作为唯一索引

- 当前治理总览散落于 `violation-rules.md`（Repository Governance）、`governance/README.md`、根 `README.md`
- 建议：治理总览统一收敛到 `governance/README.md`，其余文档仅引用

---

## 三、缺失组件 / Missing Components

### R11 — 路由配置策略文档缺失

- `routing/ai-routing.yaml` 存在，但无对应策略文档（routing-policy.md 内容错位）
- 建议：补写路由策略（intent→workflow 映射规则、alias 规则、fallback 规则）

### R12 — 违规严重度分级规则缺失

- README 承诺 violation-rules.md 提供分级，实际缺失
- 建议：补写 BLOCKER/ERROR/WARNING/INFO 违规分级 + 处置流程

### R13 — 安全策略未完成

- security-policy.md 仅占位，建议完成

---

## 四、最佳实践 / Best Practices

1. **文件名即契约**：文档文件名应精确反映内容主题；迁移改名时内容必须同步（F1/F2 教训）
2. **归档即清理引用**：文件移入 archive/ 时，同步清理所有 active 引用（F6 教训）
3. **占位符须标注状态**：未完成文档显式声明 placeholder，避免被误当正式规则引用（F3）
4. **单一索引**：治理总览收敛到 governance/README.md，避免多处维护（R10）
5. **语言纪律**：保持 governance 层英文（当前已良好，继续维持）

---

## 五、优先级汇总 / Priority Summary

| 编号 | 类型 | 优先级 | 落点 |
|---|---|---|---|
| R1 | 结构一致性 | 高 | policies/routing-policy.md + 索引 |
| R2 | 结构一致性 | 高 | violation-rules.md + 索引 |
| R3 | 完整性 | 中 | policies/security-policy.md |
| R4 | 引用修复 | 中 | 3 个引用 scripts/ 的文件 |
| R5 | 引用清理 | 中 | loaders/standards-loader.md |
| R6 | 引用清理 | 低 | README.md |
| R7 | 索引修复 | 低 | memory/coding-memory.md |
| R8 | 结构规范 | 低 | standards/java/rpc.md |
| R9 | 职责梳理 | 中 | policies/ |
| R10 | 单一索引 | 低 | governance/README.md |
| R11 | 缺失补全 | 中 | routing 策略文档 |
| R12 | 缺失补全 | 中 | violation 分级 |
| R13 | 缺失补全 | 中 | security 策略 |

---

## 六、处置记录 / Resolution Status

本次分析同窗口已应用以下建议（L1 文档级调整，`tools/check.py` PASS）：

| 编号 | 状态 | 处置 |
|---|---|---|
| R1 | 已应用 | Skill Lifecycle 内容迁至新文件 `policies/skill-lifecycle.md`；`policies/routing-policy.md` 重写为真实路由策略（路由类型、路由表、执行规则，基于 routing/ai-routing.yaml） |
| R2 | 已应用 | `violation-rules.md` 重写为违规严重度分级规则（BLOCKER/ERROR/WARNING/INFO + 违规类别 + 处置 + Change Control 引用） |
| R3 | 已应用 | `policies/security-policy.md` 补全为正式安全策略（原则、规则、违规、范围） |
| R4 | 已应用 | `quality-gates.md`、`review-standard.md` 的 `scripts/` 路径改为 `tools/`（routing-policy 重写时已同步） |
| R5 | 已应用 | standards-loader 移除已归档的 `common/code-quality.md` 引用；为 7 个语言/框架预留位创建最小骨架文档（api/rest、database/sql、go/go-style、java/mybatis、java/spring、mq/rocketmq、python/pep8），标注 Reserved |
| R6 | 已应用 | README.md 移除已归档 `code-quality.md` 引用，补充 `skill-lifecycle.md` 索引 |
| R7 | 已应用 | memory/coding-memory.md 的 python/、integration/ 类别标注为 `(reserved)` |
| R8 | 已应用 | `standards/java/rpc.md`（无引用、与 cool/rpc-conventions.md 重复的碎片文件）删除 |
| R9 | 已应用 | skill 生命周期状态定义收敛至 `policies/skill-lifecycle.md`；`skill-policy.md` 保持贡献指南职责 |
| R10 | 部分 | governance/README.md 更新为最新索引（含 skill-lifecycle、routing-policy 新描述） |
| R11 | 已应用 | 路由策略文档补全（routing-policy.md） |
| R12 | 已应用 | 违规分级规则补全（violation-rules.md） |
| R13 | 已应用 | 安全策略补全（security-policy.md） |
