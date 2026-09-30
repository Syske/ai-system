# Reports Index

集中索引 `reports/` 下所有分析、维护、提案、迁移与规范文档，便于查找与跟进待办。

- 每项一行：类型 / 主题 / 日期 / 文件 / 遗留待办。
- 提案（P 系列）状态与门禁见 `PROPOSALS.md`（proposal-audit 维护，勿手工改状态）。
- 新报告入目录即登记；本文件不参与 proposal-audit 门禁。

---

## 分类与归属

`reports/` 只放**AI 系统自身的分析与治理记录**，不是任何其他产品交付物的存放地。

**业务产物应落**：工作流自身产物 → `outputs/<workflow>/<yyMMdd>-<descriptor>/`；
项目变更产物 → `workspaces/<project-id>/…`（按 workflow 的 Outputs 段）；
机器本地运行记录 → `<workspace>/logs/`、`<workspace>/metrics/`。

> 反例（2026-09-28 处置）：某第三方产品的 7 份 `prepare` 业务报告以一次
> `chore:` 提交进入 `reports/`，并被完整登记进索引——**所有既有门禁均未告警**，
> 因为 §6 只要求报告「被登记」，从不校验它「是否属于这里」。那是一份零引用、
> 无对应工作区项目、仅一次提交后再无改动的孤儿产物。

**类别与命名**（门禁 `tools/checks/reports_scope.py` 强制，check.py 第 17 项）：

| 类别 | 命名模式 | 示例 |
|---|---|---|
| `proposals` | `P<编号>-<主题>.md` / `<主题>-PROPOSAL.md` | `P76-PHASE-CONTRACT.md` |
| `maintenance` | `MAINTENANCE-<日期>[-<范围>].md` / `DAILY-<日期>.md` | `MAINTENANCE-2026-09-28.md` |
| `assessments` | 含 `ASSESSMENT`/`REVIEW`/`DIAGNOSIS`/`ANALYSIS`/`REEVALUATION`/`OPTIMIZATION`/`REPORT`/`HANDOVER`（不区分大小写） | `ARCHITECTURE-ASSESSMENT-2026-07.md` |
| `incidents` | `INCIDENT-<日期>-<主题>.md` | `INCIDENT-2026-09-24-ignored-state-wipe.md` |
| `migrations` | `MIGRATION-<主题>.md` | `MIGRATION-PLAN-v2.md` |
| `decisions` | `VALUE-BURDEN-DECISION-<主题>.md` | `VALUE-BURDEN-DECISION-skill-sync-2026-09-23.md` |
| `standards` | `EXTENSION-STANDARDS*.md` | `EXTENSION-STANDARDS.md` |
| `analysis` | `analysis-<日期>-<主题>/`（目录） | `analysis-2026-08-01-structure-governance/` |
| `skill-sources` | `skill-source-<日期>-<技能>/`（目录） | `skill-source-2026-08-17-wayfinder/` |

顶层索引文件 `README.md` 与 `PROPOSALS.md` 豁免。

**分类按白名单而非排除法**——首段是 workflow 名无法作为判据（`analysis-*` 既是类别
也是 workflow 名，而 `prepare-<项目>-*` 是工作流的业务产出，两者首段同类）。

**本文件与 `PROPOSALS.md` 的职责**：本文件是全量分类索引（按报告类型分节）；
`PROPOSALS.md` 只管 P 系列提案的状态机，状态由 proposal-audit 维护。

详细规则见 `governance/policies/proposal-policy.md` §6.1。

---

## 提案（P 系列）

状态与门禁见 [PROPOSALS.md](PROPOSALS.md)，此处仅列主题索引：

| 提案 | 主题 | 日期 |
|------|------|------|
| [P6](P6-SKILL-SIZE-PROPOSAL.md) | Skill Size Reconciliation | 2026-08-01 |
| [P7](P7-WORKFLOW-AUTHOR-COMMAND.md) | `aic-workflow` Authoring Command | 2026-08-05 |
| [P8](P8-COMMAND-AUTHOR.md) | `aic-command` Authoring Command | 2026-08-05 |
| [P9](P9-SKILL-LAUNCHER.md) | `aic-skill-launch` Skill Launcher | 2026-08-05 |
| [P10](P10-SKILL-OPTIMIZER-SPLIT.md) | skill-optimizer 脚本拆分（超限文件 + 双入口去重） | 2026-08-06 |
| [P11](P11-SKILL-OPTIMIZER-ABSORPTION.md) | skill-optimizer 网络思想吸收（held-out 门控/demo-augment/description 调优） | 2026-08-06 |
| [P12](P12-LANGCHAIN-REMOVAL.md) | 移除 langchain 依赖（openai SDK 直调） | 2026-08-06 |
| [P13](P13-DEPENDENCY-CYCLE-CLEANUP.md) | 破除 3 个 Skill 依赖环（检测器语义分层） | 2026-08-06 |
| [P14](P14-SNAPSHOT-GOVERNANCE.md) | 跨服务 SNAPSHOT 治理纪律（S4） | 2026-08-06 |
| [P15](P15-MULTISKILL-GUARD.md) | 多-SKILL.md 输入防护（E3 缺陷修复） | 2026-08-06 |
| [P16](P16-STATE-WRITE-GUARD.md) | wizard 状态写入增加项目存在性校验（S2 根因修复） | 2026-08-08 |
| [P17](P17-MAVEN-DELEGATION-GOVERNANCE.md) | java-maven 委派规范（D1 根治） | 2026-08-08 |
| [P18](P18-THIN-COMMAND-SLIMMING.md) | aic-apply / aic-explore 命令瘦身（thin-command 门禁） | 2026-08-08 |
| [P19](P19-EXPLORE-SKILLS-RELATIONSHIP.md) | explore 与 explore-codebase 技能关系澄清（季度评估合并） | 2026-08-08 |
| [P20](P20-HOTFIX-TEST-DOC-GUARDRAILS.md) | hotfix-test-doc 发布链护栏增强（校验误报 + 空单元格自动修复） | 2026-08-11 |
| [P21](P21-HOTFIX-TEST-DOC-RENDER-FIX.md) | hotfix-test-doc 模板标题渲染缺陷修复与回填工具 | 2026-08-12 |
| [P22](P22-WSL-ENVIRONMENT-INTEGRATION.md) | WSL 环境集成与初始化能力 — **Implemented**（2026-09-21 状态同步；2 项遗留转 checkbox 跟踪） | 2026-08-14 |
| [P24](P24-PROVIDER-CONTRACT-TEST-FIX.md) | Provider Wizard 契约测试夹具修复（win32 平台 check.py 回归，已实施 exit 0） | 2026-08-17 |
| [P25](P25-WORKFLOW-FRONTMATTER-SYNTAX.md) | 统一 Workflow 资产语法为 SKILL.md frontmatter 约定（Implemented） | 2026-08-20 |
| [P26](P26-MAIN-CHAIN-BRANCH-RULE.md) | 开发主链分支创建规则（cc{date}_ipd_{desc}_{service} 暂定）+ 不可变（Proposed） | 2026-08-20 |
| [P28](P28-CHANGE-ID-GENERATION.md) | Change ID 自动生成（规则 slug 派生优先，AI 可选后续） | 2026-08-21 |
| [P29](P29-HOME-ENV-CONFIG.md) | 机器层环境配置迁移至 ~/.config（跨平台原生，首启按系统生成）— **Implemented**（2026-09-21 状态同步） | 2026-08-23 |
| [P30](P30-PROMPT-ROOT-PLACEHOLDERS.md) | 提示词渲染期解析根路径占位符（{workspace_root} 等，模板零改动）— **Implemented** | 2026-08-23 |
| [P31](P31-STANDARDS-COOL-MIGRATION.md) | standards/cool 公司规范迁出通用层（extensions + loader 可配置）— **Implemented** | 2026-08-23 |
| [P32](P32-PREPARE-OUTPUTS-LOCATION.md) | prepare 工作流子报告输出位置与 AGENTS.md 约定对齐（outputs/prepare→workspace-anchored）— **Implemented** | 2026-08-24 |
| [P33](P33-ISSUE-CAPTURE-CONTEXT-LOADING.md) | 日常运行中发现变更时的上下文加载触发规则（Issue Capture：JIT 加载 proposal-policy + OPERATIONS §12 + 尺寸分流）— **Implemented** | 2026-08-24 |
| [P34](P34-MAINTENANCE-STATE-INTO-GIT.md) | maintenance 状态纳入 ai-system 提交（拆分：系统级 maintenance 块 → config/maintenance.yaml 入 git，机器级留 workspaces 本地）— **Implemented** | 2026-08-24 |
| [P35](P35-PYTHON-INTERPRETER-ROBUSTNESS.md) | python 解释器鲁棒性（命令文档统一 python3 + 工具调用鲁棒化）— **Implemented** 2026-09-01 | 2026-08-24 |
| [P38](P38-WORKFLOW-INTERACTION-AUDIT.md) | 逐 aic 工作流用户交互审计（wizard 提示序列/确认节奏/可选字段呈现/中途检查点；与 P37 互补：P37 定必填归属、P38 定交互呈现）— **Implemented**（批次 1；批次 2 defer：全推导字段静默推导等） | 2026-08-25 |
| [P39](P39-EXTENSIONS-LINT-HIDDEN-DIRS.md) | extensions-lint 隐藏目录误判为扩展（--fix-missing-log 向 .git/.githooks 写入脚手架；修复：枚举过滤 `.` 开头目录）— **Implemented** | 2026-08-25 |
| [P40](P40-OPENSPEC-CHANGE-NAME-NAMING.md) | OpenSpec-CN change name 字母开头约束与 workspace `<YYYYMM>-` 命名惯例冲突（openspec changes 目录用字母开头，workspace 目录不变 + 映射注明）— **Implemented** | 2026-08-25 |
| [P60](P60-GATE-SELF-VERIFICATION.md) | 门禁自校验：声明 vs 收集测试数一致性 + 关键声明式规则正反例自测 + 显式相对引用存在性 — **Implemented** 2026-09-21（`2adcf4a`，三项「弄坏→必报」实证） | 2026-09-21 |
| [P61](P61-EXTERNAL-BLIND-REVIEW-AS-MAINTENANCE.md) | 外部盲检纳入运维形式：新工作流/命令 + 盲检纪律入库 + 季度节奏（补内部门禁盲区）— **Implemented** 2026-09-21（6 件产物 + 卫生门禁化 + 4 处自抓问题） | 2026-09-21 |
| [P41](P41-TR5-SECTION1-SEMANTICS.md) | tr5 脚本健壮性批次：§1 语义特判 + §18 工时 4-8h 自动校验 + tr4_url 技改降级 info（服务名正则项已失效）— **Implemented** 2026-09-21（extensions 6d8a176） | 2026-08-26 |
| [P42](P42-TR5-TEMPLATE-SKELETON.md) | tr5 templates 缺 markdown 骨架（新增 19 节骨架模板 + SKILL 拷贝指引）— **Proposed（用户确认 defer 至 tr5 专项会话 2026-09-21；接手要点已备妥）** | 2026-08-26 |
| [P43](P43-TR5-SECTION0-INLINE-BODIES.md) | tr5 §0 数据槽位恒空（`_split_section0` 不识别头行内联正文 → 0_1/0_2/0_3 恒空且 merge 僵尸保留 → 发布页 §0 露引导占位符；推荐解析器支持 inline）— **Implemented** | 2026-08-28 |
| [P44](P44-WORKTREE-CONVENTION.md) | Worktree 约定完善（项目级隔离 + 生命周期管理）— **Implemented** | 2026-08-31 |
| [P45](P45-RUNTIME-LANGUAGE-GATE.md) | 运行时语言门禁（completion-time language gate，方案 B 正式化）— **Implemented** 2026-09-01 | 2026-09-01 |
| [P46](P46-TR5-DEBT-VALIDATION-MARKER.md) | tr5 发布债收口（check_tr5 8 FAIL）+ review/verify 验证标记检查 — **Proposed** | 2026-09-01 |
| [P48](P48-CONFIG-DEFAULT-SOURCING.md) | 配置默认值治理（@Value 单一默认源 + 对象化；L1 已实施，L2 配置 POJO 化待季度窗口）— **Proposed** | 2026-09-04 |
| [P49](P49-RETURN-GRANULARITY-REUSE-CHECKLIST.md) | 返回值粒度可区分性 + 非必要不新增实体/方法 + 实现层复用核验（清单三落点）— **Implemented** 2026-09-09 | 2026-09-09 |
| [P50](P50-METHOD-GRANULARITY-DUAL-CONFIRMATION.md) | 方法粒度双确认模型（开发主链前置方案确认 + 后置一致性确认，条件式触发）— **Implemented** 2026-09-09 | 2026-09-09 |
| [P51](P51-JDT-GATE-INCREMENTAL-DIFF.md) | format-jdt-gate 增量差分语义（hunk × 改动行交集，存量豁免+新增拦截）— **Implemented** 2026-09-09 | 2026-09-09 |
| [P52](P52-SOFA-POWERMOCK-TEST-CONVENTIONS.md) | SOFA/PowerMock/jacoco 测试兼容性纪律 + 全量回归环境性基线登记 — **Implemented** 2026-09-09 | 2026-09-09 |
| [P55](P55-METHODOLOGIES-REMOVAL.md) | methodologies 整体移除（资产迁入 ai-system） | 2026-09-17 |
| [P56](P56-SENSPEC-VALUE-ABSORPTION.md) | SenSpec 价值吸收上链（来源路径已脱敏） | 2026-09-17 |
| [P57](P57-SCAN-SERVICE-SELECTION.md) | scan 命令 service 级选择 + 字段收集死循环出口（参照 code-review 交互流程）— **Implemented** 2026-09-21 | 2026-09-21 |
| [P58](P58-PROJECTS-REPOSITORIES-ONDELIVERY.md) | projects/ 真实目录 + repositories 源按需 clone（消除软链/双副本）— **Implemented** 2026-09-21 | 2026-09-21 |
| [P59](P59-TEMPLATE-AUTHORING-DISCIPLINE.md) | 模板层作者纪律（折行≠token 优化；实测收益 0.03% → 回退）— **Implemented** 2026-09-21 | 2026-09-21 |
| [P54](P54-DEDUP-PLANNING.md) | 消除双重计划（implement Stage 2 复用已确认计划，每卡省 1 次推断+确认）— **Implemented** 2026-09-09 | 2026-09-09 |
| [P47](P47-WORKFLOW-PRECONDITIONS-OUTPUTS.md) | develop 前置处理规则与产物目录约定（前置不满足→先跑 dev-setup；完成报告落 completion-reports/）— **Implemented** 2026-09-02 | 2026-09-02 |
| [P36](P36-SETUP-ENV-INIT-SCAFFOLD.md) | 初始化脚本完善（--env-init 补齐目录骨架 + 引导指定外部代码仓库；2026-09-03 增补触发层：aic 首次运行只读检测+交互确认，否决静默自动）— **Proposed** | 2026-08-25 |
| [P37](P37-REQUIRED-INPUTS-TRIAGE.md) | 工作流必填参数必要性评估（降可选/自动推导/保持，提升使用效率）— **Proposed** | 2026-08-25 |
| [P64](P64-SPEC-PRECONDITION-CONSISTENCY.md) | spec 前置条件口径不一致（"Prepare completed" 无 SSOT + 实测 0/12 变更具备 prepare 产物 + proposal.md 静默替代）— **Implemented**（SSOT 落 `prepare.md` → Exit Criteria → Completion Criteria；删恒真替代；skip/遗留/祖父三条分支；存量 0 STOP） | 2026-09-23 |
| [INCIDENT-2026-09-24](INCIDENT-2026-09-24-ignored-state-wipe.md) | **事故复盘** —— 一条 `git clean -fdx` 清空仓库内未跟踪/被忽略状态（约 200 份运行日志不可恢复；版本化资产零损失）；含 5 Whys 根因链、影响与恢复、四条教训（护栏见 P72） | 2026-09-24 |
| [P77](P77-HINDSIGHT-EVALUATION.md) | Hindsight 评估：Experience Knowledge Layer 候选定位与前置验证 — **Proposed**：外部评委推荐 Hindsight（41.4k★ / 3,262 commits / MIT）作为长期记忆层，评分 P71 9/10、Hindsight 7.5/10。二次核查 8/8 事实准确（Recall 4 路并行 + RRF + cross-encoder；Observation **refined rather than overwritten**，带 exact quotes + proof count；Bank 严格隔离；MCP per-bank；Coding Agent 集成含 opencode/pi）。**补 4 条评委遗漏**：①**Knowledge Pages**（可投影为普通 markdown 回到治理体系——但其「AI 自动改写 living document」与 protected paths 8 项默认拒绝替换**直接冲突**）②**Memory Defense**（45 种 secrets/PII 模式可 redact/block——对我们是**硬需求**：`security-policy` 禁 secret 而记忆由 AI 自动写入，现有 `memory_language_check` 只查 CJK 不查 secret）③**Multilingual**（中文可直存，恰补 P71 Inbox 短板，但与正典英文强制直接冲突，是取舍点）④**Disposition traits**（banks 人格参数**塑形 reflect 输出**——违反我们证据先于断言的 gate function，是唯一风险项）。**指出评委 §8 文字与 §9 图自相矛盾**（文字说不该进 Runtime，图里却画 `Learned Memory → Context Loader → Runtime`）。**补 2 项未评估**：retain/recall/reflect 每次都含 LLM 调用 + cross-encoder 重排 + PostgreSQL/pgvector —— 与 P71 承诺的「固定 token 成本 0」及 CONTEXT_LOADING 预算纪律冲突；97 open PRs / 3,262 commits = API 不稳定。**不认同「下一阶段 PoC」的时间安排**：288 提交 / 19 条正典（每 15 提交 1 条）、今日捕获产出 0 —— **捕获入口产出为 0 时接 Recall 层等于给空水箱装水泵**，且评委自设的 PoC 问题③无从回答。**改为 Option C 前置验证**（零安装，用既有 19 条正典 + 551 提交测普通检索命中率，**可能直接省掉整个 PoC**），并作为 **P71 §5.8 触发条件 ④**（须在 ①②③ 之后，因答案依赖正典规模）。**§10 二次反馈**：外部评委上调 Knowledge Pages ⭐⭐⭐⭐⭐ / Memory Defense ⭐⭐⭐⭐⭐（硬需求）/ Multilingual ⭐⭐⭐⭐⭐，新增 **Directive（what must be obeyed）vs Disposition（how to reason）** 论断，Observation 下调为非第一优先级 —— 全部一手核实通过（**Directives 的 strict 语义是「违反即响应被拒」，比评委描述更硬**）。三次评估判定：**采纳 4 / 部分保留 1 / 不采纳 1**。**不采纳 Directives 治理映射**：官方明写 Directives **只作用于 reflect**，而 §4.3 已禁止 reflect 产生权威输出——**映射自相矛盾**；且 disposition / reflect_mission / directives **三条 bank 配置全部只作用于 reflect**，**反向印证了 §4.3 的正确性**（Hindsight 自己就把它们限定在推理通道）。**部分保留 Memory≠Knowledge 分层**：概念认同，但 Knowledge 在我们体系里 = `standards`，硬加一层会与 `standards/` 重叠。**三项上调能力均不改变 Option C 结论**——两项可自建（Memory Defense 本质是 detector→action 映射表，自建 `tools/checks/secret_scan.py` 成本远低于引入 PG+pgvector+每次操作 LLM 调用），第三项有未解冲突（Knowledge Pages 的「AI 自动改写 living document」× protected paths 8 项拒绝替换）。**新识别缺口**：`prompt_injection` detector 揭示我们**完全没有这一类安全覆盖**（security-policy 只管 key/token/password），而 P71 Inbox 由 AI 自动写入，正是注入入口 → 待裁定 ⑥ **裁定 ②**（已记录 §11）：需独立 policy 但**暂不创建**；P77 先作为架构硬边界记录；待 P77 主体裁定采用 Hindsight/reflect 后创建；**该 policy 不绑定 Hindsight** —— 解决的是 **Dynamic/Derived Knowledge 与 Authoritative Knowledge 的边界**。据此补三点：①「不绑定」改变了**措辞判据** —— 若换成任何其他派生通道这句话仍成立才该写进 policy，只对 Hindsight 成立的部分留在 P77；②本仓已有该概念的**窄版本可复用**：`SOURCE_OF_TRUTH.md` Rule 0「外部 AI 结论 = unverified inputs」，未来 policy 应是它的**一般化**而非第二套「真值」概念（否则两处都说「什么是权威」）；③实测 `AI_OPERATING_RULES.md:18` 的 `reflect` 是 **Reflection 机制**（工作流收尾自查），与 Hindsight `reflect` **同名不同义** —— 这是暂不创建的补充理由，policy 须用不撞车的词。**裁定 ④**（已记录 §12）：引用计数缺口 **v1 不解决** —— 不立项、不改 Load 语义、记为已知缺口。语义是「**不值得**为它改变读取语义」而非「不需要知道」—— 前者可被后续证据推翻、后者不可。补三点论证：①会展开成 usage telemetry system（read event → 计数 → 持久化 → 去重/并发/重试），而 P71 目标是「经验产生 → 候选落地 → 正确分层 → 正典持久化」②`read count ≠ useful`，且 `read count = 0` 更可能说明**召回机制不好**而非知识无价值 —— 记成「无价值」会导向删掉「读不到」的 Memory，而它们恰是召回层最该修好的对象 ③**危险 KPI**：为提高「使用率」被迫加载大量 Memory，与 `CONTEXT_LOADING.md` 预算纪律正面冲突。**显式禁止**把 Memory read count / reference count / utilization % 写入观察期指标；未来若重做，起点是 `recalled → used → task outcome`。**顺带消解 P71 一处内部矛盾**：§5.8 路线图与 §5.9 派生指标表都列了「Memory 实际复用率」，而 §5.9 下方又说不用 —— 已移除并改为显式「已知缺口 · v1 不解决」记录。留着的代价是它会在观察期**被当作目标**，从而变成 KPI。同时收紧了 §5.8 前置条件 ③（改人工记录、非计数）。⑥⑦ 已由 P78/P71 执行消解。**仍待裁定：①（Option C）· ③（通过线）· ⑤（是否现在验证）** | 2026-09-29 |
| [P79](P79-CONTRACT-EVALUATOR-V1.md) | AIC Contract Evaluator V1 —— `develop` Phase 4 单点验证 | **Approved**（D1–D5 逐项裁定 + Input Contract + 措辞纪律，全部作已裁定约束写入）：**核心验证问题** = AIC 能否对 develop Phase 4 的一个明确可机械判定 criterion 做独立求值，并稳定产生 `completed`/`not-satisfied`/`undetermined` 三态 + JSONL 审计记录。**D1 A‴** 试点=develop Phase 4 单个（全仓最高频 18 次且有 `phases:` 块的 workflow；`spec` 23 次但无 Phase 块）· **D2 A** 记录=追加式 JSONL、**写入者是求值器非 Agent**（Agent 写则退回原状）· **D3 A′** 三终值、**不引入 MUST/SHOULD/MAY**（本仓 MUST:SHOULD:MAY≈20:1:1；`pass_criterion` 是单字符串；`gates.optional` 无消费者）、`undetermined` **不可静默通过**（来源=三方评委建议→我方采纳；AI 原方案「只暴露不预防」留有 Agent 说「无法判断继续」的逃逸路径）· **D4 A″** 不建 Agent Tool 表面（0 个真实调用方；Agent↔AIC 无结构化通道——`main.py:291` 是 `subprocess.call`+剪贴板）· **D4.1 A′** 不引入 `exit 2`（`comment-lint`/`format-check` 已有 `2=硬/1=软` 同构约定）· **D5 A″** stdout 人读+前缀、JSONL 机器读、**不提供 `--json`**。**Input Contract**：`project`+`change` 显式传入，**禁止推导 change-id**（实测 3 样本中 `202609-housekeeping-log-volume-reduction`/`log-volume-reduction` 构成反例，同名只是多数现象非契约）。**措辞纪律**：求值得 `completed` 只表达 **criterion satisfied**，**不是**「Phase 4 已完成」；`Task Card fully checked` 无判定语义，V1 不触碰。**Layer 2** 把「不验证业务完成性」写成**有意识的实验边界**（P77 §13.4：有数字的错误结论最难被识别）。**criterion 审查（已应用）**：首版「Completion Report Directory Non-Empty」按原三条判据会判通过，**但实测出确定性假阳性** —— 目录跨多张 Task Card 累积（`cool-italent-sync-plus` 14 文件 / `public-security-storage` 16 文件 / `T-001`…`T-045`），本次 Phase 4 未执行时目录已非空 → **evaluability 判据升级为四条**，用户追加 **Execution-Isolated**（历史状态不得伪造本次执行成功）。已改写为 task 级："Completion Report for `<task>` exists (.../`<task>`-completion-report.md)"。**Input Contract 扩为 `project + change + task`**（`task` 复用 develop 已声明的 Task ID input，非新概念）。Q1–Q4 核查（§12.3）：Task ID **两套**（`T-NNN` 116 个 / `<n>.<m>` 18 个，集中在 `qa-housekeeping-optimization` 且同目录并存）· Report 命名两套且与 Card 同构 · **无成文命名规则**（`grep` 只命中路径，`runtime-develop.md:337-339` 仅规定目录）· **`T-` 前缀不可假设**。用户担心的「T-011 对 2.4 只能人工理解」**不存在**（项目级差异，各自内部同构）。`not-satisfied` **真实可达**：`rpc_log-graceful_shutdown` 11 卡 8 报告，T-009/010/011 无报告。**采用 A1 严格匹配** —— 宽松匹配会违反 Deterministic 判据；命名不合规的**假阴性记入 Layer 2**，补命名规则属 runtime 职责，**本轮不改 runtime**。**AI 两处自我更正**：①「117 个 Phase 都有 pass_criterion」错误——实测 42 个中仅 **1 个（2.4%）**，D1 因此由「4 个」收敛到「1 个」②「JSON 在本仓无位置」错误——**6 个工具已有 `--json` 输出**。含 Scope/Repository Boundary（明确 `aic/`、`ai-runtime/`、`ai-system/projects/` **不存在**，不作实施对象）与 R1 **伪 Contract** 风险（点明本仓已生产过三次「声明而无消费者」：`runtime-base.md` 8 API / Phase `activation` 由 Agent 求值 / `gates:` 注册表）  **Implemented**（V1 完成，2026-09-30）：`workflows/develop.md` Phase 4 唯一 criterion + `tools/contract-eval.py` 求值器 + `cli/tests/test_contract_eval.py` **37 例**（含逐条短路自证）。**测试抓到一处真实假通过**：`finalize` 中 `payload = dict(result)` 复制了 `verdict`，记录写入失败时 `update` 把它覆盖回 `completed` → **仍返回 exit 0**。纯人工审阅不会暴露（三个断言中前两个都会过，只有「首条保留原始 evidence」会挂）。**实测（真实 workspace）**：`T-001`→`[PASSED]`/0；`T-011`（Card 在、无 Report，同目录另有 **8 份兄弟报告**）→`[NOT-SATISFIED]`/1 ← **判据 4 实证**，目录级检查会误判为 completed；`T-999`（Card 不存在）→`[UNDETERMINED] task-card-missing`/1；`2.1`（第二套 ID 形态）→`[PASSED]`/0 ← 证明未假设 `T-` 前缀；`T-011` 连续两次同一 `execution_id` ← 确定性实证。**一处偏离设计稿**：`--task "T-001 "` 设计稿预测透传→not-satisfied，实现改为**显式拒绝**→`input-missing`（在输入边界指出真实问题优于下游报产物缺失）。已知限制如实记录：文件名不合规→**假阴性**（有测试显式断言其为 not-satisfied）· `execution_id` 不含时间 · append 原子性仅为「单次 write()」实现事实、**非**跨进程锁契约（全仓 `open(…,"a")` 此前零命中，V1 引入新机制）· `evaluator-error` 为 8 类 evidence 之一（由用户 7 类扩展，可撤销）。门禁：**786 OK**（+37）· check.py PASS · workflow-command-audit 0/0/0 · quick-check OK · path-audit 0 broken · repo-lint 0/0 · 短路自证 11/11 | 2026-09-29 |
| [P78](P78-SECRET-INJECTION-GATE.md) | Secret + Injection 门禁 —— 补齐 `security-policy.md` **零机器执行**的缺口 | **Approved**：实测该 policy 现有规则**连自检 check 都没有**，17 项门禁**无一检查 secret**（`grep` 零命中），`pre_commit_gate` 唯一内容类检查是 `memory_language_check`（只查 CJK）。P71 Inbox 由 AI 自动写入且正典 **tracked + 提交** → secret 一旦入正典即持久泄漏，**Gate 必须在 triage 之前**。**Secret（S1–S5）ERROR + pre-commit block**：Scanner 只检测、**价值存亡由 Triage 判断，不自动 redact**（避免 `[REDACTED]` 半吊子记忆）。**Injection（I1）改结构共现检测**（A 组祈使句+规则指向 / B 组权威冒充），**不做语义判定** —— 评委要求判「是否越权成为 Instruction/Policy」在技术上正确但本仓做不到：门禁层**零 LLM 依赖**、17 项检查全为结构性，加 LLM 破坏 ADR-0009 分层与 check.py 确定性。门禁**不判定注入，只挑出需 Triage 判定者**。**不引入 BLOCK/QUARANTINE/CLEAN 三态**：`Checker` 只有 error/warn、`check.py` 只返回 exit 0/1，改为**用 severity 表达决策权归属**（ERROR=不可覆写 / WARN=强制人工判定），与 P76 C2 同构。**三道防线**：写入时 check.py 第 18 项 / 提交时 pre-commit block（`--no-verify` 可绕过故不可省）/ CI（防未 commit 文件）。**Hindsight Memory Defense 归入 §7 未来适配项 —— 本次不实现任何兼容层**（无 SDK/MCP/bank 映射/配置项），并声明**本门禁不因 Hindsight 而放宽**（Hindsight 提供纵深，不提供替代）。排除机器层 `~/.config/ai-system/env.yaml`（P29 权威位置，误报会使门禁不可用）。非目标：PII 检测（无可靠正则）、历史提交扫描（需 filter-repo）、门禁内 LLM **Implemented**（S1 commit `5b935e7` 已推送）：§4 六项全落地，§5 全部验证通过 —— 全量单测 **721 OK**（+39）、check.py PASS、**真实仓库 0 findings**；植入 secret（`git add -N`）→ check.py FAIL + pre-commit exit 1 且输出 `[redacted]`，移除后还原。**四处偏离提案**（提案写于门禁运行之前，以实测为准回写 §3）：①`.env` 语义改为**已跟踪即 ERROR**（只看工作树会让持有本地未跟踪 `.env` 的开发者被拦 → 门禁不可用）②**报告须掩码**（首版 `excerpt` 原样打印命中行 = 门禁自己制造泄漏的第二份副本）③**标记位置成为约定**（pre-commit 闸拦下了本次提交；约定收紧为置于 docstring 首行，**未用 `--no-verify`**）④**I1 极性修正**（首版把 `never skip verification`——**禁止**跳过，正是期望行为——判为注入，误伤 2 个正典文件；**关键词扫描无法区分「指示违规」与「禁止违规」**，正是评委警告的失效模式）。真实仓库 findings **67 → 15 → 0**。自证抓出 7 个独立缺陷，其中「未跟踪文件被跳过却看起来在工作」是一次**假验证** —— 据此补防空转断言（tracked 集 >200），否则 `git ls-files` 返回空会让全部仓库测试假绿。未做：Hindsight 兼容层 / PII / 历史提交扫描 / 门禁内 LLM / 自动 redact / 可配置 `default_action` | 2026-09-29 |
| [P76](P76-PHASE-CONTRACT.md) | Phase Contract（Phase 一等契约：第九段 + Activation 语义 + Declares 校验） — **Implemented**（S1+S2 均 2026-09-29 交付）：Phase 事实上是执行单元（bugfix 12 / dev-setup 10 / release·spec 9）却只以 markdown 章节存在。F1 **条件执行对 agent 不可见**（5 个 hotfix-only Phase 靠散文表达，而 `_skeletonize_runtime` 只注入标题+首句，标题的条件后缀与 "Activate only when…" 均不在骨架里）· F2 **跨 Phase 依赖用散文且区分不了状态**（6.6 "committed and pushed"=completed vs 6.7 "regression verification passed"=passed，机器无法区分）· F3 **Phase 产出无契约**（`Declares` 全缺）。顺带修两处既有破损：G1 bugfix Phase 6 `Invoke: testing/verification` 指向 39 个 skills 中**不存在**的 skill；G2 pass 判据未链接 `runtime-verify.md:214-250` 已有的 Status 机制（**判据存在，是链接缺失** → 按决策(a) 不新增 gate）。用户定案三态语义 `active`/`completed`/`passed` + 硬规则「`.passed` 只能引用有 pass_criterion 的 Phase」+ 逐 Phase 禁区间合并 + `Declares ⊆ Outputs` 单向（依据实测：多 Phase→少产物是常态，反向检查会误报）+ `## Phases` 固定 3 行入口、**表体在配置侧**（不做 workflow 特例、不放宽 100 行）。门禁 5 条含用户定案的 3 条 ERROR，另加 3 条（YAML↔runtime Phase 集合一致 / 表达式可解析 / id 唯一）；**每条配负例测试**（今日已踩三次门禁静默失效）。code-review 最小压缩 8 行（删与 runtime Phase 1 重复的 5 条，workflow:60-61 已自声明真源在 runtime）→ 99→88，+3 = 91 行 | 2026-09-28 |
| [P75](P75-RUNTIME-TEMPLATE-SIZE-GOVERNANCE.md) | runtime 模板体量治理（体量门禁 + 报告模板外提 + 契约下沉 base） — **Proposed**：巡检 18 个 runtime 模板，5 个超 10K（`release` 641 行 / `develop` 335 / `dev-setup` 497 / `spec` 485 / `bugfix` 381）。**先排除错误动机**：`_skeletonize_runtime` 已把全文压成 Phase 骨架，5 个大文件进 prompt 仅 728–1838 字符；P59 实测折行收益 0.03% → **token 不是动机，本提案治可维护性**。三类异质膨胀：P1 **runtime 侧无体量门禁**（workflow 有 RFC-0003 100 行 ERROR，runtime 零检查；已致 `develop`/`bugfix` 缺 Completion 段、`external-review` 缺 `Extends` 继承不到 base 契约）· P2 **报告模板内嵌**（`release` 100 行 markdown 报告模板使 Phase 1 膨胀到 241 行）· P3 **252 行逐字冗余**（15 文件各重复 Governance 8 行 + 14 文件各重复 Reflection 9 行，而 base 已声明继承、REFLECTION_RULES 已为 SSOT）。方案 A 体量门禁（400 WARN/600 ERROR）→ B 报告模板外提新建 `templates/reports/` → C 契约下沉 base（可行性已实测：`_merge_runtime_base` + `@keep` 机制确使 base 契约进入 prompt 骨架）；C 的 prompt 可见性实测为**阻塞项** | 2026-09-28 |
| [P74](P74-REPORTS-DIRECTORY-GOVERNANCE.md) | reports/ 目录分类治理（按类型建子目录 + 引用地址治理） — **Proposed**：盘面 124 .md + 5 目录全平铺；四缺陷 F1 归属无门禁（本日 `prepare-beecount-2608` 业务产物误入，纯孤儿、零引用）/ F2 分类维度未定义（5 目录两种自创前缀）/ F3 索引只登记不分类且与布局无对应 / F4 149 处引用散落 63 文件且 `path-audit` 完全不检查 reports 内部引用 → 移动无告警；**方案 C 分两期**：S1 归属门禁 + 分类定义入治理（Fix 级、零迁移、直接止血本次事故）+ S2 七子目录迁移 + 149 引用同步 + `glob`→`rglob`（Structural 级）；**关键风险 R1**：`proposal-audit` 用 `glob` 非 `rglob`，P 系列进子目录即 66 份提案对 Status/索引/open-item 三项校验**静默失明** → S2 强制断言份数相等；§8 七项子决策待裁定 | 2026-09-28 |
| [P73](P73-CODE-REVIEW-HISTORY-REENTRY.md) | code-review 历史重入（选择项目 → 载入历史报告与分支 → 输入新需求） — **Proposed**：路径 1（现状）零变化 + 路径 2 = 会话点选 → runtime 载入历史报告与分支 → 可选新需求（空 = 仅重载）；新增会话元数据 `code-review-report.json`（分支对 + SHA 锚点，复用 outputs-convention 槽位）+ `providers.review_sessions` 候选 + 2 个可选字段；**不做 findings 对账**；§4.1 六项子决策待裁定 | 2026-09-24 |
| [P72](P72-PROTECTED-PATHS.md) | 受保护路径 + 破坏性操作默认拒绝（Protected Paths & Destructive Operations） — **Implemented**：`config/protected-paths.yaml`（两类 11 项 + not_protected）· `AI_OPERATING_RULES` 新节（默认拒绝 + dry-run/确认流程 + 提交信息 shell 纪律）· `checks/protected_paths.py`（check.py 第 10 项）· 8 项单测；**不做快照**（用户裁定）；成本 +530 tok/run（Always Load） | 2026-09-24 |
| [P71](P71-MEMORY-INBOX.md) | Memory 候选暂存区 + 巡检确认提取（Memory Inbox） — **Approved**（用户提出"日常会话不懂维护规则、memory 应单独存放如 `logs/memory/`、运维确认提取"；核实后**采纳其思想、改其落点**：`logs/` 被 gitignore → 非持久，改为 tracked 的 `governance/memory/inbox.md`（草稿层可中文/1 行）+ 巡检 triage 晋升正典；§4 待选 A/B/C/D） | 2026-09-24 **Implemented**（S1 `f0e9e0c` + S2 `460f813`，均已推送）：§5 八项必做全部落地，**§6 验证计划实际执行**（非声明）—— ①门禁不破+双反证（正典缺 `Lesson` 仍 ERROR、正典中文仍 ERROR）②端到端 3 候选 → `generated=3/triaged=3/promoted=1/redirected=0/discarded=2`，假 Source（`adr.py:999`，该文件仅 92 行）被拒 ③摩擦：写 12 行草稿、0 次读 833 行指南、0 次提交 ④直写正典未退化 ⑦长候选 12 行无截断；⑤⑥需真实会话，**未实测**。**实施发现四问题**：薄命令门禁在 `workflow-command-audit.py`（不在 check.py）且是 error，113→100 行靠删重复而非删检查项 · 豁免需双路径（提案只写一处）· 提案示例路径被 path-audit 拦下（改文档适配门禁，非给门禁加豁免）· **豁免的「格式」那一半是理论性的**（`check_memory` 只认 `## [Category]` 形状，候选格式无论有无豁免都被忽略；真正起作用的是语言那一半）。**已修一处破坏性缺陷**：测试 `_cleanup` 原为 `DRAFTS.glob('*')` 全删，**跑一次单测即清空真实 Inbox**（git-ignored，无痕迹不可恢复）→ 改为只删自建文件 + 防回归用例。**验证计划带出新规则**：Source 的**形式**与存在性同等重要 —— 实测 `memory.py:20` 实质正确但`DRAFTS_DIR` 已漂至 31 行；严格按行号会误拒真声明，只按文件存在会放过伪造（`adr.py:999` 文件存在、行号越界）。故 triage 判行号过期为「需确认」而非「已证伪」，并写入形式强度排序：**commit hash > 引用片段 > `file:line`**（后者不可在源文件演进后存活）。**观察期数据有效性修正（用户裁定，已落地 §5.9 + S1.7）**：①**删除「候选产生率」** —— 分母「有经验密度的会话数」无采集机制，且与「捕获经验」是**同一 AI 的同一判断**（用被测系统的输出算分母）；唯一可数替代 `logs/` 是特定运行的诊断记录、非每次会话有、机器本地，更弱。**删掉是安全的** —— 该率要解决的「空目录无法区分『全部沉淀』与『根本没产生候选』」已由 `generated`×`triaged` **配对读**解决（`0/0` vs `0/N`）②**新增「discard 理由多样性」** —— 「逐条一行」是格式要求，拦不住 N 条相同措辞 ③**明确「只看方向不看水平」** —— 分子分母同源（捕获 AI / triage AI / Source 核验 AI），**唯一独立防线已被同源抵消**，故不给目标带；任何单一比例落在中间区间都不可判定为健康，四周后有真实数据再定带。④**数据无失效路径** —— 待裁定（后经 P77 §13.7 裁定转 Option D + 三分支）。**观察期范围定为四类全覆盖**（develop/review/bugfix/**change-impact**），含样本下限 n≥4（n<4 读作「样本不足」而非「入口未用」）。用户提供的三条运行现实：**①develop 与 review 通常成对出现** → 全覆盖对这两类近乎零成本，但同一条经验可能在两个收尾各捕获一次，故 **triage 去重是承重环节**；**②bugfix 日志量可能少** → 按门限**很可能达不成**，属**预期内**，**预先记录以免四周后误判为新问题**；**③change-impact 需纳入** —— **AI 核实发现真实覆盖缺口**：`runtime-change-impact.md` 存在且已有 6 份日志，但**未被仪器化**，其运行**既不进分子也不进分母**，已补第四个入口。另定判读纪律：**合并读须同时给出四类分项 n**，否则 `0/28` 会把「已覆盖」误报成「已验证」（与 P77 §12.5 危险 KPI 同一类失效）。**「候选产生率」经复核恢复为下界形式**：用户指出 `logs/` 已有运行日志 —— **AI 更正自身错误断言**（曾称「非每次会话有」；实测 develop/review/bugfix **每次运行都留痕**，22 份，且正是加了 Experience Candidates 的三个 runtime，仪器化范围精确对应）。分母 = instrumented 运行数，性质 = **真实捕获率的下界**。分布 **18:2:2** 极不均衡，须按类型分读。**用户追加两条约束**：①`logs/` **曾被 AI 误删**（INCIDENT-2026-09-24，约 200 份日志全毁）→ 分母须**巡检时落库**，**不得实时回查** ②`metrics/` 快照命名**无机器维度**（实测会碰撞）→ 落点改 `metrics/by-machine/<machine-id>/knowledge-runs.jsonl`。另加 `watermark` 防重复、`files` 全量留存使计数可审计、五项计数带 `<machine>`（捕获机与巡检机常不同机）。`aic-maintain` 99 行 —— 压回过程中删掉一处**复述工具输出**的delta 判定映射（工具自身已打印 verdict + suggested 子集）。**AI 自我更正**：复核时断言「`last_findings` 是单值字段、无法跨轮积累」—— **错误**，实测为 list（50 条目），追加可跨轮积累。犯的错是看到 `- >-` 未验证类型就下结论，正是 P78「『看起来是』不等于『是』」的反面。已撤回该缺口。`aic-maintain` 改动一度涨到 104 行触发薄命令门禁，**压回 98 行**（手段是删重复：完整读法纪律留 P71 §5.9，命令只留提示；未删任何检查项）。全量单测 **733 OK**（721→733）；check.py PASS；workflow-command-audit 0/0/0；quick-check OK；path-audit 0 broken；proposal-audit 0/0 | 2026-09-29 |
| [P70](P70-OUTPUT-DISCIPLINE.md) | AI 输出纪律（Output Discipline） — **Implemented**（caveman 评估核实后**只吸收思想、不引入本体**）：①`standards/common/output-discipline.md`（优先级链 + 可压缩/禁压缩两清单）②develop+review 阶段回复形态 ③`templates/prompts/worker-contract.md` 硬边界（含强制显式 `UNDETERMINED`）④上下文压缩原则（不造新机制）；**明确不以 token 下降百分比为验收指标**；附带修复 `workflow-command-audit` 薄命令门禁崩溃缺陷。成本：Always Load +560 tok/run，其余 0 | 2026-09-23 |
| [P69](P69-AI-COMMENT-SLOP-GATE.md) | AI 注释泔水治理（Comment Quality Gate） — **Implemented**：MVP 八步落地（8 提交）——标准 `documentation.md → Comment Quality`（六级分类 + 稳定规则 id）· 单文件工具 `tools/comment-lint.py`（tree-sitter/标准库双通道）· diff 限定 · 规则引擎（白名单优先 + 三道精度护栏）· `fix` 默认 dry-run · `gates.develop` 注册（**只报不拦**）· 技能 `comment-cleaner`；实测：真实仓两通道一致（2.9 万条）· 历史 diff 332 新增注释 → DELETE 5.1%/REVIEW 64%/KEEP 31%，**确定可删 17/17 人工审计零误删** | 2026-09-23 |
| [P68](P68-WORKQUEUE-HANDOVER.md) | 工作队列式交接（Work-Queue Handover）契约与模板 — **Proposed**（Option B：扩展 `skills/handoff` 增 work-queue 模式 + `templates/prompts/handover-workqueue.md` 9 节契约 + 两处入口；归属/生命周期待裁决） | 2026-09-23 |
| [P67](P67-STRUCTURAL-SMELL-CAPABILITY.md) | 结构性坏味道：检测 / 映射 / 劣化门（不含自动重构执行）— **Proposed**（Option B 最小切片；阈值与实施触发待 §4.1/§4.2 裁决） | 2026-09-23 |
| [P62](P62-TASK-COMMIT-TRACEABILITY.md) | 任务提交信息 `T-<id>` 强制性与实践脱节（标准↔实践↔门禁三方不一致）— **Implemented**（分支名为机器判据 + 拆 id 层级 + 模板固定 `T-\d{3}`；真 git 仓正反例 12 项） | 2026-09-23 |
| [P63](P63-BRANCH-NAMING-NON-ITERATION.md) | 主链分支命名：非迭代形态未文档化 — **Implemented**（预设驱动 `plain`/`ipd` + 场景→预设映射 `config/branch-formats.yaml` + AI 组装/用户确认具体名/冻结、格式串不可手改；含修好 parser 拒绝非迭代形态的实测缺口） | 2026-09-23 |
| [P65](P65-C2-PROFILE-SEMANTICS.md) | C2 格式 profile 语义边界与校准（`lineSplit=120` 被自身 `alignment=0` 越过；`join_wrapped_lines=false` 仅覆盖二元/条件表达式）— **Implemented** 2026-09-21（A 语义边界固化 + D 豁免治理〔理由 + 180 天复核告警〕；**B 否决**（差异 +55%~+109%）、**C1 否决**（导出与仓内 profile byte-identical）；根因＝**引擎表达力缺口**；C2 记为按需备选） | 2026-09-21 |
| [P66](P66-CR-CHANGE-IMPACT-DERIVE.md) | code-review / change-impact 重复追问项目与分支（容器已记录服务与各自分支；P57 单候选契约只认字面量 `Branch` 而实际字段为 `Branch Mapping`/`Base Branch`→ 从未生效）— **Implemented** 2026-09-21（A 容器派生〔Projects/覆盖项/默认值〕+ C 全服务预填；**P57 契约改为类别匹配**；新增 opt-in 目标集防覆盖 `scan`；+11 测试）| 2026-09-21 |
| [R4-HANDOVER-2026-09-23](R4-HANDOVER-2026-09-23.md) | **R4 残债交接文档**（盲检收尾：已完成清单 / **剩余 8 项逐条修复指引 + 验证方式** / 已判定不做项 / R3 措辞 52 条 / 未关闭提案 / 门禁命令与基线 / 本会话踩坑清单 / 记录位置）—— 供新会话无损接续 | 2026-09-23 |

---

## 维护报告（MAINTENANCE）

| 日期 | 模式 | 范围 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| 2026-07-22 | weekly | 首次全量巡检 + release.md 评估 | `MAINTENANCE-20260722.md` | — |
| 2026-08-01 | monthly | 结构/能力/生命周期/演进 | `MAINTENANCE-20260801.md` | — |
| 2026-08-05 | on-demand | aic-sync 同步核查 | `MAINTENANCE-2026-08-05.md` | — |
| 2026-08-06 | monthly | 架构/能力矩阵/一致性抽查 + 修复批次 | `MAINTENANCE-2026-08-06.md` | —（S1-S4 已闭环） |
| 2026-08-06 | on-demand | aic-sync 复查 | `MAINTENANCE-2026-08-06-aic-sync.md` | — |
| 2026-08-06 | on-demand | live-facade SNAPSHOT 风险 | `MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md` | —（P14 已闭环） |
| 2026-08-06 | on-demand | 方法长度与注释约定 | `MAINTENANCE-2026-08-06-method-comment-convention.md` | **✅ 已实施（2026-09-23，用户裁决 P1′/P2′/P3′）**：方法长度改「target ≤40 / hard ceiling 80」（编排入口不豁免）· 私有方法须一行 Purpose · bugfix Fix&Validate 改为**引用标准**且只约束已触碰方法（不授权顺手重构）· 新建 `standards-loader` 的 `For runtime-bugfix` 小节；**同时解锁 P67 阈值口径** |
| 2026-08-08 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 A1-A4 | `MAINTENANCE-2026-08-08.md` | F1-F3 已修复（A1-A4 已闭环） |
| 2026-08-13 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 S-A/S-B | `MAINTENANCE-2026-08-13.md` | F1-F2 已修复（S-A/S-B 已执行）；P18/P19 已闭环(2026-08-14)；P20 遗留 |
| 2026-08-13 | on-demand | extensions 域巡检（Scope=extensions） | `EXTENSIONS-MAINTENANCE-2026-08-13.md` | F1: 6 个 OPTIMIZATION_LOG 空模板待补录 |
| 2026-08-14 | on-demand | 巡检当前提案 + 治理一致性抽查 | `MAINTENANCE-2026-08-14.md` | P22 已 approve（阶段二 defer 至新提案）；F2/F3 已修复 |
| 2026-08-14 | on-demand | 跨平台治理落地（P23 批次：gitattributes/hook/lint） | `P23-CROSS-PLATFORM-MAINTENANCE-GOVERNANCE.md` | —（P23 已 Implemented） |
| 2026-08-17 | on-demand | 工具校验/周度巡检/一致性抽查 | `MAINTENANCE-2026-08-17.md` | R1: check.py 回归（FakeWizard 缺 projects_root）→ 已立提案 P24 待评审；其余全 PASS |
| 2026-08-20 | on-demand | openapi-gateway OOM 流程提案（P1–P7 评估） | `MAINTENANCE-2026-08-20.md` | P7 简体规范已就地修（LANGUAGE_CONVENTION）；P4 技能触发词已登记 skills/README；P1/P2/P3/P5/P6 结构建议待变更管理立项 |
| 2026-08-23 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次（提示词路径绝对化 + Windows 路径归一化 + env-init） | `MAINTENANCE-2026-08-23.md` | 批次 A 已落地：P26 置 Implemented；P28 已补 README 索引；workflow-trigger 死模板已归档；方案 3（根占位符填充）待立项 |
| 2026-08-24 | on-demand/prepare | 增量基线 CHANGED→对应子集；scope=prepare 一致性抽查（8 项 7 过/1 失败）+ 实施 P32 方案 A | `MAINTENANCE-2026-08-24.md` | P32 已闭环（prepare.md Outputs 位置对齐 workspace-anchored）；P28/P26 开放项 defer |
| 2026-08-24 | on-demand/workflows | 全量审计（delta FIRST_RUN→record）；workflows 域结构/注册表/引用链/Next 链全绿；AGENTS.md 缺失（doc-vs-reality 对象） | `MAINTENANCE-2026-08-24-workflows.md` | AGENTS.md 决策（重建/检查项降级，L2）；README 条件转移表补 release BLOCKED 行（L1 待确认）；P35 待用户决策 |
| 2026-08-25 | on-demand | prepare 工作流集成外部扩展 tr5（含受影响区域增量子集：cli / config / governance / reports / skills / templates / workflows + extensions 域） | `MAINTENANCE-2026-08-25.md` | tr5 已注册；P38 批次 1 已实施；P39 已实施；增量基线刷新 |
| 2026-08-26 | on-demand | extensions/tr5 — 前后端需求区分机制确认 | `MAINTENANCE-2026-08-26.md` | — |
| 2026-08-31 | weekly | 增量 NO_CHANGES；工具校验 OK；code-review.md 节顺序违规；7 项提案开放 | `MAINTENANCE-2026-08-31.md` | code-review.md 节结构调整需 L2 变更审批 |
| 2026-08-31 | on-demand | task 制定/拆分对齐（task-splitter → cards/ 位置 + Task Card 字段）+ 淘汰根 tasks.md + 堵 archive 归档完成度缺口 | `MAINTENANCE-2026-08-31-task-splitter.md` | task-splitter 1.1.0；tasks.md 淘汰；archive/explore/aic-propose 同步 |
| 2026-09-01 | on-demand/workflows | 语言边界专项：根因定位（执行层未按 locale 转换）+ pilot A（aic-maintain 交互语言约束，自测+实测通过） | `MAINTENANCE-2026-09-01.md` | 方案 B/C 延后（待 §11）；P35 复现实锤建议实施 |
| 2026-09-01 | on-demand | 最新改动诊断（提交 3580bb0 + 孤儿 runtime-base.md 改动）+ 最新运行日志巡检 | `MAINTENANCE-2026-09-01-logs.md` | 孤儿改动 B1/B2/B3 待决策（建议 B1）；README 索引补登；code-review.md 节序待 L2 |
| 2026-09-03 | on-demand | pi-lens 扩展安装评估（结论：现在不安装，用户已确认）+ env-init 首次运行触发场景并入 P36（触发层增补）+ 迁移后基线重置（FIRST_RUN 全量审计顺延 09-07） | `MAINTENANCE-2026-09-03.md` | extensions 仓恢复待用户（aic extensions-init 已覆盖）；P47 索引补登（本次）；P36 增补待季度回顾决策是否提前 |
| 2026-09-09 | weekly | 全量审计（delta FIRST_RUN→record）；工具门禁全绿（0/0/26，WARN 增量归因 k8s-logs 补跟踪）；一致性抽查 8 过/2 提示（合同图漏 logs/archived/、提案盘面）；3 开放提案 defer；P26:53 CI 项建议关闭；知识生命周期无新增捕获 | `MAINTENANCE-2026-09-09.md` | 合同 §2 图补两行需 §11 审批；P26:53/P46 状态收尾待用户确认；aic-maintain 133 行瘦身季度窗口；extensions 仓 1 条未提交归因见 logs/ |
| 2026-09-11 | on-demand/code-review | 按今日 code-review 日志（spec-comparison 三仓）专项 review code-review 流程：runtime「不修改业务」声明 vs 实际 fix+push 矛盾（M2）**已修复**（声明收敛 + Spec-Comparison Fix-Apply Extension 阶段）；code-review.md 节顺序违规**已修复**（用户 L2 批准，前置完成菜单交互流程评估 P1-P4）；HotFix loop wiki 更新行为**已更新**（远程 wiki 用户自管）；T-011 报告覆盖事故 → review/verify 写前检查建议；工具门禁全绿 | `MAINTENANCE-2026-09-11.md` | 建议 1/2/3 已执行（门禁全绿）；code-review 输入简化包已执行（Review Focus 预置候选+多选+默认全选、P1-i18n 补齐、移除 Output Directory、减少分支重复询问、runtime focus 优先级）；skill 加载缺陷已修复（F1：description 块标量解析）；可配置技能源目录已落地（F2：skill_roots，core 29 + extensions 9 全量可达，core_skills 白名单退役）；skill 菜单分组高亮（cyan 系）+ 每屏 10 项可筛选 + 长描述截断（F3）；aic 项目菜单置顶 system/AI 引导（F4）；skill 菜单选中行黑字白底/非选中无背景/每屏 20 项/公司技能组提前（F5 修订 3）；菜单输入中文过滤崩溃修复（F6）；非开发主链菜单体检（F7：env-init 去重 + 字段 i18n 补齐 + 交互层英文文案本地化）；chain 链路无项目问题修复（F8：required 强制项目 + 项目透传）；chain 交互调整（F9 修订：先选链再输入内容 + 保留场景选项）；chain 菜单直达（F10）；chain 重复链路合并+可选块（F11）；P2/P4 交互层结构建议待变更管理；建议 4/5 可选 |
| 2026-09-17 | on-demand | aic 项目菜单 (no repo mapped) 专项：根因 = 映射存储源与显示源脱节——dev-setup 只写 contexts/project-context.yaml、从不写 workspace.yaml（ADR-0008 执行步骤悬空），wizard 仅读 workspace.yaml；已复现（7/8 项目显示 no repo mapped，其中 4 个业务项目实际已绑定仓库）；工具门禁全绿；一致性抽查 8 项 7 过/1 失败（doc-vs-reality=映射数据源）| `MAINTENANCE-2026-09-17.md` | 方案 A（显示回退 project-context.yaml）L2 待确认；方案 B（dev-setup 生成 workspace.yaml，推荐）结构待提案；方案 C（数据源统一）季度候选；run-log 覆盖 1 观察项（coding-memory 归属）；next_maintenance 2026-09-16 已到期建议另排 weekly |
| 2026-09-21 | on-demand | scan 循环选择项目 + 缺少 service 选择专项：根因分层——F1 机器层 local.yaml 残留 /tmp 路径（Projects/Branch 字段 0 选项，机器观察→诊断日志）；F2 ScanHooks.validate 失败 step=2 全量重收死循环（实测复现，校验不验名与 aic-scan.md 不一致）；F3 无 service 级选择（Projects 扁平全量不按容器 workspace.yaml 过滤，change-impact 映射选择 CLI 未实现）；F4 memory 中文未提交块（466/187 CJK）check.py FAIL + pre-commit 不覆盖 memory 门禁；工具门禁除 check.py memory 外全绿 | `MAINTENANCE-2026-09-21.md` | 设计方向已确认（参照 code-review 交互流程）→ 立提案 P57（候选驱动 + 询问代替猜测 + 死循环出口）待评审；F1 local.yaml 就地修正 + F4 memory 翻译提交待确认；P41/P42/P46 + P26/P28 defer；next_maintenance 2026-09-16 已到期待另排 weekly |
| 2026-09-21 | weekly | **补做计划内周检**（next_maintenance 2026-09-16 逾期 5 天，用户授权）：工具门禁全绿（check.py PASS / 325 单测 / 八段 15/15 / path 0 broken / extensions 0-0）；周度专项——依赖图 33 技能 4 层真实无环（3 条 doc-only 提及环经复核为指引非依赖）、孤儿资产 0、权威层重复度 0（逐字重复段 0）、健康评分 13 通过 / 0 失败 / 2 N/A（无 playbooks//checklists/）；指标 09-17→09-21：Skills 30→33、Governance 59→60、Templates 22→24（全部为已记录迁移/新增，lint WARN 26→28 全为「无 workflow.md」类非回归）；新发现 2 低（maintain-report 上期快照误选 + P26 文案自相矛盾）；09-09 遗留 2 项核验已闭环 | `MAINTENANCE-2026-09-21-weekly.md` | 小修 2 项待确认（maintain-report 对比取值、P26 文案）；health.md N/A 计分口径建议；next_maintenance → **2026-09-28** |
| 2026-09-23 | on-demand | **盲检残债 R4 收尾 + skill-sync 价值裁决**：R4 §2.1 `generate_contract` 三项已修（G1 标量引号 / G2 去重告警 / G3 服务匹配口径统一，`015f022`，+9 测试）；§2.2 随 skill-sync 归档关闭（`7032fb0`，用户裁决 archive —— 无消费者/零运行记录/平台未配置/首提后全是审计驱动加固，技能 39→38）；S3 k8s_helper 掩盖 CrashLoopBackOff、S1 index-project Windows venv 写死、S4 idea-mcp SSE 断线吞错已修（均实测）；工具门禁全绿（check.py PASS / 529 单测 / repo-lint 38-0-0-97 / path 0 broken / workflow-command 0-0 / proposal-audit 0-0）；一致性抽查 8 项 7 过 / 1 失败；**新发现 2 低**（k8s-logs 未登记于 skills/README.md、path-audit PATH_RE 中间段误报）| `MAINTENANCE-2026-09-23.md` | 建议 4 条待确认（索引补 k8s-logs 行 + 计数统一、PATH_RE 负向后顾、generate_contract 场景条目 `服务` 字段、R4 §2.3 S2 通道裁定）；R4 余额 1 项（S2）；next_maintenance 保持 **2026-09-28**（on-demand 不重置周检节奏）|
| 2026-09-28 | on-demand | **env-init 误报专项**（用户报障「每次 aic 都提示环境未初始化」）：根因 = `cli/main.py` 触发层判据要求 workspace `local.yaml` + 机器层 `env.yaml` **两份都在**，与 P29 权威位置契约冲突（机器层为权威、workspace 层为可选兜底，仓库内被 gitignore、清理即删）；本机机器层配置齐备、workspace 层缺失属正常态 → 每次误报。取方案 A（判据收敛为仅机器层，治本）而非补文件（治标）；附带修运行态日志落在仓库内（阻塞 check.py FAIL + 单测 1 FAILED）→ 迁工作区层。门禁全绿：check.py PASS / **625 单测 OK**（修前 624 中 1 FAILED）/ repo-lint 0-0-97 / path 0 broken / workflow-command 0-0 / extensions 0-0 / quick-check OK 0 findings / language-gate PASS | `MAINTENANCE-2026-09-28.md` | 建议：`aic-env-init.md` 措辞未标 workspace 层为可选兜底（下批次文档小修）；提案盘面 5 开放（P42/P46/P67/P68/P73）+ 5 open items 延续；next_maintenance → **2026-10-05** |

---

## 评估与评审报告

| 类型 | 主题 | 日期 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| Quarterly | 季度评估（E9） | 2026-08-06 | `QUARTERLY-REVIEW-2026-08-06.md` | Q4/Q5 下季度 |
| Assessment | CLI 规范化评估 | 2026-08-06 | `CLI-STANDARDIZATION-ASSESSMENT.md` | **C1 待办（明日执行）→ C2/C3/C4** |
| Business | 业务仓 Java 格式治理建议（CLI 路线 v2：用户裁定不改 pom，C2 校准定稿） | 2026-09-03 | `SPOTLESS-FORMAT-GATE-PROPOSAL.md` | 待业务侧拍板 master 基线执行与 Checkstyle 引入；工具链已入库（c7eef0b/b5e9f70） |
| Assessment | bugfix skill 优化评估 | 2026-08-08 | `BUGFIX-SKILL-ASSESSMENT-2026-08-08.md` | — |
| Maintenance | 语言检查存量债登记 | 2026-08-08 | `MAINTENANCE-2026-08-08-language-lint-debt.md` | #1-3 参数说明可接受 / #4 顺手修 / #5-7 memory 翻译待办 |
| Maintenance | aic 项目识别与状态记录修复 | 2026-08-08 | `MAINTENANCE-2026-08-08-aic-project-recognition.md` | workspace.yaml 初始化未自动化 |
| Assessment | 上下文/注意力/架构缺口评估+修复 | 2026-08-08 | `GAP-ASSESSMENT-2026-08-08-context-attention-architecture.md` | memory 沉淀/跨会话状态持久化遗留(已闭环于 skills) |
| Assessment | ADR-0009 合规性系统诊断 | 2026-08-13 | `ADR-0009-COMPLIANCE-DIAGNOSIS-2026-08-13.md` | **P1 standards/cool 迁移待评审；P2 废弃命令待清理** |
| Assessment | Token 缓存命中率优化 | 2026-08-13 | `CACHE-OPTIMIZATION-2026-08-13.md` | **R1 骨架化 agent 读取待实测；R2 实际命中率待验证；R3 强制全量开关待实现** |
| Daily | 日终报告 | 2026-08-08 | `DAILY-2026-08-08.md` | — |
| Assessment | 架构评估 | 2026-07 | `ARCHITECTURE-ASSESSMENT-2026-07.md` | — |
| Assessment | 三方 Skill 参考价值 | 2026-08-01 | `THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md` | — |
| Assessment | Skill 来源评估: mattpocock wayfinder（吸收为 skills/wayfinder, On-Demand） | 2026-08-17 | `skill-source-2026-08-17-wayfinder/skill-source-report.md` | ✅ 已处置（2026-09-17）: TRIAL 终止回退 On-Demand，见 §九 |
| Assessment | wayfinder 价值重评估（零试用案例 → 终止 TRIAL，保留 On-Demand） | 2026-09-17 | `wayfinder-value-reevaluation-2026-09-17.md` | 低频备用工具；未来真实雾区案例再评估升格 |
| Assessment | aic 交互与提示词链路专项优化（B1/H1-H6/M1-M8 等 16 项） | 2026-08-18 | `CLI-INTERACTION-OPTIMIZATION-2026-08-18.md` | 意图链连续执行/P22 阶段二待后续 |
| Assessment | 运行诊断日志机制（logs/ 每运行落盘, 模板 + governance 契约） | 2026-08-17 | `templates/runtime/runtime-diagnostic-log.md`（经 AI_OPERATING_RULES §Completion、REFLECTION_RULES 落盘条目登记） | 待随一次实际 command/workflow 跑一轮验证字段/拆分阈值 |
| Decision | Value-Burden Check: 归档 skill-optimizer + iterative-optimizer（无价值证据的 10k 行 meta 工具） | 2026-08-17 | `VALUE-BURDEN-DECISION-skill-optimizer-2026-08-17.md` | 归档联动清理已执行；后续 MAINTENANCE/QUARTERLY 对 >3000 行技能强制检查 |
| Decision | Value-Burden Check: 归档 skill-sync（Insight 平台技能同步通道；无消费者/无运行记录/平台未配置） | 2026-09-23 | `VALUE-BURDEN-DECISION-skill-sync-2026-09-23.md` | 归档已执行（技能 39→38）；R4 §2.2 重构随之撤销；恢复需 ADR + 全门禁 |
| Assessment | Value-Burden: implement skill 保留（已兑现价值 + 健康负担，最大活跃技能 2368 行） | 2026-08-17 | `VALUE-BURDEN-ASSESSMENT-implement-2026-08-17.md` | — |
| Review | **外部盲检评审**（第三方模型双评委独立评审 ai-system 制品：241 条发现 / 抽检精度 ≈91% / 11 项真实缺陷已修，**全部逃过内部门禁**） | 2026-09-21 | `EXTERNAL-BLIND-REVIEW-2026-09-21.md` | 135 WARN+48 INFO 未逐条裁决；衍生提案 **P60**（门禁自校验）/ **P61**（外部盲检纳入运维）待评审 |
| Review | Workflow 层优化 | 2026-07 | `WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` | — |
| Report | Repository Optimization | — | `REPOSITORY-OPTIMIZATION-REPORT.md` | — |
| Report | Repository Architecture v2 | — | `REPOSITORY-ARCHITECTURE-REPORT-v2.md` | — |
| Review | 架构评审 | 2026-07 | `architecture-review-2026-07.md` | — |

---

## 规范速查

| 主题 | 文件 | 说明 |
|------|------|------|
| AI-System 扩展规范（命名/流程/命令） | `EXTENSION-STANDARDS.md` | 新增资产前的权威速查（Golden Rule） |

---

## 迁移（MIGRATION）

| 主题 | 文件 | 状态 |
|------|------|------|
| AI System Repository Migration Plan v2 | `MIGRATION-PLAN-v2.md` | — |
| AI System Repository Migration Report v1 | `MIGRATION-REPORT-v1.md` | — |

---

## 结构分析目录（analysis-*）

各目录含 `analysis-report.md` / `consistency-report.md` / `dependency-report.md` / `recommendations.md`：

| 目录 | 主题 | 日期 |
|------|------|------|
| `analysis-2026-08-01-structure-governance/` | governance 结构分析 | 2026-08-01 |
| `analysis-2026-08-01-workflows-structure/` | workflows 结构分析 | 2026-08-01 |
| `analysis-2026-08-03-structure-workflows/` | workflows 结构复查 | 2026-08-03 |

---

## 维护纪律

- 新增 `MAINTENANCE-*` / `P*` 报告：登记上方对应表（proposal-audit 自动扫门禁）。
- 新增评估/规范/迁移文档：登记对应表。
- 遗留待办列有内容的报告，在下一次维护/评估中优先跟进；闭环后更新该列。
