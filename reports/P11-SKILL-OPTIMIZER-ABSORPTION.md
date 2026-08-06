# Change Proposal: P11 — Skill Optimizer 网络思想吸收（SkillOpt / DSPy / TextGrad / Claude skill-creator）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Skill enhancement (skill-optimizer new actions) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | MAINTENANCE-2026-08-06.md; user decision "有吸收价值且收益明显的就吸收，可有可无的暂不考虑，只做记录" |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem / Opportunity

对照网络主流的 skill/prompt 优化思想（Microsoft SkillOpt、DSPy optimizers、
TextGrad、Claude skill-creator），skill-optimizer 的核心缺口不在"模式种类"
（已有 static/dynamic/trace/feedback），而在优化闭环的
**度量-门控-演化**三段：会改、但不会验证改得好不好；只动 instructions、
不碰 demos；description（路由触发面）不在优化视野内。

## 2. 吸收矩阵（用户裁决：收益明显→吸收；可有可无→仅记录）

### ✅ 已吸收（3 项，收益明显、工作量可控）

| # | 思想 | 来源 | 实现 |
|---|------|------|------|
| A1 | held-out 验证门控：候选 vs 基线在 held-out 任务集上对比通过率，输出 accept/reject 建议 | SkillOpt | 新 action `validate`（--benchmark，读 skill-benchmark-generator 产物） |
| A2 | demo-augment：成功执行轨迹沉淀为 SKILL.md 的 `## Examples` 区 | DSPy BootstrapFewShot | 新 action `augment`（--demos） |
| A3 | description 路由触发调优：评估 frontmatter description 并给改写建议 | Claude skill-creator | 新 action `tune-description`（可选 --routing-report） |

三者统一纪律：**候选优先 + 快照版本化 + 人工决策**（只写新快照，不自动采纳；
采纳走既有 `accept`）。这与 OPERATIONS §12 / Change Control 的
"AI 建议、人决策"一致。

### 📋 仅记录（9 项，暂不实施）

| # | 思想 | 来源 | 未来触发条件 |
|---|------|------|-------------|
| R1 | optimizer/target 模型角色分离 | SkillOpt | 出现自评自改盲区导致的实际失败 |
| R2 | bounded edits（编辑量预算） | SkillOpt | 单轮改动失控/过度改写成为现实问题 |
| R3 | meta skill（优化策略本身可学习） | SkillOpt | 优化决策模式重复出现且可提炼 |
| R4 | SIMBA 最差样本优先 | DSPy | 诊断分布高度不均时 |
| R5 | InferRules 规则清单供人采纳 | DSPy | 需要可审阅的显式规则产物 |
| R6 | optimization_gradient 持久化（meta.json） | TextGrad | accept/revert 缺乏"为什么改"上下文时 |
| R7 | 组件级诊断（SKILL.md/scripts/refs 分层） | TextGrad | 总是只改 SKILL.md 而忽略 scripts 成为问题 |
| R8 | regression-check（模型升级后重测） | Claude | 模型升级导致旧 skill 退化 |
| R9 | 成本指标（pass rate/time/tokens）入报告 | Claude | 优化成本成为决策瓶颈 |

> 记录原则：不因"更好的想法"而预实施（Evolution Principle），
> 每项在出现真实触发条件后再评估。

## 3. 实施内容

1. `scripts/actions.py` — **新增**（~400 行）：三个 action 处理器
   （run_augment / run_validate / run_tune_description + 共享候选快照助手）。
2. `scripts/main.py` — CLI 扩展：`--action` choices 增加
   `augment/validate/tune-description`；新增 `--demos/--benchmark/--routing-report` 参数。
3. `SKILL.md` — 模式表新增"附加 Action"章节 + 命令示例。
4. `workflow.md` — 步骤 3 新增 3.5 附加 Action 小节。

## 4. Validation

- `python -m py_compile actions.py main.py` → OK
- 三个 action 冒烟测试（stub LLM）：augment 写入快照 Examples 且不动 live skill ✅；
  validate 计数 2/3 正确、建议 ACCEPT/REJECT 逻辑正确 ✅；
  tune-description 有/无 description 字段均正确改写 ✅
- `tools/repo-lint.py` → 0 BLOCKER / 0 ERROR
- `tools/check.py` → PASS
- 环境注记：全局 Python 3.10 因 langchain 旧 API（create_agent）无法 import 全链，
  为既有环境问题（原始 main.py 同样失败），非本次引入；opt.sh 的 .opt 虚拟环境不受影响。

## 5. Risks

- **低**：新 action 均为可选路径，默认行为（optimize/accept/revert）零改动。
- **低**：augment/validate 的 LLM 输出质量依赖提示词；validate 的 PASS/FAIL 计数
  已做 "PASS RATE" 排除防重复计数。
- 未触及 workflow/config/registry。

## 6. 后续跟踪

- validate 与 skill-benchmark-generator 的产物格式对接（当前约定
  `[{task, expected_outcome}]` JSON，未来若产物格式演进需同步）。
- R1–R9 在 MAINTENANCE-2026-08-06.md §2.4 有原始评估，按触发条件逐项复审。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — 吸收 3 项，记录 9 项** | 2026-08-06 |

---

## Implementation Record (2026-08-06)

1. `scripts/actions.py` — 新增三个 action（~400 行）。
2. `scripts/main.py` — CLI 扩展（action choices + 3 个新参数 + 分发分支）。
3. `SKILL.md` — 附加 Action 章节。
4. `workflow.md` — 步骤 3.5。
5. 验证全绿（见 §4）。

**Deviations**: 无。
**Risks**: validate 依赖 benchmark 产物约定；LLM 输出质量依赖提示词。
