# Runtime: Review

Extends:

- runtime-base.md

---

## Purpose

Evaluate engineering quality before verification.

The Review Runtime assesses implementation quality against engineering standards and best practices.

The Runtime does not modify business implementation.

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

- Design Review
- Code Review
- Standards Review
- Architecture Review
- Documentation Review
- Security Review
- Performance Review
- Maintainability Review

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

Resolved by Review Runtime:

- Review Findings
- Review Suggestions

---

# Phase 1 — Review Preparation

Collect:

- Task Card（完成定义 + 代码质量检查 + 验收标准）
- Implementation Plan（tasks/plans/{task_id}-plan.md，如存在）
- Specification
- Design
- Implementation
- Test Results
- Documentation

Generate:

Review Scope

---

# Phase 2 — Design Review

Review:

- Architecture Consistency
- Layer Responsibilities
- Dependency Direction
- Domain Boundaries

## Grilling Method

For each design decision discovered in the implementation, walk the design tree:

1. **Tree-walk**: Start at the highest-level decision and drill down each branch to its leaf before moving sideways.
2. **Dependency order**: Resolve dependencies between decisions one by one. Do not skip.
3. **Single question**: Ask one question at a time. Provide a recommended answer. Wait for feedback before continuing.
4. **Codebase-first**: If a question can be answered by exploring the codebase, explore instead of asking.

The goal is reaching a shared understanding of every design trade-off, not just passing checklists.

Generate:

Design Review Report

---

# Phase 3 — Code Review

Review:

- Readability
- Naming
- Complexity
- Duplication
- Error Handling
- Logging
- Resource Management

Cross-reference against the quality checklist:

- Baseline items (General / Security / Language) → verify each item against governance/standards/common/task-quality-checklist.md to confirm actual compliance
- Conditional items (REST / MQ / RPC / Performance / Task Type) → verify each item against the Task Card inline checklist

False completion detected (marked [x] but not actually satisfied):

标注为 Critical，Task Card 回退为 Changes Required。

Generate:

Code Review Report

---

# Phase 4 — Standards Review

Review:

- Coding Standards
- Documentation Standards
- Testing Standards

Generate:

Standards Compliance Report

---

# Phase 5 — Quality Review

Review:

- Security
- Performance
- Compatibility
- Maintainability
- Extensibility

Generate:

Quality Report

---

# Phase 6 — Review Summary

Classify findings:

Critical

Major

Minor

Suggestion

Generate:

Review Report

---

# Phase 7 — Task Card Verification

Verify against Task Card:

- 完成定义 → all satisfied
- 代码质量检查 → all actually passed (not just marked)
- 验收标准 → all covered

Generate:

Task Card Review Status

If any item is marked [x] but not actually satisfied:

Revert to [ ], classify as Critical finding.

---

# Outputs

Generate:

- Updated Task Card (Review Result appended)
- review-report.md
- design-review.md
- code-review.md
- quality-review.md

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

## Review Summary

## Findings

## Severity

## Recommendations

Sync Review Status to Task Card:

```
## Review Result

**Status**: Approved / Changes Required
**Date**: {date}
**Baseline**: governance/standards/common/task-quality-checklist.md

### Findings
| Level | Item | Detail |
|-------|------|--------|

### Passed Checks
- General: {passed}/{total}
- Security: {passed}/{total}
- Java: {passed}/{total}
- REST: {passed}/{total}
- MQ: {passed}/{total}
- RPC: {passed}/{total}
- 性能: {passed}/{total}
```

If Critical findings exist:

Status = Changes Required
Task Card → Review Failed, return to develop

Otherwise:

Status = Approved for Verification
Task Card → Review Approved

---

Review Result synced to the Task Card. Ask the user to choose the next action based on findings:

| Finding Type | Action |
|---|---|
| Approved, no action items | → **verify** (continue the standard gate) |
| Minor observations that don't block approval | → **verify** + optionally create an **issue** to track follow-up |
| Implementation issues (logic errors, wrong behaviour) | → **develop** (fix in place on the task branch; re-review) |
| The root cause is a genuine defect tracked separately | → **bugfix** (the review opened an unexpected bug; file a bugfix card, then verify the task independently) |
| Behaviour diverges from expected spec in a way that looks like a requirement gap | → **spec re-entry** (L3: specification / contract may need updating before the implementation is correct) |
| Code surface-level quality problems (lint, naming, style) | → **develop** (fix and re-review) |

Fallback: Status = Changes Required defaults to return to develop.
