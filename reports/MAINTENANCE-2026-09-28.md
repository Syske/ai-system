# 系统巡检报告 — 2026-09-28（on-demand / env-init 误报专项）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- Scope: CLI 触发层 —— aic 反复提示「环境未初始化」
- 日期: 2026-09-28
- 用户报障: 「解决每次执行 aic 都提示初始化环境问题：`config/environments/local.yaml`」

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 39 | Files: 39 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 97 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 39 | 39 | = |
| Workflows | 16 | 16 | = |
| RFC | 14 | 14 | = |
| Governance | 63 | 63 | = |
| Templates | 27 | 27 | = |

（上期快照 timestamp: 2026-09-24T11:20:13.133852）

---

## 二、巡检发现（AI 填写，按严重度分级）

<!-- 高 / 中 / 低 / 信息 -->

### 中 1 — aic 入口把「可选的 workspace 层配置」当作初始化前提，导致每次运行误报

**现象**：每次执行 aic 均输出

```
⚠️  环境未初始化（配置缺失）：
   - /home/syske/ws/ai-workspace/ai-system/config/environments/local.yaml
是否现在初始化环境？(y/N):
```

**根因**：`cli/main.py` 的 `_env_uninitialized()` 要求**两份配置都在**才算已初始化：

```python
ws_cfg   = ai-system/config/environments/local.yaml    # workspace 层
home_cfg = ~/.config/ai-system/env.yaml                # 机器层
return not ws_cfg.exists() or not home_cfg.exists()
```

而 P29（`reports/P29-HOME-ENV-CONFIG.md` §2）已确立**机器层 `~/.config/ai-system/env.yaml` 为权威位置**，
workspace 层 `config/environments/{env}.yaml` 是**可选兜底**——`README_MIGRATION.md:16-18` 与
`config/environments/local.yaml.template:1-11` 均写明「缺失属正常，且该文件在仓库内被 gitignore，
仓库级清理会删除它」（2026-09-24 `git clean -fdx` 事故已实证）。

本机实测：机器层 env.yaml **存在且完整**（workspace.root / build / k8s / bugfix.mode 齐备），
workspace 层 local.yaml **不存在**（即正常状态）→ 检测误判 → 每次提示。

**为何不能只补文件**：`local.yaml` 被 `.gitignore:22` 忽略且位于仓库内，任何一次仓库级清理即再次消失
（同根因已发生过一次）。B 方案（跑一次 `env-init` 生成文件）治标不治本，用户已按 A 方案处置。

**归属**：P36 触发层 T-b（`reports/P36-SETUP-ENV-INIT-SCAFFOLD.md` §5 改动项 6）写于 P29 之前，
其「两份配置存在性」判据未随 P29 的权威位置迁移同步 → doc-vs-reality 漂移。

### 中 2 — 运行态日志落在仓库内，阻塞 check.py 与 CLI 单测

`ai-system/logs/develop-20260924-180000.md`（2026-09-24 develop 运行记录）位于**仓库内**，
违反 `AGENTS.md`「`logs/` 在工作区层、仓库外」约定。后果：

- `tools/check.py` → FAIL（1 error）
- `python3 -m unittest discover -s cli/tests` → 1 FAILED
  （`test_protected_paths.test_real_repo_is_clean`）

处置：已按用户确认迁至 `<workspace>/logs/develop-20260924-180000.md`，仓库内 `logs/` 目录清空移除。

### 低 — 未修复前的次生症状（已随中 1 一并消除）

修复前每次 aic 提示若选 `y`，`env_init()` 会在仓库内生成 gitignored 的 `local.yaml`；
`config/maintenance.yaml` 2026-09-21 已记录同类观察（`local.yaml` 残留 `/tmp` 测试路径、
`projects_root` 指向不存在目录）。该残留在 A 方案下不再被触发。

### 信息 — 提案与开放项盘面（proposal-audit）

5 开放提案（P42 / P46 / P67 / P68 / P73）、5 open action items
（P22×2 / P26 / P28 / P65-C2）。与 2026-09-21 盘面相比新增 P67 / P68 / P73，
P22×2 / P26 / P28 / P65 延续。均属已知在途项，本次专项不涉其处置。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

| 抽查项 | 结论 | 说明 |
|---|---|---|
| workflows/*.md 八段完整与顺序 | 通过 | 16 workflow，structure check 0 违规 |
| config/workflows/*.yaml 注册表最小化 | 通过 | 仍为 name/workflow/runtime 三键，无回胀 |
| 引用路径存在性（standards/ loaders/ templates/prompts/ cli/commands/） | 通过 | path-audit 0 broken |
| AGENTS.md 工作区结构图 vs 实际布局 | 通过 | `logs/` 工作区层口径与实际一致 |
| 机器层/工作区层环境配置权威位置 | **失败→已修** | 见 §二 中 1；`cli/main.py` 判据与 P29 契约冲突 |
| 运行态日志位置 | **失败→已修** | 见 §二 中 2 |
| 状态卫生（`workspaces/.aic-state.yaml` 引用） | 通过 | 引用项目/change 均存在 |
| run-log 覆盖（未提交改动 vs 日志） | 通过 | 本次两处改动均属本次已归档 run |
| 提案遗留 | 通过（记录） | 5 开放提案 / 5 open items，见 §二 信息 |

---

## 四、修复动作与建议清单（AI 填写）

### 本次已实施（用户逐项确认）

| # | 动作 | 层级 | 验证 |
|---|---|---|---|
| 1 | `cli/main.py` `_env_uninitialized()` / `_offer_env_init()`：判据收敛为**仅机器层 `~/.config/ai-system/env.yaml`**，与 P29 权威位置对齐；缺失清单同步只列机器层路径 | 触发层（cli） | `test_main_p36` 6 用例 OK；实机 `_env_uninitialized() == False`；aic 启动不再提示 |
| 2 | `cli/tests/test_main_p36.py`：`test_missing_workspace_config` → `test_missing_home_config`；新增 `test_workspace_layer_optional`（workspace 层缺失不算未初始化） | 测试 | 6/6 OK |
| 3 | 迁移 `ai-system/logs/develop-20260924-180000.md` → `<workspace>/logs/`，移除仓库内 `logs/` 目录 | 运行态归位（经用户确认） | check.py PASS；单测 625 OK |

### 门禁结果（修复后）

- `tools/check.py` → PASS（2 warning，既有 P41/P42/P46 提示类）
- `python3 -m unittest discover -s cli/tests` → **625 OK**（修复前 624 中 1 FAILED）
- `tools/quick-check.py` → verdict OK / findings 0
- `tools/path-audit.py` → 0 broken
- `tools/repo-lint.py` → BLOCKERS 0 / ERRORS 0 / WARNINGS 97（基线内，无新增类别）

### 建议（仅记录，未实施 —— 结构性变更走提案流程）

1. **P36 触发层判据回写文档**：`reports/P36-SETUP-ENV-INIT-SCAFFOLD.md` §5 改动项 6 仍写
   「检测 workspace `local.yaml` + 机器层 `env.yaml` 存在性」。代码已改，建议在该提案补
   Implementation Record 说明 2026-09-28 判据收敛（避免后人按旧文案「修回去」）。
2. **`aic-env-init.md` 措辞对齐**：Outputs 段仍以「workspace + 机器层」并列描述，
   未标明 workspace 层为可选兜底；建议下一批次文档小修时统一。
3. `tools/path-audit.py` 的 `FALSE_POSITIVES` 含 `config/environments/local.yaml`——
   该条目仍有必要（文档引用合法），无需清理。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-24 | OK | 0 |
| 2026-09-28 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 5 开放提案 / 5 open action items
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P46-TR5-DEBT-VALIDATION-MARKER.md
  - 开放: P67-STRUCTURAL-SMELL-CAPABILITY.md
  - 开放: P68-WORKQUEUE-HANDOVER.md
  - 开放: P73-CODE-REVIEW-HISTORY-REENTRY.md
  - P22-WSL-ENVIRONMENT-INTEGRATION.md:143 交互向导完整自动化测试（agent 启动后的真实交互断言）→ 仍开；2026-09-21 已有临时 mock 扫描（全目标循环检测），但未入库为常驻交互测试。
  - P22-WSL-ENVIRONMENT-INTEGRATION.md:144 `contexts/project.yaml` 与 `workspace.yaml` 两处 repo 路径来源统一（`repo_path_for` 仍只读 project.yaml，实际数据在 workspace.yaml）→ 仍开（季度候选 C；P58 已使 workspace.yaml 成为容器映射权威源，剩余为 `repo_path_for` 收口）。
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P28-CHANGE-ID-GENERATION.md:46 D：AI 可选生成（skill 层落点）——触发条件未到（不引入 wizard LLM，Evolution Principle）
  - P65-C2-PROFILE-SEMANTICS.md:298 C2（按需）：若业务侧提出「门禁须与 IDE 行为同源」，按 CI/批处理形态引入 IDEA 引擎基线（`format.sh`/`format.bat`，需解析 stdout 取代退出码、并处理单实例互斥与冷启动成本）—— 见 §C2 二审
