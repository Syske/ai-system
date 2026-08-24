# Change Proposal: P37 — 工作流必填参数必要性评估（省掉不必要的必填项，提升用户使用效率）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Enhancement（多 workflow 参数契约评估；触及结构，走 §12） |
| Author | AI Maintainer |
| Created | 2026-08-25 |
| Reference | 用户需求：后续评估各工作流必填参数必要性，省掉不必要的参数，让用户使用效率更高 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状 / 缺口）

各工作流 `workflow.inputs.required` 存在**重复必填**与**可推导参数被强制必填**两类低效：

| 现象 | 实例 | 影响 |
|---|---|---|
| 链路重复必填 | dev-setup / develop / review / verify 都要 `Project ID + Task ID`；prepare 要 `Change ID + Change Request` | 主链每步都向用户重复索要已确定的标识，效率低 |
| 可推导参数必填 | verify 的 `Specification Reference`（可由 Project ID + Task ID + spec 产物路径推导）；release 的 `Workspace ID`（主链已定 project/workspace） | 用户被迫提供可从上下文推导的值 |
| 必填 vs 可选失衡 | dev-setup / review / verify 的 optional 为空（全必填）；bootstrap 全空（全可选） | 无梯度，无法区分「必须」与「建议」 |

## 2. Root-Cause（根因分析）

- **契约保守**：每个 workflow 独立声明必填，未考虑主链上下游已产生的标识（prepare→spec→dev-setup→develop→review→verify→release 有明确产物链，但输入契约未复用前序输出）。
- **无推导机制**：wizard 未做「从已收集值推导本字段」（如 Specification Reference 从 spec 产物路径推导），一律要求用户显式输入。
- 属历史演进累积，非单一缺陷——需逐 workflow 评估后决定「降可选 / 自动推导 / 保持」。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 逐 workflow 评估 + 分三类处置（Recommended）** | 对每个必填参数分类：①降可选（信息可后补/低风险）；②自动推导（wizard 从已收集值/前序产物填充，用户可改）；③保持必填（真·不可推导）。产出评估表 + 实施 | 系统性、可回退（每类独立变更）、直击重复必填与可推导冗余 |
| B. 仅调个别明显项 | 只改 verify/release 等个别必填 | 快但不根治，无评估记录，易漏 |
| C. 引入全局「必填最小集」规则 | 制定统一原则（如：凡可从 Project ID+Task ID 推导的一律不设必填） | 原则先行好，但需逐 workflow 落实，实际与 A 合并执行 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A + C 原则**：
1. **立原则**：主链上「已由前序产出/可从上下文推导」的标识不设必填（降可选或 wizard 自动填充）。
2. **逐 workflow 评估**（产出下表），按分类处置：
   - 降可选候选：review/verify 的 Task ID（spec 已产出任务卡？）；release 的 Workspace ID
   - 自动推导候选：verify 的 Specification Reference（= spec 产物路径）
   - 保持必填：prepare 的 Change ID（变更标识，P28 已有默认）、bugfix 的 Bug Description、change-impact 的 Code Reference 等（真·不可推导）
3. **wizard 支持**：对「自动推导」字段，复用 `_field_defaults`/`_previous_value` 机制预填（既有模式，零架构改动）。

## 4.1 评估标准（用户定案，2026-08-25）

必填参数的三条衡量点（追加为本提案的评估标准，替代宽松的「降可选」表述）：

1. **可生成/可推断 → 不让用户填**：用户可以不填的、或可在运行期生成/推断出的参数，坚决不让用户输入（自动推导或前序产物复用）。
2. **可填可不填 → 不让用户填**：用户可填可不填的参数，一定不让用户填（默认值/自动推导覆盖，不呈现为必填也不呈现为可选输入）。
3. **优先自动生成**：优先由 aic 生成（确定性规则/前序产物），或运行期 ai 生成（workflow 运行时按上下文推断）。

> 实现注记（与 P28 评估的关系）：「aic 生成」落地为规则推导 + 前序产物复用（wizard `_field_defaults`，零 LLM 依赖）；
> 「运行期 ai 生成」落地为 workflow 运行时由 AI 按上下文推断 + 用户确认，**不引入向导层 LLM**（维持 P28 对
> 「LLM 进 wizard 是架构级改动」的结论，Evolution Principle）。

## 4.2 初版评估表（15 workflow × 必填参数 → 处置）

| Workflow | 必填参数 | 处置 | 依据（衡量点） |
|---|---|---|---|
| analysis | Analysis Target | 自动推导 | 默认分析 ai-system 自身（1） |
| bootstrap | （无） | 保持 | — |
| bugfix | Project ID | 自动推导 | wizard 已选项目（1） |
| bugfix | Bug Description | **保持必填** | 真·不可推导（3 不适用） |
| change-impact | Projects | 自动推导 | wizard 已选项目（1） |
| change-impact | Code Reference | **保持必填** | 真·不可推导 |
| code-review | Projects | 自动推导 | wizard 已选项目（1） |
| dev-setup | Workspace/Project/Task ID | 自动推导 | 前序产物 + 项目选择（1） |
| develop | Project ID | 自动推导 | 前序产物（1） |
| develop | Task ID | 自动推导 | Task Card 读取（1） |
| hotfix-test-doc | Branch Name | 自动推导 | 当前分支/项目分支（1） |
| knowledge | Knowledge Operation | 保持（默认 collect） | 意图明确但可给默认（2/3） |
| prepare | Change ID | 自动生成 | P28 默认 + slug 派生（3） |
| prepare | Change Request | **保持必填** | 核心内容不可推导 |
| proposal | Topic | **保持必填** | 核心内容不可推导 |
| release | Workspace ID | 自动推导 | 主链已定 project/workspace（1） |
| release | Release Version | 自动生成 | git tag/上一版本（3） |
| review | Project ID | 自动推导 | 前序产物（1） |
| review | Task ID | 自动推导 | Task Card（1） |
| spec | Change ID | 自动推导 | prepare 已产出（1） |
| verify | Project ID | 自动推导 | 前序产物（1） |
| verify | Task ID | 自动推导 | Task Card（1） |
| verify | Specification Reference | 自动推导 | spec 产物路径（1） |

> 预期效果：15 个 workflow 中，真·必填收敛到 4 个（bugfix Bug Description、change-impact Code Reference、
> prepare Change Request、proposal Topic）；其余全部自动推导/生成/默认。评估表为初稿，实施时逐项核对
> runtime 消费点后定稿。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改**；批准后按 OPERATIONS §12 Implement 阶段执行。

1. 产出「必填参数评估表」（15 个 workflow × 每个必填参数 → 保持/降可选/自动推导 + 理由）。
2. 按评估表实施：
   - 降可选：修改对应 `workflows/*.md` frontmatter `inputs.required/optional`
   - 自动推导：`cli/services/wizard/fields.py` 对应字段接入 `_field_defaults`（或新增推导逻辑），prompt_builder 的 `_inputs` 契约同步
3. 验证：CLI 测试（字段契约用例）、prompt 渲染（必填集变化）、repo-lint / check.py / path-audit 全绿。
4. 文档：评估表归档到 reports/（作为 P37 附录或独立报告），P37 状态与 PROPOSALS.md/README 登记。

## 6. Validation Plan（如何验证）

- 评估表评审通过后，抽查 3 个代表性 workflow（prepare / verify / release）改后 prompt 的 required 集符合预期。
- `python -m unittest discover -s cli/tests` 全绿（字段契约断言同步更新）。
- 手测：wizard 走 prepare→spec→dev-setup→develop 主链，确认降可选字段不再强制、推导字段自动填充可改。
- repo-lint / check.py / path-audit 全绿。

## 7. Risks（风险与缓解）

- **契约漂移**：降可选后，下游 runtime 若仍假定必填会缺参——缓解：评估表逐项核对 runtime 消费点（如 verify 用 Specification Reference 定位 spec 产物）。
- **推导错误**：自动推导路径若猜错（如多 spec 产物）→ 缓解：预填可编辑（`_field_defaults` 本就是「建议默认」），用户可改。
- **改动面**：15 个 workflow 前端 + wizard + 测试，分批实施（先高价值 3-5 个，再推广），避免一次性大改。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-08-25 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 评估表 + 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）
