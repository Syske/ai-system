---
name: propose-openspec
description: Create an OpenSpec change with all required artifacts. Use when running aic-propose, or when the user asks to create a new OpenSpec change. Carries the full creation procedure (project guardrail → scaffold → artifact loop → status) so the aic-propose command stays a thin trigger.
---

# OpenSpec Change Creation

Procedure for creating a new OpenSpec change with all artifacts. Loaded by
the `aic-propose` command; can also be invoked directly.

## Steps

0. **Confirm project context (guardrail)**

   `openspec-cn` locates the project by cwd: change is created in
   `./openspec/changes/<name>/` (must contain `openspec/`).

   - Wrong directory → ask which project, switch
   - `openspec/` missing → prompt `openspec-cn init`

   Context loading (minimal): read the Preparation Report if it exists;
   formal requirements go through the main chain (prepare → spec);
   standalone use is only for small, low-risk changes.

1. **If no input provided, ask what they want to build**

   AskUserQuestion (open-ended), in the system language:
   > "您想要处理什么变更？请描述您想要构建或修复的内容。"

   Derive a kebab-case name (e.g. "add user authentication" →
   `add-user-auth`). Do not proceed without knowing the goal.

2. **Create the change directory**
   ```bash
   openspec-cn new change "<name>"
   ```

3. **Get artifact build order**
   ```bash
   openspec-cn status --change "<name>" --json
   ```
   Parse: `applyRequires` (artifact IDs required before implementation),
   `artifacts` (status + dependencies per artifact).

4. **Create artifacts in order until ready to apply**

   TodoWrite to track progress. Loop artifacts in dependency order
   (no pending dependencies first):

   a. For each ready artifact:
      ```bash
      openspec-cn instructions <artifact-id> --change "<name>" --json
      ```
      Instruction JSON: `context` (project background — constraint, not
      output), `rules` (artifact rules — constraint), `template`
      (output structure), `instruction` (schema-specific guidance),
      `outputPath`, `dependencies` (completed artifacts to read).
      - Read completed dependency files for context
      - Create the artifact using `template` as structure
      - Apply `context`/`rules` as constraints; do not copy into the file
      - Show progress: "✓ Created <artifact-id>"

   b. Continue until all `applyRequires` artifacts are `done`:
      re-run status after each artifact; stop when all are complete.

   c. If an artifact needs user input: AskUserQuestion, then continue.

5. **Show final status**
   ```bash
   openspec-cn status --change "<name>"
   ```

## Validation

- All `applyRequires` artifacts created with `status: done`
- Artifact files follow the schema `template`; no `context`/`rules` leaked
  into artifact content
