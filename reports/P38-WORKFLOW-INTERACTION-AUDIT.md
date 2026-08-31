# Change Proposal: P38 — 逐 aic 工作流用户交互审计（wizard 交互序列/确认节奏/呈现）

| Field | Value |
|---|---|
| Status | **Implemented**（批次 1；批次 2 defer，见 Implementation Record） |
| Type | Enhancement（wizard 交互 UX 系统化审计；触及 cli/services/wizard + 工作流提示词，走 §12） |
| Author | AI Maintainer |
| Created | 2026-08-25 |
| Reference | 用户需求：后续逐个 aic 工作流评估必填参数和用户交互情况；P37 已覆盖「必填参数」维度（评估表全 15 + 批次 1 已实施），本提案专攻「用户交互情况」维度，与 P37 互补不重叠 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状 / 缺口）

P37 解决了「**哪些**参数必填/可选/自动推导」（输入契约层），但未覆盖「**如何**与用户交互」：
每个 aic 工作流的 wizard 交互体验是**逐工作流零散演进**的，无系统性审计：

- **提示序列/数量未统一**：有的工作流 2 步收完，有的多步连环问；同一类信息（项目/任务/分支）在不同工作流问法不一。
- **确认节奏不一**：有的收完即跑，有的中途二次确认；何时 recap、何时允许 abort 无约定。
- **可选字段呈现不一**：降为可选后，是「跳过不问」还是「带默认问一句」不统一（P37 批次 1 已把 5 工作流降可选，但呈现策略未定）。
- **中途检查点缺失**：长工作流（develop/review）无 mid-task checkpoint，与 ATTENTION_MANAGEMENT 未对齐。
- 另一台机器 f3e49dd 已零散做「输入界面中文化 + 交互提示优化」，但未做逐工作流系统性交互审计。
- **（2026-08-25 用户实证补充）澄清阶段「一次一个问题」从未被体验到**：该约束在
  governance/AI_USER_RESPONSIBILITY_CONTRACT.md:124,153、skills/bugfix/workflow.md:84、
  templates/runtime/runtime-review.md:109、runtime-spec.md:184 均有定义，但**实际构建的
  spec/bugfix/review/prepare 提示词中零命中**——`_skeletonize_runtime`（cli/services/prompt_builder.py:438）
  只保留「Phase 标题 + 首行要求」，行为类约束被裁剪，设计上依赖 agent 到达阶段时按需读全量模板文件，
  实际不发生；governance 合同则从不注入提示词。→ 审计需覆盖「行为约束是否真正到达提示词层」维度，
  而非仅 wizard 字段交互。

## 2. Root-Cause（根因分析）

- **P37 只到契约层**：P37 评估表只决定字段「必填/可选/推导」归属，未规定可选字段的呈现策略与交互序列。
- **wizard 无交互规范**：`cli/services/wizard/` 有 `_field_defaults`/`_previous_value` 等机制，但无「每工作流交互模式」约定，各工作流 frontmatter `inputs` 只声明字段，不声明交互。
- 属演进累积、非单一缺陷——需逐工作流审计后定交互模式。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 逐工作流交互审计 + 分模式处置（Recommended）** | 对每个工作流审计：提示序列/数量、确认节奏、可选字段呈现、中途检查点；产出交互评估表 + 实施 | 系统性、与 P37 评估表对齐（同 15 工作流维度）、直击体验不一 |
| B. 仅统一个别高频工作流 | 只审 develop/review | 快但不根治，无全量审计记录 |
| C. 引入全局「交互最小化」规则 | 如：可选字段一律跳过不问、仅必填问 | 原则好但需逐工作流落实，实际与 A 合并 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A + C 原则**，与 P37 对齐（同一 15 工作流维度，不同轴）：

1. **立原则**：可选字段默认「带默认问一句、可空回退」（既不强制也不隐身，保留用户覆盖权）；主链工作流在 spec→develop 间设 mid-task checkpoint（对齐 ATTENTION_MANAGEMENT）。
2. **逐工作流审计**（产出下表骨架），定交互模式：
   - 提示序列/数量（必填问几步、可选是否呈现）
   - 确认节奏（收完即跑 / 中途确认 / 结尾 recap）
   - 可选字段呈现（跳过 / 带默认问 / 显式列出）
   - 中途检查点（有/无、位置）
3. **与 P37 衔接**：P37「降可选/自动推导」的字段，其呈现策略由本提案定（P37 定归属、P38 定呈现）。
4. **wizard 支持**：复用既有 `_field_defaults`/`_previous_value`，零架构改动。

### 4.1 交互评估表（2026-08-25 审计定稿；数据源：`_fields_for` 实测 + `_steps` 状态机核对）

**已定原则（P38 §4 落地）**
- 可选字段呈现 = **带默认问一句、可空回退**（现状 wizard 已符合，确认为规范）
- 必填留空 = 重问当前字段不前进（`steps.py` 已实现，确认保留）
- 行为约束（澄清节奏/checkpoint）必须**到达提示词层**：`<!-- @keep -->` 骨架白名单（批次 1 已实施）

| Workflow | 提示序列/数量（必填+可选） | 确认节奏 | 可选字段呈现 | 中途检查点 | 行为约束到达提示词 |
|---|---|---|---|---|---|
| analysis | 1+2（Analysis Target 必填） | 收尾 launch 确认 | 逐项问、可空 | 无 | n/a |
| bootstrap | 0+1（Environment 带默认） | 收尾确认 | 默认值预填 | 无 | n/a |
| bugfix | 2+4 | 收尾确认 | Mode 带默认 | 无（澄清节奏见 runtime-bugfix，批次 2） | 部分（3+ 次失败 STOP 未 @keep） |
| change-impact | 2+4 | 收尾确认 | Base Branch 带默认 | 无 | n/a |
| code-review | 1+6 | 收尾确认 | Base Branch 带默认 | 无 | n/a |
| dev-setup | 0+3（全推导） | 收尾确认 | 逐项问（批次 2：静默推导候选） | 无 | n/a |
| **develop** | 0+3（全推导） | Phase 2 计划确认 + 收尾确认 | 逐项问（批次 2：静默推导候选） | ✅ **@keep checkpoint 已加**（~3 步一检） | ✅ |
| hotfix-test-doc | 1+3 | 收尾确认 | 逐项问 | 无 | n/a |
| knowledge | 1+2 | 收尾确认 | 逐项问 | 无 | n/a |
| **prepare** | 1+6（Change Request 必填，重入预填跳过） | 收尾确认 | 逐项问、可空 | 无 | ✅ **一次一个问题 + 多方案提议 @keep** |
| proposal | 1+4 | 收尾确认 | 逐项问 | 无 | n/a |
| release | 0+3 | 收尾确认 | 逐项问 | 无 | n/a |
| **review** | 0+2 | 收尾确认 | 逐项问 | 设计树逐分支走查（既有） | ✅ **Single question + Codebase-first @keep** |
| **spec** | 1+3（Change ID 必填） | 收尾确认 | 逐项问 | 无 | ✅ **一次一个问题 + 多方案 + grilling @keep** |
| verify | 0+3 | 收尾确认 | 逐项问 | 无 | n/a |

> 批次 2 候选（defer）：① dev-setup/develop/review/verify/release 全推导字段的「静默推导 + recap」呈现（需 wizard 改动）；② 非 main-chain 工作流澄清行为约束评估；③ bugfix「3+ 失败 STOP」行 @keep 化。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改**；批准后按 OPERATIONS §12 Implement 阶段执行。建议分批（先主链高交互量工作流 prepare/spec/develop/review，再其余）。

1. 逐工作流核对 `cli/services/wizard/` 实际交互（提示序列、确认点、可选呈现），填满 §4.1 评估表。
2. 按评估表实施：可选字段呈现策略（跳过/带默认问/显式列出）、确认节奏、主链 mid-task checkpoint。
3. 文档：交互评估表归档 reports/（P38 附录或独立报告），P38 状态与 PROPOSALS.md/README 登记。
4. 不动 P37 的输入契约归属（必填/可选/推导由 P37 定）；本提案只定呈现与交互。

## 6. Validation Plan（如何验证）

- 评估表评审通过后，抽查 3 个代表性工作流（prepare/develop/review）改后 wizard 交互符合预期。
- `python -m unittest discover -s cli/tests` 全绿。
- 手测：主链 prepare→spec→develop→review，确认可选字段呈现一致、checkpoint 位置合理。
- repo-lint / check.py / path-audit 全绿。

## 7. Risks（风险与缓解）

- **与 P37 边界模糊**：可选字段「归属」（P37）与「呈现」（P38）易混淆——缓解：评估表明确「P37 定归属、P38 定呈现」，实施时双表对照。
- **过度交互化**：给可选字段加提示可能反而增负担——缓解：原则是「带默认问一句、可空回退」，不强制；若实测证明某字段该跳过则跳过。
- **改动面**：15 工作流 + wizard + 测试，分批实施（先主链 4-5 个）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved（落地实施）** | 2026-08-25 |

---

## Implementation Record (2026-08-25, 批次 1)

Applied per approval (OPERATIONS §12 → Implement → Validate)：

**改动清单**
1. `cli/services/prompt_builder.py` `_skeletonize_runtime()`：新增 `<!-- @keep -->` 行为约束白名单——带标记的行在骨架化时保留（剥离标记、缩进挂靠所属 Phase）；其余裁剪逻辑不变；`AIC_FULL_RUNTIME=1` 全量路径不受影响
2. 模板标记（行为约束到达提示词层）：
   - `runtime-prepare.md`：一次一个问题 + 多方案提议（2 行 @keep）
   - `runtime-spec.md`：一次一个问题 + 多方案提议 + grilling 触发与不越权确认（3 行 @keep）
   - `runtime-review.md`：Single question + Codebase-first（2 行 @keep）
   - `runtime-develop.md`：Phase 2 计划确认 + mid-task checkpoint（~3 步一检，对齐 ATTENTION_MANAGEMENT）（2 行 @keep）
3. 文档：§4.1 评估表定稿（15 工作流实测数据 + 新增「行为约束到达提示词」列）

**Validation 结果**
- 渲染断言：prepare/spec/review/develop 四提示词全部命中预期约束行；`@keep` 标记零泄漏；其余 11 工作流无污染 — ALL OK
- `python3 -m unittest discover -s cli/tests` → Ran 164 tests, OK
- repo-lint 0 BLOCKER/ERROR；quick-check OK(0)；workflow-command-audit 0 blocker
- 手测说明：checkpoint 与澄清节奏为运行时行为，需实际跑主链验证（建议下次 prepare→spec→develop→review 实战观察）

**批次 2（部分实施，2026-08-25 同日获批）**
- ✅ 已实施 ①「静默推导 + recap」：`cli/services/wizard/steps.py` 新增 `SILENT_DERIVE_WORKFLOWS` 白名单（dev-setup/develop/review/verify/release）+ `_try_derive_silent()`——满足条件（workflow 类、无必填、有项目/工作区锚点）时跳过逐项提问，默认值+推导（Task Card/git/产物路径）预填后单次 recap 确认；选「逐项修改」或 BACK 回退常规逐项流程（覆盖权保留）
- ⏳ defer ② 非 main-chain 工作流澄清行为约束评估；③ bugfix「3+ 失败 STOP」行 @keep 化
- 验证：mock 单测全路径通过（白名单外/含必填/无锚点回退 × 确认/逐项修改/BACK）；CLI 164 tests OK；repo-lint / quick-check 绿
