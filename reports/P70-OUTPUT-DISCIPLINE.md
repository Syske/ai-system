# Change Proposal: P70 — AI 输出纪律（Output Discipline：回复文本 · 阶段形态 · 子代理契约）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural（治理条款 + 阶段形态契约 + 子代理输出契约；**不引入外部项目/工具/命令**） |
| Author | AI Maintainer |
| Created | 2026-09-23 |
| Reference | 用户 2026-09-23 提供的外部评估（`github.com/Karnonson/caveman` + 四条吸收建议）；本仓「输出与上下文治理」现状侦察（§1.2）；`reports/P49-*`（代码返回值粒度，非本主题）· `reports/P59-*`（模板折行≠token 优化，反证见 §3.3） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 一句话

本仓对「**输出应该包含哪些字段**」契约化程度很高，对「**输出不该包含什么（复述/旁白/填充）**」几乎无 binding 规则；
按阶段区分的**回复形态**与**子代理输出契约**则完全空白。结果是 token 与注意力花在"把已经写进产物/需求/账本的内容再复述一遍"。

### 1.2 现状核查（本仓实证，全部带位置）

| 方向 | 现状 | 证据 |
|---|---|---|
| **A 回复简洁/去废话** | **几乎无 binding 规则**。唯一"简洁"轴是反思自评（可选）：`governance/REFLECTION_RULES.md:81`「Conciseness — minimum words/tokens?」；明确的"禁止赞美/复述摘要"只存在于盲检判官 prompt（`templates/prompts/external-blind-review.md:29`），作用域仅限盲检 | `AI_OPERATING_RULES.md:205` 管的是"别老追加答后提示"，非正文简洁 |
| **A 结构契约（对照面）** | 很完整：Completion 六段（`AI_OPERATING_RULES.md:360-366`）· 决策点单行理由（`AI_USER_RESPONSIBILITY_CONTRACT.md:163`）· 报告头一行结论（`governance/outputs-convention.md:51`）· Runtime Result 字段（`runtime-base.md:239-253`） | 有"必须含什么"，**没有"必须多短 / 不该重复什么"** |
| **B 按阶段输出形态** | **全部为"部分"**：各 runtime 只有字段清单（`runtime-prepare.md:280`、`runtime-spec.md:467`、`runtime-bugfix.md:379`、`runtime-release.md:625`）；`develop` 与 `review` **无形态约束**（没有"Changed/Verified/Blocked"，没有"Findings + file:line"） | 字段 ≠ 形态 |
| **C 上下文压缩** | **策略与仪器都已具备**：`CONTEXT_LOADING.md`（最小化加载 + 40/60/80 健康度 + Context Budget）· `CONTEXT_RETENTION.md`（Keep/Drop）· `ATTENTION_MANAGEMENT.md`（衰减信号）· `tools/context-audit.py`（会话 token 审计）· `tools/prompt-metrics.py`（提示词体积 + 前缀稳定性） | 缺：**"只压缩表达、不压缩约束与事实"的明文原则**；缺**定期整体审计的整合入口**（仪器有，没被定期调用） |
| **D 子代理输出契约** | **无**。全仓仅 `CONTEXT_LOADING.md:179` 一行「subagent isolation (pi-worker style) \| returns conclusions only」；外部盲检双判官是唯一"多角色 + 各自输出格式"的落点 | 每次派发 worker 的提示词**当场重写**（本会话即如此），无复用契约 |

### 1.3 浪费的实际形态（本会话可直接指认）

1. **复述用户输入**：把用户刚给的需求/报告再概括一遍再回答（信息增量为零，且引入转述误差）。
2. **复述既有产物**：把已写进 `reports/*.md` / 诊断日志 / 交接文档的内容在回复里重讲一遍（本会话多轮如此）。
3. **整段搬运工具输出**：长 grep/find/测试输出直接铺进会话（`CONTEXT_RETENTION` 已要求 Drop 原始输出，但无"回复层"约束）。
4. **worker 提示词重复发明**：每次派发子代理都重写一遍"只要结论、带证据、别贴原文"，无标准契约。

## 2. 外部对象核实（Caveman —— 先核实，再判定价值）

**是什么**（MIT；`install.sh`/`install.ps1` 一键安装，Node ≥18）：面向 30+ 编码 agent 的 skill/plugin，
核心是**提示词/persona 层**：让 agent 用"caveman-speak"压缩**回复文本**。附带命令
`/caveman [lite|full|ultra|supra|silence]`、`/caveman-commit`（≤50 字符 subject）、`/caveman-review`（单行 PR 评论）、
`/caveman-stats`（读会话日志统计省下的 token，写 statusline badge）、`/caveman-compress <file>`（把记忆文件
改写成 caveman 体，代码/URL/路径字节保留）、`caveman-shrink`（MCP 中间件：压缩工具描述）、
`cavecrew-*`（investigator/builder/reviewer 子代理）。

**它自己声明的边界**（重要）：只影响 **output token**，thinking/reasoning 不动；不改代码、命令、错误字符串；
不做上下文/模型本身。

**它给出的量化证据（均为 README 自报，未获独立复现）**：10 条提示实测平均输出 token **-65%**（区间 22–87%）·
记忆文件压缩平均 **-46%** · 标题宣称 **~75%**（高于自报基准均值 → 属宣传口径）。

**它引用的外部研究（本次已核实为真）**：arXiv **2604.00025**《Brevity Constraints Reverse Performance
Hierarchies in Language Models》—— 31 个模型（0.5B–405B）/ 1,485 题 / 5 数据集；大模型因"随规模增长的冗长"
在 **7.7%** 题目上落后小模型 **28.4 个百分点**，施加简洁约束后反转。
**两点偏差需记明**：① README 称"26 点"，论文摘要为 **28.4 个百分点**（口径不一致）；② 该论文测的是
**基准推理准确率**，与"聊天回复风格压缩"是**类比关系而非直接证据**——不能据此声称"回复变短就能提准确率"。

## 3. 价值判定（逐条核实用户报告的四条建议）

### 3.1 Output Compression（AI 文本输出）—— **采纳，但限定形式**

- **缺口真实**（§1.2-A）：我们只规定了"必须含什么"，没规定"不该重复什么"。
- **不采纳的部分**：不追求 -75%/-65% 这类指标，不采用"电报体"。本仓回复承载**强制契约**
  （Completion 六段、Task Card、证据、风险、裁决请求），压缩成碎片会直接摧毁可审计性 —— 与
  `AI_OPERATING_RULES.md:58`「Never hide uncertainty / skip verification」冲突。
- **采纳的形式 = 内容级纪律**：禁止**复述**（用户输入 / 既有产物 / 工具原始输出）· 禁止**旁白**（"接下来我要…"
  "分析一下→总结一下"）· 禁止**填充语**（赞美、客套、"如前所述"式重述）；**必须保留**：结论、证据
  （file:line）、裁决请求、验证结果、不确定性。

### 3.2 Workflow-specific Output（阶段形态）—— **采纳**

- 缺口真实（§1.2-B）。落点与用户判断一致：**放进既有 runtime，不新增技能**。
- 形态建议（每阶段一条，**不得取代**已强制的字段契约）：`develop` → Changed / Verified / Blocked；
  `review` → Findings 优先（file:line + 严重度 + 建议）；`bugfix` → Root Cause / Fix / Verification；
  `prepare`/`spec` → 结论 + 指针（详细内容进产物）。

### 3.3 Context Compression（上下文压缩）—— **大部分已具备；只补两点，且不做"改写式压缩"**

- **已具备**：三件套（LOADING/RETENTION/ATTENTION）+ 两个仪器（`context-audit.py` 会话 token 审计、
  `prompt-metrics.py` 提示词体积/前缀稳定性）+ R3 已完成的治理去重收口。
- **反证（本仓实测）**：`reports/P59-*:19` 已测过"模板折行优化"仅省 **41 字符（0.031%）** →
  **我们的文档已经是密写的**，"压缩改写"收益很小；真正的浪费在**重复**与**加载面**，不在措辞啰嗦。
- **只补两点**：① 明文原则「**只压缩表达，不压缩约束与事实**」（落到 `CONTEXT_RETENTION.md` 的 Keep/Drop 旁：
  压缩/摘要**不得删**约束、阈值、契约、事实，只能删复述与修饰）；② 把既有仪器**定期化**（下次巡检跑
  `prompt-metrics` + `context-audit`，看趋势而非追求数字目标）。
- **不采纳**：把治理文档改写成 caveman 体（收益小 + 破坏可读性与语言门禁）。

### 3.4 Tool / Subagent Output Contract —— **采纳（新契约，最便宜的一块）**

- 缺口真实（§1.2-D）：唯一一行 `CONTEXT_LOADING.md:179`；worker 提示词靠当场重写（§1.3-4）。
- 采纳形式：**一个可复用契约**（只回结论 · 每条结论带证据 file:line 或一行引文 · 显式标注"不可判定/未查证"
  · 不贴原文/不转述全文 · 固定输出小节），供派发子代理时引用。

### 3.5 明确排除

| 排除项 | 理由 |
|---|---|
| 引入 Caveman 本体（installer / 命令体系 / statusline / cavecrew 子代理 / MCP 中间件） | 与 §1.2 的既有能力重复；命令面不是我们的短板；安装器与 statusline 绑定特定 agent（Claude Code），跨 agent 不稳 |
| 追求 -75% / -65% 输出 token 指标 | 与本仓强制报告契约冲突；且是他人自报口径，未独立复现 |
| 用"电报体"改写治理文档 | §3.3 反证：折叠措辞仅省 0.031%；且破坏语言门禁与可读性 |
| 照搬 `/caveman-commit`、`/caveman-review` 命令 | 我们的提交规范（`commit-content.md` + P62）与评审 findings 格式**已存在**，缺的是"回复形态"而非命令 |
| 把"简洁"升级为新的门禁 | 无客观判据（会退化成字数门禁，逼出"为过门禁而删信息"）；本提案保持**条款 + 形态**层面 |

## 4. Recommendation

**采纳 §3.1 + §3.2 + §3.3（两点） + §3.4**，即"输出纪律三落点"，全部为**文本/契约级**改动：
不新增工具、不新增技能、不新增命令、不引入外部项目。

### 4.1 待裁决清单（每条带建议）

| # | 待裁决 | 建议 |
|---|---|---|
| 1 | 落点形态：新建 `governance/standards/common/output-discipline.md`（~40 行）并登记 `standards-loader` 的 **Always Load**，还是塞进 `AI_OPERATING_RULES.md`？ | **新建独立小标准**（单一来源；AI_OPERATING_RULES 已长，避免混职责）。代价 = 每次运行多 ~300 token，远小于去废话的收益 |
| 2 | 阶段形态改哪几个阶段 | 先改 **develop + review**（浪费最集中），`bugfix`/`prepare`/`spec` 视效果再扩 |
| 3 | 子代理契约放哪 | `templates/prompts/worker-contract.md`（可复用片段）+ `CONTEXT_LOADING.md:179` 那一行改成指向它 |
| 4 | 是否同时补 §3.3 的两点 | **补**（一行原则 + 巡检定期跑既有仪器），成本近零 |
| 5 | 要不要设"输出 token 下降 X%"的目标 | **不设**。只做**趋势观察**（`prompt-metrics` / `context-audit` 前后对比），避免为数字而删信息 |

### 4.2 实施成本实测（2026-09-23 量取，非估算）

**基线**：`Always Load` 7 个文件合计 **1,399 行 / 42,081 字节 ≈ 10.5k token**；
`tools/prompt-metrics.py` 显示全量提示词 146,646 字符 ≈ 36,661 token（前缀稳定 16/16）。

| 落点 | 一次性改动 | **每次运行固定 token 增量** | 说明 |
|---|---|---|---|
| Q1-A 新标准文件（**中文** 40 行） | +1 文件；3 处编辑（loader 登记 / 盲检 prompt 改引用 / 指示） | **+1,000 ~ +1,400 tok**（≈ Always Load 的 10–13%） | 中文 1 字符 ≈ 1 token，英文 ≈ 4 字符/token → **同一内容中文版贵 ~7 倍** |
| Q1-A′ 新标准文件（**英文简写** 35 行） | 同上 | **+400 tok**（≈4%） | 与 `clean-code.md` 同风格（英文、极简） |
| Q1-B 不新建，扩 `ai-coding-rules.md`（+12 行英文） | 2 处编辑 | **+135 tok**（≈1.3%） | 最省，代价：输出纪律与"编码规则"混居一个文件 |
| Q2 阶段形态（develop + review） | 2 个 runtime 各 +1~2 行（**必须英文**，Rule 4 英文纪律区） | **0**（仅该阶段 +~50 tok） | 无长度门禁（100 行门禁只管 `workflows/` 与 `cli/commands/aic-*.md`） |
| Q3 worker 契约 | +1 提示模板（~30 行，英文，与同类一致）+ 1 行指向 | **0**（只在派发子代理时加载） | `templates/prompts/` 不在 Rule 4 范围 |
| Q4 上下文两点 | 1 行（`CONTEXT_RETENTION.md`）+ 巡检登记 1 条 | **0** | `CONTEXT_RETENTION` 不在 Always Load（压缩时才读） |

**合计（最小方案 = Q1-B + Q4）**：2 处编辑 · **零新增文件** · **+135 tok/run** · 1 个提交。
**合计（推荐方案 = Q1-A′ + Q2 + Q3 + Q4）**：3 个新文件（1 标准 + 1 提示 + 0，其中标准英文简写）·
6 处编辑 · 约 110 行 · **+400 tok/run** · 3 个提交 + 1 个验证步骤。

**非行数成本（须计入）**：
1. **零可执行改动** → 609 个单测不受影响、无需新测试；门禁只需重跑（`check.py` / `repo-lint` /
   `path-audit` / `check-contract` / `proposal-audit`）。
2. **无孤儿门禁**：本仓**没有**"标准必须被 loader 登记"的检查 → 新标准靠人记得登记（+1 维护面）。
3. **效果不能立即证明**：与 P69 同源——纪律落地 ≠ 立刻少 token，需要观察窗口（`prompt-metrics` /
   `context-audit` 前后对比）。可立即证明的只有"固定成本 +400 tok"这一笔。
4. **注意力成本**：§4.1 五项裁决（若走 Q1 先行可先只裁 1 项）。
5. **回归面**：Q1 会把盲检 prompt 的同类条款改为引用（净 −2/+1 行），须确认盲检输出结构不变。

**成本结论**：整体属**轻量文本级改动**（无工具、无命令、无测试面），唯一持续成本是 Always Load 增量；
把标准写成**英文简写**可把它从 ~1,200 tok 压到 ~400 tok/run。建议**分两批**：先 Q1-A′ + Q4（1 提交，
固定成本 +400 tok），观察后再决定 Q2/Q3。

## 5. Proposed Changes（按优先级）

| 阶段 | 内容 | 落点 |
|---|---|---|
| **Q1 输出纪律本体** | 禁止三件事（复述 / 旁白 / 填充语）· 必须保留五件事（结论 / 证据 / 裁决请求 / 验证结果 / 不确定性）· 与盲检 prompt 的"不要复述"统一为同一口径（盲检改为引用本标准） | `standards/common/output-discipline.md`（新）+ `standards-loader` Always Load + `external-blind-review.md` 改引用 |
| **Q2 阶段形态** | `develop`：回复只给 Changed / Verified / Blocked（细节进产物与诊断日志）；`review`：Findings 优先（file:line + 严重度 + 建议），不重复被审内容；各加一条但**不改**既有 Completion 字段 | `templates/runtime/runtime-develop.md` · `runtime-review.md` |
| **Q3 子代理输出契约** | 结论制 · 证据制 · 显式不可判定 · 不贴原文 · 固定小节 | `templates/prompts/worker-contract.md`（新）+ `CONTEXT_LOADING.md:179` 指向它 |
| **Q4 上下文原则 + 仪器定期化** | 「只压缩表达，不压缩约束与事实」一行；巡检条目：定期跑 `prompt-metrics` / `context-audit` 看趋势 | `CONTEXT_RETENTION.md` + `config/maintenance.yaml`/巡检清单 |

## 6. Validation Plan

1. **不损契约（首要）**：改动后跑全门禁；用 `tools/check-contract.py` 确认 workflow↔runtime 输出契约未漂移；
   跑一次真实任务，检查 Completion 六段与产物落盘**一个字段都没少**（收缩的是回复，不是产物）。
2. **去废话可观察**：同一任务在改前/改后各做一次，比较 `tools/context-audit.py` 的会话 token 与
   `tools/prompt-metrics.py` 的提示词体积（**只记录趋势，不设目标值**）。
3. **口径统一检查**：盲检 prompt 由"不要复述"改为引用新标准后，验证盲检结论格式未变（可对比上一轮盲检报告结构）。
4. **子代理契约有效性**：派发同一探索任务两次（有/无契约），比较返回长度与"是否带 file:line 证据"。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| **为简洁而丢信息**（最严重） | 标准写明"必须保留五件事"；只禁复述/旁白/填充；不设字数门禁；验证步骤要求逐字段核对 |
| 与既有 Completion/Runtime Result 契约冲突 | Q2 明确"**不改**既有字段，只加'不要重复'的形态要求"；`check-contract.py` 兜底 |
| 又一处"输出规范"造成多来源 | 盲检 prompt 的同类条款改为**引用**新标准（不复制）；`outputs-convention.md`（产物）与新标准（回复）职责划分写明 |
| Always Load 增加上下文成本 | 控制 ≤40 行；用 `prompt-metrics` 实测增量并记录（预期 ~300 token，一次性） |
| 阶段形态把控制流压没了 | 形态只管"回复呈现"，控制流（Phase/确认点/停止条件）不动 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户要求评估 caveman 并"必要时立新提案"；§4.1 五项待裁定） | 2026-09-23 |

## Implementation Record

*(待实施后填写)*