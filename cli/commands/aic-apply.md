---
description: 实现 OpenSpec 变更中的任务（实验性）
---

Implement tasks in an OpenSpec change.

**Inputs**: Optionally specify the change name (e.g. `/aic-apply add-auth`). If omitted, check whether it can be inferred from conversation context. If ambiguous or unclear, you must prompt for the available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - If the user mentioned a change, infer it from conversation context
   - If only one active change exists, auto-select it
   - If ambiguous, run `openspec-cn list --json` to get available changes, and use the **AskUserQuestion tool** to let the user choose

   Always announce: "Using change: <name>" and how to override (e.g. `/aic-apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec-cn status --change "<name>" --json
   ```
   Parse JSON to understand:
   - `schemaName`: the workflow schema in use (e.g. "spec-driven")
   - Which artifact holds the tasks (usually "tasks" for spec-driven; check the status of other artifacts)

3. **Get apply instructions**

   ```bash
   openspec-cn instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (schema-specific)
   - Progress (total, done, remaining)
   - Task list with statuses
   - Dynamic instructions based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest `/aic-continue`
   - If `state: "all_done"`: congratulate, suggest archiving
   - Otherwise: continue implementation

4. **Read context files**

   Read each file path listed in `contextFiles` in the apply instructions output.
   Files depend on the schema in use:
   - **spec-driven**: proposal, specs, design, tasks
   - Other modes: follow `contextFiles` in the CLI output

5. **Show current progress**

   Show:
   - Schema in use
   - Progress: "N/M tasks complete"
   - Overview of remaining tasks
   - Dynamic instructions from the CLI

6. **Implement tasks (loop until complete or blocked)**

   For each pending task:
   - Show which task is being processed
   - Make the required code changes
   - Keep changes minimal and focused
   - Mark the task complete in the task file: `- [ ]` → `- [x]`
   - Continue to the next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design problem → suggest updating artifacts
   - Hit an error or blocker → report and wait for guidance
   - User interrupts

7. **On completion or pause, show status**

   Show:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest archiving
   - If paused: explain why and wait for guidance

**Output**

During implementation:

```
## 正在实现：<change-name>（Schema：<schema-name>）

正在处理任务 3/7：<task description>
[...正在进行实现...]
✓ 任务完成

正在处理任务 4/7：<task description>
[...正在进行实现...]
✓ 任务完成
```

On completion:

```
## 实现完成

**变更：** <change-name>
**Schema：** <schema-name>
**进度：** 7/7 任务已完成 ✓

### 本次会话已完成
- [x] 任务 1
- [x] 任务 2
...

所有任务已完成！您可以使用 `/aic-archive` 归档此变更。
```

When paused (hit a problem):

```
## 实现暂停

**变更：** <change-name>
**Schema：** <schema-name>
**进度：** 4/7 任务已完成

### 遇到的问题
<problem description>

**选项：**
1. <option 1>
2. <option 2>
3. 其他方法

您想怎么做？
```

**Guardrails**
- Keep executing tasks until complete or blocked
- Always read context files before starting (from the apply instructions output)
- If a task is ambiguous, pause and ask before implementing
- If implementation reveals a problem, pause and suggest updating artifacts
- Keep code changes minimal and scoped to each task
- Update task checkboxes immediately after completing each task
- Pause on errors, blockers, or unclear requirements - do not guess
- Use `contextFiles` from the CLI output; do not assume specific file names

**Fluid workflow integration**

This skill supports the "operate on a change" model:

- **Invokable anytime**: before all artifacts are complete (if tasks exist), after partial implementation, interleaved with other operations
- **Allows artifact updates**: if implementation reveals a design problem, suggest updating artifacts - not phase-locked, works fluidly
