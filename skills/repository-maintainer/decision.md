# Decision Rules

---

## Asset Classification Decisions

When a new piece of content is proposed, classify it:

| Content describes | Asset type |
|---|---|
| An executable task for an AI agent | Skill |
| An orchestration of multiple Skills | Workflow |
| Engineering best practices | Playbook |
| Project-specific context | Knowledge |
| A reusable document format | Template |
| A verifiable item list | Checklist |

## Lifecycle Decisions

| Current state | Recommended action | Condition |
|---|---|---|
| Draft → Experimental | Passes RFC compliance | All quality gates pass |
| Experimental → Stable | Referenced by ≥ 1 Workflow | Stable usage pattern |
| Stable → Deprecated | Superseded by another asset | ADR documents replacement |
| Deprecated → Archived | No references for ≥ 1 month | Grace period elapsed |

## Recommendation Priorities

| Priority | Criteria | Timeline |
|---|---|---|
| P0 | Circular dependency, backward compat violation | Immediate |
| P1 | Excessive duplication, orphaned Skill, broken references | This cycle |
| P2 | Missing frontmatter, naming violations, unused assets | Next cycle |
| P3 | Minor inconsistencies, improvement suggestions | When possible |

## Stop Conditions

| Condition | Action |
|---|---|
| Repository has no violations | Stop, report "Repository healthy" |
| User rejects recommendations | Stop |
| Linter fails after approved changes | Revert, report, stop |
| User cancels | Stop |

## Execution Gate

| Stage | Gate | If not passed |
|---|---|---|
| 11 — Prioritize | Each recommendation passes quality gates | Rework recommendation |
| 13 — Approval | User explicitly approved | Do not execute |
| 14 — Execute | No BLOCKER from post-change linter | Revert changes |
