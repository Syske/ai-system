# Clean Code Standard

## Goal

Generated code must prioritize:

1. Readability
2. Maintainability
3. Testability
4. Extensibility

Functional correctness is only the minimum requirement.

---

# General Principles

Must follow:

- KISS
- DRY
- YAGNI
- SOLID (emphasis on SRP, DIP)
- Tell Don't Ask
- Fail Fast

Forbidden:

- Over-engineering
- Pre-emptive abstraction for future requirements
- Reuse for the sake of reuse
- Copy-paste code

---

# Class Design

Every class must:

- Have a single responsibility
- Express business meaning through its name
- Avoid combining Controller + Service + Mapper responsibilities

Forbidden:

God Object

---

# Method Design

Methods should:

- Stay short (recommended ≤40 lines)
- Do one thing only
- Express business intent through the name

Prefer:

Early Return

Avoid:

Deeply nested if/else

Recommendation:

Maximum 3 levels of nesting.

---

# Variable

Variable names must:

Express business meaning.

Forbidden names:

data

obj

tmp

flag

test

str

list1

---

# Constants

Forbidden:

Magic Number

Magic String

Must:

Extract as named constants.

---

# Boolean

Avoid:

boolean parameters.

Prefer:

Enum

Strategy pattern

Parameter object

---

# Null

Must:

Prevent NullPointerException.

Prefer:

Objects.requireNonNull()

Return empty collections.

Forbidden:

Return null Collection.

---

# Exception

Exceptions must:

Include business context.

Forbidden:

catch(Exception){}

After catch you must:

Log the error

Rethrow

Or convert to a business exception

Never swallow exceptions.

---

# Logging

Logs must include:

Business ID

Request ID (if available)

Key parameters

Forbidden:

System.out.println

Logs must never contain:

Passwords

Tokens

Secrets

Private data

---

# Comments

Comments explain:

Why

Not:

What

Wrong:

// Check if null

Right:

// WeCom API returns 42001 when the token expires; refresh and retry once

---

# Reuse

Prefer:

Extending existing capabilities.

Forbidden:

Copy an existing implementation then modify it.

---

# Dependency

Dependency direction:

Controller

↓

Service

↓

Repository

Reverse dependencies are forbidden.

---

# Completion Checklist

After coding, confirm:

□ No duplicated code

□ No magic numbers

□ No TODO

□ No FIXME

□ No dead code

□ Methods have a single responsibility

□ Classes have a single responsibility

□ Passes review
