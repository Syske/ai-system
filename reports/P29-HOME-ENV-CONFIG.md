# Change Proposal: P29 — 机器层环境配置迁移至 ~/.config（跨平台原生，首启按系统生成）

| Field | Value |
|---|---|
| Status | **Approved**（用户决策 2026-08-23，随 maintain 修复批次实施） |
| Type | Structural (环境配置契约：机器层 home / 工作区层拆分) |
| Author | AI Maintainer |
| Created | 2026-08-23 |
| Reference | P22 阶段二（Option C `aic env-init` 跨平台初始化）；用户决策：默认全部走 `~/.config`，特殊情况（如 WSL）用户自行编辑 |
| Process | OPERATIONS §12 Change Management（配置布局契约级变更，实施随用户确认落地） |

---

## 1. Problem

`config/environments/local.yaml`（gitignored）位于**共享 workspace 树内**（D: 盘 Windows + WSL 共用）：

1. build 机器配置（java_home `D:\tools\java\jdk8`、idea64.exe `C:/Program Files/...`）为单份共享文件，
   Windows 填的路径 WSL 用不了；任一侧重生成/编辑会互相覆盖（跨系统被覆盖）。
2. 多人共用同一 workspace 时，同平台不同机器也冲突（同一文件只能有一份 java_home）。
3. P22 已确认此问题（`reports/P22-WSL-ENVIRONMENT-INTEGRATION.md`），Option C（跨平台初始化子命令）搁置待后续提案——本提案即该落点。

## 2. Clarified Design（用户决策）

**默认全部走 `~/.config`，跨平台原生；特殊情况（如当前 WSL）用户自行修改配置。**

- **机器层**：`~/.config/ai-system/env.yaml`（`Path.home()/".config"/"ai-system"/"env.yaml"`；
  Windows 下即 `C:\Users\<user>\.config\...`，各平台各有一份，天然互不覆盖）
  - 首启由 `tools/setup.py` 按系统检测生成（windows / wsl / linux），探测常见 JDK/Maven 位置，
    生成后提示用户按需编辑（特殊情况如 WSL 用 `/mnt/d/...`）
  - 内容：`workspace.root`（工作区锚定）+ `build.*`（机器构建路径）
- **workspace 层**：`config/environments/{env}.yaml` 保留工作区级共享项（`bugfix.mode`、`layers` 等），
  并作为旧版 fallback（build 段在机器层未配置时生效）——不破坏既有部署
- **读取合并顺序**（`cli/services/environment.py` 单点实现）：
  `机器层 home（优先） → workspace local.yaml（兜底） → 自动推导`
- **布局派生不变**：workspace 为锚，repository/workspaces/outputs/methodologies/extensions 均据此推断
  （ad618bc 已落地；`_normalize_path` 保证显式 Windows 值在 WSL 下安全）
- 测试/多配置场景：`AI_HOME_CONFIG` 环境变量可覆盖 home 配置路径

## 3. Options

- **A. 机器层迁至 home（采纳）**：真 per-machine/per-user，多平台多用户零冲突；ops 上配置不在
  workspace 内可见，靠首启生成 + 注释引导
- **B. workspace 内分平台文件**（local.wsl.yaml / local.windows.yaml）：可见简单，但同平台多人共享
  仍冲突；跨系统语义仍在共享树内
- **C. 维持现状**（仅文档约定"各平台手动改"）：不解决覆盖问题

## 4. Recommendation

采用 **Option A**：与用户决策一致（默认走 ~/.config，特殊情况自行编辑），且与 P22 Option C 衔接。

已知取舍：`bugfix.mode` 等工作区共享键若被用户在 home 层覆盖，会出现跨平台漂移——文档已在
local.yaml 注明"工作区级共享项留 workspace 层"；home 覆盖为显式特例。

## 5. Implemented Changes

- [x] `cli/services/environment.py`：`home_config_path()`（AI_HOME_CONFIG 可覆盖）、`load_home_environment()`、
  `_deep_merge()`（home 优先递归合并）、`load_merged_environment()`；`paths()`/`resolve_environment()`
  改读合并配置（单点，全部消费者零改动）
- [x] `tools/setup.py`：`detect_platform()`（windows/wsl/linux）、`_probe_build_paths()`（常见 JDK/Maven 探测）、
  `generate_home_env()`（首启非破坏生成，已存在即跳过）；main() 接入
- [x] `config/environments/local.yaml` + `local.yaml.template`：头注更新（机器层 home 优先 / 本文件兜底 / 布局自动推导）
- [x] `templates/runtime/runtime-bootstrap.md` Phase 2：配置源顺序（机器层 → workspace 层 → 推导）
- [x] `skills/skill-author/SKILL.md`：机器路径归属与 `resolve_environment` 合并说明更新
- [x] `cli/tests/test_home_env.py`：9 用例（路径/合并/合并读取/生成非破坏）

## 6. Validation Plan

- `python -m unittest cli/tests/test_home_env.py` → 9 OK（平台检测识别 wsl）
- `python -m unittest discover -s cli/tests` → 全量回归
- `python tools/repo-lint.py --repo-root .` / `python tools/check.py` / `tools/path-audit.py` 全绿

## 7. 后续（未实施，触发再说）

- 当前机器（WSL）尚未生成 home 配置——现有 workspace local.yaml（backend=idea 等）继续生效为 fallback；
  用户下次运行 `tools/setup.py` 时首启生成（非破坏），或手动创建 `~/.config/ai-system/env.yaml` 接管
- `aic env-init` 子命令化（P22 Option C 完整形态）——视实际使用频率再评估

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（决策：默认全部走 ~/.config，跨平台原生；特殊情况如 WSL 用户自行编辑） | 2026-08-23 |
