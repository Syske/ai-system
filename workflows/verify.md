---
name: verify
description: Verify against specification and contract.
workflow:
  inputs:
    required: []
    optional:
      - name: Project ID            # 自动推导（主链前序产物/wizard 已选项目）
      - name: Task ID               # 自动推导（Task Card 读取）
      - name: Specification Reference  # 自动推导（change 产物路径）
  next: [release, develop]
  outputs:
    base: "workspaces/<project-id>/"
---
# Workflow: Verify

## Purpose

Verify implementation correctness against specification and contract.

## Runtime

- templates/runtime/runtime-verify.md

## Preconditions

- Review completed with Status = Approved for Verification

## Inputs

Required:

（无——均由主链上下文自动推导）

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
- **Location**: → `workspaces/<project-id>/` (workspace-anchored)

## Exit Criteria

Success:

- Verification Status = PASS

Stop:

- Any mandatory verification fails → Verification Status = FAIL
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- release — on PASS
- develop — on FAIL
