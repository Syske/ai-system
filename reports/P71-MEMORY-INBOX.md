# Change Proposal: P71 — Memory 候选暂存区 + 巡检确认提取（Memory Inbox）

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
日常会话（默认路径，零负担、不提交）
  └─ governance/memory/drafts/{yyyymmdd}-{session|topic}.md
     每条候选 ≥4 行，**必须含来源**（可中文、不要求正典格式、不读 833 行指南、不改索引）
                        │
周巡检 / 日常巡检 —— aic-maintain step 2.6
  └─ 逐条 triage（用来源字段去核验/查重）：① 蒸馏进 governance/memory/<category>/（英文+格式+索引）
                                             ② 改投 standards/ 或 skills/（本是规则/能力）
                                             ③ 写进 workspaces/<project_id>/（单项目需求）
                                             ④ 丢弃（重复/瞬时/无价值）——记理由
  └─ **提交沉淀结果**（提交蒸馏后的正典，不是草稿原文）· 删除已处理草稿 · 结果写进巡检报告
```

**草稿条目最小 schema（4~6 行，可中文）**：

```text
## <一句话：学到什么>
- 来源: <会话/日期> · <项目或仓库> · <触发: 事故 / 评审发现 / 复盘 / 用户要求>
- 证据: <commit sha / file:line / 命令与输出摘要>（若只存在于本机日志 → 标 [机器本地]）
- 候选归属: memory(<category>) | standards | skills | workspace(<project>) | 丢弃
- 要点: <1~3 行>
```

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

**四条护栏（缺一即退化）**：① 每次巡检都沉淀（挂周巡检 + 日常巡检；月度 review 仍只管去重/查矛盾/查过期）
② 沉淀后**必须提交 + 必须删草稿**（陈旧草稿 WARN 先不做）③ 草稿层**非正典、不得被任何规则/技能/报告引用**
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

## 5. Proposed Changes（Option C″ + D）

| # | 改动 | 落点 | 规模 |
|---|---|---|---|
| 1 | **草稿区约定**：`governance/memory/drafts/{yyyymmdd}-{session\|topic}.md`，每条含 §4.7 的最小 schema（**必须含来源**）；中文/任意格式/**不提交**；会话按需 `mkdir -p` | 约定写入 `MEMORY_GUIDELINES` 与技能（tracked 文档） | 极小 |
| 2 | **gitignore**：忽略 `governance/memory/drafts/`（草稿不进 git，避免 `??` 噪音与 `git add -A` 误提交） | `.gitignore` +1 行 | 极小 |
| 3 | **门禁豁免**：`checks/memory.py` 跳过 `drafts/`（因它是 `rglob` 遍历，gitignore 挡不住；否则草稿中文 → error） | `tools/checks/memory.py` + 1 条单测 | 小 |
| 4 | 技能双路径：**默认写草稿**（零负担、含来源）；会话确定且能合规、或用户要求立即沉淀时仍可直写正典；二者都不要求会话提交 | `skills/memory-capture/SKILL.md`（+5~6 行） | 小 |
| 5 | 巡检沉淀：读 `drafts/*.md` → 用来源核验 → triage（正典 / 改投 standards·skills / workspace / 丢弃）→ **提交沉淀结果** → 删草稿 → 记报告 | `cli/commands/aic-maintain.md` step 2.6（**当前 99 行，需重写措辞守住 100 行薄命令门禁**） | 中 |
| 6 | 节奏与职责划分：沉淀挂周巡检/日常巡检；月度 review 仍只管去重/矛盾/过期 | `OPERATIONS.md §1.7`（+2~3 行） | 小 |
| 7 | 草稿层声明：非正典、不得被引用、含来源要求、巡检后清空 | `governance/memory/MEMORY_GUIDELINES.md` 一节（~12 行） | 小 |
| 8 | **场景集成**：develop / review / bugfix 三个 runtime 收尾各加一条「经验候选」指令（英文；含资格门槛与「无候选是合法结果」） | `templates/runtime/runtime-{develop,review,bugfix}.md`（各 +3~4 行） | 小 |
| 9 | （可选）陈旧草稿 WARN（>1 个巡检周期未处理）→ **先不做**，等真实需要 | — | 待定 |
| 10 | （可选，**待裁定**）L3 草稿原文不丢：drafts 改 tracked + 巡检归档提交 | `.gitignore` · `checks/memory.py` · `pre_commit_gate` · 巡检步骤 | 中 |

**成本**：**零新增 tracked 文件**（草稿区 gitignored；空目录不入库）· gitignore +1 行 · 门禁豁免 1 处 + 1 单测 ·
**8 处文档/技能/runtime 小改（约 50 行）** · 无新工具/命令 · 固定 token 成本 **0**
（草稿不在任何提示词路径上；runtime 三处各 +3~4 行随该阶段提示词加载）。

## 6. Validation Plan

1. **门禁不破**：`check.py`（含 memory 第 8 项）· `pre_commit_gate`（staged CJK 记忆）· `repo-lint` 全绿；
   `drafts/` 豁免后**正典检查强度不变**（反证：故意缺 `Lesson` 的正典仍须 error；故意在正典写中文仍须 error）。
2. **端到端一次**：模拟日常会话写 2 条草稿（1 条中文经验、1 条其实是「规则」）→ 跑巡检 step 2.6 →
   验证 ① 经验条晋升为正典（英文 + 索引已更新）② 「规则」条被改投 standards ③ 草稿被删除 ④ **来源字段能被核验**
   （故意写一条假证据 → 巡检须拒绝沉淀）。
3. **摩擦对比**：完成一次 capture 所需的**读写文件数**：现状（读 833 行指南 + 写正典 + 改索引 + 提交）
   vs 新路径（写 5 行草稿、**不提交**）。
4. **不退化**：直写正典路径仍可用（用一次真实捕获验证）。
5. **场景集成有效**：跑一次 develop（或 review/bugfix）任务收尾 → 验证 ① 满足资格者写进草稿
   ② 不满足者明确报告「无经验候选」（两个方向都要测，防"为交差硬写"）③ 草稿来源字段可核验。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| `drafts/` 变成**垃圾堆**（只进不出） | 巡检每次清空；不设"永久参考区"；（可选）陈旧草稿 WARN |
| 与正典出现**两套记忆** | 草稿层明文声明「非正典、不得被引用」；沉淀即删；索引不列它 |
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

## Implementation Record

*(待实施后填写)*