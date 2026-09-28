# Change Proposal: P74 — reports/ 目录分类治理（按类型建子目录 + 引用地址治理）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural（资产目录布局契约：分类维度、迁移映射、门禁与引用同步） |
| Author | AI Maintainer |
| Created | 2026-09-28 |
| Reference | 用户 2026-09-28 指示「reports 目录的管理，需要按类型创建文件夹，并更新引用地址」；同日本会话前置事件：`prepare-beecount-2608` 业务产物误入 `reports/`（`3b6206c` 已删，暴露归属无门禁）；`governance/policies/proposal-policy.md` §6；`AGENTS.md` 工件目录约定 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状事实，带证据）

### 1.1 盘面

`reports/` 当前 **124 个 .md + 5 个目录**，全部平铺在顶层，无分类：

| 类型 | 数量 | 命名形态 | 是否被工具按路径耦合 |
|---|---|---|---|
| 提案 P 系列 | 66 | `P<n>-<TOPIC>.md` | **是**（`proposal-audit.py` 4 处 `glob`） |
| 巡检报告 | 30 | `MAINTENANCE-<date>[-<scope>].md`（含 2 个无横线历史形态） | **是**（`maintain-report.py:26,210`） |
| 其他单文件报告 | 26 | 大写连字符 / 小写混合，语义前缀不统一 | 否 |
| 多文件报告目录 | 5 | `analysis-<date>-<topic>/`（3）、`skill-source-<date>-<skill>/`（2） | 否 |

### 1.2 四个具体缺陷

**F1 — 归属无门禁，异类产物可直接落入。** 本日 `reports/prepare-beecount-2608/`
（BeeCount 第三方开源 App 的**业务** prepare 产物，7 份报告）以一次
`chore: add prepare-beecount-2608 report` 误提交进入 `reports/`，**全仓零引用、
工作区无对应项目、仅 1 次提交无演进** —— 是纯孤儿。`proposal-policy.md` §6 只要求
「登记进索引」，**不校验归属是否正确**；未登记才 WARN，而它当时被登记了
（否则 check.py 会报 `not registered`），故从未触发任何告警。

**F2 — 分类维度未定义，同类不同形态。** 5 个多文件目录用 `analysis-<date>-<topic>/`、
`skill-source-<date>-<skill>/` 两种**各自发明的**前缀；26 个单文件报告里
`ARCHITECTURE-ASSESSMENT-2026-07.md`（大写）与
`wayfinder-value-reevaluation-2026-09-17.md`（小写）并存；`DAILY-2026-08-08.md`、
`MIGRATION-PLAN-v2.md`、`SPOTLESS-FORMAT-GATE-PROPOSAL.md` 各自为政。
**没有任何文档定义 reports/ 应有哪些类别**。

**F3 — 索引只登记不分类。** `reports/README.md` 已按「提案 / 巡检 / 评估与评审报告」
分节，但 (a) 分节与磁盘布局**无对应关系**（磁盘是平铺）；(b) 66 份提案的 P 系列
在 README 与 `PROPOSALS.md` **双索引重复登记**；(c) `README.md` 用**裸文件名**登记
（`MAINTENANCE-2026-09-28.md`），无目录前缀 → 一旦引入子目录，索引即失效。

**F4 — 引用脆弱，无链接校验。** 全仓 **149 处** `reports/<file>.md` 引用，散落
**63 个文件**（含 `cli/commands/` 3、`templates/runtime/` 2、`governance/policies/` 2、
`skills/` 2、`tools/README.md`）。`path-audit.py` **不检查 reports 内部引用**
（`reports/` 内的路径引用不在其 broken 判据范围，仅有 `reports/foo-skill/` 一条
反例豁免）。实测：移动任一被引文件，**无门禁会报错**，只会静默留下死链。

### 1.3 为什么不能直接动手搬

搬动会同时触发 5 处硬耦合（§5.2），其中 3 处是**门禁代码**（proposal-audit 的
`glob` 假设平铺、maintain-report 的写死路径、protected-paths 的整目录声明）。
proposal-audit 用 `reports.glob("P*.md")` 而非 `rglob` → **一旦 P 系列进子目录，
66 份提案对门禁直接隐形**（Status 校验、索引一致性校验、open-item 扫描全部失效，
且失效是**静默**的）。这正是 R4 记录的「门禁静默失效」类缺陷。

---

## 2. Goal

1. **归属有门禁**：业务产物/临时产物**不能**进入 `reports/`（F1 根治）。
2. **分类有定义**：类别清单写进治理文档，磁盘布局 = 分类布局（F2 根治）。
3. **索引与布局一致**：索引登记含目录前缀，评审与提案状态机可机械核对（F3 根治）。
4. **引用不悬空**：迁移后引用全部同步，且**新增门禁防止再断**（F4 根治）。
5. **门禁不失明**：任何分类调整都不得让 proposal-audit 静默漏扫（§1.3）。

**非目标**：不删改任何报告内容；不重命名既有提案编号（P1–P73 编号与外部引用稳定）；
不引入新工作流/新命令；不把 `reports/` 迁出仓库（它属 `ai-system-body` 受保护路径）。

---

## 3. Options

### 3.1 Option A — 只加「归属门禁」，不动布局（最小）

新增 `tools/checks/reports_scope.py`（或并入 `proposal-audit`）：校验
`reports/` 下每个条目属允许类别（按命名模式白名单 + 可选 frontmatter `type:`），
业务产物模式 → ERROR。**布局保持平铺。**

- ✅ 零迁移、零引用改动、零门禁失明风险；直击 F1（本次事故的真因）
- ❌ 不解决 F2（分类未定义）/ F3（索引无目录）/ F4（引用脆弱）

### 3.2 Option B — 平铺 + 命名规范（次小）

保持平铺，用统一命名前缀表达类别（`ASSESSMENT-` / `INCIDENT-` / `MIGRATION-` …），
补 `reports/README.md` 分类清单 + 归属门禁。

- ✅ 引用全不动（文件名不变）；分类可读；门禁零失明
- ❌ 124 文件平铺的可浏览性问题未解（`ls` 仍是一长串）；用户明确要求「按类型创建文件夹」
- ❌ 前缀 proliferate（现有 26 个单文件已有 8+ 种前缀风格，再加规范 = 长期混淆）

### 3.3 Option C — 引入子目录分类 + 全量迁移 + 引用同步（**推荐**）

按类型建子目录，全量迁移，同步全部引用与门禁。

**分类方案（3 类，按「是否被工具路径耦合」分层，这是关键判据）**：

```text
reports/
├── proposals/     P 系列提案（66）—— 唯一有工具耦合的类别
├── maintenance/   巡检报告（30）—— 唯一有写侧耦合的类别
├── assessments/   评估/评审/诊断（架构、gap、ADR 合规、cache、CLI、三方 skill…）
├── incidents/     事故与复盘（INCIDENT-*）
├── migrations/    迁移（pack 迁移、README_MIGRATION 相关报告）
├── analysis/      多文件结构分析（现 3 个 analysis-* 目录并入）
├── skill-sources/ 单文件 skill 溯源（现 2 个 skill-source-* 目录并入）
└── README.md · PROPOSALS.md（索引，留在顶层）
```

**判据说明**：为什么只有 `proposals/` 与 `maintenance/` 需要工具改路径 —— 因为
`proposal-audit.py` 的 `glob("P*.md")` 与 `maintain-report.py` 的写死输出路径
**假设了平铺**。其余 5 类无任何代码按路径消费它们，纯粹是文档组织需求，
迁移只影响索引与引用文本。

- ✅ 三项缺陷全解；`ls reports/` 一眼可辨；新报告有明确归属落点
- ⚠️ 迁移面大：149 处引用 + 5 处工具/文档硬编码
- ⚠️ `glob` → `rglob` 改造若漏，会静默失明（§1.3）→ 必须配回归测试

### 3.4 Option D — 归档制（不推荐）

维持平铺 + 只把已闭环的老报告（60 份 Implemented 提案 + 20 份 3 个月前巡检）
移入 `reports/archive/`。❌ 反驳：Implemented 提案是**决策历史**，外部引用频次最高
（P65/P29/P22 各被引 2–3 次），移入归档反而**制造**引用变更；且未闭环提案与已闭环
提案同处一地才是真问题，分类解决不了「找不找得到当前有效的决策」。

---

## 4. Recommendation

**采用 Option C**，但**分两期**，且**期一必须先落地归属门禁**（它是本次事故的直接
止血，与布局解耦）：

- **S1（本次事故直接相关，先做）**：归属门禁 + 分类定义写进治理 + README 分类清单。
  零迁移、零引用变更。**即使后续 C 被否决，S1 仍独立有价值。**
- **S2（布局迁移）**：子目录分类 + 全量引用同步 + `glob`→`rglob` + 引用校验门禁。

**理由**：
1. **根因优先**：本次事故的真因是「无归属门禁」而非「无分类」（F1）。先堵 F1，
   即使 S2 延后也不再复发。
2. **Evolution Principle**：S1 是 Fix 级（补缺失校验），S2 是 Structural 级
   （改资产布局契约）。混在一起会让用户为一个紧急止血承担 149 处引用的迁移风险。
3. **风险可控**：S2 的最大风险是门禁静默失明（`glob` 假设平铺），单列为
   §5.2 的强制回归项 + §6 的验证项，不与 S1 捆绑。
4. **Minimal Change**：26 个单文件报告的归类本身有主观性（`CACHE-OPTIMIZATION`
   算 assessment 还是 incidents？），需要用户在看到清单后逐项确认，不宜由 AI 独断。

---

## 5. Proposed Changes（待批准实施）

### 5.1 S1 — 归属门禁 + 分类定义（Fix 级）

| # | 层 | 改动 | 备注 |
|---|---|---|---|
| 1 | `governance/policies/proposal-policy.md` §6 | 扩写 Reports Index Discipline：新增「**归属与分类**」小节 —— 定义 7 类（proposals / maintenance / assessments / incidents / migrations / analysis / skill-sources）、各类允许的命名模式、**业务产物禁止入 `reports/`**（应去 `outputs/<workflow>/` 或 `workspaces/<project>/`） | §6 现只有「登记」纪律，无「归属」纪律 |
| 2 | `tools/checks/proposal_audit`（`tools/proposal-audit.py` 或新 `tools/checks/reports_scope.py`） | 归属校验：`reports/` 下每个 `.md`/目录名须匹配某类别的命名模式；命中「业务产物模式」（如 `prepare-*` / `*-prepare-*` / 已知业务项目名）→ **ERROR** 并给出正确落点提示 | 复用 `proposal-audit` 既有扫描结果，避免第二次遍历 |
| 3 | `tools/checks/__init__.py` + `tools/check.py` docstring | 接入 check.py（新增第 16 项或并入第 11 项 proposal-audit） | 门禁须在 pre-commit 可见 |
| 4 | `reports/README.md` | 顶部新增「分类与归属」小节（7 类定义 + 落点判据 + 「本文件与 PROPOSALS.md 各自职责」）；既有分节标题与新分类对齐 | 消除 F3(a) 索引/布局脱节 |
| 5 | 测试 | `cli/tests/`：①业务产物命名 → ERROR；②各合法类别命名 → 放行；③`reports/` 顶层索引文件（README/PROPOSALS）豁免；④与 `test_real_repo_is_clean` 同款「真实仓库零 findings」断言 | 防门禁自身误报 |
| 6 | 文档 | `ai-system/README.md:73` 结构图补 reports 分类说明；`governance/AI_OPERATING_RULES.md` 落报告位置时补一句归属判据 | 与 §1.3 的 5 处硬耦合对齐 |

### 5.2 S2 — 布局迁移 + 引用同步（Structural 级）

| # | 层 | 改动 | 风险控制 |
|---|---|---|---|
| 7 | `tools/proposal-audit.py` | 4 处 `glob` → `rglob`（`:88` P 系列、`:141` open-item、`:168` 索引登记、`:192` refresh-index）+ `:295` 计数 | **强制回归项**：迁移后断言「扫到的 P 系列仍为 66 份」；另加「`rglob` 命中数 == `glob` 命中数（在平铺态）」的等价性测试，防止改造本身丢扫描 |
| 8 | `tools/maintain-report.py:26,210` | `REPORTS / "maintenance"`，目录 `mkdir(parents=True, exist_ok=True)` | 与 §5.2-7 同批 |
| 9 | `config/protected-paths.yaml` | `<repo>/reports` 保持整目录声明（子目录自动覆盖），**无需改**；仅在注释里补「含 7 个分类子目录」 | 确认无需改而非漏改 |
| 10 | 磁盘迁移 | `git mv` 124 文件 + 5 目录 → 7 子目录；**先出逐文件映射表交用户确认**（26 个单文件的归类有主观性） | 映射表是 P72 意义上的「清单确认」，逐条确认 |
| 11 | 引用同步 | 149 处 `reports/<file>.md` → `reports/<category>/<file>.md`；按被引文件批量替换（每目标文件一次 sed，避免漏改） | 迁移后 `path-audit` + 全量 grep 双向核对：0 悬空 |
| 12 | 新增引用门禁 | `tools/path-audit.py` 增判据：`reports/**` 内部的相对引用纳入 broken 检测（当前完全不管） | 根治 F4「移动无告警」 |
| 13 | 索引迁移 | `reports/README.md` 表格的文件列全部加目录前缀；`reports/PROPOSALS.md` 的 `refresh-index` 输出加前缀 | 与 §5.2-7 同批 |
| 14 | 测试 | 引用完整性回归：遍历全仓 `reports/...md` 引用断言目标存在（覆盖 §5.2-11 的 149 处） | 防后续再断 |

**明确非目标**：不改任何报告**内容**；不重命名 P 编号；不删报告；不迁 `reports/` 出仓库。

---

## 6. Validation Plan

**S1**：
1. 负例：造 `reports/prepare-foo-2608/x.md` → check.py 报 ERROR 并提示正确落点
2. 正例：现存 124 文件 + 5 目录全量扫描 → 0 error（真实仓库零 findings）
3. 门禁自检：`tools/check.py` PASS · 全量 CLI 单测 OK · pre-commit hook 可见
4. 治理一致性：`ai-system/README.md` 结构图与新分类一致

**S2**：
5. **门禁不失明（最高优先）**：迁移前后 `proposal-audit` 报告的「scanned 文件数」
   与「P 系列份数」**完全相等**（66）；`rglob`/`glob` 等价性测试通过
6. 引用零悬空：全仓 grep `reports/**/*.md` 引用 → 逐条断言目标存在（149 处）；
   `path-audit` 0 broken
7. 索引一致：`proposal-audit` 0 gate error / 0 warn（索引含目录前缀后仍匹配）
8. 单测 / check.py / repo-lint / extensions-lint / workflow-command-audit 全绿
9. 破坏性验证：迁移为纯 `git mv` + 文本替换，`git diff --stat` 应显示
   **100% rename + 引用行变更**，无内容行意外改动

---

## 7. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **`glob`→`rglob` 改造不彻底 → 门禁静默失明**（66 份提案对 Status/索引/open-item 三项校验全部失效且零告警） | §6-5 强制断言份数相等；§5.2-7 等价性测试；**S2 单独提交、单独验证，不与 S1 混批** |
| R2 | 149 处引用漏改 → 静默死链 | §5.2-11 按目标文件批量替换（非按模式盲替换）；§6-6 逐条断言；§5.2-12 新增门禁防复发 |
| R3 | 26 个单文件归类主观（`CACHE-OPTIMIZATION` 属 assessment 还是 incident？`DAILY-` 属哪类？） | §5.2-10 映射表**逐条交用户确认**，AI 不独断；允许用户指定新类 |
| R4 | 索引双份（README + PROPOSALS）迁移后不一致 | §5.2-13 与 §5.2-7 同批；`refresh-index` 为唯一权威生成源 |
| R5 | `reports/` 是 P72 受保护路径，批量移动触发 `protected_paths` 门禁 | 与 2026-09-28 BeeCount 删除同款流程：先出**完整映射清单** → 用户确认 → 执行 → 提交后门禁转绿（该门禁是事后检测，属设计意图） |
| R6 | 提案编号被外部引用，重命名会破坏下游 | **明确不重命名**（§2 非目标）；目录前缀对外部读者是增量信息 |
| R7 | 分类维度将来再次漂移（再造前缀） | S1-1 把类别定义写进治理文档并要求新增类别走变更管理；S1-2 门禁按定义校验（改定义须改门禁） |

---

## 8. 待裁定子决策（每条附建议）

| # | 决策点 | 选项 | 建议 |
|---|---|---|---|
| ① | 整体方案 | A 仅门禁 / B 命名规范 / **C 子目录** / D 归档 | **C 分两期**（S1 先做） |
| ② | 分类粒度 | 7 类（本文）/ 3 类（proposals·maintenance·other）/ 9 类（+ 更细） | 7 类（每类 ≥1 实存文件，无空类） |
| ③ | `analysis/` 与 `skill-sources/` 是否合并为 `multi-file/` | 合并 / 分列 | 分列（两类产出者不同：结构分析 vs skill 溯源） |
| ④ | `INCIDENT-*` 是否独立成类 | 独立 / 归 assessments | 独立（事故复盘有独立读者与响应流程，且已有 `INCIDENT-2026-09-24` 先例） |
| ⑤ | S2 迁移是否用 `git mv` 保留历史 | `git mv` / 删除重建 | `git mv`（保留 blame） |
| ⑥ | 是否同时补「引用完整性门禁」（§5.2-12） | 是 / 否（留待后续） | **是**（否则 F4 未根治，下次移动仍静默断链） |
| ⑦ | 归档已闭环提案（60 份 Implemented） | 本提案不做 / 另立 | 另立（与分类正交，且 Implemented 提案引用频次高，混在迁移里风险大） |

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| User | **Pending** | 需裁定 §8 七项子决策；建议先批 S1（独立有价值、零迁移风险），S2 待 S1 落地后另行授权 |
