---
name: review
description: Review engineering quality.
workflow:
  inputs:
    required: []
    optional:
      - name: Project ID   # auto-derived (wizard-selected project)
      - name: Task ID      # auto-derived (from Task Card)
  next: [verify, develop, bugfix, spec]
  outputs:
    base: "workspaces/<project-id>/"
  phases:
    - id: "1"
      name: "Review Preparation"
    - id: "2"
      name: "Design Review"
    - id: "3"
      name: "Code Review"
    - id: "4"
      name: "Standards Review"
    - id: "5"
      name: "Quality Review"
    - id: "6"
      name: "Review Summary"
    - id: "7"
      name: "Task Card Verification"
    - id: "8"
      name: "Validation Status Check"
---
# Workflow: Review

## Purpose

Review engineering quality before verification.

## When to Use

Use `review` when:
- A task has passed `develop` or `bugfix` self-check
- You need a formal quality gate before `verify`
- The task has a complete Task Card with acceptance criteria

Use `review-changes` (skill) instead when:
- Assessing risk/impact of uncommitted local changes
- Quick knowledge-graph-driven analysis (not a full gate review)
- Exploring codebase impact of an idea before writing a spec

## Runtime

- templates/runtime/runtime-review.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- Develop or BugFix completed for the task
- Task Card marked complete and implementation changes available

## Inputs

Required:

(None — all auto-derived from main-chain context)

Optional:

- Project ID
- Task ID

## Context

Load in this order, only what the review requires:

- Task Card → Specification → Contracts → Applied Standards
- Implementation changes and test results for the task

Never load the entire repository tree into context.

## Outputs

- Updated Task Card (Review Result appended)
- review-report.md
- design-review.md
- code-review.md
- quality-review.md
- **Location**: reports → `workspaces/<project-id>/review/<task-id>/` (per-task subdir); Task Card → `workspaces/<project-id>/openspec/changes/<change-id>/tasks/cards/`

## Exit Criteria

Success:

- Review Status = Approved for Verification

Stop:

- Critical findings exist → Review Status = Changes Required
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- verify — on approved
- develop — on changes required
- bugfix — when the review finds a bug (routing: approved→verify / bug found→bugfix / spec gap→spec re-entry)
- spec — on spec gap (re-entry; same routing line as above)
