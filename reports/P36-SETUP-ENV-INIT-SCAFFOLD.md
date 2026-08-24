# Change Proposal: P36 — 初始化脚本完善（--env-init 补齐目录骨架 + 引导指定代码仓库）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix（工具行为，初始化脚本 tools/setup.py + aic-env-init 命令文档） |
| Author | AI Maintainer |
| Created | 2026-08-25 |
| Reference | 用户反馈（maintain on-demand/workflows 巡检后续）：初始化脚本不完善——未创建必要文件夹、未引导用户指定代码仓库、未生成 workspaces/repositories 等目录 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

`tools/setup.py` 声明完整能力（docstring 6 步），但 `--env-init` 分支（`aic env-init` / bootstrap 调用的推荐入口）**只生成两份配置**，跳过 scaffold / repo links / baseline / audit（`env_init()` 注释明示 "skips scaffold / repo links / baseline / audit"）。后果：

1. **必要文件夹未创建**：workspaces/ projects/ repositories/ methodologies/ extensions/（`BASE_DIRS`）与 ai-system 的 metrics/ logs/（`ensure_runtime_dirs`）在 `--env-init` 下全部不建；新机器按推荐路径初始化后目录缺失（本机实测 extensions/、logs/ 缺失）。
2. **未引导用户指定代码仓库**：`detect_repos()` 只扫 workspace 根**直接子目录**（`iterdir()`），且 `SYSTEM_DIRS` 排除表过滤；真正的代码仓库多在任意外部路径（如 `/mnt/d/code/xxx`、`~/code/xxx`），脚本**没有任何交互提示让用户输入外部仓库路径**，`link_repos()` 只能链接 workspace 根下现成目录 → projects/ 无法被引导填充。
3. **workspaces/repositories 等目录缺失**：同 1，scaffold 只存在于完整流程；`--env-init` 不跑（本机 workspaces/repositories 为历史遗留手建，新机器走 `--env-init` 则全缺）。

## 2. Root-Cause（根因分析）

`--env-init` 被设计为「配置聚焦」模式（aic-env-init.md Guardrails 明示 provisioning 归属完整 `setup.py`），但**新机器初始化路径恰恰走 `--env-init`**（bootstrap workflow Context 指明「config 缺失时 invoke `tools/setup.py` 来 provision」；命令推荐入口即 env-init）——配置与目录骨架被硬拆分到两个入口，用户按推荐路径执行时目录永远不建。另有独立缺陷：repo 引导仅覆盖 workspace 根内目录，无任意路径输入能力。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. env-init 补齐目录骨架 + 交互引导外部仓库（Recommended）** | `env_init()` 增加 `scaffold()` + `ensure_runtime_dirs()`（幂等，非破坏）；`link_repos()` 增加「输入外部仓库路径（逗号分隔，可多个）」步骤逐个链接进 projects/（`--non-interactive` 跳过）；命令文档同步更新 | 最小、幂等、与新机器初始化路径一致；目录创建与配置生成解耦但同入口交付 |
| B. 引入独立 `aic-bootstrap-dirs` 命令 | 新增菜单入口专做目录/仓库引导 | 增入口面（menu.yaml + 命令 + 文档 + 测试），职责本已属 setup.py，属重复轮子（Evolution Principle 反对） |
| C. 仅改文档（指引用户手动建目录 + 手敲 link） | 零代码 | 未根治：新机器仍手动犯错，摩擦持续（与 P35 同理，重复踩坑留日志） |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**。理由：
1. **最小变更**：复用既有 `scaffold()` / `ensure_runtime_dirs()` / `link_repos()`，仅在 `--env-init` 分支补调用 + 加一个外部路径输入步骤；无新命令、无新目录、无契约改动。
2. **根因对齐**：摩擦出自「推荐入口不建目录」；让 env-init 交付完整骨架直击。
3. **幂等安全**：所有步骤非破坏（存在即跳过），重跑无副作用，符合 aic-env-init Guardrails「Never delete or overwrite existing config」。
4. **Evolution Principle**：不新增入口（B），不靠文档补丁（C）。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改**；批准后按 OPERATIONS §12 Implement 阶段执行。

1. `tools/setup.py` — `env_init()`：在配置生成后调用 `scaffold(workspace_root)` + `ensure_runtime_dirs()`；打印创建的目录清单。
2. `tools/setup.py` — `link_repos()`：交互模式增加「指定外部仓库路径（可多个，逗号分隔）」提示 → 逐个存在性校验 + `_create_link` 进 projects/；`--non-interactive` 跳过；路径校验（存在、非 projects/ 自身、非 ai-system）。
3. `cli/commands/aic-env-init.md`：Guardrails 更新——`--env-init` 亦 scaffold 基础目录（workspaces/projects/repositories/methodologies/extensions + ai-system metrics/logs）并引导仓库链接（交互模式）。
4. 测试：`cli/tests/test_maintain_tools.py` 或新增 `tools` 侧用例——env-init 幂等（重跑不重复创建）、scaffold 创建清单、link_repos 外部路径链接（tempdir 夹具）。
5. 文档：P36 状态与 PROPOSALS.md / reports/README.md 登记。

## 6. Validation Plan（如何验证）

- 在临时 workspace（tempdir）跑 `python tools/setup.py --env-init --workspace <tmp>` → 断言 5 个 BASE_DIRS + metrics/logs 创建；重跑断言幂等（created=0）。
- `link_repos` 外部路径用例：tmp 外建 fake repo（含 .git），交互注入路径 → projects/ 下 symlink 出现。
- `python -m unittest discover -s cli/tests` 全 PASS。
- `python tools/quick-check.py` / repo-lint / path-audit 全绿（无回归）。
- 真实工作区重跑 `--env-init`：extensions/、logs/ 补齐，无破坏。

## 7. Risks（风险与缓解）

- 风险低：全部步骤幂等非破坏，仅补目录 + 交互引导，无契约/结构影响。
- 缓解：链接前校验目标存在性 + 排除自链（projects/ 自身、ai-system/）；交互输入用 `ask_path`（有默认值），`--non-interactive` 无输入路径则跳过。
- 遗留：`--env-init` 仍不跑 metrics baseline / path-audit（属完整流程，保持现状，避免 env-init 过重）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-08-25 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）
