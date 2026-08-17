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

- Change ID
- Change Request

Optional:

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

- Requirement Summary
- Repository Summary
- Architecture Summary
- Dependency Report
- Impact Report
- Risk Report
- Preparation Report

## Exit Criteria

Success:

- Readiness = Ready for Specification

Stop:

- Readiness = Blocked → report missing information and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- spec — on ready
