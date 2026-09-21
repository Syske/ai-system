# 系统巡检报告 — 2026-09-21（on-demand）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- 日期: 2026-09-21
- 范围: scan 命令「循环选择项目」问题 + 「缺少选择具体 service」问题（使用过程反馈）

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0，2026-09-21 快照） |
| lint | Skills: 32 | Files: 32 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 30 |
| path | OK: no broken path dependencies（254 files / 730 refs） |
| check.py | **FAIL 1**（memory 中文门禁）+ 2 WARN（提案遗留） |
| workflow-command-audit | 15 workflows / 13 commands：0 blocker 0 warn |
| proposal-audit | 3 提案未关闭 + 2 action items |

### 指标对比（2026-09-17 → 2026-09-21 快照）

- skills: 30 → 33（+3：spec-updater/openspec-archive-change/openspec-explore 迁入）
- workflows: 15 → 15（稳定）
- rfc: 14 → 14
- governance: 59 → 60（+1：evidence-levels.md 等）
- templates: 22 → 23（+1）

quick-check 趋势：近 5 个快照（09-09 / 09-11 / 09-14 / 09-17 / 09-21）全 OK，无工具链回退。

---

## 二、巡检发现（按严重度分级）

### 【高】F1 — 机器层环境配置残留临时路径 → scan 的 Projects/Branch 字段 0 选项

- 现象：wizard 选项目容器 → 选 scan 后，「Projects」字段候选为空、「Branch」字段为空
  （用户无法选择具体 service，也推导不出分支）。
- 复现证据（本次实测）：
  - `config/environments/local.yaml`（未入库、机器本地）的 `workspace.root` /
    `workspace.repository_root` / `layers.projects.path` / `layers.skills.path`
    全部指向 `/tmp/tmp4qyb9n9t`（**已删除**的测试临时目录）。
  - 机器层 `~/.config/ai-system/env.yaml` 只有 `workspace.root`（深合并按 key 覆盖）：
    root 被修正为 `/home/syske/ws/ai-workspace`，但 `repository_root` 未覆盖 →
    `projects_root = /tmp/tmp4qyb9n9t/projects`（不存在）。
  - 实测 `projects_root: /tmp/tmp4qyb9n9t/projects`；`Projects` 字段 choices=0，
    `git_branches` 找不到任何 repo。
- 影响面：scan / change-impact / code-review / proposal 的 Projects 字段、Branch 推导、
  `repo_path_for` 兜底（projects_root/<pid>）全部失效。
- 处置：机器级观察 → 进诊断日志；修复 = 就地修正 local.yaml（删除残留路径或显式指向
  真实 repository_root）——**待用户确认**（Change Control）。

### 【高】F2 — scan「循环选择项目」：字段收集验证失败后 step=2 重收全部字段 → 死循环

- 现象链（用户反馈的「循环选择项目」）：
  1. step 0 选择项目容器（workspaces/，8 个）→ step 1 选 scan；
  2. 「Workspace」字段再次列出**同一批 8 个容器**（与 step 0 重复，观感即"再次选项目"）；
  3. 「Projects」字段因 F1 为空 → 用户跳过；
  4. `ScanHooks.validate` 失败（未选 Workspace 且 Projects 空）→ `steps.py` 置
     `step = 2` 重问**全部字段**；
  5. 再次跳过 → 再次失败 → **无限循环**（唯一出口：选 Workspace / Projects 手输任意
     非空字符串 / 连按 BACK 退出）。
- 复现证据（本次实测）：`validate(空 Workspace、空 Projects) = False`；
  `validate(空 Workspace、手输任意项目名) = True` —— 校验只查真值**不验名称存在性**，
  与 aic-scan.md Step 1「无可用范围则报告并停止」的运行时语义不一致（假通过后运行期才报错）。
- 处置：结构性问题 → **仅输出建议**（见修复建议 C）。

### 【中】F3 — 缺少 service 级选择入口（「当前入口都需要先选项目」）

- 现状：wizard 唯一的「项目」概念是**工作区容器**（workspaces/<pid>，step 0 必选，
  或 system / AI 引导）；service（仓库）级选择只有 `projects_dirs()` 的**扁平全量**
  （projects/ 下 70+），**不按所选容器的 workspace.yaml 映射过滤**。
- 已选中容器 `202610-cool-italent-sync-plus`（映射 4 服务：platform-api /
  user-center-api / bs-integration / cmdb-api）后，仍无法只扫其中 1 个服务。
- doc-vs-reality：`workflows/change-impact.md` 声称「有项目容器时也可从 workspace.yaml
  映射选择」，但 CLI 未实现（`providers.project_repos` 仅用于容器列表展示与 skill_launcher，
  未接入 Projects 字段）。
- 处置：结构性问题 → **仅输出建议**（见修复建议 B）。

### 【中】F4 — memory 门禁缺口 + run-log 覆盖观察项

- `governance/memory/java/integration.md`（+466 CJK）与 `coding-memory.md`（+187 CJK）
  存在**未提交**中文块（2026-09-20 实证内容），`check.py` FAIL
  （"AI System memory must be English"）。
- 预提交钩子只跑 repo-lint Rule 4 + contract：实测
  `repo-lint --files governance/memory/java/integration.md` **exit 0** →
  memory 中文可通过提交钩子（`tools/checks/memory.py` 门禁只在 check.py 全量时生效）。
- 同类问题 2026-09-16（c404753）、2026-09-18（4f26f14）已两次修复 → **≥2 次重复观察**，
  按 logs recycle 判定应固化为门禁/纪律。
- run-log 覆盖：这两处改动**无当日归属日志**，提交前需确认来源（2026-09-01 巡检同类发现）。

### 【低】F5 — 提案遗留（既有定案，继续 defer）

- P41/P42/P46（TR5，status=Proposed）+ P26/P28 action items（延迟设计项）——
  处置：defer（与 2026-09-17 判定一致，非本次范围）。

### 【信息】F6 — 双仓库根并存（机器观察，P58 已解决）

- 原：本机同时存在 `/home/syske/ws/projects`（7 服务，workspace.yaml 映射指向此处）与
  `/home/syske/ws/ai-workspace/projects`（软链 → D 盘池 `/mnt/d/workspace/project-resources`）。
- P58 实施后（2026-09-21）：projects/ 改真实目录，7 服务移入并 `git worktree repair`；
  workspace.yaml 路径归一为相对 service id；`/home/syske/ws/projects` 已移除；
  D 盘池解链（只读参考，不再入 projects 供给）。软链目标记录于诊断日志。

### 【高】G1 — change-impact 与 scan 同款死循环（hook-validate 失败路径为通用问题）

- `ChangeImpactHooks.validate`（Projects 空 → FAIL）→ `steps.py` `step=2` 全量重收 →
  再失败 → **死循环**（同 F2）。Projects 必填且当前 0 候选（F1）→ 更易触发。
- 结论：F2 不是 scan 专属，而是 **steps.py hook-validate 失败路径的通用缺陷**；
  P57 需显式覆盖 change-impact（当前第 4/5 项仅点名 ScanHooks）。

### 【中】G2 — code-review / change-impact / proposal 的 Projects 字段候选缺失

- 当前 0 候选（F1 当机根因）；F1 修复后为 projects/ 扁平全量（F3，无容器映射）。
- code-review 的 Projects 为**必填**，其文档声称「从 workspace.yaml 映射选择」——
  该映射选择从未在 CLI 实现（doc-vs-reality，与 F3 同根）。

### 【中】G3 — Review Focus 预置候选未接线（09-11 半实现遗留）

- 09-11 已把 10 项候选（性能/安全/正确性/并发/兼容性/错误处理/日志/资源管理/标准合规/
  代码质量）写入 `menu.yaml field_choices` + `multi_select_fields`，但
  `_choices_for` 分派表**缺 "Review Focus"** → 实际走自由文本，候选从不展示。
- 实测：`_choices_for({}, "Review Focus") = []`；`git log -S "Review Focus"` 无 wizard 层
  历史；`cli/tests/` 无 Review Focus 用例。
- 建议：并入 P57（同 `_choices_for` 候选接线主题）。

### 【低】G4 — Environment 字段无候选（信息）

- env-init / bootstrap 的 Environment 字段无候选提供器 → 自由文本（当前仅 local 环境，
  文档默认 local，影响小）。可选：候选 = config/environments/*.yaml 列表。

### 【确认无问题】其余非主开发链流程

- trace / task（有容器 Change ID 候选正常）；explore / skill-source / workflow / command /
  extensions-init（自由文本字段设计正确）；analysis / knowledge（Analysis Target / Analysis
  Scope / Knowledge Operation 候选已接线）；bugfix / hotfix-test-doc（hidden，字段合理，
  bugfix 的 Project ID 有容器候选）；proposal（Projects 可选，Topic 自由文本正确）。

---

## 三、一致性抽查结论（逐项通过/失败）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| workflows/*.md 八节结构与顺序 | ✅ | workflow-command-audit 0 blocker 0 warn |
| workflow 术语与 README 选择表 | ✅ | 15 工作流全注册、无孤儿文件 |
| config/workflow-registry.yaml → workflows → runtime 引用链 | ✅ | 0 missing |
| config/workflows/*.yaml 保持最小（name/workflow/runtime） | ✅ | 无 A1 复发（bugfix-modes.yaml 为独立模式配置） |
| 引用路径存在（standards/loaders/prompts/commands） | ✅ | path-audit 0 broken |
| 文档-现实一致（AGENTS.md / CONTRACT / OPERATIONS） | ⚠️ | 2 处例外：change-impact.md「workspace.yaml 映射选择」未实现（F3/G2）；code-review.md Review Focus 候选配置未接线（G3） |
| 状态卫生（.aic-state.yaml 项目引用） | ✅ | 4/4 容器存在 |
| run-log 覆盖（未提交改动 vs 日志） | ❌ | memory 2 文件未提交改动无归属日志（F4） |
| proposal 遗留 | ⚠️ | 4 提案（+P57 Proposed）+ 2 action（处置：defer / P57 待评审） |
| quick-check 趋势 | ✅ | 连续 5 个快照 OK |
| 非主开发链菜单流程逐一诊断 | ⚠️ | 14 项流程中：change-impact 死循环（G1）、Projects 候选缺失（G2）、Review Focus 未接线（G3）、Environment 无候选（G4，低）；其余 10 项无问题 |

---

## 四、修复动作与建议清单

**本次实际修复**：
- **P57 已实施（2026-09-21）**：候选驱动 service 选择（Projects 候选 = 容器 workspace.yaml
  映射服务，无容器回退 repositories 元数据 ∪ projects/ 本地）+ Branch 候选（dev_branch + git
  分支，单候选自动采用）+ Review Focus 候选接线（G3）+ hook-validate 失败改重问单字段
  （F2/G1 死循环消除，scan / change-impact 双双覆盖）+ `_scope_empty` 名称存在性校验 + 16 新测试。
- **P58 已实施（2026-09-21）**：projects/ 真实目录 + repositories 源按需 clone —— 新增
  `tools/repo-ensure.py`（ensure/check/list/validate）；setup scaffold 顺序 repositories 先于
  projects；providers 候选 = 元数据 ∪ 本地克隆；本机解链 + 7 服务移入 + worktree repair +
  路径归一（相对 service id）；317 单测 OK、门禁全绿。
- **小修 A/E 已执行（2026-09-21）**：A 机器层 local.yaml 移除 /tmp 残留路径（projects_root
  恢复，无容器回退 82→77 元数据驱动）；E memory 中文块翻译为英文（CJK 466+187 → 0，check.py
  PASS）。
- **模板折行专项（2026-09-21，用户手动改动实测）**：实测折行收益 **41/130,975 字符
  （0.03%，≈10 tokens）** + 引入 3 处丢空格 → 判定**净负价值**，回退纯折行 hunk
  （保留全角括号真修复）；立 **P59** 并新增 `templates/README.md` 固化模板层作者纪律
  （不 reflow 为 AI 优化 / 省 token 靠内容与骨架 / 换行承载语义处保留 / 批量改写必须归一比对）。
- **Tier 1 批量（2026-09-21，用户确认执行）**：
  ① `pre-commit` 补 memory 英文纪律门禁（并修 `tools/checks/memory.py` 按名排除漏洞：
  主题级 `coding-memory.md` 此前被 `check.py` 漏检——实测修复后能拦下）；新增
  `staged_memory_files`/`memory_language_check` + 4 单测，端到端实测钩子 exit=1；
  ② 提案状态漂移同步：P22 / P29 `Approved` → **Implemented**（追记实施记录 + 索引同步；
  P22 残留 2 项转 checkbox 跟踪）；③ AGENTS.md 文档漂移：`docs/` 描述修正（RFC/ADR 在
  `ai-system/rfc/`）+ 非规范目录改为“may appear”（实际均不存在）。
- **Tier 2 批量（2026-09-21，用户确认执行）**：
  ① **extensions 仓 13 项未提交归因并入库**（2026-09-11 工作遗留，mtime 佐证）：
  `hotfix-test-doc` 脚本自包含化（Confluence 脚本迁入 + 去外部扩展依赖 + 去硬编码
  Windows 路径）；提交前 py_compile 8/8 OK、无硬编码凭据、extensions-lint 0/0；
  另修 **extensions pre-commit 误报**（`token=token)` 被误判 HIGH，阻断合法提交）——
  `scan_sensitive.py` 变量链终止符扩为 `[(),\[\]}]`（安全性不变，回归矩阵验证）；
  提交：`5a34de0`（自包含化）+ `ebf86b7`（扫描器修复 + 教训 6）。
  ② **D 盘池定位明确化**（P58 残留）：`runtime-dev-setup.md` 增「Repository Sourcing
  (P58 — authoritative)」子节（元数据源 = repositories/；projects/ 真实目录按需 clone；
  机器路径遗留池为只读参考、非来源）；AGENTS.md 同步。提交 `4749b2d`。
  ③ **TR5 提案收口**：**P41 实施**（§1 语义特判 + §18 工时 4-8h 校验 + tr4_url 条件化 +
  SKILL.md 校验语义；`test_tr5_scripts` 16 用例全绿、真实数据 0 error；P41-c 服务名正则
  已失效——check_spec 重构已移除）→ Status **Implemented**（extensions `6d8a176`）；
  **P46 = 已准确记录**（(b) 已实施 00c8c34 / (a) 待线上 TR5 update，Status=Proposed 无误）；
  **P42 未实施**（需 19 节 markdown 骨架创作 + 构建验证，建议专项）→ 保留 Proposed。

**结构/治理类建议（仅输出，走提案；B/C 已按用户指示参照 code-review 交互流程细化）**：

> **参考：code-review 交互流程（runtime-code-review.md Phase 1 Target Resolution）**
> 1. Projects 输入：一次性任务 = 仓库路径/URL 逗号分隔；有项目容器 = 从 workspace.yaml 映射选择
>    （`repository.available[].service`）；
> 2. 候选驱动：收集候选（workspace.yaml dev_branch → git 分支）→ **单一候选直接采用**、
>    **多候选呈现用户选择（AskUserQuestion）**、**零候选/无覆盖则 ASK 不猜测**；
> 3. 不重复询问：Branch Mapping 显式覆盖时不 double-ask；
> 4. service 级粒度：每项目独立解析（多项目共享 theme、分支各自解析）；解析前验证分支存在，否则停该项目。

- B. **scan 的 service 级选择（参照 code-review）**：选中项目容器后，Projects 字段优先呈现
  该容器 `workspace.yaml → repository.available[].service` 作为候选（复用 `providers.project_repos`），
  替代当前扁平全量 projects/ 或空列表；多选由用户勾选（保持 choose_many）；无容器/无映射时才回退
  projects/ 全量。手输名称时校验存在性，不存在则呈现候选询问（不猜测、不回退死循环）。
- C. **死循环出口（参照 code-review「ASK 不猜测」）**：`ScanHooks.validate` 失败不再 step=2
  全量重收；改为停住并呈现候选询问（Projects 候选 = 容器映射服务；Branch 候选 = workspace.yaml
  dev_branch + git 分支，单候选自动、多候选选择、零候选询问），并保留明确退出/返回入口；
  `_scope_empty` 增加名称存在性校验，与 aic-scan.md Step 1 对齐（F2）。
- D. 预提交门禁补 memory CJK 检查（pre_commit_gate 增加 memory 门禁调用）（F4）。

---

## 五、后续维护状态

- next_maintenance 2026-09-16 已到期：建议另排一次 weekly（本 on-demand 专项不推进计划内下次）。
