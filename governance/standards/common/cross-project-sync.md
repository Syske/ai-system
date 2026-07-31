# Cross-Project Duplicate Definition Sync Convention

## Purpose

Ensure that when an identically named class, enum, or constant exists in multiple projects, all copies are kept in sync when any one of them is modified.

## Scope

- `runtime-release` — release readiness validation

## Validation

1. During Release Scope Analysis, identify files classified as **Cross-Project Duplicated Definitions**
2. Search the workspace for identical filenames appearing in multiple modules (e.g., `**/AuditTypeEnum.java`)
3. Compare the content of each copy to determine whether synchronization is needed
4. If a copy intentionally does not need modification, confirm it is either marked `@deprecated` or has a clear business justification for divergence

## BLOCKER Condition

- A duplicate definition is modified but at least one copy is not updated AND has no valid justification

## Example

```
Modified:   enterprise-manage-api/.../AuditTypeEnum.java
Missed:     knowledge-api/.../AuditTypeEnum.java
            offline-course-api/.../AuditTypeEnum.java
```

All copies MUST be consistent before proceeding to the next phase.
