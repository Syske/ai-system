# Runtime: Verify

Extends:

- runtime-base.md

---

## Purpose

Verify implementation correctness against Specification and Contracts.

The Verify Runtime provides evidence that the implementation satisfies expected behaviour.

The Verify Runtime does not perform implementation changes.

---

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

# Responsibilities

The Runtime is responsible for:

- Specification Verification
- Contract Verification
- Behaviour Verification
- Test Verification
- Regression Verification
- Acceptance Verification
- Verification Reporting

---

# Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Provided by Dev Setup Runtime:

- Project Context

Provided by Dev Setup Runtime:

- Workspace Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Applied Standards

Provided by Specification Runtime:

- Specification
- Contracts
- Scenarios
- Task Cards

Resolved by Verify Runtime:

- Verification Criteria
- Verification Evidence
- Verification Result

---

# Phase 1 — Verification Preparation

Collect:

- Specification
- Design
- Contracts
- Scenarios
- Task Card
- Implementation Plan (if present)
- Implementation Changes
- Test Results

Generate:

Verification Plan

---

# Phase 2 — Specification Verification

Verify:

Requirement

↓

Specification

↓

Implementation

Check:

- Required behaviour exists
- Acceptance criteria satisfied
- Scope matches Task Card
- Implementation matches the approved plan (if present); deviations recorded

Generate:

Specification Verification Report

---

# Phase 3 — Contract Verification

Verify:

API:

- Request
- Response
- Error Handling

Data:

- Field Definition
- Compatibility
- Version

Interaction:

- Dependencies
- Rules

Generate:

Contract Verification Report

---

# Phase 4 — Behaviour Verification

Verify business scenarios.

For every scenario:

Check:

- Trigger
- Input
- Output
- Success Path
- Failure Path
- Boundary Conditions

Generate:

Scenario Verification Report

---

# Phase 5 — Test Verification

Verify:

Test Coverage:

- Happy Path
- Error Path
- Boundary Conditions

Verify:

- Unit Tests
- Integration Tests
- Regression Tests

Generate:

Test Verification Report

---

# Phase 6 — Quality Verification

Verify:

- Build Success
- Runtime Stability
- Compatibility
- Performance Requirements

Generate:

Quality Verification Report

---

# Phase 7 — Final Assessment

Calculate:

Verification Status:

PASS

or

FAIL

Rules:

If any mandatory verification fails:

Status = FAIL

---

# Outputs

Generate:

- verification-report.md
- specification-verification.md
- contract-verification.md
- scenario-verification.md
- test-verification.md

# Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:
1. Simpler implementation possible?
2. Code duplication introduced?
3. Standards violated?
4. Over-engineering present?
5. Anything incomplete?

Record the Reflection Report in the Completion output.
Do NOT modify code during Reflection.

---

# Completion

Return:

## Verification Summary

## Verification Status

## Evidence

## Failed Items

## Recommended Action

If PASS:

Next Runtime:

Release Runtime

If FAIL:

Return to Development Runtime