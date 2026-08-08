---
description: 实现 OpenSpec 变更中的任务（实验性）
---

Implement tasks in an OpenSpec change.

> **Contract binding**: this command drives the **develop workflow**
> (`workflows/develop.md` + `templates/runtime/runtime-develop.md`) — it is
> the CLI entry point for that workflow. Implementation MUST follow the
> develop contract: one task card per cycle, contract-driven, traceable to
> Specification → Contract → Task Card, smallest safe change. The openspec
> commands below (`status` / `instructions apply`) are the workflow's
> artifact-resolution steps, not a parallel implementation path.

**Inputs**: Optionally specify the change name (e.g. `/aic-apply add-auth`). If omitted, check whether it can be inferred from conversation context. If ambiguous or unclear, you must prompt for the available changes.

**Steps**

> The full implementation procedure (select change → schema → apply
> instructions → context files → task loop) lives in the
> **`apply-openspec` skill** — load `skills/apply-openspec/SKILL.md` and
> execute it step by step. Contract binding: this command drives the
> **develop workflow** (`workflows/develop.md` + runtime-develop); the
> steps below are the thin trigger.

1. **Select the change** — name provided, inferred, auto-selected, or
   AskUserQuestion from `openspec-cn list --json`.

2. **Check status** — `openspec-cn status --change "<name>" --json` for
   schema and task artifact.

3. **Get apply instructions** — `openspec-cn instructions apply
   --change "<name>" --json`; handle blocked / all_done / in-progress.

4. **Read context files** from `contextFiles` (proposal, specs, design,
   tasks for spec-driven).

5. **Show progress** — schema, N/M complete, remaining tasks.

6. **Implement tasks** — loop per the skill: minimal changes per task,
   mark `- [x]`, pause on unclear/design-problem/blocker/interrupt.

7. **On completion or pause, show status** — completed this session,
   overall progress, suggest archive when all done.

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
