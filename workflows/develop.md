# Workflow: Develop

## Purpose

Implement exactly one task.

## Runtime

- templates/runtime/runtime-develop.md

## Preconditions

- Dev Setup completed (Project Context and Workspace Context available)
- Task Card exists and is not completed
- Specification and Contracts exist for the task

## Inputs

Required:

- Project ID
- Task ID

Optional:

- Related Issue

## Context

Load in this order, only what the task requires:

- Task Card → Specification → Contracts → Applied Standards
- Modules and tests related to the task

Never load the entire repository tree into context.

## Outputs

- Implementation changes (code and documentation)
- Test results
- Updated Task Card (Completion Definition + Code Quality Checks + Acceptance Criteria all [x])
- Updated Workspace Context
- Completion Report
- **Location**: code → `projects/<service-id>/`; Completion Report + Test results + updated
  Workspace Context → `workspaces/<project-id>/`; Task Card → `workspaces/<project-id>/openspec/tasks/`

## Exit Criteria

Success:

- Task Card fully checked
- Completion Report generated

Stop:

- Plan not approved → wait for confirmation
- L2 change (approach) → stop, report, continue after confirmation
- L3 change (specification, contract or scope) → stop and route to spec
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip

Change levels are defined in governance/AI_OPERATING_RULES.md (Change Control).
## Next

- review
