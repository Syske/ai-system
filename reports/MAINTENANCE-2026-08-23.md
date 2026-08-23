# 系统巡检报告 — 2026-08-23（weekly）

- 类型: 系统巡检（MAINTENANCE）
- 模式: weekly
- 范围: ai-system + workflow 系统（工具校验 / 周度巡检 / 治理一致性抽查 / 知识生命周期）
- 日期: 2026-08-23
- 环境: WSL（默认 `python` shim 指向 Windows pyenv 不可执行，全部工具用 `/usr/bin/python3` 运行正常，沿用 08-20 记录）
- 调度: `.aic-state.yaml` 显示 next_maintenance=2026-08-27（08-20 on-demand 设定），用户于 08-23 显式发起 weekly 巡检——以用户指令为准

---

## 一、工具校验结果

| 工具 | 结果 | 说明 |
|---|---|---|
| quick-check | verdict **OK**（0 findings） | 记录至 `metrics/quick-check-2026-08-23.json`；lint 25 WARN 为既有债 |
| quick-check --history | 6 snapshot 全 OK | 08-13/14/17/18/20/23 均 OK，趋势平稳 |
| repo-lint | **0 BLOCKER / 0 ERROR / 25 WARN** | 与 08-20 持平，无回退 |
| repo-metrics | snapshot 已存 | `metrics/maintain-2026-08-23.json`，见下方对比 |
| path-audit | files=253，refs=666，**0 BROKEN** | placeholders=117，known_debt=3 |
| check.py（完整性门禁，15 项） | **PASS（3 warning）** | 15 workflows / 14 commands；3 warning 均为提案类（见三.7） |
| workflow-command-audit | **0 blocker / 0 warning** | 15 workflows 八段齐全、Next 链闭合、无悬空命令引用 |
| proposal-audit | **0 gate error / 1 warn** | P28 未登记 reports/README.md 索引；2 开放提案；4 open action items |
| CLI 单测 | **123 tests OK** | `python3 -m unittest discover -s cli/tests`（4.9s） |

**结论：无 BLOCKER / ERROR，全部工具门禁通过。**

### 指标对比（vs 08-20 快照）

| 指标 | 08-20 | 08-23 | 变化 |
|---|---|---|---|
| Skills（目录） | 31 | 31 | = |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 61 | 61 | = |
| Templates | 22 | **23** | **+1** |
| 平均技能行数 | 468 | 468 | = |

Templates +1 已核对：`templates/prompts/external-ai-review.md`（P3 外部 AI 结论核查模板，
08-20 修复批次落地，快照于当日 11:39 采集、文件 12:04 落盘，故计入本期）。其余指标零变化。

---

## 二、巡检发现（weekly，按严重度分级）

### 高 / 中
无。

### 低

**L1. P28 未登记 reports/README.md 提案索引（proposal-policy §6 门禁警告）**
- 证据：`reports/PROPOSALS.md` 第 33 行已含 P28，但 `reports/README.md` 提案索引表（P6–P26）
  缺 P28 行；proposal-audit 与 check.py 均报此 warn。
- 处置：**建议就地小修**（补一行索引），待确认后执行。

**L2. P26 状态残留 Proposed，但实现已全部落地（状态同步滞后）**
- 证据（git 实证）：`cli/services/branch_parser.py` + `cli/tests/test_branch_parser.py`
  （5 用例 OK）已存在；`tools/checks/__init__.py` 含 `check_branch_parser`（check.py 第 14 项）；
  `templates/runtime/runtime-spec.md:321` Task Card `branch` 字段、`aic-trace.md:29` 复用
  ParsedBranch 契约、AI_OPERATING_RULES Workspace Discipline 分支纪律均已提交（cc96a7b 等）。
  提案 §5 的 7 个 `[x]` 项全部实证。
- 处置：**建议状态更新 Proposed → Implemented**（P26 文件 + PROPOSALS.md 同步），待确认后执行；
  2 个未勾选项为显式 defer（见下）。

**L3. 25 个 lint WARN 既有债（与 08-17/08-20 同源，无新增）**
- 构成：12 × skill 缺 workflow.md（agent-debug-diagnosis / apply-openspec / contract-maintainer /
  deepseek-share-to-md / explore / handoff / idea-build / java-maven / review /
  skill-benchmark-generator / wayfinder / agent-browser 等）、12 × 英文代码注释
  （interactive.py / menu_config.py / test_services.py / test_skill_launcher.py /
  test_state_store.py / context-audit.py）、1 × idea-build SKILL.md Maven 命令字面量。
- 处置：跟踪项，本巡检不改（技能缺 workflow.md 涉及技能架构口径，走技能维护流程）。

### 信息

**I1. skills/architecture/ 为分类目录（非技能）**
- 内含 7 个子技能（architecture-base / context-architect / design-review / platform-governor /
  provider-architect / runtime-architect / workflow-architect），无 SKILL.md——解释
  repo-metrics 计 31 目录 vs repo-lint/quick-check 计 30 SKILL.md 及 frontmatter "1 missing"。
  属已知良性差异，无需处理。

**I2. 重复块扫描（13 组 8+ 行重复）全部良性**
- workflows frontmatter 同构块（analysis/change-impact/code-review/knowledge/proposal 等）——
  P25 单一来源约定使然，属设计；architecture 分类下 context-architect ↔ design-review 共享
  boilerplate 段；`skills/implement/examples.md` 内部示例自重复（同文件 129↔201、231↔347 行），
  建议后续技能维护时顺手去重。

**I3. 扩展仓状态：codeup-submit-mr 工作树有未提交修改**
- `extensions/` 仓 `git status`：codeup-submit-mr 下 5 个文件 M（OPTIMIZATION_LOG.md /
  README.md / SKILL.md / agents/openai.yaml / scripts/submit_mr_test.py），extensions-lint
  （quick-check 内联）0 err 0 warn。属 extensions 域（非本命令架构范围），仅记录提示提交/归档。

**I4. AGENTS.md 运行目录表轻微漂移**
- `ai-system_bak_260803/` 已不存在（AGENTS.md 自述"一次性备份、非权威"，移除属预期，可顺手删行）；
  `.qoder/` 未登记（新增工具状态目录，信息级）。

### 周度项结论

| 项 | 结论 |
|---|---|
| 重复报告 | 13 组重复块，全部良性/设计使然（见 I2） |
| 依赖图 | 无真实环；3 组 doc-only mention 环（review↔review-changes、java-maven↔idea-build、explore↔explore-codebase）；层深 ≤4，符合 health 模型 |
| 孤儿资产 | **0 孤儿**：32 个 skill 目录全库可引用（含 config/workflows/cli/governance/templates/reports/rfc + skills/README + 跨技能引用）；runtime/prompt 模板无孤儿 |
| 健康分 | **12.5 / 13 ≈ 96 / 100**（良好，较 08-13 的 86 上升，见下表） |

| 维度 | 状态 | 得分 |
|------|------|------|
| 结构 / Skill 架构 / Workflow 架构 | ✅（30 SKILL.md 有效；15 workflow 全过 RFC-0003 行数门禁） | 3/3 |
| 能力分布 | ✅ 无 >60% 重叠（architecture 组共享 boilerplate 不属能力重叠） | 1/1 |
| 依赖图 | ✅ 无真实环，层深 ≤4 | 1/1 |
| 知识组织 / 治理 / 命名 | ✅（memory 11 条目结构合法、索引有效；命令 kebab-case + aic- 前缀） | 3/3 |
| 语言规范 | ⚠️ 25 WARN（较 08-13 的 35 净 -10，稳定） | 0.6/1 |
| 重复控制 | ✅（仅设计使然的 frontmatter 块 + 1 处信息级内部重复） | 1/1 |
| 状态卫生 | ✅ 项目引用全存在 | 1/1 |
| 链接卫生 | ✅ 0 broken（666 refs） | 1/1 |
| 文档一致性 | ⚠️ P28 缺 README 索引（L1）；AGENTS.md 两处信息级漂移 | 0.9/1 |

---

## 三、一致性抽查结论（逐项）

| 检查项 | 结论 | 证据 |
|---|---|---|
| 1. workflows 八段齐全且有序 + 术语与 README 选择表一致 + Runtime 引用存在 + Preconditions/Next 链闭合 | ✅ | workflow-command-audit 0/0；README 表 15 项与 workflows/ 目录、config/workflows/ 一一对应；check.py 第 3 项 config→workflow→runtime 链 PASS |
| 2. config/workflows/*.yaml 注册表保持极简（name/workflow/runtime），无 inputs/outputs/next 回潮 | ✅ | 程序化核验 15/15 文件 key 集 = {version,name,workflow,runtime}，引用目标全存在——A1 未复发 |
| 3. 引用路径存在（governance/standards/、loaders/、templates/prompts/、cli/commands/） | ✅ | path-audit 666 refs 0 broken；cli/commands/ 14 个 aic-* 文件与 audit 计数一致 |
| 4. 链接健康：projects junction/symlink | ✅ | `projects -> /mnt/d/workspace/project-resources`，target 存在且可访问 |
| 5. 文档-现实一致：AI_DEVELOPMENT_CONTRACT 架构树 / AGENTS.md 结构图 / OPERATIONS §1 | ✅（2 处信息级） | 契约树 13 个顶层目录全存在；AGENTS.md 主结构 + 运行目录表匹配（I4 两处信息级）；OPERATIONS §1 引用的 runtime/流程全部可解析 |
| 6. 状态卫生：.aic-state.yaml 项目/变更引用 | ✅ | projects（pywechat-live-2608、202610-cool-italent-sync-plus）与 workspaces/ 实存目录一致；last_project 有效 |
| 7. 提案残留（proposal-audit + 处置） | ⚠️ 见下 | 2 开放提案 / 4 open items / 1 索引警告 |

### 提案残留处置（Step 3.7）

| 残留 | 状态 | 处置 |
|---|---|---|
| P26 整体 | Proposed | **implement（已实现）→ 建议置 Implemented**（L2，实证见上；待确认） |
| P26:52 分支扩展 provider | 开放 | **defer**（原文"按需"；契约已预留，触发再评估） |
| P26:53 CI git 分支保护 | 开放 | **defer**（原文"后续"） |
| P28 整体 | Proposed | **defer**（A 已落地；B/D 触发条件未到，提案自述"维持 A、B 记入触发条件"） |
| P28:42 B slug 派生 | 开放 | **defer**（触发条件未到；需 Change Request 前置收集设计） |
| P28:44 D AI 可选生成 | 开放 | **defer**（触发条件未到；落点 skill 层） |
| P28 未登记 reports/README.md | 门禁警告 | **就地小修**（L1，补索引行；待确认） |
| --refresh-index | 已执行 | PROPOSALS.md 索引已按各 P*.md 实际标题规范化（3 行标题同步，无状态变更） |

---

## 四、修复动作与建议清单

**本次已执行（命令授权范围内，只读/工具自带）**
1. `quick-check.py` 记录 `metrics/quick-check-2026-08-23.json`
2. `repo-metrics.py` 快照 `metrics/maintain-2026-08-23.json`
3. `proposal-audit.py --refresh-index`：PROPOSALS.md 标题规范化（3 行，与源文件标题对齐，无状态改动）
4. `reports/README.md` 登记本报告（README 自身约定「新报告入目录即登记」，check.py 门禁要求）

**修复批次已落地（用户确认，L1）——提示词路径绝对化 + Windows 路径归一化**
- `cli/services/prompt_builder.py`：`_skeletonize_runtime` 骨架引用改为绝对路径（`Full runtime template: {root}/{runtime}`）；
  主链可选能力路径按存在性解析（`skills/...`→ai-system 根、`extensions/...`→workspace 根，修复双基准不一致）；
  workflow/command 渲染注入 `ai_system_root` / `workspace_root` 绝对根
- `templates/prompts/workflow.md` / `command.md`：头部 `ai-system/...` 相对引用改为 `{{ai_system_root}}/...` 绝对引用，
  新增 **Path Anchor** 段（两个绝对根），覆盖正文/模板内所有相对引用
- `cli/services/environment.py`：新增 `_normalize_path`（Windows 盘符路径 `D:\...` → `/mnt/d/...`），
  `_path` 与 `ai_system_root($AI_SYSTEM_ROOT)` 统一归一化——封堵 P22 类「伪目录」复发（`/home/.../D:\workspace\...`）
- 验证：dev-setup/maintain/prepare 提示词重建后路径全部绝对化（含 caps 路径）；`D:\workspace\x`→`/mnt/d/workspace/x`；
  repo-lint 25 WARN 无新增 / check.py PASS / CLI 123 测试 OK

**P29 批次已落地（用户决策：机器层环境配置迁至 ~/.config，跨平台原生，首启按系统生成）**
- `cli/services/environment.py`：`home_config_path()`（`~/.config/ai-system/env.yaml`，`AI_HOME_CONFIG` 可覆盖）、
  `load_home_environment()`、`_deep_merge()`（home 优先递归合并）、`load_merged_environment()`；
  `paths()` / `resolve_environment()` 改读合并配置——单点实现，全部消费者（idea-build 等技能）零改动
- `tools/setup.py`：`detect_platform()`（windows/wsl/linux）+ `_probe_build_paths()`（常见 JDK/Maven 探测）+
  `generate_home_env()`（首启非破坏生成，已存在即跳过）；main() 接入
- `config/environments/local.yaml`（+template）、`runtime-bootstrap.md` Phase 2、`skill-author/SKILL.md`：
  配置源顺序（机器层 home 优先 → workspace 层兑底 → 自动推导）文档化
- `tools/path-audit.py`：`~/.config/ai-system/env.yaml` 入豁免（机器层运行时路径，与 $HOME/.claude 同类）
- 新测试 `cli/tests/test_home_env.py`（9 用例：路径/合并/合并读取/生成非破坏）；
  验证：CLI 132 测试 OK（123+9）/ repo-lint 25 WARN 无新增 / check.py PASS(3 既有) / path-audit 0 broken
- 当前机器未生成 home 配置（避免静默把 backend=idea 换成探测默认）——现有 workspace local.yaml 继续生效为 fallback，
  用户下次运行 setup.py 时首启生成（非破坏）；提案记录 `reports/P29-HOME-ENV-CONFIG.md`（Approved）

**P29 批次补充（用户决策 1+2）——`aic env-init` 子命令化 + setup.py/AI 引导保留**
- `cli/commands/aic-env-init.md` 薄命令（Steps/Guardrails 英文，description 中文）+ `config/menu.yaml`（命令+字段）
  + `config/intents.yaml`（init-env 意图，builtin）
- `tools/setup.py --env-init`：配置聚焦初始化（复用 generate_env/generate_home_env，仅生成两份配置 + 解析冒烟，
  不碰 scaffold/链接/基线/审计）
- 合并语义修正：home 机器层**仅对安装根生效**（`_is_installed_root` 守卫）——测试/备用克隆传任意 root 时
  跳过 home 合并，保持隔离（修复 test_wizard_output 2 例回归）
- 本机已生成 `/home/syske/.config/ai-system/env.yaml`（jdk8/idea 保留，WSL 路径形式）；`env-init --non-interactive`
  真机冒烟：两份配置均 exists 跳过、解析正确
- 验证：CLI 135 测试 OK（+2 env-init +1 隔离性）/ repo-lint 25 WARN / check.py PASS(3 既有) /
  path-audit 0 broken / workflow-command-audit 0/0（命令 14→15）

**待确认小修（Change Control：确认后落）**
1. `reports/README.md` 提案索引补 P28 行（L1，doc drift，一行）
2. P26 状态 Proposed → Implemented（P26 文件 Status 字段 + PROPOSALS.md 同步；实现已 git 实证）

→ **批次 A 已全部执行（用户确认 2026-08-23）**：P26 置 Implemented（补 Review Log + Implementation
  Record，P25 惯例）；P28 补 README 提案索引；`templates/prompts/workflow-trigger.md` 死模板归档至
  `archived/templates/`（+ ARCHIVE.md 记录）；AGENTS.md 运行目录表清理（删 ai-system_bak_260803、补
  .qoder）。check.py 警告 3→2（P28 索引 warn 消失）。

**建议（不改，跟踪/走各自流程）**
- 25 WARN 既有债：技能缺 workflow.md 属技能架构口径，随技能维护流程处理；英文注释随相关文件改动顺手转中文
- `skills/implement/examples.md` 内部重复示例：下次技能优化时去重
- extensions 仓 codeup-submit-mr 未提交修改：由 extensions 域流程提交/归档
- AGENTS.md：`ai-system_bak_260803` 行可删、`.qoder` 可补登记（信息级，随文档改动顺手）
- P26 provider / CI、P28 B/D：触发条件未到，defer（已登记触发条件）

---

## 五、quick-check 趋势（近 6 快照）

| 日期 | verdict | findings | lint |
|---|---|---|---|
| 08-13 | OK | 0 | — |
| 08-14 | OK | 0 | — |
| 08-17 | OK | 0 | 27 WARN |
| 08-18 | OK | 0 | — |
| 08-20 | OK | 0 | 25 WARN |
| 08-23 | **OK** | **0** | 25 WARN |

趋势平稳：近 6 个快照全部 OK，lint WARN 自 08-17 的 27 收敛至 25 后稳定，无回退。

---

## 附：环境备注

- WSL 默认 `python` 为 pyenv-win shim（不可执行），全部工具以 `/usr/bin/python3` 运行（与 08-20 记录一致，属已知环境事实，非本次新发现）。
- 维护经验（CI 环境 / pyc 缓存 / 仓库布局）索引见 `reports/`（README），本报告不重复积累。
