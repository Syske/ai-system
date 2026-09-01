---
description: 新增命令 - 先评估必要性（分类/重叠/真实需求），确认后才脚手架生成
---

Scaffold a new command: **first assess whether the command is necessary** (layer classification, overlap, real need) and get user confirmation; only then generate the command definition skeleton and print the registration checklist.

**Inputs**: Command Name (required, kebab-case); Description (optional, one sentence).

**Steps**

1. **Assess necessity (hard gate — do NOT scaffold before confirmation)**

   a. **Layer classification (OPERATIONS §15 Golden Rule)**: confirm the request truly belongs to the Command layer, not Skill / Workflow / Playbook / Knowledge / Template / Checklist. A thin operation that builds prompts → Command; a business process → Workflow; a reusable method → Skill. If it is not Command-layer, route to the correct layer and stop.

   b. **Overlap check (skill-policy §2 pattern)**: list existing commands and compare descriptions:

      ```bash
      python3 tools/command-scaffold.py --list
      ```

      - Overlap > 60% with an existing command → **extend the existing one**, do not create new.
      - Overlap 30–60% → document the relationship; only proceed with a distinct scope.
      - No meaningful overlap → candidate to proceed.

   c. **Evolution Principle (AI_OPERATING_RULES)**: is this driven by a real, current project need — not speculation or "a better idea"? If no real issue exists, do not create.

   d. **Confirm with the user** (AskUserQuestion tool, in the system language): proceed with a new command / extend an existing command / cancel. **Do not continue to Step 2 until the user confirms a new command is warranted.**

2. **Validate the name** (guardrail): kebab-case (`[a-z][a-z0-9-]*`), `aic-` prefix applied automatically (OPERATIONS §1.10.1). Not already registered — the scaffold tool refuses duplicates.

3. **Run the scaffold**

   ```bash
   python3 tools/command-scaffold.py "<name>" [--description "<description>"]
   ```

   Creates (non-destructive, never overwrites):
   - `cli/commands/aic-<name>.md` — command definition skeleton (frontmatter description + Steps/Output/Guardrails)

4. **Fill the content**: complete the Steps / Output / Guardrails sections. Commands build prompts via `templates/prompts/command.md`; keep the command thin and deterministic. Do not duplicate existing command logic.

5. **Register in the menu**: add a `kind: command` item in `config/menu.yaml` (with an icon) under a sections entry; add `command_fields` (+ optional `command_next`); add per-field icons.

6. **Add i18n copy**: field_notes / option_descriptions in `config/i18n/{locale}.yaml` for any new fields.

7. **Add hooks (only if needed)**: register lifecycle hooks in `cli/services/command_hooks.py` (e.g. `scan` pattern: validate / prepare). Keep hooks out of the command definition.

8. **Validate**

   ```bash
   python3 tools/check.py
   python3 tools/repo-lint.py --repo-root .
   ```

   check.py verifies `aic-` prefix, kebab-case, no `opsx-` remnants, menu referential integrity, i18n keys, prompt build, and wizard field resolution. Exit `0` before finishing.

**Output**

## Command Scaffold Report

- 必要性评估结论（层分类 / 重叠对比 / 真实需求依据）
- 用户确认结果（新建 / 扩展现有 / 取消）
- 生成文件清单（cli/commands/aic-<name>.md）
- 菜单 / i18n / hooks 注册待办
- 校验结果（check.py / repo-lint.py）

**Guardrails**

- **Necessity assessment is a hard gate**: never scaffold before the user confirms a new command is warranted. If the request maps to an existing command (>60% overlap) or a different layer, do not create.
- Scaffold is non-destructive: never overwrites existing command files.
- Commands stay thin prompt-builders (OPERATIONS §1.10); logic belongs to tools or skills, not the command definition.
- Structural changes to existing commands still require OPERATIONS §12 change management.
- Run `python3 tools/check.py` and `python3 tools/repo-lint.py --repo-root .` before finishing; both must exit 0.
