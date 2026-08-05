# Maintenance Report — 2026-08-05

**Mode**: on-demand
**Scope**: workflows（巡检当前工作流，确认是否需要新增"工作流管理"类能力，以及外部/公司专用工作流支持）
**Date**: 2026-08-05
**Environment**: Windows (`D:\workspace\ai-workspace`)

---

## 1. 工具校验结果 / Tool Check Results

### repo-lint.py

| Severity | Count |
|----------|-------|
| BLOCKER  | 0     |
| ERROR    | 0     |
| WARNING  | 9     |

**Result**: ✅ PASS — 无 BLOCKER / ERROR，可继续后续步骤。

Warnings 明细（均为既有技能层问题，不在本次 workflows 范围内）：
- 4× `skill.md` 无 `workflow.md`（agent-debug-diagnosis, contract-maintainer, java-maven, review）
- 5× Maven 命令提及（bugfix ×2, mock-test ×3）

### repo-metrics.py

| Metric | Current (2026-08-05) |
|--------|----------------------|
| Snapshot | `metrics/maintain-2026-08-05.json` |
| Skills    | 26 |
| Workflows | 14 |
| Governance | 55 |
| Templates | 19 |
| Frontmatter | 25 valid / 1 missing |

**Result**: ✅ PASS — 指标采集正常。

> ⚠️ 命令规范写的是 `--snapshot metrics/maintain-{date}.json`，但 `ai-system/metrics/` 目录不存在（见 F3），快照实际落盘 `reports/`。

### path-audit.py

| Metric | Value |
|--------|-------|
| Files scanned | 133 |
| References checked | 472 |
| Placeholders | 62 |
| Known debt | 3 |
| BROKEN | **0** |

**Result**: ✅ PASS — 无失效路径引用。

### check.py（完整性门禁）

**Result**: ✅ PASS — `discovered: 14 workflows, 9 commands`，0 warning。

### 指标对比（vs 2026-08-01 月报基线）

| Metric | 2026-08-01 | 2026-08-05 | Delta |
|--------|-----------|-----------|-------|
| Workflows | 11 | 14 | +3（code-review, change-impact, proposal） |
| Skills | 27 | 26 | -1（refactor-safely 归档，与 metric/lint 计数口径差异见历史 F6） |
| Templates | 16 | 19 | +3（runtime-code-review/change-impact/proposal） |
| Governance | 56 | 55 | -1（routing-policy.md 删除，commit 54d36e5） |
| Lint BLOCKER/ERROR | 0/0 | 0/0 | ✅ 稳定 |
| Path-audit BROKEN | 0 | 0 | ✅ 稳定 |

---

## 2. 巡检发现 / Inspection Findings（按严重度）

### BLOCKER / ERROR（0 项）

无。

### WARNING / MINOR（按 workflows 巡检范围内）

| # | Severity | Area | Finding |
|---|----------|------|---------|
| F1 | LOW | 工作流作者路径 | 新增工作流完全靠手工多文件操作（8 段契约 md + 配置 yaml + runtime md + 注册表 + 菜单 + README 索引），**没有**如技能层 `aic-skill-source` / `skill-author` 对应的脚手架命令或作者技能。`workflow-architect` 技能存在但只做设计，不产出可注册资产 |
| F2 | LOW | 外部工作流 | 注册表 `config/workflow-registry.yaml` 仅支持 ai-system 内部相对路径；PromptBuilder / Wizard 均从 ai-system root 解析，无外部/公司/项目级工作流来源机制。与技能层既有吸收模式（skill-source → skill-policy → 吸收为原生资产）不对齐 |
| F3 | INFO | 工具/文档漂移 | AI_DEVELOPMENT_CONTRACT 架构图中声明 `metrics/` 与 `logs/` 目录，实际不存在；`aic-maintain.md` 快照路径 `metrics/maintain-{date}.json` 对应目录缺失，导致规范路径下无法落盘 |
| F4 | INFO | 文档漂移 | 工作区根 AGENTS.md 结构图未列出 `ai-system_bak_260803/`（备份目录）与 `worktrees/`（git worktree 根）；`nul` 文件为 Windows 重定向产物（pack.py 已排除，无害） |

### 已核验的健康项（无问题）

- 14 个工作流 8 段契约全部齐全且顺序一致（脚本逐一验证）
- 注册表 ↔ 配置 ↔ workflow md ↔ runtime md 四层引用闭合（脚本逐一验证，0 缺失）
- `config/workflows/*.yaml` 全部保持最小化（version/name/workflow/runtime），无 A1 复发
- standards-loader 26 处路径引用全部存在；runtime Extends 引用无失效
- `workspaces/.aic-state.yaml` 引用（pywechat-live-2608 / wecom-live-integration / T-013）全部存在
- `projects/` junction → `D:\workspace\project-resources` 可访问（83 个子目录）
- 工作流推荐路由（wizard 解析 `## Next`）单一来源，无独立路由表冗余

---

## 3. 一致性抽查结论 / Consistency Spot Check

| 检查项 | 结果 |
|--------|------|
| workflows/*.md 八段齐全且顺序一致（14/14） | ✅ PASS |
| 术语与 workflows/README.md 词汇表一致 | ✅ PASS |
| Runtime 引用文件存在（14/14） | ✅ PASS |
| Preconditions / Next 链闭合（主链 + bugfix 分支 + 独立入口） | ✅ PASS |
| config/workflows/*.yaml 保持最小化，无 A1 复发 | ✅ PASS |
| workflow-registry.yaml 链（config → workflow → runtime）闭合 | ✅ PASS |
| governance/standards + loaders + templates/prompts + cli/commands 引用路径存在 | ✅ PASS（path-audit 0 BROKEN） |
| junction/symlink（projects/）存在且可访问 | ✅ PASS |
| AGENTS.md 结构图 vs 实际布局 | ⚠️ MINOR — 备份/工作树目录未列（F4） |
| AI_DEVELOPMENT_CONTRACT 架构图 vs ai-system 布局 | ⚠️ MINOR — metrics/、logs/ 声明但不存在（F3） |
| OPERATIONS 入口章节 vs 工作流注册表 | ✅ PASS |
| 状态卫生：workspaces/.aic-state.yaml 引用仍存在 | ✅ PASS |

---

## 4. 核心结论 / Two Questions Answered

### Q1：是否需要新增"工作流管理的工作流"（用来添加新工作流）？

**结论：不建议新增一个注册在工作流链里的"工作流管理工作流"。** 真正的缺口是一个**作者/脚手架命令或技能**，而不是一个业务工作流。

依据：

1. **层级责任**：Workflow 决定"执行什么业务过程"，选择 Runtime 编排执行。而"添加一个新工作流"是对 ai-system 自身的**维护/创作任务**（改注册表、菜单、契约文件），不是可被 Runtime 编排的业务过程。若做成工作流，将变成自指元工作流，违反 RFC-0003「Workflow 只编排、不实现」，也不符合 OPERATIONS §15 黄金法则的分类追问。
2. **既有先例**：技能层新增已有成熟路径 —— `aic-skill-source`（外部评估）+ `skill-author`（作者）+ `skill-policy`（治理）。工作流层目前只有文档化流程（OPERATIONS §1.10.1 + workflows/README.md 模板 + ADR-0006），没有对应命令/技能。
3. **建议落点（结构性建议，走 OPERATIONS §12）**：
   - 方案 A（推荐）：新增命令 `aic-workflow`（镜像 `aic-skill-source`），脚手架生成 8 段契约 md + 配置 yaml + runtime md，自动注册注册表 + 菜单 + README，并跑 `check.py` 校验。
   - 方案 B：扩展 `workflow-architect` 技能，补充"产出可注册资产 + 注册清单"。
   - 方案 C（最小）：保持文档流程，本次不做任何代码改动。

   三者均不新增工作流注册项；当前用户要"加新工作流"可直接按 OPERATIONS §1.10.1 手工执行，无需等脚手架。

### Q2：工作流是否应该支持外部/公司专用工作流？

**结论：应该支持，但走"吸收为原生资产"路径，而非外部路径引用。** 与技能层既有模式对齐。

依据：

1. **技能层先例**：`aic-skill-source` 评估外部三方技能 → `skill-policy` 强制"重写为原生资产，绝不引用三方文件"。公司级能力已按此模式吸收（如 `governance/standards/cool/*`：rocketmq / rpc / i18n / enum-naming）。工作流应遵循同一模式。
2. **架构约束**：注册表保持最小化、单一来源（ADR-0006）；RFC-0003 §7 禁止工作流硬编码项目路径 / 内嵌项目专用知识；`pack.py` 迁移模型打包整个 ai-system —— 外部路径引用会破坏可迁移性与引用校验。
3. **建议路径**：
   - 公司/外部工作流 → 按 `aic-skill-source` 模式评估 → **重写为 ai-system 原生工作流**（`workflows/<name>.md` + 配置 + runtime + 注册 + 菜单 + README）→ 复用既有注册流程。
   - 项目级覆盖（如 `workspaces/{project_id}/workflows/` 叠加层）是结构性扩展，需要改动 Wizard / PromptBuilder 发现逻辑 —— **仅当真实项目需求出现时**（Evolution Principle），再走 OPERATIONS §12 / RFC。
4. **现阶段无需实现**：注册表最小化、单一来源、可迁移性优先；当前公司工作流需求可通过原生吸收满足。

---

## 5. 修复动作与建议清单 / Fix Actions & Suggestions

### 结构性建议（输出建议，不直接实施 → OPERATIONS §12）

| # | 建议 | 类型 |
|---|------|------|
| S1 | 新增 `aic-workflow` 脚手架命令（或扩展 workflow-architect 技能），自动化"新增工作流"全流程 | 命令/技能层新增 |
| S2 | 外部/公司工作流统一走"吸收为原生资产"路径，评估命令可复用 `aic-skill-source` | 流程/策略 |
| S3 | 项目级工作流叠加层：仅当真实项目需求出现时再评估（RFC + §12） | 结构性扩展（待触发） |

### 已执行的文档级小修（L1，用户确认后应用）

| # | 落点 | 改动 | 状态 |
|---|------|------|------|
| P1 | `ai-system/metrics/` | 创建 `metrics/` 目录；快照落盘规范路径 `metrics/maintain-2026-08-05.json` | ✅ DONE |
| P2 | 根 `AGENTS.md` | 补充"运维非规范目录"表：`ai-system_bak_260803/`（备份）、`worktrees/`（git worktree 根） | ✅ DONE |
| P3 | `tools/setup.py` | metrics 集成到初始化流程：`ensure_runtime_dirs()` 创建 `metrics/`、`logs/`；`record_baseline()` 在初始化末尾生成 `metrics/baseline-{date}.json`（幂等，已存在则跳过）。同步更新 docstring 与 `runtime-bootstrap.md` Phase 1 描述 | ✅ DONE |

### 确认清单

- F1 已落地（S1，Option A，见下）；F2 结构性结论（外部工作流走原生吸收）已给出，落地随 S1 脚手架覆盖。
- P1/P2/P3 属 L1 级小修/工具增强，已于本批次应用。

### S1 — `aic-workflow` 作者命令（OPERATIONS §12：Analyze → Propose → Review → **Approve: Option A** → Implement → Validate）

已实施（详见 `reports/P7-WORKFLOW-AUTHOR-COMMAND.md`）：

| # | 产物 | 说明 |
|---|------|------|
| S1-1 | `tools/workflow-scaffold.py` | 非破坏性脚手架：生成 8 段契约 md + 配置 yaml + runtime 骨架，追加注册表条目；幂等（重名拒绝） |
| S1-2 | `cli/commands/aic-workflow.md` | 命令定义：脚手架 → 填 8 段 → 菜单/README 注册 → check.py/lint 校验 |
| S1-3 | `config/menu.yaml` | `commands_maintenance` 段注册 `workflow` 命令 + `command_fields`（Workflow Name 必填；Purpose/Next Workflow 可选）+ 图标 |
| S1-4 | `config/i18n/zh.yaml` | 新增字段备注（Workflow Name / Purpose / Next Workflow） |
| S1-5 | `tools/README.md` | 注册 workflow-scaffold.py（check_tools_readme 门禁） |

**功能验证**：脚手架 `demo-wf` 全链路（生成 4 文件 + 注册 → 填充内容 → check.py PASS 15 workflows → 幂等重复拒绝 → 清理恢复 14 workflows）✅；`check.py` 0 warning、`repo-lint` 0/0/9、`path-audit` 0 broken ✅。

**S1 补充（必要性评估前置）**：收到反馈后确认原命令缺"先评估、后执行"门禁，已补齐：

- `cli/commands/aic-workflow.md` — Step 1 改为硬门禁"Assess necessity"：层分类（OPERATIONS §15 黄金法则）→ 重叠检查（skill-policy §2 模式，`--list` 对比，>60% 扩展现有）→ Evolution Principle 真实需求 → **用户确认后**才进入脚手架。未确认不得执行。
- `tools/workflow-scaffold.py` — 新增 `--list` 辅助（列出现有工作流 + Purpose，供重叠对比）。

**验证**：`--list` 正常输出 14 个工作流及 Purpose；`check.py` 0 warning、`repo-lint` 0/0/9、`path-audit` 0 broken、`py_compile` 通过 ✅。

**S2 补充（commands 作者命令，OPERATIONS §12：Analyze → Propose → Review → **Approve: Option A** → Implement → Validate）**：

commands 层与 workflows 对称的缺口已补齐（详见 `reports/P8-COMMAND-AUTHOR.md`）：

| # | 产物 | 说明 |
|---|------|------|
| S2-1 | `tools/command-scaffold.py` | 非破坏性脚手架：生成 `cli/commands/aic-<name>.md` + 注册清单；`--list` 列出现有命令 + description；幂等重名拒绝 |
| S2-2 | `cli/commands/aic-command.md` | 命令定义，Step 1 硬门禁"必要性评估"（层分类 → `--list` 重叠对比 → Evolution Principle → 用户确认）后才脚手架 |
| S2-3 | `config/menu.yaml` | `commands_maintenance` 段注册 `command` 命令 + `command_fields`（Command Name 必填；Description 可选）+ 图标 |
| S2-4 | `config/i18n/zh.yaml` | 新增字段备注（Command Name / Description） |
| S2-5 | `tools/README.md` | 登记 command-scaffold.py |

**功能验证**：脚手架 `demo-cmd` 全链路（生成 → 填充 → check.py PASS 12 commands → 幂等重复拒绝 → 清理恢复 11 commands）✅；`check.py` 0 warning、`repo-lint` 0/0/9、`path-audit` 0 broken ✅。

> 过程发现：`aic-command.md` 初始 Guardrails 中 `tools/skills` 连写被 path-audit 误判为路径引用（BROKEN 1），已改为 `tools or skills` 措辞修复（0 broken）。

**S4 — `aic-skill-launch` 启动器（OPERATIONS §12：Analyze → Propose → Review → **Approve: Option A** → Implement → Validate）**：

用户需求：启动脚本 → 选 skill → 选 agent（opencode/pi）→ 自动触发。设计要点：

- **公司 skill 存 `extensions/` 目录**（`D:\workspace\ai-workspace\extensions`，config 驱动 `layers.skills`，默认 `{workspace_root}/extensions`）。目录名避开 `skills`/`.claude/skills`/`.agents/skills`，**不被 opencode/pi 自动扫描**，不污染上下文；由启动器显式加载。
- **pi 共享同一 SKILL.md 机制**（`~/.pi/agent/npm/node_modules/pi-cache-optimizer` 扫描 `~/.agents/skills`，无独立 pi 技能目录）→ 一次扫描服务 opencode 与 pi。
- **薄触发提示**：生成的 prompt 只引用 skill name + SKILL.md 路径，指示 agent 按需加载，**不嵌入完整 SKILL.md**（上下文 ~0）。

| # | 产物 | 说明 |
|---|------|------|
| S4-1 | `cli/services/skill_scan.py` | 扫描 extensions（config 驱动，优先）→ 全局 `~/.agents/skills` → 项目级 `.opencode/.claude/.agents/skills`；realpath 去重 |
| S4-2 | `cli/services/skill_launcher.py` | 编排：选 skill（菜单）→ 选 agent（复用 `_select_launch`，含 pi）→ 输任务 → 渲染提示 → 复制 + 启动 |
| S4-3 | `cli/main.py` | `skill-launch` 子命令入口 + `--agent` 参数 |
| S4-4 | `templates/prompts/skill-launch.md` | 薄触发模板（不嵌 SKILL.md 正文） |
| S4-5 | `cli/commands/aic-skill-launch.md` | 命令定义 |
| S4-6 | `config/menu.yaml` + `i18n/zh.yaml` | 注册命令 + 字段 + 图标 |
| S4-7 | `config/environments/local.yaml`(+template) + `setup.py` | `layers.skills` 配置项 + `skills_root` resolver（`environment.py`） |

**功能验证**：skill_scan 正确（extensions 优先/test 技能识别/global 6 个去重/local 0）；提示渲染薄触发（无 SKILL.md 正文）；`check.py` 0 warning、`repo-lint` 0/0/9、`path-audit` 0 broken、全模块编译通过 ✅。测试 skill 已清理，extensions 目录就绪待放真实公司技能。

**S4 后续 — 恢复 6 个公司技能到 extensions/**：

从 `ai-system_bak_260803/skills/` 恢复 6 个公司特有技能到 `D:\workspace\ai-workspace\extensions\`：

| 技能 | 用途 | 处置 |
|---|---|---|
| `codeup-submit-mr` | Codeup MR 提交 | ✅ 恢复 + 改写 `~/.claude` 路径为相对 `codeup-mr.py` |
| `confluence-markdown-publisher` | Confluence 发布 | ✅ 恢复（无路径问题） |
| `hotfix-test-doc` | 转测文档 | ✅ 恢复（保留 `~/.ai-env` 机器配置引用，合法） |
| `oncall-weekly-report` | iTalent/YouKeCRM 周报 | ✅ 恢复 |
| `tr5` | TR5 一页纸方案流水线（44 文件） | ✅ 恢复 |
| `yapi-openapi` | YAPI 接口维护 | ✅ 恢复 |

**未恢复**：
- `coolbugfix` — 已 deprecated（frontmatter 自标，指向新链路）
- `refactor-safely` — 已 deprecated，`archived/skills/` 已有副本
- `multi-model-dispatch` — 含明文 API Key（`.env`），按"吸收方法论、不恢复脚本"决策；方法论待提取

**一致性调整**：移除全局 `~/.agents/skills/codeup-submit-mr` 重复副本（与 extensions 内容一致），公司技能统一存 extensions，由 `aic skill-launch` 显式加载，不污染全局上下文。

**最终状态**：extensions 6 公司技能 + global 5 通用技能（codegraph-helper/coolreview/find-skills/grilling/karpathy-guidelines）= 11 技能，无重复；`skill_scan` 验证 extensions 优先、去重正确 ✅。门禁：check.py 0 warning、lint 0/0/9、audit 0 broken ✅。

**S4 补充 — 初始化脚本支持 extensions + 空目录降级**：

- `tools/setup.py` `BASE_DIRS` 增加 `extensions`：scaffold 时自动创建工作区 `extensions/` 目录（幂等，已存在则跳过）；docstring 步骤同步。
- `templates/runtime/runtime-bootstrap.md` Phase 1 setup 步骤描述同步（含 extensions scaffold）。
- **空 extensions 降级**：`skill_scan._skills_in` 对缺失/空目录安全返回空（`is_dir()` 检查），scan 自动降级到 global 技能；launcher 在 extensions 空时仅显示 global/local 技能，不报错。
- 验证：extensions 缺失时 setup 创建成功（`created: ...extensions`）；空目录扫描返回 `[]`；正常扫描仍返回 6 extensions 技能。门禁全绿 ✅。

**S4 补充 2 — agent 选择独立化 + skill 展示增强**：

- `config/providers.yaml` — 每 provider 增加可选 `label` / `description`（用户可见显示名 + 一句话描述）。
- `cli/services/agent_picker.py` — 新增全局可复用的 agent 选择服务：从 providers.yaml 读 enabled providers，渲染带 label/description 的选择菜单（默认项高亮）。供 skill-launch 及未来所有需选 agent 的流程复用。
- `cli/services/menu_config.py` — 新增 `provider_meta()`（name → {label, description}）。
- `cli/services/skill_launcher.py` — 改用 `agent_picker`（替换 `wizard._select_launch`，去掉不适用的 "finish (no launch)" 项）；skill 列表显示来源标记（`[ext]`/`[g]`/`[proj]`）+ 全部技能展示 + 关键词输入过滤。
- `cli/commands/aic-skill-launch.md` — 步骤与 guardrails 同步。

**验证**：agent_picker 菜单正确（默认 opencode，可选 pi/claude）；skill 列表 11 项带来源标记全显示；keyword filter 由 menu 通用能力提供。门禁全绿 ✅。

**S4 补充 3 — skill-launch emoji 集成**：

- `cli/utils/menu.py` — 新增公开 `e(icon)` 辅助（复用 wizard `_e` 逻辑：TTY + `AIC_ICONS` 控制，`AIC_ICONS=off` 自动隐藏）。
- `cli/services/skill_launcher.py` — skill 菜单标题 `🧩 Select a skill`、来源标记 `[🧩 ext]`/`[🌍 g]`/`[📁 proj]`、task 提示 `📝 Task`、agent 菜单标题传入 `🤖 Select an agent`。
- `cli/main.py` — 启动成功消息 `🚀 {agent} launched`。

**验证**：`AIC_ICONS=emoji` 下来源标记带 emoji；`AIC_ICONS=off` 自动隐藏。门禁全绿 ✅。

**S4 补充 4 — skill 分组 + 多选（配置化）**：

- `config/skill-groups.yaml` — 新增配置（对齐 menu.yaml 模式）：`version`/`locale`/`groups`；分组类型 `source`（按来源）与 `list`（自定义组合，显式技能清单）；组标题走 i18n `skill_groups.*`；未命中分组技能自动落入"其他"组。
- `config/i18n/zh.yaml` — 新增分组标题：公司技能/全局技能/常用组合/项目技能/其他技能。
- `cli/services/menu_config.py` — 新增 `skill_groups()` / `skill_group_title(key)` 访问器 + 加载 `skill-groups.yaml`。
- `cli/services/skill_launcher.py` — `_pick_skills` 改多选（`choose_many`，空格切换/Enter 确认）；`_group_skills` 按配置生成分组（Section 标题 + 去重，早组优先，晚组跳过已分配技能）；prompt 渲染多技能清单。
- `cli/utils/menu.py` — `_interactive_many` / `_fallback_many` 支持 Section 分组（selectable 排除 Section，标题渲染，fallback 编号跳过 Section）。
- `templates/prompts/skill-launch.md` — 改为 `{{skill_list}}` 多技能清单（名称+路径+来源），移除单数占位符。

**验证**：分组正确（常用组合前置 → 公司技能去重 → 全局 → 其他 fallback），11 技能无重复；多选渲染 OK（多技能清单）；非 TTY fallback 多选编号正确。门禁全绿 ✅。

**S4 补充 5 — skill-launch 交互优化（任务模板/详情预览/结果回显）**：

| # | 优化 | 说明 |
|---|------|------|
| P0-1 | 任务模板/预设 | `skill-groups.yaml` 组合组支持 `task` 默认任务字段（选热修复组合自动带出"转测文档"模板）；新增 `tasks` 预设清单（常用任务菜单：转测文档/MR/Confluence/周报）；`_pick_task` 提供预设选择 + 自定义入口 |
| P0-2 | skill 详情预览 | `skill_scan` 读取完整 frontmatter（usage/trigger）；选技能后 `_preview_skills` 展示用法/触发词确认选择 |
| P2-1 | 结果回显 | 生成 prompt 后 `_echo` 显示摘要（skills/agent/task），确认后才复制+启动 agent |

- `config/skill-groups.yaml`：组合组加 `task` 字段 + 顶层 `tasks` 预设
- `cli/services/menu_config.py`：`skill_tasks()` / `combo_task()` 访问器
- `cli/services/skill_scan.py`：frontmatter 解析扩展（usage/trigger）
- `cli/services/skill_launcher.py`：preview / task-preset / echo / confirm 流程

**验证**：热修复组合选中后默认任务自动带出（"根据提交内容编写转测文档…"）；preview 显示 skill 详情；echo 摘要 + 确认后启动。门禁全绿 ✅。

**S4 补充 6 — 可拔插统一交互（修复退格断层 + 统一状态机）**：

问题：skill-launch 内退格直接退出（run 返回 None → main 硬 return），交互断层。

方案：新增 `cli/services/interactive.py` 统一状态机抽象。

| # | 产物 | 说明 |
|---|------|------|
| I-1 | `cli/services/interactive.py` | `InteractiveCommand` 基类：声明 `steps` 步骤序列，统一驱动（NEXT/BACK/QUIT/done），每步 BACK 回退上一步，第 1 步 BACK → QUIT（由调用方决定重选，不硬退出） |
| I-2 | `skill_launcher` | 重构为 `SkillLauncher(InteractiveCommand)`：steps = [选技能 → 选agent → 选task → 确认]；agent/task/confirm 步 BACK 逐级回退，skill 步（第1步）BACK → QUIT |
| I-3 | `cli/main.py` | wizard 分支改循环：skill-launch 退出（None）→ 打印"back to the wizard" → 重新进入向导重选，而非硬退出 |

**BACK 行为**：skill 步 BACK → 回向导（可重选/退出）；agent/task/confirm 步 BACK → 回退上一步。**可拔插**：未来其他交互命令继承 InteractiveCommand 声明 steps 即可获得统一 BACK/回退契约。

**验证**：agent 步 BACK 回退到 skill 步（重新预览）→ 重选 agent → 完成 ✅；launcher 退出后 main 循环回到向导（第 2 次选 prepare 正常）✅；门禁全绿 ✅。

**S4 补充 7 — 修复 Esc 崩溃**：

问题：技能多选时按 Esc，`_interactive_many` 抛 `KeyboardInterrupt`（既定取消语义），但 `skill_launcher.run()` 在 main 的 try 块之外，异常穿透崩溃。

修复：`cli/main.py` 将 skill_launcher.run 纳入 try，捕获 `EOFError`/`KeyboardInterrupt` → 打印"back to the wizard" → `continue` 回向导。

**Esc 语义**：skill-launch 内 Esc → 回到向导；向导再 Esc → 退出程序（逐级退出，与 wizard 一致）。**验证**：Esc 模拟 → 捕获 → 重新进入向导（第 2 次选 prepare 正常）✅；门禁全绿 ✅。

**S4 补充 8 — 交互小优化（task 前置 + 空选回车 + emoji）**：

| # | 优化 | 说明 |
|---|------|------|
| I-1 | task 选择前置 | steps 顺序改为 [skills → task → agent → confirm]（task 在 agent 前，符合"先定做什么再做"的心智） |
| I-2 | 空选回车选中当前 | `choose_many` 新增 `enter_selects_current` 参数（默认 False）：交互模式空选 Enter 返回当前高亮项，fallback 空输入返回第一项；skill-launch 传 True |
| I-3 | task/agent emoji | task 步 `📝`/`✏️`；agent 标题 `🤖` + `providers.yaml` 每 provider 新增 `icon`（🤖/🌀/⚡/💠），agent_picker 选项带图标 |

- `cli/utils/menu.py`：`choose_many`/`_interactive_many`/`_fallback_many` 支持 `enter_selects_current`
- `config/providers.yaml`：每 provider 加 `icon`
- `cli/services/menu_config.py`：`provider_meta` 含 icon
- `cli/services/agent_picker.py`：选项渲染带 icon
- `cli/services/skill_launcher.py`：steps 顺序调整 + 空选回车

**验证**：steps 顺序 [skills→task→agent→confirm] ✅；空选回车返回当前项（单测 [idx]）✅；agent 选项 `🤖 opencode`/`🌀 pi`/`⚡ claude` ✅；门禁全绿 ✅。

**S4 补充 9 — `aic-skill-optimize` 薄命令（接现有 skill-optimizer 能力）**：

用户问题：当前系统是否需要 skill 优化评估命令。调研结论：`skill-optimizer` 已具备完整优化评估能力（static 静态合规+LLM 五维评估 / dynamic / trace / feedback + 快照/diff/报告），但**无 CLI 入口**，只能靠对话触发。按 Repository First + 最小改动，新增**薄命令**接现有能力（不重复造评估逻辑）。

| # | 产物 | 说明 |
|---|------|------|
| O-1 | `cli/services/skill_optimize.py` | `SkillOptimizeLauncher(InteractiveCommand)`：steps = [选技能 → 选模式 → 选agent → 确认]；复用 skill_scan 分组/多选 + agent_picker + 统一 BACK 状态机 |
| O-2 | `templates/prompts/skill-optimize.md` | 薄触发模板：引用 skill-optimizer 位置 + 技能清单 + 模式，指示 agent 按 workflow 执行（不嵌正文） |
| O-3 | `cli/commands/aic-skill-optimize.md` | 命令定义 |
| O-4 | `cli/main.py` | 新增 `_INTERACTIVE_COMMANDS` 映射（skill-launch/skill-optimize）+ `_run_interactive` 统一分发（直接 CLI + 向导分支均走） |
| O-5 | `cli/services/wizard.py` | skill-optimize 纳入零字段 + 直接返回 |
| O-6 | `config/menu.yaml` + `i18n/zh.yaml` | 注册命令（🔧 图标）+ Mode 字段备注 |

**模式**：static（默认，无需额外数据）/ dynamic（Insight 平台）/ trace（trace 数据）/ feedback（用户反馈）。

**验证**：直接 `aic skill-optimize --agent pi` → COPY + LAUNCH ✅；向导选 skill-optimize → 进入启动器 ✅；prompt 渲染（技能+模式 static）✅；check.py 0 warning（13 commands）、lint 0/0/9、audit 0 broken ✅。

**S1/S2 Review（用户要求复核两个新增作者能力）**：

| # | 检查项 | 结果 |
|---|--------|------|
| 1 | 两个命令文档：结构对称、必要性评估硬门禁（层分类/重叠/Evolution/用户确认）齐全 | ✅ PASS |
| 2 | 命令 vs 工具一致性：命令 Step 与工具行为对齐（--list / 幂等 / 非破坏） | ✅ PASS |
| 3 | 生成的模板：workflow 8 段顺序、runtime extends base、command frontmatter 合法 | ✅ PASS |
| 4 | **发现 1（L1，已修）**：`workflow-scaffold.py` 死代码 `_title_case()`（与 `_title()` 重复且未用）+ `_list_workflows()` 内未使用的 `import re as _re` | ✅ 已删除 |
| 5 | **发现 3（L1，已修）**：scaffold `NAME_RE`（`^[a-z][a-z0-9-]*$`）接受尾部连字符 `foo-`，与 check.py 命令规则 `[a-z0-9]+(-[a-z0-9]+)*` 不一致 → 统一为 `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`（两工具同步） | ✅ 已修复，`foo-`/`-foo`/`foo--bar` 现被源头拒绝 |
| 6 | 已知行为（不修改）：`--next` 目标不预校验，由 `check.py check_next_sections` 兜底；允许"先建引用、后建目标"合法顺序 | ✅ 记录 |
| 7 | 已知差异（不修改）：scaffold 要求名字以字母开头（比 check.py 更严）——数字开头会破坏 wizard `_parse_next` 路由，前置拒绝是正确防御 | ✅ 记录 |

**Review 验证**：`check.py` 0 warning、`repo-lint` 0/0/9、`path-audit` 0 broken、双工具 `py_compile` + AST 通过 ✅。

---

## 6. Completion

### Modified Files

- `AGENTS.md` — 补充运维非规范目录表（P2）
- `tools/setup.py` — metrics 集成初始化：`ensure_runtime_dirs()` + `record_baseline()` + docstring（P3）
- `templates/runtime/runtime-bootstrap.md` — Phase 1 setup 步骤同步（P3）
- `tools/workflow-scaffold.py` — S1：新工作流脚手架工具（新增）
- `tools/command-scaffold.py` — S2：新命令脚手架工具（新增）
- `tools/README.md` — 登记 workflow-scaffold.py / command-scaffold.py（S1/S2）
- `cli/commands/aic-workflow.md` — S1：命令定义（新增）+ S1 补充必要性评估门禁
- `cli/commands/aic-command.md` — S2：命令定义（新增）
- `config/menu.yaml` — S1/S2：注册 workflow/command 命令 + 字段 + 图标
- `config/i18n/zh.yaml` — S1/S2：新增字段备注
- `reports/P7-WORKFLOW-AUTHOR-COMMAND.md` — S1 提案（新增）
- `reports/P8-COMMAND-AUTHOR.md` — S2 提案（新增）
- `reports/P9-SKILL-LAUNCHER.md` — S4 提案（新增）
- `cli/services/skill_scan.py` — S4：skill 扫描服务（新增）
- `cli/services/skill_launcher.py` — S4：skill 启动器服务（新增）
- `cli/main.py` — S4：skill-launch 子命令入口 + --agent
- `templates/prompts/skill-launch.md` — S4：薄触发模板（新增）
- `cli/commands/aic-skill-launch.md` — S4：命令定义（新增）
- `config/environments/local.yaml`(+template) + `tools/setup.py` — S4：layers.skills 配置
- `cli/services/environment.py` — S4：skills_root resolver
- `reports/MAINTENANCE-2026-08-05.md` — 本报告（P1–P3 + S1/S2/S4 记录、快照路径修正）

### New Files

- `ai-system/metrics/maintain-2026-08-05.json`（指标快照，规范路径）
- `ai-system/metrics/baseline-2026-08-05.json`（初始化基线快照，由 setup.py 生成）
- `ai-system/config/environments/local.yaml`（setup.py bootstrap 生成，gitignored）
- `ai-system/logs/`（setup.py 创建，gitignored）
- `ai-system/tools/workflow-scaffold.py`（S1 脚手架工具）
- `ai-system/tools/command-scaffold.py`（S2 脚手架工具）
- `ai-system/cli/commands/aic-workflow.md`（S1 命令）
- `ai-system/cli/commands/aic-command.md`（S2 命令）
- `ai-system/reports/P7-WORKFLOW-AUTHOR-COMMAND.md`（S1 提案）
- `ai-system/reports/P8-COMMAND-AUTHOR.md`（S2 提案）
- `ai-system/reports/P9-SKILL-LAUNCHER.md`（S4 提案）
- `ai-system/cli/services/skill_scan.py`（S4）
- `ai-system/cli/services/skill_launcher.py`（S4）
- `ai-system/templates/prompts/skill-launch.md`（S4）
- `ai-system/cli/commands/aic-skill-launch.md`（S4）
- `D:\workspace\ai-workspace\extensions\`（S4 公司技能目录，已创建）

### Moved Files

- `reports/metrics-maintain-2026-08-05.json` → `metrics/maintain-2026-08-05.json`（P1，对齐 aic-maintain.md 规范路径）

### Deviations（L1 / L2）

- 无（仅执行巡检与报告落盘）。

### Risks

- 新增工作流仍为手工多文件操作，频率升高时易产生注册遗漏 / 契约缺段；建议在出现第二次"手动新增"痛点后优先落地 S1。
- 若公司工作流直接以外部文件形式引用而不吸收，将破坏注册表单一来源、pack 迁移与引用校验 —— 请坚持 S2 吸收模式。

### Next Recommendation

1. ✅ 巡检结论（Q1：不做元工作流，缺作者命令/技能；Q2：外部工作流走原生吸收）。
2. 📋 确认 P1 / P2 文档级小修是否本批次落地。
3. 📋 S1（`aic-workflow` 脚手架）作为结构性建议，按 OPERATIONS §12 推进或暂缓。
