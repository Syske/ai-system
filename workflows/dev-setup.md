---
name: dev-setup
description: Bind a project and prepare the workspace.
workflow:
  inputs:
    required: []
    optional:
      - name: Workspace ID  # auto-derived (wizard-selected project)
      - name: Project ID    # auto-derived (wizard-selected project)
      - name: Task ID       # auto-derived (from Task Card)
  next: [develop]
  outputs:
    base: "workspaces/<project-id>/"
  phases:
    - id: "1"
      name: "Resolve Project"
    - id: "2"
      name: "Load Project Configuration"
    - id: "3"
      name: "Resolve Project Standards"
    - id: "4"
      name: "Resolve Project Knowledge"
    - id: "5"
      name: "Build Project Context"
    - id: "6"
      name: "Bind Project"
    - id: "7"
      name: "Resolve Working Environment"
    - id: "8"
      name: "Resolve Specification Reference"
    - id: "9"
      name: "Build Workspace Context"
    - id: "10"
      name: "Persist"
---
# Workflow: Dev Setup

## Purpose

Resolve project context and prepare development environment.

## Runtime

- templates/runtime/runtime-dev-setup.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- Bootstrap completed (Environment Context and Workspace Metadata available)
- Task Card exists for the given Task ID (produced by spec)

## Inputs

Required:

(None — all auto-derived from main-chain context)

Optional:

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
- Repository Mapping (`workspaces/<project-id>/workspace.yaml`, ADR-0008 — wizard / code-review / change-impact / release consume)
- **Location**: → `workspaces/<project-id>/` (workspace context/state + repository mapping); applied standards per `loaders/standards-loader.md`

## Exit Criteria

Success:

- All service branches confirmed
- Workspace Context persisted
- Repository Mapping (`workspace.yaml`) generated/refreshed per ADR-0008

Stop:

- Project cannot be resolved → report missing project information and stop
- Missing branches → prompt for confirmation and stop until confirmed
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- develop
