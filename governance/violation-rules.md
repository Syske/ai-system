# Repository Governance

> This document is the entrypoint for the AI Engineering Repository governance
> system. It describes what governance is, why it exists, and how the pieces
> fit together.

---

## What Is Repository Governance?

Repository Governance is the set of rules, processes, and automated checks
that ensure this repository remains maintainable, consistent, and composable
as it grows.

Without governance, repositories naturally degrade: Skills duplicate content,
naming becomes inconsistent, dead references accumulate, and no one knows
what is safe to change.

## Governance Layers

```
┌─────────────────────────────────────────────────────────┐
│                  1. RFCs (Specifications)               │
│  Define what each component is and how it must behave   │
│  Location: rfc/                                       │
├─────────────────────────────────────────────────────────┤
│                  2. Governance Docs (Policies)          │
│  Define processes, gates, lifecycle, conventions        │
│  Location: governance/                                │
├─────────────────────────────────────────────────────────┤
│                  3. ADRs (Decisions)                    │
│  Record why architectural decisions were made           │
│  Location: rfc/ (co-located with RFCs)               │
├─────────────────────────────────────────────────────────┤
│                  4. Automated Tools (Enforcement)       │
│  Linter, metrics, dependency graph — run on CI          │
│  Location: tools/                                        │
├─────────────────────────────────────────────────────────┤
│                  5. Metrics (Tracking)                  │
│  Snapshot repository health over time                   │
│  Location: metrics/                                   │
└─────────────────────────────────────────────────────────┘
```

## Governance Documents

| Document | Purpose |
|---|---|
| `governance/policies/quality-gates.md` | BLOCKER/ERROR/WARNING/INFO quality checks |
| `OPERATIONS.md` (section 7, Repository Lifecycle Rules) | Draft → Proposed → Active → Deprecated → Archived |
| `governance/review-standard.md` | When and how to review Skill changes |
| `governance/policies/skill-policy.md` | How to add new Skills or modify existing ones |
| `governance/repo-lint.md` | Naming rules for all components |

## Tooling

| Tool | Purpose | Run with |
|---|---|---|
| `tools/repo-lint.py` | Structural linting against RFCs | `python tools/repo-lint.py --repo-root .` |
| `tools/repo-metrics.py` | Health metrics collection | `python tools/repo-metrics.py --repo-root .` |
| `tools/dependency-graph.py` | Skill dependency visualization | `python tools/dependency-graph.py --repo-root .` |

## How to Use This System

**Everyday development:** Run `python tools/repo-lint.py --repo-root .` before
committing changes to ensure no BLOCKER or ERROR exists.

**Adding a new Skill:** Read `governance/policies/skill-policy.md` first.
Follow the RFC-0002 specification. Run the linter. Submit for review.

**Quarterly health check:** Run `python tools/repo-metrics.py --repo-root .`
and save the snapshot to `metrics/`. Compare with the previous snapshot to
track trends.

**Architecture review:** When a significant change is proposed, create an RFC
in `rfc/` and an ADR in `rfc/`. Record the review in `reports/`.
