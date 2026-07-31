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
