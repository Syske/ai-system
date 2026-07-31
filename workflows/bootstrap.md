# Workflow: Bootstrap

## Purpose

Load environment configuration and prepare execution context for all downstream workflows.

## Runtime

- ai-system/templates/runtime/runtime-bootstrap.md

## Preconditions

- None. This is the entry point of the workflow chain.
- ai-system/config/environments/{environment}.yaml exists

## Inputs

Required:

- None

Optional:

- Environment (default: local)

## Context

Load only:

- ai-system/config/environments/{environment}.yaml

Never load project repositories or workspace content in this workflow.

## Outputs

- Environment Context (workspace_root, repository_root, workspaces_root, ai_system_root, methodologies_root)
- Workspace Metadata (initialized, no project binding)

## Exit Criteria

Success:

- Environment Context resolved and persisted
- Workspace directory initialized

Stop:

- Environment configuration missing → report and stop

## Next

- prepare (new change), or any workflow that requires Environment Context
