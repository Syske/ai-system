---
description: 实现 OpenSpec 变更中的任务（实验性）
---

Implement tasks in an OpenSpec change.

> **Contract binding**: this command drives the **develop workflow**
> (`workflows/develop.md` + `templates/runtime/runtime-develop.md`) — it is
> the CLI entry point for that workflow. One task card per cycle,
> contract-driven, smallest safe change.

**Inputs**: Optionally specify the change name (e.g. `/aic-apply add-auth`). If omitted, check whether it can be inferred from conversation context. If ambiguous or unclear, you must prompt for the available changes.

**Steps**

> The full implementation procedure (select change → schema → apply
> instructions → context files → task loop → output formats) lives in the
> **`apply-openspec` skill** — load `skills/apply-openspec/SKILL.md` and
> execute it step by step. The steps below are the thin trigger.

1. Load `skills/apply-openspec/SKILL.md` and execute it step by step.
2. Select the change (provided / inferred / auto-selected / ask).
3. Loop implementation per task; pause on unclear / blocked.
4. On completion or pause, show progress and suggest `/aic-archive` when all done.

**Output**

Progress and pause/completion formats follow the `apply-openspec` skill
(section "Output formats"): per-task progress (`正在处理任务 N/M`),
completion summary (`实现完成` + completed tasks), and pause prompt
(`实现暂停` + problem + options) in the system language.

**Guardrails**
- Keep executing tasks until complete or blocked
- Always read context files before starting (from the apply instructions output)
- If a task is ambiguous, pause and ask before implementing
- If implementation reveals a problem, pause and suggest updating artifacts
- Keep code changes minimal and scoped to each task
- Update task checkboxes immediately after completing each task
- Pause on errors, blockers, or unclear requirements - do not guess
- Use `contextFiles` from the CLI output; do not assume specific file names
- Fluid model: invokable anytime tasks exist; may update artifacts when
  implementation reveals a design problem (not phase-locked)
