---
name: verify
description: Verify against specification and contract.
workflow:
  inputs:
    required: []
    optional:
      - name: Project ID            # auto-derived (main-chain predecessors / wizard-selected)
      - name: Task ID               # auto-derived (from Task Card)
      - name: Specification Reference  # auto-derived (change artifact path)
  next: [release, develop]
  outputs:
    base: "workspaces/<project-id>/"
  phases:
    - id: "1"
      name: "Verification Preparation"
    - id: "2"
      name: "Specification Verification"
    - id: "3"
      name: "Contract Verification"
    - id: "4"
      name: "Behaviour Verification"
    - id: "5"
      name: "Test Verification"
    - id: "6"
      name: "Quality Verification"
    - id: "7"
      name: "Validation Status Check"
    - id: "8"
      name: "Final Assessment"
---
# Workflow: Verify

## Purpose

Verify implementation correctness against specification and contract.

## Runtime

- templates/runtime/runtime-verify.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- Review completed with Status = Approved for Verification

## Inputs

Required:

(None — all auto-derived from main-chain context)

Optional:

- Project ID
- Task ID
- Specification Reference

## Context

Load in this order, only what the verification requires:

- Task Card → Specification → Contracts → Scenarios
- Implementation changes and test results for the task

Never load the entire repository tree into context.

## Outputs

- verification-report.md
- specification-verification.md
- contract-verification.md
- scenario-verification.md
- test-verification.md
- **Location**: verification artifacts → `workspaces/<project-id>/verify/<task-id>/` (per-task subdir)

## Exit Criteria

Success:

- Verification Status = PASS

Stop:

- Any mandatory verification fails → Verification Status = FAIL
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- release — on PASS
- develop — on FAIL
