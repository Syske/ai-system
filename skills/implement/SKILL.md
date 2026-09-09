---
name: implement
description: >
  Contract-driven implementation skill.
  Implements exactly one OpenSpec Task Card with planning,
  coding, testing, validation, and self-review.
---

# Implement Skill

## Purpose

Implement one OpenSpec Task Card in a controlled and verifiable way.

The Skill transforms:

```
Task Card
    +
Specification
    +
Contract
    +
Existing Code
    +
Applied Standards

        ↓

Production Code
+
Tests
+
Validation Report
```

---

# Responsibility

This Skill is responsible for:

- Understanding implementation requirements
- Creating implementation plans
- Writing production code
- Creating automated tests
- Validating implementation correctness
- Producing completion reports


---

# Non Responsibility

This Skill does NOT:

- Modify Specifications
- Modify Contracts
- Split tasks
- Design architecture
- Release code
- Deploy services
- Implement future tasks
- Perform unrelated refactoring


---

# Required Context

Before implementation, the following must exist:

Required:

- OpenSpec Task Card
- Specification
- Contract
- Existing source code
- Applicable standards


If any required context is missing:

STOP.

Request clarification.

---

# Knowledge Files

Before execution, load:

## Workflow

```
workflow.md
```

Defines execution stages.

---

## Planning

```
planning.md
```

Defines task analysis and implementation planning.

---

## Decision Rules

```
decision.md
```

Defines decisions and stop conditions.

---

## Checklists

```
checklists.md
```

Defines mandatory verification items.

---

## Validation

```
validation.md
```

Defines correctness verification.

---

## Anti Patterns

```
anti-patterns.md
```

Defines forbidden behaviors.

---

## Examples

```
examples.md
```

Provides reference execution patterns.

---

# Execution Rules

## Atomic Task

Implement exactly one:

```
OpenSpec Task Card
```

Never:

- combine multiple tasks
- implement future tasks
- expand scope


---

## Planning Gate

Before coding:

1. **Reuse the confirmed plan (P54)**: when the develop runtime already
   generated, confirmed and persisted the plan
   (`.../tasks/plans/{task_id}-plan.md`), load it and verify it still matches
   the Task Card (scope / contracts / acceptance). Match → the plan is
   pre-approved — do NOT regenerate or re-run a full confirmation round-trip.
   Deviation → L2 stop-confirm path.
2. **Generate only when no confirmed plan exists** (independent implement
   invocation): generate the implementation plan via planning.md, including the
   method-granularity design summary (P50): design-critical methods
   (interface/contract surface) — signature, return granularity
   & failure-branch representation, resource/error semantics; plus the Reuse
   Decision from a mandatory existing-implementation scan (REPOSITORY_FIRST /
   karpathy Read Existing Code): each planned method marked reuse / extend /
   new; discovered similar implementations surface an explicit reuse decision
   (no silent copy or re-implementation). Self-check the plan against the P49
   checklists (return-granularity / non-necessary entities-methods) before
   presenting.

Wait for explicit user confirmation only in the generate path (Stage 3).

No code generation before a confirmed plan exists.


---

## Implementation Rules

Implementation must:

- follow Contract
- follow Specification
- follow Applied Standards
- follow existing project patterns
- minimize changes


Avoid:

- unnecessary abstraction
- speculative design
- unrelated cleanup


---

## Testing Rules

Every implementation must include tests.

Minimum:

- Happy Path
- Error Path
- Boundary Conditions


Tests must prove acceptance criteria.


---

## Validation Rules

Before completion verify:

- Build succeeds
- Tests pass
- Contract compliance
- Specification compliance
- Standards compliance
- Documentation compliance

## Post-Implementation Confirmation (P50, conditional)

For cards marked `实现后置确认: required` (interface/contract surface, refactor /
behavior change, cross-component / cross-repo contract — see Task Card field;
AI feature-detection as fallback), before the final commit:

Present the implementation method-granularity summary (new/changed methods +
signatures; return granularity & failure-branch representation; resource/error
semantics; reuse-decision execution; deviations vs the confirmed plan; gate results)
and wait for user confirmation. Mechanical cards (DTO / channel beans / config / docs)
skip. Plan-vs-implementation deviations follow the L2 stop-confirm path.


---

# Output Contract

The Skill must return:

## Implementation Summary

- Task ID
- Objective

## Changes

- Created files
- Modified files
- Deleted files


## Testing

- Tests added
- Tests executed
- Results


## Validation

- Build result
- Contract result
- Spec result
- Standards result


## Risks

- Known limitations
- Follow-up suggestions

## ⚠️  Next Step

Implement is only the first quality gate.

**Independent Review is required.**  Request the user to trigger the `review` workflow.

The Review will verify:
- Design / Architecture consistency
- Code quality (against task-quality-checklist)
- Standards compliance
- Security / Performance / Maintainability
- Detection of false completions (items marked [x] but not actually satisfied)

Only after Review passes (Status = Approved for Verification) can the task proceed to `verify`.


---

# Pipeline

After implementation:

```
implement
    ↓
review
```

The next workflow must be explicitly triggered.

Never continue automatically.

The implement Skill validates correctness (Spec / Contract / Acceptance).
The review Workflow validates engineering quality (Design / Code / Standards / Security / Performance).
Both are required before verify.
