# RFC & ADR Index

Two complementary layers:

## RFC (Detailed Specification)

Authoritative, approved design documents. Reading order by dependency.

| Number | Title | Status |
|---|---|---|
| RFC-0001 | Repository Architecture | Approved |
| RFC-0002 | Skill Specification | Approved |
| RFC-0003 | Workflow Specification | Approved |
| RFC-0004 | Playbook Specification | Approved |

## ADR (Architecture Decision Record)

Lightweight records capturing why a decision was made, its context, consequences, and rationale.
Each ADR references the RFC it implements.

| Number | Title | Status |
|---|---|---|
| ADR-0001 | OpenSpec Integration as Planning Layer | Accepted |
| ADR-0002 | Playbook as Separate Knowledge Layer | Accepted |
| ADR-0003 | java-maven as Foundation Skill | Accepted |
| ADR-0004 | Repository Governance Architecture | Accepted |
| ADR-0005 | Runtime Architecture | Accepted |
| ADR-0006 | Workflow-First Design | Accepted |
| ADR-0007 | Governance Independence | Accepted |

## Reading Order

New to the project: `README.md` → `OPERATIONS.md` → `RFC-0001` → `ADR-0004` (governance) → rest as needed.

Adding a new Skill: `RFC-0002` + `ADR-0004` + `governance/policies/skill-policy.md`.

All references in ADR files were updated (2026-07-19) to reflect the current `ai-system/` directory structure
(replacing stale `.opencode/` paths).
