---
description: 评估外部三方 skill 来源 - 克隆仓库、列出 skills、按参考价值分类，产出评估报告供吸收决策
---

Assess an external third-party skill source (e.g. a skill repository on GitHub), classify its skills by reference value, and produce a structured assessment report to inform absorption decisions.

**Inputs**:
- Skill Source URL: the third-party skill repository URL (required)
- Report Name (optional, default `THIRD-PARTY-SKILL-ASSESSMENT-{date}`)

**Steps**

0. **Search before creating (avoid duplication)**: before cloning or classifying, search existing local and remote skill sources for the target capability:
   - Local: `find skills -maxdepth 2 -name "SKILL.md"` and grep frontmatter descriptions in the local skills tree
   - Remote: GitHub search for the capability (`gh search repos "<keyword> skill"`), plus at most three targeted web queries
   - If a close match already exists locally, prefer it over absorbing a new source. Only proceed when no close match exists.

1. **Clone the source**: shallow-clone the repository to a temp directory (`git clone --depth 1 <url>`), not into the workspace.

2. **Inventory skills**: list all skill directories (dirs containing `SKILL.md`/`skill.md`), recording each skill's name and description.

3. **Classify**: classify each skill by reference value into three tiers (following the classification framework in `reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md`):
   - **High value**: fills a real gap; methodology can be absorbed directly
   - **Medium value**: methodology borrowable, not a direct copy
   - **Low/no value**: platform-specific / personal writing / already internalized / depends on external tools / deprecated

   Compare against current ai-system assets (`skills/`, `governance/standards/`, `templates/runtime/`) to judge overlap and gaps.

4. **Vet high-value candidates**: for each high-value candidate recommended for absorption, before finalizing the report:
   - Read the `SKILL.md` frontmatter and instructions
   - Look for unexpected shell commands, file writes, network calls, credential handling, or package installs
   - Check whether the repository appears maintained
   - Rank candidates by: exact name match > description match > maintained source > web-only mention; cap at 10

5. **Generate report**: write `reports/THIRD-PARTY-SKILL-ASSESSMENT-{date}.md`, containing:
   - Source and date
   - Absorption suggestions (high-value items + landing points), presented as decision options
   - Borrowable suggestions (medium-value items + borrow point)
   - Non-absorbed items and reasons
   - Future trigger conditions (Evolution Principle: do not pre-emptively introduce)

6. **Present decision options to the user** (in the system language):

   | Option | Meaning |
   |---|---|
   | 直接吸收 | Adopt a matching skill as-is (rewritten as native asset) |
   | 派生扩展 | Copy the closest skill and modify it |
   | 新建 | Build fresh after confirming no close match exists |

7. **Clean up**: delete the temp clone directory.

**Output**

## Skill Source Assessment Report

- 来源 URL
- Skill 总数与分类统计
- 已吸收建议（高/中价值）
- 不吸收项及原因
- 后续触发条件
- 吸收决策选项（直接吸收 / 派生扩展 / 新建）

产出写入 `outputs/skill-source/{date}-{descriptor}/`（workspace 根），
`descriptor` 为来源主题（kebab-case，如 `awesome-coding-agents`），同日重跑追加 `-N`：

```
outputs/skill-source/2026-08-13-awesome-coding-agents/
  └── skill-source-report.md   # 评估报告（含 来源/统计/吸收建议）
```

**Guardrails**

- Only assess and classify, **do not implement absorption**. Absorption decisions go through skill-policy after user confirmation.
- Rewrite as native assets (skill-policy), never copy third-party files.
- Follow the Evolution Principle: only recommend absorption that fills a real gap, never introduce because "it is better".
