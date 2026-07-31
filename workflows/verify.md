# Workflow: Verify

## Purpose

Verify implementation correctness against specification and contract.

## Runtime

- ai-system/templates/runtime/runtime-verify.md

## Preconditions

- Review completed with Status = Approved for Verification

## Inputs

Required:

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

## Exit Criteria

Success:

- Verification Status = PASS

Stop:

- Any mandatory verification fails → Verification Status = FAIL

## Next

- On PASS: release
- On FAIL: develop
