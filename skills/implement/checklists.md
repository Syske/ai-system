# Implement Skill Checklists

Purpose

Provide mandatory checklists for implementing a single OpenSpec Task Card.

These checklists define the minimum implementation quality requirements.

All applicable checklist items must be satisfied before the task can be completed.

---

# Task Understanding Checklist

Use during Stage 1.

## Context

- [ ] Task Card loaded.
- [ ] Task ID, title and description understood.
- [ ] Acceptance criteria extracted.
- [ ] Referenced Spec sections loaded.
- [ ] Referenced Contract definitions loaded.
- [ ] Referenced Scenario definitions loaded.

## Dependencies

- [ ] Prerequisite task cards identified.
- [ ] All prerequisite tasks are completed.
- [ ] No unresolved dependency blocks implementation.

---

# Scope Checklist

Use during Stage 1–2.

## Scope

- [ ] Every code change can be traced to the current Task Card.
- [ ] In-scope items are clearly identified.
- [ ] Out-of-scope items are documented.

## Restrictions

- [ ] Spec is not modified.
- [ ] Contract is not modified.
- [ ] Future task functionality is not implemented.
- [ ] Unrelated refactoring is not introduced.

## Assumptions

- [ ] No guesses made. All behavior is documented in Spec or Contract.
- [ ] If information is missing, stop and ask. Do not fabricate.
- [ ] Undocumented behavior assumptions are explicitly confirmed with user.

## Stop Conditions

Stop immediately and report when:

- [ ] Specification conflicts with Contract.
- [ ] Requirements are missing or ambiguous.
- [ ] Architecture impact is uncertain.
- [ ] Required dependencies are unavailable.

---

# Planning Checklist

Use during Stage 2.

## Planning

- [ ] All affected modules identified.
- [ ] All affected source files identified.
- [ ] New files listed.
- [ ] Modified files listed.
- [ ] Deleted files listed (if any).

## Impact Analysis

- [ ] Public API impact identified.
- [ ] Internal implementation impact identified.
- [ ] Configuration impact identified.
- [ ] Database impact identified.
- [ ] MQ/Event impact identified.
- [ ] Dependency impact identified.

## Testing

- [ ] Unit test strategy defined.
- [ ] Validation strategy defined.

## Approval

- [ ] Implementation plan presented to the user.
- [ ] User approval obtained before coding.

---

# Implementation Checklist

Use during Stage 4.

## Read Before Modify

- [ ] Surrounding code read and understood before first edit.
- [ ] Existing conventions (naming, structure, patterns) identified.
- [ ] Existing abstractions and utilities reused where applicable.

## Scope Control

- [ ] Only the approved Task Card is implemented.
- [ ] No unrelated code changes.
- [ ] No speculative implementation.
- [ ] No future task implementation.

## Code Quality

- [ ] Simple over clever: prefer explicit logic, small functions, readable names.
- [ ] No hidden behavior or deep inheritance introduced.
- [ ] No premature abstraction.
- [ ] Existing implementation reused where appropriate.
- [ ] No duplicated logic introduced.
- [ ] No dead code introduced.
- [ ] Changes remain minimal and maintainable.

## Minimal Diff

- [ ] No reformatting of unrelated files.
- [ ] No unnecessary import changes.
- [ ] No method reordering outside the change scope.
- [ ] No large file rewrites.

## Dependencies

- [ ] Existing project dependencies preferred.
- [ ] No new library introduced without explicit justification and approval.

## Performance

- [ ] Correctness validated first, readability second, performance third.
- [ ] No optimization without evidence of a problem.

## Architecture

- [ ] Current architecture respected.
- [ ] Incremental improvement only.
- [ ] System not redesigned during feature work.

## Compatibility

- [ ] Backward compatibility preserved.
- [ ] Public interfaces changed only when required.
- [ ] Existing behavior preserved unless specified.

---

# Documentation Checklist

Use during Stage 4.

## Documentation

- [ ] Every new class includes class-level Javadoc.
- [ ] Public methods include required documentation.
- [ ] DTO fields include comments.
- [ ] VO fields include comments.
- [ ] Entity fields include comments.
- [ ] MQ message fields include comments.
- [ ] Configuration items are documented when required.
- [ ] Complex business logic explains **why**, not only **what**.

---

# Naming Checklist

Use during Stage 4.

- [ ] Package names follow project conventions.
- [ ] Class names follow project conventions.
- [ ] Method names are consistent.
- [ ] Variable names use business terminology.
- [ ] DTO / VO / Entity naming is consistent.
- [ ] MQ topic/tag names match Contract definitions.

---

# Error Handling Checklist

Use during Stage 4.

- [ ] Existing exception handling patterns are followed.
- [ ] Business exceptions handled correctly.
- [ ] External API errors handled correctly.
- [ ] No exception swallowing.
- [ ] Meaningful log messages provided.
- [ ] Sensitive information is not logged.

---

# Testing Checklist

Use during Stage 5.

## Unit Tests

- [ ] Happy Path covered.
- [ ] Error Path covered.
- [ ] Boundary Conditions covered.

## Contract

- [ ] Contract behavior verified.
- [ ] Scenario behavior verified.

## Test Quality

- [ ] Existing test patterns reused.
- [ ] External dependencies mocked where appropriate.
- [ ] Tests are deterministic.
- [ ] Tests are repeatable.

---

# Validation Checklist

Use during Stage 6.

## Build

- [ ] Project compiles successfully.
- [ ] Incremental build completed.

## Tests

- [ ] Related unit tests pass.
- [ ] Dependent module tests pass (if applicable).

## Compliance

- [ ] Spec requirements satisfied.
- [ ] Contract requirements satisfied.
- [ ] Applied Standards satisfied.
- [ ] Documentation requirements satisfied.

## Quality

- [ ] No unresolved compilation errors.
- [ ] No unresolved validation failures.

---

# Self Review Checklist

Use during Stage 7.

- [ ] Review Checklist completed.
- [ ] Coding standards satisfied.
- [ ] Documentation complete.
- [ ] Naming consistent.
- [ ] Logging appropriate.
- [ ] Exception handling appropriate.
- [ ] Maintainability acceptable.
- [ ] No temporary implementation.
- [ ] No hardcoded values (config center for URL/Token/Secret).
- [ ] No magic values (numbers/strings extracted to constants or enums).
- [ ] No TODO left in production code.
- [ ] No commented-out code.

---

# Acceptance Checklist

Use during Stage 7.

For every acceptance criterion:

- [ ] Implementation completed.
- [ ] Test evidence available.
- [ ] Contract satisfied.
- [ ] Spec satisfied.

Final Result

- [ ] All acceptance criteria satisfied.

If any criterion is not satisfied:

Return to the Implementation stage.

---

# Completion Checklist

Use during Stage 8–9.

## Task Card Status

- [ ] 完成定义：所有 `- [ ]` 已标记为 `- [x]`.
- [ ] 代码质量检查：所有 `- [ ]` 已标记为 `- [x]`.
- [ ] 验收标准：所有 `- [ ]` 已验证并标记为 `- [x]`.
- [ ] Task Card 文件已保存.

## Reports

- [ ] Implementation report generated.
- [ ] Validation report generated.
- [ ] Acceptance report generated.

## Deliverables

- [ ] Created files documented.
- [ ] Modified files documented.
- [ ] Deleted files documented.

## Status

- [ ] Task Card file updated (完成定义 + 代码质量检查 + 验收标准 all [x]).
- [ ] Global Plan updated (if required).
- [ ] Known risks documented.
- [ ] Follow-up recommendations documented.

## Completion

- [ ] Current Task Card completed.
- [ ] Next Task Card not started automatically.
- [ ] Workflow stopped.