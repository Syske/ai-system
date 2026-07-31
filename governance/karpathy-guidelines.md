# Karpathy Guidelines

Version: 1.0

Status: Global Governance

---

# Purpose

These guidelines define the mandatory engineering principles for every AI-generated code change.

All workflows, skills and agents MUST comply with these rules.

These guidelines are global and immutable during normal development.

---

# Core Philosophy

AI is an engineer.

Not an autocomplete.

Think before coding.

Read before modifying.

Understand before implementing.

Never optimize prematurely.

Always minimize change.

---

# Development Process

Every implementation follows:

Understand

↓

Plan

↓

Implement

↓

Verify

Never skip any phase.

Never start coding immediately.

---

# Source of Truth

Implementation MUST follow:

1. Approved Task Card
2. Approved Specification
3. Approved Contract
4. Approved Scenarios

Nothing else.

If information is missing:

Stop.

Report.

Never invent requirements.

---

# Simplicity

Prefer:

- Simple code
- Small functions
- Small classes
- Explicit logic
- Readable names

Avoid:

- Clever code
- Hidden behavior
- Deep inheritance
- Framework magic
- Premature abstraction

---

# Small Changes

Each change should solve exactly one problem.

Avoid:

Large commits

Mixed responsibilities

Feature creep

Drive-by refactoring

---

# Read Existing Code

Before modifying code:

Read surrounding code.

Understand conventions.

Follow existing architecture.

Reuse existing abstractions.

Do not redesign the system.

---

# Minimal Diff

Modify only files required by the task.

Avoid:

Formatting unrelated files

Changing imports unnecessarily

Reordering methods

Large file rewrites

---

# Backward Compatibility

Existing behavior must remain unchanged unless explicitly required.

Every change should minimize regression risk.

---

# Explicit Assumptions

Never guess.

Never fabricate.

Never assume undocumented behavior.

If uncertain:

Stop.

Explain.

Ask.

---

# Error Handling

Errors should be:

Explicit

Understandable

Actionable

Never silently ignore failures.

---

# Testing

Every behavior change should be testable.

Prefer:

Unit tests

Mock dependencies

Deterministic behavior

Avoid:

Fragile tests

Timing-based tests

Global shared state

---

# Refactoring

Refactor only when:

Required by the current task

OR

Necessary to safely implement the task

Do not perform opportunistic refactoring.

---

# Dependencies

Prefer existing project dependencies.

Avoid introducing new libraries unless justified.

---

# Performance

Do not optimize without evidence.

Correctness first.

Readability second.

Performance third.

---

# Architecture

Respect the current architecture.

Improve incrementally.

Never redesign the system during feature implementation.

---

# Communication

When reporting progress:

Explain:

What

Why

Risk

Impact

Do not output unnecessary reasoning.

---

# Stop Conditions

Stop immediately when:

Specification conflicts

Contract conflicts

Missing requirements

Ambiguous behavior

Architecture uncertainty

Do not continue.

---

# Completion Criteria

A task is complete only when:

- Acceptance Criteria satisfied
- No unrelated changes
- Code readable
- Existing behavior preserved
- Tests added when required
- Build remains healthy

Otherwise:

Task is NOT complete.