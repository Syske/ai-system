# Mockito Maintenance

This document defines rules for maintaining Mockito stubbing, verification,
and matcher usage. Use during Stages 6-7 of the workflow.

---

## Stubbing Synchronization

### Method signature changed

If production method signature changed, every stubbing block for that method
must be updated:

```java
// Production: void foo(String s) → String foo(String s, int n)

// Before:
doNothing().when(dependency).foo(anyString());

// After:
when(dependency.foo(anyString(), anyInt())).thenReturn("result");
```

### Method removed

Remove every `when()` and `doReturn()`/`doThrow()` block that references the
removed method:

```java
// Remove this entirely:
when(dependency.removedMethod()).thenReturn(x);
```

### Method renamed

Update stubbing target to new name:

```java
// Before:
when(dependency.oldName()).thenReturn(x);

// After:
when(dependency.newName()).thenReturn(x);
```

### Return type changed

If return type changed, update both stubbing and any assertion on the result:

```java
// Production: List<String> getNames() → Set<String> getNames()

// Stubbing change:
when(dependency.getNames()).thenReturn(Set.of("a", "b"));  // ← Set not List

// Assertion change:
assertThat(result).containsExactly("a", "b");  // ← Set order not guaranteed
// Don't use: assertThat(result).get(0)        // Set has no get(int)
```

---

## Verification Synchronization

### Method removed

Remove associated `verify()` block:

```java
// Remove:
verify(dependency).removedMethod();
```

### Call count changed

Update `times(n)` to match new production behavior:

```java
// Production loop: send(msg) → for (m in list) send(m)

// Before:
verify(dependency, times(1)).send(any());

// After:
verify(dependency, times(list.size())).send(any());
```

### Call order changed

Update or remove `InOrder` blocks:

```java
// Production: save(user) → send(email) → send(email) → save(user)
// Order not predictable → remove InOrder verification
InOrder order = inOrder(userRepo, emailService);
order.verify(userRepo).save(any());    // may fail
// Fix: remove InOrder, verify independently
```

### Async transition

```java
// Production: sync call → async call

// Before:
verify(dependency).send(any());

// After (if result is used differently):
verify(dependency, timeout(1000)).send(any());
```

---

## ArgumentCaptor

### Captor type mismatch

If production parameter type changed, update captor generic type:

```java
// Production: void process(String s) → void process(NewType n)

// Before:
@Captor ArgumentCaptor<String> captor;

// After:
@Captor ArgumentCaptor<NewType> captor;
```

### Captor usage

Verify the captured value matches the new production behavior:

```java
verify(dependency).process(captor.capture());
NewType actual = captor.getValue();
assertThat(actual.getField()).isEqualTo("expected");
```

---

## Matcher Selection Guide

Select the narrowest matcher that reflects actual production behavior:

| Production call | Production allows null? | Matcher | Reason |
|---|---|---|---|
| `foo("hello")` | No | `eq("hello")` | Exact match |
| `foo(someVar)` | No | `anyString()` | Variable value, any string is fine |
| `foo(null)` | Documented | `isNull()` | Explicit null |
| `foo(someVar)` | Yes (`@Nullable`) | `nullable(String.class)` | Could be null |
| `foo(42)` | No | `eq(42)` | Literal int |
| `foo(someObj)` | No | `any()` or `eq(someObj)` | Depends on test scenario |
| `foo(list)` with content | No | `argThat(l -> l.size() == 2)` | Match specific content |
| `foo(anyString())` currently | N/A | Check if narrowing is safe | Never widen without reason |

### Matcher replacement rules

| Current | Replace with | When |
|---|---|---|
| `anyString()` | `eq("value")` | Production always passes same literal |
| `any()` | `anyString()` / `anyInt()` | Type-specific match is safe |
| `any()` | `nullable(Class)` | Production could pass null |
| `eq("x")` | `nullable(String.class)` | **Only** when null is valid and tested |
| `anyString()` | `isNull()` | Production explicitly passes null |

### Never do

- Replace `eq("x")` with `anyString()` without checking fixture correctness first
- Replace `anyString()` with `nullable(String.class)` unless null is intentionally passed
- Use `argThat(x -> true)` to bypass matching — this is equivalent to removing the assertion

---

## Lenient vs. Strict

| Scenario | Decision |
|---|---|
| Stubbing never called in test | Remove stubbing (production removed the call) |
| Stubbing called only conditionally | `lenient()` + comment explaining condition |
| Stubbing used by setup but not by every test | Extract setup to separate `@TestConfiguration` |
| Stubbing used across `@Nested` tests | Keep strict; verify each test path calls it |

**Lenient comment format:**

```java
when(dependency.optionalCall()).thenReturn(x);  // lenient: only called when feature flag is on
Mockito.lenient().when(dependency.optionalCall()).thenReturn(x);
```

---

## Unnecessary Stubbing Cleanup

During validation stage, check for unnecessary stubbings:

```java
// Run: mvn test -Dtest=XxxTest -Dmockito.junit.jupiter.StrictMockitoJUnitRunner
// Or add to test class:
@ExtendWith(MockitoExtension.class)
class XxxTest {
    // Strict mode automatically detects unnecessary stubbings
}
```

If detected:

| Condition | Action |
|---|---|
| Method no longer in production | Remove stubbing |
| Method called only in different branch | Move stubbing to specific test method or `lenient()` |
| Method replaced with different one | Remove old, add new stubbing |
