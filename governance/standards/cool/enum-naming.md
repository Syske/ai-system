# Enum Value Naming Convention

## Purpose

Standardize Java enum string value naming to prevent compatibility issues across frontend, backend, database, and API layers caused by non-standard symbols.

## Scope

- `runtime-release` — release readiness validation
- Cool College projects

## Rules

1. Enum string values MUST only contain: lowercase letters, digits, underscores (`[a-z0-9_]`)
2. Forbidden characters: dot `.`, hyphen `-`, spaces, special characters
3. Enum constant names (Java identifiers) MUST follow `UPPER_SNAKE_CASE`

## Correct Example

```java
DELETE_LIVE_COURSE_SYNC("delete_live_course_sync", "book")
```

## Incorrect Examples

```java
DELETE_LIVE_COURSE_SYNC("delete_live_course.sync", "book")  // dot forbidden
EDIT_LIVE_COURSE_SYNC("edit-live-course-sync", "book")      // hyphen forbidden
```

## Validation

- Scan all new/modified Java enum classes
- Extract the string value parameter from each enum constructor
- Match against `^[a-z0-9_]+$` — any non-match is a BLOCKER
