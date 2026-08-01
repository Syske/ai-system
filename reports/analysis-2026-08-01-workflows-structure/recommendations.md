# 优化建议 / Recommendations

- 目标 / Target: structure
- 范围 / Scope: workflows
- 日期 / Date: 2026-08-01

---

## 一、改进建议 / Improvement Suggestions

### R1 — 统一主链定义（高优先）

**问题**：`workflows/README.md` 与 `config/menu.yaml`、`OPERATIONS.md §1.2` 对主链起点定义不一致（README 含 bootstrap，另两处从 prepare 起）。

**建议**：统一口径。推荐采用"bootstrap 为一次性冷启动入口，变更生命周期主链从 prepare 开始"的口径（与 OPERATIONS.md、menu.yaml、dev-setup 依赖链一致），并同步修订 `workflows/README.md` 主链图。

**落点**：
- `workflows/README.md` Main Chain 段：改为 `prepare → spec → dev-setup → develop → review → verify → release`，bootstrap 单列为 Entry/Cold-start。
- 保持 `bootstrap → prepare` 的 Next 不变（真实存在的前置关系）。

### R2 — 固化 review.md 的额外章节（低优先）

**问题**：`workflows/review.md` 含标准八段之外的 `When to Use` 章节，与 README 模板规范"恰好包含这些章节"冲突。

**建议**：二选一。
- 选项 A（推荐）：在 `workflows/README.md` §Workflow Template 中显式允许可选章节（如 `When to Use`、`Mode`），声明其插入位置（Purpose 之后）。
- 选项 B：将 review-changes 区分说明移入 `skills/review-changes/SKILL.md`，review.md 保持严格八段。

### R3 — 定义分析产物落盘位置（低优先）

**问题**：analysis 工作流声明输出 `analysis-report.md` 等 4 份报告，但未指定存放目录；本次分析将产物放于 `reports/analysis-<date>-<target>-<scope>/`。

**建议**：在 `workflows/analysis.md` Outputs 或 Context 中补充产物目录约定（如 `reports/analysis-{date}-{target}-{scope}/`），使后续分析运行可确定性落盘、可追溯。

### R4 — 清理 AI 控制流中的中英混排（低优先）

**问题**：`workflows/release.md` Next、`workflows/review.md` 注释中使用中文括号 `（...）`；`runtime-release.md`、`runtime-review.md`、`runtime-spec.md` 的 AI 指令文本中也存在中文。LANGUAGE_CONVENTION 明确：AI 控制流层（Workflow definitions / Runtime templates / Skills / Governance / Config）必须英文；仅用户输出内容允许中文（且混排仅允许双语标题形式）。

**建议**：按"控制流指令英文、用户报告模板中文"的边界清理。AI 指令/判定文本中的中文一律改英文；内嵌的用户报告模板（runtime 中输出给用户的 markdown 报告块、Task Card Review Result）保留中文。

---

## 二、重构机会 / Refactoring Opportunities

### R5 — 无（评估结论）

本次分析未发现需要重构的结构性问题：

- 11 个工作流集合完整，无合并/拆分需求（与 WORKFLOW-OPTIMIZATION-REPORT-2026-07 五结论一致）
- 运行时全部 Extends runtime-base.md，无中间抽象残留
- 条件回边（review→develop、verify→develop、release→develop）为有意返工通道，保留

---

## 三、缺失组件 / Missing Components

### R6 — workflows/README.md 主链图与术语表同步

若采纳 R1，需同步更新 README 主链图和"Main Chain"描述，避免文档内部矛盾。

### R7 — 无功能缺口

工作流层覆盖完整：环境（bootstrap）、需求（prepare）、规格（spec）、绑定（dev-setup）、实现（develop）、审查（review）、验证（verify）、发布（release）、缺陷（bugfix）、系统体检（analysis）、知识（knowledge）。未发现缺失的业务工作流。

---

## 四、最佳实践 / Best Practices

1. **注册表驱动新增**：新增工作流走 `config/workflow-registry.yaml` → `config/workflows/<name>.yaml` → `workflows/<name>.md` → 菜单注册的固定流程（OPERATIONS.md §1.10.1），不修改运行时。
2. **保持契约最小化**：工作流文件不含实现逻辑，生命周期细节保留在 Runtime 层（SOURCE_OF_TRUTH 层级）。
3. **上下文最小加载**：所有工作流坚持"最小加载集 + 禁止全仓加载"。
4. **命名纪律**：身份字段统一 `ID` 后缀（Project ID / Task ID / Change ID），内容字段描述性命名。
5. **回边受退出准则约束**：review/verify/release 的返工回路依赖显式 Exit Criteria 触发，保持这一约束模式。

---

## 五、优先级汇总 / Priority Summary

| 编号 | 类型 | 优先级 | 落点 |
|---|---|---|---|
| R1 | 一致性 | 高 | workflows/README.md |
| R2 | 一致性 | 低 | workflows/README.md 或 skills/review-changes |
| R3 | 完整性 | 低 | workflows/analysis.md |
| R4 | 规范 | 低 | workflows/release.md、workflows/review.md |
| R6 | 一致性 | 随 R1 | workflows/README.md |

实施建议：R1 可独立低风险落地；其余为低优先文档级调整，可与下次维护窗口合并执行。所有改动应遵循 change control（L1 直接应用并记录，L2 需确认）。

---

## 六、处置记录 / Resolution Status

本次分析同窗口已应用以下建议（L1 文档级调整，`tools/check.py` PASS）：

| 编号 | 状态 | 处置 |
|---|---|---|
| R1 / R6 | 已应用 | `workflows/README.md` 主链改为 `Entry & Main Chain`：bootstrap 列为冷启动，变更主链从 prepare 起算，与 menu.yaml、OPERATIONS.md §1.2 口径统一 |
| R2（选项 A） | 已应用 | `workflows/README.md` §Workflow Template 显式允许可选章节 `When to Use`（置于 Purpose 之后），review.md 结构合规 |
| R3 | 已应用 | `workflows/analysis.md` Outputs 补充报告落盘约定：`reports/analysis-{date}-{target}-{scope}/` |
| R4 | 已应用 | `workflows/review.md`、`workflows/release.md`、`templates/prompts/develop-start.md`、`templates/runtime/runtime-release.md`、`runtime-review.md`、`runtime-spec.md`：AI 控制流指令文本全部改为英文；内嵌用户报告模板保留中文。工作流/提示/配置/路由层 CJK 残留 = 0。补充：面向用户的提问/选择/确认统一遵循系统语言（`config/menu.yaml → locale`，当前 zh），涉及 runtime-prepare / spec / review（Grilling + 完成路由表）/ dev-setup（分支确认）/ develop / bugfix / release（确认流程） |
