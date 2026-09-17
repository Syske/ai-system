# 系统巡检报告 — 2026-09-17（on-demand）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand（专项）
- 日期: 2026-09-17
- 范围: 检查 aic 选择项目时，项目后面为何显示 (no repo mapped)
- 关联: ADR-0008（项目-仓库逻辑映射）、runtime-dev-setup.md、cli/services/providers.py、cli/services/wizard/selection.py

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 29 | Files: 29 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 30 | 30 | = |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 59 | 59 | = |
| Templates | 22 | 22 | = |

> 上期口径取自 metrics/maintain-2026-09-11.json；本期快照 metrics/maintain-2026-09-17.json。
> 15 commits（2026-09-11 → 2026-09-17）涉及 cli/config/reports/skills/templates/tools/workflows，
> 指标层面无增减，以流程修订/平台修复为主。

---

## 二、巡检发现（AI 填写，按严重度分级）

### [高] aic 项目菜单大量项目显示 (no repo mapped)——映射数据源与显示源脱节

**现象（已复现）**：`aic` 项目列表 8 个工作区项目中 7 个显示 `(no repo mapped)`，仅
`pywechat-live-2608` 显示服务名（knowledge-api, training-manage-api, isv-api）。
其中 4 个业务项目（20260901-cool-test / 202610-cool-italent-sync-plus /
202610-public-security-storage-no-ai-parse-optimization /
202610-qa-housekeeping-optimization）实际已绑定仓库，显示与实际不符；
opencode-test / openspec-test / pi-agent-develop 为工具测试工作区，无仓库属正确显示。

**根因（证据链）**：
1. 显示源单一：`cli/services/wizard/selection.py::_select_project` 仅读
   `providers.project_repos()` → `workspaces/<pid>/workspace.yaml → repository.available`，
   为空即显示 `(no repo mapped)`（selection.py L97-114）。
2. 存储源迁移：dev-setup 运行时（templates/runtime/runtime-dev-setup.md Phase 9-10）把
   仓库绑定持久化到 `workspaces/<pid>/contexts/project-context.yaml`（Phase 6 repository /
   Phase 7 worktrees 段），**从不写 workspace.yaml**；全仓 grep 确认无任何工具/运行时写
   workspace.yaml（仅读者：providers.py / command_hooks.md / runtime-code-review.md /
   runtime-release.md）。
3. 执行步骤悬空：ADR-0008（2026-08-08，commit 084a6d4）规定 workspace.yaml 由 AI 在
   dev-setup/prepare 阶段初始化，但 workflows/dev-setup.md 与 runtime-dev-setup.md 均无此步
   ——2026-08-08 报告遗留「workspace.yaml 初始化尚未自动化」至今未接。
4. 次级：`providers.project_meta()` 读 `contexts/project.yaml`（该文件全工作区不存在，
   dev-setup 写的是 project-context.yaml）；`repo_path_for()` 回退 `projects_root/<pid>`
   也无法命中（projects/ 下是服务名目录而非工作区 id）。P22 / MAINTENANCE-2026-08-14 遗留的
   「两处 repo 路径来源统一」问题延续，且新增了第三处来源（project-context.yaml）。

**影响**：项目选择时无法确认项目背后的服务；依赖 workspace.yaml 的链路
（code-review dev_branch 匹配、release 仓库定位、change-impact 映射选择）在 dev-setup 时代
项目上同样落空。

**状态：已修复（方案 B，2026-09-17 用户确认）**——dev-setup Phase 10 增补 workspace.yaml
生成/刷新规则（ADR-0008 格式），存量 4 项目已回填；aic 菜单实测 3 个业务项目显示服务名，
cool-test（prepare-only，无绑定）保持 (no repo mapped) 属正确显示。详见第四节。

**遗留（季度候选）**：方案 C——repo 数据源统一（project-context.yaml 为权威、workspace.yaml
由 dev-setup 生成；project_meta 的 contexts/project.yaml 读取路径清理），治理 P22/2026-08-14 遗留。

**修复建议（结构改动，仅建议，待用户决策，见第四节）**：
- 方案 A（最小显示修复）：`project_repos()` 在 workspace.yaml 缺失时回退读
  `contexts/project-context.yaml → repository / worktrees`。
- 方案 B（恢复 ADR-0008 契约，推荐）：dev-setup Phase 10 增补 workspace.yaml 生成/刷新步
  （repository.available/unavailable 按 ADR-0008 分类规则），显示逻辑不动。
- 方案 C（统一数据源，季度候选）：三处来源合并为单一数据源，治理 P22 遗留。

### [中] release 产物布局约定欠指定/自相矛盾 → 已修复（方案 X，用户确认 2026-09-17）

**现象（用户报告）**：security-storage 的 release 逐卡审查产物落在
`openspec/changes/<change>/release/`，其余 release 清单/报告散落在 workspace 根（14 个散文件），
与 italent 的目录结构不一致。

**根因**：① runtime-release.md Phase 1.Y 自初始提交（99f56d6）起硬编码 Save-to
`openspec/changes/<change>/release/`（生成物入 OpenSpec 资产领地，违反 AGENTS.md 边界）；
② Outputs Location 只写 "workspace-anchored / co-located" 不定子目录 → 每次 AI 运行自由发挥
（security-storage 平铺根目录 + reports/，italent 自组织 release//review//verify/ 子目录）；
③ workflows/release.md 与 runtime 的 Location 措辞不一致（一个提 release/ 子目录、一个不提）；
④ 同类问题波及 review/verify（runtime Location 同样欠指定）。

**修复（方案 X，参考 italent 结构 + 用户细化「统一落 review」）**：
- release 包（sql/ + checklists + 聚合 release-branch-review.md + 变更报告）→ `release/`；
- 逐卡分支差异审查 review-{task-id}.md → `review/<task-id>/`（与 review 工作流报告统一）；
- verify 报告 → `verify/<task-id>/`；runtime-review/verify/release 的 Location + Save-to 全部显式化；
- AGENTS.md 工件约定明确各生成物子目录；security-storage 全量迁移（14 根文件 → release/、
  30 逐卡报告 → review//verify/ 子目录、会话快照 → temp/、openspec/changes/.../release/ 清空），
  italent 18 个 release/review-T-*.md 同步归入 review/<task>/；task cards 等 34 处引用已更新。

**遗留观察项**：italent openspec-cn validate 存量失败（reconcile-state/spec.md 7 需求缺
`#### Scenario:` 块，spec 合规债，与本次迁移无关，建议走 spec/grilling 修复）；
security-storage reports/ 保留 prepare 期分析子报告（requirement/architecture/dependency/impact/risk，
project-context Phase 5 引用，非 release 产物）。

### [低] run-log 覆盖：governance/memory/java/integration.md 修改无对应运行日志

`governance/memory/java/integration.md` 于 2026-09-16 17:45 追加 28 行
（knowledge-api i18n 消息必须 ASCII + \uXXXX 转义，编码记忆），当日无 develop/review 等
运行日志与之对应（最近日志为 09-15 develop）。属 Coding Memory 惯例的合法记忆捕获，但按
2026-09-01 维护发现的 run-log 覆盖纪律，提交前需归属到某次已记录运行或补一条记忆捕获记录。

### [信息] projects/ 目录为符号链接，AGENTS.md 未注明

`projects/` → `/mnt/d/workspace/project-resources`（D 盘，87 仓）；活跃项目主 checkout 在
`/home/syske/ws/projects/`（WSL，7 仓）。此为 2026-09-03 用户主导迁移方案 A 的既定状态
（见 maintenance.yaml last_findings），AGENTS.md 结构图仍写「projects/ 为业务源码权威源」
未注明软链——文档漂移观察项，方案 B 落地时 workspace.yaml 路径应以 WSL 权威路径为准
（与 project-context.yaml Phase 6 一致）。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

| 检查项 | 结论 | 说明 |
|---|---|---|
| workflows/*.md 八段齐全且有序 | ✅ 过 | workflow-command-audit 0 blocker/0 warning（15 workflows / 13 commands），抽查 analysis/bootstrap/bugfix/change-impact/code-review 均 Purpose→Next 八段 |
| config/workflows/*.yaml 注册表最小化 | ✅ 过 | 全部仅 name/workflow/runtime 三段，无回涨（A1 未复发） |
| 引用路径 / 链接健康 | ✅ 过 | path-audit 712 refs 0 broken；projects/ 软链目标可访问 |
| doc-vs-reality | ✅ 过（已修复） | 原失败项：ADR-0008 声称 workspace.yaml 为映射单一来源 vs dev-setup 只写 project-context.yaml——方案 B 落地后 dev-setup Phase 10 生成/刷新 workspace.yaml，存量已回填（见 [高] 发现状态）；次要：AGENTS.md projects/ 软链未注明仍为观察项 |
| 状态卫生（.aic-state.yaml 引用） | ✅ 过 | last_project 与 4 个 projects 条目全部指向现存工作区 |
| run-log 覆盖 | ⚠️ 观察 | governance/memory/java/integration.md 修改无当日运行日志（见 [低] 发现） |
| 提案遗留 | ✅ 过 | proposal-audit 0 gate error；P41/P42/P46 维持 defer（季度回顾），P26/P28 action items 无新触发 |
| 工具门禁 | ✅ 过 | quick-check OK / lint 0/0/25 / path 0 broken / extensions-lint 0/0 / workflow-command-audit 0/0 |

---

## 四、修复动作与建议清单（AI 填写）

本次为 on-demand 专项：巡检阶段 read-first；方案 B 经用户确认（2026-09-17）后实施完毕。

### 已执行（巡检阶段）
- 无代码/文档改动（仅指标快照、报告、诊断日志写盘）。

### 已执行（方案 B 实施，用户确认 2026-09-17）
| # | 动作 | 落点 | 验证 |
|---|---|---|---|
| 1 | dev-setup Phase 10 增补 Repository Mapping（workspace.yaml）生成/刷新规则（ADR-0008 格式：available=service/path/branch/dev_branch/remote，unavailable=带 note，禁止虚构、禁止列非参与服务） | templates/runtime/runtime-dev-setup.md | check.py PASS / 无新增 CJK / 单测 268 OK |
| 2 | workflows/dev-setup.md Outputs + Exit Criteria 同步（Repository Mapping） | workflows/dev-setup.md | workflow-command-audit 交叉校验通过 |
| 3 | ADR-0008 执行者接线：悬空「AI 手动初始化」→ dev-setup Phase 10（2026-09-17） | rfc/ADR-0008-project-repo-mapping.md | 语言纪律区（英文）无违规 |
| 4 | 存量回填 4 个项目 workspace.yaml（italent 4 服务 / security-storage 2 / qa-housekeeping 2 / cool-test 0+2 unavailable） | workspaces/*/workspace.yaml（磁盘，非 ai-system git） | project_repos 8/8 读通；aic 菜单实测：3 个业务项目显示服务名，cool-test 保持 (no repo mapped) 属正确 |
| 5 | 顺带 minor-fix：governance/memory/java/integration.md 2026-09-16 追加块 8 个 CJK 字符（memory 必须英文，check.py 门禁 FAIL）→ 已英文化（站内信→station message 等） | governance/memory/java/integration.md | check.py PASS |

### 已执行（方案 X 实施，用户确认 2026-09-17；用户细化「统一落 review」）
| # | 动作 | 落点 | 验证 |
|---|---|---|---|
| 1 | release 包产物位置显式化：Save-to → `workspaces/<pid>/release/`（聚合 release-branch-review.md）；逐卡审查 Save-to → `workspaces/<pid>/review/<task-id>/review-<task-id>.md`；Outputs Location 同步 | templates/runtime/runtime-release.md | check.py PASS（workflow↔runtime 对齐） |
| 2 | workflows/release.md Location 同步（release 包 + 逐卡 → review/<task-id>/） | workflows/release.md | workflow-command-audit 通过 |
| 3 | review/verify 报告位置显式化：`review/<task-id>/`、`verify/<task-id>/`（per-task subdir） | templates/runtime/runtime-review.md + runtime-verify.md + workflows/review.md + workflows/verify.md | check.py PASS |
| 4 | AGENTS.md 工件约定澄清：生成报告子目录化（release 包 → release/；逐卡审查 + review 报告 → review/<task-id>/；verify → verify/<task-id>/；completion → openspec/changes/<change>/completion-reports/） | AGENTS.md（workspace 根） | 无 CJK |
| 5 | security-storage 迁移：14 根散文件 → release/（含 sql/）；openspec/changes/.../release/ 3 文件 → review/<task>/；30 逐卡 review/verify 报告 → review//verify/ 子目录；会话快照 → temp/；34 处 task cards/日志引用更新 | workspaces/202610-public-security-storage-no-ai-parse-optimization/（磁盘） | openspec-cn validate 通过；0 残留旧路径引用 |
| 6 | italent 同步：18 个 release/review-T-*.md → review/<task>/review-<task>.md（统一布局） | workspaces/202610-cool-italent-sync-plus/（磁盘） | openspec validate 存量失败（spec 债，与迁移无关，观察项） |

### 建议清单（待用户决策）

| # | 建议 | 变更等级 | 落点 |
|---|---|---|---|
| 1 | ~~方案 B（dev-setup 生成 workspace.yaml）~~ **已实施（2026-09-17 用户确认）** | — | — |
| 2 | 方案 A（显示回退 project-context.yaml）——方案 B 落地后不再必要，废弃 | — | — |
| 3 | 方案 C（repo 数据源统一：project-context.yaml 为权威，workspace.yaml 由 dev-setup 生成；project_meta 的 contexts/project.yaml 读取清理）——季度候选，治理 P22/2026-08-14 遗留 | 结构（季度窗口） | providers.py + 相关 runtime |
| 4 | run-log 覆盖：governance/memory/java/integration.md 的 2026-09-16 追加内容归属（本次仅修 CJK 违规，归属仍需提交前确认——文件当前未提交） | L1（提交前动作） | logs/ |
| 5 | 计划内下次周检（next_maintenance 2026-09-16 已到期）：本专项不推进；建议另排一次 weekly | — | — |

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-09 | OK | 0 |
| 2026-09-11 | OK | 0 |
| 2026-09-14 | OK | 0 |
| 2026-09-17 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 3 开放提案 / 2 open action items
  - 开放: P41-TR5-SECTION1-SEMANTICS.md
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P46-TR5-DEBT-VALIDATION-MARKER.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P28-CHANGE-ID-GENERATION.md:46 D：AI 可选生成（skill 层落点）——触发条件未到（不引入 wizard LLM，Evolution Principle）
