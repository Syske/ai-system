# Skill 来源评估报告: mattpocock/skills — wayfinder

- 日期 / Date: 2026-08-17
- 来源 / Source: https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md
  （所属仓库：https://github.com/mattpocock/skills，35 个 skills，MIT, 活跃维护，最后提交 2026-08-17）
- 评估目标 / Target: `wayfinder`（附带整仓盘点）
- 评估框架 / Framework: `reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md`
  （2026-08-01 首轮已评估同仓库并吸收 grilling / diagnosing-bugs / writing-great-skills /
  codebase-design，借鉴 to-tickets / tdd / code-review / domain-modeling；彼时 wayfinder
  因"依赖 issue tracker"记为低价值。本报告对该项复审，因当前版已加入本地 Markdown tracker 回退。）

---

## 一、搜索先于吸收（Step 0）结论

- 本地资产检索（`skills/`, `governance/standards/`, `templates/runtime/`, `workflows/`）：
  - **无** "fog of war / decision ticket / frontier" 任何出现（grep 为空）。
  - 最接近的资产是 `skills/task-splitter`，但它是**规范之后的执行任务切片**（基于 OpenSpec 规范
    拆原子开发任务并排依赖）——不覆盖"构想太模糊、路线未知、远超单会话"的前置规划段。
  - `workflows/prepare → spec → develop` 链的前提是已有 Change Request；"松散构想 → 决策图"缺口真实存在。
- 远端检索（GitHub search 不可用，改用 web）：
  - wayfinder 是 mattpocock/skills 独有的成熟 skill（工程/目录，非 in-progress），
    有独立 docs 页（docs/engineering/wayfinder.md）与 ask-matt 路由入口；无本地或他库重复实现。
- 结论：**存在真实缺口**，按 Evolution Principle 进入评估吸收。

## 二、来源清单与分类统计

仓库 35 个 SKILL.md（engineering 18 / productivity 7 / misc 5 / in-progress 5）。
按参考价值分类（与 ai-system 现有资产叠加判断）：

| 价值 | 数量 | 清单 |
|---|---|---|
| 高价值（本次新增） | 1 | **wayfinder**（决策图 + 迷雾/前沿方法论） |
| 中价值（可借鉴） | 4 | research、prototype、to-spec、writing-for-agents |
| 低/无价值 | 30 | 详见第四节 |
| 已在 2026-08-01 吸收/借鉴 | 8 | grilling、diagnosing-bugs、writing-great-skills、codebase-design、to-tickets、tdd、code-review、domain-modeling |

## 三、wayfinder 深度评估（高价值候选 vetting）

### 3.1 内容与前端资料核验

- 前端内容（frontmatter + instructions）已通读（128 行）：把"远超单会话、路线被迷雾覆盖"的大块工作
  绘制为 issue tracker 上的**共享决策图（`wayfinder:map`）**，子 issue 即**决策工单（decision ticket）**，
  逐个解决直至路线清晰。
- 核心方法论：
  1. **决策工单 ≠ 执行工单**：工单内容是"待决策的问题"，不是可执行的构建切片；**规划默认，不做工**。
  2. **迷雾 vs 工单的判别测试**："现在能否精确陈述问题"——能则开单，不能则记入 **Not yet specified**
     （迷雾区），不可预切。
  3. **前沿（frontier）**：open + unblocked + unclaimed 子工单；认领 = 先赋值给自己；一次会话至多解一个工单。
  4. **HITL / AFK 分类**：research 归 AFK（并行子代理），prototype/grilling 归 HITL——
     HITL 工单只能通过与真人实时对话解决，禁止 agent 自问自答。
  5. **地图是指针而非仓库**：决策只存在于工单一处，地图只做索引与链接；按名称引用而非 issue 编号。
  6. **范围纪律**：目的地固定范围；超范围工作关闭并记入 Out of scope，永不"毕业"回前沿。
- 依赖面：调用 Skill 工具中的 grilling / domain-modeling / research / prototype（同仓库）
  ——而 grilling 与 domain-modeling 的要点**已在 2026-08-01 吸收进 ai-system**，
  故吸收 wayfinder 不需要连带吸收这四个依赖。
- 危险行为扫描：SKILL.md 与 agents/openai.yaml 中**无 shell 命令、无文件写入（除 tracker 外）、
  无网络调用、无凭据处理、无包安装**；纯提示词方法论。`disable-model-invocation: true`（仅用户显式调用）。
- 维护度：成熟 skill（2026-08-01 从 in-progress 毕业到 engineering，PR #464/#763 持续打磨，
  今天仍有提交、MIT、CHANGELOG 完整）。满足"high value = 填补真实缺口"。上限 10 名内：恰 1 名。

### 3.2 与 2026-08-01 首轮结论的差异

首轮记"依赖 issue tracker（我们无）→ 低价值"。当前版（CHANGELOG PR #472 之后）已改成：
**"若未提供 tracker，默认回退到本地 Markdown tracker"**——不依赖任何三方服务即可运行。
该反对理由不再成立；保留"fog vs ticket"部分适用性的判断并提升为整体吸收建议。

### 3.3 吸收形态建议（供 skill-policy 决策，本报告不执行吸收）

| 决策选项 | 落地建议 |
|---|---|
| 直接吸收 | 重写为 `skills/wayfinder/` 原生资产（本地 Markdown 图 + 决策工单规范），
  复用现有 grilling 2.5；不复制文件。 |
| 派生扩展 | 将 wayfinder 的"迷雾判别测试 + 决策工单 + 前沿"方法并入 `workflows/prepare.md`
  或 `skills/task-splitter`，作为规范前的"规划段"前置步骤。 |
| 新建 | 不推荐——无更贴近的本地或远端资产。 |

中价值借鉴点（按借用点）：research 的"高信任一手来源 + 落盘 Markdown"与 ai-system 知识工作流
理念一致；prototype 的"廉价具体工件抬高讨论保真度"可作 grilling 补充话术；
to-spec 的"seam 决策 + 仅综合不访谈"与 spec 工作流重叠提示；writing-for-agents 的
AGENTS.md/CLAUDE.md 写作纪律与 skill-author 重叠。

## 四、不吸收项及原因（全部 30 项）

| 类别 | 项 | 原因 |
|---|---|---|
| 已内化（2026-08-01） | grilling、diagnosing-bugs、writing-great-skills、codebase-design (4) | 已吸收为 skills/grilling、bugfix/feedback-loop、RFC-0002+skill-author、design-review vocabulary |
| 已借鉴（2026-08-01） | to-tickets、tdd、code-review、domain-modeling (4) | 已借鉴进 task-splitter T3、testing 标准、review smell-baseline、rfc/README+grilling 2.5 |
| 平台特定（Claude/TS 生态） | git-guardrails-claude-code、setup-pre-commit、migrate-to-shoehorn、setup-ts-deep-modules、setup-matt-pocock-skills (5) | 绑定 Claude Code hooks / TS 工具链 / 插件安装流程；ai-system 不用 |
| 依赖外部工具/平台编排 | triage、to-spec、to-tickets、ask-matt、wizard、claude-handoff、loop-me (7) | tracker 状态机/路由已有 aic-* CLI 与菜单替代；wizard 偏交互式环境；handoff/loop-me 为会话编排 |
| 个人写作/非本领域 | writing-beats、writing-fragments、writing-shape、teach、scaffold-exercises (5) | 内容创作与练习脚手架，非治理/运维领域 |
| 方法论纪律（非资产，不吸收） | research、prototype、implement、resolving-merge-conflicts、to-questionnaire、wait-what (6) | 通用纪律或轻量交互；ai-system 已有等效路径（spec/verify/知识工作流） |
| 会话交互话术 | grill-me、grill-with-docs、wait-what (3) | grilling 变体，已吸收核心；本地 _archive 已存旧版 grill-with-docs |

说明：中价值 4 项（research、prototype、to-spec、writing-for-agents）默认**不吸收**，
仅按 Evolution Principle 记录触发条件（下节），避免"它更好"式预先引入。

## 五、后续触发条件（不预先引入）

| 项 | 触发条件 |
|---|---|
| wayfinder 吸收（直接吸收或派生扩展） | 用户确认要对 wayfinder 决策图做吸收决策后，经 skill-policy 重写推进；落地前需先补一次实际"大块模糊构想"案例验证方法论适用性 |
| research / prototype 借鉴 | 若知识工作流或 grilling 出现"来源可信度失控"或"讨论保真度不足"的真实案例 |
| to-spec seam 决策 | 若 spec 工作流出现"该沿用既有决策结构却重新访谈"的偏差 |
| writing-for-agents | 若 skill-author 出现 AGENTS.md/CLAUDE.md 写作偏离案例 |
| setup-matt-pocock-skills 的 tracker 接线 | 若 ai-system 未来引入真实 issue tracker（当前无，维持本地 Markdown） |

## 六、决策选项（等待用户确认，本报告不执行吸收）

| 选项 | 含义 | 对 wayfinder 的适配建议 |
|---|---|---|
| 直接吸收 | 按匹配 skill 原样吸收（重写为原生资产） | 重写为 `skills/wayfinder/`，tracker 固定为本地 Markdown，issue 语义映射为 repo 内文件 |
| 派生扩展 | 复制最接近的 skill 修改之 | 并入 `workflows/prepare.md` / `skills/task-splitter` 作规划前段 |
| 新建 | 确认无相近匹配后全新构建 | 不推荐（有明确相似源） |

---

## 七、吸收决策记录（2026-08-17，用户确认直接吸收）

**决策**：直接吸收 wayfinder → 重写为原生资产 `skills/wayfinder/`，On-Demand 起步，
暂不绑定 workflow（Evolution Principle：等真实案例再评估升格）。

**落地形态**（重写为原生资产，不复制三方文件）：
- tracker 固定为 repo 内本地 Markdown（`.wayfinder/` 目录）
- 决策记录三层：地图=gist+链接索引 / 工单文件=完整问答 / 满足 rfc/README 三条件者晋升 ADR
- 核心方法论保留：决策工单≠执行工单、迷雾判别测试、frontier 认领=先赋值、HITL/AFK、一次会话一工单、超范围即关闭
- 明确复用已有 grilling（决策树访谈）生成工单，不重复实现

**变更清单**：新建 `skills/wayfinder/SKILL.md`、注册 `config/skill-groups.yaml`、索引 `skills/README.md`、落档本报告。

**执行状态**：2026-08-17 已执行（见下方执行记录）。

---

## 八、执行记录（2026-08-17 完成）

| 项 | 结果 | 验证 |
|---|---|---|
| 新建 `skills/wayfinder/SKILL.md` | 已重写为原生资产（本地 Markdown tracker、决策三层、复用 grilling） | grep 无三方逐字残留；frontmatter 合法 |
| 注册 `config/skill-groups.yaml` | 无需修改——local 分组为自动发现，wayfinder 自动落入 | 确认 local 分组为 source 自动扫描 |
| 索引 `skills/README.md` | On-Demand 表已追加 wayfinder | grep 命中 |
| 落档本报告 | 吸收决策 + 执行记录已入档 | 本节存在 |

- 变更文件：新建 `skills/wayfinder/SKILL.md`；修改 `skills/README.md`（索引）；修改本报告（补记录）
- 变更控制：L1（任务内新增原生 skill + 索引），不含 workflow/templates 改动（留 L3 待真实案例）
- 清理：临时克隆已于评估阶段删除

---

## 附：Sources / Evidence

- SKILL.md 全文: `tmp clone /mattpocock-skills/skills/engineering/wayfinder/SKILL.md`（128 行，已读）
- agents/openai.yaml: `allow_implicit_invocation: false`（已读）
- docs/engineering/wayfinder.md（已读: prerequisites / map-fog-frontier / invocation 决策矩阵）
- docs/engineering/setup-matt-pocock-skills.md（wayfinder 依赖接线说明，已读）
- CHANGELOG.md（PR #464 毕业、PR #472 tracker 回退、PR #763 决策工单命名，已读）
- 本地对照: ai-system skills/grilling、skills/task-splitter、workflows/prepare、templates/runtime
- 前轮框架: reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md（已读：评估框架与 wayfinder 前评）
- 临时克隆已删除（见清理记录）

---

## 九、复审与 TRIAL 终止记录（2026-09-17）

### 9.1 复审背景

08-17 决策直接吸收（On-Demand 起步）；08-25 按方案 A 登记 TRIAL（prepare/spec/develop 三处主链注入，
硬截止 08-30，判定标准：≥1 真实案例 + 决策图/工单产物 + ≥1 决策被 spec/develop 消费）。
截止逾期未评估，2026-09-17 用户要求重新评估并走 skill-source 流程处置。

### 9.2 复审判定（证据）

| 判定项 | 结果 | 证据位置 |
|---|---|---|
| OPTIMIZATION_LOG 实战记录（08-25 起强制） | **0 条** | skills/wayfinder/OPTIMIZATION_LOG.md 记录区 |
| `.wayfinder/` 决策图产物 | **0** | 全工作区 find |
| 被 spec/develop 消费的决策 | **0** | 无任何引用 |
| 08-30 硬截止评估 | 未执行（周维护逾期） | maintenance 记录 |

价值重评估结论：**低频高价值**——方法论要素大多已被 grilling / task-splitter / 确认纪律覆盖，
独有价值仅「跨会话持久决策图」；零案例不满足升格条件。详见
`reports/wayfinder-value-reevaluation-2026-09-17.md`。

### 9.3 处置决策（用户确认，2026-09-17）

| 项 | 动作 |
|---|---|
| 主链注入 | **终止 TRIAL 形态**：撤销 config/main-chain-capabilities.yaml 三处 TRIAL 条目（prepare/spec/develop）及头部注释 |
| skill 本体 | **保留 On-Demand**（skills/wayfinder/ 不动；菜单经 skill_roots 扫描可达，见 skills/README.md 索引） |
| OPTIMIZATION_LOG | 归档终止结论（零案例 → 未通过试用） |
| 升格条件 | 未来真实「跨会话大块模糊构想」案例 + 决策图被消费后再评估绑定 prepare |

**9.3b 最终处置修订（用户决策，同日）**：经第三方仓库复核（§五）、日常工作价值分析
（原则已由 grilling/task-splitter/指针纪律/E1-E4 吸收兑现，本体为低频备用）、阶段适配评估
（develop 等执行阶段错配，prepare 为唯一合理候选）后，用户决定：

| 项 | 最终动作 |
|---|---|
| **prepare** | **接入**（use-skill 方案，显式触发 desc：跨会话雾区构想 → 生成 .wayfinder/ 决策图；具体需求 → 明确跳过） |
| spec / develop | **保持终止**，不注入（雾区应在 spec 前解决） |
| 触发方式 | 显式判断句（非低显式度可选附注），解决前次 TRIAL 0 案例的入口错配问题 |
| 记录 | 实战使用后记入 skills/wayfinder/OPTIMIZATION_LOG.md |
| 升格条件 | 真实案例被 spec/develop 消费后再评估绑定更多阶段 |

**为什么不再需要试用（价值论证，2026-09-17 用户追问后补记）**：

1. TRIAL 已验证的结论 = **触发频率 ≈ 0**（23 天主链三阶段注入，0 案例；酷学院主链需求以具体
   Change Request / TR3/TR4 文档 / 工单进入，雾区场景本身稀缺，非提示注入方式问题）；
2. TRIAL 无法验证的 = 「低频高价值」——低频场景价值无法靠短期试用统计验证（样本量趋零），
   继续试用边际收益 ≈ 0；
3. 试用成本为负：三阶段注入 = 提示词噪音 + 记录管道维护；
4. 故保留形态 = **On-Demand 备用工具**（零成本，SKILL.md description 已写清触发条件，
   AI 遇雾区场景可手动调用），与低频高价值定位匹配。

### 9.4 执行记录（2026-09-17 完成）

| 项 | 结果 | 验证 |
|---|---|---|
| 撤销三处 TRIAL 注入 + 注释 | 已完成（终止 TRIAL 形态） | grep main-chain-capabilities spec/develop 0 命中 |
| **prepare 接入（use-skill）** | 已添加显式触发条目（skill/path/desc/enabled） | prepare 提示词含 /skills/wayfinder（测试断言恢复） |
| OPTIMIZATION_LOG | 终止结论 + 最终处置修订（prepare 接入） | 记录区 2026-09-17 条目 |
| skill 保留 On-Demand | 未改动 | skills/README.md On-Demand 表含 wayfinder |
| 门禁 | 全绿 | check.py PASS、lint、path-audit 0、单测 294 OK |

### 9.5 变更文件

- 修改 `config/main-chain-capabilities.yaml`（撤销 TRIAL 3 条目 + 注释；prepare 新增 use-skill 条目）
- 修改 `skills/wayfinder/OPTIMIZATION_LOG.md`（归档结论 + 最终处置修订）
- 修改 `skills/wayfinder/SKILL.md`（补 Refer by name 纪律）
- 修改 `cli/tests/test_maintain_tools.py`（断言恢复 skills/wayfinder 绝对路径）
- 修改本报告（补记录）
- 新增 `reports/wayfinder-value-reevaluation-2026-09-17.md`（价值重评估 + 第三方复核 §五）

### 9.6 变更控制

L1（配置/文档级撤销 + skill 未动），无 workflow/templates 改动。