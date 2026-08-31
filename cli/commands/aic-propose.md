---
description: 提案新变更 - 一步创建并生成所有产出物
---

Propose a new change - create the change and generate all artifacts in one step.

I will create a change containing these artifacts:
- proposal.md (what and why)
- design.md (how)
- tasks/cards/ (task cards: implementation steps)

When ready to implement, run /aic-apply

---

**Inputs**: Arguments after `/aic-propose` are the change name (kebab-case), or a description of what the user wants to build.

**Steps**

> The full creation procedure (project guardrail → scaffold → artifact
> loop → status) lives in the **`propose-openspec` skill** — load
> `skills/propose-openspec/SKILL.md` and execute it step by step. The
> command below is the thin trigger: derive the change name, then follow
> the skill's 6 steps (context guardrail → ask goal → `openspec-cn new
> change` → artifact loop → final status).

0. **Confirm project context (guardrail)**

   Load the `propose-openspec` skill. Key guardrail: cwd must be the
   target project workspace `workspaces/{project_id}/` (contains
   `openspec/`); wrong directory → ask which project; missing `openspec/`
   → prompt `openspec-cn init`. Formal requirements go through the main
   chain (prepare → spec); standalone use is for small, low-risk changes.

**Output**

After all artifacts are created, summarize:
- Change name and location
- List of created artifacts with brief descriptions
- Readiness: "All artifacts created! Ready to implement."
- Prompt: "Run `/aic-apply` to start implementation."

**Artifact Creation Guidelines**

- Follow the `instruction` field in `openspec-cn instructions` for each artifact type
- The schema defines what each artifact should contain; follow it
- Read dependency artifacts before creating new ones, for context
- Use `template` as the structure for the output file - fill its sections
- **Important**: `context` and `rules` are constraints on you, not file content
  - Do not copy `<context>`, `<rules>`, `<project_context>` blocks into artifacts
  - They guide how you write, but should not appear in the output

**Guardrails**
- Create all artifacts required for implementation (per the schema's `apply.requires`)
- Always read dependency artifacts before creating new ones
- If context is extremely unclear, ask the user - but prefer reasonable decisions to keep momentum
- If a change with the same name exists, ask whether to continue it or create a new one
- Verify each artifact file exists after writing, before moving on
