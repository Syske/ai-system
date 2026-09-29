# Change Proposal: P71 — Experience Inbox（经验候选队列）+ 巡检确认提取

> **命名（用户 2026-09-29 追加裁定）**：`governance/memory/drafts/` 在语义上**不是**
> "memory 的草稿文件"，而是**未经审核的经验候选队列（Experience Inbox）**。
> 路径保留在 `governance/memory/` 下只为就近，但**读法必须按 Inbox**：
>
> ```text
> Experience
>     ↓
> Candidate
>     ↓
> Inbox                                    ← 未经审核，不可作为知识使用
>     ↓
> Triage
>     ├── Memory                （正典条目：英文 + 格式 + 索引）
>     ├── Standards             （本就是规则）
>     ├── Skill                 （本就是能力）
>     ├── Project Workspace     （单项目需求）
>     └── Discard               （+ 必须记录理由）
> ```
>
> **由此产生一条硬规则**（原「非正典、不得被引用」是软纪律，现升级）：
> **Agent 默认不得读 Inbox 当知识使用。** 见 §4.10。

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Structural（新增草稿区 `governance/memory/drafts/`（gitignored）+ 技能双路径 + 巡检沉淀 + 一处门禁豁免） |
| Author | AI Maintainer |
| Created | 2026-09-24 |
| Reference | 用户 2026-09-24 三次裁定：① 提出「日常会话不懂维护规则 → memory 单独存储 + 运维确认提取」② 落点定为 **`governance/memory/drafts/`**（否 `logs/memory/`）③ 草稿须**记清来源便于溯源**；本仓记忆机制侦察（§1） |
| Process | OPERATIONS §12 Change Management |

---

## 1. 现状核查（本仓实证）

**机制**：**AI 直写正典 + 索引强制 + 机器门禁**，**无暂存区**。

| 环节 | 现状 | 位置 |
|---|---|---|
| 写入者 | `skills/memory-capture/SKILL.md`：Step 4 直接写 `governance/memory/<category>/`，Step 5 追加 scope index，Step 6 报告 | 技能已指向同目录 `entry-format.md`（短模板） |
| 规则本体 | `governance/memory/MEMORY_GUIDELINES.md`（**833 行**）：条目模板（`## [Category] Title` + `Date/Priority/Context/Problem/Root Cause/Solution/Lesson/Scope/Related`）· **英文强制** · 归属边界（规则→standards、单项目需求→workspace、技能→skills、运行时→templates）· 资格四要件（Verified/Reusable/Experience/Non-duplicate） | 833 行，日常会话**不会读** |
| 机器兜底 | `tools/checks/memory.py`：`Lesson` 缺失=**error**；`Context/Problem/Solution/Scope` 缺失=warn；根索引必须纯索引且引用路径必须存在；**非索引文件出现 CJK=error**；Lesson 跨文件 Jaccard ≥0.8 告警 | 挂入 `check.py` 第 8 项 |
| 提交前拦截 | `tools/pre_commit_gate.py`：staged 记忆文件命中 CJK → **block 提交** | — |
| 生命周期 | `OPERATIONS.md §1.7`：`collect`（每次 release/retro）· `review`（**每月**：去重/查矛盾/查过期 + **扫描 `logs/` 中"重复 ≥2 次但从未入库"的观察** → triage 为 capture / machine-config / proposal，单次瞬时跳过）· `archive`（每季） | `aic-maintain.md` step 2.6 同款 |

**持久性事实（决定方案可行性）**：`.gitignore:26-27` 忽略 **`logs/`** 与 **`metrics/`**。
`logs/` 现存约 200 个会话/巡检文件，**全部不被 git 跟踪、不跨机器存活**。
**反差证据**：已入库的记忆 `governance/memory/java/coding-memory.md:192` 自己就引用了被忽略的
`ai-system/logs/env-maven-distmgmt-deploy-20260918-110006.md` —— 记忆已经在指向**非持久证据**。

## 2. 问题（哪些是真缺口，哪些不是）

| # | 缺口 | 实证 |
|---|---|---|
| **F2** | **写入不落库**：日常会话写完正典却**不提交** → 长期滞留工作区，随时可能丢 | 2026-09-23 实例：`java/coding-memory.md` 被另一会话写入后**未提交 1 天以上**（mtime 09-22 20:43），最终由本会话核实后代为落库（`a539a59`） |
| **F1** | **格式/语言摩擦**：833 行规则 + 英文强制，日常会话写得不对 → 事后修复 | 历史两次修复提交：`c404753`「java/integration.md 2026-09-16 追加块 8 处 CJK → 英文」· `4f26f14`「2026-09-18 会话中文段 → 英文（memory 必须英文门禁）」 |
| **F4** | **分层判断放错**：是否属"经验"（→memory）、"规则"（→standards）、"单项目需求"（→workspace） | 规则写在 `MEMORY_GUIDELINES` 的归属边界章节，但判断发生在**写入时**，而读 833 行的人几乎没有 |
| **F3** | **无前置查重**：只有事后 Jaccard ≥0.8 告警，没有写入前查重 | `memory.py` 相似度检查在 check 阶段 |
| 反例（**不是**缺口） | 2026-09-23 那条记忆**走的正是设计路径**（memory-capture 直写正典），格式与最近两条一致、内容经核实无误 | 故本提案**不推翻**直写能力，只补"低摩擦入口 + 提交纪律 + 分层前置" |

### 2.1 **核心论据：捕获机制在真实工作流中没有形成闭环**（2026-09-29 实测）

比「833 行指南没人读」更直接的证据 —— **拿一次真实的高经验密度会话测**：

| 观测 | 数值 |
|---|---|
| 2026-09-29 单日提交（`cd6f366..edd5feb`） | **14 个** |
| 期间明确产生的工程经验 | **至少 6 条**（逐条可指认） |
| 经 `memory-capture` 捕获流程进入 `governance/memory/` 的 | **0 条** |

这 6 条经验（均非一次性笔误，全部满足 `MEMORY_GUIDELINES` 的
Verified / Reusable / Experience / Non-duplicate）：

1. 门禁自证本身也会写错（`or ["*"]` 把门禁反转而非关闭）
2. 短路变异脚本本身也需要审查（锚点写错 ≠ 门禁失效）
3. 「负例失败」≠「该检查被覆盖」——冗余检查必须构造只有自己能报的场景
4. 无法失败的负例比没有负例更糟（报告了不存在的覆盖）
5. 门禁 bug 是「对文件格式的细节假设」而非逻辑错误（`re.M` / 权威源 / YAML 转义）
6. 分类门禁须用**白名单**而非排除法（`analysis-*` 既是类别也是 workflow 名）

**必须精确表述的一点**：当日 `governance/memory/` 确有 2 个提交改动
（`7de56c7` / `edd5feb`），但那 4 条 memory 条目是**门禁自证规范落地时顺带写的实证**，
属"做别的事时附带记录"，**不是捕获机制主动产出的**。按捕获路径计，产出为 **0**。

**这条证据的分量**：F1（指南太长）只是**可能**没人读；本表是**已经**发生且可量化的
失灵。§6 的 operational metric 就是为了持续监测这条曲线，而不是靠一次性论证。

## 3. 用户提案评估（`logs/memory/` + 运维确认提取）

**"确认提取"的精神与既有设计一致**：`OPERATIONS §1.7 review` 与 `aic-maintain` step 2.6 **本来就是**
"扫描 logs → 把重复 ≥2 次、从未入库的观察 triage 为 capture / machine-config / proposal"。
即"日常写原料、运维提取"**已是既定设计**。

**但 `logs/memory/` 这个落点有两处硬冲突**：

1. **`logs/` 被 gitignore** → 写进去的东西**不跨机器、不随 git 存活**，且语义上被当作可清理物
   （现有约 200 个文件）。把"待提取的记忆原料"放进**被声明为丢弃区**的目录，与"别丢经验"的初衷相反。
2. **提取时机依赖偶然性**：既有规则要求"**重复 ≥2 次**"才提取，且提取发生在巡检那一刻的机器上；
   单次但重要的教训（如 09-22 的 `@Autowired` 锚点事故）按现有规则**可能被跳过**。

**结论**：采纳其**思想**（低摩擦入口 + 运维确认），**改其落点**为**被 git 跟踪的候选暂存区**。

## 4. Options

### 4.1 Option A — 维持现状

代价：F1/F2/F4 继续；经验靠"会话自觉"和"重复 ≥2 次"两条不确定路径存活。**不推荐**。

### 4.2 Option B — 用户原案（`logs/memory/`）

优点：摩擦最低、与会话日志同处。**硬缺陷**：非持久（§3.1）、与"≥2× 才提取"叠加后单次重要教训仍可能丢。
若坚持，须明确接受"仅本机 + 仅到下次巡检"。**不推荐**（除非用户明确要"故意轻量、允许丢"）。

### 4.3 Option C — 被跟踪的候选暂存文件 `governance/memory/inbox.md`（**已被 §4.7 C″ 取代**）

```text
日常会话（默认路径）
  └─ 追加 1 行候选 → governance/memory/inbox.md        （tracked · 允许中文 · 无格式负担）
                        │
维护巡检（aic-maintain step 2.6 / OPERATIONS §1.7 review）
  └─ triage 每行：① 晋升到 governance/memory/<category>/（按正典契约，英文 + 索引）
                  ② 改写入 standards/ 或 skills/（本来就是规则/能力，不是经验）
                  ③ 写进 workspaces/<project_id>/（单项目需求）
                  ④ 丢弃（重复/瞬时/无价值）——并记录理由
  └─ 提取后删除该行（inbox 保持清空状态）
```

要点：
- **草稿层与正典层分离**：inbox **允许中文、只要 1 行**（低摩擦）；**正典仍强制英文 + 格式 + 索引**（纪律不减）。
- **前置分层**：候选行含 `proposed target`（memory / standards / skills / workspace），把"F4 判断"从写入时
  推到巡检时（那时有规则全文与历史可比）。
- **不再依赖"≥2 次重复"**：候选是显式沉淀，单次重要教训也能被 triage。
- **提交纪律**：memory-capture 明确"候选/正典都必须**独立提交**"（补 F2）。

### 4.4 Option D — 只加提交纪律与分层三问（最小改动，可与 C 并行）

不给新增文件：在 `memory-capture` 里加两处（① 结束必须提交 ② 写入前三问：规则？单项目需求？经验？）。
成本近零，但**不解决**"日常会话不想读 833 行、不想写英文"的摩擦。**建议作为 C 的一部分同时落**。

### 4.5 Option C′ — 草稿文件夹放在 `logs/memory/`（**已被 §4.7 C″ 取代：落点改回 governance/memory**）

用户修正：不要求日常会话提交；日常/周巡检时检查、**沉淀并提交**。

```text
日常会话（默认路径，零负担）
  └─ 写草稿文件 logs/memory/{yyyymmdd}-{session}.md
     （中文/任意格式/不提交/不需读 833 行指南/不需改索引）
                        │
周巡检（或日常巡检）—— aic-maintain step 2.6
  └─ 逐条 triage：① 蒸馏进 governance/memory/<category>/（英文 + 格式 + 索引）
                  ② 改投 standards/ 或 skills/（本来是规则/能力）
                  ③ 写进 workspaces/<project_id>/（单项目需求）
                  ④ 丢弃（重复/瞬时/无价值）——记理由
  └─ **提交沉淀结果**（提交的是蒸馏后的正典条目，不是草稿原文）
  └─ 删除已处理的草稿文件（草稿区保持清空）· 结果写进巡检报告
```

**为什么这次接受 `logs/` 落点（推翻 §3 的反对理由）**：§3.1 的反对前提是"草稿是**唯一记录**"——
一旦草稿丢失经验就没了。用户把"巡检**必须**沉淀并提交"补上后，**持久性由沉淀结果（tracked 正典 + 提交）
保证，草稿本身不再需要持久** → 反对前提消失。且原始素材同时存在于会话记录中，草稿只是低摩擦入口。

**关键差异（下表为 C′ 与 C 的取舍）**：

| 维度 | **C′ `logs/memory/`**（推荐） | C `governance/memory/drafts/` |
|---|---|---|
| 改动量 | **零 gitignore 改动**（`logs/` 已忽略，子目录自动继承）· **零门禁改动**（`memory.py` 只遍历 `governance/memory/**`，不碰 logs） | 需 +1 条 `.gitignore` + `checks/memory.py` 显式跳过 drafts（它是 `rglob` 遍历，gitignore 挡不住，否则草稿写中文会被 `check.py` 判 **error**）+ 1 条单测 |
| 语义 | 略弱：`logs/` 是"可清理区" | 更清晰：草稿 ≠ 丢弃区 |
| 持久性（沉淀前） | 不跨机器（可接受：见上） | 同样不跨机器（草稿若 tracked 则进历史噪音） |
| 发现性 | 固定子目录 `logs/memory/`，不在 200 个日志里翻找 | 固定 |

**C′ 必须配的三条护栏（缺一即退化为垃圾堆/丢经验）**：
1. **每次巡检都沉淀**（不是每月）—— 挂在周巡检（`next_maintenance` 已是 weekly）+ 日常巡检顺带；
   `OPERATIONS §1.7` 的月度 review 仍只管"去重/查矛盾/查过期"，两者不混。
2. **沉淀后必须提交 + 必须删草稿**；陈旧草稿（超过 1 个巡检周期未处理）→ WARN。
3. **草稿区不得被引用**：明文声明"草稿层非正典"；任何规则/技能/报告不得引用 `logs/memory/` 路径
   （否则重演 §1 的"记忆引用被忽略的 logs 证据"问题）。
4. `logs/` 的常规清理/归档必须**排除** `logs/memory/`（在巡检说明中写明，避免被顺手清掉）。

### 4.6 中间结论（历史）：A 维持现状 / B 原案无沉淀保证 / C′（曾推荐）—— **最终裁定见 §4.7**

### 4.7 **最终裁定：C″ —— 草稿区 `governance/memory/drafts/` + 巡检必沉淀必提交 + 草稿记清来源**（用户 2026-09-24）

```text
Experience（会话中遇到的经验）
    ↓
Candidate（判断够格 → 写成候选；不够格则不写，「无候选」是合法结果）
    ↓
Inbox —— governance/memory/drafts/{yyyymmdd}-{session|topic}.md
        最低结构 5 字段（可中文、不要求正典格式、不读 833 行指南、不改索引、不提交）
        ⚠ 未审核：**Agent 不得读 Inbox 当知识使用**（§4.10 硬规则）
                        ↓
周巡检 / 日常巡检 —— aic-maintain step 2.6
  └─ 逐条 triage（**先用 Source 核验真伪**，再查重）：
       ⓪ **若候选非英文，在此完成语言转换**（Capture 层不限语言；**转换责任在
          triage，不在 Capture** —— 见下方「语言分层」）
       ① 蒸馏进 governance/memory/<category>/（英文 + 格式 + 索引）  → Memory
       ② 改投 standards/                                            → Standards
       ③ 改投 skills/                                                → Skill
       ④ 写进 workspaces/<project_id>/                               → Project Workspace
       ⑤ 丢弃（重复/瞬时/无价值）—— **必须记录理由**                → Discard
  └─ **提交沉淀结果**（提交的是蒸馏后的正典，不是 Inbox 原文）
  └─ 删除已处理候选 · 结果写进巡检报告
```

**注意 Inbox 的四类去向里只有一类是 Memory** ——这正是它不叫「memory 草稿」的原因：
多数候选最终**不是**记忆（是规则、是能力、是单项目需求、是垃圾）。

**候选条目：最低结构 5 字段（可中文；行数不限）**：

```text
Candidate: <一句话：学到什么>
What:  <发生了什么 / 结论是什么>
Why:   <为什么值得沉淀 —— 下一个任务或另一个服务会不会再遇到>
Source: <会话/日期> · <项目或仓库> · <触发: 事故 / 评审发现 / 复盘 / 用户要求>
        <证据: commit sha / file:line / 命令与输出摘要>
        <若只存在于本机日志 → 标 [机器本地]>
Candidate Category: memory(<category>) | standards | skill | workspace(<project>) | discard
```

**行数不设上限**（用户 2026-09-29 追加裁定：原文的「4~6 行」是**误设的硬限制**）。
理由：把「4~6 行」当约束会诱发**为压行数而丢上下文**——而 `Why` 与 `Source` 恰恰
是 triage 时最不可省的部分（前者决定值不值得沉淀，后者决定能不能核验）。
**优先保证来源与事实完整性，而不是行数。** 3 行可以，8 行也可以。

**5 个字段全部必填**（不是「建议包含」）：缺 `Source` 则无法核验真伪，缺
`Candidate Category` 则 triage 无从下手，缺 `Why` 则无法判断是否够格。
字段**可以换行展开**（如上 `Source` 示例）。

**为什么要求来源**：① 巡检 poter 核验真伪（避免把"应该是 X"沉淀成记忆）② 去重时可比对来源
③ 事后审计能回答"这条记忆从哪来" ④ 显式区分**持久证据**（commit sha、业务仓 file:line）与
**机器本地证据**（`logs/**`），避免重演 §1 记录的既有缺陷（`java/coding-memory.md:192` 引用了被 gitignore 的 logs）。

**与 C′ 的差异（两处小改动）**：

| 维度 | C′（曾推荐，`logs/memory/`） | **C″（最终，`governance/memory/drafts/`）** |
|---|---|---|
| 语义 | 落在被声明为可清理的日志区 | **草稿紧挨正典**，路径自解释 |
| 清理风险 | `logs/` 的常规清理/归档可能顺手删掉 | 不在日志清理范围内 |
| gitignore | 无需改动（`logs/` 已忽略） | **+1 行**：忽略 `governance/memory/drafts/`（草稿不进 git、不产生 `??` 噪音、避免被 `git add -A` 误提交） |
| 门禁 | 无需改动（`memory.py` 不遍历 logs） | **+1 处豁免**：`checks/memory.py` 是 `rglob("governance/memory/**")`，**gitignore 挡不住它** → 草稿写中文会被 `check.py` 判 error，故须显式跳过 `drafts/`（+1 条单测） |
| 持久性 | 由沉淀结果保证 | 同（草稿自身不持久：gitignored 即本机工作区） |

**持久性精确边界（重要，防误读为「草稿不丢」）**：

| 内容 | 是否保证不丢 | 依赖什么 |
|---|---|---|
| 已沉积的**正典条目**（英文 + 格式 + 索引） | ✅ 不丢 —— tracked + 提交，可跨机器、可从远端恢复 | **巡检必须沉淀并提交**（本提案的不变量） |
| 草稿**原文**（`governance/memory/drafts/`，gitignored） | ❌ **不保证** —— 只存在于本机工作区：机器故障/重装/`git clean -fdx`/误删即丢 | 仅保证「自上次巡检起的窗口内」不丢 |
| 草稿里的**来源与要点** | ✅ 沉淀后不丢（写进正典的 Context / 来源字段） | 若某条草稿未沉淀即丢失，则连来源一起丢 |

**暴露窗口** = 自上次巡检起（周巡检 → 最多 7 天；日常巡检触发则更短）。
**没有任何未提交的内容可以保证不丢** —— 能保证的只有「提交过的东西」。若要连草稿原文也不丢，
见 §4.9。

**语言分层（2026-09-29 追加，源自 P77 §10 的 Multilingual 讨论）**：

```text
Capture 层（Inbox）    ── 不限语言，中文候选原样沉淀
        ↓
Triage 层             ── **在此完成语言转换**（Capture 不承担翻译）
        ↓
Canonical 层（正典）  ── 仍强制英文（MEMORY_GUIDELINES + pre_commit_gate 阻断 CJK）
```

**为什么必须显式分层**：本提案同时要求「Inbox 可中文（低摩擦）」与「正典强制英文」，
但**从未规定转换发生在哪一步**——triage 描述里只有「蒸馏进正典（英文）」这一句结果性
表述，过程缺位。分层后责任唯一：**triage 转换，Capture 不翻译**。

这不是取舍（Capture 要中文 **且** 正典要英文，两者不冲突），而是**把已有但未言明的
责任归属写死**。同一分层在 Hindsight 的 multilingual 设计中亦被独立得出
（capture 保留原语言，canonical 层语言另定）——见 `reports/P77-HINDSIGHT-EVALUATION.md` §10.4-③。

**四条护栏（缺一即退化）**：① 每次巡检都沉淀（挂周巡检 + 日常巡检；月度 review 仍只管去重/查矛盾/查过期）
② 沉淀后**必须提交 + 必须删草稿**（陈旧草稿 WARN 先不做）③ **Inbox 硬规则**（§4.10）：Agent 不得读 Inbox 当知识使用；任何规则/技能/报告不得引用其路径
④ 目录存在性：gitignored 目录不入库，故**草稿由会话按需 `mkdir -p` 创建**（空目录 git 不跟踪），
路径约定写在 `MEMORY_GUIDELINES` 与 `memory-capture` 技能里（两处均为 tracked 文档）。

### 4.8 **场景集成：把 memory 捕获挂到写代码的 runtime**（用户 2026-09-24 追加）

**现状缺口（实测）**：`runtime-develop.md` / `runtime-review.md` / `runtime-bugfix.md` 对
memory|capture|lesson 的命中数**全为 0** —— 三个真正产生工程经验的阶段**没有任何捕获挂钩**；
`memory-capture` 的触发器只有「会话结束 / 困难调试后 / 用户明示 / release·复盘后」，全靠 agent 自觉。
（本会话 50+ 提交的实现工作即为例证：develop 类工作做了很多，**零**经验沉淀。）
`config/main-chain-capabilities.yaml` 的 `capabilities.{develop,review,verify}` **均为空**；
`knowledge` 是独立 workflow（`config/workflow-registry.yaml:16`），不会被 develop/review/bugfix 触发。

**设计**：三个阶段收尾各加一条「经验候选」指令（英文，Rule 4 英文区），指向既有技能与资格规则：

| 阶段 | 触发条件（不满足则不写） | 落点 |
|---|---|---|
| **develop** | 实现中出现**编译期不可见且可复用**的教训（如静默语义漂移、注入/映射/时序类坑；本仓实例：`@Autowired` 锚点事故） | Completion 之后，写草稿 |
| **review** | 发现**新的缺陷类**（不是一次性笔误），且能给出判定证据（`file:line`） | review 报告之后，写草稿（**不碰业务代码**——草稿在 ai-system，与 review 的「不得改业务实现」不冲突） |
| **bugfix** | 根因属**易复发的坑**（同一类问题可能在别处重演），且修复已验证 | 修复收尾，写草稿（bugfix 的「不做无关改动」只约束业务仓，不约束 ai-system 草稿） |

**防草稿泛滥的资格门槛（复用既有规则，不复制）**：以 `MEMORY_GUIDELINES` 的
「What Qualifies：Verified / Reusable / Experience / Non-duplicate」为准，**并显式要求**
「另一个服务或下一个任务也会遇到」——否则**不写**；**「本次无候选」是合法且常见的结果**
（必须在会话小结里明确说"无经验候选"，与"忘了写"区分）。

**为什么与草稿区是一体**：草稿区让「多收集样本」变便宜（低摩擦、可中文、不提交、不读 833 行），
而**沉淀环节**保证正典不被稀释 —— 二者缺一就会退化成"要么不敢写、要么写烂正典"。

**注册表是否一并登记**：**不登记**（Minimal Change）。`capabilities.*` 的语义是「阶段**可选**外部能力
注入」，而本捕获是核心流程；触发器写在 runtime（SSOT），资格与格式写在 `MEMORY_GUIDELINES` + 技能，
三处各司其职，不产生第二声明。若日后需要 prompt 自动注入再评估。

### 4.9 （可选）持久性等级 L3：草稿原文也不丢

若要求**草稿原文也不丢**，唯一可行做法是把 `drafts/` 变为 **tracked 并由巡检归档提交**：
代价 = ① 草稿进入 git 历史（噪音）② **两处**门禁豁免（`checks/memory.py` 跳过 + `pre_commit_gate`
放行 drafts 的 CJK）③ 需设计「提交后归档而非删除」的路径（否则提交即删无意义）。
**建议不做**：草稿的原始素材在会话记录与本机日志中另有一份，且要点与来源会随沉淀进入正典；
只有"未沉淀即丢失"这一周窗口内的原文会损失。**待用户裁定**。

## 4.10 **硬规则：Inbox 不是知识，Agent 不得读它当知识使用**

（用户 2026-09-29 追加裁定，把原「非正典、不得被引用」的**软纪律升级为硬规则**）

### 规则

> **Agent 默认不得把 `governance/memory/drafts/`（Inbox）的内容作为知识依据。**

具体地，**禁止**：

| 禁止的行为 | 反例形态 |
|---|---|
| 在回答中引用 Inbox 内容作为事实依据 | 「根据经验候选 X，……」（而 X 未经审核） |
| 在规则/技能/报告/正典条目中链接或引用 Inbox 路径 | `` 见 `governance/memory/drafts/20260929-foo.md` `` |
| 把 Inbox 内容当作「已验证的经验」推理 | 用未核验的候选去支持一个技术判断 |
| 把 Inbox 路径写进任何 tracked 资产 | 索引、脚本文档、ADR、报告 |
| 在 memory 门禁豁免的名义下扩大豁免范围 | 往 Inbox 塞「其实想长期保留」的内容 |

**允许**（且仅限）：

| 允许的行为 | 条件 |
|---|---|
| 写入候选 | 会话结束时 |
| **triage 时读取** | 仅巡检角色（`aic-maintain` step 2.6） |
| triage 后删除 | 沉淀完成即删 |
| 报告「Inbox 现有 N 条待 triage」 | 巡检报告 |

### 为什么必须升级为硬规则

**最危险的误区**是：一旦它被叫「memory 的草稿」，Agent 会自然推断「memory 我可以读」——
于是把**未经审核、甚至有假证据**的候选当知识使用。提案 §4.7 的来源字段设计正是为了
让 triage 能**拒绝**假证据；但若候选在 triage 前就被当作知识引用，核验机制形同虚设。

**路径仍在 `governance/memory/` 下**（就近），这是唯一的妥协点——因此**命名与文档必须
明确它不是 memory 的草稿**，否则路径本身就在持续误导。§5-7 的草稿层声明必须以本节的
措辞书写，不得弱化为「建议不要」。

### 与既有设计的一致性

本规则不新增机制，只把三处既有约定**合并升格**：

- §5-3 门禁豁免只针对 `drafts/` 目录（永久内容不得进 Inbox）
- §5-4 技能双路径（直写正典仍可用，且**那才是** Agent 可读的知识路径）
- `MEMORY_GUIDELINES.md` 的归属边界（判断在 triage 时做，不在写入时）

---

## 5. Proposed Changes（Option C″ + D）

| # | 改动 | 落点 | 规模 |
|---|---|---|---|
| 1 | **Inbox 约定**：`governance/memory/drafts/{yyyymmdd}-{session\|topic}.md`（语义 = **Experience Inbox**，非 memory 草稿），每条含 §4.7 的**最低结构 5 字段**（`Candidate` / `What` / `Why` / `Source` / `Candidate Category`，全必填，**行数不限**）；中文/任意格式/**不提交**；会话按需 `mkdir -p` | 约定写入 `MEMORY_GUIDELINES` 与技能（tracked 文档） | 极小 |
| 2 | **gitignore**：忽略 `governance/memory/drafts/`（草稿不进 git，避免 `??` 噪音与 `git add -A` 误提交） | `.gitignore` +1 行 | 极小 |
| 3 | **门禁豁免**：`checks/memory.py` 跳过 `drafts/`（因它是 `rglob` 遍历，gitignore 挡不住；否则草稿中文 → error） | `tools/checks/memory.py` + 1 条单测 | 小 |
| 4 | 技能双路径：**默认写草稿**（零负担、含来源）；会话确定且能合规、或用户要求立即沉淀时仍可直写正典；二者都不要求会话提交 | `skills/memory-capture/SKILL.md`（+5~6 行） | 小 |
| 5 | 巡检沉淀：读 `drafts/*.md` → 用来源核验 → triage（正典 / 改投 standards·skills / workspace / 丢弃）→ **提交沉淀结果** → 删草稿 → 记报告 | `cli/commands/aic-maintain.md` step 2.6（**当前 99 行，需重写措辞守住 100 行薄命令门禁**） | 中 |
| 6 | 节奏与职责划分：沉淀挂周巡检/日常巡检；月度 review 仍只管去重/矛盾/过期 | `OPERATIONS.md §1.7`（+2~3 行） | 小 |
| 7 | **Inbox 硬规则声明**：以 §4.10 的措辞写入（**Agent 不得读 Inbox 当知识使用**；禁止行为 5 条 / 允许行为 4 条；5 字段必填且行数不限；巡检后清空） | `governance/memory/MEMORY_GUIDELINES.md` 一节（~20 行） | 小 |
| 8 | **场景集成**：develop / review / bugfix 三个 runtime 收尾各加一条「经验候选」指令（英文；含资格门槛与「无候选是合法结果」） | `templates/runtime/runtime-{develop,review,bugfix}.md`（各 +3~4 行） | 小 |
| 9 | （可选）陈旧草稿 WARN（>1 个巡检周期未处理）→ **先不做**，等真实需要 | — | 待定 |
| 9b | **Operational Metric 记录**：每次巡检在报告与 `config/maintenance.yaml` 记录 §5.9 的五项计数（含逐条 discard 理由） | `cli/commands/aic-maintain.md` step 2.6（与 #5 同处改，注意 100 行）+ `aic-maintain` Outputs 段 | 小 |
| 10 | （可选，**待裁定**）L3 草稿原文不丢：drafts 改 tracked + 巡检归档提交 | `.gitignore` · `checks/memory.py` · `pre_commit_gate` · 巡检步骤 | 中 |

**成本**：**零新增 tracked 文件**（草稿区 gitignored；空目录不入库）· gitignore +1 行 · 门禁豁免 1 处 + 1 单测 ·
**8 处文档/技能/runtime 小改（约 50 行）** · 无新工具/命令 · 固定 token 成本 **0**
（草稿不在任何提示词路径上；runtime 三处各 +3~4 行随该阶段提示词加载）。

## 5.8 **路线图与优先级**（用户 2026-09-29 定）

```text
现在
 │
 ├─ P71 C″（本提案）
 │    ├─ 低摩擦 Experience Inbox
 │    ├─ Triage（去 Memory / Standards / Skill / Workspace / Discard+理由）
 │    ├─ Source verification（先核验再沉淀）
 │    ├─ Persistence / commit discipline（沉淀必提交，草稿必删）
 │    └─ Runtime 收尾候选入口（develop / review / bugfix）
 │
 ↓
观察一段时间（用 §5.9 的五项计数 + 四个派生指标）
 │
 ├─ 候选产生率   —— 入口是否真被用
 ├─ 沉淀率       —— triage 是否真做筛选
 ├─ 丢弃率       —— 资格门槛 / 来源核验是否失效
 └─ 积压         —— 巡检是否跟上
    （**不含**「复用率」—— 已裁定 v1 不解决，见 §5.9-未）
 │
 ↓
若 **Canonical Memory 稳定增长**
 │
 ↓
再评估 **Hindsight**
 │
 └─ Hindsight 负责 **Recall / Reflect**，
    **不负责 Governance / Triage**
```

**优先级判定**：

| 项 | 评分 | 处置 |
|---|---|---|
| **P71 C″** | **9 / 10** | **应该落地** —— 缺口有实证（§2.1 捕获 0 条）、方案已裁定、成本低 |
| **Hindsight** | **7.5 / 10** | **保留为下一阶段 PoC** —— 有价值，但**依赖 P71 先跑出数据**：没有稳定增长的正典，Recall/Reflect 无对象 |

**职责边界必须写死**：Hindsight 做 Recall / Reflect；Governance / Triage 仍归 P71
的巡检流程。理由：把「审核与晋升」外包给检索层，等于让**未审核内容**借 Recall
通道重新进入知识面——正是 §4.10 硬规则要防的事。

**触发下一阶段的前置条件**（缺一不动 Hindsight）：

| # | 条件 | 状态 |
|---|---|---|
| ① | 连续 ≥4 次巡检记录了完整的 §5.9 五项计数（证明 metric 可持续采集） | 本提案 §5.9 |
| ② | 正典条目周累计稳定增长 | 本提案 §5.9 |
| ③ | 至少 1 条正典条目在真实任务中被实际复用，且该事实被**人工记录**（非计数 —— §5.9 已裁定不建引用计数） | 本提案 §5.9 |
| ④ | **「普通检索够不够」的前置验证结论为「不够」** | **`reports/P77-HINDSIGHT-EVALUATION.md` §6（2026-09-29 追加）** |

> **④ 必须在 ①②③ 之后**，因为「检索够不够」的答案**依赖正典规模** —— 19 条时普通
> grep 很可能已经够用，此时做验证会得出「Hindsight 无价值」的**错误结论**；规模翻倍
> 后答案可能相反。**不得在当前规模下验证并据此下结论。**

---

## 5.9 **Operational Metric —— 验收靠指标，不靠「目录空不空」**

（用户 2026-09-29 追加裁定）

P71 有大量结构性检查，但最终要证明的是**它真的降低了经验沉淀摩擦**。而
「`drafts/` 是否为空」**不是有效指标**：

| `drafts/` = 0 的两种含义 | 后果 |
|---|---|
| ① 所有经验都成功沉淀了 | 理想 |
| ② **Agent 根本没产生候选** | 失败，但指标看不出来 |

§2.1 已实测第 ② 种确实存在（14 提交 / 6 条经验 / 捕获 0 条）——**而这两种情况在
`drafts/ = 0` 这个观测下完全无法区分**。故必须改用可区分的计数指标。

### 每次巡检必须记录的五项

```text
Experience Inbox — <日期>
  Candidates generated:   N      ← 本期新增候选数（入口是否真的被用）
  Candidates triaged:     N      ← 本期处理数（入口是否积压）
  Canonical memories created: N  ← 去向 ①（正典）
  Redirected: standards N / skills N / workspaces N   ← 去向 ②③④
  Discarded:             N      ← 去向 ⑤
  Discard reasons:       <逐条一行，不允许只给总数>
```

**示例（一次巡检）**：

```text
Candidates: 7 → Memory: 2 · Standards: 1 · Skill: 0 · Project: 1 · Discard: 3
Discard reasons:
  - gate 自证反转实例 → 与 policies/quality-gates.md §Rule 2 重复（规则已在，不重复沉淀）
  - 一次性 CLI 传参笔误 → 不满足 Reusable
  - 路径大小写差异 → 属本次改动细节，已在该 commit 说明
```

### 派生指标（观察期用）

| 指标 | 定义 | 读法 |
|---|---|---|
| **入口是否被用** | `generated` 与 `triaged` **配对**读绝对值 | `0 / 0` → 没发生任何事；`0 / >0` → 上一轮已全部消化（正常） |
| **运行捕获率（下界）** | `generated` / instrumented 运行数（develop+review+bugfix，分母采集见上节） | 持续为 0 → **入口确定未被使用**（严格结论）；> 0 → 捕获发生了但不可量化 |
| **沉淀率** | Canonical created / Candidates triaged | 过高（≈100%）→ triage 走过场，未真做筛选 |
| **丢弃率** | Discarded / Candidates triaged | 过高 → 资格门槛或来源核验失效，Inbox 成了垃圾堆 |
| **积压** | Candidates generated − Candidates triaged | 持续为正 → 巡检没跟上 |
| **正典增长** | Canonical memories created 的周累计 | **最终目标曲线**：稳定增长才说明闭环成立 |
| **discard 理由多样性** | 相同 discard 理由的条目数 / 丢弃总数 | 高占比 → 理由可能是**批量编造**的。「逐条一行」是格式要求，拦不住 N 条完全相同的合理措辞 |

### 运行捕获率（下界）—— 分母的采集与落库（用户 2026-09-29 裁定）

原「候选产生率」（分母 = 有经验密度的会话数）因分母不可得而于本日删除，随后
**恢复为下界形式**。恢复的依据来自实测：`<workspace>/logs/` 中 develop / review /
bugfix 三类**每次运行都留有诊断日志**（实测 22 份），而这三类正是加了
`## Experience Candidates` 的三个 runtime —— 仪器化范围与日志范围精确对应。

| 项 | 值 |
|---|---|
| 定义 | `Candidates generated` / **instrumented 运行数**（develop + review + bugfix） |
| 性质 | **真实捕获率的下界** —— 分母含无经验的运行，故 ≤ 真实值 |
| 读法 | 下界持续为 0 → **入口确定未被使用**（严格结论）；下界 > 0 → 捕获发生了，但不可量化该多频繁 |
| 按类型 | 18 develop : 2 review : 2 bugfix，**按 workflow 类型分读**；合并读会掩盖 review 路径的空白 |

#### 采集与落库：三条强制约束

**① 不得实时读 `logs/`。** `logs/` 曾被误删 —— `reports/INCIDENT-2026-09-24-ignored-state-wipe.md`
记录 repo 内 gitignored 目录被清空，**约 200 份运行日志全毁**。分母必须在**巡检时
落库**为累积值，而不是在分析时回查 `logs/`。回查等于把刚建立的观测重新挂在已被证明
不可靠的存储上。

**② 落库按机器隔离。** `<workspace>/metrics/` 现有快照命名 `maintain-<date>.json`
**无机器维度** —— 两台机器同日巡检会**互相覆盖**（实测该命名已如此）。故分母落点为：

```text
<workspace>/metrics/by-machine/<machine-id>/knowledge-runs.jsonl
```

以机器目录为隔离单元，同名文件不可能碰撞。当前仓内**无现成机器标识**
（`grep machine_id/hostname` 零命中），故 `<machine-id>` 取 hostname 派生值 ——
记一条已知局限：hostname 变更会造成分母断档（表现为该机读取数骤降为 0），
届时需人工重置 watermark。

**③ 追加式 + watermark，且必须可审计。** 因 `logs/` 可能被清空，计数是**累积**的：

```jsonl
{"ts":"2026-09-28T00:00:00","watermark":"20260929-165225","develop":6,"review":1,"bugfix":0,"files":["develop-20260929-144455.md","..."]}
```

- **watermark** = 本次计入的最后一条日志时间戳，防止重复计数
- **files** = 本次计入的日志文件名**全量留存**。计数本身不可信 —— 要求同时记下
  被数的文件，才能事后核对「数的是什么」。理由与「discard 理由多样性」同源：
  **只记结论不记依据的数字无法被质疑。**

**④ 分子也要带机器标识。** 捕获发生在开发机、triage 发生在巡检机，两者常常不同机。
五项计数的记录中须带 `machine` 字段，否则跨机比率的分子分母会错配。

#### 与「不新建指标文件」的关系

P71 §5.9 原写「不新建指标文件（避免又一处需要维护的状态源）」。本次落点**遵守**该
约定：`metrics/` 已是既有机器层指标区，**不新增指标区**，只在其中增设一个
per-machine 子目录。代价是多一个采集步骤（巡检时数一次日志文件名）。

#### 未决：review / bugfix 路径样本可能不足

实测 18 : 2 : 2。若观察期主要走 develop，review / bugfix 的候选质量**将无样本**，
而 P77 的结论建立在三类的合并读上。**这比指标形式更影响结论** —— 记在案，
观察期内须分类型记录，出现长期空白须在 P77 复核时说明。

---

### 观察期的读法口径（2026-09-29 修正）

**只看方向，不看水平。** 上表的「读法」列全部是**失效方向**（过高 / 过低 / 长期为
零 / 持续为正），**没有目标带**。这是刻意的：

分子分母**同源** —— 捕获是 AI，triage 也是 AI，Source 核验还是 AI 做的。**沉淀率
衡量的是「AI triage AI 的捕获」**，唯一的独立防线已经被同源抵消。

后果是：一个产出垃圾、且一致地处理垃圾的闭环，能得到全部「健康」读数 —— 沉淀率落在
60%（不触发「过高」），丢弃率 30% 且每条理由都写得合理（不触发「理由多样性」）。
**因此任何单一比例落在中间区间时都不可判定为健康。** 观察期内**不给目标带**，四周
后再根据实际分布决定是否需要；那时有了真实数据，带子才是有依据的。

**「候选产生率」已删除**（2026-09-29）。原因：分母「期间有经验密度的会话数」
**无采集机制**，且它与「捕获经验」是同一 AI 的同一判断 —— 用被测系统的输出去算分母。
唯一可数的替代是 `logs/` 的运行记录，但那是**特定运行的诊断记录**（非每次会话都有）
且位于机器本地，是更弱的代理。

**删掉它是安全的**：该率原本要解决的是 §2.1 的「`drafts/` 为空无法区分『全部沉淀』与
『Agent 根本没产生候选』」，而**五项计数的配对读已经解决了这个问题** ——
`generated=0 且 triaged=0` 与 `generated=0 且 triaged>0` 天然可区分。率的引入没有
解决问题，只引入了不可算的分母。

### 落点

写入**巡检报告**（`reports/MAINTENANCE-<date>.md` 的巡检发现节）+ 追加一行到
`config/maintenance.yaml` 的 `last_findings`（供跨会话对比趋势）。

**不新建指标文件**（避免又一处需要维护的状态源）；`drafts/` 是否清空仍作为
**必要但不充分**的检查保留。

### 已知缺口 · v1 不解决：正典引用计数（用户 2026-09-29 裁定）

「正典是否真被用」这个数据**不采集**。裁定为 **v1 不解决**：不独立立项、不在
观察期实施、不修改 `MEMORY_GUIDELINES` 的 Load 规则。

**「不解决」的语义是「不值得」，不是「不需要」**：不是正典有没有被用不重要，
而是当前系统不值得为这个指标改变 Memory 的**读取语义**。「不值得」可被后续
证据推翻，「不需要」不可 —— 这个区别决定了它未来可以被重新评估。

三条理由（完整论证见 `reports/P77-HINDSIGHT-EVALUATION.md` §12）：

1. **它不是一个小指标。** 引用计数会展开成 usage telemetry system：read event →
   计数更新 → 持久化 → 去重/并发/失败重试 → 统计 → 才谈得上指标意义。而 P71 的
   目标是「经验产生 → 候选落地 → 正确分层 → 正典持久化」。
2. **read count 是粗 proxy。** `read count ≠ useful`；且 `read count = 0` 更可能
   说明**召回机制不好**而非知识无价值 —— 把它记成「无价值」会导向删掉那些
   「读不到」的 Memory，而它们恰是召回层最该修好的对象。未来若做，优先路径是
   `recalled → used → task outcome`，而不是「读即计数」。
3. **危险 KPI。** 一旦「复用率」成为指标，反向激励会把系统推向
   「为提高使用率而被迫加载大量 Memory」，与 `CONTEXT_LOADING.md` 的预算纪律
   正面冲突 —— 指标会把系统推向它本该避免的行为。

**因此显式禁止**把下列三项写入观察期指标：Memory read count · Memory reference
count · Memory utilization %。

未来若出现明确的 Memory 价值评估需求，可重新立项，起点应为 §12.4 的「有效使用」
链路，而非引用计数。

---

## 6. Validation Plan

1. **门禁不破**：`check.py`（含 memory 第 8 项）· `pre_commit_gate`（staged CJK 记忆）· `repo-lint` 全绿；
   `drafts/` 豁免后**正典检查强度不变**（反证：故意缺 `Lesson` 的正典仍须 error；故意在正典写中文仍须 error）。
2. **端到端一次 + 指标核对**：模拟日常会话写 2 条候选（1 条中文经验、1 条其实是「规则」）→
   跑巡检 step 2.6 → 验证 ① 经验条晋升为正典（英文 + 索引已更新）②「规则」条被改投 standards
   ③ Inbox 清空 ④ **Source 字段能被核验**（故意写一条假证据 → 巡检须拒绝沉淀）
   ⑤ **§5.9 五项计数与实际一致**（generated=2 / triaged=2 / memory=1 / standards=1 / discard=0，
   且 discard 逐条理由非空当 discard>0）。
   **关键反证**：另跑一次「本轮无候选」的巡检 → 必须记录 `generated: 0`，
   **不得**把它记成「全部成功沉淀」（§5.9 表格第 ② 种失败）。
3. **摩擦对比**：完成一次 capture 所需的**读写文件数**：现状（读 833 行指南 + 写正典 + 改索引 + 提交）
   vs 新路径（写 5 行草稿、**不提交**）。
4. **不退化**：直写正典路径仍可用（用一次真实捕获验证）。
5. **场景集成有效**：跑一次 develop（或 review/bugfix）任务收尾 → 验证 ① 满足资格者写进 Inbox
   ② 不满足者明确报告「无经验候选」（两个方向都要测，防"为交差硬写"）③ Source 字段可核验。
6. **硬规则可判定**（§4.10）：造一份 Inbox 候选后跑一次常规 develop/bugfix 会话 → 验证
   **prompt 与产物中不出现该候选内容**；再跑巡检 → 验证 **triage 角色能读到**它。
   （两个方向都要测：只测「不被引用」会漏掉「triage 读不到」这个反向失效。）
7. **长候选不被压扁**：写一条 10+ 行、`Why` 与 `Source` 完整的候选 → 验证巡检核验时
   信息完整、triage 结论不因行数而失真（反向：不得出现「因超行数而跳过核验」）。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| `drafts/` 变成**垃圾堆**（只进不出） | 巡检每次清空；不设"永久参考区"；（可选）陈旧草稿 WARN |
| 与正典出现**两套记忆** | §4.10 硬规则：Agent 不得读 Inbox 当知识使用；沉淀即删；索引不列它 |
| **Agent 把 Inbox 当知识读取**（误认为「memory 草稿」） | §4.10 硬规则（禁止行为 5 条 / 允许行为仅限写入与 triage）；`MEMORY_GUIDELINES` 与技能两处均须以硬规则措辞书写，不得弱化为「建议」 |
| **为压行数而丢上下文** | 行数不限；5 字段必填；`Why` 与 `Source` 是 triage 最不可省的部分 |
| 巡检负担增加 | 草稿是结构化小文件（比扫 200 个 logs 更快）；可与既有 logs 扫描合并成一次 |
| 门禁豁免被滥用（往 `drafts/` 塞永久内容） | 豁免只针对 `drafts/` 目录；巡检每次清空；正典检查强度不变（已列反证） |
| `aic-maintain.md` 触及 100 行薄命令门禁 | 改措辞压缩（当前 99 行，需重写而非追加） |
| 分层判断仍会出错 | 草稿带「候选归属」+ 巡检有规则全文；出错成本从「污染正典」降为「删一条草稿」 |
| **溯源信息缺失或造假** | 来源字段为**必填**；巡检**先用来源核验再沉淀**（假证据 → 拒绝，见验证计划 2）；区分持久证据与 `[机器本地]` |
| 草稿被误当正典引用 | 明文禁止引用；`drafts/` gitignored（不可能被 tracked 文档正确引用） |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** —— 采纳 §4.7 **C″**：① 草稿区落在 **`governance/memory/drafts/`**（明确否决 `logs/memory/`：草稿紧挨正典，语义自解释、不在日志清理范围）② 日常会话**不要求提交** ③ **巡检必沉淀并提交**（持久性由沉淀结果保证）④ 草稿**必须记清来源**以便溯源 | 2026-09-24 |
| User (AI Maintainer operator) | **Approved（追加）** —— ⑤ 在 develop / review / bugfix **集成 memory 捕获**以扩大样本（§4.8）；并确认持久性边界按 §4.7 表执行（**草稿原文不保证不丢**，能保证的是提交过的正典）；L3 是否要做见 §4.9 | 2026-09-24 |
| User (AI Maintainer operator) | **Approved（第四追加）** —— ⑫ **显式写入「语言分层」**（源自 P77 对 Hindsight multilingual 的讨论）：Capture 层（Inbox）不限语言、中文候选原样沉淀；**语言转换发生在 triage**（Capture 不承担翻译）；Canonical 层仍强制英文。这补上了本提案一直缺位的一环——此前同时要求「Inbox 可中文」与「正典强制英文」，却从未规定转换责任在哪一步 | 2026-09-29 |
| User (AI Maintainer operator) | **Approved（第三追加）** —— ⑨ **增加 operational metric**（§5.9）：验收不再看「`drafts/` 是否为空」（该观测**无法区分**「全部沉淀」与「Agent 根本没产生候选」，而后者已实测存在），改为每次巡检记录五项计数（candidates generated / triaged / canonical memories created / redirected / discarded + **逐条 discard 理由**）与四个派生指标（候选产生率 / 沉淀率 / 丢弃率 / 积压）。**「Memory 实际复用率」不列入首版** —— 当前无机制记录反向引用，无数据来源。⑩ **路线图与优先级**（§5.8）：**P71 C″ = 9/10 应该落地**；**Hindsight = 7.5/10 保留为下一阶段 PoC**，且其职责**只做 Recall / Reflect，不做 Governance / Triage**（否则等于让未审核内容借 Recall 通道重新进入知识面，正是 §4.10 要防的）；并给出触发下一阶段的三个前置条件。⑪ 确认 §2.1 实测为 **P71 的核心论据** —— 「14 提交 / 6 条经验 / 捕获 0 条」比「833 行指南没人读」更直接，因为它证明的是**机制在真实工作流中已失灵**，而非「可能没人读」 | 2026-09-29 |
| User (AI Maintainer operator) | **Approved（再追加）** —— ⑥ **语义改名 Experience Inbox**：不是 "memory 的草稿"，而是**未经审核的经验候选队列**；生命周期显式为 Experience → Candidate → Inbox → Triage → {Memory / Standards / Skill / Project Workspace / Discard+理由}（§4.7）。**理由**：多数候选最终不是记忆；叫「草稿」会诱发「Agent 可以读草稿」这一危险误区。⑦ **「非正典、不得被引用」升级为硬规则**（§4.10）：**Agent 默认不得读 Inbox 当知识使用**；列禁止行为 5 条 / 允许行为 4 条（仅写入与 triage 角色可读）。⑧ **取消「4~6 行」硬限制**，改为**最低结构 5 字段必填**（`Candidate` / `What` / `Why` / `Source` / `Candidate Category`），行数不限；**优先保证来源与事实完整性而非行数** —— 理由：行数上限会诱发为压行数而丢 `Why` / `Source`，而这两者恰是 triage 最不可省的部分 | 2026-09-29 |

| User | **裁定（v1 不解决）** —— 2026-09-29：**正典引用计数缺口 v1 不解决**。不独立立项、不在观察期实施、不修改 `MEMORY_GUIDELINES` 的 Load 规则以实现「读即计数」。理由是**不值得为它改变 Memory 的读取语义**，而非「不需要知道」—— 前者可被后续证据推翻，后者不可。三条理由：①它会展开成 usage telemetry system（read event → 计数 → 持久化 → 去重/并发/重试 → 统计），而 P71 的目标是「经验产生 → 候选落地 → 正确分层 → 正典持久化」②`read count ≠ useful`，且 `read count = 0` 更可能说明**召回机制不好**而非知识无价值——记成「无价值」会导向删掉「读不到」的 Memory，而它们恰是召回层最该修好的对象 ③**危险 KPI**：为提高「使用率」被迫加载大量 Memory，与 `CONTEXT_LOADING.md` 预算纪律正面冲突。**显式禁止**把 Memory read count / reference count / utilization % 写入观察期指标。未来若重做，起点是 `recalled → used → task outcome` 而非计数 | 2026-09-29 |

| User | **观察期数据有效性裁定（2026-09-29）** —— 用户问「如何保证后续产生有效数据」，经逐项复核后修正四项：①**删除「候选产生率」**（用户确认）—— 分母「期间有经验密度的会话数」无采集机制，且与「捕获经验」是同一 AI 的同一判断（用被测系统的输出算分母）；唯一可数替代 `logs/` 是**特定运行的诊断记录**、非每次会话都有、且在机器本地，是更弱的代理。**删掉是安全的**：该率要解决的「`drafts/` 为空无法区分『全部沉淀』与『根本没产生候选』」已由 `generated`/`triaged` **配对读**解决（`0/0` vs `0/N`），率的引入没解决问题、只引入了不可算的分母 ②**新增「discard 理由多样性」**（用户确认）—— 「逐条一行」是格式要求，拦不住 N 条完全相同的合理措辞 ③**明确「只看方向不看水平」**（用户确认）—— 分子分母同源（捕获 AI / triage AI / Source 核验 AI），唯一独立防线已被同源抵消，故**不给目标带**；任何单一比例落在中间区间都不可判定为健康，四周后有真实数据再定带 ④**数据无失效路径** —— 条件 ② 若不满足，P77 停在 Blocked 且无定义好的下一步，**待裁定**。**AI 自我更正**：复核时我断言「`config/maintenance.yaml` 的 `last_findings` 是单值字段、无法跨轮积累」—— **错误**。实测为 list（50 条目），`.gitignore` 与文件头注释均写明是「折叠块标量序列」，追加**确实**能跨轮积累。犯的错误是读了文件开头看到 `- >-` 却未验证类型就下结论 —— 这正是 P78 里写过的「『看起来是』不等于『是』」的反面。已撤回该缺口 | 2026-09-29 |

| User | **恢复为下界形式 + 采集落库约束**（2026-09-29）—— 用户指出现有 `<workspace>/logs/` 已有 develop/review/bugfix 运行日志。**AI 据此更正自身此前的错误断言**：曾称 `logs/` 是「特定运行的诊断记录、**非每次会话都有**」—— 实测**该三类每次运行都留痕**（22 份），且正是加了 `## Experience Candidates` 的三个 runtime，仪器化范围与日志范围精确对应。故「候选产生率」**恢复为下界形式**：分母 = instrumented 运行数，性质 = 真实捕获率的**下界**（分母含无经验的运行）。实测分布 **18 develop : 2 review : 2 bugfix** 极不均衡，须**按 workflow 类型分读**。**用户追加两条约束**：①`logs/` **曾被 AI 误删**（`reports/INCIDENT-2026-09-24-ignored-state-wipe.md` 记录 repo 内 gitignored 目录被清空，约 200 份日志全毁）→ 分母必须在**巡检时落库**为累积值，**不得实时回查 `logs/`**；②`metrics/` 现有快照命名 `maintain-<date>.json` **无机器维度**（实测），两机同日巡检会互相覆盖 → 落点改为 `metrics/by-machine/<machine-id>/knowledge-runs.jsonl`，以机器目录为隔离单元。追加 `watermark` 防重复计数、`files` 全量留存使计数可审计（理由同「discard 理由多样性」：只记结论不记依据的数字无法被质疑）、五项计数记录须带 `<machine>`（捕获机与巡检机常不同机，跨机比率的分子分母会错配）。落点遵守 §5.9「不新建指标文件」——`metrics/` 是既有机器层指标区，仅增设 per-machine 子目录 | 2026-09-29 |

## Implementation Record (2026-09-29) — S1 + S2

§5 的 8 项必做全部落地（#9 陈旧草稿 WARN 与 #10 L3 按提案保持「可选 / 待裁定」，未做）。
§6 的验证计划**实际执行**，未执行项逐条说明。

### S1.1 交付物（commit `f0e9e0c`）

| 文件 | 内容 |
|---|---|
| `governance/memory/MEMORY_GUIDELINES.md` | `# Experience Inbox` 节（~100 行）：硬规则 · 五字段 · 语言分层 · triage 去向 |
| `.gitignore` | 忽略 `governance/memory/drafts/`，附理由 |
| `tools/checks/memory.py` | `DRAFTS_DIR` 豁免，`language_violations` 与 `check_memory` **双路径** |
| `skills/memory-capture/SKILL.md` | 双路径（Inbox 默认 / 直写正典为例外）+ Source 纪律 |
| `cli/tests/test_memory_drafts_exemption.py` | 新增 12 例 |

### S1.2 交付物（commit `460f813`）

| 文件 | 内容 |
|---|---|
| `cli/commands/aic-maintain.md` | step 2.6 triage + 五项计数；Guardrails 加 Inbox 只读硬规则；99 → **100 行**（贴薄命令门禁上限） |
| `OPERATIONS.md` | §1.7.1 Experience Inbox：职责分工 + 节奏 + 三条分界 |
| `templates/runtime/runtime-{develop,review,bugfix}.md` | 各 +22 行 `## Experience Candidates` |

### S1.3 验证计划执行结果（§6）

| # | 项 | 结果 |
|---|---|---|
| 1 | 门禁不破 | **通过**。Inbox 含中文 + 缺字段时 `check.py` PASS、`pre_commit_gate` exit 0。**反证**：正典缺 `Lesson` → ERROR；正典写中文 → ERROR（`4 CJK chars`）。豁免未扩大到正典 |
| 2 | 端到端 + 五项计数 | **部分通过**。3 候选 → `generated=3 / triaged=3 / promoted=1 / redirected=0 / discarded=2`，逐条 discard 理由非空。假 Source（`adr.py:999`，该文件仅 92 行）**被拒**。「本轮无候选」的反向用例未跑（需真实会话） |
| 3 | 摩擦对比 | **通过**。Inbox 路径：写 12 行草稿、**0 次**读 833 行指南、**0 次**提交 |
| 4 | 直写正典不退化 | **通过**。`## [ai-system] …` + `Lesson:` 独占一行 → 0 errors |
| 5 | 场景集成有效 | **未执行** —— 需真实 develop/review/bugfix 收尾。无候选的合法结果已有措辞兜底，但**未实测** |
| 6 | 硬规则可判定 | **部分通过**。规则文本存在性已由 `test_guidelines_document_the_hard_rule` 断言。「普通会话不引用候选」与「triage 能读到」两个方向**未实测** |
| 7 | 长候选不被压扁 | **通过**。12 行候选（含第 12 行尾标）完整保留，行数无截断 |

### S1.4 实施中发现的四个问题

**① 薄命令门禁比提案预估的更严（提案 §7 已预警，实测更甚）**
P71 §5-5 写「当前 99 行，需重写措辞守住 100 行」。该门禁在
`tools/workflow-command-audit.py`（**不在 `check.py` 内**），且是 **error 不是
warning**。加完 triage 113 行 → FAIL。压回 100 的优先级：**删重复**（triage 细节改为
指向 `MEMORY_GUIDELINES`，初稿把路由表重述了一遍 = 第二份真相）→ 合并 bash 块 →
删解释性从句。**未删** step 0/1/2 的实际检查项 —— 门禁该守的是薄，不是空。

**② 门禁豁免需双路径（提案只写一处）**
`checks/memory.py` 有两条独立遍历路径。只改 `check_memory` 会让 `language_violations`
继续对 Inbox 报 CJK ERROR，豁免形同无效。

**③ 提案的示例路径被自己的门禁拦下**
`MEMORY_GUIDELINES` 的禁止反例原写 `20260929-foo.md`，被 `path-audit` 判为 broken。
改为 `{yyyymmdd}-{session|topic}.md` 模板形态 —— **改文档适配门禁，不是给门禁加豁免**。

**④ 豁免的「格式」那一半是理论性的**
实测 `check_memory` 只校验 `## [Category] Title` 形状的条目；候选的 `## Candidate:`
**无论有没有豁免都会被它忽略**。真正起作用的是语言那一半。已更正 `tools/checks/memory.py`
的注释（原注释把两处理由写成等价）。若日后候选格式改为方括号式，此豁免才具格式意义。

### S1.5 一个已修的破坏性缺陷（测试自身）

`test_memory_drafts_exemption` 的 `_cleanup` 原本是
`for p in DRAFTS.glob("*"): p.unlink()` —— **跑一次单测会清空整个真实 Inbox**。
Inbox 是 git-ignored 的，清空后**无痕迹、不可恢复**。已改为只删本测试创建的文件，
并加 `test_cleanup_does_not_touch_foreign_candidates` 钉住该性质。

同批修掉两处测试自身的脆弱性：
- 断言用 `"_probe"` 子串匹配，误伤真实 memory 树里任何同名探测文件 → 改为按
  `DRAFTS_DIR` 匹配
- 「同内容对照」用例的前提不成立（`## Candidate:` 根本不是 canonical 形状）→ 改为
  准确陈述格式那一半为理论性

### S1.6 验证计划带出的一个新规则：Source 的**形式**与存在性同等重要

端到端 triage 跑出的实测：候选引用 `tools/checks/memory.py:20` **实质正确**，
但 `DRAFTS_DIR` 已漂移到第 31 行。

- **严格按行号核验** → 误拒一个真声明
- **只按文件存在核验** → 放过一个伪造的（`adr.py:999` 文件存在但行号越界）

故 triage 对**行号过期/越界**判为「需确认」而非「已证伪」，并按内容确认。
并在 `MEMORY_GUIDELINES` 写入 Source 形式强度排序：

| 形式 | 源文件被编辑后仍可核验 |
|---|---|
| commit hash | **是** —— 不可变 |
| 引用片段 / 命令输出 | **是** —— 自包含 |
| `file:line` | **否** —— 行号随文件演进漂移 |

**能在自己的源文件下一次编辑后存活的候选，才值得晋升。**

### S1.7 观察期读数口径的修正（2026-09-29，用户裁定）

S2 交付后复核「如何保证后续产生有效数据」，修正四项（详见 Review Log）：

| # | 修正 | 落点 |
|---|---|---|
| ① | **删除「候选产生率」**，改为 `generated` × `triaged` **配对读绝对值** | §5.9 派生指标表 |
| ② | **新增「discard 理由多样性」** | §5.9 派生指标表 |
| ③ | **明确「只看方向不看水平」** —— 分子分母同源，不给目标带 | §5.9 新增「观察期的读法口径」节 |
| ④ | 数据无失效路径 —— **待裁定** | 未改 |

同步 `cli/commands/aic-maintain.md` step 2.6 的措辞（配对读法 + 「无计数即未完成」），
并补 `append to last_findings`（该文件确为 list，可跨轮积累）。

`aic-maintain` 行数：本次改动一度涨到 104 行触发薄命令门禁，**压回 98 行** ——
手段是**删重复**：完整读法纪律留在 P71 §5.9，命令只留「去查」级别的提示。
未删任何检查项。

**一条自我更正**：复核时断言「`last_findings` 是单值字段、无法跨轮积累」——
**错误**。实测为 list（50 条目），追加可跨轮积累；该缺口不存在。犯的错误是
看到 `- >-` 未验证类型就下结论。

### S1.8 未做（按提案保持）

#9 陈旧草稿 WARN（提案「先不做」）、#10 L3 草稿原文不丢（待裁定）、
PII 检测、门禁内 LLM 语义判定。§5.9 的真实数据须待实际会话与巡检产生 ——
**当前五项计数全为空是正常的，代码已部署但尚未运行**。