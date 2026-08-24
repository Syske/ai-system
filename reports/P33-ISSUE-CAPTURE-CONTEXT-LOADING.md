# Change Proposal: P33 — 日常运行中发现变更时的上下文加载触发规则（Issue Capture）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Governance（治理条款登记 + Context Loading 纪律，非结构改动） |
| Author | AI Maintainer |
| Created | 2026-08-24 |
| Reference | maintain on-demand/prepare 2026-08-24：核实日常主链 runtime 不加载 proposal-policy / OPERATIONS §12，导致运行中记录的提案不规范、维护兜底纠偏成本上升 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

日常单次运行（prepare/develop/spec/review/verify）中，当 AI 发现需记录的变更（doc drift、契约不一致、新缺口等）时，记录出的提案**不规范**，给后续 maintenance 巡检增加纠偏成本。

根源于 **Context Loading 缺口**：主链 runtime 继承 `templates/runtime/runtime-base.md`，其加载的治理仅 5 份——AI_OPERATING_RULES / SOURCE_OF_TRUTH / CONTEXT_LOADING / REPOSITORY_FIRST / REFLECTION_RULES。其中：

- **OPERATIONS.md（含 §12 变更管理流程）**：仅 `runtime-change-impact.md` 引用，主链 runtime 不加载。
- **proposal-policy.md（提案 7 节模板 / Status 状态机 / PROPOSALS.md 索引登记 / proposal-audit 门禁 / 报告登记纪律）**：**无任何 runtime 或 skill 引用**（仅出现在历史 log 与 tools/README）。
- AI_OPERATING_RULES 自身只提过一次 "proposal"（且在无关的「答后核查」节），不定义提案格式、不指向 proposal-policy。

后果：运行中冒出问题时，AI 只知道 Change Control 里「L3 → route to prepare/spec」这条路由，却不知道提案模板、状态机、索引登记、就地小修旁路、尺寸分流阈值，只能临场发挥 → 格式/流程不规范 → maintenance 靠 proposal-audit 兜底纠偏。**P32 即典型**：单行 doc drift 本应走就地小修旁路（maintain 命令 line 85 已允许），却立了完整 P 提案（7 节 + 索引 + 状态机）。

## 2. Root-Cause（根因分析）

非「缺原则」，而是「**缺一条加载触发**」。Small Changes / Minimal Change 原则已在 AI_OPERATING_RULES；proposal-policy §3 第 7 步「巡检回收」+ maintain 命令 Step 3「Proposal leftovers」已闭环运维检查（本次巡检已验证）。缺的是：

> 「**记录提案前，必须 JIT 加载 proposal-policy + OPERATIONS §12**」这条触发规则没有挂在任何**每天都被加载**的文档里。

proposal-policy 无法修自己的加载——它是被加载对象。触发规则必须落在**主链 runtime 都加载的** AI_OPERATING_RULES。属单点 Context Loading 纪律缺口，非架构问题。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| A. 在 runtime-base 基础上下文加载 OPERATIONS + proposal-policy | 每个 runtime 都常驻这两份 | 否决：违反 CONTEXT_LOADING「只加载任务所需」；对从不碰提案的 runtime（change-impact/code-review/部分 skill）是噪声与 token 负担；过度加载 |
| **B. AI_OPERATING_RULES 加「Issue Capture」触发条款（Recommended）** | 记录提案**前** JIT 加载 proposal-policy + OPERATIONS §12；附尺寸分流阈值 | 最小：规则只挂触发 + 阈值，细节仍留 proposal-policy（单一来源）；JIT 不增常驻负担；分层正确（Operating Rules 全局行为，每 runtime 都加载） |
| C. 新建 governance/ISSUE_CAPTURE.md 并由 runtime-base 加载 | 独立短文档常驻 | 否决：又给每 runtime 加常驻负担；且触发与细节仍需分置，徒增一层文件；违反 Minimal Change |

## 4. Recommendation（推荐方案 + 理由）

**方案 B**。理由：

1. **分层正确**：触发规则属全局 AI 行为 → Operating Rules；主链 runtime 都加载 AI_OPERATING_RULES，天然全覆盖。
2. **尊重 CONTEXT_LOADING**：JIT（仅「决定记录提案」那一刻加载一次），平时 0 常驻 token；不污染 runtime-base 基础上下文。
3. **单一来源**：细节（模板/状态机/门禁/分流阈值）仍留 proposal-policy，AI_OPERATING_RULES 只挂「何时加载 + 分流」，不重述。
4. **可验证**：下次 maintenance proposal-audit 应见「运行中立案」全合规（7 节齐 + 索引登记 + 状态机一致），兜底纠偏项下降。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改** 治理文件；批准后按 OPERATIONS §12 Implement 阶段执行。

1. `governance/AI_OPERATING_RULES.md` 的 Change Control 节末追加「Issue Capture」条款：

   > **Issue Capture（运行中发现需记录的变更时）**：
   > - 在记录任何提案**前**，JIT 加载 `governance/policies/proposal-policy.md` + `OPERATIONS.md §12`（单次，仅此刻）。
   > - 尺寸分流：单点 doc-drift / typo / 断链 / 文本对齐 → 经确认就地改 + 记 diagnostic-log + 维护报告「修复动作」节（**不立 P 提案**）；触及结构 / 契约 / 多文件 / 标准 / 新能力 → 按 proposal-policy §1 立 P 提案。
   > - 立案后即登记 `reports/PROPOSALS.md` + `reports/README.md` 对应表。

2. `governance/policies/proposal-policy.md` §1 末补「尺寸分流」小节，把上述分流阈值落为单一来源（与 maintain 命令 line 85 minor-fix 旁路对齐），并标注「触发规则见 AI_OPERATING_RULES Issue Capture」。

3. 回溯佐证：在 proposal-policy §1 注明 P32 为「本应就地小修、却走了完整提案机器」的反例，作为分流判定依据。

4. 不动 runtime-base / 各 runtime（避免常驻负担）；不动 CONTEXT_LOADING 主体（其 Per-Runtime Rules 不变）。

5. 不建 ADR（按 rfc/README 三条件：非 hard-to-reverse、非 surprising、无真实 trade-off——方案选择已由本提案记录，inline 级文本修正即可）。

## 6. Validation Plan（如何验证）

- `python tools/check.py` / `repo-lint.py` / `path-audit.py` 全绿（治理文本改动无结构影响）。
- `python tools/proposal-audit.py`：P33 登记一致、无新增 ERROR/WARN。
- `grep -rn "proposal-policy\|OPERATIONS" templates/runtime/runtime-base.md` 实施后**仍应无新增常驻引用**（确认未误改成 Option A）。
- `grep -n "Issue Capture" governance/AI_OPERATING_RULES.md` 命中新增条款。
- 行为回归：下一次日常运行发现 doc drift 时，AI 走就地小修旁路（diagnostic-log + 报告），不再立 P 提案；发现结构级缺口时，JIT 加载 proposal-policy 后按 §1 立案并登记索引。

## 7. Risks（风险与缓解）

- 风险低：纯治理文本 + JIT 加载纪律，无运行时/契约/数据影响。
- 缓解：实施时分流阈值措辞与 maintain 命令 line 85 对齐，避免二次漂移；若将来确有 runtime 需常驻提案规范（目前无），再单独评估（届时为真实新需求，非本提案范围）。
- 依赖：JIT 加载依赖 AI 在「决定记录提案」时刻自觉触发——条款须在 AI_OPERATING_RULES 显式、可 grep，便于巡检与 AI 自检。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-24 |

---

## Implementation Record

Approved per proposal-policy §2 + OPERATIONS §12 → Implement → Validate。方案 B：

1. `governance/AI_OPERATING_RULES.md` Change Control 节末追加「## Issue Capture (运行中发现需记录的变更时)」条款：记录提案前 JIT 加载 proposal-policy + OPERATIONS §12（单次、不进 runtime-base 常驻）；附尺寸分流阈值（就地小修 vs 提案）与立案登记要求；明示触发规则单一来源为本节、细节见 proposal-policy。
2. `governance/policies/proposal-policy.md` §1 末补「### 1.1 尺寸分流（Sizing Triage）」小节：分流判定表（就地小修 / 提案两类）+ P32 回溯佐证 + 与 maintain 命令 minor-fix 旁路同一阈值的单一来源声明。
3. 不动 runtime-base / 各 runtime / CONTEXT_LOADING 主体（确认未误改为 Option A）。
4. 未建 ADR（非 hard-to-reverse / 非 surprising / 无真实 trade-off）。

**Validation**（gate，fresh）：
- `grep -n "Issue Capture" governance/AI_OPERATING_RULES.md` → 命中新增条款。
- `grep -rn "proposal-policy\|OPERATIONS" templates/runtime/runtime-base.md` → 仍无新增常驻引用（确认 JIT、未误改 Option A）。
- `repo-lint.py` / `path-audit.py` / `quick-check.py` 全绿。
- `proposal-audit.py`：0 error / 0 warn；P33 Status=Implemented 与索引一致。
