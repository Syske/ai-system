# Change Proposal: P34 — maintenance 状态纳入 ai-system 提交（拆分：系统级入 git / 机器级留本地）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (state management: 新增提交态文件 + 状态分层) |
| Author | AI Maintainer |
| Created | 2026-08-24 |
| Reference | 用户请求：maintenance 状态管理纳入 ai-system、跟随系统提交，方便跨机器维护；maintain on-demand/prepare 2026-08-24 后续 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

`workspaces/.aic-state.yaml` 位于 workspaces/（非 git 仓库），maintenance 状态（last_run / mode / next_maintenance / last_findings）**不随 ai-system 提交**，导致：

- 跨机器/跨环境拉取 ai-system 后看不到上一次维护时间与发现，maintenance 连续性断裂。
- 团队/CI 无法从 git 判断系统是否到期维护（ADR-0009 的 next_maintenance 调度只在本地）。

另：当前 `last_findings` 混入机器/环境噪音（如「当前机器未生成 ~/.config」「WSL python shim 不可用」「extensions 仓有未提交修改」），跨机入库后是无意义噪音，需解耦。

## 2. Root-Cause（根因分析）

`.aic-state.yaml` 混装五类状态，只有 `maintenance` 块是系统级可共享，其余是机器/工作区特定：

| 块 | 性质 | 能否入 git |
|---|---|---|
| `maintenance` | 系统级维护调度 + 发现 | ✅ 可共享 |
| `last_project` / `projects` | 机器活动（last workflow/action/task/change） | ❌ 跨机冲突 + 泄露活动 |
| `bootstrap` | 机器环境（environment=local / last_run） | ❌ 机器特定 |
| `projectless_usage` | 机器用法计数 / last_used 时间戳 | ❌ 机器特定 |
| `last_target` | 机器最近目标 | ❌ 机器特定 |

根因：未做状态分层——系统级与机器级混存一文件，导致「整文件入库」不可行（会跨机冲突、泄露），「不入库」又丢失系统级维护连续性。需**拆分**。

消费者盘点（fresh）：`maintenance` 块**完全由 AI 手改**，指令在 `cli/commands/aic-maintain.md:13/98` + `OPERATIONS.md:194`；**无 Python 工具读写**（quick-check.py / proposal-audit.py / maintain-delta.py / maintain-report.py 均不读该文件）。→ 迁移为 doc + 路径 + 文件搬迁，无代码重构。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| A. 整文件 `workspaces/.aic-state.yaml` 入 git | 全块提交 | 否决：机器特定块跨机冲突 + 泄露活动；违背状态分层 |
| **B. 拆分：maintenance 块 → config/maintenance.yaml（提交），其余留 workspaces/.aic-state.yaml（本地）；last_findings 只留系统级、环境噪音进 diagnostic-log（Recommended）** | 系统级入 git、机器级留本地；AI 按新路径读写 maintenance | 最小：无代码重构；跨机维护连续性达成；机器活动/环境噪音不泄露不污染；放 config/ 与现有静态 yaml 统一（解耦后文件精简、系统级调度语义适配 config/） |
| C. 放 ai-system/state/maintenance.yaml | 独立 state/ 顶层目录 | 可行但多一顶层目录；解耦后 maintenance.yaml 精简、更近「运维配置」，config/ 更统一 |
| D. 复用 reports/ 或 metrics/ | | 否决：reports/ 人类报告非机读状态；metrics/ 已 gitignore；语义不符 |

## 4. Recommendation（推荐方案 + 理由）

**方案 B**（位置：`config/maintenance.yaml`）。理由：

1. **最小改动**：无代码重构（StateStore 是通用 key-path 存储，路径由调用方传入；maintenance 块本就 AI 手改），仅 doc 路径 + 文件搬迁 + 新增提交文件。
2. **状态分层清晰**：系统级 maintenance 入 git（跨机共享）；机器级活动留 workspaces 本地（不泄露、不冲突）；与 P29 机器层 ~/.config 形成「机器 / 工作区 / 系统」三层。
3. **跨机连续性**：拉取 ai-system 即见上次维护时间/发现/next_maintenance，CI/团队可判到期。
4. **噪音解耦**：`last_findings` 只留系统级（指标/门禁/提案/修复）；机器/环境观察（python shim、extensions 脏、机器未生成配置）只进 diagnostic-log（本地）。判定：含「当前机器」「WSL」「shim」「extensions 仓…未提交」字样 → 不入提交态。
5. **config/ 统一**：解耦后 maintenance.yaml 为精简系统级调度文件，与 config/ 现有 yaml 统一；省一顶层 state/ 目录。
6. **风险可控**：maintenance 更新频率低（weekly+），冲突罕发且取最新即可。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改**；批准后按 OPERATIONS §12 Implement 阶段执行。

1. 新建 `ai-system/config/maintenance.yaml`（提交态），承载 `maintenance` 块（last_run/mode/scope/next_maintenance/last_findings），内容取自当前 `workspaces/.aic-state.yaml` 的 maintenance 块。
2. **last_findings 解耦**：迁入时剔除机器/环境噪音（当前 #7 尾段「当前机器未生成」+ #8 整条「WSL python shim / extensions 仓未提交」），只保留系统级 findings（#1–#6）；#6 尾段残留碎片（`/ check.py PASS / CLI 123 测试 OK`）一并清理。环境噪音已在本次 maintain diagnostic-log（logs/，本地）留迹，不丢。
3. 从 `workspaces/.aic-state.yaml` **移除** `maintenance` 块（保留 last_project/projects/bootstrap/projectless_usage/last_target）。
4. 更新 doc 指令路径：
   - `cli/commands/aic-maintain.md:13`（读 next_maintenance）→ `config/maintenance.yaml`
   - `cli/commands/aic-maintain.md:98`（写 maintenance 块）→ `config/maintenance.yaml`；并在 Outputs/状态更新处加「last_findings 只留系统级；机器/环境观察进 diagnostic-log」约定。
   - `OPERATIONS.md:194`（Due maintenance 检查）→ 新路径
5. `.gitignore` 不变（`config/` 不在忽略列；确认 `config/maintenance.yaml` 可提交）。
6. quick-check.py / proposal-audit.py / maintain-delta.py / maintain-report.py 无需改（不读该块）。
7. 不建 ADR（按 rfc/README 三条件：非 hard-to-reverse、非 surprising、无真实 trade-off——方案选择已由本提案记录；状态分层与 P29 一脉相承，inline 级即可）。

## 6. Validation Plan（如何验证）

- `git -C ai-system check-ignore -v config/maintenance.yaml` → 未被忽略（可提交）。
- `git -C ai-system status` → `config/maintenance.yaml` 为新增可提交文件。
- 噪音解耦验证：`grep -iE "WSL|shim|当前机器|extensions 仓.*未提交" config/maintenance.yaml` → 0 命中（系统级 only）。
- `python tools/check.py` / `repo-lint.py` / `path-audit.py` / `quick-check.py` 全绿。
- `python tools/proposal-audit.py`：P34 登记一致、无新增 ERROR/WARN。
- 文档一致性：`grep -rn "workspaces/.aic-state.yaml.*maintenance\|aic-state.yaml → maintenance" cli/ OPERATIONS.md` → 旧路径引用已替换为 `config/maintenance.yaml`。
- 行为回归：下一次 maintain 运行，AI 按 `config/maintenance.yaml` 读写 maintenance 块、last_findings 只留系统级；`workspaces/.aic-state.yaml` 仅留机器级字段；机器/环境观察进 diagnostic-log。

## 7. Risks（风险与缓解）

- 风险低：无代码重构，仅 doc + 文件搬迁；StateStore 与 wizard 不受影响（它们读写机器级块，路径不变）。
- 缓解：实施时确认 `config/` 可提交、maintenance.yaml 不与现有 config yaml 语义混淆（它是唯一高频变动项，但解耦后为精简调度文件，可接受）；migration 后跑一次 maintain 确认 AI 按新路径读写、last_findings 不含机器噪音；若将来确有工具需读 maintenance（目前无），再单独评估。
- 并发：多机同期维护冲突罕发（weekly cadence），取 latest 解决；可接受。
- 语义取舍：config/ 现为静态能力配置，maintenance.yaml 为高频变动运行态；解耦噪音后语义收敛为「系统运维调度」，可接受；若日后出现更多运行态文件再评估独立 state/ 目录。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-24 |

---

## Implementation Record

Approved per proposal-policy §2 + OPERATIONS §12 → Implement → Validate。方案 B（位置
`config/maintenance.yaml`，含噪音解耦）：

1. 新建 `ai-system/config/maintenance.yaml`（提交态），承载 maintenance 块
   （last_run/mode/scope/next_maintenance/last_findings），含精简 header 说明系统级范围 +
   机器观察进 logs/ 的纪律。
2. **last_findings 解耦**：迁入时剔除机器/环境噪音（原 #7 尾段「当前机器未生成」+
   #8 整条「WSL python shim / extensions 仓未提交」）+ #6 残留碎片，只保留系统级 6 条。
3. 从 `workspaces/.aic-state.yaml` **移除** maintenance 块（保留
   last_project/projects/bootstrap/projectless_usage/last_target 机器级字段，并加注释指向新位置）。
4. 更新 doc 路径：`cli/commands/aic-maintain.md:13`（读 next_maintenance）+ `:98`
   （写 maintenance 块 + 加 last_findings 系统级纪律与触发词判定）+ `OPERATIONS.md:194`
   （Due maintenance 检查）→ `config/maintenance.yaml`。
5. quick-check.py / proposal-audit.py / maintain-delta.py / maintain-report.py 无需改（不读该块）。
6. 未建 ADR（非 hard-to-reverse / 非 surprising / 无真实 trade-off）。

**Validation**（gate，fresh）：
- `git check-ignore -v config/maintenance.yaml` → 未被忽略（可提交）。
- 噪音解耦：`grep -icE "WSL|shim|当前机器|extensions 仓.*未提交" config/maintenance.yaml` → 0。
- `path-audit.py` → BROKEN 0（初稿 finding[1] 误写 `cli/reports/templates/tools` 斜杠连接被当路径，已改逗号分隔 `cli, reports, templates, tools` 复原）。
- `repo-lint.py` 0-0-25 / `quick-check.py` OK(0) / `proposal-audit.py` 0-0。
- 文档一致性：`grep -rn "workspaces/.aic-state.yaml" cli/commands/ OPERATIONS.md | grep -i maintenance` → 0 残留。
- 状态分层：`workspaces/.aic-state.yaml` keys 不含 maintenance（仅机器级）；maintenance 系统级在 config/。
