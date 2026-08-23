# AI Command

# Operating Rules

Load and obey {{ai_system_root}}/governance/AI_OPERATING_RULES.md before execution.

Change control levels (L1 / L2 / L3) and workspace discipline apply to this run.

On completion of this run, WRITE a per-run diagnostic record to `{{ai_system_root}}/logs/`
per `{{ai_system_root}}/templates/runtime/runtime-diagnostic-log.md` (fields mirror the
Completion Report + Reflection checklist; failures carry root cause + reproduction;
normal runs keep a one-page summary, splitting out detail on demand). Filename:
`<command>-<YYYYMMDD-HHMMSS>.md`. Do not declare completion without writing it.

# Path Anchor

文内所有相对引用（`ai-system/...`、`extensions/...`、`workspaces/...`、`outputs/...`）
以这两个绝对根为基准解析：

- AI System root: `{{ai_system_root}}`
- Workspace root: `{{workspace_root}}`

---

{{command_definition}}

---

# Task

## Command

{{command_name}}

## Inputs

{{inputs}}

---

Begin execution.
