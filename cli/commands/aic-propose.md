---
description: 提案新变更 - 一步创建并生成所有产出物
---

Propose a new change - create the change and generate all artifacts in one step.

I will create a change containing these artifacts:
- proposal.md (what and why)
- design.md (how)
- tasks.md (implementation steps)

When ready to implement, run /aic-apply

---

**Inputs**: Arguments after `/aic-propose` are the change name (kebab-case), or a description of what the user wants to build.

**Steps**

0. **Confirm project context (guardrail)**

   openspec-cn locates the project by the current working directory: the change is created in `./openspec/changes/<name>/`.

   Check:
   - Current directory must be the target project workspace `workspaces/{project_id}/` (contains `openspec/`)
   - Wrong directory → use the **AskUserQuestion tool** to ask which project, switch to `workspaces/{project_id}/` and continue
   - `openspec/` missing → prompt to run `openspec-cn init` first; never create a change in the wrong location

   Context loading (minimal loading):
   - If a Preparation Report for this change exists (prepare phase artifact), read it before generating proposal.md
   - Formal requirements should go through the main chain (prepare → spec, driven by the provider during spec); standalone use of this command is only for small, low-risk changes

1. **If no input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask, in the system language:
   > "您想要处理什么变更？请描述您想要构建或修复的内容。"

   Derive a kebab-case name from their description (e.g. "add user authentication" → `add-user-auth`).

   **Important**: Do not proceed without knowing what the user wants to build.

2. **Create the change directory**
   ```bash
   openspec-cn new change "<name>"
   ```
   This creates a scaffolded change with `.openspec.yaml` under `openspec/changes/<name>/`.

3. **Get artifact build order**
   ```bash
   openspec-cn status --change "<name>" --json
   ```
   Parse JSON to get:
   - `applyRequires`: array of artifact IDs required before implementation (e.g. `["tasks"]`)
   - `artifacts`: list of all artifacts with status and dependencies

4. **Create artifacts in order until ready to apply**

   Use the **TodoWrite tool** to track artifact progress.

   Loop over artifacts in dependency order (artifacts with no pending dependencies first):

   a. **For each `ready` artifact (dependencies satisfied)**:
      - Get instructions:
        ```bash
        openspec-cn instructions <artifact-id> --change "<name>" --json
        ```
      - The instruction JSON includes:
        - `context`: project background (a constraint on you - do not include in output)
        - `rules`: artifact-specific rules (a constraint on you - do not include in output)
        - `template`: structure for the output file
        - `instruction`: schema-specific guidance for this artifact type
        - `outputPath`: where to write the artifact
        - `dependencies`: completed artifacts to read for context
      - Read any completed dependency files for context
      - Create the artifact file using `template` as structure
      - Apply `context` and `rules` as constraints - but do not copy them into the file
      - Show brief progress: "✓ Created <artifact-id>"

   b. **Continue until all `applyRequires` artifacts are done**
      - After creating each artifact, re-run `openspec-cn status --change "<name>" --json`
      - Check that each artifact ID in `applyRequires` has `status: "done"` in the artifacts array
      - Stop when all `applyRequires` artifacts are complete

   c. **If an artifact needs user input** (unclear context):
      - Use the **AskUserQuestion tool** to clarify
      - Then continue creating

5. **Show final status**
   ```bash
   openspec-cn status --change "<name>"
   ```

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
