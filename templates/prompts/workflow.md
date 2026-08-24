# AI Coding Workflow

# Operating Rules

Load and obey {{ai_system_root}}/governance/AI_OPERATING_RULES.md before execution.

Change control levels (L1 / L2 / L3) and workspace discipline apply to this run.

On completion of this run, WRITE a per-run diagnostic record to `{{ai_system_root}}/logs/`
per `{{ai_system_root}}/templates/runtime/runtime-diagnostic-log.md` (fields mirror the
Completion Report + Reflection checklist; failures carry root cause + reproduction;
normal runs keep a one-page summary, splitting out detail on demand). Filename:
`<workflow>-<YYYYMMDD-HHMMSS>.md`. Do not declare completion without writing it.

# Path Anchor

All relative references in the body below (`ai-system/...`, `extensions/...`,
`workspaces/...`, `outputs/...`) resolve against these two absolute roots:

- AI System root: `{{ai_system_root}}`
- Workspace root: `{{workspace_root}}`

---

{{workflow_definition}}

---

{{runtime_definition}}

---

# Task

## Workflow

{{workflow_name}}

## Inputs

{{inputs}}

---

Begin execution.
