# Testing Standard

## Goal

All new features must include automated tests.

---

# Coverage

At minimum cover:

Happy path

Error path

Boundary conditions

Null values

Invalid parameters

---

# Seams

Tests verify behavior through **public interfaces**, not implementation details.

A **seam** is the public boundary at which you test — the interface where you observe
behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing tests, state the seams under
test and confirm them with the user. No test is written at an unconfirmed seam.
Agreeing seams up front directs testing effort at critical paths and complex
logic instead of every edge case.

A good test reads like a specification — "user can checkout with valid cart"
tells you exactly what capability exists — and survives refactors because it
does not care about internal structure.

---

# Naming

Recommended:

should_xxx_when_xxx

Example:

shouldRefreshTokenWhenExpired()

Method names MUST be **English ASCII identifiers** (`[A-Za-z0-9_$]`):

- **禁止中文/Unicode 方法名**（Java 允许 Unicode 标识符且能编译，但破坏 Javadoc / 反射 /
  测试报告 / IDE 重构与跨团队可读性）。反例：`syncToBeisen_enterpriseId空_抛参数异常`；
  应改：`syncToBeisen_enterpriseIdNull_shouldThrowIllegalArgument`。
- 场景化描述用英文下划线后缀可保留（`shouldX_whenY` / `method_englishScenario`）；
  中文场景说明只允许写在方法注释或 `@DisplayName` 中，不进方法名。

---

# Structure

Follow:

Given

When

Then

---

# Isolation

Unit tests:

Must not depend on:

Database

MQ

Redis

HTTP

Mock all external dependencies.

---

# Assertion

Assertions:

Only verify the current test target.

Forbidden:

One test covering multiple business scenarios.

---

# Exception

Must verify:

Exception type

Exception message (when necessary)

---

# Mock

Mock:

Behavior

Return values

Exceptions

Avoid:

Over-mocking.

---

# Test Anti-Patterns

Avoid:

**Implementation-coupled** — mocks internal collaborators, tests private methods,
or verifies through a side channel. The tell: the test breaks on refactor but
behavior is unchanged.

**Tautological** — the assertion recomputes the expected value the way the code
does, so it passes by construction and can never disagree with the code.
Expected values must come from an independent source of truth (a known-good
literal, a worked example, the spec).

**Horizontal slicing** — writing all tests first, then all implementation. This
tests imagined behavior and the shape of things rather than user-facing behavior.
Work in vertical slices instead: one test → one implementation → repeat.

---

# Repeatability

Tests must:

Be repeatable.

Must not depend on:

Time

Random numbers

Network

Environment variables

---

# Completion

All tests:

Runnable locally.

Runnable in CI.
