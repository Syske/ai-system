# Memory Entry Format

Entry format for Coding Memory, per `governance/memory/MEMORY_GUIDELINES.md`.
All sections required except `Related`.

## Template

```
## [<Category>] <Short Title>

Context:

<background — why this situation arose>

Problem:

<what went wrong / what was unclear>

Root Cause:

<proven cause, with evidence>

Solution:

<verified fix / approach>

Lesson:

<one actionable sentence — MUST be present (memory.py checks)>

Scope:

- <affected areas: repos / modules / file paths>

Related:

- Standard: <governance reference if any>
```

## Rules

- **Language**: English (LANGUAGE_CONVENTION: Coding Memory → English).
- **Lesson** is mandatory and must be one actionable sentence (memory.py
  checks its presence).
- **Category** tag in the title matches the memory directory
  (`ai-system` / `java` / `python` / `integration`).
- **Related** links to a governance standard when the lesson touches one.
- Never write rules (→ governance/), task state (→ handoff), or reports
  (→ outputs/) into memory.
