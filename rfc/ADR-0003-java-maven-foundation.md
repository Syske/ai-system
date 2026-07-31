# ADR-0003: java-maven as Foundation Skill

| Field | Value |
|---|---|
| Status | **Accepted** |
| Decided | 2026-07-02 |

## Context

Every Java-related Skill in the repository needed to execute Maven commands.
Originally, each Skill had its own Maven invocation logic:
- bugfix had `mvn -pl ... test` in 3 files
- implement had `mvn -pl ... compile` in validation.md
- mock-test had `mvn test -Dtest=...` in diagnosis.md

This caused inconsistent scope selection, wrapper handling, and diagnosis.

## Decision

Create `java-maven` as a dedicated Foundation Skill responsible for ALL
Maven execution. Every other Skill must delegate Maven execution to
java-maven. No Skill may contain Maven commands directly.

## Consequences

**Positive:**
- Consistent Maven scope selection (smallest first)
- Consistent wrapper support (mvnw detection in one place)
- Consistent failure diagnosis (Surefire patterns in one place)
- Cache-friendly (no unnecessary clean builds)

**Negative:**
- Skills must wait for java-maven to complete before continuing
- java-maven becomes a bottleneck if it doesn't handle a specific case

## Rationale

Maven execution is a cross-cutting concern. Every Java Skill needs it.
Centralizing it in a Foundation Skill eliminates duplication and ensures
consistent behavior. The cost of the indirection is negligible compared
to the benefit of a single, well-tested Maven executor.

## Related

- `RFC-0001` — Repository Architecture (Layer 1 Foundation)
- `RFC-0002` — Skill Specification (prohibition of Maven commands in non-Maven skills)
- `skills/java-maven/`
