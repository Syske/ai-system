---
name: dev-setup
description: Bind a project and prepare the workspace.
workflow:
  inputs:
    required: [Workspace ID, Project ID, Task ID]
  next: [develop]
---
# Workflow: Dev Setup

## Purpose

Resolve project context and prepare development environment.

## Runtime

- templates/runtime/runtime-dev-setup.md

## Preconditions

- Bootstrap completed (Environment Context and Workspace Metadata available)
- Task Card exists for the given Task ID (produced by spec)

## Inputs

Required:

- Workspace ID
- Project ID
- Task ID

## Context

Load only:

- Environment Context and Workspace Metadata (from Bootstrap)
- workspaces/{project_id}/ project configuration
- {workspace_root}/repositories/{service_id}.yaml for each project service
- Specification Reference (identity only, not content)

Never load repository source code in this workflow.

## Outputs

- Project Context
- Applied Standards
- Project Knowledge Context
- Workspace Context
- Workspace State
- **Location**: → `workspaces/<project-id>/` (workspace context/state); applied standards per `loaders/standards-loader.md`

## Exit Criteria

Success:

- All service branches confirmed
- Workspace Context persisted

Stop:

- Project cannot be resolved → report missing project information and stop
- Missing branches → prompt for confirmation and stop until confirmed
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- develop
