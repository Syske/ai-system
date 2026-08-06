# Change Proposal: P13 — 破除 3 个 Skill 依赖环（S3）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (skill reference graph cleanup) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | MAINTENANCE-2026-08-06.md F3 / S3 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`tools/dependency-graph.py` 检出 3 个依赖环：

```
review → review-changes → review
skill-benchmark-generator → routing-benchmark-generator → skill-benchmark-generator
skill-benchmark-generator → outcome-benchmark-generator → skill-benchmark-generator
```

## 2. Root-Cause Analysis（逐环核查引用文本）

依赖检测器（`dependency-graph.py:58-88`）从技能 md 文件中提取三类引用：
- `delegates to:`（显式委托）
- `` `skill-name` `` 反引号提及（references）
- `Invoke \`skill\``（调用）

### 环 1：review ↔ review-changes

| 方向 | 引用文本 | 位置 | 性质 |
|------|---------|------|------|
| review → review-changes | `Replace \`review-changes\` (knowledge-graph-driven lightweight analysis)` | review/SKILL.md:48 | **对比说明**（"不要用 X 替代"，非依赖） |
| review-changes → review | `Use \`review\` (workflow) instead when:` | review-changes/SKILL.md:13 | **路由说明**（指向 workflows/review，非技能引用） |

> 两个引用都是**文档性提及**，不是真实依赖。检测器的反引号正则无法区分"提及"与"依赖"。

### 环 2 / 环 3：benchmark 三件套

| 方向 | 引用文本 | 性质 |
|------|---------|------|
| skill-benchmark-generator → routing / outcome | `调用 \`routing-benchmark-generator\``（SKILL.md:59-60） | **真实编排**（orchestrates） |
| routing → skill-benchmark-generator | `通常作为 \`skill-benchmark-generator\` 的内部组成部分出现` | **归属说明**（反指父组件，非调用） |
| outcome → skill-benchmark-generator | 同上 | **归属说明**（反指父组件，非调用） |

> 真实依赖单向：**编排器 → 子组件**。反方向的"内部组成部分"是声明式归属文本，被误检为依赖。

## 3. 本质结论

**3 个环均为"文档提及被误判为依赖"，无真实循环调用。** 两类误判来源：
1. 反引号提及正则把"对比/路由/归属说明"当成依赖边（环 1、环 2/3 反方向）。
2. 检测器未识别 "orchestrates" 语义（`get_skill_layers` 已用 orchestrates 分层，但 `extract_references` 未提取），导致真实编排方向与提及混在同一图里。

## 4. Options

### Option A — 检测器语义分层（Recommended）

修改 `tools/dependency-graph.py`：
1. `extract_references` 增加 "orchestrates" 提取（与 `get_skill_layers` 一致），使编排方向成为显式 `orchestrates` 边。
2. **环检测只对真实依赖边**（`delegates_to` / `invokes` / `orchestrates`）进行；纯 `references`（反引号提及）不参与环检测，仅在图中标记。
3. 报告区分 `[CYCLE: real]`（真实调用环）与 `[CYCLE: doc-only]`（纯文档提及环）。

**Impact**：消除误报；保留真实环的检测能力；不修改任何技能内容。同时满足"文档表述可保留"——routing/outcome 的"内部组成部分"归属说明是正确且有价值的文档。

### Option B — 改技能文本消除反引号

改写 3 处引用文本（review.md:48、routing/outcome 的归属句），移除技能名反引号。
**Impact**：环消除但检测器失去对"提及"的感知；且 review.md:48 的对比说明语义会被削弱；治标不治本——未来新增提及仍会误报。

### Option C — 维持现状

**Impact**：3 个环持续出现在依赖图与 MAINTENANCE 报告中，误导架构评审。

## 5. Recommendation

**Adopt Option A。** 检测器应区分"提及"与"依赖"——这是分析工具的正确语义，而非技能内容的问题。Option B 是用文档内容迁就工具缺陷，违背"最小变更"且削弱文档价值。

## 6. Proposed Changes (Option A)

1. `tools/dependency-graph.py`：
   - `extract_references` 增加 orchestrates 提取（`[Oo]rchestrates?\s+`?([a-z][a-z0-9-]+)`?`）
   - `detect_cycles` 改为只对 `delegates_to`/`invokes`/`orchestrates` 边做 DFS；references 边跳过
   - 输出增加环类型标注（real / doc-only）
2. 技能文档**不改**（routing/outcome 归属说明保留）。
3. 回归：`python tools/dependency-graph.py --repo-root .` → 0 CYCLES；MAINTENANCE 报告 F3 更新为已解决。

## 7. Validation

- `python tools/dependency-graph.py --repo-root . --format text` → 无 CYCLES 或仅有 doc-only 标注
- 构造含真实环的临时用例验证检测器仍能捕获
- repo-lint / check.py / path-audit 全绿
- 依赖图分层输出保持稳定

## 8. Risks

- **低**：检测器语义变化可能改变既有分层输出（references 边仍在图中显示，仅环检测排除）。
- 无技能内容/流程/注册表变更。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A**（检测器语义分层） | 2026-08-06 |

---

## Implementation Record (2026-08-06)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `tools/dependency-graph.py`:
   - `REAL_EDGE_KINDS = {delegates_to, invokes, orchestrates}`
   - `extract_references` 新增 orchestrates 提取（与 get_skill_layers 分层语义一致）
   - `detect_cycles` 支持 edge_kinds 过滤；环检测只对真实依赖边进行
   - text 输出区分 `⚠ CYCLES DETECTED (real)` 与 `ℹ DOC-ONLY MENTION CYCLES`
   - json 输出 cycles 结构化为 {"real": [], "doc_only": []}
   - 退出码仅在真实环存在时置 1
2. 技能文档未改（routing/outcome 归属说明保留）。

**Validation（全绿）**：
- 实仓依赖图：真实环 0，3 个既有环归入 doc-only 标注 ✅
- 负向测试 1（真实环 alpha→beta→alpha）：仍可检测 ✅
- 负向测试 2（benchmark 场景 orchestrates+归属说明）：不再构成真实环 ✅
- repo-lint 0/0/9、path-audit 0 broken、check.py PASS（1 warning = P13 自身开放提示，关闭后归零）

**Deviations**: 无。
**Risks**: 检测器对 "orchestrates" 的提取依赖文本措辞（`Orchestrates `X``），与既有 get_skill_layers 的包含判断一致；未来若引入新措辞需同步。
