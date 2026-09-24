# Change Proposal: P71 — Memory 候选暂存区 + 巡检确认提取（Memory Inbox）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural（新增候选暂存文件 + 技能双路径 + 巡检提取 + 一处门禁豁免） |
| Author | AI Maintainer |
| Created | 2026-09-24 |
| Reference | 用户 2026-09-24 提出「日常会话不清楚维护规则、大概率出错 → memory 单独存储（如 `logs/memory/`）+ 日常运维确认提取」；本仓记忆机制侦察（§1） |
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

### 4.3 Option C — **被跟踪的候选暂存区 + 巡检确认提取**（推荐）

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

## 5. Proposed Changes（Option C + D）

| # | 改动 | 落点 | 规模 |
|---|---|---|---|
| 1 | 新增候选暂存文件（tracked；表头说明 + 一行一条；不要求英文/格式） | `governance/memory/inbox.md`（新，~15 行） | 小 |
| 2 | 门禁豁免：inbox 不受"条目格式 / Lesson 必填 / CJK=error"约束，但仍做**英文以外的**基础校验（可解析、非空行） | `tools/checks/memory.py`（1 处豁免 + 可能 1 条 WARN：inbox 有陈旧行未处理） | 小 |
| 3 | 技能双路径：默认写候选行 + **必须独立提交**；会话明确要落正典且能满足契约时仍可直写（保留能力） | `skills/memory-capture/SKILL.md`（+3~4 行） | 小 |
| 4 | 巡检提取：triage inbox（+ 既有 logs 扫描）→ 晋升/改投/丢弃，提取后删行 | `cli/commands/aic-maintain.md` step 2.6（**注意 100 行薄命令门禁，当前 99 行，需压缩措辞**）· `OPERATIONS.md §1.7` | 小 |
| 5 | 索引/根索引同步说明：inbox 不在索引内（它不是正典） | `governance/memory/coding-memory.md` 一行备注（可选） | 极小 |

**成本**：1 个新文件 + 4 处小改（合计约 30 行）；**无新工具、无新命令、无新测试面**
（`memory.py` 的豁免需 1 条单测）；固定 token 成本 **0**（inbox 不在 Always Load）。

## 6. Validation Plan

1. **门禁不破**：`check.py`（含 memory 第 8 项）· `pre_commit_gate`（staged CJK 记忆）· `repo-lint` 全绿；
   inbox 豁免后正典检查强度**不变**（用一条故意缺 `Lesson` 的正典做反证，仍须 error）。
2. **端到端一次**：模拟日常会话往 inbox 追加 2 行（1 行中文经验、1 行其实是"规则"）→ 跑巡检 step 2.6 →
   验证 ① 经验行晋升为正典（英文 + 索引已更新）② "规则"行被改投 standards ③ inbox 被清空。
3. **摩擦对比**：完成一次 capture 所需的**读写文件数**：现状（读 833 行指南 + 写正典 + 改索引 + 提交）
   vs 新路径（追加 1 行 + 提交）。
4. **不退化**：直写正典路径仍可用（用一次真实捕获验证）。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| inbox 变成**垃圾堆**（只进不出） | 巡检 WARN"陈旧候选"；提取后必须删行；不设"永久参考区" |
| 与正典出现**两套记忆** | inbox 明文声明"草稿层，非正典，不得被引用"；提取即删；索引不列它 |
| 巡检负担增加 | 候选行是结构化的 1 行（比扫 200 个 logs 文件更快）；且可与既有 logs 扫描合并成一次 |
| 门禁豁免被滥用（往 inbox 塞永久内容） | 豁免只针对 inbox 单文件；陈旧 WARN 兜底；巡检每次清空 |
| `aic-maintain.md` 触及 100 行薄命令门禁 | 改措辞压缩（当前 99 行，需重写而非追加） |
| 分层判断仍会出错 | 候选行带 `proposed target` + 巡检有规则全文；出错成本从"污染正典"降为"删一行" |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户提出"是否需要完善 memory/维护机制"，并要求评估"单独存储到 logs/memory/ + 运维确认提取"；§4 待选 A/B/C/D） | 2026-09-24 |

## Implementation Record

*(待实施后填写)*