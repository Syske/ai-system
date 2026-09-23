# 系统巡检报告 — 2026-09-23（on-demand）

- 类型: 系统巡检（MAINTENANCE）
- 模式: **on-demand**（Scope: 盲检残债 R4 收尾 + skill-sync 价值裁决与归档）
- 日期: 2026-09-23
- 说明: 骨架由 `maintain-report.py` 按 weekly 生成，本节模式/范围与下表口径已按本次实际运行人工校正

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: **38** | Files: 38 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 97 |
| path | OK: no broken path dependencies（refs 783 / placeholders 140 / known_debt 3） |
| extensions | Summary: 0 errors, 0 warnings |
| 其它门禁 | check.py **PASS**（2 已知 warning）· unittest **516 OK** · workflow-command-audit 0/0 · proposal-audit 0 gate err / 0 gate warn |

> WARN 97 口径未变：96 为既有基线（`cli/**/*.py`、`tools/*.py` 英文注释类），第 97 条来自 R1 口径统一后
> `skills/architecture/design-review/SKILL.md` 首次进入 lint 视野（正当可见化）。

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 33 | 38 | **+5** |
| Workflows | 15 | 16 | +1 |
| RFC | 14 | 14 | = |
| Governance | 60 | 60 | = |
| Templates | 24 | 26 | +2 |

（上期快照 timestamp: 2026-09-21T17:17:13.558878；本期快照已按**归档后**状态刷新）

**变化原因核对**：Skills 33 → 38 是**两个方向**叠加，不是单一增长 ——
上期 33 为 **R1 技能枚举口径统一之前**的数（容器目录 `architecture/` 被当 1 个技能）；口径统一后为 39
（+6：容器自身不再计数、其下 7 个技能入列）；本期 **skill-sync 归档 −1 → 38**。
即 33 + 6 − 1 = 38。**不要**为让数字好看而回退枚举口径（见 `R4-HANDOVER` §6）。

---

## 二、巡检发现（AI 填写，按严重度分级）

### 信息 —— skill-sync 归档（本轮主任务，已执行）

用户问询「skill-sync 对我们有什么价值」，按 `AI_OPERATING_RULES` 的 Value-Burden Check 四步实证后
裁决 **archive**（2026-09-23，提交 `7032fb0`）。证据：唯一消费者 `skill-optimizer` / `iterative-optimizer`
已于 2026-08-17 归档；`logs/` `reports/` `outputs/` 全量搜**零条真实 push/pull 运行记录**；本机三个凭据
路径均不存在；`git log` 5 次提交首提后**全是审计驱动加固**（描述 lint / T5 / R1 安全 / R4 退出码），零功能提交。
负担：576 行 / 4 文件（其中 `sync-policy.js` 136 行整体是 R1 加固产物）+ 119 行契约测试。
决策报告见 `reports/VALUE-BURDEN-DECISION-skill-sync-2026-09-23.md`，执行记录见 `archived/ARCHIVE.md`。

### 中 —— 技能索引完整性缺口（**新发现**）

`k8s-logs` 是真实技能（`skills/k8s-logs/SKILL.md` 存在、`skill_index` 计数含它），但
`skills/README.md` **未登记**该行 → 索引与实现脱节（`repo-lint` 与索引各自为政，未被任何门禁拦截）。

### 低 —— `skills/README.md` 计数漂移（既有，R3 类）

`On-Demand Skills (10)` 声明与实际 **19 行**不符（含 2 行删除标记）；本轮已按实际行数更正**所触碰节**
（`Optimization & Benchmarking Skills` 由 `(6)` → `(1)`），其余节留给 R3 文档批次统一收口。

### 低 —— `path-audit` PATH_RE 无词边界（**新发现**，本轮实测 2 处误报）

`PATH_RE` 的路径前缀分支（`skills|reports|config|…`）**无负向后顾**，会匹配更长路径的**中间段**：
登记 `archived/skills/skill-sync/scripts/sync-policy.js` 时，子串 `skills/skill-sync/scripts/sync-policy.js`
被当作独立引用并被判 broken（本轮先绕开字面量规避）。同仓 `DOT_REL_RE` 早已用 `(?<![\w./])` 处理过同类误报
（`.../x.java` 尾部），属同一治理面。建议一行修复，但**属门禁口径变更 → 需确认后实施**。

### 信息 —— 未提交改动的日志归属（抽查命中，已归属）

`governance/memory/java/coding-memory.md` 处于**他人未提交**状态：无本 run 日志归属。
按 `R4-HANDOVER` §7 纪律**不代提交**（本 run 两次提交均只 `git add` 明确路径，提交前 `git show --stat` 核对）。

### 信息 —— `generate_contract` 场景条目缺 `服务` 字段（既有行为，未在 R4 清单内）

`format_entry_yaml` 的键清单为 `场景引用/调用方/被调用方/类型/协议/接口/主题`，**不含 `服务`**，
而 `build_scenario_entry` 是写入了 `服务` 的 → 产物中场景条目的服务名静默缺失。属既有行为、
与本轮 G1/G2/G3 不同根因，建议**单独立项**（未擅自修改）。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

抽查脚本 8 项（on-demand / Scope=skills+R4 定向）：**7 通过 / 1 失败**。

| # | 抽查项 | 结论 |
|---|---|---|
| 1 | `workflows/*.md` 八段齐备且有序 | ✅ 16 个工作流全通过 |
| 2 | `config/workflows/*.yaml` 注册表最小化（name/workflow/runtime） | ✅ 17 个注册表无回胀（A1 未复发） |
| 3 | 注册表 `workflow` / `runtime` 目标文件存在 | ✅ 全部存在 |
| 4 | 状态卫生：`workspaces/.aic-state.yaml` 项目引用存在 | ✅ 5 个项目引用均存在 |
| 5 | 运行日志覆盖（未提交改动可归属） | ⚠️ 命中 `coding-memory.md`（他人在途，已归属，不代提交） |
| 6 | Doc-vs-reality：`AGENTS.md` 顶层结构图目录存在 | ✅ 7 个顶层目录均在 |
| 7 | 技能索引完整性（README 覆盖全部技能） | ❌ **`k8s-logs` 未登记** |
| 8 | 活跃技能/工作流不引用 `archived/` | ✅ 唯一命中为 `workflows/external-review.md:65` 的**禁止载入**清单（语义正确，非陈旧引用） |

**首轮误报与自更正（记录以证口径）**：第 2 项初判 `bugfix-modes.yaml` 回胀 —— 实为**模式配置**
（非工作流注册表），已按「声明 `workflow:` 才校验」收敛；第 6 项初判 `openspec` / `contexts` 缺失 ——
实为 `AGENTS.md` 中 `workspaces/<project_id>/` 的**嵌套模板树**，已改为只校验顶层；第 8 项初版按
子串 `archived` 匹配 → 命中 `skills/README.md`（`~~archive-openspec~~` 标记）与
`repository-maintainer/checklists.md` 的普通词，已收敛为路径形态 `archived/`。

---

## 四、修复动作与建议清单（AI 填写）

### 本 run 已执行

| # | 动作 | 提交 | 验证 |
|---|---|---|---|
| 1 | R4 §2.1 `generate_contract` 三项（G1 标量引号 / G2 去重告警 / G3 服务匹配口径统一） | `015f022` | 危险标量回读 18 例 + 端到端产物 `yaml.safe_load` 通过；新增 9 测试 |
| 2 | skill-sync 归档 + 连带清理（README / T5 断言 / path-audit 注释 / maintenance.yaml 旧路径 / 索引登记） | `7032fb0` | 单测 516 OK · lint **38**/0/0/97 · path 0 broken |

### R4 进度（残债账本）

§2 共 8 项 → **已修 3**（G1/G2/G3）· **随归档关闭 1**（§2.2 `loadConfiguration` 去重：判决前在途重构已撤销，
不为将归档资产投入重构）· **余 4**（§2.3 S1 index-project venv 探测 · S2 k8s-logs 通道一致性 ·
S3 k8s_helper CrashLoopBackOff · S4 idea-mcp SSE 断连快速失败）。

### 建议（**需确认后实施**，本轮未擅自修改）

| # | 建议 | 级别 | 依据 |
|---|---|---|---|
| 1 | `skills/README.md` 补 `k8s-logs` 行，并统一更正各节计数（On-Demand `(10)` → 实际行数） | 低（文档） | §二 中/低发现；归入 R3 文档批次 |
| 2 | `tools/path-audit.py` `PATH_RE` 加负向后顾 `(?<![\w./])`（消中间段误报） | 低（门禁口径） | §二 低发现；与 `DOT_REL_RE` 既有做法一致 |
| 3 | `generate_contract.py` 场景条目补 `服务` 字段（或明确其不在产物契约内） | 低（产物正确性） | §二 信息级发现；建议单独立项 |
| 4 | 继续 R4 §2.3 四项（S3 → S1 → S4 → S2） | — | 交接文档 §9 建议顺序 |

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-09 | OK | 0 |
| 2026-09-11 | OK | 0 |
| 2026-09-14 | OK | 0 |
| 2026-09-17 | OK | 0 |
| 2026-09-21 | OK | 0 |
| 2026-09-22 | OK | 0 |
| 2026-09-23 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 5 开放提案 / 5 open action items
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P46-TR5-DEBT-VALIDATION-MARKER.md
  - 开放: P62-TASK-COMMIT-TRACEABILITY.md
  - 开放: P63-BRANCH-NAMING-NON-ITERATION.md
  - 开放: P64-SPEC-PRECONDITION-CONSISTENCY.md
  - P22-WSL-ENVIRONMENT-INTEGRATION.md:143 交互向导完整自动化测试（agent 启动后的真实交互断言）→ 仍开；2026-09-21 已有临时 mock 扫描（全目标循环检测），但未入库为常驻交互测试。
  - P22-WSL-ENVIRONMENT-INTEGRATION.md:144 `contexts/project.yaml` 与 `workspace.yaml` 两处 repo 路径来源统一（`repo_path_for` 仍只读 project.yaml，实际数据在 workspace.yaml）→ 仍开（季度候选 C；P58 已使 workspace.yaml 成为容器映射权威源，剩余为 `repo_path_for` 收口）。
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P28-CHANGE-ID-GENERATION.md:46 D：AI 可选生成（skill 层落点）——触发条件未到（不引入 wizard LLM，Evolution Principle）
  - P65-C2-PROFILE-SEMANTICS.md:298 C2（按需）：若业务侧提出「门禁须与 IDE 行为同源」，按 CI/批处理形态引入 IDEA 引擎基线（`format.sh`/`format.bat`，需解析 stdout 取代退出码、并处理单实例互斥与冷启动成本）—— 见 §C2 二审
