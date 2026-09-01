---
description: 新增工作流 - 先评估必要性（分类/重叠/真实需求），确认后才脚手架生成
---

Scaffold a new workflow: **first assess whether the workflow is necessary** (layer classification, overlap, real need) and get user confirmation; only then generate the 8-section entry contract, minimal config yaml, runtime skeleton, and append the registry entry — then guide registration and validation.

**Inputs**: Workflow Name (required, kebab-case); Purpose (optional, one sentence); Next Workflow (optional, downstream workflow name or None).

**Steps**

1. **Assess necessity (hard gate — do NOT scaffold before confirmation)**

   a. **Layer classification (OPERATIONS §15 Golden Rule)**: confirm the request truly belongs to the Workflow layer, not Skill / Command / Playbook / Knowledge / Template / Checklist. A recurring business process → Workflow; a tool operation → Command; reusable engineering method → Skill. If it is not Workflow-layer, route to the correct layer and stop.

   b. **Overlap check (skill-policy §2 pattern)**: list existing workflows and compare purposes:

      ```bash
      python3 tools/workflow-scaffold.py --list
      ```

      - Overlap > 60% with an existing workflow → **extend the existing one**, do not create new.
      - Overlap 30–60% → document the relationship; only proceed with a distinct scope.
      - No meaningful overlap → candidate to proceed.

   c. **Evolution Principle (AI_OPERATING_RULES)**: is this driven by a real, current project need — not speculation or "a better idea"? If no real issue exists, do not create.

   d. **Confirm with the user** (AskUserQuestion tool, in the system language): proceed with a new workflow / extend an existing workflow / cancel. **Do not continue to Step 2 until the user confirms a new workflow is warranted.**

2. **Validate the name** (guardrail): kebab-case (`[a-z][a-z0-9-]*`), one word preferred (OPERATIONS §1.10.1). Not already registered — the scaffold tool refuses duplicate names.

3. **Run the scaffold**

   ```bash
   python3 tools/workflow-scaffold.py "<name>" [--purpose "<purpose>"] [--next <workflow>]
   ```

   Creates (non-destructive, never overwrites):
   - `workflows/<name>.md` — 8-section contract with TBD placeholders
   - `config/workflows/<name>.yaml` — minimal (version/name/workflow/runtime)
   - `templates/runtime/runtime-<name>.md` — runtime skeleton (extends runtime-base.md)
   - Appends the registry entry to `config/workflow-registry.yaml`

4. **Fill the content**: complete the TBD sections in the workflow md (Preconditions / Inputs / Context / Outputs / Exit Criteria) and the runtime phases. Follow the 8-section template and terminology in `workflows/README.md`. Never put implementation logic in the workflow (RFC-0003).

5. **Register in the menu**: add a `kind: workflow` item for the workflow in `config/menu.yaml` under a sections entry (with an icon; optional `number` for the main chain). Add i18n copy (`config/i18n/{locale}.yaml`) for any new field notes / option descriptions.

6. **Update the index**: add the workflow to the selection table in `workflows/README.md`; extend terminology only if new fields are introduced.

7. **Validate**

   ```bash
   python3 tools/check.py
   python3 tools/repo-lint.py --repo-root .
   ```

   check.py verifies the registry chain (config → workflow → runtime), 8-section presence, Next convention, and menu referential integrity. Exit `0` before finishing.

**Output**

## Workflow Scaffold Report

- 必要性评估结论（层分类 / 重叠对比 / 真实需求依据）
- 用户确认结果（新建 / 扩展现有 / 取消）
- 生成文件清单（workflows/<name>.md、config/workflows/<name>.yaml、templates/runtime/runtime-<name>.md）
- 注册表登记结果
- 菜单 / README 注册待办
- 校验结果（check.py / repo-lint.py）

**Guardrails**

- **Necessity assessment is a hard gate**: never scaffold before the user confirms a new workflow is warranted. If the request maps to an existing workflow (>60% overlap) or a different layer, do not create.
- Scaffold is non-destructive: never overwrites existing files or registry entries.
- Workflow files must stay orchestration-only (RFC-0003); runtime owns lifecycle detail.
- Structural changes to existing workflows still require OPERATIONS §12 change management.
- Run `python3 tools/check.py` and `python3 tools/repo-lint.py --repo-root .` before finishing; both must exit 0.
