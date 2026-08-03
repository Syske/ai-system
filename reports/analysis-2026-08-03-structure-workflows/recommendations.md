# 优化建议 / Recommendations

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-03

---

## 一、改进建议 / Improvement Suggestions

### R1 — 同步陈旧记忆引用（中优先）

**问题**：`governance/memory/ai-system/file-contract.md` 的 Solution 仍指引重写 `policies/routing-policy.md`，但该文件已在 commit 54d36e5（2026-08-01）删除，`routing/` 亦已归档至 `archived/`。记忆内容描述的是已不存在的文件。

**建议**：更新该记忆条目的 Solution/Scope，记录最终形态：
- routing-policy.md 因冗余被删除（无消费方；路由由 wizard.py 解析 workflow `## Next` 段承担）
- `routing/ai-routing.yaml` 归档至 `archived/routing/`
- 保留该记忆的原始教训（文件名-内容契约），但落点改为当前真实文件（如 `skills/README.md`、`config/workflow-registry.yaml` 的维护约定）

**落点**：
- `governance/memory/ai-system/file-contract.md`

### R2 — 归档记录标注已删除的中间状态（低优先）

**问题**：`archived/ARCHIVE.md`（2026-08-01 Routing & Frameworks Archival）第 51/66 行记录"routing-policy.md 现描述 wizard-driven routing"，但该文件在归档后同日被删除。归档记录描述了一个被取代的中间状态，后续阅读者可能误以为 routing-policy.md 仍存在。

**建议**：二选一。
- 选项 A（推荐）：在 ARCHIVE.md 该条目追加一行备注，说明 routing-policy.md 随后（commit 54d36e5）被判定冗余并删除。
- 选项 B：接受归档记录作为历史快照，仅在 governance/README.md 中确保不再索引 routing-policy.md（已满足）。

---

## 二、重构机会 / Refactoring Opportunities

### R3 — 无（评估结论）

本次分析未发现需要重构的结构性问题：

- 11 个工作流集合完整，无合并/拆分需求
- 运行时全部 Extends runtime-base.md，无中间抽象残留
- 路由层冗余已被移除（ai-routing.yaml 归档、routing-policy.md 删除），向导路由为单一来源
- 条件回边（review→develop、verify→develop、release→develop）为有意返工通道，保留

---

## 三、缺失组件 / Missing Components

### R4 — 无功能缺口

工作流层覆盖完整：冷启动（bootstrap）、需求（prepare）、规格（spec）、绑定（dev-setup）、实现（develop）、审查（review）、验证（verify）、发布（release）、缺陷（bugfix）、系统体检（analysis）、知识（knowledge）。未发现缺失的业务工作流。

---

## 四、最佳实践 / Best Practices

1. **注册表驱动新增**：新增工作流走 `config/workflow-registry.yaml` → `config/workflows/<name>.yaml` → `workflows/<name>.md` → 菜单注册的固定流程，不修改运行时。
2. **路由单一来源**：工作流推荐从 `## Next` 段派生（wizard.py），不维护独立路由表；新增 Next 目标时保证其指向存在的文件。
3. **保持契约最小化**：工作流文件不含实现逻辑，生命周期细节保留在 Runtime 层（SOURCE_OF_TRUTH 层级）。
4. **上下文最小加载**：所有工作流坚持"最小加载集 + 禁止全仓加载"。
5. **命名纪律**：身份字段统一 `ID` 后缀（Project ID / Task ID / Change ID），内容字段描述性命名。
6. **记忆与现状同步**：治理/记忆层引用删除或归档的文件时，应随变更同步更新，避免陈旧指引（本次 R1）。

---

## 五、优先级汇总 / Priority Summary

| 编号 | 类型 | 优先级 | 落点 |
|---|---|---|---|
| R1 | 引用一致性 | 中 | governance/memory/ai-system/file-contract.md |
| R2 | 文档同步 | 低 | archived/ARCHIVE.md |

实施建议：R1 建议在下次 knowledge 维护（collect/update）时一并处理，属文档级调整；R2 可随时低成本落地。均不涉及代码逻辑，遵循 L1 文档级调整即可。

---

## 六、处置记录 / Resolution Status

| 编号 | 状态 | 处置 |
|---|---|---|
| R1 | 已应用 | `governance/memory/ai-system/file-contract.md` Solution 更新：routing-policy.md 已删除（commit 54d36e5），路由为 wizard 驱动（wizard.py 解析 `## Next` 段） |
| R2 | 已应用 | `archived/ARCHIVE.md` 追加 Note：routing-policy.md 于 commit 54d36e5 被删除 |
