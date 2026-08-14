---
name: apply-openspec
description: Implement tasks in an OpenSpec change following the develop contract. Use when running aic-apply, or when the user asks to implement an OpenSpec change. Carries the full implementation procedure (select → schema → instructions → context → loop) so the aic-apply command stays a thin trigger.
---

# OpenSpec Change Implementation

Procedure for implementing tasks in an OpenSpec change. Loaded by the
`aic-apply` command. **Contract binding**: this drives the **develop
workflow** (`workflows/develop.md` + `templates/runtime/runtime-develop.md`)
— one task card per cycle, contract-driven, traceable to
Specification → Contract → Task Card, smallest safe change. The openspec
commands below are the workflow's artifact-resolution steps, not a
parallel implementation path.

## Steps

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous: `openspec-cn list --json` + AskUserQuestion

   Announce: "Using change: <name>" and how to override.

2. **Check status to understand the schema**
   ```bash
   openspec-cn status --change "<name>" --json
   ```
   Parse: `schemaName`, which artifact holds the tasks (usually "tasks"
   for spec-driven).

3. **Get apply instructions**
   ```bash
   openspec-cn instructions apply --change "<name>" --json
   ```
   Returns `contextFiles` (artifact ID → file paths), progress
   (total/done/remaining), task list, dynamic instructions.

   Handle states:
   - `blocked` (missing artifacts): show message, suggest `/aic-apply`
   - `all_done`: congratulate, suggest archiving
   - Otherwise: continue

4. **Read context files**

   Read each path in `contextFiles` (spec-driven: proposal, specs,
   design, tasks; other modes follow the CLI output).

5. **Show current progress**

   Schema / progress "N/M tasks complete" / remaining tasks / dynamic
   instructions.

6. **Implement tasks (loop until complete or blocked)**

   For each pending task:
   - Show which task is being processed
   - Make the required code changes (minimal and focused, per develop
     contract)
   - Mark complete: `- [ ]` → `- [x]`
   - Continue to the next

   Pause if: task unclear → ask; design problem revealed → suggest
   updating artifacts; error/blocker → report and wait; user interrupts.

7. **On completion or pause, show status**

   Tasks completed this session / overall progress / if all done, suggest
   archiving / if paused, explain why.

## Validation

- All completed tasks marked `- [x]` in the task file
- Changes trace to the task card (Specification → Contract → Task)
- Changes minimal — no unrelated edits
- State reported accurately (blocked / all_done / in-progress)

## Output formats

Present progress and results in the system language (Chinese):

**During implementation**

```
## 正在实现：<change-name>（Schema：<schema-name>）

正在处理任务 3/7：<task description>
[...正在进行实现...]
✓ 任务完成
```

**On completion**

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

**When paused (hit a problem)**

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
