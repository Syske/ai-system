# Change Proposal: P38 — 逐 aic 工作流用户交互审计（wizard 交互序列/确认节奏/呈现）

| Field | Value |
|---|---|
| Status | **Proposed** |
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

### 4.1 初版交互评估表骨架（15 workflow × 4 维，待逐项核对 wizard 实际后定稿）

| Workflow | 提示序列/数量 | 确认节奏 | 可选字段呈现 | 中途检查点 |
|---|---|---|---|---|
| analysis | 待审 | 待审 | 待审 | 待审 |
| bootstrap | 待审 | 待审 | 待审 | 待审 |
| bugfix | 待审 | 待审 | 待审 | 待审 |
| change-impact | 待审 | 待审 | 待审 | 待审 |
| code-review | 待审 | 待审 | 待审 | 待审 |
| dev-setup | 待审 | 待审 | 待审 | 待审 |
| develop | 待审 | 待审 | 待审 | 待审（主链，候选 checkpoint） |
| hotfix-test-doc | 待审 | 待审 | 待审 | 待审 |
| knowledge | 待审 | 待审 | 待审 | 待审 |
| prepare | 待审（P37 已收敛必填） | 待审 | 待审 | 待审 |
| proposal | 待审 | 待审 | 待审 | 待审 |
| release | 待审 | 待审 | 待审 | 待审 |
| review | 待审 | 待审 | 待审 | 待审（主链，候选 checkpoint） |
| spec | 待审 | 待审 | 待审 | 待审 |
| verify | 待审 | 待审 | 待审 | 待审 |

> 15 行全「待审」为有意：本提案先立案 + 定维度，逐工作流核对 wizard 实际交互后填表（避免未审先断）。

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
| User (AI Maintainer operator) | **Pending** | 2026-08-25 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 交互评估表 + 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）
