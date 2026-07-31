# Repository First

Version: 1.0

---

## Purpose

Before writing any new code, the AI must search the existing repository for reusable implementations.

This rule prevents code duplication, ensures consistency, and minimizes change footprint.

---

## Principle

```
REUSE > REWRITE

ONLY CREATE WHEN NECESSARY
```

---

## Required Search

Before implementing any change, perform these searches:

1. **Search Existing Implementation**: Is there an existing class, method, or service that already solves this?

2. **Search Existing Tests**: Are there existing test patterns, fixtures, or utilities that can be extended?

3. **Search Existing Utilities**: Does the project already have helper classes, converters, or validators?

4. **Search Existing Patterns**: What is the established pattern for this kind of change in the project?

---

## Decision Rule

| Situation | Action |
|---|---|
| Exact match exists | Reuse directly |
| Near match exists | Extend existing (prefer modification over new files) |
| Pattern exists but no usable code | Follow the existing pattern |
| Nothing exists | Create new, following project conventions |

---

## Anti-Patterns

Never:

- Create a new utility class when a project utility already covers the need
- Rewrite existing logic because "it could be cleaner" (unrelated refactoring)
- Create a new pattern when the project has an established pattern
- Import a new library when the project already has a dependency that solves it
- Duplicate configuration, constants, or error codes

---

## Scope

Applies to these Runtimes:

- develop
- bugfix
- review
- spec

Each must reference this document.

The reference line is:

```
Repository first: governance/REPOSITORY_FIRST.md
```
