---
name: knowledge
description: Manage knowledge assets.
workflow:
  inputs:
    required: [Knowledge Operation]
    optional:
      - name: Knowledge Scope
      - name: Source
  next: [None]
  phases:
    - id: "1"
      name: "Knowledge Discovery"
    - id: "2"
      name: "Knowledge Extraction"
    - id: "3"
      name: "Knowledge Classification"
    - id: "4"
      name: "Knowledge Validation"
    - id: "5"
      name: "Knowledge Storage"
    - id: "6"
      name: "Knowledge Retrieval"
---
# Workflow: Knowledge

## Purpose

Manage AI System knowledge assets.

> AI-operation-first (ADR-0009): knowledge lifecycle (collect/review/archive)
> is managed by AI as part of the maintenance cycle (OPERATIONS 1.7); the
> workflow may be invoked directly on demand but is not a standalone user
> menu entry.

## Runtime

- templates/runtime/runtime-knowledge.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

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
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- None (maintenance-internal stage: reusable findings feed analysis → prepare
  through governance/memory/, not a separate chain step)
