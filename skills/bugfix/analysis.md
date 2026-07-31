# Analysis

This document provides detailed workflows for evidence collection, hypothesis
generation, and root cause analysis. Use during Stages 2, 7-9 of the workflow.

---

## Evidence Sources

### Stack Trace Analysis

**Extract from the trace:**
1. First application-class frame (skip framework/lib frames)
2. Exception type and message
3. Caused-by chain (if present)

**Categorize by exception:**

| Exception | Likely root cause |
|---|---|
| `NullPointerException` | Uninitialized field, null return not handled, missing null check |
| `IllegalArgumentException` | Invalid input not validated |
| `IndexOutOfBoundsException` | Off-by-one, empty collection access |
| `ArithmeticException` | Division by zero |
| `ClassCastException` | Type mismatch in generic or casting |
| `ConcurrentModificationException` | Collection modified during iteration |
| `IllegalStateException` | Object in wrong state for operation |

### Test Failure Analysis

**Extract from the test output:**
1. Test class and method name
2. Expected vs actual values (for assertion failures)
3. Exception type and message (for unexpected exceptions)
4. First relevant stack frame

**Categorize by failure type:**

| Failure type | Likely root cause |
|---|---|
| Assertion: wrong value | Production logic changed, test expected value stale |
| Assertion: wrong type | Return type changed |
| Mockito: WantedButNotInvoked | Production call removed or conditional |
| Mockito: UnnecessaryStubbing | Production call removed |
| Mockito: ArgumentsAreDifferent | Production argument changed |
| Spring: context load failure | Missing `@MockBean` or `@TestPropertySource` |
| Compilation: cannot find symbol | Dependency or API changed |

### Compilation Error Analysis

**Extract from the error:**
1. File path and line number
2. Error type (symbol/package/method/constructor/type)
3. Symbol that cannot be found
4. Module name

### Log Analysis

**Extract from logs:**
1. Log level (ERROR, WARN, INFO)
2. Logger name (which class logged it)
3. Message and parameters
4. Thread context
5. 10 lines before and after for context

### Git Diff Analysis

**Always run:**
```shell
# Recent changes in the affected area
git log --oneline -10 -- <affected-file>

# Who last changed a specific line
git blame <affected-file> -L<line>,+10

# Full diff of recent commit
git show <commit-hash> --stat

# All changes in the last N commits
git diff HEAD~5 --name-only
```

---

## Root Cause Analysis Flow

### Deductive reasoning

```
Symptom
  ↓
What conditions must be true for this symptom to occur?
  ↓
Check each condition against the source code
  ↓
Eliminate impossible conditions
  ↓
Remaining condition → root cause hypothesis
  ↓
Verify by tracing cause → effect → symptom
```

### Common bug categories with reasoning patterns

**Logic errors:**
```
Symptom: wrong output for known input
  → Trace input through the code path
  → Find first point where value diverges
  → That point is the root cause
```

**Null/empty handling:**
```
Symptom: NPE at line X
  → Which variable is null? (check line X)
  → Trace back: where was it assigned?
  → Is there a null check? Should there be?
```

**Boundary conditions:**
```
Symptom: fails on edge case (empty, max value, first/last)
  → Check loops: off-by-one?
  → Check condition: inclusive vs exclusive?
  → Check collection: get() on empty list?
```

**State management:**
```
Symptom: stale or incorrect state
  → Where is the state stored?
  → When is it updated?
  → When is it read?
  → Is there a cache invalidation path?
  → Is there a race condition?
```

**Concurrency:**
```
Symptom: intermittent failure, only under load
  → Check shared mutable state
  → Check synchronization
  → Check atomicity of read-modify-write
  → Check visibility (volatile, happens-before)
```

---

## Hypothesis Validation Methods

| Method | Procedure | Cost |
|---|---|---|
| Code reading | Trace the suspected path manually | Free |
| Add debug log | `System.out.println` or logger at key points | Low |
| Write test | Isolated test reproducing the scenario | Medium |
| Run existing test | Tests that cover the suspected code path | Low |
| Git archeology | `git blame`, `git log`, `git diff` | Free |
| Assertion injection | Add temporary assert to verify assumption | Low |
| Simplify input | Reduce input to minimal repro case | Low |
