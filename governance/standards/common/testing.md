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

# Naming

Recommended:

should_xxx_when_xxx

Example:

shouldRefreshTokenWhenExpired()

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
