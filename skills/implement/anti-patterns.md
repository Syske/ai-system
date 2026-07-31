# Implement Skill Anti-Patterns

Purpose

Define behaviors that are strictly prohibited during implementation.

If any anti-pattern is detected, stop and correct it before continuing.

---

# Scope Violations

## Multiple Task Implementation

❌ Never implement multiple Task Cards in a single execution.

Instead

- Implement exactly one approved Task Card.
- Stop after completion.

---

## Scope Creep

❌ Never add functionality outside the approved Task Card.

Examples

- Refactoring unrelated code
- Adding future features
- Optimizing unrelated modules

Instead

Only implement what the current Task Card requires.

---

## Spec or Contract Modification

❌ Never modify Spec or Contract during implementation.

Instead

Report inconsistencies and stop.

---

# Assumption Violations

## Guessing Instead of Verifying

❌ Never assume:

- APIs exist
- Method signatures
- Configuration keys
- Database schemas
- Error codes
- Third-party behavior

Instead

Verify before implementation.

---

## Ignoring Official Documentation

❌ Never implement third-party integrations based on memory.

Examples

- WeCom
- DingTalk
- OpenAI
- AWS

Instead

Verify against official documentation.

---

# Code Quality Violations

## Duplicate Implementation

❌ Never reimplement existing functionality.

Instead

Reuse existing implementation whenever possible.

---

## Unnecessary Abstraction

❌ Never introduce abstraction without current requirements.

Examples

- Generic framework
- Future extension points
- Unused interfaces
- Unused strategy classes

Instead

Prefer the simplest correct implementation.

---

## Dead Code

❌ Never leave:

- unused methods
- unused classes
- unused variables
- commented-out code

Instead

Delete unnecessary code.

---

## Temporary Implementations

❌ Never submit:

- TODO implementation
- FIXME implementation
- placeholder logic
- fake return values

Instead

Implement completely or report the blocker.

---

# Documentation Violations

## Missing Documentation

❌ Never create new code without required documentation.

Required

- Class Javadoc
- Public method documentation
- DTO field comments
- VO field comments
- Entity field comments
- MQ message field comments

---

## Explaining What Instead of Why

❌ Avoid comments that merely repeat the code.

Bad

```java
// Set userId
user.setUserId(id);
```

Good

```java
/**
 * UserId comes from the authenticated enterprise context.
 */
```

---

# Naming Violations

## Inconsistent Naming

❌ Never invent new business terminology.

Instead

Reuse existing domain terminology defined by:

- Spec
- Contract
- Existing codebase

---

# Compatibility Violations

## Breaking Backward Compatibility

❌ Never change public behavior unless explicitly required.

Examples

- Method signatures
- DTO fields
- MQ message format
- Public APIs

---

# Logging Violations

## Missing Error Logs

❌ Never silently swallow exceptions.

Instead

Log meaningful business context.

---

## Logging Sensitive Information

❌ Never log:

- passwords
- secrets
- tokens
- personal information

---

# Testing Violations

## Missing Tests

❌ Never complete implementation without required tests.

Required

- Happy Path
- Error Path
- Boundary Conditions

---

## Ignoring Existing Test Failures

❌ Never fix unrelated failing tests during implementation.

Instead

Document them as pre-existing issues.

---

# Completion Violations

❌ Never mark a Task Card as completed when:

- Build fails
- Tests fail
- Acceptance criteria are incomplete
- Documentation is incomplete
- Review Checklist fails
- Applied Standards are not satisfied

Stop and resolve the issue first.