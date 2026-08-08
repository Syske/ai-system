# Repair

This document defines repair strategies and patterns. Use during Stages 10-11
of the workflow.

---

## Repair Priorities

| Priority | Rule | Example |
|---|---|---|
| 1 — Correctness | Fix the root cause | Add null check where null is possible |
| 2 — Minimal impact | Change only the affected scope | One line change, not a refactor |
| 3 — Maintainability | Code remains readable | Clear guard clause, not cryptic expression |
| 4 — Consistency | Follow existing patterns | Same style as surrounding code |
| 5 — Performance | Only if the fix introduces a bottleneck | Prefer correctness over micro-optimization |

---

## Fix Patterns by Bug Category

### Logic errors

| Root cause | Fix pattern |
|---|---|
| Wrong operator (`=` vs `==`, `&&` vs `\|\|`) | Correct the operator |
| Wrong conditional (`<` vs `<=`, `>` vs `>=`) | Correct the comparison |
| Wrong variable used | Change to correct variable |
| Missing `else` branch | Add the else branch |
| Wrong method called | Change to correct method |

### Null/empty handling

| Root cause | Fix pattern |
|---|---|
| Method returns null unexpectedly | Add null check at call site |
| Parameter not validated | Add guard clause at method entry |
| Collection operation on null | Initialize before use |
| Optional not checked | Add `isPresent()` check or `orElse()` |

**Example — add guard clause:**
```java
// Before:
public void process(Data data) {
    String value = data.getValue();  // NPE if data is null
}

// After:
public void process(Data data) {
    if (data == null) {
        return;  // or throw, based on contract
    }
    String value = data.getValue();
}
```

### Boundary conditions

| Root cause | Fix pattern |
|---|---|
| Off-by-one in loop | Adjust loop condition (`<` vs `<=`) |
| Empty collection not handled | Add `isEmpty()` check |
| Max value overflow | Use `long` or add overflow check |
| String index out of bounds | Check `length()` before `charAt()` |

### State management

| Root cause | Fix pattern |
|---|---|
| Cache not invalidated | Add cache eviction |
| Stale reference | Refresh reference on state change |
| Mutable shared state | Use defensive copy or immutable |
| Missing flush | Add flush after write |

### Concurrency

| Root cause | Fix pattern |
|---|---|
| Missing synchronization | Add `synchronized` block |
| Race condition on read-modify-write | Use `Atomic*` or lock |
| Missing volatile | Add `volatile` to shared flag |
| Deadlock | Reorder lock acquisition |
| Thread safety of collection | Use `ConcurrentHashMap` / `CopyOnWriteArrayList` |

---

## Skill Delegation

When the repair requires capabilities owned by other Skills, do not implement
them here — invoke the other Skill.

| Need | Skill | Trigger |
|---|---|---|
| Compile code | `java-maven` | Delegate: compile the affected module |
| Run tests | `java-maven` | Delegate: run the affected test(s) |
| Update mock fixtures | `mock-test` | Describe the mock change needed |
| Code review | `review` | Request review of the change |
| Specification update | `spec` | Describe the spec change needed |

---

## Minimum Change Principles

1. **One fix per commit** — never batch unrelated fixes
2. **Change only what's broken** — no opportunistic refactoring
3. **Follow existing style** — match surrounding code, don't reformat
4. **Preserve existing tests** — don't modify tests that pass
5. **Add tests for the fix** — a fix without a test is incomplete
