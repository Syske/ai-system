# Change Proposal: P72 — 受保护路径 + 破坏性操作默认拒绝（Protected Paths & Destructive Operations）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（新增声明式清单 `config/protected-paths.yaml` + Operating Rules 条款 + 一处机器检测 + 单测） |
| Author | AI Maintainer |
| Created | 2026-09-24 |
| Reference | `reports/INCIDENT-2026-09-24-ignored-state-wipe.md`（事故复盘）；用户 2026-09-24 收敛方案（受保护路径 + 破坏性操作两概念；**不做快照**）；`3c7dd9f`（logs 迁出仓库）· `e488ec7`（metrics 迁出仓库） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 事实（详见事故报告）

2026-09-24：一条 `git clean -fdx` 清空了 `ai-system` 工作树内所有**未跟踪 + 被忽略**路径 ——
约 200 份运行日志不可恢复。版本化文件零损失；但暴露了三条结构性缺陷：

| # | 缺陷 | 证据 |
|---|---|---|
| D1 | **关键路径无"受保护"声明**：哪些路径不允许被删除/移动/整体替换，全仓无一处声明 | 全仓无 protected 概念（本次新增） |
| D2 | **破坏性操作无默认拒绝**：删除/移动/重命名/替换/截断/整目录移除没有任何前置约束 | 事故命令一次通过 |
| D3 | **无检测**：被删后唯一信号是**间接**的（path-audit 断链），且不覆盖"机器本地、不在文档里被引用"的路径 | 日志被删后无任何门禁报警 |

### 1.2 为什么"机器本地路径"尤其危险

`logs/`、`metrics/` 按设计**不入库**（`runtime-diagnostic-log.md`：runtime state，机器本地）→
**git 恢复对它们毫无意义**。这类路径的正确防护不是快照，而是**位置 + 默认拒绝 + 检测**。

## 2. Goal

给两类概念装上**声明 + 默认拒绝 + 可检测**，且不引入快照、不改动既有运行语义：

> **① 受保护路径**：一份声明式清单，列出"禁止直接删除 / 移动 / 重命名 / 替换 / 截断 / 整目录移除"的路径。
> **② 破坏性操作**：对受保护路径的上述操作**默认拒绝**；例外须**先 dry-run 列出清单 + 用户显式确认**。

## 3. Options

### 3.1 Option A — 只靠纪律（把教训写进日志/记忆）

成本最低，但**无检测**：同类事故再次发生仍然只有间接信号。**不推荐为主方案**（可作为补充）。

### 3.2 Option B — 受保护路径 + 破坏性操作默认拒绝（**用户收敛方案，推荐**）

三个部件：

1. **声明式清单**：`config/protected-paths.yaml`（与 `branch-formats.yaml` / `comment-lint.yaml` 同类的
   配置资产）——**唯一来源**，规则与检测都引用它，不复制清单。
2. **行为条款**：`governance/AI_OPERATING_RULES.md`（**Always Load**，每次运行必进上下文）新增一节
   「Protected Paths & Destructive Operations」：默认拒绝 + 例外流程 + 破坏性 shell 命令清单
   + 提交信息 shell 纪律（本次事故的直接原因）。
3. **机器检测**：`tools/checks/` 新增一项（挂进 `check.py`）：
   - 受保护路径**不存在** → **ERROR**（等价于"被删/被改名"）
   - 受保护路径在 git 中显示为**删除/重命名**（工作树或暂存区） → **ERROR**
   - 运行时态目录（工作区层 `logs/`、`metrics/`）**缺失** → **WARN**（可能被清；新机器首启前属正常）
   - 仓库内**出现**历史位置 `ai-system/logs|metrics` → **WARN**（回归信号）

### 3.3 Option C — B + Snapshot / append-only / Mutation Guard

**用户明确否定**，理由充分：logs 本就不入 git → 快照对"恢复 git 内容"无意义；且实现重（需存储层、
写入约定、状态机）。**不做**。

### 3.4 Option D — 把整个工作区变成 git 仓库

异想（会把 projects/、workspaces/、外部仓库全部卷进一个仓）；且仍挡不住 `-x`。**排除**。

## 4. Recommendation

**采纳 Option B**（A 作为补充写入事故报告与 memory）。

### 4.1 建议的受保护清单（**待裁定**）

清单按"两类"原则收敛，避免膨胀成"什么都保护"（那样等于没有信号）：

| 类 | 路径 | 为什么保护 | git 可恢复？ |
|---|---|---|---|
| **机器本地运行时态** | `<workspace>/logs/` | 运行诊断记录；**不在 git** → 删了不可恢复 | ❌ 否 → 保护强度最高 |
| | `<workspace>/metrics/` | 健康快照（历史快照不可再生） | ❌ 否（仅当期可再生成） |
| | `~/.config/ai-system/env.yaml`（机器层） | 机器配置（JDK/Maven/k8s 通道） | ❌ 否 |
| **AI 系统本体** | `ai-system/governance/` | 规则、标准、策略、记忆本体 | ✅ 是（但**整体替换/批量删**仍须确认） |
| | `ai-system/skills/` · `ai-system/workflows/` · `ai-system/templates/` | 能力与流程契约 | ✅ 是 |
| | `ai-system/tools/` · `ai-system/config/` | 门禁工具与配置 | ✅ 是 |
| | `ai-system/rfc/` · `ai-system/reports/` | 决策记录与报告（审计面） | ✅ 是 |
| （历史位置） | `ai-system/logs/` · `ai-system/metrics/` | **不应再存在**；出现即回归 | — → 检测为 WARN |

**明确不保护**：`projects/`（业务仓由各自 git 管）· `workspaces/`、`temp/`、`outputs/`（可再生产物）·
`__pycache__`、构建产物（可再生）。

### 4.2 待裁决清单（每条带建议）

| # | 待裁决 | 建议 |
|---|---|---|
| 1 | 受保护清单范围 | 按 §4.1 的**两类**（机器本地运行时态 + AI 系统本体）；业务仓/可再生产物不列入 |
| 2 | 检测强度 | 受保护路径缺失/被删 = **ERROR**；运行时态缺失与历史位置回归 = **WARN** |
| 3 | 是否把「破坏性 shell 命令须先 dry-run + 用户确认」写入 Operating Rules | **写入**（本次直接原因：`-m` 携带反引号 → 命令替换；一并写明 `git commit -F -` + 引号定界 heredoc） |
| 4 | 是否需要 `aic` 命令入口（如 `aic protect list`） | **不需要**（清单是配置文件，检测在门禁；命令面无收益） |
| 5 | 是否做日志归档/保留（retention） | **本提案不做**：属独立生命周期问题（用户已指出：与误删防护是两件事） |
| 6 | 新检测文件放哪 | `tools/checks/protected_paths.py`（`checks/` 是 check.py 的检查项容器）+ 在 `checks/__init__.py` 接线 |

## 5. Proposed Changes（Option B）

| # | 改动 | 落点 | 规模 |
|---|---|---|---|
| 1 | 声明式清单（含每条理由与 git 可恢复性注释） | `config/protected-paths.yaml`（新，~35 行） | 小 |
| 2 | 行为条款：默认拒绝 + 例外流程（dry-run + 用户确认）+ 破坏性命令清单 + 提交信息 shell 纪律 | `governance/AI_OPERATING_RULES.md` 新增一节（**Always Load**，~20 行，英文） | 小 |
| 3 | 机器检测（4 类判据，见 §3.2） | `tools/checks/protected_paths.py`（新）+ `checks/__init__.py` 接线 | 中 |
| 4 | 单测（正反例：缺路径=ERROR · git 删除=ERROR · 运行时态缺失=WARN · 历史位置出现=WARN · 干净树=0 findings） | `cli/tests/test_protected_paths.py`（新） | 中 |
| 5 | 工作区层 `AGENTS.md` 同步（受保护概念 + 指向清单；非仓库文件，不入库） | `AGENTS.md` | 极小 |
| 6 | 事故报告与 memory 交叉引用 | `reports/INCIDENT-2026-09-24-*.md`（已建）· memory 条目（见 §7 待确认） | 小 |

**成本**：1 个新配置 + 1 个新检测文件 + 1 个新测试文件 + 2 处接线 · 约 120 行 ·
**固定 token 成本**：仅 Operating Rules 新增节（英文 ~20 行 ≈ +250 tok/run，Always Load）·
其余按需加载 · 无新命令、无新技能。

## 6. Validation Plan

1. **反证（必须）**：故意删一个受保护路径 → 检测必须 **ERROR**；故意把某受保护目录改名 → 同样 ERROR；
   故意在仓库内建 `ai-system/logs/` → **WARN**；清空工作区层 `metrics/` → **WARN**。
2. **不误报**：干净树上运行 → findings = 0（含新机器首启、CI checkout 场景：受保护路径存在性判据需
   明确"哪些在有 git 的 checkout 中必然存在、哪些只在机器上有"——机器本地项缺失只 WARN）。
3. **门禁回归**：单测全绿 · `check.py` / `repo-lint` / `path-audit` / `check-contract` /
   `workflow-command-audit` 全绿。
4. **规则可达性**：确认新条款在 `standards-loader` 的 `### Always Load` 覆盖范围内（AI_OPERATING_RULES 已在其中）。
5. **成本实测**：`prompt-metrics` 前后对比 Always Load 增量（预期 ~+250 tok/run）。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| **检测只能事后发现，不能阻止命令**（诚实说明） | 三层配合：位置（运行时态已在仓库外）+ Always-Load 规则（默认拒绝）+ 检测（缺失即 ERROR）；命令本身无法被 git 钩子拦截（git 无 pre-clean hook） |
| 受保护清单膨胀成"什么都保护" | §4.1 限定为**两类**，并写明"明确不保护"的清单 |
| 误报（新机器、CI） | 机器本地项缺失只 WARN；受保护路径存在性判据区分"git 必然存在"与"机器本地" |
| Always Load 增加固定成本 | 条款控制 ≤20 行英文；用 `prompt-metrics` 实测增量 |
| 与 git 自带恢复能力重叠而显得冗余 | 清单注释写明每条"git 可恢复？"——可恢复的仍需确认（整体替换/批量删代价高），不可恢复的必须保护 |
| 规则写了但 AI 不遵守 | 检测兜底（缺失即 ERROR）+ 事故报告与 memory 作为案例；不追求 100% 预防 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** —— 采纳收敛方案：① 受保护路径 + 破坏性操作默认拒绝 ② **不做快照**（logs 本就不入 git，快照无意义）③ 日志归档 retention 属独立生命周期问题，不在本提案；并要求「新增能力需要提案」（本提案即按此流程补立） | 2026-09-24 |
| User (AI Maintainer operator) | **Implemented** —— §4.2 六项按建议执行（清单两类 / 缺失 error·机器本地 warn / shell 纪律入规则 / 不加 aic 命令 / 不做 retention / 检测落 `checks/protected_paths.py`） | 2026-09-24 |

## Implementation Record

**实施时间**：2026-09-24（1 个能力提交 `cdd5d7f`；事故复盘另见 `reports/INCIDENT-2026-09-24-ignored-state-wipe.md`）

### §4.2 六项裁决的执行结果

| # | 裁决 | 执行 |
|---|---|---|
| 1 | 清单范围 | 按两类收敛：`machine-runtime-state`（3 项，missing=warn）+ `ai-system-body`（8 项，missing=error）；并显式写入 `not_protected`（projects/workspaces/temp/outputs）防膨胀 |
| 2 | 检测强度 | 受保护路径缺失→按类 error/warn · git 中删除/重命名→error · 仓库内出现历史位置→warn · 非 git 工作树→warn · 清单缺失→warn（跳过不崩） |
| 3 | shell 纪律入 Operating Rules | ✅ 写入 `AI_OPERATING_RULES.md` 新节：禁 `-m` + 反引号/`$( )`；一律 `git commit -F -` + 引号定界 heredoc（本次事故直接原因） |
| 4 | aic 命令入口 | 未加（清单是配置、检测在门禁，命令面无收益） |
| 5 | 日志 retention | 未做（独立生命周期问题） |
| 6 | 检测落点 | `tools/checks/protected_paths.py` + `checks/__init__.py` 接线（check.py 第 10 项） |

### 验证（提案 §6 要求）

1. **反证（真仓库实测，均已撤销）**：
   - 仓库内建 `logs/` → 检测**正确 WARN**；且 `test_real_repo_is_clean` 守卫测试 **fail-loud**（预期行为）
   - 把 `skills/` 临时改名 → 受保护路径缺失被检出；**同时相关测试与门禁集体 fail-loud** ——
     证明"改名/移动受保护目录"这类操作确实会造成广泛破坏，正是本能力要挡住的类型
2. **单测**：`cli/tests/test_protected_paths.py` 8 项（缺失 error/warn 分流 · git 删除 · 历史位置回归 ·
   非 git 工作树 · 清单缺失不崩 · 真仓库应干净）；全仓单测 **620 OK**（612 + 8）
3. **不误报**：干净树上本检测 0 findings（`check.py` 仍 PASS 且 2 个已知 warning 未变）；
   CI/新机器场景由 `missing: warn`（机器本地类）覆盖
4. **规则可达性**：新节在 `governance/AI_OPERATING_RULES.md` 内，该文件已在 `standards-loader` 的
   `### Always Load` → 每次运行必进上下文
5. **成本实测**：`AI_OPERATING_RULES.md` 14,366 → 15,985 字节（**+1,619 字节 ≈ +404 tok/run**，
   441 → 476 行）；Always Load 固定成本；`prompt-metrics` 前缀稳定 16/16 未破

### 与提案的偏差

- 清单新增 1 项超出提案示例：`<workspace>/metrics`（提案 §4.1 已含）与 3 项工作区/仓库占位符解析
  （`<repo>` / `<workspace>` / `~`）——机械实现细节，无实质偏差。
- `tools/README.md` 的 `check.py` 行同步为 **10 checks**（原写 9，属既有陈旧计数）。

### 未做 / 残留（诚实边界）

- **检测只能事后发现**，无法阻止命令本身（git 无 pre-clean 钩子）。预防 = 位置（运行时态在仓库外）+
  Always-Load 规则（默认拒绝 + dry-run/确认流程）+ 本检测。
- 不做快照/append-only/Mutation Guard（用户裁定）；日志 retention 归档为独立议题，按 Evolution Principle 待真实需要。