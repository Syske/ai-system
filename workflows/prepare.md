---
name: prepare
description: Prepare context for a new change.
workflow:
  inputs:
    required: [Change Request]
    optional:
      - name: Change ID        # auto-generated ({YYYYMM}-{slug} from Change Request, editable)
      - name: Requirement Documents
      - name: Existing Design
      - name: Related Issues
      - name: Existing Specifications
      - name: Mode
  next: [spec]
  outputs:
    base: "workspaces/<project-id>/"
---
# Workflow: Prepare

## Purpose

Prepare complete implementation context before specification.

## Runtime

- templates/runtime/runtime-prepare.md

## Preconditions

- Bootstrap completed (Environment Context available)
- Change Request available

## Inputs

Required:

- Change Request

Optional:

- Change ID
- Requirement Documents
- Existing Design
- Related Issues
- Existing Specifications
- Mode

## Context

Load only:

- Environment Context (from Bootstrap)
- Change Request materials
- Target repositories identified by the Change Request (structure and entry points only)
- Project Context and Workspace Context, if a previous Dev Setup exists

Never load the entire repository tree into context.

## Outputs

Generate (required — consumed by spec):

- Requirement Summary
- Architecture Summary
- Impact Report
- Preparation Report

Generate on-demand only (skip unless the change warrants them):

- Dependency Report — cross-service / multi-repo dependency changes
- Risk Report — high-risk changes (release re-assesses independently otherwise)
- **Location**: Preparation Report → `workspaces/<project-id>/openspec/changes/<change-id>/prepare/preparation-report.md`;
  sub-reports → `workspaces/<project-id>/openspec/changes/<change-id>/prepare/`; captured/temp sources → `workspaces/<project-id>/temp/`

## Exit Criteria

Success:

- Readiness = Ready for Specification

Stop:

- Readiness = Blocked → report missing information and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip

## Next

- spec — on ready
