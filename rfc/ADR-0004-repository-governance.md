# ADR-0004: Repository Governance Architecture

| Field | Value |
|---|---|
| Status | **Accepted** |
| Decided | 2026-07-02 |

## Context

As the repository grew beyond 15 Skills, several maintenance challenges
emerged:
1. No standard for what a "valid" Skill looks like
2. No detection of duplication, dead references, or circular dependencies
3. No metrics to track repository health over time
4. No lifecycle for Skills (when to create, deprecate, archive)

Without governance, the repository would degrade as more Skills are added.

## Decision

Establish a four-layer governance architecture:

| Layer | Component | Responsibility |
|---|---|---|
| Specification | `rfc/RFC-0001` through `RFC-0003` | Define the rules |
| History | `adr/` | Record why decisions were made |
| Enforcement | `governance/` | Quality gates, review process, lifecycle |
| Automation | `scripts/repo-lint.py`, `scripts/repo-metrics.py` | Automated checking |

Plus a governance Skill (`repository-governor`) that analyzes repository
health and suggests improvements.

## Consequences

**Positive:**
- Every future Skill addition follows a defined standard
- Repository health is measurable and trackable over time
- Duplication is detected automatically
- Dead/orphaned components are flagged

**Negative:**
- Adding a new Skill requires more upfront work (RFC, governance checks)
- Automated checks must be maintained alongside the repository

## Rationale

Governance is the only way to ensure a repository of this size remains
maintainable over years. Without it, the natural trend is toward
entropy — duplication, inconsistency, and dead content.

## Related

- `RFC-0001` — Repository Architecture
- `RFC-0002` — Skill Specification
- `RFC-0003` — Workflow Specification
- `governance/policies/quality-gates.md`
- `OPERATIONS.md` §7 — Repository Lifecycle Rules
- `tools/repo-lint.py`
- `skills/repository-governor/`
