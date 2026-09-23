# Change Proposal: P68 — 工作队列式交接（Work-Queue Handover）契约与模板

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (skill 扩展 + 新增 prompt 模板 + 两处入口登记；**不新增 workflow/runtime/command**） |
| Author | AI Maintainer |
| Created | 2026-09-23 |
| Reference | 用户指示立案 2026-09-23（源自本会话：`reports/R4-HANDOVER-2026-09-23.md` 的实际产出与消费）；`governance/CONTEXT_RETENTION.md`；`skills/handoff/SKILL.md` |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 两类「交接」需求，只覆盖了一类

| 类别 | 用途 | 现状 |
|---|---|---|
| **上下文边界摘要**（context summary） | 压缩 / 换工具 / 换任务时，按 Keep/Drop 优先级把 P0/P1 存活下来 | ✅ 已有：`skills/handoff/SKILL.md` + `CONTEXT_RETENTION.md` 的 Keep/Drop 表与摘要模板；`CONTEXT_LOADING.md:182-186`、`ATTENTION_MANAGEMENT.md:84` 为触发入口 |
| **工作队列式交接**（work-queue handover） | 把一个**多批次未完成任务**移交给**新会话**：已完成勿重做 / 剩余项**附修法与验收** / 已裁决不做项 / 门禁基线 / **本会话踩坑** | ❌ **无契约、无模板、无入口** |

### 1.2 实证（本会话即真实案例，非推测）

`reports/R4-HANDOVER-2026-09-23.md` 由上一会话**临时发明**结构并写下，本会话消费后：
- §1「已完成勿重做」→ **避免了重复劳动**（未重做 T1–T7/R1/R2/R4 各批）；
- §2「剩余 8 项（逐条修法 + 验收方式）」→ **全部收口到零**（G1/G2/G3 · S1–S4 · §2.2 随归档关闭）；
- §3「已判定不做/维持」→ 未重复翻查（`tools_readme` 范围、退格哨兵 `"<"` 等）；
- §7「本会话踩坑清单」→ **直接命中**：`git add -A` 误提交他人文件（本会话仍差点重犯，凭该条改为只 `git add` 明确路径）、`maintenance.yaml` 是块标量（**今天仍被 ` #` 这类终止符咬了两次**，见 §1.3）。

**反向证据（缺契约的代价）**：该文档的结构是**当场即兴制定**的 —— 若下次交接由另一次会话撰写，很可能漏掉价值最高的三节（勿重做 / 踩坑 / 门禁基线），因为**没有任何地方写着"必须包含它们"**。本会话写它时也需重新推导节次；且「同一任务的后续推进」没有既定去处（本会话只能把阶段 2–8 追加进 gitignored 的 `logs/`，跨机不可见）。

### 1.3 根因

1. **概念错位**：`handoff` 技能与 CONTEXT_RETENTION 摘要模板的定位是「**上下文里留什么**」（易失、为压缩服务），而不是「**交给下一个会话的一份可独立阅读的工作队列**」（持久、带契约）。
2. **无文档契约**：交接文档的**节次与每节的最小内容**从未被定义。
3. **无入口**：「为同一未完成任务开新会话」这个事件，在 `CONTEXT_LOADING.md` 的触发表里不成立（那里只有「New **large task**」），因此没有指向 work-queue 交接的路径。

## 2. Goal

让「多批次任务交接」有**单一来源的节次契约 + 可复制模板 + 明确入口**，使新会话**零推导**接续，
且价值最高的三节（勿重做 / 修法+验收 / 踩坑）**不可被省略**。

## 3. Options

### 3.1 Option A — 完整流程形态（P61 形态）

新增 `workflows/handover.md` + `templates/runtime/runtime-handover.md` + `cli/commands/aic-handover.md`（hidden）
+ 注册 `menu.yaml` / `workflow-registry.yaml`。

代价：4+ 新资产 + 注册表 + 命令面；而交接文档是**会话收尾时由 AI 产出**的，并非用户发起的命令 → **形态不匹配**，且违反 Minimal Change。**不建议**（若将来出现真实命令需求再评估）。

### 3.2 Option B — 扩展 handoff 技能 + 契约模板 + 两处入口（**推荐**）

1. `skills/handoff/SKILL.md` 增**模式划分**：`context-summary`（既有 Keep/Drop，压缩/换工具触发）与
   **`work-queue`（新）**（多批次任务移交新会话触发）；写明两者**互不替代**，且共用同一入口技能（不新增技能）。
2. 新增 `templates/prompts/handover-workqueue.md`：**9 节契约**（以 `R4-HANDOVER-2026-09-23.md` 为范本），
   每节标注 **required/optional + 「为什么需要这一节」**：
   ① 30 秒速览（状态表）② **已完成 · 勿重做**（含提交号）③ **剩余项（逐条：修法 + 验收方式）** ④ 已判定不做/维持（含理由）
   ⑤ 门禁命令与**期望基线值** ⑥ **本会话踩坑清单** ⑦ 记录位置（哪份文件权威、哪些不入库）⑧ 下一步顺序 ⑨ 新会话启动提示词。
   并在模板头部写明两条纪律：**数字须为 run 终态**（不得写中途快照）· **不得写未验证结论**。
3. 入口登记（一行引用，不复制契约）：`governance/CONTEXT_LOADING.md`（§handoff/压缩附近）与 `OPERATIONS.md`（续接处）
   —— 指明「同一未完成任务开新会话 → 用 `handoff` 的 work-queue 模式 + 该模板」。

### 3.3 Option C — 不做（维持即兴撰写）

代价：每次重新推导节次；最容易漏掉勿重做/踩坑/基线三节（§1.3）；跨机不可见。**不建议**。

### 3.4 Option D — 只写契约、不出模板（在 governance 里定义 9 节）

最省，但无「可复制产物」→ 新会话仍要手搭骨架，且契约位置与 `handoff` 技能分离（易漂移）。**不建议**（B 已含契约，只是把它放在模板里并让技能引用）。

## 4. Recommendation

**采纳 Option B**；Option A 明确排除（形态不匹配 + 范围蔓延），若将来出现真实命令需求再另行评估。

**待裁决子项（§5.4 的归属与生命周期）**：建议 —— 系统级 run → `reports/HANDOVER-<date>.md`（沿用今日先例 + 登记
`reports/README.md`）；**项目级** run → `workspaces/<project_id>/handover/<date>.md`（AGENTS.md 的工作区锚定约定）；
**保留策略**：属工作产物，下一次 maintain 巡检时将已失效（被后续交接取代 / 任务已收口）的交接文档归档，**不长期堆积**。

## 5. Proposed Changes

1. `skills/handoff/SKILL.md`：增 `work-queue` 模式（触发条件、与 `context-summary` 的区别、产出物与归属、**必须包含的节次**由模板 SSOT 定义，技能只引用不复制）。
2. `templates/prompts/handover-workqueue.md`（新）：9 节契约 + 两条纪律 + 每节 required/optional 与存在理由。
3. `governance/CONTEXT_LOADING.md` + `OPERATIONS.md`：各加一行入口引用（续接处）。
4. 归属与生命周期（按 §4 子项裁决结果）：`reports/`（系统级）/ `workspaces/<project_id>/handover/`（项目级）+ 归档策略。
5. 索引登记：`reports/PROPOSALS.md` + `reports/README.md`。

## 6. Validation Plan

- **模板自证（dry-run）**：用模板**重写** `R4-HANDOVER-2026-09-23.md`，逐节比对 —— 9 节**无遗漏**，
  且 §2 每条剩余项都带「修法 + 验收方式」（若某条填不出验收方式 → 模板在逼出未澄清项，属正向作用）。
- **节次必要性反证**：逐节问「去掉它会怎样」；对无法给出具体损失的节次要么删掉、要么降级为 optional（避免模板膨胀）。
- **真实复用测试（最强证据）**：下一次「多批次任务交接」由模板产出，新会话消费后回报是否出现
  「漏掉勿重做 / 漏掉踩坑 / 基线值过时」三类失败；结果记入 Implementation Record。
- **门禁**：`check.py` / `repo-lint` / `path-audit` / `proposal-audit` 全绿；`repo-lint` 对新增模板的 frontmatter/语言规则合规。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 与 `CONTEXT_RETENTION` 的 handoff 摘要**概念撞车**（造出第二个"handoff"） | §3.2 明确两类产物 + 由**同一入口技能**分流；两处文档互相引用、不复制条款 |
| 模板膨胀成"什么都要写" | 每节标注 required/optional + **必须写出存在理由**；§6 的反证步骤专门砍冗余节 |
| 交接文档**过期后误导**新会话 | ①「30 秒速览」必须带状态 ②每条剩余项带**验收方式**（过期即暴露） ③下一次 maintain 归档失效件 ④头部写明产出时间与适用范围 |
| 数字/结论失真（写中途快照或未验证结论） | 模板头部两条纪律（终态数字 + 不得写未验证结论）；与 P67/R3 同类的"声明↔执行"治理取向一致 |
| 范围蔓延到 Option A（顺手加 workflow/command） | 本提案**明确排除 A**；确需命令面时另行立项 |
| 与 P62（提交可追溯）等的关联被过度绑定 | 互补但不合并：P62 管提交信息，本提案管交接产物 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户于 2026-09-23 指示立案） | 2026-09-23 |