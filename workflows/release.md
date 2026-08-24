---
name: release
description: Prepare release readiness.
workflow:
  inputs:
    required: []
    optional:
      - name: Workspace ID    # 自动推导（主链已定 project/workspace）
      - name: Release Version # 自动生成（git tag / 上一版本推导，可编辑）
      - name: Environment
  next: [deployment, develop]
  outputs:
    base: "workspaces/<project-id>/"
---
# Workflow: Release

## Purpose

Prepare release readiness information before deployment.

This workflow does not execute deployment.

## Runtime

- templates/runtime/runtime-release.md

## Preconditions

- Verify completed with Status = PASS for all tasks in the release scope

## Inputs

Required:

（无——均由主链上下文自动推导）

Optional:

- Workspace ID
- Release Version
- Environment

## Context

Load only:

- Specification, Contracts and Scenarios for the release scope
- Git changes, completed tasks and test results in the release scope
- Configuration and database change materials
- Per-project branch diff (git diff master...HEAD --stat) for every project in the release scope

Never load the entire repository tree into context.

For multi-project releases, the Runtime must iterate over each project/service in scope, collect its task-branch-to-master diff, and classify changed files into: Application Code / Database / Configuration / Infrastructure / Documentation.

## Outputs

- release-checklist.md             # Overall release readiness per service
- release-change-report.md          # Per-project branch diff summary with change classification
- release-branch-review.md          # Aggregated branch diff quality review
- review-{task-id}.md               # Per-task branch diff review (one per Task Card)
- sql-checklist.md                  # DDL/DML/Scripts with order, rollback, risk
- sql/                              # Executable SQL files organized by execution order
  - {service}-{type}.sql
- data-migration-plan.md            # Data migration scripts with execution plan
- configuration-checklist.md        # Summary checklist for all configuration changes
- configuration-apollo.md           # Apollo per-namespace .properties blocks
- configuration-mq-topics.md         # MQ topic table with producer/consumer matrix + message body schemas
- configuration-canal.md            # Canal/binlog config changes for new/renamed fields
- dependency-checklist.md           # Service dependencies, RPC, MQ, deploy order
- risk-report.md                    # Risk registry with severity and mitigation
- **Location**: → `workspaces/<project-id>/` (workspace-anchored; sql/ + checklists + reports co-located)

## Exit Criteria

Success:

- Release Readiness = READY

Stop:

- Release Readiness = BLOCKED → report missing items; resolve them, then re-run this workflow (loop exits on READY)
- Branch Diff Review BLOCKER → fix findings, then re-run verify + release
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- deployment — on READY (outside this workflow set)
- develop — on BLOCKED (Branch Diff Review BLOCKER: fix findings then re-run verify + release)
