# Change Proposal: P79 — AIC Contract Evaluator V1（develop Phase 4 单点验证）

| Field | Value |
|---|---|
| Status | **Implemented**（V1 完成，2026-09-30） |
| Type | Evaluation / Experiment（验证「AIC 能否对一个明确、可机械判定的 Phase Contract 做独立求值」，**不含业务完成性判定**） |
| Author | AI Maintainer |
| Created | 2026-09-29 |
| Reference | 三方评委建议 + 用户逐项裁定（D1–D5）· 现状证据见 §2 · 前置提案 `reports/P76-PHASE-CONTRACT.md`（Phase schema）· `reports/P77-HINDSIGHT-EVALUATION.md` §13.4（「有实测数字的错误结论比无结论更危险」） |

---

## 1. 核心验证问题（锁定）

> **AIC 能否对 `develop` Phase 4 的一个明确、可机械判定的 criterion，进行独立求值，并稳定产生 `completed` / `not-satisfied` / `undetermined` 三态结果与 JSONL 审计记录？**

首个 criterion：

> **Completion Report 存在** —— `workspaces/<project>/openspec/changes/<change>/completion-reports/` 下有文件。

**明确声明**：这只证明**产物 Contract 满足**，不证明**工程任务已完成**。措辞纪律见 §8。

---

## 2. Scope / Repository Boundary

本提案**仅针对当前实际存在并经实测验证的结构**：

```text
<workspace>/
├── ai-system/        # CLI · tools/checks/ · templates/runtime/ · workflows/ · governance/
├── workspaces/       # 机器层运行态与 OpenSpec 产物
├── logs/             # 运行诊断（机器层，仓库外）
└── metrics/          # 指标快照（机器层，仓库外）
```

**不作为实施对象的路径**（原提案提及但本仓不存在）：

| 路径 | 状态 |
|---|---|
| `aic/` | **不存在** |
| `ai-runtime/` | **不存在**（runtime 模板在 `ai-system/templates/runtime/`） |
| `ai-system/projects/` | **不存在**（业务代码在工作区层 `~/ws/ai-workspace/projects/`） |

本文件明确写入此边界，避免日后有人按原提案路径重新产生歧义。

---

## 3. 现状证据（全部实测）

### 3.1 Phase 状态：无存储

- `tools/checks/phase_contract.py` 是**编写期静态门禁** —— 它校验 `phase("6.5").passed` 引用的 id 是否声明了 `pass_criterion`，**不读取任何运行期状态**
- `cli/services/prompt_builder.py:_phase_contract_section` 把 Phase 表**渲染进 prompt**，Activation 条件由 **Agent 自己求值**
- `grep -rln "phase_status|completed_at" cli/ tools/ config/` → **零结果**
- `runtime-base.md` 声明的 5 态（Initialized/Running/Paused/Failed/Completed）在 `cli/` `tools/` 中**零引用**

### 3.2 门禁看不到运行期产物（结构性根因）

| 事实 | 证据 |
|---|---|
| Runtime 产物落在 `workspaces/<project>/openspec/changes/<id>/completion-reports/` | `runtime-develop.md:338` |
| `workspaces/` 在**仓库外** | 实测仓库内无 `workspaces/` |
| `check.py` 扫描根 = 仓库根 | `checks/base.py: ROOT = HERE.parent` |

**推论**：18 项门禁全部只读仓库内 tracked 文件。Completion Report、Task Card 勾选状态、Phase 进度 —— **没有任何门禁把它们当输入**。

### 3.3 Phase Contract 覆盖率极低

| 事实 | 值 |
|---|---|
| 带 `phases:` 块的 workflow | **6** 个 |
| Phase 总数 | **42** 个 |
| 有 `activation` 的 | **5**（11.9%） |
| 有 `pass_criterion` 的 | **1**（2.4%） |

唯一实例（`workflows/bugfix.md:39`）：

```yaml
- id: "6"
  name: "Regression Verification"
  pass_criterion: "Verification Status = PASS (runtime-verify Phase 7/8 criteria)"
```

> 这直接决定了 V1 的规模：**求值器建好后只能对 1 个 Phase 工作**，其余 41 个需要先撰写可判定 criterion —— 属 V1 之外的延后项（§7）。

### 3.4 运行频次（用于选择试点）

| workflow | 运行次数 | 有 `phases:` 块 |
|---|---|---|
| maintain | 24 | — |
| spec | 23 | **✗** |
| **develop** | **18** | ✓ |
| prepare | 9 | ✓ |
| change-impact | 6 | **✗** |
| review / release / bugfix | 2 各 | bugfix ✓ |

`develop` 是**最高频且有 `phases:` 块**的 workflow。`spec` 频次第二但无 Phase 块（P76 未覆盖它）。

### 3.5 `change-id` 不可从 project-id 推导

`workflows/develop.md` 的 Inputs 为「all derived from main-chain context」，但实测 `workspaces/<project>/contexts/project-context.yaml` **只含 `project.id`，无 `change-id`**。

实测 3 个真实目录：

| project-id | change-id | 同名 |
|---|---|---|
| `202610-cool-italent-sync-plus` | `202610-cool-italent-sync-plus` | ✓ |
| `202609-rpc_log-graceful_shutdown` | `202609-rpc_log-graceful_shutdown` | ✓ |
| `202609-housekeeping-log-volume-reduction` | `log-volume-reduction` | **✗** |

> **同名是 3 样本中的多数现象，不是契约。** 第三行是明确反例。

### 3.6 本仓已有的三档退出码约定（V1 必须遵守）

| 工具 | 约定 |
|---|---|
| `comment-lint.py:1086` | `2 if failures else (1 if reviews else 0)` |
| `format-check.py:609` | `2 if has_fail else (1 if has_warn else 0)` |

两处完全同构，且 `1 = 较软` / `2 = 较硬`。**V1 不引入 `exit 2`**，避免仓内出现两套「2」的语义。

### 3.7 JSON 作为输出格式已有先例

6 个工具提供 `--json` 输出：`comment-lint` / `context-audit` / `extensions-lint` / `knowledge-metric` / `maintain-delta` / `prompt-metrics`。

**JSON 在本仓是既有的机器可读*输出*格式，不是协议。**

---

## 4. 已裁定约束（D1–D5，不再开放讨论）

| 决策 | 选择 | 结论 |
|---|---|---|
| **D1** | A‴ | 试点 = `develop` Phase 4 Completion **单个 Phase**（高频可评判 + 最小） |
| **D2** | A | 执行记录 = 追加式 JSONL；**写入者是 AIC 求值器，非 Agent** |
| **D3** | A′ | 三终值 `completed` / `not-satisfied` / `undetermined`；**不引入 MUST/SHOULD/MAY**；`undetermined` **不可静默通过** |
| **D4** | A″ | V1 只有 AIC 侧求值器，**不建 Agent Tool 表面** |
| **D4.1** | A′ | **不改变全仓既有 exit code 语义**；不引入 `exit 2` |
| **D5** | A″ | stdout 人读 + 严重度前缀；**结构由 JSONL 承载**；V1 **不提供 `--json`** |

### 4.1 D3 的来源与一处实质修正

D3 采纳**三方评委建议 → 我方采纳**。其中一处是 AI 原分析遗漏的：

> `undetermined` 不是「弱完成」，不能静默通过 —— 它必须**阻断**依赖该 criterion 的 Phase 完成判定。

AI 原方案是「只暴露、不预防」，存在逃逸路径：

```text
criterion 不可判定 → undetermined → Agent:「无法判断，继续」→ 下一 Phase
```

该路径使可靠性增益归零。修正为：**V1 不在写入时预防，但判定时必须阻断。**

### 4.2 一条被采纳的原则

> **状态不是义务等级。**
> `MUST/SHOULD/MAY` 描述「要求有多强」= 规则语言；`completed/not-satisfied/undetermined` 描述「系统能确定什么」= 执行状态。

否决 MUST/SHOULD/MAY 的三条依据：

1. 本仓实际使用 `MUST` **82** 次，`SHOULD` / `MAY` 各 **4** 次（≈20:1:1）—— 事实上是二元
2. `pass_criterion` 是**单一字符串**，不是义务集合 —— 求值器不需要「哪几条是 MUST」
3. `gates.optional` 已存在「声明了语义但无消费者」的问题（`main_chain_caps.py` 唯一接口读 `capabilities:`，**不读 `gates:`**）—— 不应再引入同类未落地语义

### 4.3 职责分离（V1 与后续门禁不混）

```text
V1 Runtime           → 如何面对 undetermined（不静默通过）
Future phase_contract 门禁 → 如何防止不可判定 criterion 进入运行期
```

---

## 5. Input Contract

```text
AIC Evaluator
  required inputs:
    project
    change
    task

  missing any of the three
    → verdict=undetermined
    → reason=input-missing
    → exit 1
```

求值器**不得推导** `change-id` 或 `task-id`，二者均为显式入参。

| 入参 | 来源 | 依据 |
|---|---|---|
| `project` | 显式传入 | 现有 workflow input |
| `change` | 显式传入 | §3.5 —— project-id 与 change-id 同名只是 3 样本中的多数现象，`202609-housekeeping-log-volume-reduction` / `log-volume-reduction` 构成明确反例 |
| `task` | 显式传入 | **复用** `workflows/develop.md` 已声明的 Task ID input（`auto-derived (read from Task Card)`），**非新概念** |

| 方案 | 判定 | 理由 |
|---|---|---|
| 显式 `project + change + task` | ✅ | 最小、确定、无猜测；让「入参缺失」成为 `undetermined` 的**真实触发路径** |
| 从 project 推导 change | ❌ | 把偶然命名规则升格为契约 |
| 建立 change-id 权威映射 | ❌ | 超出 V1（属 dev-setup / prepare 职责） |
| 判定「目录非空」而不需要 task | ❌ | **确定性假阳性** —— 见 §12 |

---

## 12. Criterion 可判定性审查（2026-09-29 实测）

criterion 写入后按四条判据审查。**前三条不足以排除缺陷** —— 审查过程中正是漏掉第四条，产出了一个确定性假阳性。

### 12.1 四条判据

| # | 判据 | 含义 |
|---|---|---|
| 1 | **Observable** | 能观察到客观事实 |
| 2 | **Deterministic** | 不依赖 LLM / Agent 自述 |
| 3 | **Mechanically Evaluatable** | 能由求值器机械判断 |
| 4 | **Execution-Isolated** | **历史状态不能伪造本次执行成功** |

第 4 条由用户裁定追加。没有它，「文件存在 → completed」会被读成「本次 Phase 产生了文件 → completed」，而 P79 的全部目的恰恰是后者。

### 12.2 第一版 criterion 被判不通过（保留记录）

```yaml
pass_criterion: "Completion Report Directory Non-Empty (...)"
```

**实测证据**：

| change | 文件数 | 日期跨度 |
|---|---|---|
| `202610-cool-italent-sync-plus` | 14 | Sep 2 – Sep 4 |
| `202609-rpc_log-graceful_shutdown` | 8 | Sep 29 – Sep 30 |
| `202610-public-security-storage-…` | 16 | Sep 4 – Sep 28 |

文件名为 `T-001`…`T-045` —— **一个 change 跨多张 Task Card，目录在第 45 张卡跑完后仍非空**。

**后果**：本次 Phase 4 完全未执行时，求值器仍返回 `completed`。这是**确定性假阳性** —— 比 `undetermined` 更危险，因为它携带 exit 0。

判据 1/2/3 全部通过，**仅判据 4 不通过**。

### 12.3 Task → Completion Report 映射的实测核查

| 问题 | 答案 |
|---|---|
| Task Card 的 ID 形式 | **两套**：`T-NNN.md` **116** 个 · `<n>.<m>.md` **18** 个（全部集中在 `202610-qa-housekeeping-optimization`，且与 `T-` 系**同目录并存**） |
| Completion Report 命名 | **两套且与 Card 同构**：`T-NNN-completion-report.md` 44 个 · `2.x-completion-report.md` 4 个 · 另有 2 个非 report 文件（`T-011-L3-check-log.md`、`completed-cards-walkthrough-log-20260909.md`） |
| 能否机械确定映射 | **结构上能**：`<change>/tasks/cards/<task-id>.md` ↔ 同 change 下 `completion-reports/<task-id>-completion-report.md`，ID 原样透传 |
| 是否有**成文**命名规则 | **没有**。`grep -rn "completion-report" governance/ templates/ workflows/ skills/` 只命中**路径**；`runtime-develop.md:337-339` 只规定存放目录，**未规定文件名** |
| `T-{task}-…` 可否当契约 | **不可**。116:18 两套并存，假设 `T-` 前缀会在 `qa-housekeeping` 类项目上失效 |

用户担心的「T-011 对 2.4 只能人工理解」**不存在** —— 两套 ID 是项目级差异，各自内部严格同构。

### 12.4 `not-satisfied` 是真实可达状态

`202609-rpc_log-graceful_shutdown` 实测：11 张 Task Card、8 份报告，**T-009 / T-010 / T-011 无报告**；反向（报告无 Card）为零。

故三态在真实数据上均可达，不是理论构造。

### 12.5 最终 criterion

```yaml
pass_criterion: "Completion Report for <task> exists (workspaces/<project>/openspec/changes/<change>/completion-reports/<task>-completion-report.md)"
```

**严格匹配是刻意的**（裁定 A1）：宽松匹配（`*<task>*report*.md`）会违反判据 2（Deterministic）。

**已知代价**：命名不合规（如 `T-011-report.md` 漏 `-completion`）会产生**假阴性** —— 实际已完成但求值器返回 `not-satisfied`。该代价**记入 §9.2 Layer 2，不在此处绕过**。补命名规则属 runtime 职责，**本轮不改 runtime**。

---

## 6. 求值结果模型

### 6.1 四层职责

| 层 | 形态 | 职责 |
|---|---|---|
| Exit code | `0` / `1` | 门禁是否通过 |
| stdout | 文本 + `[PASSED]` / `[NOT-SATISFIED]` / `[UNDETERMINED]` 前缀 | 人、Agent、日志 |
| JSONL record | 结构化 `verdict` + `reason` | AIC 巡检 + 后续机器处理 |
| `--json` | **不提供** | 待真实机器消费者出现 |

> **stdout 前缀是稳定的人类可读标识，不是机器协议。** 因此不会出现「巡检脚本去解析 stdout 文本」—— 与 P77 §14.4 判为不可取的「门禁读自由文本字段」保持一致。

### 6.2 术语

```text
exit 0  verdict=completed

exit 1  verdict=not-satisfied     reason=<诊断>

exit 1  verdict=undetermined      reason=input-missing | criterion-not-evaluable | ...
```

> **exit code 表达过程/门禁结果；`verdict` 表达 Contract 判定结果。**
> 不使用 `result` 作为第二套术语（会与 D2 的 JSONL 字段 `verdict` 冲突）。

### 6.3 `undetermined` 的两个 reason

```text
undetermined
├── input-missing            输入不完整（project/change 缺失）
└── criterion-not-evaluable  输入完整，但 Contract 本身无法判断
```

两者同为 `undetermined`，**原因可区分**。`reason` 是诊断信息，**不是第四种 verdict**。

它们分别验证 D3 的两个不同边界：**输入不完整导致无法判断** vs **输入完整但 Contract 本身无法判断**。

### 6.4 执行记录格式

```json
{"execution_id":"...","project":"...","change":"...","phase":"...",
 "verdict":"completed|not-satisfied|undetermined","reason":"...",
 "evidence":[],"ts":"..."}
```

落点遵循 `tools/runtime_state.py` 已自述的 SSOT：**工作区层、仓库之外**（2026-09-24 事故后确立）—— 任何 `git clean -fdx` 结构性碰不到。

追加式、含 watermark 语义的先例见 `metrics/by-machine/<id>/knowledge-runs.jsonl`（P71）。

---

## 7. V1 明确不做

| 不做 | 归入 |
|---|---|
| AgentAdapter Contract | 延后。无 Extension 时无独立价值；`config/providers.yaml` + `cli/services/agent_detect.py`（7 个已知 agent）已满足 Agent Independence |
| Tool API（MCP / JSON-RPC） | 延后。Agent↔AIC 之间**无结构化通道**（`cli/main.py:291` 用 `subprocess.call(shell=True)` + 剪贴板），且 0 个真实调用方 |
| Execution 一等实体（ID + 5 态 + 迁移） | 延后。V1 只需回答「判定过没有」 |
| MUST/SHOULD/MAY 义务模型 | **否决**（§4.2） |
| `--json` 输出 | 延后（§6.1） |
| `exit 2` | **否决**（§3.6） |
| `criterion 必须可判定` 静态门禁 | 延后至 `phase_contract` 候选门禁 |
| 为其余 41 个 Phase 撰写 criterion | 延后 |
| 为 develop Phase 1/2/3 撰写 criterion | 延后（见 §8.2） |
| MCP / Pi / DSh / Qocder Extension | 本轮禁止 |
| 改 `runtime-base.md` 的 8 个 Runtime API | 本轮禁止 |

---

## 8. 措辞纪律（写入代码注释与报告）

### 8.1 criterion satisfied ≠ Phase completed

求值器得到 `completed` 时，表达的是：

> **Contract criterion satisfied**

**不是**：

> Agent 的开发任务已经正确完成

否则 V1 会把「文件存在性」偷偷升级成「业务完成性」—— 这违反本提案自身的 Contract 设计。

**禁止的表述**：「Phase 4 已完成」。**正确的表述**：「Phase 4 的 criterion 满足」。

### 8.2 develop Phase 1/2/3 为何延后

| Phase | 名称 | 有无客观锚点 |
|---|---|---|
| 1 | Resolve Development Context | ✗ 「上下文解析正确」是语义判断 |
| 2 | Planning | ✗ 「计划被批准」是语义判断 |
| 3 | Invoke Implement Skill | ✗ 「技能被调用」是语义判断 |
| **4** | **Completion** | ✅ **产物存在性可机械判定** |

> 4 个 criterion 里有 3 个在 V1 阶段**必然返回 `undetermined`**，那将得到「3 个 undetermined + 1 个 completed」—— **看起来有结论，其实没验证到求值能力**。故 V1 只取 Phase 4。

### 8.3 `undetermined` 不得降级为 warning

```text
exit 1 + verdict=undetermined  → BLOCK + 暴露 Contract Gap
```

**不允许**出现「`undetermined` → warning → continue」。**退出码相同，不代表执行语义相同。**

---

## 9. 成功标准

### 9.1 Layer 1 —— Evaluator 能力（12 项：10 场景 + 2 异常分支，全部必配必失败负例）

场景集为**并集重分层**（2026-09-30 裁定）：原 §9.1 偏机制行为、F.1 偏输入边界，
两份各持一半。合并为 10 项并按「判定路径」而非「发现顺序」分层，避免只保留一份
再次出现「测试已覆盖但提案未完整表达」。

**A. 判定路径（criterion 可判定时）**

| # | 场景 | 期望 | 覆盖的裁定 |
|---|---|---|---|
| 1 | Completion Report 存在 | `completed` / exit 0 | D3 主路径 |
| 2 | Completion Report 不存在 | `not-satisfied` / exit 1 | D3 第二终值 |
| 3 | 历史 / 兄弟 report 污染（目录已有其他报告） | **不得误判 `completed`** | **判据 4** |

> 第 3 项是本提案最重要的真实发现：`rpc_log-graceful_shutdown` 实测同目录有 **8 份**
> 兄弟报告时，无报告的 `T-011` 仍判 `not-satisfied`。目录级检查会误判为 `completed`。

**B. 输入与契约边界（判定条件无法建立时）**

| # | 场景 | 期望 |
|---|---|---|
| 4 | `project` 缺失 | `undetermined` / `input-missing` |
| 5 | `change` 缺失 | `undetermined` / `input-missing` |
| 6 | `task` 缺失 | `undetermined` / `input-missing` |
| 7 | `workspace` / path 无法解析（含入参含分隔符） | `undetermined` / `input-missing` |
| 8 | criterion 不可判定（Phase 不存在 / 无 criterion / 文本被改） | `undetermined` / `criterion-missing` \| `criterion-invalid` |

**C. 机制性质（求值之外的承重断言）**

| # | 场景 | 期望 |
|---|---|---|
| 9 | 重复求值确定性 | 相同输入 → 相同 `verdict` / `evidence` / `execution_id`；JSONL 追加而非覆盖 |
| 10 | 审计记录落盘 + stdout 前缀一致 | 记录与判定同源；前缀与 `verdict` 恒定对应；stdout 无可解析结构 |

**D. 异常分支（fail-closed 原则）**

| # | 场景 | 期望 |
|---|---|---|
| 11 | evaluator 自身异常 | `undetermined` / `evaluator-error` / **记录仍写入** / exit 1 |
| 12 | 记录写入失败 | `undetermined` / 末条 `record-unwritable` / **首条保留原始 evidence** / exit 1 |

第 11、12 项验证的是 D3 最核心的 fail-closed 原则：

> **Evaluator 自己无法完成判定时，也绝不能让系统表现为 `completed`。**

两者均经**反向验证**（破坏后测试确实挂），非仅正向通过：

| 破坏方式 | 结果 |
|---|---|
| 把 record 失败的兜底改回覆盖 verdict | **4 个测试挂** |
| 把 crash 兜底改成返回 `completed` | **2 个测试挂** |

### 9.1.1 `evaluator-error` 的复核结论（2026-09-30）

复核发现：**该分支原先完全未被测试** —— 把它改成假通过（返回 `completed`）后，
原 37 个测试**仍然全绿**。经查，两处「引用」均未触达真实兜底：一处只是闭集清单
`EVIDENCE_TYPES` 的元素，一处是 monkeypatch 的**桩值**。

> **这与 `runtime-base.md` 的 8 个 Runtime API、`gates:` 注册表是同一种失败模式 ——
> 声明了，没有消费者。** 它一度被写入报告却未验证是否真会触发。

**已补两个真实测试**（注入异常 → 断言 exit 1 + `[UNDETERMINED]` + `evaluator-error`，
并断言**崩溃后记录仍存在**）。补后：再改成假通过 → **2 个测试挂**。

**保留必要性**：无该分支时，未捕获异常虽会以 exit 1 偶然 fail-closed，但
① **stdout 不会有任何前缀**，违反裁定 12（每个路径都必须发出三前缀之一）；
② **不产生审计记录**，Contract Gap 不可见。故正式纳入 Layer 1 异常分支。

### 9.2 Layer 2 —— 明确不验证（实验边界，非「V1 的不足」）

> **V1 的目标不是证明 develop Phase 4 的业务完成性，而是证明一个具有明确、可机械判定 criterion 的 Phase，可以被 AIC 独立求值，并产生可持久化、可审计的判定结果。**

V1 **不**证明 AIC 能判断：

- 代码是否正确
- 需求是否真正完成
- 测试是否充分
- Agent 是否进行了正确的工程行为

这些都需要更完整的 Phase Contract。

特别是：

- **`Task Card fully checked`（Exit Criteria 的另一半）无判定语义** —— 谁都能打勾、无人验证。V1 **不**触碰它。
- **报告文件名不合规导致假阴性**（§12.5）—— 严格匹配是判据 2 的代价。命名规则属 runtime 职责，本轮不改。
- **Task ID 两套形态**（`T-NNN` / `<n>.<m>`，§12.3）—— 求值器原样透传，不假设 `T-` 前缀。若某项目引入第三套命名，criterion 会失效并需重裁。

### 9.3 验证方式

每条 Layer 1 场景一个**必失败**的负例测试（`policies/quality-gates.md` §Writing a Gate That Can Be Proven to Fail）：逐条禁用求值路径 → 对应用例必须失败 → 还原全绿。**不可省。**

---

## 10. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **伪 Contract** —— 造出第二个 `runtime-base.md`（8 个 API / 零实现）。本仓已生产过三次此类声明：①`runtime-base.md` 的 8 个 Runtime API ②Phase `activation` 条件由 Agent 求值 ③`gates:` 注册表无消费者 | V1 交付**可运行的求值器 + 必失败负例**，而非 schema。第 4 条清单在 §9.1 |
| R2 | **`undetermined` 被静默通过** —— 可靠性增益归零 | §8.3 明确 BLOCK；场景 3/4 必测 |
| R3 | **措辞失守** —— 把「criterion 满足」写成「Phase 完成」 | §8.1；代码注释与报告须用规定表述 |
| R4 | 单点结论被外推 —— 用 1 个 criterion 宣称「AIC 能判定完成」 | §9.2 的 Layer 2 须与 Layer 1 同等显著；P77 §13.4 的判据（有数字的错误结论最难被识别） |
| R5 | `change-id` 归属漂移 | §5 要求显式传入，不推导；`reason=input-missing` 使漂移可见 |
| R6 | 记录丢失（`logs/` 曾被误删约 200 份） | §6.4 落工作区层、仓库外，遵循 `runtime_state.py` SSOT |
| R7 | 求值器被后续误当作通用执行框架 | 试点限于单一 criterion 形态（产物存在性）；V1 不接受第二类 criterion 而不重新裁定 |

---

## 11. 若 V1 成功

顺序**必须**是：

```text
Phase 4 稳定求值
      ↓
更多真实 criterion（逐个，每类形态单独验证）
      ↓
phase_contract 静态门禁（criterion 必须可判定）
      ↓
其他 Phase
      ↓
更强的完成性判定
```

**不得**在 V1 成功后一次性铺满 42 个 Phase —— 每类 criterion 形态（存在性 / 状态值 / 内容匹配）需要**分别验证求值器**。

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| 外部评委（三方） | **建议** | 提出「来源与裁定严格分开」；并给出 D3 的关键修正：`undetermined` 不能静默通过，否则 Agent 会说「无法判断，继续」，可靠性增益归零 |
| User | **Approved（D1–D5 + Input Contract + 措辞纪律）** | 2026-09-29 逐项裁定：D1 A‴（develop Phase 4 单点）· D2 A（追加式 JSONL，写入者为求值器）· D3 A′（三终值，不引入 MUST/SHOULD/MAY）· D4 A″（不建 Tool API）· D4.1 A′（不改全仓 exit code 语义）· D5 A″（stdout 人读 / JSONL 机器读 / 不提供 --json）· Input Contract A（显式 project+change，禁止推导 change-id）· 措辞纪律（criterion satisfied ≠ Phase completed）· Layer 2 写成有意识的实验边界 |
| User | **裁定 criterion 审查结论** | 2026-09-29：①criterion 方向采纳 **A**（task 级），但**先核查 Task→Report 的机械映射，不允许 AI 假设 `T-{task}-…` 就是契约** ②Input Contract 扩为 `project + change + task`（`task` 复用已有声明，非新概念）③**不引入 mtime / watermark** ④**不补命名规则**（runtime 职责）、不改 runtime、不写 evaluator、不提交 ⑤**采用 A1**：严格匹配 `<task-id>-completion-report.md`，假阴性记入 Layer 2 ⑥**evaluability 判据升级为四条**，新增 **Execution-Isolated**（历史状态不得伪造本次执行成功）—— 用户指出原三条「不足以排除这类缺陷」 |
| AI | **criterion 审查（已应用）** | 首版「Directory Non-Empty」按原三条判据会判通过，**但实测出确定性假阳性**（目录跨多张卡累积，最多 16 文件）→ 补第 4 条判据后改写为 task 级。Q1–Q4 核查见 §12.3：Task ID **两套**（116:18）、Report 命名两套且与 Card 同构、**无成文命名规则**（仅规定目录）、`T-` 前缀不可假设；`not-satisfied` 在真实数据上可达（11 卡 8 报告）。门禁：check.py PASS、test_phase_contract 15/15 OK |
| AI | **Proposed** | 证据见 §3。**两处更正自身先前结论**：①「117 个 Phase 都有 pass_criterion」错误 —— 实测 42 个中仅 1 个（2.4%），D1 因此从「4 个 Phase」收敛到「1 个」②「JSON 在本仓无位置」错误 —— 6 个工具已有 `--json` 输出，先例存在（D5 据此调整表述） |

---

## Implementation Record (2026-09-30) — V1

### 交付物

| 文件 | 内容 |
|---|---|
| `workflows/develop.md` | Phase 4 唯一 `pass_criterion`（task 级精确匹配） |
| `tools/contract-eval.py` | 求值器：Input Resolver · Criterion Resolver · Evaluator · Recorder · CLI |
| `cli/tests/test_contract_eval.py` | 37 例，含逐条短路自证 |
| `tools/README.md` | 工具登记 |

### 裁定落点

| 裁定 | 实现 |
|---|---|
| D1 A‴ | 单 Phase 单 criterion；`KNOWN_CRITERION` 常量逐字比对 |
| D2 A | `metrics/by-machine/<id>/contract-eval.jsonl`，追加式；`execution_id = sha256("project\|change\|task\|phase")[:16]`（派生值，非实体） |
| D3 A′ | 三终值；`evidence[].type` 为**唯一**诊断分类；**无 `reason` 字段** |
| D4 A″ | `tools/` 独立脚本 —— 非 `aic-*` 命令、非门禁、无 Tool/MCP |
| D4.1 A′ | 仅 exit `0` / `1` |
| D5 A″ | stdout 三前缀；**无 `--json`**（有负例断言传入即 SystemExit） |
| Input Contract | `project` + `change` + `task` 全显式，**零推导**；`workspace` 可缺省取 `runtime_state.workspace_root()` |
| criterion 归属 | 求值器**自行读取** frontmatter 并逐字校验，**不接受调用方注入**（有测试断言 `evaluate()` 签名无 `criterion` 参数） |
| 解析复用 | 复用 `checks/phase_contract._frontmatter/_parse_phases` —— Phase 定义只有一份 |

### 测试抓到的真实 bug：记录失败时的假通过

`finalize` 原为：

```python
payload = dict(result)          # ← 复制了 verdict
...
failed.update({k: v for k, v in payload.items() if k != "evidence"})
```

`payload` 携带 `verdict`，`update` 把它**覆盖回 `completed`** —— 即**记录写入失败时仍返回 `completed` / exit 0**。

这是 `test_record_unwritable_never_yields_completed` 抓到的。**它正是裁定 3（记录成功是判定生效前提）要关闭的那扇门**，而实现自己把它推开了。修正为排除 `verdict` 与 `evidence` 两键。

> 该 bug 在纯人工审阅下不会暴露 —— 三个断言（verdict 变 undetermined / 最后一条是 record-unwritable / 首条保留原始 evidence）中前两个都会通过，只有第三个会失败。

### 实测（真实 workspace，非 fixture）

| 场景 | 输出 | exit |
|---|---|---|
| `T-001`（Card+Report 都在） | `[PASSED] … report-found` | 0 |
| `T-011`（Card 在、无 Report，同目录另有 8 份兄弟报告） | `[NOT-SATISFIED] … report-missing` | 1 |
| `T-999`（Card 不存在） | `[UNDETERMINED] … task-card-missing` | 1 |
| 缺 `task` | `[UNDETERMINED] … input-missing task` | 1 |
| `2.1`（第二套 ID 形态） | `[PASSED] … report-found` | 0 |

**判据 4（Execution-Isolated）实证**：同目录 8 份兄弟报告存在时，`T-011` 仍判 `not-satisfied` —— 目录级检查会误判为 `completed`。

**第二套 ID 形态实证**：`2.1` 判 `completed`，证明未假设 `T-` 前缀。

**确定性实证**：`T-011` 连续两次求值产生同一 `execution_id`（`de1619d104cc4a79`），JSONL 追加两行。

### 偏离设计稿的一处（实现更严格）

设计稿 §1.3 预测「`--task "T-001 "` 原样透传 → `not-satisfied`」。实现改为**显式拒绝** → `input-missing`。

两者都不是静默修正，但拒绝在**输入边界**指出了真实问题（入参格式错误），优于透传后在下游报「产物缺失」。测试与实现取一致，并记录该偏离。

### 已知限制（如实记录）

| 限制 | 说明 |
|---|---|
| 报告文件名不合规 → **假阴性** | §12.5 已声明；测试 `test_non_conforming_filename_is_a_known_false_negative` 显式断言其为 `not-satisfied`，使其可见而非退化为 bug report |
| `execution_id` 不含时间 | 同一任务的多次判定靠 `ts` 排序区分；Execution 实体属 V1 之外 |
| append 原子性 | 保证仅为「单次 `write()` 调用」这一实现事实，**非**跨进程锁契约。全仓 `open(…,"a")` 此前零命中 —— 这是 V1 引入的新机制 |
| Task ID 第三套形态 | 若引入，`criterion` 求值会失效并需重裁 |
| `evaluator-error` 为 8 类 evidence 之一 | 由用户给的 7 类扩展而来（崩溃无类型可用）；属**最小扩展**，可撤销 |

### 门禁

全量单测 **786 OK**（749 → 786，+37）· check.py PASS（2 WARN 既有基线）·
workflow-command-audit 0/0/0 · quick-check OK/findings 0 · path-audit 0 broken ·
repo-lint 0 BLOCKER / 0 ERROR · 短路自证 11/11（已固化为 4 个常驻测试）

---

## P80 裁定：No-Go（2026-09-30）

对 `bugfix` Phase 6 的 `pass_criterion` 做 **SSOT 审查**（只查不改），结论 **不成立**。
本节记录 No-Go 及其重开条件，避免同一议题被反复重开。

### 被审查的 criterion

```yaml
# workflows/bugfix.md:39
pass_criterion: "Verification Status = PASS (runtime-verify Phase 7/8 criteria)"
```

### 四问的答案

| 问 | 答案 | 证据 |
|---|---|---|
| PASS 事实存在哪里 | `workspaces/<project>/verify/<task>/verification-report.md` 的**一行 Markdown 文本**。无独立状态文件、无 schema、无 frontmatter 字段 | 55 份产物；`grep -rln "verification_status" --include=*.py/*.yaml/*.json` → **零命中** |
| 谁产生 | **Agent**。`runtime-verify.md:298` 的 `## Verification Status` 是**空标题模板** —— 无取值规定、无格式、无产出指令 | 该行是给 Agent 填充的槽位 |
| 谁消费 | **无人**。`grep "Verification Status" tools/ cli/` → **零消费者**；`runtime-bugfix.md:390` 仅在 `Return:` 中列出该字段名 | 无机器读取方 |
| 能否脱离 Agent 自述确定性读取 | **不能** | 见下 |

### 决定性证据

54 份含该字面量的产物中，状态行有 **7 种散文形态**：

| 形态 | 份数 |
|---|---|
| `Verification Status: **PASS**` | 24 |
| `Verification Status: PASS**` | 12 |
| `Verification Status**: ✅ **PASS**` | 9 |
| 带尾注（`（零改动核验卡）`、`（批量版）`、`→ M4 全链收口`、`（1 待办转发布清单…）`） | 各 1 |

**且有一份的行内同时含 `PASS` 与 `FAIL`**：

```
workspaces/202610-cool-italent-sync-plus/verify/T-021/verification-report.md:7
## Verification Status: **PASS**（含一轮 FAIL→develop→复验闭环）
```

任何基于 `PASS`/`FAIL` 子串的判定器都会误判。另有 1 份（55 份中）完全无该行。

### 四维验证中三维无机器证据

| 维度 | 机器可生成的事实 |
|---|---|
| Specification Verification | ❌ Agent 逐条判断 MUST/SHALL |
| Contract Verification | ❌ Agent 判断 |
| Scenario Verification | ❌ Agent 判断 |
| Test Verification | ⚠️ 底层有 surefire XML，但 Phase 5 指令为 `Verify: …` + `Generate: Test Verification Report` —— **仍是 Agent 写报告** |

即使退到底层，`projects/*/target/surefire-reports/` 是 `target/` 下的**构建产物**（gitignored），**不与 task/change 绑定**，且不含其余三维。**无法从中确定性推出 `Verification Status = PASS`。**

### 判据核对

| 判据 | 结论 |
|---|---|
| 1 Observable | ⚠️ 可观察到，但观察到的是散文 |
| 2 Deterministic（不依赖 LLM / Agent 自述） | ❌ **产出者即 Agent** |
| 3 Mechanically Evaluatable | ❌ 7 种格式 + 尾注 + 内嵌 FAIL |
| 4 Execution-Isolated | 不适用（未到该层） |
| 5 输入与状态来源有明确 SSOT | ❌ **零机器消费者** |

### 关键：98% 覆盖率不是问题

**54/55 份含该字面量（98%）—— 但这 98% 全部是 Agent 生成的非结构化文本。**

> 覆盖率衡量的是「Agent 有多常写这一行」，不是「是否存在机器可判定的状态」。

必须连同此句一并留档，否则日后有人看到 `54/55` 极易误判为「已具备机器判定基础」。

### 硬边界

> **不得通过解析历史 `verification-report.md` 中的 Agent 自述来构造 P80 evaluator。**

违反该边界将把自述固化成契约，且 55 份历史产物中那 1 份内嵌 `FAIL` 的会立刻成为不合格样本 —— 而它正是需要保留的反例。

**同时明确不做**：❌ 改造 `runtime-verify` 以配合 P80 · ❌ 为 P80 增加解析规则 · ❌ 进入 evaluator。

### 重开条件（任一满足）

1. 出现**机器生成且 task/change 绑定**的验证状态
2. 四维验证中出现足够的机器可判定锚点
3. `Verification Status` 获得 **schema + 生产者 + 消费者 + 格式门禁**（使 7 种形态收敛为 1 种，且尾注被排除）

### 审查方法上的一处自我更正

审查中我一度统计「198 份中仅 19 份有状态行」并准备据此断言覆盖率极低。**该数字错误** —— 198 是所有 verify 相关文件（含 `specification-verification.md` 等），非 `verification-report.md`。

精确值：**55 份 `verification-report.md`，54 份含该字面量，1 份缺失**。

覆盖率其实很高，**但结论不变** —— 问题不在覆盖率，而在**产出者与格式**。高覆盖率不等于可机械解析。

（这是本会话第二次因未验证即下结论而报错，第一次是 P79 之前误判 `last_findings` 为单值字段。）
