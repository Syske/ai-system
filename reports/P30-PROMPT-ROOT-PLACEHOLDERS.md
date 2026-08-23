# Change Proposal: P30 — 提示词渲染期解析根路径占位符（{workspace_root} 等，模板零改动）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix (prompt 渲染层，模板文件零改动) |
| Author | AI Maintainer |
| Created | 2026-08-23 |
| Reference | 2026-08-23 maintain 巡检「方案 3」；路径问题修复批次（提示词绝对化 + Path Anchor）的未根治点 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`workflows/*.md` 与 `templates/runtime/*.md` 正文含符号占位符，经 `{{workflow_definition}}` /
`{{runtime_definition}}` **原样透传**进生成的提示词（`prompt_builder.py:113-114`）：

- 根路径类：`{workspace_root}`（workflows 1 处 + runtime 11 处）、`{repository_root}`（4）、
  `{workspaces_root}`（2）等——**可在构建期由 `environment.paths()` 解析**，但目前留给 agent
  对照 Path Anchor 自行拼装，存在猜错/解析不一致风险
- 运行期类：`{desc}`（10）、`{date}`（10）、`{service_id}`（15）、`{project_id}`（6）、
  `{environment}`、`{type}`、`{target}` 等——**每运行不同**，必须保持符号

8-23 批次的 Path Anchor 已提供两个绝对根缓解，但根路径占位符本身仍透传，是路径类问题的
最后一个未根治点。

## 2. Root-Cause

`prompt_builder._render` 只做 `{{双括号}}` 模板占位符替换（`prompt_builder.py:393-402`），
对正文中的 `{单括号}` 符号占位符无渲染期解析层；模板为单一来源（P25），直接改模板会造成
"会话直读模板"与"提示词产物"双视图漂移。

## 3. Options

- **A. 渲染期白名单替换（Recommended）**：`prompt_builder` 在渲染后对产物做一次
  **根键白名单**替换——仅替换 `environment.paths()` 返回的根键（`{workspace_root}` /
  `{repository_root}` / `{workspaces_root}` / `{outputs_root}` 等），**模板文件零改动**
  （单一来源不变，替换只是渲染叠加）；`{desc}`/`{date}`/`{service_id}` 等运行期键不在
  白名单，保持符号；paths() 解析失败时回退原文
- **B. 维持 Path Anchor，标 won't-fix**：不替换，靠 agent 按绝对根自行解析
- **C. 全量替换所有占位符**（不推荐）：需在构建期获得全部运行期值，且模板与产物双视图
  漂移，违反 P25

## 4. Recommendation

采用 **Option A**：与 8-23 路径修复同向，白名单机制天然隔离运行期键，模板单一来源不受
影响；改动集中在 `prompt_builder`（~20 行）+ 测试，风险低。

## 5. Proposed Changes

- [ ] `cli/services/prompt_builder.py`：新增 `_resolve_root_placeholders(prompt, root)`——
  以 `environment.paths(root)` 根键为白名单，仅替换 `{key}` 单括号占位符；paths() 异常
  或键缺失时保留原文；应用于 workflow/command 渲染产物
- [ ] `cli/tests/test_prompt_builder.py`（或 test_home_env.py）：断言 dev-setup/bootstrap
  构建产物中 `{workspace_root}` 已替换为绝对路径、`{service_id}`/`{desc}` 等运行期键保留、
  paths() 失败回退
- [ ] 文档：`reports/P30-...md` 状态与 README 登记

## 6. Validation Plan

- 构建 dev-setup / bootstrap / release prompt：`{workspace_root}` 等根键无残留；
  `{service_id}`/`{desc}` 等运行期键保留
- `python -m unittest discover -s cli/tests` 全绿
- repo-lint / check.py / path-audit 全绿

## 7. Risks

- **双视图**：替换仅存在于渲染产物，模板文件不变——直读模板的会话仍见符号（现状不变，非回归）
- **误替换**：白名单严格限于 paths() 根键，杜绝触碰运行期键；如未来模板引入同名键，白名单
  机制保证只按 paths() 键集合替换
- **环境依赖**：paths() 解析失败（环境缺失）→ 回退原文，与现状一致

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
