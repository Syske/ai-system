# Change Proposal: P18 — aic-apply / aic-explore 命令瘦身（thin-command 门禁）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (command slimming) |
| Author | AI Maintainer |
| Created | 2026-08-08 |
| Reference | MAINTENANCE-2026-08-08.md F4 / S3 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`python tools/check.py` wfc-audit 持续报 2 个 thin-command 告警：

- `cli/commands/aic-apply.md`：114 行（门禁超限）
- `cli/commands/aic-explore.md`：124 行（门禁超限）

## 2. Root-Cause

命令定义文件承载了完整交互/探索引导（aic-explore 含 Stance / Things You Might Do / Guardrails 等章节），超过 thin-command 门禁（约 100 行）的预期。引导内容与技能（explore / implement）职责部分重叠。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A | 把引导性章节下沉到对应技能（aic-explore → explore 技能；aic-apply → implement/apply-openspec 技能），命令文件保留薄壳（触发条件 + 技能引用） | 符合分层（命令 = 触发入口，技能 = 引导知识） | 需确认技能文件吸收内容后的规模合规（≤1000 行/文件，当前均合规） |
| B | 提高 thin-command 门禁阈值（如 100 → 150 行） | 改动最小 | 治标，门禁失去约束力 |
| C | 维持现状（warning 而非 error） | 零改动 | 门禁持续告警 |

## 4. Recommendation

**Option A**（方向性建议，季度窗口评估）：命令瘦身为触发入口，引导内容下沉技能。本提案先记录方向与检查项；**实施前需单独评估**：aic-apply 的 114 行中哪些属 apply-openspec 技能重复、aic-explore 的引导章节是否已在 explore 技能存在（存在则直接删除重复）。若评估发现下沉后技能超限，回退 Option B（阈值调整）。

## 5. Proposed Changes（评估通过后）

1. 对照 `skills/apply-openspec/skill.md` 与 `cli/commands/aic-apply.md`，去重并下沉。
2. 对照 `skills/explore/skill.md` 与 `cli/commands/aic-explore.md`，去重并下沉。
3. 命令文件保留：Purpose / Trigger / 技能引用 / 输出约定。
4. wfc-audit 回归：2 个 warning 归零。

## 6. Validation Plan

- `python tools/check.py`：0 wfc-audit warnings
- `python tools/repo-lint.py --repo-root .`：0 BLOCKER/ERROR
- 命令冒烟：`aic-apply --help` / `aic-explore` 入口正常

## 7. Risks

- 下沉内容可能导致技能文件增大（apply-openspec 现 78 行，explore 现 64 行，余量充足）。
- 命令引导与技能职责边界需保持清晰，避免内容二次分散（由 §12 变更流程 Review 把关）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved & Implemented** | 2026-08-14 |

---

## Implementation Record (2026-08-14)

Applied per approval (OPERATIONS §12 → Implement → Validate), Option A:

1. **aic-apply.md** (114 → 43 行): 删除与 apply-openspec 技能重复的 7 步详细流程,
   压缩 Output 模板为短引用(`apply-openspec` 技能 "Output formats" 章节),
   保留 Purpose/Inputs/Contract binding/thin Steps/Output 引用/Guardrails/Fluid model。
2. **aic-explore.md** (124 → 41 行): Stance 精简为 6 条核心,Captch 章节下沉
   explore 技能,保留 Purpose/Important("思考非实现")/Stance/OpenSpec Awareness/
   Guardrails, 引用 explore 技能。
3. **skills/apply-openspec/SKILL.md** (78 → 129 行): 吸收原命令的 Output formats
   (进行中/完成/暂停 三种输出模板)。
4. **skills/explore/SKILL.md** (64 → 129 行): 吸收原命令的 `Things You Might Do` /
   `Things You Don't Have to Do` / `Ending Exploration` 章节。

**Validation**: check.py (wfc-audit 2 warnings → 0) / repo-lint 0 BLOCKER 0 ERROR
(技能 >80 行无 workflow.md 新增 2 WARNING, 与既存 25 同类 warning 一致,
为 health signal 非 P18 范围; 技能拆 workflow.md 留独立治理项) /
path-audit OK / 命令 prompt 冒烟通过(apply 2354B / explore 2769B, 含技能引用)。

**Deviations**: 技能增长触发 repo-lint "无 workflow.md >80 行" warning(x2),
与既存 agent-debug-diagnosis(114)/contract-maintainer(134) 同质接受, 不在 P18 范围。
