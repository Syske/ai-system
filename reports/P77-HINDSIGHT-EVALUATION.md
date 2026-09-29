# Change Proposal: P77 — Hindsight 评估：Experience Knowledge Layer 候选定位与前置验证

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Evaluation（外部方案评估 + 前置验证设计；**不含任何集成**） |
| Author | AI Maintainer |
| Created | 2026-09-29 |
| Reference | 外部评委对 [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)（41.4k stars / 3,262 commits / MIT）的评估结论 + AI 二次核查（逐条对照官方 README 与 best-practices）；`reports/P71-MEMORY-INBOX.md` §5.8（路线图与优先级）· `governance/memory/MEMORY_GUIDELINES.md` · `governance/CONTEXT_LOADING.md` §Context Budget Discipline · `governance/policies/security-policy.md` |
| Process | OPERATIONS §12 Change Management |

---

## 1. 结论先行

**认同外部评委的核心定位**：Hindsight ≠ Runtime / Workflow / Governance / Skill 的替代品，
它对应我们缺失的 **Experience Knowledge Layer**。

**不认同其时间安排**（"7.5/10，保留为下一阶段 PoC"）。理由是**顺序倒置**：

| 事实 | 值 | 来源 |
|---|---|---|
| 近 30 天提交 | **288** | `git log` 实测 |
| 近 90 天提交 | **551** | 同上 |
| memory 正典条目 | **19** | `governance/memory/**` 实测 |
| 提交/正典比率 | **每 15 个提交沉淀 1 条经验** | 计算 |
| 今日实测（`cd6f366..edd5feb`） | 14 提交 / ≥6 条明确经验 / **经捕获流程入库 0 条** | P71 §2.1 |

**捕获入口产出为 0 时，接入 Recall 层等于给空水箱装水泵。** 且评委自设的 PoC 问题③
（"Memory 是否真的比现有 Markdown Knowledge 有价值"）在当前状态下**无法回答**——
因为没有 Memory 产生。

**本提案的定位**：**不立项集成，只立项「前置验证」**——用我们已有的 19 条正典 + 551 个
提交的 git 历史，验证「普通检索是否已经够用」。成本极低（不安装任何东西），
但可能直接**省掉整个 PoC**。

---

## 2. 对外部评委结论的二次核查

### 2.1 事实核对：评委所述基本准确（8/8 核实通过）

| 评委论断 | 核查结果 |
|---|---|
| Retain / Recall / Reflect 三操作 | ✅ 官方 README 确认 |
| Recall = 语义 + BM25 + 图遍历 + 时间 | ✅ 确认，且更精确：**4 路并行 → RRF（reciprocal rank fusion）融合 → cross-encoder 重排 → token 预算裁剪** |
| Observation = 多事实 consolidation，保留证据 | ✅ 确认，**且强于评委描述**：`refined rather than overwritten`——新证据是增强/削弱/扩展既有信念，**不是静默替换**；带 exact quotes + proof count |
| Memory Bank 严格隔离、无交叉泄漏 | ✅ 确认（"Isolation is strict: no cross-bank leakage"） |
| MCP per-bank endpoint | ✅ `http://localhost:8888/mcp/{bank_id}/`，**每服务自带、默认启用** |
| Coding Agent 集成含 opencode / pi | ✅ 确认 |
| per-repo bank 从 git history + past sessions 自动构建 | ✅ 确认 |
| 不建议现在进 Runtime | ✅ **认同**，且见 §2.3 的补强 |

### 2.2 评委漏掉的 4 条（**2 条对我们的价值高于评委力推的 Observation**）

#### ① Knowledge Pages —— 比 Observation 更值得重点关注

官方 README：

> "**knowledge pages** are mental models with the mechanics hidden: living
> documents a bank writes about itself, organized in folders like a wiki,
> searchable, and **projectable onto disk as ordinary markdown**"

> "Reading one is a **database read — no retrieval, no LLM call** — so an agent
> can boot with a page of settled knowledge instead of rediscovering it every session."

**为什么对我们最关键**：这是 Hindsight 提供的「**AI 生成的知识如何回到可治理形态**」的机制
——投影为普通 markdown，即可进入我们既有的 tracked + diff + review + 17 项门禁的
体系。评委完全未提此条。

**注意它与我们的张力**：「a living document the bank writes about itself」意味着
**AI 会自动改写这个文件**。我们的 protected paths（`config/protected-paths.yaml`）
对 `reports/` / `governance/` 等 8 项默认拒绝删除/移动/替换——**自动改写与该护栏直接冲突**。
这是评委未识别的一次架构冲突。

#### ② Memory Defense —— 我们的**硬需求**，不是加分项

官方 README：per-bank 策略，扫描 secrets / PII **45 种模式**，可 `redact`
（`[REDACTED:github_token]`）或 `block`。

我们 `governance/policies/security-policy.md:9`：

> "**Never commit secrets.** API keys, tokens, passwords, and private certificates
> must never appear in source code, configuration, or reports."

而记忆是 **AI 自动写入**的。当前我们**唯一的自动化防线**是提交前的
`memory_language_check`（查 CJK，**不查 secret**），以及人工 review。
P71 定了「Inbox 只做 triage 不做知识」，但**triage 之后写入正典的路径同样可能带进 token**。

**这是引入 Hindsight 的最强正面论据之一，而非加分项**——但评委未识别。

#### ③ Multilingual —— 与我们的英文强制**直接冲突**，且恰好补 P71 短板

官方 README：输入语言检测并端到端保留，*「张伟 stays 张伟, not "Zhang Wei"」*。

我们 `MEMORY_GUIDELINES.md:26`：

> "Memory entries **MUST** be written in English (AI-internal layer)"

且 `tools/pre_commit_gate.py` 会**阻断**含 CJK 的 staged 记忆文件。

**这不是小差异**：Hindsight 可**直接 retain P71 Inbox 的中文候选**（无需先转英文），
而 P71 的 Inbox 设计假设的就是中文。**这条能力恰好补上 P71 的一处短板**——
但它同时要求我们放弃"正典强制英文"这条既有纪律，**这是一次真实的取舍，不能顺手采纳**。

#### ④ Disposition traits —— 评委漏掉的唯一**风险项**

官方 README：banks 携带 *「**disposition traits** (skepticism, literalism, empathy)
that **shape how reflect reasons over their memories**」*。

即：**reflect 的输出不是纯事实检索，会被 bank 的人格参数塑形**。

我们的 `AI_OPERATING_RULES.md` §Validation 要求 **gate function 五步**
（IDENTIFY → RUN → READ → VERIFY → **ONLY THEN** 声称），本质是
**证据先于断言**。一个带 disposition 的 reflect 通道**不满足该前提**——
它产出的"结论"无法与"证据"分离。

**处置**：若未来评估，reflect 通道必须与 recall 通道**同等对待**——都只能作为
**人/AI 的参考输入**，都不得直接进 Runtime 决策或 Governance。

### 2.3 评委的架构图与其文字**自相矛盾**（必须修正）

- **§8 文字**：「现在让 Hindsight 进入 Runtime，会让原本 deterministic 的 Runtime
  行为变成**依赖历史记忆质量**」
- **§9 图**：`Learned Memory → Context Loader → Runtime`

**图与文字冲突**。按 §8 的正确判断，Runtime 不应直接消费 Learned Memory。修正：

```text
Learned Memory ──triage──▶ Candidate ──approval──▶ Controlled Knowledge ──▶ Runtime
      │                                                              ▲
      └──────────── Recall（仅供人/AI 参考，**不进 Runtime 决策**）───┘
```

**这条边界与 P71 §4.10 是同一件事的两种表述**：P71 已把
「Agent 默认不得读 Inbox 当知识使用」定为**硬规则**；本提案把它扩展到
「Learned Memory 层的一切输出都不得直接进 Runtime」。

### 2.4 评委完全未评估的两项

#### 成本与延迟（我们已有明确纪律）

Hindsight 的每次操作都有 LLM / 模型调用：

| 操作 | 内部代价 |
|---|---|
| `retain` | **LLM 抽取** facts / entities / relationships / 归一化 |
| `recall` | 4 路检索 + **cross-encoder 重排** |
| `reflect` | **LLM 深度分析** |

存储还需 **PostgreSQL + pgvector**（或 Oracle AI Database 23ai），或使用
Hindsight Cloud（**则数据出境到第三方**）。

我们 `CONTEXT_LOADING.md:132` 有 **Context Budget Discipline**；P71 立项时明确承诺
**「固定 token 成本 0」**。引入 Hindsight 意味着**每个工作流都可能触发多次 LLM 调用** +
一个新常驻服务 + 一套数据库。

**这不是「顺路加一层」，是引入有状态、有成本、有外部依赖的基础设施。**

#### 成熟度（决定 API 稳定性预期）

- **41.4k stars，但 90 open issues + 97 open PRs、3,262 commits** → 迭代极快，
  **API 不稳定**，需锁定版本并预期迁移
- 依赖 PostgreSQL + pgvector（重量级）；或 Hindsight Cloud（数据出境）
- MIT 协议（可接受）

---

## 3. Options

### 3.1 Option A — 现在引入 Hindsight 作为 Runtime 依赖

❌ **否决**。与 §2.3 的自相矛盾、违反 P71 §4.10 硬规则、引入 LLM 调用到执行路径、
破坏 Runtime 的 deterministic 属性。

### 3.2 Option B — 立即做 Hindsight PoC（评委方案）

❌ **现在做不可行**：没有 Memory 产生（捕获产出 0），PoC 的三个问题都无从回答。
且需先付出部署 + 数据库 + LLM key 的成本。

### 3.3 Option C — **前置验证「普通检索够不够」**（**推荐**）

在**零安装、零外部依赖**的前提下，先回答评委的问题③：

```text
现有资产：
  governance/memory/**  19 条正典
  git 历史             551 提交（90 天）
  CodeGraph 索引        （本仓已有）
  grep / 语义搜索       （CONTEXT_LOADING 的三档检索）

测试问题：
  给定一个「跨 session 找回某条经验」的真实问题，
  用本仓既有检索能力，命中率是多少？需要几次检索？
```

| 结果 | 后续 |
|---|---|
| **普通检索已够**（高命中率、少轮次） | **Hindsight 的核心价值主张不成立** → 不做 PoC，节省全部成本 |
| 普通检索不够（需多轮拼凑 / 跨文件关联） | Hindsight 的 **Graph / Observation / Mental Model** 层有真实增量 → 此时才进入 PoC 评估 |

**这一步的成本**：一次（或少数几次）人工检索实验，**不需要装任何东西**。
**可能的收益**：直接省掉整个 PoC。

### 3.4 Option D — 只做文档登记，暂不验证

记录评估结论与边界（Learned Memory 不进 Runtime 等），不做任何验证。
❌ 理由：结论会随时间失效（19 条正典会增长、检索能力会变），**没有实测锚点的结论
不具备决策价值**。

### 3.5 Option E — 借 Hindsight 补 P71 的三个已知短板

不等 PoC，直接借鉴三项具体能力：
① Memory Defense（secrets 扫描）② Multilingual（中文候选直存）③ Knowledge Pages
（投影为 markdown 回到治理体系）。

❌ 理由：这三条**都可以不用 Hindsight 而自行实现**（我们已有 17 项门禁的工程能力）。
为三个可自建的能力引入整套基础设施，是本末倒置。

---

## 4. Recommendation

**采用 Option C（前置验证），并把 Option A/B 的边界写成硬约束记录在案。**

### 4.1 执行顺序（与 P71 §5.8 合并）

```text
现在
 └─ P71 C″ 落地（捕获机制 0 → 有产出）        ← 先决条件，不可跳过
     ↓
 观察期（P71 §5.9 五项计数 + 四个派生指标）
     ↓
 ├─ 正典周累计稳定增长 ──▶ 【本提案】前置验证「普通检索够不够」（Option C）
 │                            ├─ 够 ──▶ Hindsight 价值主张不成立，**不继续**
 │                            └─ 不够 ──▶ 评估 PoC（届时才讨论部署）
 └─ 增长停滞 ──▶ 问题在捕获/资格门槛，**加 Recall 层无用**
```

### 4.2 触发 PoC 的前置条件（在 P71 §5.8 三个条件上追加第 ④ 条）

| # | 条件 | 状态 |
|---|---|---|
| ① | 连续 ≥4 次巡检记录完整 §5.9 五项计数 | P71 已定 |
| ② | 正典条目周累计稳定增长 | P71 已定 |
| ③ | ≥1 条正典条目被实际复用并记录 | P71 已定 |
| ④ | **本提案 Option C 的前置验证结论为「普通检索不够」** | **本提案新增** |

**④ 必须在 ①②③ 之后**——因为检索够不够的答案**依赖正典规模**：19 条时普通 grep 也许
够，200 条时未必。所以验证必须在捕获机制跑一段时间、正典积累之后做。

### 4.3 无论 PoC 是否进行，这些边界现在就成立（硬约束）

| 约束 | 理由 |
|---|---|
| **Learned Memory 不得进 Runtime 决策** | 评委 §8 已认定；扩展为 P71 §4.10 硬规则 |
| **reflect 通道不得产出「结论」** | disposition traits 会塑形输出，违反证据先于断言 |
| **Hindsight 数据不得成为 Governance 依据** | 未审核内容不得借 Recall 通道进知识面 |
| **不引入 LLM 调用到执行路径** | P71 承诺固定 token 成本 0；`CONTEXT_LOADING` 有预算纪律 |
| **若用 Cloud 则数据出境** | 与 `ai-system` 公开仓库属性 + secret 禁令冲突，须单独评估 |
| **锁版本 + 预期 API 迁移** | 97 open PRs / 3,262 commits |

---

## 5. Proposed Changes（本提案范围 = 评估记录 + 验证设计，**不含集成**）

| # | 改动 | 落点 | 规模 |
|---|---|---|---|
| 1 | 评估记录：§2 的一/二次核查结论（含评委 4 条遗漏、1 处自相矛盾、2 项未评估） | 本提案 | 已完成 |
| 2 | 硬边界登记（§4.3 六条） | `governance/` 某处（待裁定：新增 policy 小节 or 记入本提案即可） | 小 |
| 3 | Option C 前置验证的**测试设计**（问题集、评分口径、通过线） | 本提案 §6 | 文档 |
| 4 | 把「④ 前置验证结论」追加为 P71 §5.8 的第 4 个触发条件 | `reports/P71-MEMORY-INBOX.md` §5.8 | 极小 |
| 5 | `governance/memory/MEMORY_GUIDELINES.md` 增一条：正典条目的**反向引用无法自动统计**（已知局限，见 §7） | tracked 文档 | 极小 |

**明确不做**：不部署 Hindsight、不加依赖、不改配置、不写 PoC 代码、不接入任何工作流。

---

## 6. Option C 前置验证设计（待 P71 落地后执行）

### 6.1 测试问题集（每条须是**真实发生过的**跨 session 检索需求）

从 19 条现有正典 + 551 个提交的历史中，构造 **8–12 个**问题，形如：

```text
「为什么 workflow 正文不能把 Phase 表直接写进去？」
「哪次门禁静默失效被发现了、怎么发现的？」
「memory 写入为什么必须独立提交？」
```

**问题必须满足**：答案**确实存在于**本仓某处（commit / 正典 / 报告 / 代码注释），
且**不是靠单一文件路径就能直接命中**（否则测的是 grep 不是检索能力）。

### 6.2 评分口径

| 指标 | 定义 |
|---|---|
| **命中率** | 检索结果中包含正确答案的比例 |
| **轮次** | 找到答案所需的检索轮次（越少越好） |
| **可定位性** | 能否指向具体 commit sha / file:line（我们的经验条目依赖来源字段） |
| **跨机器可用性** | 换一台机器（无本地索引）后是否仍能召回 —— **Hindsight 的核心宣称就在这里** |

### 6.3 通过线（**先定线，避免事后找理由**）

| 结果 | 判定 |
|---|---|
| 命中率 ≥80% 且平均轮次 ≤2 | **普通检索已够** → Hindsight 核心价值主张不成立，**不继续** |
| 命中率 <60% 或平均轮次 ≥4 | **普通检索不够** → Hindsight 的 Graph/Observation 层有真实增量 |
| 介于两者之间 | 记录数据，**不决策**；等正典规模再翻倍后重测 |

---

## 7. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **Knowledge Pages 的「AI 自动改写」与我们的 protected paths 冲突**（`reports/` / `governance/` 8 项默认拒绝替换） | §2.2-① 已识别；若未来评估，投影产物须落在**非受保护**位置或改为「AI 提议 + 人批准」 |
| R2 | **Disposition traits 使 reflect 不可作为证据** | §4.3 硬约束：reflect 通道不得产出结论 |
| R3 | **Multilingual 与正典英文强制冲突** | 明确标为取舍点，不得顺手采纳；引入须先修订 `MEMORY_GUIDELINES` 纪律 |
| R4 | **LLM 调用破坏「固定 token 成本 0」** | §4.3 硬约束：不引入执行路径；PoC 须用旁路 MCP，不改 prompt |
| R5 | **API 不稳定**（97 open PRs / 3,262 commits） | 锁版本 + 预期迁移成本 |
| R6 | **Cloud 方案导致数据出境** | 与公开仓库属性 + secret 禁令冲突，须单独评估，默认不用 |
| R7 | **本提案变成「无限期观察、不做决定」的借口** | §6.3 **先定通过线**；且明确 §4.2 的触发条件与顺序，避免「等 P71 跑够数据」无限拖延 |
| R8 | 验证只在**当前 19 条**规模上做，结论不可外推 | §6.3 明写「中间区间不决策」+ 须在正典规模翻倍后重测 |

---

## 8. 一个已知的测量盲区（须记在案）

P71 §5.9 定义了派生指标 **「Memory 实际复用率」**，并已注明「首版不列入，因为
**当前无任何机制记录反向引用**」。

本提案的 §6 评分口径中的「可定位性」会遇到同一盲区：**我们无法自动统计某条正典
条目被引用了多少次**。因此：

- 复用率**继续**排除在首版 metric 之外（与 P71 一致）
- §6 的验证只能**人工抽样评估**，不能做全量统计
- 若未来要自动化复用率，需要新增「正典条目引用计数」机制 —— **这是一个独立的、
尚未立项的缺口**（见 §9）

---

## 9. 待裁定

| # | 决策点 | 建议 |
|---|---|---|
| ① | 整体方案 | **Option C（前置验证）+ §4.3 硬边界登记**；不做 PoC |
| ② | §4.3 硬边界登记落点 | 记入本提案即可；**若认为需要长期生效**，另立 policy 小节（倾向后者，因硬约束不该只存在于提案里） |
| ③ | §6.3 通过线（80%/2 轮 vs 60%/4 轮） | 按此定线；**关键是先定，避免事后找理由** |
| ④ | 「正典引用计数」缺口是否单独立项 | **是** —— 它同时是 P71 §5.9 与本提案 §6 的共同盲区 |
| ⑤ | 是否现在就做 §6 验证（不等 P71） | **否** —— 19 条时普通检索很可能已够，此时验证会给出「Hindsight 无价值」的错误结论 |

---

## 10. 二次反馈的采纳与修正（2026-09-29）

外部评委在读到本提案 §2 后调整了评分，本节记录**第三轮**的采纳判定。

### 10.1 评委调整后的核心论断

> "Hindsight 不只是'一个长期记忆组件'，它里面有两项能力与你们的架构高度同构：
> **Knowledge Pages + Memory Defense**。但 `Disposition traits` 恰好说明了：Hindsight
> 不能直接成为你们的权威知识层，必须被放在治理边界之后。"

并新增一条：**`Disposition`（how to reason）vs `Directive`（what must be obeyed）**
是两种不同的东西，Directive 值得研究治理映射。

### 10.2 事实核实（全部一手依据，逐条通过）

| 评委新论断 | 一手依据 | 结果 |
|---|---|---|
| Directives 与 Disposition 是两种东西 | `memory-banks.md:706` — "Directives are **hard rules** the agent must follow during reflect… Unlike disposition traits which influence *how* the agent reasons" | ✅ |
| Directives 是 **strict** 的 | `memory-banks.md:908` — "**Enforcement: Strict — responses are rejected if violated**" / Disposition: "Flexible — shapes interpretation" | ✅ **比评委描述更硬**：不是"提示"，而是**违反即响应被拒** |
| Directives 支持 scope/tag | 未打标签 = 每次 reflect 都生效；打标签 = 仅 `tags_match` 匹配时生效；`apply_all_directives: true` 可强制全生效 | ✅ |
| Memory Defense 动作集 = `allow`/`redact`/`quarantine`/`block` | `memory_defense.default_action` 枚举 + `Rule.action` 枚举 + `min_severity`（low/medium/high/critical） | ✅ |
| 5 个 detector | `prompt_injection` · `sensitive_data` · `protected_key` · `immutable_key` · `size_anomaly` | ✅ **评委未强调其中 `prompt_injection` 的意义（见 §10.4-①）** |

### 10.3 逐条采纳判定

| 评委建议 | 判定 | 理由 |
|---|---|---|
| Knowledge Pages ⭐⭐⭐⭐⭐ **重点研究** | **认同价值判断，不改变 Option C 结论** | 价值高 ≠ 现在该做。**且其「AI 自动改写 living document」与 protected paths 8 项默认拒绝替换的冲突（§7 R1）在评分提升后更需要先解决，而非更次要** |
| Memory Defense 是**硬需求** | **完全认同并升级定位** | 从「Hindsight 的加分项」升级为「**我们自己的缺口**」→ 建议**独立立项自建**（§10.4-②），不等 Hindsight |
| Multilingual **分层**（Capture 不限语言 / Canonical 强制英文） | **完全采纳** | 比本提案 §2.2-③ 原先的「取舍点」表述更准确：**不是二选一，是分层**。且**解掉了 P71 的一个隐含矛盾**（§10.4-③） |
| Memory ≠ Knowledge 分层，P71 链路改为 `drafts → triage → Memory → Knowledge distillation → Canonical` | **部分保留** | 概念认同（历史经验 vs 蒸馏后规则确应区分）；但**「Knowledge」在我们体系里不是一个新层，而是 `standards` 的另一个名字**。P71 现有五类去向已含 `standards`（本就是规则）与 `skills`（本就是能力）——**硬加一层会与 `standards/` 重叠**。建议 P71 链路保持五类去向 |
| **Directives 做治理映射**（`AI_SYSTEM_GOVERNANCE → Hindsight Directive → Reflect`） | **不采纳** | 理由见 §10.4-④：**该映射在治理上自相矛盾** |
| Memory Defense **只做第一道防线**，不能是唯一防线 | **完全采纳** + 补一条 | 我们的原则是「安全约束必须在系统边界成立」：`retain → Memory Defense` 只是**前置过滤**，`pre-commit` / `check.py` / git 边界一道都不能少。**补：`quarantine` 隔离区不得进 export/import**——否则隔离内容会随 `include_data: true` 的导出重新流入（§10.4-⑤） |
| 架构图：Canonical Knowledge 与 Dynamic Memory 并列，Memory 经 Context/Recall 进 Agent | **采纳其修正方向**，但**收紧**：Recall 通道的产物仍**不得进 Runtime 决策** | 与 §2.3 / §4.3 一致；P71 §4.10 硬规则的扩展形式 |

### 10.4 三条评委未展开、但被其结论带出的补充

#### ① `prompt_injection` detector 揭示了一个我们完全缺失的安全类目

5 个 detector 中，**`prompt_injection` 不是 secret 泄漏，而是「记忆内容里携带指令」**——
即一条被 retain 的经验如果包含「忽略你之前的指令」这类文本，未来 recall 出来时会被 agent 当成指令执行。 <!-- ai-secret-scan: allow -->

我们的 `governance/policies/security-policy.md` 覆盖 API key / token / password / private
certificate / 内部仓库地址，**完全没有这一类**。而 P71 的 Inbox 是 **AI 自动写入**的
（"这个 token 可能对以后有帮助" → Inbox），正是注入内容最可能进入的入口。

**这是一条独立的缺口识别，与是否引入 Hindsight 无关。**

#### ② Memory Defense 的自建成本远低于引入成本（对 Option E 的量化支撑）

Hindsight 的 Memory Defense 本质是**detector（正则/规则）→ action（4 选 1）** 的映射表，
加上 `min_severity` 分级。我们已有 17 项门禁的工程能力（`tools/checks/*.py`）、
已确立的「每条门禁配负例 + 逐条短路自证」纪律（`policies/quality-gates.md`）。

**自建一个 `tools/checks/secrets.py` 覆盖 4 个 secret 类 + 1 个 injection 类，
成本远低于引入 PostgreSQL + pgvector + 每次操作的 LLM 调用。**

#### ③ Multilingual 分层解掉了 P71 的一个隐含矛盾

P71 现状同时要求：**Inbox 可中文**（低摩擦）**+ 正典强制英文**（`MEMORY_GUIDELINES.md:26`
+ `pre_commit_gate` 阻断 CJK），但**从未规定"谁负责翻译"**——triage 步骤里只有
「蒸馏进正典（英文 + 格式 + 索引）」这一句结果性描述，转换过程缺位。

分层后答案明确：**Capture 层不限语言（中文候选原样存），Canonical 层仍强制英文，
转换发生在 triage**。这与评委的表述一致，且补齐了 P71 的流程缺口。

### 10.5 Directives 为何**不采纳**（治理自相矛盾论证）

评委设想的映射是：

```text
AI_SYSTEM_GOVERNANCE  →  Hindsight Directive  →  Reflect
```

**该链条在治理上自相矛盾**，依据有二：

1. **Directives 只作用于 `reflect`**。官方文档两处明说：
   - "Directives **only affect the `reflect` operation**"
   - "Disposition traits and `reflect_mission` **only affect** the `reflect` operation"
2. **§4.3 硬约束已禁止 reflect 产生权威输出**：「reflect 结果不得直接成为
   Governance / Standard / Runtime Contract」。

即：**Directives 唯一能约束的通道，正是我们禁止其产生权威输出的那个通道。**
把治理规则映射过去，等于让治理依赖一个输出不可信的功能。

**Directives 对我们的净价值 ≈ 0**，但它反向印证了 §4.3 的正确性——
Hindsight 的三个 bank 级配置（`disposition` / `reflect_mission` / `directives`）**全部
只作用于 reflect**，这从外部证实了「reflect 是一个推理通道，不是一个知识写入通道」。

### 10.6 评分表修订

| Hindsight 能力 | 评委新评分 | 本提案判定 | 变化 |
|---|---|---|---|
| Knowledge Pages | ⭐⭐⭐⭐⭐ 重点研究 | 认同价值；**R1 冲突须先解决**；不改变 Option C | ↑（原 ⭐⭐⭐⭐，评委未提） |
| Memory Defense | ⭐⭐⭐⭐⭐ 硬需求 | **认同并升级为「我们自己的缺口」→ 建议自建** | ↑（原 ⭐⭐⭐⭐，评委未提） |
| Multilingual | ⭐⭐⭐⭐⭐ 直接缓解 P71 F1 | **完全采纳其分层表述**；解掉 P71 隐含矛盾 | ↑（原标注为取舍点） |
| Memory Banks | ⭐⭐⭐⭐⭐ | 维持 | = |
| Retain / Recall | ⭐⭐⭐⭐ | 维持 | = |
| Observation | ⭐⭐⭐⭐ | 降为「有价值但非第一优先级」（评委自行下调） | ↓ |
| Directives | ⭐⭐⭐⭐ 值得研究治理映射 | **不采纳**（§10.5）；反向印证 §4.3 | ↓↓ |
| Disposition | ⚠️ 必须隔离/限制 | 维持，并**加强**（三条 bank 配置全部只作用于 reflect） | ↓ |
| Reflect | ⭐⭐⭐ 只能作为候选推理 | 维持 | = |
| 替代 `ai-system` / 替代 P71 | ❌ 不建议 | 维持 | = |

**净变化**：评委上调的三项（Knowledge Pages / Memory Defense / Multilingual）**都不改变
Option C 的结论**——因为三项中两项可自建（§10.4-②），第三项有未解冲突（R1）。
评委下调的两项（Observation / Directives）**恰好都不影响我们的关键路径**。

### 10.7 追加到待裁定的两项

| # | 决策点 | 建议 |
|---|---|---|
| ⑥ | **secret + prompt-injection 门禁是否独立立项**（§10.4-①） | **是** —— 这是**我们自己的缺口**，与 Hindsight 无关；P71 的 Inbox 是 AI 自动写入的，正是注入入口。属 Fix 级，可先于 P71 落地 |
| ⑦ | **P71 链路是否显式写入「triage 负责语言转换」**（§10.4-③） | **是** —— 成本一行文本，补齐流程缺口 |

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| 外部评委 | **有保留的推荐** | 「有价值，但不要作为 Runtime 基础设施直接引入；定位为 Knowledge Memory Layer 候选实现」；评分 P71 9/10、Hindsight 7.5/10 |
| AI 二次评估 | **部分采纳 + 修正时间安排** | 认同定位（§1）；**不认同「下一阶段 PoC」**——顺序倒置（捕获产出 0，PoC 问题③无法回答）；提出 Option C 前置验证并追加触发条件 ④；补 4 条评委遗漏（其中 Memory Defense 是我们的硬需求、Disposition traits 是风险项）；指出评委 §8 文字与 §9 图自相矛盾；补 2 项未评估（LLM 成本、成熟度） |
| 外部评委（二次） | **上调两项 + 新增 Directives 论断** | 「Knowledge Pages + Memory Defense 与你们架构高度同构」；Knowledge Pages ⭐⭐⭐⭐⭐、Memory Defense ⭐⭐⭐⭐⭐（硬需求）、Multilingual ⭐⭐⭐⭐⭐（Capture/Canonical 分层）；新增 `Disposition`(how to reason) vs `Directive`(what must be obeyed) 之别，提出治理映射构想；Observation 下调为非第一优先级 |
| AI 三次评估 | **采纳 4 / 部分保留 1 / 不采纳 1** | 全部新论断一手核实通过（§10.2），Directives 的 strict 语义（**违反即响应被拒**）比评委描述更硬。**不采纳 Directives 治理映射**（§10.5：Directives 只作用于 reflect，而 reflect 正是 §4.3 禁止产生权威输出的通道——映射自相矛盾；且三条 bank 配置全部只作用于 reflect，**反向印证 §4.3 的正确性**）。**部分保留 Memory≠Knowledge 分层**（Knowledge 在我们体系里 = `standards`，硬加一层会重叠）。三项上调能力**不改变 Option C 结论**：两项可自建、一项有未解冲突。新增待裁定 ⑥⑦ |
| User | **Pending** | 需裁定 §9 的 ①②③④⑤ + §10.7 的 ⑥⑦ |
