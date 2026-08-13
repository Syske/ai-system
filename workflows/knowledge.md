# Workflow: Knowledge

## Purpose

Manage AI System knowledge assets.

> AI-operation-first (ADR-0009): knowledge lifecycle (collect/review/archive)
> is managed by AI as part of the maintenance cycle (OPERATIONS 1.7); the
> workflow may be invoked directly on demand but is not a standalone user
> menu entry.

## Runtime

- templates/runtime/runtime-knowledge.md

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Knowledge Operation

Supported: collect, update, search, review, archive

Optional:

- Knowledge Scope
- Source

## Context

Load only:

- Knowledge sources required by the requested operation
- Existing knowledge index for the declared scope

Never load unrelated knowledge categories.

## Outputs

- Knowledge Assets
- Knowledge Index
- Knowledge Metadata
- Knowledge Report

## Exit Criteria

Success:

- Requested operation completed and assets persisted

Stop:

- Duplicate or contradictory knowledge detected → reject and report

## Next

- None
