# Implement Skill Decision Rules

Purpose

Provide deterministic decision rules during implementation.

When multiple implementation options exist, follow these rules in order.

If no rule applies, stop and request clarification.

---

# Priority Order

Always make decisions in the following priority:

1. Spec
2. Contract
3. Task Card
4. Applied Standards
5. Existing Project Conventions
6. Existing Implementation
7. User Instructions

Lower-priority rules must never override higher-priority rules.

---

# Scope Decisions

## Implementation Scope

When deciding whether to modify code:

Choose the smallest change that satisfies the current Task Card.

Never:

- Implement future tasks
- Refactor unrelated code
- Optimize unrelated modules

---

## File Changes

Before creating a new file:

Ask:

- Can an existing implementation be reused?
- Does the project already contain the same pattern?

Prefer modifying existing code over creating unnecessary files.

---

# Design Decisions

## Existing Pattern

If multiple implementation styles exist:

Choose the one already used in the current module.

Consistency is preferred over personal preference.

---

## Reuse

Always prefer:

Reuse

over

Rewrite.

Only introduce new implementations when reuse is impossible.

---

## Abstraction

Before introducing abstraction, ask:

- Is it required by the current Task?
- Is there at least one real consumer today?

If not,

Do not abstract.

---

# Documentation Decisions

Before completing implementation, verify:

- New classes require Javadoc.
- Public methods require documentation.
- DTO / VO / Entity / MQ fields require comments.
- Complex business logic explains why.

Documentation is mandatory, not optional.

---

# Third-party Decisions

For external systems:

Never rely on memory.

Always verify:

- API definitions
- Request parameters
- Response fields
- Error codes
- Retry behavior

Official documentation always overrides prior experience.

---

# Compatibility Decisions

If implementation may affect existing behavior:

Prefer backward compatibility.

Only introduce breaking changes when explicitly required by:

- Spec
- Contract

---

# Testing Decisions

Every implementation requires tests.

Minimum coverage:

- Happy Path
- Error Path
- Boundary Conditions

If existing tests cover the scenario,

Extend them instead of creating duplicates.

---

# Validation Decisions

Before completion:

Verify:

- Build succeeds.
- Tests pass.
- Spec satisfied.
- Contract satisfied.
- Applied Standards satisfied.

Do not complete the Task Card if any validation fails.

---

# Stop Decisions

Immediately stop when:

- Spec is missing.
- Contract is missing.
- Required dependency is missing.
- Official documentation cannot be verified.
- Scope is unclear.
- Acceptance criteria cannot be satisfied.

Report the issue.

Wait for clarification.