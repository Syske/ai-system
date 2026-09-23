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

Verdict rules for these artifacts → the **Completion Criteria** block under Exit Criteria
(single definition; never restated). The artifact names below are mirrored in
`templates/runtime/runtime-prepare.md` because `checks/workflow.py` enforces
output-declaration ↔ runtime-production consistency.

Required (consumed by spec):

- Preparation Report

Generate on-demand only (skip unless the change warrants them):

- Requirement Summary
- Architecture Summary
- Impact Report
- Dependency Report — cross-service / multi-repo dependency changes
- Risk Report — high-risk changes (release re-assesses independently otherwise)
- **Location**: Preparation Report → `workspaces/<project-id>/openspec/changes/<change-id>/prepare/preparation-report.md`;
  sub-reports → `workspaces/<project-id>/openspec/changes/<change-id>/prepare/`; captured/temp sources → `workspaces/<project-id>/temp/`

## Exit Criteria

Success:

- Readiness = Ready for Specification
- Completion Criteria satisfied (block below)

Stop:

- Readiness = Blocked → report missing information and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip

### Completion Criteria (consumed by spec)

Single definition of "Prepare completed". `workflows/spec.md` Preconditions and
`templates/runtime/runtime-spec.md` Pre-flight **reference this block**; neither restates it.

1. **Preparation Report** exists and is non-empty at the canonical path
   `workspaces/<project-id>/openspec/changes/<change-id>/prepare/preparation-report.md`.
2. **Explicit skip (the only lawful exception)**: the change's OpenSpec `proposal.md` carries
   `- **Prepare**: skipped (<reason>)` with a non-empty reason (the reason is the audit trail).
3. **Legacy storage**: a report written into the change's `proposal.md` (before 2026-09-23) counts
   as present but is flagged **WARN** — migrate it to the canonical path.
4. **Grandfathering**: changes whose `proposal.md` predates the rule's effective date
   (**2026-09-23**) are **WARN**, not Stop.

Violation → spec **Stops** with the missing item + canonical path. Never substitute another
artifact — that silent substitution is what made "Prepare completed" unverifiable.

## Next

- spec — on ready
