# Change Proposal: P57 — scan 命令 service 级选择 + 字段收集死循环出口

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (CLI/wizard 交互契约) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | MAINTENANCE-2026-09-21.md F2/F3（用户反馈：scan 循环选择项目 + 缺少选择具体 service；设计方向经用户确认，参照 code-review 交互流程） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. **缺少 service 级选择**（F3）：wizard 唯一的「项目」概念是工作区容器
   （workspaces/\<pid\>，step 0 必选）；service（仓库）级选择只有 `projects_dirs()`
   的扁平全量（projects/ 下 70+），不按所选容器的 `workspace.yaml` 映射过滤。
   选中容器 `202610-cool-italent-sync-plus`（映射 4 服务）后仍无法只扫其中 1 个服务。
   `workflows/change-impact.md` 声称「有项目容器时也可从 workspace.yaml 映射选择」，
   但 CLI 未实现（`providers.project_repos` 仅用于容器列表展示与 skill_launcher）。
   code-review（Projects 必填）同样受影响（G2）。
2. **hook-validate 失败死循环**（F2/G1，通用）：`ScanHooks.validate` 与
   `ChangeImpactHooks.validate` 失败（未选 Workspace / Projects 空）→ `steps.py` 置
   `step = 2` 重问**全部字段** → 再次失败 → 无限循环；唯一出口为选 Workspace /
   Projects 手输任意非空字符串（校验只查真值**不验名称存在性**，与 aic-scan.md
   Step 1「无可用范围则报告并停止」的运行时语义不一致）。
3. **Review Focus 预置候选未接线**（G3，09-11 半实现遗留）：`menu.yaml field_choices`
   已配 10 项 Review Focus 候选 + multi_select_fields 已含 Review Focus，但
   `_choices_for` 分派表缺该字段 → 实际走自由文本，候选从不展示。
4. 机器层 `config/environments/local.yaml` 残留 `/tmp` 测试路径导致 Projects/Branch
   字段 0 选项，是本问题在当机的**触发器**（机器观察，另行就地修复，不入本提案范围）。

## 2. Root-Cause

- Projects 字段候选来源单一且与容器脱节：`_choices_for("Projects")` 只调
  `providers.projects_dirs`（扁平全量），从不读所选容器的 `workspace.yaml` 映射。
- 字段收集失败路径无出口：hook validate 失败统一回 `step = 2`（字段 0），
  没有「呈现候选 / 询问 / 退出」的交互契约。
- 校验语义与运行时语义分裂：CLI 只查字段非空，运行期（aic-scan.md Step 1）
  才验范围可用性。

## 3. Options

- **Option A（推荐）— 参照 code-review 交互流程，候选驱动 + 询问代替猜测**：
  - Projects 字段有容器时优先呈现容器 `workspace.yaml → repository.available[].service`
    候选（复用 `providers.project_repos`），无容器/无映射时回退 projects/ 全量；
  - 失败路径不再全量重收：停住并呈现候选询问（Projects 候选 = 容器映射服务；
    Branch 候选 = workspace.yaml dev_branch + git 分支，单候选自动、多候选选择、
    零候选询问），保留明确退出/返回入口；
  - `_scope_empty` 增加名称存在性校验（与 aic-scan.md Step 1 对齐）。
  优点：与既有 code-review/change-impact 的运行时交互契约一致；复用现有
  `project_repos`；同时消除 F2 与 F3。缺点：涉及 wizard fields/hooks 两处逻辑。
- **Option B — 仅补 Projects 字段候选（最小）**：只把 Projects 候选换成容器映射
  服务，不动失败路径。优点：改动最小。缺点：F2 死循环仍在（候选非空时触发面
  变小，但手输假名/跳过后仍会循环）。
- **Option C — 仅改失败路径**：validate 失败停在字段收集尾并提示，不重收。
  优点：F2 解决。缺点：F3 未解决（仍是扁平全量/空列表）。

## 4. Recommendation

**Option A**。理由：
- 与 code-review 交互流程（runtime-code-review.md Phase 1：workspace.yaml 映射选择、
  候选驱动、单候选自动/多候选选择/零候选询问、不猜测）保持同一交互契约；
- 一次改动同时闭合 F2 与 F3，避免两轮迭代；
- 复用已有 `providers.project_repos`，不新增能力（Repository First）。

## 5. Proposed Changes

1. `cli/services/providers.py`：新增 `container_services(wizard, project)` —— 读容器
   `workspace.yaml` 返回 `repository.available[].service`（复用 `project_repos`）；
   `projects_dirs` 保持全量回退用途。
2. `cli/services/wizard/fields.py` `_choices_for("Projects")`：有项目容器时返回
   容器映射服务候选；无容器/无映射时回退 `projects_dirs` 全量（覆盖 scan /
   code-review / change-impact / proposal 的 Projects 字段）。
3. `cli/services/wizard/fields.py` `_choices_for("Branch")`：候选来源扩展为
   `workspace.yaml dev_branch` + `git_branches`（单候选自动、多候选选择）。
4. `cli/services/wizard/fields.py` `_choices_for` 分派表**补齐 "Review Focus"**：
   返回 menu.yaml field_choices 的 10 项预置候选（修 G3，09-11 配置层已就绪）。
5. `cli/services/command_hooks.py`：`ScanHooks.validate` 与
   `ChangeImpactHooks.validate` 失败时**不触发全量重收**，返回可呈现的候选询问消息；
   `_scope_empty` 增加 Projects 名称存在性校验（路径或 workspace.yaml 服务名解析）。
6. `cli/services/wizard/steps.py`：hook validate 失败路径从 `step = 2`（全量重收）
   改为停留在当前字段收集尾 + 明确退出/返回入口（对照 code-review「ASK 不猜测」）。
7. `cli/commands/aic-scan.md` + `workflows/change-impact.md`：同步描述
   「容器映射选择」已实现（消除 doc-vs-reality）；scan Inputs 的 Projects 说明
   更新为候选驱动语义。
8. 测试：`cli/tests/` 增补——容器映射候选 / 无容器回退全量 / Review Focus 候选接线 /
   失败路径不重收 / `_scope_empty` 验名（假名拒绝）。

## 6. Validation Plan

- `python3 tools/check.py`（含 wizard dry-run 字段解析、workflow-command-audit）
- `python3 tools/repo-lint.py --repo-root .`（0 BLOCKER/ERROR）
- `python3 tools/path-audit.py`（0 broken）
- `python -m unittest discover -s cli/tests`（新增用例全绿，回归 294+）
- 手工链路：选容器 → scan → Projects 呈现容器映射服务 → 跳过/假名 → 提示询问而非循环
- language-gate：CLI 用户可见文案 locale=zh

## 7. Risks

- 行为变更：Projects 候选从「全量 70+」变为「容器映射优先」——无容器场景回退全量，
  不影响一次性任务（change-impact 的仓库路径/URL 直输保持）。
- 兼容：`projects_dirs` 保留，其他调用方（proposal/code-review）不受影响。
- 机器层 local.yaml 残留（F1）是本提案在当机的触发器，但提案本身不依赖其修复；
  两者独立（F1 走就地修正）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-09-21 |

---

## Implementation Record (2026-09-21)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `cli/services/providers.py`：新增 `container_services`（workspace.yaml 映射服务）与
   `branch_candidates`（dev_branch + git 分支）；`projects_dirs` 保留全量回退。
2. `cli/services/wizard/fields.py` `_choices_for("Projects")`：有容器时优先返回容器映射
   服务候选，无容器/无映射回退 projects/ 全量（scan/code-review/change-impact/proposal）。
3. `_choices_for("Branch")` → `branch_candidates`（容器 dev_branch + git 分支）。
4. `_choices_for` 分派表补齐 "Review Focus"（G3：10 项预置候选接线）。
5. `_ask_field`：Branch 单候选自动采用（code-review 契约，不询问）。
6. `cli/services/command_hooks.py`：ScanHooks/ChangeImpactHooks 新增 `fail_field`
   （返回 Projects）；`_scope_empty` 增名称存在性校验（假名拒绝，与 aic-scan.md 对齐）。
7. `cli/services/wizard/steps.py`：hook validate 失败改重问 fail_field 单字段（不再
   step=2 全量重收 → 死循环消除），保留 BACK/Esc 退出。
8. 文档：`cli/commands/aic-scan.md` Projects/Branch 候选驱动说明；
   `workflows/change-impact.md` 映射选择已实现说明。
9. 测试：`cli/tests/test_wizard_fields.py`（15 用例：容器候选/回退/Review Focus 接线/
   Branch 候选/假名拒绝/fail_field/单候选自动）。
**Validation**: 单测全量 311 OK（+15）；repo-lint 0 BLOCKER/ERROR（WARN 30 基线）；
path-audit 0 broken；check.py 仅剩既有 memory 中文 FAIL（F4，待 E 小修）；language-gate PASS
