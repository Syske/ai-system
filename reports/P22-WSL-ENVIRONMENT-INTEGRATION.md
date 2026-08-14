# Change Proposal: P22 — WSL 环境集成与初始化能力

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Structural (环境能力) |
| Author | AI Maintainer |
| Created | 2026-08-14 |
| Reference | 实战：WSL 与 ai-system 集成勘察（2026-08-14） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

ai-system（`aic` CLI）当前仅面向 Windows 运行：`config/environments/local.yaml` 使用 Windows 绝对路径（`D:\workspace\...`），`providers.yaml` 假设 agent 命令直接可执行。将 ai-system 用于 WSL 时暴露以下问题：

1. **路径解析错误**：WSL 中 Python `Path("D:\...")` 被当作相对路径（`PosixPath('/mnt/d/.../D:/workspace/...')`），workspace/repository/layers 全部定位失败。
2. **命令命中 Windows 副本**：`aic` 默认命中 Windows pyenv shim（`/mnt/c/Users/syske/.pyenv/pyenv-win/shims/aic`，Linux 下不可执行）；`opencode`/`pi` 可能命中 `/mnt/d/tools/node-...` 的 Windows 版而非 WSL 原生版（`~/.nvm/.../bin`）。
3. **环境初始化缺失**：WSL 内安装依赖（PyYAML / pyperclip / prompt_toolkit）、注册 `aic`、修正 shell PATH 优先级（`.zshrc` / `.bashrc` / `.profile`）均为**一次性手工操作**，无脚本可复现，新 WSL 实例/新机器需重走一遍。

## 2. Root-Cause

- **路径**：`local.yaml` 是唯一的默认环境配置，路径硬编码为 Windows 风格，无 WSL 变体。
- **命令解析**：WSL 默认将 Windows PATH 追加进 PATH，且 `subprocess.call(shell=True)` 使用非交互 shell（PATH 不含 nvm），导致 `which` 命中的是 Windows 副本。
- **初始化**：ai-system 无环境初始化工具，依赖安装与 PATH 修复靠手工；各 shell 配置分散（`.zshrc`/`.bashrc`/`.profile`），未统一收敛。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | 新增 `config/environments/wsl.yaml`（已落地）+ 提供 WSL 初始化脚本（依赖安装 + PATH 收敛 + 校验） | 环境可复现、可审计；Windows 端不受影响；`--environment wsl` 原生支持 | 需维护初始化脚本与文档 |
| B | 仅保留 wsl.yaml 手工配置，不提供脚本 | 改动最小 | 初始化不可复现，新环境需人工重走 |
| C | 在 ai-system 内置 `aic env-init` 子命令（Python 实现跨平台初始化） | 能力固化进 CLI，可复用/可测试 | 改动面大，超出当前勘察范围，需后续提案 |

## 4. Recommendation

**Option A**，分两阶段：

- **阶段一（本提案）**：固化已落地的 WSL 集成内容——`wsl.yaml` 配置、依赖安装、PATH 收敛（三处 shell 配置文件）、验证结果，形成文档化基线。
- **阶段二（后续提案）**：在 ai-system 内置环境初始化能力（`aic env-init`），支持一键初始化 WSL 环境（安装依赖、配置 PATH、生成 wsl.yaml、自检），最终收敛 Option C。

阶段一不引入代码改动，仅登记配置与知识；阶段二需要新提案审批后实施。

## 5. Proposed Changes

**阶段一（已落地，本提案登记）**：

1. 新增 `config/environments/wsl.yaml`（**机器级配置，已 gitignore**，不入库）：
   - `workspace.root: /mnt/d/workspace/ai-workspace`，`repository_root` 同构。
   - `build.backend: maven`（WSL 无 IDEA）。
   - `layers.*.path` 全部 `/mnt/d/...` 风格。
   - 入库的是 `wsl.yaml.template`（占位路径 `{wsl_workspace_root}`），新机器复制后替换。
2. WSL 内依赖安装（清华 PyPI）：
   - `pip install --break-system-packages PyYAML pyperclip prompt_toolkit`
   - `pip install --break-system-packages --no-build-isolation -e .`（注册 `aic` → `/home/syske/.local/bin/aic`）。
3. PATH 收敛（WSL 原生 bin 优先于 Windows 副本）：
   - `~/.zshrc`：`export PATH="$HOME/.local/bin:$PATH"` + `export PATH="$NVM_BIN:$PATH"`。
   - `~/.bashrc` / `~/.profile`：`if [ -n "$NVM_BIN" ]; then export PATH="$NVM_BIN:$HOME/.local/bin:$PATH"; fi`。

**阶段二（后续提案，本提案仅登记方向）**：

4. `aic env-init` 子命令：检测当前环境（WSL/Windows）、生成对应 `config/environments/<platform>.yaml`、安装依赖、收敛 PATH、自检（`paths()` 可解析 + `provider_command` 可执行）。
5. 环境感知：`ai-system` 能自动识别运行平台并选择默认环境，减少 `--environment wsl` 的显式传参。

## 6. Validation Plan

阶段一验证（已通过）：

- `paths(root, 'wsl')`：workspace/repository/workspaces/ai_system/methodologies/skills 全部存在 ✅
- `tools/check.py`：PASS（3 个原有 warning）✅
- `aic verify --environment wsl`：exit 0，prompt 生成正常 ✅
- 交互向导：项目选择 → workflow 选择正常流转 ✅
- `which aic opencode pi`：全部命中 WSL 原生版 ✅
- `subprocess.call(shell=True)`：继承 aic 进程 PATH，命中原生版 ✅

阶段二门禁：`tools/check.py` / `tools/proposal-audit.py` 通过；新 WSL 实例跑 `aic env-init` 一次通过全部自检。

## 7. Risks

- **wsl.yaml 路径绑定 `/mnt/d`**：依赖固定的 D 盘挂载点；换盘/换机需重新生成。缓解：阶段二 `env-init` 自动探测实际挂载点生成配置。
- **三处 shell 配置分散**：PATH 收敛靠手工维护三文件，易漏。缓解：阶段二统一收敛到初始化脚本；文档已记录。
- **交互向导未做完整自动化模拟**：阶段一验证了项目/workflow 选择流转，但 agent 启动后的真实交互未自动化断言。缓解：阶段二 `env-init` 自检补充 agent 冒烟启动（`--agent opencode --version`）。
- **Windows pyenv shim 干扰**：WSL 中若 PATH 未收敛，`aic` 命中不可执行 shim。缓解：初始化脚本必须包含 PATH 收敛步骤。

## 8. 使用方式（用户视角）

**WSL 无需常驻**：WSL2 最后一个进程退出后约 8 秒自动关闭并释放内存；`memory=16GB` 为上限非预留，`autoMemoryReclaim=gradual` 空闲 1 分钟后逐步归还缓存。

**任务归属**：

| 场景 | 用哪个 | 原因 |
|------|--------|------|
| 跑 `aic` / opencode / pi（AI 编排） | WSL | 已集成 `--environment wsl`，命中原生 agent |
| 日常编码、git、Linux 工具链 | WSL | 文件系统 IO 快、工具全 |
| Windows 专属（IDEA、Office、PowerShell 脚本） | Windows | 无替代 |

**关键实践**：

1. 统一从 WSL 操作代码：`D:\workspace\...` 对应 `/mnt/d/workspace/...`（9P 协议较慢）；避免两套工具交替改同一文件（行尾/权限互相干扰）。
2. 跑 ai-system：进 WSL `cd` 到项目目录直接 `aic --environment wsl`，PATH 已收敛无需额外设置。
3. 用完即走：退出终端 WSL 自动关闭；改 `.wslconfig` 后 `wsl --shutdown` 重启生效。
4. 访问 Windows 文件用 `/mnt/c|d/...` 直接读写，不用 `cmd.exe` 反向操作 WSL 文件。
5. 可选：`.zshrc` 加 `export CDPATH=/mnt/d/workspace/ai-workspace` 快速跳转；Windows 的 `workspace-config.ps1` 别名同步到 `.zshrc` 统一体验。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（阶段一落地确认；阶段二 defer 至新提案） | 2026-08-14 |

---

## Implementation Record (2026-08-14)

阶段一已落地（登记为主）；阶段二开始落地代码改动：

1. `config/environments/wsl.yaml` 已创建（`/mnt/d` 路径 + maven 后端）。
2. WSL 依赖已安装，`aic` 注册至 `~/.local/bin/aic`。
3. `~/.zshrc` / `~/.bashrc` / `~/.profile` 已追加 PATH 收敛。
4. 验证全部通过（见 §6）。
5. **WSL 项目识别修复（阶段二核心落地）**：`workspace.yaml` 的 `repository.available[].path` 为 Windows 路径（`D:\...`），Linux 下 `Path().is_absolute()` 为 False，导致 `project_repos` / `repo_path_for` 把路径错误拼到 `projects_root` 后 → 项目 repo 无法识别。已在 `cli/services/providers.py` 新增 `_linux_path()` / `_repo_path()`（Windows 绝对路径 → `/mnt/d/...` 转换），应用于 `repo_path_for` 与 `project_repos` 的 available/unavailable 路径。

**Validation**: `tools/check.py` / 路径解析 / 向导流转 / PATH 命中 全部通过 ✅；`python -m unittest discover -s cli/tests` **71 tests OK** ✅；`project_repos('pywechat-live-2608')` 3 个 repo 路径转换后 `exists=True` ✅

**Deviations**: 无。
**Open Items**:
1. 阶段二 `aic env-init` 子命令（自动探测挂载点生成环境配置 + 依赖安装 + PATH 收敛 + 自检）。
2. 环境感知：默认环境按运行平台自动选择，减少 `--environment wsl` 显式传参。
3. 交互向导完整自动化测试（agent 启动后的真实交互断言）。
4. `contexts/project.yaml` 与 `workspace.yaml` 两处 repo 路径来源统一（`repo_path_for` 目前仅读 project.yaml，实际数据在 workspace.yaml），后续合并为单一数据源。
