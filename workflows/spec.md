---
name: spec
description: Create specification artifacts.
workflow:
  inputs:
    required: [Change ID]
    optional:
      - name: Requirement Documents
      - name: Existing Design
      - name: Mode
  next: [dev-setup]
---
# Workflow: Spec

## Purpose

Create specification artifacts for the next task.

## Runtime

- templates/runtime/runtime-spec.md

## Preconditions

- Prepare completed for this change (Preparation Report available)

## Inputs

Required:

- Change ID

Optional:

- Requirement Documents
- Existing Design
- Mode

## Context

Load only:

- Environment Context (from Bootstrap)
- Preparation Report, Architecture Summary, Impact Report (from Prepare)
- Existing Specifications and Contracts within the change scope

Never load the entire repository tree into context.

## Outputs

- Proposal
- Design
- Specification
- Contracts
- Scenarios
- Global Plan
- Task Cards
- **Location**: → `workspaces/<project-id>/openspec/{changes,specs,tasks}/`

## Exit Criteria

Success:

- Development Readiness = Ready
- Specification, Contracts, Scenarios and Tasks internally consistent

Stop:

- Required information missing → generate clarification questions and stop
- Consistency check failed → generate Consistency Report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- dev-setup — on ready
