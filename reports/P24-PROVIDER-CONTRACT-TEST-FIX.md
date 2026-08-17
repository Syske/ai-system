# Change Proposal: P24 — Provider Wizard 契约测试夹具修复（win32 平台 check.py 回归）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix（测试夹具补全 + provider 契约韧性） |
| Author | AI Maintainer |
| Created | 2026-08-17 |
| Reference | MAINTENANCE-2026-08-17（R1：check.py 完整性门禁回归，exit 1） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

2026-08-17 维护巡检（on-demand）运行完整性门禁 `python tools/check.py` 返回 **exit 1**：

```
ERROR: test_reads_repository_mapping (test_skill_launcher.TestProjectRepos)
  File "cli/services/providers.py", line 47, in _repo_path
    return wizard.projects_root / path
AttributeError: 'FakeWizard' object has no attribute 'projects_root'
Ran 71 tests ... FAILED (errors=1)
```

**影响**：完整性门禁（OPERATIONS §11）失败。CI/发布前 gate 无法通过，属于**平台相关回归**——同一提交在 WSL（Linux）下 71/71 通过，在 Windows（win32）下 1 error。

## 2. Root-Cause

- P22 提交 `6035d19` 为 `_repo_path`（`cli/services/providers.py:40-48`）新增 `wizard.projects_root` 依赖（win32 分支 `return wizard.projects_root / path`），以支持 WSL 路径识别与项目-仓库映射（ADR-0008）。
- 随该改动，`project_repos` → `_repo_path` 的 **wizard 契约属性集**从 `{workspaces, target_name, ...}` 扩展为需含 `projects_root`。
- 测试夹具 `FakeWizard`（`cli/tests/test_skill_launcher.py:175`）**未同步补该属性**。
- `sys.platform == "linux"` 分支（`_linux_path`）不访问 `projects_root` → WSL 下测试仍绿，掩盖缺陷；win32 分支必触达 → 仅 Windows 平台暴露。**平台相关性的测试盲区**导致门禁在 WSL 下误报通过。
- 本次巡检在 Git Bash（win32）环境运行，恰好暴露。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | 测试夹具补 `projects_root`（与 `workspaces` 对齐同根），并补强度：新增 `tests/` 中 `_repo_path` 对 win32/Linux 双分支的显式用例 | 修复最小；双平台回归有保护；不动生产代码 | 需手工维护夹具与生产契约同步 |
| B | 生产代码 `_repo_path` 对缺 `projects_root` 的 wizard 优雅降级（`getattr`/默认根） | 不再抛异常 | 掩盖契约缺陷；生产代码为测试让步，风险更高 |
| C | 仅补夹具属性（不补用例） | 最小改动 | 不防"再引入平台分支依赖但夹具漏跟"的复发 |

## 4. Recommendation

**Option A**，理由：

1. 根因在**测试夹具未同步生产契约**，而非生产代码错误——修夹具即是对症最小改动。
2. `projects_root` 是 provider 契约的必要属性（ADR-0008 项目-仓库映射），不该被生产代码容忍缺失（Option B 弱化契约、掩盖问题）。
3. 附加双分支用例把"平台盲区"固化为回归测试，防复发（本次 R1 正是被 platform 分支掩盖的典型）。

## 5. Proposed Changes

1. `cli/tests/test_skill_launcher.py` 的 `FakeWizard` 补 `projects_root = root`（与现有 `workspaces = root / "workspaces"` 同一临时根）。
2. 校验 `test_missing_yaml_returns_empty` 等其他使用 `project_repos`/`_repo_path` 的夹具是否缺属性（缺则一并补）。
3. 新增 `_repo_path` 双平台用例（documented via pytest monkeypatch 或直接验证 `_linux_path`/`projects_root` 两分支）：
   - Linux 分支：路径转换走 `_linux_path`，不依赖 `projects_root`；
   - win32 分支：绝对路径直达、相对路径经 `projects_root` 拼接。
4. 运行 `python tools/check.py` 全量门禁验证（71 tests 应全绿，0 error / 0 warning）。

## 6. Validation Plan

- `python tools/check.py` → exit 0（当前为 1）。
- `pytest cli/tests/ -q` → 71 passed（当前 70 passed / 1 error）。
- `python tools/repo-lint.py --repo-root .` → 0 BLOCKER / 0 ERROR（WARN 27 不变，无新增）。
- git status 仅含本提案涉及文件。
- 双平台确认：WSL 与 win32 各跑一遍 check.py（修复后不应再依赖平台）。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 夹具属性与真实 wizard 不一致，测试假绿 | 用例锚定 `providers.py` 实际访问路径（只测真实调用链） |
| 新增用例过度耦合 `_repo_path` 实现细节 | 用例聚焦"输入→输出"双分支行为，不 mock 内部 |
| 改动面大于最小 | 严格限于测试文件 + 必要用例；生产代码零改动 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-17 |

---

## Implementation Record (2026-08-17)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `cli/tests/test_skill_launcher.py`：`FakeWizard` 在 `test_reads_repository_mapping` 与 `test_missing_yaml_returns_empty` 补 `projects_root = root`（与 `workspaces` 同根）。
2. 新增回归用例 `test_repo_path_dual_platform`：
   - Linux 分支用 `NoRootWizard`（无 `projects_root`）断言不依赖该属性（`_linux_path` 直返）；
   - win32 分支断言相对路径经 `wizard.projects_root` 拼接；
   - 绝对路径直通、空路径→None；`_linux_path` 单测（`D:\workspace\\svc-a` → `/mnt/d/workspace/svc-a`）。

**Validation**:
- `python tools/check.py` → **exit 0**，72 tests PASS，**0 warning**（修复前 71 中 1 error FAIL exit 1）。
- `python tools/repo-lint.py --repo-root .` → 0 BLOCKER / 0 ERROR / **27 WARN（无新增）**。
- `python tools/path-audit.py` → **0 broken**。
- 单平台验证：win32 全绿；Linux 分支经 mock + `_linux_path` 单测覆盖（无需真 WSL）。

生产代码零改动（仅测试夹具 + 用例）；双平台门禁按 P24 §6 目标达成。