# Change Proposal: P47 — develop 前置处理规则与产物目录约定

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（workflow 行为规则 + 产物路径规范收口） |
| Author | AI Maintainer |
| Created | 2026-09-02 |
| Reference | 迁移后会话迷失事件（develop 前置未满足时 AI 纠结自推 vs 先跑 dev-setup，用户裁决「先执行 dev-setup」）；T-002-completion-report.md 路径根因（develop 无路径约束 → 落项目根）；runtime-develop Location 行旧指向 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

两项同属「develop 执行规范缺口」：

**(a) 前置不满足时的处理无规则**（用户载决驱动）：
- `workflows/develop.md` Preconditions 声明「Dev Setup completed (Project Context and Workspace Context available)」但**未定义不满足时怎么办**
- 实测迷失：某 workspace `last_workflow: spec`（dev-setup 从未运行、无 `contexts/`）时，AI 会话纠结「先跑 dev-setup 还是 develop 自推」——决策无据可依

**(b) 完成报告产物位置无约定**（T-002 事故驱动）：
- develop 模板 Location 把 Completion Report 指向 `workspaces/<project-id>/`（项目根）——T-002 报告落根的模板依据
- 无目录约定 → 报告散落；归档脚本以「根目录 glob」收集，与不当位置互相锁定

两缺口同根：**develop 输出/前置的路径与行为规范缺失**——AI 凭临场判断而非显式规则。

## 2. Root-Cause（根因分析）

- (a) Preconditions 只声明条件、不给处理路径；主链阶段衔接（dev-setup→develop）无「前置未满足先补跑」显式条款。
- (b) runtime-develop.md / develop.md 的 Outputs/Location 沿用早期自由放置；归档扩展 rglob 收集反制了问题但没修正位置本身。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 规则+路径收口（Recommended）** | (a) Preconditions 增处理规则：缺 Dev Setup 先跑 dev-setup，禁止自推/跳步；(b) 完成报告目录约定 `openspec/changes/<change-id>/completion-reports/`，runtime-develop/develop 双文件 Location 对齐 | 行为与路径双双显式化；归档扩展 rglob+--delete 已天然适配（实证全自动） |
| B1. 仅补前置规则 | (a) 做、(b) 维持根目录 | 报告位置债继续 |
| B2. 仅约定目录 | (b) 做、(a) 靠 AI 自觉 | 前置迷失复发风险 |
| C. 维持现状 | 都保留，文档记录 | 已证伪：迷失+落根均实测发生 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**：
1. 用户已明确裁决 (a) 的处理路径（先 dev-setup，不迷失）——规则化即把裁决固化。
2. (b) 与归档扩展协同闭环（单源 workspace → 归档 rglob 全树收集 → --delete 清理旧位），目录约定是链路最后一环。
3. 均为轻量文本级改动（workflow/template 一处），无新机制/工具。

## 5. Proposed Changes（具体改动清单）

1. **workflows/develop.md Preconditions** 增处理规则：Missing Dev Setup（无 `contexts/` 或 `.aic-state` 无 dev-setup 记录）→ 先执行 `dev-setup` workflow（主链前置阶段），再继续 develop；禁止编造 Project/Workspace Context、禁止跳步（即使请求仅说 develop）。
2. **产物目录约定**：Completion Report + Test results → `workspaces/<project-id>/openspec/changes/<change-id>/completion-reports/`；updated Workspace Context → `contexts/`；Task Card → `tasks/cards/<task-id>.md`。
3. **双文件对齐**：runtime-develop.md 与 develop.md 的 Outputs/Location 行同文案（proposal-audit/check 双文件一致性校验通过）。
4. 归档扩展无改动（rglob 全树收集 + --delete 旧位清理天然适配）；OPTIMIZATION_LOG 记目录约定。

## 6. Validation Plan（如何验证）

- `python3 tools/check.py` → PASS（workflow 输出声明与 runtime 双文件一致校验收口）
- 单测 `cli/tests/test_prompt_builder` → OK（15 tests，结构断言不受影响）
- 实证：T-002 完成报告迁移至 `completion-reports/` 由 archive_sync 自动同步（delete 旧位 + copy 新位 + commit + push 全程 0 人工干预）
- grep 全仓：完成报告路径约定仅 runtime-develop/develop 一处定义（单一事实源）

## 7. Risks（风险与缓解）

- 前置规则强制补跑 dev-setup 可能延长首次 develop 链路——预期行为（主链完整性优先），且在 Preconditions 明示
- 目录迁移对既有散落报告：存量报告按约定逐步归位（T-002 已归位示范）；归档快照由脚本自动跟齐

## Review Log

- 2026-09-02：用户裁决 (a)（「针对没有 Dev Setup completed 的项目应该先执行 dev-setup，而不是迷失」）；(b) 由用户问询「completion-report 文件夹统一管理」驱动，命名取复数 `completion-reports/`（对齐 tasks/cards、tasks/plans 惯例）

## Implementation Record

- `da469ab` runtime-develop.md Location 收口（completion-reports/contexts/tasks/cards）
- `c7c6496` workflows/develop.md 前置处理规则（用户裁决固化）
- `b0a09ae` workflows/develop.md Location 与 runtime-develop 对齐（check.py FAIL 修复）
- 扩展侧：archive_sync rglob+--delete 适配实证；OPTIMIZATION_LOG/SKILL 约定记录