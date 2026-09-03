# Alibaba Java Standard (Project Subset)

## Naming

Classes:

UpperCamelCase

Methods:

lowerCamelCase

Constants:

UPPER_SNAKE_CASE

Packages:

All lowercase.

---

## Visibility

Methods MUST declare an explicit access modifier (`public` / `protected` /
`private`); package-private method declarations are **prohibited** in normal
code.

- Default to `private` for class-internal helpers.
- Public API (interface implementations / facades / entry points) uses `public`.
- Exception — same-package test direct access: a class-internal helper that a
  unit test must call directly MAY stay package-private, but MUST (1) state that
  intent in the Javadoc first line (`供同包测试直接调用`), and (2) stay a review
  focus (test-coupled visibility widening). Prefer instead: test through the
  public behavior path, or extract the helper into a package-private testable
  component.
- The A-layer format gate (format-check.py check #7) warns on method
  declarations without an explicit access modifier.

---

## Lombok

Prefer:

@Data

@RequiredArgsConstructor

@Builder (when needed)

Forbidden:

Meaningless getters and setters.

---

## Collection

Return:

Empty collections.

Forbidden:

Returning null.

---

## String

String comparison:

Objects.equals()

Or:

StringUtils.equals()

Forbidden:

==

---

## Optional

Forbidden:

Optional as a field.

Forbidden:

Optional as a parameter.

Only use for:

Return values.

---

## Exception

Forbidden:

throws Exception

Must:

Use business exceptions.

---

## Log

Unified:

SLF4J

Forbidden:

printStackTrace()

System.out.println()

---

## Thread

Must:

Use thread pools.

Forbidden:

new Thread()

---

## Date

Unified:

java.time

Forbidden:

Date + Calendar in new code.

---

## Stream

Use judiciously.

Forbidden:

Complex nested Streams.

---

## SQL

Forbidden:

SQL in loops.

Must:

Paginate

Batch

Index-friendly

---

## Transaction

Transactions:

Minimum scope.

Forbidden:

Calling remote interfaces inside a transaction.

---

## Config

Forbidden:

Hardcoding:

URL

Token

Secret

Must:

Externalize to configuration.

---

## MQ

Unified:

Typed VOs.

Forbidden:

Assembling messages with JSONObject.

---

## Review

Before submission must:

Compile Pass

Unit Test Pass

Review Checklist Pass
