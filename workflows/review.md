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

## Preconditions

- Develop or BugFix completed for the task
- Task Card marked complete and implementation changes available

## Inputs

Required:

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
- **Location**: reports → `workspaces/<project-id>/` (workspace-anchored); Task Card → `workspaces/<project-id>/openspec/tasks/`

## Exit Criteria

Success:

- Review Status = Approved for Verification

Stop:

- Critical findings exist → Review Status = Changes Required
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- verify — on approved (routing: approved→verify / bug found→bugfix / spec gap→spec re-entry)
- develop — on changes required
