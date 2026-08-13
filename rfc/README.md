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
| ADR-0008 | Project ↔ Repository Logical Mapping | Accepted |
| ADR-0009 | AI-Operation-First Design (AI 自运行自维护优先) | Accepted |

### When to Create an ADR

Create an ADR only when **all three** conditions hold:

1. **Hard to reverse** — the cost of changing your mind later is meaningful.
2. **Surprising without context** — a future reader will wonder why it was done this way.
3. **The result of a real trade-off** — there were genuine alternatives, and one was chosen for specific reasons.

If any condition is missing, skip the ADR — record the decision inline in the
relevant spec or commit instead. Creating ADRs sparingly keeps the index a
high-signal record of consequential decisions, not a log of routine choices.

## Reading Order

New to the project: `README.md` → `OPERATIONS.md` → `RFC-0001` → `ADR-0004` (governance) → rest as needed.

Adding a new Skill: `RFC-0002` + `ADR-0004` + `governance/policies/skill-policy.md`.

All references in ADR files were updated (2026-07-19) to reflect the current `ai-system/` directory structure
(replacing stale `.opencode/` paths).
