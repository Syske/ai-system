# Change Proposal: P16 — wizard 状态写入增加项目存在性校验（S2 根因修复）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix (state hygiene) |
| Author | AI Maintainer |
| Created | 2026-08-08 |
| Reference | MAINTENANCE-2026-08-08.md F1 / S2 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`.aic-state.yaml` 的 `last_project` 引用两次被判定为陈旧（08-06 F1 修复、08-08 F1 复发）：`workspaces/pywechat-live-2608/` 目录存在，但业务仓库已不在 junction 目标 `D:\workspace\project-resources` 中。每次手动清空后，只要用户再次通过交互 wizard 运行任一命令，状态即被重新写入陈旧项目名。

## 2. Root-Cause

已定位（2026-08-08 排查）：

- **唯一写路径**：`cli/services/wizard/output.py:98-131` `_save_state()`——交互 wizard 每次完成都会**无条件自动回写** `last_project` / `last_command` / `last_action`，无 opt-out。
- **唯一守卫**：`if not project: return`（output.py:100）——仅防空值，**不校验项目存在性**。
- **项目来源**：`cli/services/wizard/selection.py:79-81` 只枚举 `workspaces/` 目录（排除 archived），**不校验 junction 目标中业务仓库是否存在**。

结论：清空是治标；根因是「写入无存在性校验 + 项目列表基于 workspace 目录而非业务仓库」。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | `_save_state` 写前校验项目存在性（workspace 目录存在 + 可选业务仓库存在），失败则不写入 | 根治陈旧引用；改动小（单函数） | 需要明确"存在性"定义 |
| B | 仅清理已失效状态，不改代码 | 零改动 | 复发，08-06 已验证 |
| C | 移除 last_project 记忆功能 | 彻底无陈旧引用 | 损失 wizard 默认项目便利 |

## 4. Recommendation

**Option A**：在 `_save_state` 中增加校验——项目 workspace 目录存在（沿用 selection.py 的判定标准），可选增强为同时校验 `projects/<id>`（junction 目标）存在。校验失败则跳过写入（保留现有状态不覆盖）。最小改动、根治复发、保留记忆便利。

## 5. Proposed Changes

1. `cli/services/wizard/output.py` `_save_state()`：写入前调用存在性校验（workspace 目录存在；若 `projects/` junction 可访问且对应仓库缺失则视为不存在）。
2. 校验逻辑提取为独立方法（如 `_project_exists()`），供 selection.py 复用（项目列表过滤可选增强）。
3. 增加单测：`cli/tests/test_state_store.py` 或 wizard 测试——校验失败不写入、成功时正常写入。

## 6. Validation Plan

- `python tools/check.py`（exit 0）
- `python -m pytest cli/tests/ -q`（新增用例通过）
- 手动：指向不存在仓库的 workspace 项目运行 wizard → 状态不写入陈旧引用

## 7. Risks

- 判定标准差异：workspace 目录存在但仓库缺失（当前 F1 场景）→ 按"不存在"处理，用户可能无法记忆该项目的 last_project（可接受，与默认值功能等价）。
- 兼容性：`system (no project)` 路径不受影响（project 为空直接 return）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-08 |

---

## Implementation Record (2026-08-08)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `cli/services/wizard/output.py`：新增 `_project_exists()`——workspace 目录存在 +（projects_root 可用时）对应业务仓库存在；`_save_state()` 写入前调用校验，失败则跳过（不覆盖现有状态）。
2. `cli/services/wizard/selection.py` `_select_project()`：项目候选列表用同一 `_project_exists()` 过滤，陈旧项目不再出现在列表与默认项中。
3. `cli/tests/test_wizard_output.py`（新增）：9 个用例——空值/缺失 workspace/无 repo root/失效 junction 回退/F1 场景（workspace 在、仓库缺）/有效项目/保存跳过与写入分支。
4. `reports/README.md`：P16 登记提案索引；`reports/PROPOSALS.md` 状态同步。

**Validation**:
- `python -m unittest discover -s cli/tests`：50 tests OK（含新增 9 个）
- `python tools/check.py`：exit 0（warnings 仅剩 open proposals 跟踪 + thin-command 既有项）
- `python tools/repo-lint.py --repo-root .`：0 BLOCKER / 0 ERROR / 25 WARNINGS（无新增）
- `python tools/path-audit.py`：0 broken
