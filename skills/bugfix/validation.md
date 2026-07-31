# Validation

This document defines validation strategies and regression checking.
Use during Stages 12-13 of the workflow.

---

## Validation Methods

| Method | When to use |
|---|---|
| Run the exact failing test | Always — confirms the fix resolves the symptom |
| Run full test class | When the fix may affect other tests in the same class |
| Run module tests | When verifying no regressions within the module |
| Compile | When the fix is a compilation error |
| Static analysis | When the fix involves null safety or type safety |
| Runtime verification | When the fix involves observable behavior (API response, UI) |

## Scope Selection

Always prefer the smallest scope that provides confidence:

```
Failing test only          → -Dtest=FailingClass#method
  ↓
Failing test class         → -Dtest=FailingClass
  ↓
Affected module            → -pl <mod> -am test
  ↓
Module + dependents        → -pl <mod> -amd test
  ↓
Full repository            → mvn test (only when explicitly needed)
```

**Escalation rule:** Pass at current scope → done. Fail at current scope → fix
and retry at same scope. Never jump to larger scope without passing current.

## Regression Checking

### What to check

| Check | Scope | Cost |
|---|---|---|
| Tests in affected module | `-pl <mod> -am test` | Medium |
| Tests in dependent modules | `-pl <mod> -amd test` | Medium-high |
| All tests in repository | `mvn test` | High |
| Integration tests | `mvn verify` | High |

### When to check what

| Fix scope | Minimum regression check |
|---|---|
| Single file, no API change | Same module tests |
| Method signature change | Same module + dependent modules |
| Public API change | All projects using the API |
| Configuration change | Same module + dependent modules |
| pom.xml change | All modules (dependency change) |

### Handling regression failures

1. Determine if the failing test is related to the change:
   - Trace the test → does it exercise the changed code?
   - Related → the fix needs to be redesigned
   - Unrelated → pre-existing failure, document and proceed

2. If related, return to Stage 10 (redesign repair).

## Sufficiency Check

Validation is sufficient when:

- [ ] The exact symptom no longer reproduces
- [ ] The failing test passes
- [ ] All tests in the affected module pass
- [ ] No new regressions introduced
- [ ] The fix compiles without errors

## Validation Report Template

```
Validation:
  Scope:   -pl service -am test -Dtest=LiveServiceTest
  Result:  BUILD SUCCESS (15 tests, 0 failures, 0 errors)
  Fix:     Added null check in LiveService.sendMessage()
  Symptom: NullPointerException when message is null
  Root cause: sendMessage() assumed non-null message parameter
```
