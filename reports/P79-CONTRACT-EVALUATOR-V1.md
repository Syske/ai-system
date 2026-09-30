# Change Proposal: P79 — AIC Contract Evaluator V1（develop Phase 4 单点验证）

| Field | Value |
|---|---|
| Status | **Approved** |
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

## 5. Input Contract（V1 内定，非独立决策项）

```text
AIC Evaluator
  required inputs:
    project
    change

  missing project or change
    → verdict=undetermined
    → reason=input-missing
    → exit 1
```

**求值器不得猜测 `change-id`。** 依据 §3.5：project-id 与 change-id 同名只是 3 样本中的多数现象，第三行构成明确反例。

| 方案 | 判定 | 理由 |
|---|---|---|
| 显式 `project + change` | ✅ | 最小、确定、无猜测；且让「入参缺失」成为 `undetermined` 的**真实触发路径** |
| 从 project 推导 | ❌ | 把偶然命名规则升格为契约 |
| 建立 change-id 权威映射 | ❌ | 超出 V1（属 dev-setup / prepare 职责） |

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

### 9.1 Layer 1 —— Evaluator 能力（必须全过）

| # | 场景 | 期望 | 覆盖的裁定 |
|---|---|---|---|
| 1 | Completion Report 存在 | `exit 0` + `verdict=completed` | D3 主路径 |
| 2 | Completion Report 不存在 | `exit 1` + `verdict=not-satisfied` | D3 第二终值 |
| 3 | criterion 本身不可判定 | `exit 1` + `verdict=undetermined` + `reason=criterion-not-evaluable` | **D3 的核心语义** |
| 4 | `change` 未提供 | `exit 1` + `verdict=undetermined` + `reason=input-missing` | §5 Input Contract |
| 5 | 同一 criterion + 相同 workspace state 重复求值 | 结果**完全一致**（确定性） | §1 核心问题 |
| 6 | 记录落盘 | 追加一条 JSONL，含 `verdict` / `reason` / `evidence` / `ts` | D2 |
| 7 | stdout 前缀与 `verdict` 一致 | 两者不得矛盾 | D5 |

> 场景 3 与 4 缺一不可 —— 若只有「存在 → completed / 不存在 → not-satisfied」，则 D3 最关键的 `undetermined` 语义未验证。

场景 5 的必要性：若求值结果随调用时刻变化，则「确定性」这一核心主张不成立。`knowledge-runs.jsonl` 的 watermark 机制提供了「哪些 workspace 日志已被计入」的先例。

### 9.2 Layer 2 —— 明确不验证（实验边界，非「V1 的不足」）

> **V1 的目标不是证明 develop Phase 4 的业务完成性，而是证明一个具有明确、可机械判定 criterion 的 Phase，可以被 AIC 独立求值，并产生可持久化、可审计的判定结果。**

V1 **不**证明 AIC 能判断：

- 代码是否正确
- 需求是否真正完成
- 测试是否充分
- Agent 是否进行了正确的工程行为

这些都需要更完整的 Phase Contract。

特别是：**`Task Card fully checked`（Exit Criteria 的另一半）无判定语义** —— 谁都能打勾、无人验证。V1 **不**触碰它。

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
| AI | **Proposed** | 证据见 §3。**两处更正自身先前结论**：①「117 个 Phase 都有 pass_criterion」错误 —— 实测 42 个中仅 1 个（2.4%），D1 因此从「4 个 Phase」收敛到「1 个」②「JSON 在本仓无位置」错误 —— 6 个工具已有 `--json` 输出，先例存在（D5 据此调整表述） |
