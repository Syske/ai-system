---
description: 评估外部三方 skill 来源 - 克隆仓库、列出 skills、按参考价值分类，产出评估报告供吸收决策
---

Assess an external third-party skill source (e.g. a skill repository on GitHub), classify its skills by reference value, and produce a structured assessment report to inform absorption decisions.

**Inputs**:
- Skill Source URL: the third-party skill repository URL (required)
- Report Name (optional, default `THIRD-PARTY-SKILL-ASSESSMENT-{date}`)

**Steps**

1. **Clone the source**: shallow-clone the repository to a temp directory (`git clone --depth 1 <url>`), not into the workspace.

2. **Inventory skills**: list all skill directories (dirs containing `SKILL.md`/`skill.md`), recording each skill's name and description.

3. **Classify**: classify each skill by reference value into three tiers (following the classification framework in `reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md`):
   - **High value**: fills a real gap; methodology can be absorbed directly
   - **Medium value**: methodology borrowable, not a direct copy
   - **Low/no value**: platform-specific / personal writing / already internalized / depends on external tools / deprecated

   Compare against current ai-system assets (`skills/`, `governance/standards/`, `templates/runtime/`) to judge overlap and gaps.

4. **Generate report**: write `reports/THIRD-PARTY-SKILL-ASSESSMENT-{date}.md`, containing:
   - Source and date
   - Absorption suggestions (high-value items + landing points)
   - Borrowable suggestions (medium-value items + borrow point)
   - Non-absorbed items and reasons
   - Future trigger conditions (Evolution Principle: do not pre-emptively introduce)

5. **Clean up**: delete the temp clone directory.

**Output**

## Skill Source Assessment Report

- 来源 URL
- Skill 总数与分类统计
- 已吸收建议（高/中价值）
- 不吸收项及原因
- 后续触发条件

**Guardrails**

- Only assess and classify, **do not implement absorption**. Absorption decisions go through skill-policy after user confirmation.
- Rewrite as native assets (skill-policy), never copy third-party files.
- Follow the Evolution Principle: only recommend absorption that fills a real gap, never introduce because "it is better".
