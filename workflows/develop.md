---
name: develop
description: Implement one task.
workflow:
  inputs:
    required: []
    optional:
      - name: Project ID     # auto-derived (wizard-selected project)
      - name: Task ID        # auto-derived (read from Task Card)
      - name: Related Issue
  next: [review]
  outputs:
    base: "workspaces/<project-id>/"
  phases:
    - id: "1"
      name: "Resolve Development Context"
    - id: "2"
      name: "Planning"
    - id: "3"
      name: "Invoke Implement Skill"
    - id: "4"
      name: "Completion"
      # SSOT for "what satisfies this Phase" (P76 schema: criterion lives in
      # workflow frontmatter, never in the runtime).
      #
      # States an observable fact, not an engineering result (P79 §8.1):
      # "generated successfully" is excluded because `successfully` is a
      # semantic judgement no deterministic evaluator can make.
      #
      # Scoped to <task>, NOT "directory non-empty": measured across real
      # workspaces, one change accumulates reports across many Task Cards
      # (up to 16 files), so a non-empty directory was already true before this
      # Phase ran. That is a deterministic false positive. Mapping is
      # <task-id> verbatim — real Task IDs come in two shapes (`T-001` 116×,
      # `2.1` 18×), so no `T-` prefix may be assumed (P79 §5, §12).
      #
      # Strict match on purpose: loose matching (`*<task>*report*.md`) would
      # violate the Deterministic criterion. A non-conforming filename yields
      # a false negative — disclosed in P79 §9.2, not worked around here.
      pass_criterion: "Completion Report for <task> exists (workspaces/<project>/openspec/changes/<change>/completion-reports/<task>-completion-report.md)"
---
# Workflow: Develop

## Purpose

Implement exactly one task.

## Runtime

- templates/runtime/runtime-develop.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- Dev Setup completed (Project Context and Workspace Context available)
- Task Card exists and is not completed
- Specification and Contracts exist for the task

Precondition handling — do NOT improvise around a missing precondition:

- Missing Dev Setup (workspace has no `contexts/`, or `.aic-state.yaml` shows no
  dev-setup run): run the `dev-setup` workflow first (previous main-chain stage),
  then continue `develop`. Never fabricate Project/Workspace Context and never
  skip the stage, even when the request said "develop".

## Inputs

Required:

(none — all derived from main-chain context)

Optional:

- Project ID
- Task ID
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
- **Location**: code → `projects/<service-id>/`; Completion Report + Test results →
  `workspaces/<project-id>/openspec/changes/<change-id>/completion-reports/`;
  updated Workspace Context → `workspaces/<project-id>/contexts/`;
  Task Card → `workspaces/<project-id>/openspec/changes/<change-id>/tasks/cards/<task-id>.md`

## Exit Criteria

Success:

- Task Card fully checked
- Completion Report generated

Stop:

- Plan not approved → wait for confirmation
- L2 change (approach) → stop, report, continue after confirmation
- L3 change (specification, contract or scope) → stop and route to prepare (scoped) → spec
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip

Change levels are defined in governance/AI_OPERATING_RULES.md (Change Control).
## Next

- review
